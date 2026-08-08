"""
ParsingEngine Helper Class

Centralized parsing operations using CorpusParser integration. Eliminates UVI's
duplicate parsing methods and provides centralized, optimized corpus parsing
through CorpusParser delegation.

This class centralizes all parsing operations and replaces UVI's duplicate
parsing logic with CorpusParser integration.
"""

from typing import Dict, List, Optional, Union, Any, Callable
from pathlib import Path
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusParser


class ParsingEngine(BaseHelper):
    """
    Centralized parsing operations using CorpusParser integration.
    
    Provides comprehensive corpus parsing capabilities through CorpusParser delegation,
    eliminating duplicate parsing logic from UVI. This class centralizes all parsing
    operations and provides enhanced parsing capabilities with error handling and
    statistics tracking.
    
    Key Features:
    - Individual corpus parsing via CorpusParser delegation
    - Batch parsing of all available corpora
    - Re-parsing capabilities with fresh data
    - Comprehensive parsing statistics across all corpora
    - Parsed data validation using CorpusParser error handling
    - Parsing performance metrics and optimization
    - Error handling and recovery for parsing failures
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize ParsingEngine with CorpusParser integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Access to CorpusParser for centralized parsing operations
        self.corpus_parser = getattr(uvi_instance, 'corpus_parser', None)
        
        # Initialize CorpusParser if not available
        if not self.corpus_parser:
            try:
                # Initialize with UVI's corpus paths and logger
                corpus_paths = getattr(uvi_instance, 'corpus_paths', {})
                self.corpus_parser = CorpusParser(corpus_paths, self.logger)
                # Set the parser reference in UVI for other components
                uvi_instance.corpus_parser = self.corpus_parser
            except Exception as e:
                self.logger.warning(f"Could not initialize CorpusParser: {e}")
                self.corpus_parser = None
        
        # Parsing cache for performance optimization
        self.parsing_cache = {}
        self.parsing_statistics = {}
        
        # Parser method mapping for different corpus types
        self.parser_methods = self._initialize_parser_methods()
        
    def parse_corpus_files(self, corpus_name: str) -> Dict[str, Any]:
        """
        Parse all files for a specific corpus using CorpusParser.
        
        Args:
            corpus_name (str): Name of corpus to parse
            
        Returns:
            Dict[str, Any]: Parsed corpus data with statistics
        """
        if not self.corpus_parser:
            return self._error_result(corpus_name, "CorpusParser not available")
            
        # Check cache first
        if corpus_name in self.parsing_cache:
            cached_result = self.parsing_cache[corpus_name]
            self.logger.info(f"Retrieved {corpus_name} from parsing cache")
            return cached_result
            
        # Get parser method for corpus
        parser_method = self.parser_methods.get(corpus_name)
        if not parser_method:
            return self._error_result(corpus_name, f"No parser method available for {corpus_name}")
            
        try:
            self.logger.info(f"Parsing {corpus_name} using CorpusParser")
            
            # Execute parsing with CorpusParser error handling
            parsed_data = parser_method()
            
            # Cache the result
            self.parsing_cache[corpus_name] = parsed_data
            
            # Update UVI's corpus data
            if parsed_data and not parsed_data.get('error'):
                self.uvi.corpora_data[corpus_name] = parsed_data
                self.uvi.loaded_corpora.add(corpus_name)
                
            # Update parsing statistics
            self._update_parsing_statistics(corpus_name, parsed_data)
            
            self.logger.info(f"Successfully parsed {corpus_name}")
            return parsed_data
            
        except Exception as e:
            error_info = {
                'corpus': corpus_name,
                'error': str(e),
                'method': parser_method.__name__ if hasattr(parser_method, '__name__') else 'unknown'
            }
            return self._handle_parsing_errors(corpus_name, error_info)
            
    def parse_all_corpora(self) -> Dict[str, Any]:
        """
        Parse all available corpora using CorpusParser methods.
        
        Returns:
            Dict[str, Any]: Parsing results for all corpora with summary statistics
        """
        if not self.corpus_parser:
            return {
                'error': 'CorpusParser not available',
                'parsing_summary': {
                    'total_corpora': 0,
                    'successful_parses': 0,
                    'failed_parses': 0
                }
            }
            
        parsing_results = {
            'parsing_timestamp': self._get_timestamp(),
            'parsing_method': 'CorpusParser_batch',
            'corpus_results': {},
            'parsing_summary': {
                'total_corpora': 0,
                'successful_parses': 0,
                'failed_parses': 0,
                'total_parsing_time': 0.0
            }
        }
        
        # Get available corpora from UVI
        supported_corpora = getattr(self.uvi, 'supported_corpora', list(self.parser_methods.keys()))
        parsing_results['parsing_summary']['total_corpora'] = len(supported_corpora)
        
        # Parse each corpus
        for corpus_name in supported_corpora:
            if corpus_name in self.uvi.corpus_paths or corpus_name in self.parser_methods:
                try:
                    corpus_result = self.parse_corpus_files(corpus_name)
                    parsing_results['corpus_results'][corpus_name] = corpus_result
                    
                    if corpus_result and not corpus_result.get('error'):
                        parsing_results['parsing_summary']['successful_parses'] += 1
                    else:
                        parsing_results['parsing_summary']['failed_parses'] += 1
                        
                except Exception as e:
                    parsing_results['corpus_results'][corpus_name] = {
                        'error': str(e),
                        'parsing_method': 'batch_parse'
                    }
                    parsing_results['parsing_summary']['failed_parses'] += 1
            else:
                self.logger.warning(f"No path or parser method available for {corpus_name}")
                
        # Calculate overall statistics
        parsing_results['overall_success_rate'] = (
            parsing_results['parsing_summary']['successful_parses'] / 
            parsing_results['parsing_summary']['total_corpora'] * 100
            if parsing_results['parsing_summary']['total_corpora'] > 0 else 0
        )
        
        self.logger.info(f"Batch parsing completed: {parsing_results['parsing_summary']['successful_parses']}/{parsing_results['parsing_summary']['total_corpora']} successful")
        
        return parsing_results
        
    def reparse_corpus(self, corpus_name: str, force_refresh: bool = True) -> Dict[str, Any]:
        """
        Re-parse specific corpus with fresh data.
        
        Args:
            corpus_name (str): Name of corpus to re-parse
            force_refresh (bool): Force refresh of cached data
            
        Returns:
            Dict[str, Any]: Re-parsing results
        """
        if force_refresh and corpus_name in self.parsing_cache:
            del self.parsing_cache[corpus_name]
            self.logger.info(f"Cleared cache for {corpus_name}")
            
        # Remove from UVI's loaded data to force fresh parse
        if corpus_name in self.uvi.corpora_data:
            del self.uvi.corpora_data[corpus_name]
        self.uvi.loaded_corpora.discard(corpus_name)
        
        # Parse with fresh data
        reparse_result = self.parse_corpus_files(corpus_name)
        
        # Add re-parsing metadata
        if isinstance(reparse_result, dict):
            reparse_result['reparse_metadata'] = {
                'reparse_timestamp': self._get_timestamp(),
                'force_refresh': force_refresh,
                'cache_cleared': force_refresh
            }
            
        return reparse_result
        
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive parsing statistics across all corpora.
        
        Returns:
            Dict[str, Any]: Parsing statistics and performance metrics
        """
        statistics = {
            'statistics_timestamp': self._get_timestamp(),
            'statistics_source': 'CorpusParser_enhanced',
            'overall_statistics': {
                'total_supported_corpora': len(getattr(self.uvi, 'supported_corpora', [])),
                'total_parsed_corpora': len(self.uvi.loaded_corpora),
                'total_cached_results': len(self.parsing_cache),
                'parsing_success_rate': 0.0
            },
            'corpus_statistics': {},
            'parsing_performance': {},
            'error_summary': {}
        }
        
        # Calculate overall success rate
        if hasattr(self.uvi, 'supported_corpora'):
            total_supported = len(self.uvi.supported_corpora)
            total_parsed = len(self.uvi.loaded_corpora)
            statistics['overall_statistics']['parsing_success_rate'] = (
                total_parsed / total_supported * 100 if total_supported > 0 else 0
            )
        
        # Collect statistics for each corpus
        for corpus_name in self.uvi.loaded_corpora:
            if corpus_name in self.uvi.corpora_data:
                corpus_data = self.uvi.corpora_data[corpus_name]
                corpus_stats = self._extract_corpus_statistics(corpus_name, corpus_data)
                statistics['corpus_statistics'][corpus_name] = corpus_stats
                
        # Add parsing statistics from our tracking
        for corpus_name, stats in self.parsing_statistics.items():
            if corpus_name in statistics['corpus_statistics']:
                statistics['corpus_statistics'][corpus_name]['parsing_metadata'] = stats
            else:
                statistics['corpus_statistics'][corpus_name] = {'parsing_metadata': stats}
                
        # Performance metrics
        statistics['parsing_performance'] = self._calculate_parsing_performance()
        
        # Error summary
        statistics['error_summary'] = self._summarize_parsing_errors()
        
        return statistics
        
    def validate_parsed_data(self, corpus_name: str) -> Dict[str, Any]:
        """
        Validate parsed corpus data using CorpusParser error handling.
        
        Args:
            corpus_name (str): Name of corpus to validate
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_result = {
            'corpus_name': corpus_name,
            'validation_timestamp': self._get_timestamp(),
            'validation_method': 'CorpusParser_integrated',
            'valid': False
        }
        
        # Check if corpus is loaded
        if corpus_name not in self.uvi.loaded_corpora:
            validation_result['error'] = f'Corpus {corpus_name} is not loaded'
            return validation_result
            
        # Check if data exists
        if corpus_name not in self.uvi.corpora_data:
            validation_result['error'] = f'No data available for {corpus_name}'
            return validation_result
            
        corpus_data = self.uvi.corpora_data[corpus_name]
        
        # Use CorpusParser validation if available
        if self.corpus_parser and hasattr(self.corpus_parser, 'validate_parsed_data'):
            try:
                parser_validation = self.corpus_parser.validate_parsed_data(corpus_name, corpus_data)
                validation_result.update(parser_validation)
            except Exception as e:
                validation_result['parser_validation_error'] = str(e)
                
        # Perform additional validation checks
        validation_checks = self._perform_validation_checks(corpus_name, corpus_data)
        validation_result['validation_checks'] = validation_checks
        
        # Determine overall validity
        validation_result['valid'] = self._determine_overall_validity(validation_result)
        
        return validation_result
        
    def get_parser_capabilities(self) -> Dict[str, Any]:
        """
        Get information about parser capabilities and supported formats.
        
        Returns:
            Dict[str, Any]: Parser capabilities information
        """
        capabilities = {
            'parser_available': self.corpus_parser is not None,
            'supported_corpora': list(self.parser_methods.keys()),
            'parsing_features': [],
            'error_handling': True,
            'statistics_tracking': True,
            'caching_enabled': True
        }
        
        if self.corpus_parser:
            # Get CorpusParser capabilities
            capabilities['parsing_features'] = [
                'xml_parsing',
                'json_parsing', 
                'csv_parsing',
                'error_recovery',
                'statistics_generation',
                'validation_support'
            ]
            
            # Add parser-specific information
            capabilities['parser_info'] = {
                'parser_class': self.corpus_parser.__class__.__name__,
                'error_handlers_available': self._check_error_handlers(),
                'corpus_paths_configured': bool(getattr(self.corpus_parser, 'corpus_paths', {}))
            }
        else:
            capabilities['limitation'] = 'CorpusParser not available - limited parsing functionality'
            
        return capabilities
        
    def clear_parsing_cache(self, corpus_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Clear parsing cache for specified corpora or all corpora.
        
        Args:
            corpus_names (Optional[List[str]]): Specific corpora to clear, None for all
            
        Returns:
            Dict[str, Any]: Cache clearing results
        """
        clear_result = {
            'clear_timestamp': self._get_timestamp(),
            'cleared_corpora': [],
            'total_cleared': 0
        }
        
        if corpus_names is None:
            # Clear all cache
            cleared_corpora = list(self.parsing_cache.keys())
            self.parsing_cache.clear()
            clear_result['cleared_corpora'] = cleared_corpora
            clear_result['total_cleared'] = len(cleared_corpora)
            clear_result['clear_scope'] = 'all'
        else:
            # Clear specific corpora
            for corpus_name in corpus_names:
                if corpus_name in self.parsing_cache:
                    del self.parsing_cache[corpus_name]
                    clear_result['cleared_corpora'].append(corpus_name)
                    
            clear_result['total_cleared'] = len(clear_result['cleared_corpora'])
            clear_result['clear_scope'] = 'selective'
            
        self.logger.info(f"Cleared parsing cache for {clear_result['total_cleared']} corpora")
        
        return clear_result
    
    # Private helper methods
    
    def _initialize_parser_methods(self) -> Dict[str, Optional[Callable]]:
        """Initialize mapping of corpus names to CorpusParser methods."""
        parser_methods = {}
        
        if not self.corpus_parser:
            return parser_methods
            
        # Map corpus names to CorpusParser methods
        method_mapping = {
            'verbnet': 'parse_verbnet_files',
            'framenet': 'parse_framenet_files',
            'propbank': 'parse_propbank_files',
            'ontonotes': 'parse_ontonotes_files',
            'wordnet': 'parse_wordnet_files',
            'bso': 'parse_bso_mappings',
            'semnet': 'parse_semnet_data',
            'reference_docs': 'parse_reference_docs',
            'vn_api': 'parse_vn_api_files'
        }
        
        for corpus_name, method_name in method_mapping.items():
            method = getattr(self.corpus_parser, method_name, None)
            if method and callable(method):
                parser_methods[corpus_name] = method
            else:
                self.logger.warning(f"Parser method {method_name} not available for {corpus_name}")
                
        return parser_methods
        
    def _error_result(self, corpus_name: str, error_message: str) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            'corpus_name': corpus_name,
            'error': error_message,
            'parsing_timestamp': self._get_timestamp(),
            'parsing_successful': False,
            'statistics': {
                'total_files': 0,
                'parsed_files': 0,
                'error_files': 1
            }
        }
        
    def _handle_parsing_errors(self, corpus_name: str, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parsing errors with detailed error information."""
        self.logger.error(f"Parsing failed for {corpus_name}: {error_info.get('error', 'Unknown error')}")
        
        error_result = {
            'corpus_name': corpus_name,
            'parsing_successful': False,
            'parsing_timestamp': self._get_timestamp(),
            'error_info': error_info,
            'statistics': {
                'total_files': 0,
                'parsed_files': 0,
                'error_files': 1,
                'error_details': error_info
            }
        }
        
        # Track error in parsing statistics
        self._track_parsing_error(corpus_name, error_info)
        
        return error_result
        
    def _update_parsing_statistics(self, corpus_name: str, parsed_data: Dict[str, Any]):
        """Update internal parsing statistics tracking."""
        if corpus_name not in self.parsing_statistics:
            self.parsing_statistics[corpus_name] = {
                'first_parsed': self._get_timestamp(),
                'parse_count': 0,
                'last_successful_parse': None,
                'errors': []
            }
            
        stats = self.parsing_statistics[corpus_name]
        stats['parse_count'] += 1
        stats['last_parse_attempt'] = self._get_timestamp()
        
        if parsed_data and not parsed_data.get('error'):
            stats['last_successful_parse'] = self._get_timestamp()
            stats['last_parse_status'] = 'success'
            
            # Extract parsing statistics from CorpusParser result
            if 'statistics' in parsed_data:
                parser_stats = parsed_data['statistics']
                stats['last_statistics'] = parser_stats
                
        else:
            stats['last_parse_status'] = 'failed'
            if parsed_data.get('error'):
                stats['errors'].append({
                    'timestamp': self._get_timestamp(),
                    'error': parsed_data['error']
                })
                
    def _track_parsing_error(self, corpus_name: str, error_info: Dict[str, Any]):
        """Track parsing error in statistics."""
        if corpus_name not in self.parsing_statistics:
            self.parsing_statistics[corpus_name] = {
                'parse_count': 0,
                'errors': []
            }
            
        self.parsing_statistics[corpus_name]['errors'].append({
            'timestamp': self._get_timestamp(),
            'error_info': error_info
        })
        
    def _extract_corpus_statistics(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract statistics from parsed corpus data."""
        stats = {
            'corpus_name': corpus_name,
            'data_available': bool(corpus_data),
            'data_size': len(str(corpus_data)) if corpus_data else 0
        }
        
        # Add CorpusParser statistics if available
        if isinstance(corpus_data, dict) and 'statistics' in corpus_data:
            parser_stats = corpus_data['statistics']
            stats['parser_statistics'] = parser_stats
            
        # Add corpus-specific statistics
        if corpus_name == 'verbnet' and 'classes' in corpus_data:
            stats['total_classes'] = len(corpus_data['classes'])
        elif corpus_name == 'framenet' and 'frames' in corpus_data:
            stats['total_frames'] = len(corpus_data['frames'])
        elif corpus_name == 'propbank' and 'predicates' in corpus_data:
            stats['total_predicates'] = len(corpus_data['predicates'])
        elif isinstance(corpus_data, dict):
            # Generic statistics for unknown corpus types
            stats['top_level_keys'] = list(corpus_data.keys())
            stats['total_top_level_items'] = len(corpus_data)
            
        return stats
        
    def _calculate_parsing_performance(self) -> Dict[str, Any]:
        """Calculate parsing performance metrics."""
        performance = {
            'cache_hit_ratio': 0.0,
            'average_parse_attempts': 0.0,
            'error_rate': 0.0,
            'most_problematic_corpus': None,
            'most_reliable_corpus': None
        }
        
        if not self.parsing_statistics:
            return performance
            
        total_parses = 0
        total_errors = 0
        corpus_reliability = {}
        
        for corpus_name, stats in self.parsing_statistics.items():
            parse_count = stats.get('parse_count', 0)
            error_count = len(stats.get('errors', []))
            
            total_parses += parse_count
            total_errors += error_count
            
            if parse_count > 0:
                corpus_reliability[corpus_name] = (parse_count - error_count) / parse_count
                
        # Calculate metrics
        if total_parses > 0:
            performance['error_rate'] = (total_errors / total_parses) * 100
            performance['average_parse_attempts'] = total_parses / len(self.parsing_statistics)
            
        # Find most/least reliable corpora
        if corpus_reliability:
            most_reliable = max(corpus_reliability.items(), key=lambda x: x[1])
            least_reliable = min(corpus_reliability.items(), key=lambda x: x[1])
            
            performance['most_reliable_corpus'] = {
                'corpus': most_reliable[0],
                'reliability': most_reliable[1]
            }
            performance['most_problematic_corpus'] = {
                'corpus': least_reliable[0],
                'reliability': least_reliable[1]
            }
            
        # Calculate cache efficiency
        cached_corpora = len(self.parsing_cache)
        loaded_corpora = len(self.uvi.loaded_corpora)
        
        if loaded_corpora > 0:
            performance['cache_hit_ratio'] = (cached_corpora / loaded_corpora) * 100
            
        return performance
        
    def _summarize_parsing_errors(self) -> Dict[str, Any]:
        """Summarize parsing errors across all corpora."""
        error_summary = {
            'total_errors': 0,
            'errors_by_corpus': {},
            'common_error_types': {},
            'recent_errors': []
        }
        
        for corpus_name, stats in self.parsing_statistics.items():
            errors = stats.get('errors', [])
            error_count = len(errors)
            
            if error_count > 0:
                error_summary['total_errors'] += error_count
                error_summary['errors_by_corpus'][corpus_name] = error_count
                
                # Analyze error types
                for error in errors:
                    error_message = error.get('error_info', {}).get('error', 'unknown')
                    error_type = self._classify_error_type(error_message)
                    error_summary['common_error_types'][error_type] = (
                        error_summary['common_error_types'].get(error_type, 0) + 1
                    )
                    
                # Add recent errors
                recent_errors = sorted(errors, key=lambda x: x.get('timestamp', ''), reverse=True)[:3]
                for error in recent_errors:
                    error_summary['recent_errors'].append({
                        'corpus': corpus_name,
                        'timestamp': error.get('timestamp'),
                        'error': error.get('error_info', {}).get('error', 'unknown')
                    })
                    
        return error_summary
        
    def _classify_error_type(self, error_message: str) -> str:
        """Classify error type based on error message."""
        error_lower = error_message.lower()
        
        if 'file not found' in error_lower or 'no such file' in error_lower:
            return 'file_not_found'
        elif 'permission denied' in error_lower:
            return 'permission_error'
        elif 'xml' in error_lower and 'parse' in error_lower:
            return 'xml_parsing_error'
        elif 'json' in error_lower and 'decode' in error_lower:
            return 'json_parsing_error'
        elif 'encoding' in error_lower:
            return 'encoding_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        elif 'memory' in error_lower:
            return 'memory_error'
        else:
            return 'unknown_error'
            
    def _perform_validation_checks(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform additional validation checks on parsed data."""
        checks = {
            'data_structure_check': self._check_data_structure(corpus_name, corpus_data),
            'completeness_check': self._check_data_completeness(corpus_name, corpus_data),
            'consistency_check': self._check_data_consistency(corpus_name, corpus_data)
        }
        
        return checks
        
    def _check_data_structure(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if data structure matches expected format for corpus type."""
        structure_check = {
            'valid': True,
            'issues': []
        }
        
        # Expected structures for different corpora
        expected_structures = {
            'verbnet': ['classes'],
            'framenet': ['frames'],
            'propbank': ['predicates'],
            'ontonotes': ['entries', 'senses'],
            'wordnet': ['synsets']
        }
        
        expected_keys = expected_structures.get(corpus_name, [])
        
        if expected_keys:
            for key in expected_keys:
                if key not in corpus_data:
                    structure_check['valid'] = False
                    structure_check['issues'].append(f'Missing expected key: {key}')
                elif not corpus_data[key]:
                    structure_check['issues'].append(f'Empty data for key: {key}')
                    
        return structure_check
        
    def _check_data_completeness(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness."""
        completeness_check = {
            'complete': True,
            'completeness_score': 0.0,
            'issues': []
        }
        
        if not corpus_data:
            completeness_check['complete'] = False
            completeness_check['issues'].append('No data available')
            return completeness_check
            
        # Calculate completeness score based on data richness
        total_keys = len(corpus_data)
        non_empty_keys = sum(1 for v in corpus_data.values() if v)
        
        if total_keys > 0:
            completeness_check['completeness_score'] = (non_empty_keys / total_keys) * 100
            
        if completeness_check['completeness_score'] < 80:
            completeness_check['complete'] = False
            completeness_check['issues'].append(f'Low completeness score: {completeness_check["completeness_score"]:.1f}%')
            
        return completeness_check
        
    def _check_data_consistency(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consistency."""
        consistency_check = {
            'consistent': True,
            'issues': []
        }
        
        # Perform corpus-specific consistency checks
        if corpus_name == 'verbnet':
            consistency_check.update(self._check_verbnet_consistency(corpus_data))
        elif corpus_name == 'framenet':
            consistency_check.update(self._check_framenet_consistency(corpus_data))
        elif corpus_name == 'propbank':
            consistency_check.update(self._check_propbank_consistency(corpus_data))
            
        return consistency_check
        
    def _check_verbnet_consistency(self, verbnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check VerbNet-specific data consistency."""
        consistency = {
            'consistent': True,
            'issues': []
        }
        
        if 'classes' not in verbnet_data:
            consistency['consistent'] = False
            consistency['issues'].append('Missing classes structure')
            return consistency
            
        classes = verbnet_data['classes']
        
        for class_id, class_data in classes.items():
            if not isinstance(class_data, dict):
                consistency['issues'].append(f'Class {class_id} data is not a dictionary')
                continue
                
            # Check for required fields
            if 'members' not in class_data:
                consistency['issues'].append(f'Class {class_id} missing members')
                
        if consistency['issues']:
            consistency['consistent'] = len(consistency['issues']) < len(classes) * 0.1
            
        return consistency
        
    def _check_framenet_consistency(self, framenet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check FrameNet-specific data consistency."""
        consistency = {
            'consistent': True,
            'issues': []
        }
        
        if 'frames' not in framenet_data:
            consistency['consistent'] = False
            consistency['issues'].append('Missing frames structure')
            return consistency
            
        frames = framenet_data['frames']
        
        for frame_name, frame_data in frames.items():
            if not isinstance(frame_data, dict):
                consistency['issues'].append(f'Frame {frame_name} data is not a dictionary')
                
        if consistency['issues']:
            consistency['consistent'] = len(consistency['issues']) < len(frames) * 0.1
            
        return consistency
        
    def _check_propbank_consistency(self, propbank_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PropBank-specific data consistency."""
        consistency = {
            'consistent': True,
            'issues': []
        }
        
        if 'predicates' not in propbank_data:
            consistency['consistent'] = False
            consistency['issues'].append('Missing predicates structure')
            return consistency
            
        predicates = propbank_data['predicates']
        
        for pred_lemma, pred_data in predicates.items():
            if not isinstance(pred_data, dict):
                consistency['issues'].append(f'Predicate {pred_lemma} data is not a dictionary')
                
        if consistency['issues']:
            consistency['consistent'] = len(consistency['issues']) < len(predicates) * 0.1
            
        return consistency
        
    def _determine_overall_validity(self, validation_result: Dict[str, Any]) -> bool:
        """Determine overall validity from validation checks."""
        if 'error' in validation_result:
            return False
            
        validation_checks = validation_result.get('validation_checks', {})
        
        # All major checks must pass
        structure_valid = validation_checks.get('data_structure_check', {}).get('valid', False)
        completeness_valid = validation_checks.get('completeness_check', {}).get('complete', False)
        consistency_valid = validation_checks.get('consistency_check', {}).get('consistent', False)
        
        return structure_valid and completeness_valid and consistency_valid
        
    def _check_error_handlers(self) -> bool:
        """Check if CorpusParser has error handling decorators."""
        if not self.corpus_parser:
            return False
            
        # Check if parser methods have error handling
        sample_methods = ['parse_verbnet_files', 'parse_framenet_files']
        
        for method_name in sample_methods:
            method = getattr(self.corpus_parser, method_name, None)
            if method and hasattr(method, '__wrapped__'):
                # Method has decorators (likely error handlers)
                return True
                
        return False
    
    def __str__(self) -> str:
        """String representation of ParsingEngine."""
        return f"ParsingEngine(corpora={len(self.uvi.loaded_corpora)}, parser_enabled={self.corpus_parser is not None}, cached={len(self.parsing_cache)})"