"""
CorpusMonitor module for UVI package.

This module provides file system monitoring capabilities for corpus directories,
triggering rebuilds when files change and maintaining change logs and error handling.
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from collections import deque

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    # Fallback if watchdog is not available
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None


class CorpusMonitor:
    """
    A standalone class for monitoring corpus directories and triggering
    rebuilds when files change.
    """
    
    def __init__(self, corpus_loader):
        """
        Initialize CorpusMonitor with CorpusLoader instance.
        
        Args:
            corpus_loader: Instance of CorpusLoader for rebuilds
        """
        self.corpus_loader = corpus_loader
        self.observer = None if not WATCHDOG_AVAILABLE else Observer()
        self.watch_paths = {}
        self.is_monitoring_active = False
        self.rebuild_strategy = 'immediate'
        self.batch_timeout = 60
        self.max_retries = 3
        self.retry_delay = 30
        
        # Logging setup
        self.logger = self._setup_logger()
        self.change_log = deque(maxlen=1000)  # Keep last 1000 changes
        self.rebuild_history = deque(maxlen=500)  # Keep last 500 rebuilds
        
        # Batch processing
        self.batch_changes = {}
        self.batch_timer = None
        self.batch_lock = threading.Lock()
        
        # Error tracking
        self.error_counts = {}
        self.last_successful_rebuild = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for corpus monitoring."""
        logger = logging.getLogger('CorpusMonitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def set_watch_paths(self, 
                       verbnet_path: Optional[str] = None,
                       framenet_path: Optional[str] = None, 
                       propbank_path: Optional[str] = None,
                       reference_docs_path: Optional[str] = None) -> Dict[str, str]:
        """
        Set paths to monitor for changes.
        
        Args:
            verbnet_path (str): Path to VerbNet corpus
            framenet_path (str): Path to FrameNet corpus
            propbank_path (str): Path to PropBank corpus
            reference_docs_path (str): Path to reference documents
            
        Returns:
            dict: Configured watch paths
        """
        new_paths = {}
        
        if verbnet_path and os.path.exists(verbnet_path):
            new_paths['verbnet'] = verbnet_path
        if framenet_path and os.path.exists(framenet_path):
            new_paths['framenet'] = framenet_path
        if propbank_path and os.path.exists(propbank_path):
            new_paths['propbank'] = propbank_path
        if reference_docs_path and os.path.exists(reference_docs_path):
            new_paths['reference_docs'] = reference_docs_path
        
        self.watch_paths.update(new_paths)
        
        self.logger.info(f"Updated watch paths: {list(new_paths.keys())}")
        self.log_event('config_update', {
            'action': 'set_watch_paths',
            'paths': new_paths
        })
        
        return self.watch_paths.copy()
    
    def set_rebuild_strategy(self, strategy: str = 'immediate', batch_timeout: int = 60) -> Dict[str, Any]:
        """
        Set rebuild strategy for detected changes.
        
        Args:
            strategy (str): 'immediate' or 'batch'
            batch_timeout (int): Seconds to wait before batch rebuild
            
        Returns:
            dict: Current strategy configuration
        """
        if strategy not in ['immediate', 'batch']:
            raise ValueError("Strategy must be 'immediate' or 'batch'")
        
        self.rebuild_strategy = strategy
        self.batch_timeout = batch_timeout
        
        config = {
            'strategy': self.rebuild_strategy,
            'batch_timeout': self.batch_timeout
        }
        
        self.logger.info(f"Updated rebuild strategy: {config}")
        self.log_event('config_update', {
            'action': 'set_rebuild_strategy',
            'config': config
        })
        
        return config
    
    def start_monitoring(self) -> bool:
        """
        Start monitoring configured paths for changes.
        
        Returns:
            bool: Success status
        """
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Watchdog library not available. File monitoring disabled.")
            return False
        
        if self.is_monitoring_active:
            self.logger.warning("Monitoring is already active")
            return True
        
        if not self.watch_paths:
            self.logger.warning("No watch paths configured")
            return False
        
        try:
            # Create event handler
            event_handler = self._create_event_handler()
            
            # Add watches for each configured path
            for corpus_type, path in self.watch_paths.items():
                self.observer.schedule(event_handler, path, recursive=True)
                self.logger.info(f"Started watching {corpus_type} at {path}")
            
            # Start the observer
            self.observer.start()
            self.is_monitoring_active = True
            
            self.log_event('monitoring_start', {
                'paths': self.watch_paths.copy(),
                'strategy': self.rebuild_strategy
            })
            
            self.logger.info("Corpus monitoring started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            self.log_event('monitoring_error', {
                'action': 'start_monitoring',
                'error': str(e)
            })
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop monitoring file changes.
        
        Returns:
            bool: Success status
        """
        if not self.is_monitoring_active:
            return True
        
        try:
            if self.observer and WATCHDOG_AVAILABLE:
                self.observer.stop()
                self.observer.join(timeout=5)  # Wait up to 5 seconds
            
            # Cancel any pending batch operations
            if self.batch_timer:
                self.batch_timer.cancel()
                self.batch_timer = None
            
            self.is_monitoring_active = False
            
            self.log_event('monitoring_stop', {
                'reason': 'manual_stop'
            })
            
            self.logger.info("Corpus monitoring stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
            self.log_event('monitoring_error', {
                'action': 'stop_monitoring', 
                'error': str(e)
            })
            return False
    
    def is_monitoring(self) -> bool:
        """
        Check if monitoring is active.
        
        Returns:
            bool: Monitoring status
        """
        return self.is_monitoring_active
    
    def handle_file_change(self, file_path: str, change_type: str) -> Dict[str, Any]:
        """
        Handle detected file change event.
        
        Args:
            file_path (str): Path to changed file
            change_type (str): Type of change (create/modify/delete)
            
        Returns:
            dict: Action taken
        """
        try:
            # Determine corpus type from file path
            corpus_type = self._determine_corpus_type(file_path)
            
            if not corpus_type:
                return {'action': 'ignored', 'reason': 'unknown_corpus_type'}
            
            self.logger.info(f"File change detected: {change_type} in {corpus_type}: {file_path}")
            
            # Log the change
            self.log_event('file_change', {
                'file_path': file_path,
                'change_type': change_type,
                'corpus_type': corpus_type
            })
            
            # Route to appropriate handler
            if corpus_type == 'verbnet':
                success = self.handle_verbnet_change(file_path, change_type)
            elif corpus_type == 'framenet':
                success = self.handle_framenet_change(file_path, change_type)
            elif corpus_type == 'propbank':
                success = self.handle_propbank_change(file_path, change_type)
            elif corpus_type == 'reference_docs':
                success = self.handle_reference_docs_change(file_path, change_type)
            else:
                success = self.handle_generic_change(file_path, change_type, corpus_type)
            
            return {
                'action': 'processed',
                'corpus_type': corpus_type,
                'success': success,
                'strategy': self.rebuild_strategy
            }
            
        except Exception as e:
            self.logger.error(f"Error handling file change: {str(e)}")
            self.log_event('change_error', {
                'file_path': file_path,
                'change_type': change_type,
                'error': str(e)
            })
            return {'action': 'error', 'error': str(e)}
    
    def handle_verbnet_change(self, file_path: str, change_type: str) -> bool:
        """
        Handle VerbNet corpus file change.
        
        Args:
            file_path (str): Changed file path
            change_type (str): Type of change
            
        Returns:
            bool: Rebuild success status
        """
        try:
            # Only trigger rebuild for XML files
            if not file_path.lower().endswith('.xml'):
                return True
            
            return self._trigger_corpus_rebuild('verbnet', {
                'file_path': file_path,
                'change_type': change_type,
                'reason': f'VerbNet {change_type} detected'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling VerbNet change: {str(e)}")
            return False
    
    def handle_framenet_change(self, file_path: str, change_type: str) -> bool:
        """
        Handle FrameNet corpus file change.
        
        Args:
            file_path (str): Changed file path
            change_type (str): Type of change
            
        Returns:
            bool: Rebuild success status
        """
        try:
            # Trigger rebuild for XML files
            if not file_path.lower().endswith('.xml'):
                return True
            
            return self._trigger_corpus_rebuild('framenet', {
                'file_path': file_path,
                'change_type': change_type,
                'reason': f'FrameNet {change_type} detected'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling FrameNet change: {str(e)}")
            return False
    
    def handle_propbank_change(self, file_path: str, change_type: str) -> bool:
        """
        Handle PropBank corpus file change.
        
        Args:
            file_path (str): Changed file path
            change_type (str): Type of change
            
        Returns:
            bool: Rebuild success status
        """
        try:
            # Trigger rebuild for XML files
            if not file_path.lower().endswith('.xml'):
                return True
            
            return self._trigger_corpus_rebuild('propbank', {
                'file_path': file_path,
                'change_type': change_type,
                'reason': f'PropBank {change_type} detected'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling PropBank change: {str(e)}")
            return False
    
    def handle_reference_docs_change(self, file_path: str, change_type: str) -> bool:
        """
        Handle reference documentation file change.
        
        Args:
            file_path (str): Changed file path
            change_type (str): Type of change
            
        Returns:
            bool: Rebuild success status
        """
        try:
            # Trigger rebuild for JSON/TSV files
            if not any(file_path.lower().endswith(ext) for ext in ['.json', '.tsv', '.csv']):
                return True
            
            return self._trigger_corpus_rebuild('reference_docs', {
                'file_path': file_path,
                'change_type': change_type,
                'reason': f'Reference docs {change_type} detected'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling reference docs change: {str(e)}")
            return False
    
    def handle_generic_change(self, file_path: str, change_type: str, corpus_type: str) -> bool:
        """
        Handle generic corpus file change.
        
        Args:
            file_path (str): Changed file path
            change_type (str): Type of change
            corpus_type (str): Type of corpus
            
        Returns:
            bool: Rebuild success status
        """
        try:
            return self._trigger_corpus_rebuild(corpus_type, {
                'file_path': file_path,
                'change_type': change_type,
                'reason': f'{corpus_type} {change_type} detected'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling {corpus_type} change: {str(e)}")
            return False
    
    def trigger_rebuild(self, corpus_type: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger rebuild of specific corpus collection.
        
        Args:
            corpus_type (str): Type of corpus to rebuild
            reason (str): Optional reason for rebuild
            
        Returns:
            dict: Rebuild result with timing
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting rebuild of {corpus_type}" + (f" - {reason}" if reason else ""))
            
            # Attempt rebuild with retry logic
            success = False
            attempts = 0
            last_error = None
            
            while attempts < self.max_retries and not success:
                attempts += 1
                try:
                    # Call appropriate rebuild method on corpus loader
                    if hasattr(self.corpus_loader, f'rebuild_{corpus_type}'):
                        rebuild_method = getattr(self.corpus_loader, f'rebuild_{corpus_type}')
                        success = rebuild_method()
                    elif hasattr(self.corpus_loader, 'rebuild_corpus'):
                        success = self.corpus_loader.rebuild_corpus(corpus_type)
                    elif hasattr(self.corpus_loader, 'load_corpus'):
                        # Fallback to reloading the corpus
                        result = self.corpus_loader.load_corpus(corpus_type)
                        success = bool(result)
                    else:
                        raise AttributeError(f"No rebuild method available for {corpus_type}")
                    
                except Exception as e:
                    last_error = e
                    if attempts < self.max_retries:
                        self.logger.warning(f"Rebuild attempt {attempts} failed: {str(e)}. Retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                    else:
                        self.logger.error(f"All rebuild attempts failed for {corpus_type}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                'corpus_type': corpus_type,
                'success': success,
                'attempts': attempts,
                'duration': duration,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.last_successful_rebuild[corpus_type] = datetime.now()
                self.error_counts[corpus_type] = 0
                self.logger.info(f"Successfully rebuilt {corpus_type} in {duration:.2f}s")
            else:
                self.error_counts[corpus_type] = self.error_counts.get(corpus_type, 0) + 1
                result['error'] = str(last_error) if last_error else 'Unknown error'
                self.handle_rebuild_error(last_error, corpus_type)
            
            # Log rebuild
            self.rebuild_history.append(result)
            self.log_event('rebuild_complete', result)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            error_result = {
                'corpus_type': corpus_type,
                'success': False,
                'attempts': 1,
                'duration': duration,
                'reason': reason,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            self.rebuild_history.append(error_result)
            self.handle_rebuild_error(e, corpus_type)
            
            return error_result
    
    def batch_rebuild(self, corpus_types: List[str]) -> Dict[str, Any]:
        """
        Perform batch rebuild of multiple corpora.
        
        Args:
            corpus_types (list): List of corpus types to rebuild
            
        Returns:
            dict: Results for each corpus rebuild
        """
        results = {}
        start_time = time.time()
        
        self.logger.info(f"Starting batch rebuild of: {corpus_types}")
        
        for corpus_type in corpus_types:
            results[corpus_type] = self.trigger_rebuild(
                corpus_type, 
                reason=f"Batch rebuild"
            )
        
        end_time = time.time()
        batch_duration = end_time - start_time
        
        batch_result = {
            'type': 'batch_rebuild',
            'corpus_types': corpus_types,
            'duration': batch_duration,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'total_success': all(r.get('success', False) for r in results.values())
        }
        
        self.logger.info(f"Batch rebuild completed in {batch_duration:.2f}s")
        self.log_event('batch_rebuild_complete', batch_result)
        
        return batch_result
    
    def get_change_log(self, limit: int = 100) -> List[Dict]:
        """
        Get recent file change log.
        
        Args:
            limit (int): Maximum entries to return
            
        Returns:
            list: Recent change entries
        """
        return list(self.change_log)[-limit:]
    
    def get_rebuild_history(self, limit: int = 50) -> List[Dict]:
        """
        Get rebuild history.
        
        Args:
            limit (int): Maximum entries to return
            
        Returns:
            list: Recent rebuild entries
        """
        return list(self.rebuild_history)[-limit:]
    
    def log_event(self, event_type: str, details: Dict) -> bool:
        """
        Log monitoring event.
        
        Args:
            event_type (str): Type of event
            details (dict): Event details
            
        Returns:
            bool: Success status
        """
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'details': details.copy() if details else {}
            }
            
            self.change_log.append(event)
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging event: {str(e)}")
            return False
    
    def handle_rebuild_error(self, error: Exception, corpus_type: str) -> Dict[str, Any]:
        """
        Handle errors during rebuild process.
        
        Args:
            error (Exception): The error that occurred
            corpus_type (str): Corpus being rebuilt
            
        Returns:
            dict: Error handling result
        """
        error_count = self.error_counts.get(corpus_type, 0) + 1
        self.error_counts[corpus_type] = error_count
        
        self.logger.error(f"Rebuild error for {corpus_type} (#{error_count}): {str(error)}")
        
        # Log detailed error information
        error_details = {
            'corpus_type': corpus_type,
            'error_message': str(error),
            'error_type': type(error).__name__,
            'error_count': error_count,
            'max_retries': self.max_retries
        }
        
        self.log_event('rebuild_error', error_details)
        
        # Determine if we should take additional action
        action_taken = None
        if error_count >= self.max_retries:
            self.logger.warning(f"Maximum errors reached for {corpus_type}. Consider manual intervention.")
            action_taken = 'max_errors_reached'
        
        return {
            'handled': True,
            'error_count': error_count,
            'action_taken': action_taken,
            'details': error_details
        }
    
    def set_error_recovery_strategy(self, max_retries: int = 3, retry_delay: int = 30) -> Dict[str, Any]:
        """
        Configure error recovery strategy.
        
        Args:
            max_retries (int): Maximum rebuild retry attempts
            retry_delay (int): Seconds between retries
            
        Returns:
            dict: Current error recovery configuration
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        config = {
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
        
        self.logger.info(f"Updated error recovery strategy: {config}")
        self.log_event('config_update', {
            'action': 'set_error_recovery_strategy',
            'config': config
        })
        
        return config
    
    def _create_event_handler(self):
        """Create file system event handler."""
        if not WATCHDOG_AVAILABLE:
            return None
            
        class CorpusEventHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor
            
            def on_any_event(self, event):
                if event.is_directory:
                    return
                
                change_type_map = {
                    'created': 'create',
                    'modified': 'modify', 
                    'deleted': 'delete',
                    'moved': 'move'
                }
                
                change_type = change_type_map.get(event.event_type, 'unknown')
                self.monitor.handle_file_change(event.src_path, change_type)
        
        return CorpusEventHandler(self)
    
    def _determine_corpus_type(self, file_path: str) -> Optional[str]:
        """Determine corpus type from file path."""
        file_path = os.path.normpath(file_path)
        
        for corpus_type, watch_path in self.watch_paths.items():
            watch_path = os.path.normpath(watch_path)
            if file_path.startswith(watch_path):
                return corpus_type
        
        return None
    
    def _trigger_corpus_rebuild(self, corpus_type: str, context: Dict) -> bool:
        """Internal method to trigger corpus rebuild based on strategy."""
        try:
            if self.rebuild_strategy == 'immediate':
                result = self.trigger_rebuild(corpus_type, context.get('reason'))
                return result.get('success', False)
            
            elif self.rebuild_strategy == 'batch':
                with self.batch_lock:
                    # Add to batch queue
                    if corpus_type not in self.batch_changes:
                        self.batch_changes[corpus_type] = []
                    self.batch_changes[corpus_type].append(context)
                    
                    # Reset or start batch timer
                    if self.batch_timer:
                        self.batch_timer.cancel()
                    
                    self.batch_timer = threading.Timer(
                        self.batch_timeout,
                        self._execute_batch_rebuild
                    )
                    self.batch_timer.start()
                
                return True  # Queued successfully
            
            else:
                self.logger.warning(f"Unknown rebuild strategy: {self.rebuild_strategy}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error triggering rebuild: {str(e)}")
            return False
    
    def _execute_batch_rebuild(self):
        """Execute batch rebuild after timeout."""
        try:
            with self.batch_lock:
                if not self.batch_changes:
                    return
                
                corpus_types = list(self.batch_changes.keys())
                self.batch_changes.clear()
                self.batch_timer = None
            
            self.logger.info(f"Executing batch rebuild for: {corpus_types}")
            self.batch_rebuild(corpus_types)
            
        except Exception as e:
            self.logger.error(f"Error executing batch rebuild: {str(e)}")