"""
File System Utilities

Provides utilities for managing corpus files including path detection,
safe file reading, and corpus structure management.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import os
import json
import csv
import mimetypes
from datetime import datetime
import hashlib


class CorpusFileManager:
    """
    Manager for corpus file operations and directory structure detection.
    
    Handles safe file operations, directory structure detection, and
    corpus file management tasks.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize corpus file manager.
        
        Args:
            base_path (Path): Base path for corpus directories
        """
        self.base_path = Path(base_path)
        self.file_cache = {}
        self.structure_cache = {}
        self.corpus_paths = self._detect_corpus_paths()
    
    def detect_corpus_structure(self) -> Dict[str, Any]:
        """
        Detect the structure of corpus directories.
        
        Returns:
            dict: Detected corpus structure information
        """
        if not self.base_path.exists():
            return {'error': f'Base path does not exist: {self.base_path}'}
        
        structure = {
            'base_path': str(self.base_path),
            'detected_corpora': {},
            'unknown_directories': [],
            'file_counts': {},
            'total_files': 0
        }
        
        # Known corpus directory patterns
        corpus_patterns = {
            'verbnet': ['verbnet', 'vn', 'verbnet3.4', 'verbnet-3.4'],
            'framenet': ['framenet', 'fn', 'framenet1.7', 'framenet-1.7'],
            'propbank': ['propbank', 'pb', 'propbank3.4', 'propbank-3.4'],
            'ontonotes': ['ontonotes', 'on', 'ontonotes5.0', 'ontonotes-5.0'],
            'wordnet': ['wordnet', 'wn', 'wordnet3.1', 'wordnet-3.1'],
            'bso': ['bso', 'BSO', 'basic_semantic_ontology'],
            'semnet': ['semnet', 'semnet20180205', 'semantic_network'],
            'reference_docs': ['reference_docs', 'ref_docs', 'docs', 'references'],
            'vn_api': ['vn_api', 'verbnet_api', 'vn-api']
        }
        
        # Scan directories
        for item in self.base_path.iterdir():
            if item.is_dir():
                corpus_type = self._identify_corpus_type(item.name.lower(), corpus_patterns)
                
                if corpus_type:
                    corpus_info = self._analyze_corpus_directory(item, corpus_type)
                    structure['detected_corpora'][corpus_type] = corpus_info
                    structure['file_counts'][corpus_type] = corpus_info.get('file_count', 0)
                    structure['total_files'] += corpus_info.get('file_count', 0)
                else:
                    structure['unknown_directories'].append(str(item))
        
        self.structure_cache = structure
        return structure
    
    def _identify_corpus_type(self, dir_name: str, patterns: Dict[str, List[str]]) -> Optional[str]:
        """Identify corpus type from directory name."""
        for corpus_type, pattern_list in patterns.items():
            if any(pattern in dir_name for pattern in pattern_list):
                return corpus_type
        return None
    
    def _analyze_corpus_directory(self, corpus_path: Path, corpus_type: str) -> Dict[str, Any]:
        """Analyze a corpus directory structure."""
        analysis = {
            'path': str(corpus_path),
            'type': corpus_type,
            'exists': corpus_path.exists(),
            'readable': os.access(corpus_path, os.R_OK),
            'file_count': 0,
            'file_types': {},
            'subdirectories': [],
            'size_mb': 0.0,
            'last_modified': None
        }
        
        if not corpus_path.exists():
            return analysis
        
        try:
            # Get modification time
            analysis['last_modified'] = datetime.fromtimestamp(corpus_path.stat().st_mtime).isoformat()
            
            # Scan files and subdirectories
            total_size = 0
            for item in corpus_path.rglob('*'):
                if item.is_file():
                    analysis['file_count'] += 1
                    
                    # Track file types
                    suffix = item.suffix.lower()
                    if suffix:
                        analysis['file_types'][suffix] = analysis['file_types'].get(suffix, 0) + 1
                    
                    # Calculate size
                    try:
                        total_size += item.stat().st_size
                    except (OSError, IOError):
                        pass
                
                elif item.is_dir() and item.parent == corpus_path:
                    analysis['subdirectories'].append(item.name)
            
            analysis['size_mb'] = round(total_size / (1024 * 1024), 2)
            
        except (OSError, IOError) as e:
            analysis['error'] = f'Error analyzing directory: {e}'
        
        return analysis
    
    def get_corpus_files(self, corpus_type: str, file_pattern: str = '*') -> List[Path]:
        """
        Get list of files in a corpus directory.
        
        Args:
            corpus_type (str): Type of corpus
            file_pattern (str): File pattern to match
            
        Returns:
            list: List of file paths
        """
        structure = self.structure_cache or self.detect_corpus_structure()
        corpus_info = structure.get('detected_corpora', {}).get(corpus_type)
        
        if not corpus_info:
            return []
        
        corpus_path = Path(corpus_info['path'])
        if not corpus_path.exists():
            return []
        
        try:
            if corpus_type == 'framenet':
                # FrameNet has special structure with frames in subdirectory
                frame_dir = corpus_path / 'frame'
                if frame_dir.exists():
                    return list(frame_dir.glob(file_pattern))
                else:
                    return list(corpus_path.glob(file_pattern))
            else:
                return list(corpus_path.glob(file_pattern))
        except (OSError, IOError):
            return []
    
    def safe_read_file(self, file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
        """
        Safely read a file with error handling.
        
        Args:
            file_path (Path): Path to file
            encoding (str): File encoding
            
        Returns:
            str: File contents or None if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (OSError, IOError, UnicodeDecodeError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def safe_read_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Safely read a JSON file.
        
        Args:
            file_path (Path): Path to JSON file
            
        Returns:
            dict: JSON data or None if error
        """
        content = self.safe_read_file(file_path)
        if content is None:
            return None
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {file_path}: {e}")
            return None
    
    def safe_read_csv(self, file_path: Path, delimiter: str = ',') -> Optional[List[Dict[str, Any]]]:
        """
        Safely read a CSV file.
        
        Args:
            file_path (Path): Path to CSV file
            delimiter (str): CSV delimiter
            
        Returns:
            list: CSV data as list of dictionaries or None if error
        """
        try:
            rows = []
            with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
                # Try to detect delimiter if not specified
                if delimiter == ',':
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    if '\t' in sample and sample.count('\t') > sample.count(','):
                        delimiter = '\t'
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    rows.append(dict(row))
            
            return rows
        except (OSError, IOError, csv.Error) as e:
            print(f"Error reading CSV file {file_path}: {e}")
            return None
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get detailed information about a file.
        
        Args:
            file_path (Path): Path to file
            
        Returns:
            dict: File information
        """
        info = {
            'path': str(file_path),
            'name': file_path.name,
            'suffix': file_path.suffix,
            'exists': file_path.exists(),
            'readable': False,
            'size_bytes': 0,
            'size_mb': 0.0,
            'last_modified': None,
            'mime_type': None,
            'checksum': None
        }
        
        if not file_path.exists():
            return info
        
        try:
            stat_info = file_path.stat()
            
            info.update({
                'readable': os.access(file_path, os.R_OK),
                'size_bytes': stat_info.st_size,
                'size_mb': round(stat_info.st_size / (1024 * 1024), 2),
                'last_modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            })
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            info['mime_type'] = mime_type
            
            # Calculate checksum for small files
            if stat_info.st_size < 10 * 1024 * 1024:  # Less than 10MB
                content = self.safe_read_file(file_path, encoding='utf-8')
                if content:
                    info['checksum'] = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        except (OSError, IOError) as e:
            info['error'] = f'Error getting file info: {e}'
        
        return info
    
    def find_schema_files(self, corpus_path: Path) -> List[Path]:
        """
        Find schema files (DTD, XSD) in a corpus directory.
        
        Args:
            corpus_path (Path): Path to corpus directory
            
        Returns:
            list: List of schema file paths
        """
        schema_files = []
        
        if not corpus_path.exists():
            return schema_files
        
        # Common schema file patterns
        patterns = ['*.dtd', '*.xsd', '*.rng', '*schema*']
        
        for pattern in patterns:
            schema_files.extend(corpus_path.glob(pattern))
            schema_files.extend(corpus_path.glob(f'**/{pattern}'))
        
        return list(set(schema_files))  # Remove duplicates
    
    def backup_file(self, file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Create a backup of a file.
        
        Args:
            file_path (Path): Path to file to backup
            backup_dir (Path): Directory for backup (default: same directory)
            
        Returns:
            Path: Path to backup file or None if error
        """
        if not file_path.exists():
            return None
        
        if backup_dir is None:
            backup_dir = file_path.parent
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except (OSError, IOError) as e:
            print(f"Error creating backup: {e}")
            return None
    
    def validate_file_integrity(self, file_path: Path, expected_checksum: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate file integrity.
        
        Args:
            file_path (Path): Path to file
            expected_checksum (str): Expected MD5 checksum
            
        Returns:
            dict: Validation results
        """
        validation = {
            'file_exists': False,
            'readable': False,
            'checksum_valid': None,
            'current_checksum': None,
            'file_size': 0,
            'errors': []
        }
        
        if not file_path.exists():
            validation['errors'].append('File does not exist')
            return validation
        
        validation['file_exists'] = True
        
        if not os.access(file_path, os.R_OK):
            validation['errors'].append('File is not readable')
            return validation
        
        validation['readable'] = True
        
        try:
            validation['file_size'] = file_path.stat().st_size
            
            # Calculate checksum
            content = self.safe_read_file(file_path)
            if content:
                current_checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
                validation['current_checksum'] = current_checksum
                
                if expected_checksum:
                    validation['checksum_valid'] = (current_checksum == expected_checksum)
                    if not validation['checksum_valid']:
                        validation['errors'].append('Checksum mismatch')
        
        except Exception as e:
            validation['errors'].append(f'Error validating file: {e}')
        
        return validation

    def _detect_corpus_paths(self) -> Dict[str, Path]:
        """Detect corpus directories and return mapping."""
        corpus_paths = {}
        if not self.base_path.exists():
            return corpus_paths
            
        for item in self.base_path.iterdir():
            if item.is_dir():
                name = item.name.lower()
                # Map directory names to standard corpus names
                if name == 'verbnet':
                    corpus_paths['verbnet'] = item
                elif name == 'framenet':
                    corpus_paths['framenet'] = item
                elif name == 'propbank':
                    corpus_paths['propbank'] = item
                elif name == 'ontonotes':
                    corpus_paths['ontonotes'] = item
                elif name == 'wordnet':
                    corpus_paths['wordnet'] = item
                elif name in ['bso', 'BSO']:
                    corpus_paths['bso'] = item
                elif name.startswith('semnet'):
                    corpus_paths['semnet'] = item
                elif name == 'reference_docs':
                    corpus_paths['reference_docs'] = item
                
        return corpus_paths

    def detect_corpus_files(self, corpus_name: str, pattern: str) -> List[Path]:
        """
        Detect files in a corpus directory matching a pattern.
        
        Args:
            corpus_name (str): Name of the corpus
            pattern (str): File pattern to match
            
        Returns:
            list: List of matching file paths
        """
        import glob
        
        corpus_path = self.corpus_paths.get(corpus_name)
        if not corpus_path or not corpus_path.exists():
            return []
            
        # Use corpus_path as base for all patterns
        matches = list(corpus_path.glob(pattern))
            
        return [Path(match) for match in matches if Path(match).is_file()]

    def get_corpus_statistics(self, corpus_name: str) -> Dict[str, Any]:
        """
        Get statistics for a corpus directory.
        
        Args:
            corpus_name (str): Name of the corpus
            
        Returns:
            dict: Statistics about the corpus
        """
        stats = {
            'corpus_name': corpus_name,
            'exists': False,
            'file_count': 0,
            'total_size': 0,
            'file_types': {},
            'last_modified': None
        }
        
        corpus_path = self.corpus_paths.get(corpus_name)
        if not corpus_path or not corpus_path.exists():
            return stats
            
        stats['exists'] = True
        stats['path'] = str(corpus_path)
        
        try:
            files = list(corpus_path.rglob('*'))
            files = [f for f in files if f.is_file()]
            
            stats['file_count'] = len(files)
            stats['total_files'] = len(files)  # For test compatibility
            
            for file_path in files:
                try:
                    file_size = file_path.stat().st_size
                    stats['total_size'] += file_size
                    
                    extension = file_path.suffix.lower()
                    if extension not in stats['file_types']:
                        stats['file_types'][extension] = 0
                    stats['file_types'][extension] += 1
                    
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if not stats['last_modified'] or file_mtime > stats['last_modified']:
                        stats['last_modified'] = file_mtime
                        
                except (OSError, PermissionError):
                    continue
                    
        except (OSError, PermissionError):
            stats['error'] = 'Permission denied or access error'
        
        # Add xml_files count for test compatibility
        stats['xml_files'] = stats['file_types'].get('.xml', 0)
        
        return stats

    def validate_corpus_structure(self, corpus_name: str, required_patterns: List[str]) -> bool:
        """
        Validate that a corpus has required file patterns.
        
        Args:
            corpus_name (str): Name of the corpus
            required_patterns (list): List of required file patterns
            
        Returns:
            bool: True if corpus structure is valid
        """
        corpus_path = self.corpus_paths.get(corpus_name)
        if not corpus_path or not corpus_path.exists():
            return False
            
        for pattern in required_patterns:
            matching_files = self.detect_corpus_files(corpus_name, pattern)
            if not matching_files:
                return False
                
        return True


def detect_corpus_structure(base_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Detect corpus directory structure.
    
    Args:
        base_path: Base path for corpus directories
        
    Returns:
        dict: Detected structure information
    """
    manager = CorpusFileManager(Path(base_path))
    full_structure = manager.detect_corpus_structure()
    
    # For test compatibility, flatten the structure
    flattened = {}
    for corpus_name, corpus_info in full_structure.get('detected_corpora', {}).items():
        corpus_details = {
            'path': corpus_info['path'],
            'type': corpus_info['type'],
            'exists': corpus_info['exists'],
            'readable': corpus_info['readable'],
            'file_count': corpus_info['file_count']
        }
        
        # Add specific file type counts based on corpus type
        file_types = corpus_info.get('file_types', {})
        if corpus_name == 'verbnet':
            corpus_details['xml_files'] = file_types.get('.xml', 0)
            corpus_details['schema_files'] = file_types.get('.xsd', 0) + file_types.get('.dtd', 0)
        elif corpus_name == 'framenet':
            corpus_details['xml_files'] = file_types.get('.xml', 0)
        elif corpus_name == 'wordnet':
            corpus_details['data_files'] = file_types.get('.verb', 0) + file_types.get('.noun', 0) + file_types.get('.adj', 0) + file_types.get('.adv', 0)
            corpus_details['index_files'] = sum(1 for ext in file_types.keys() if 'index' in str(ext))
            
        flattened[corpus_name] = corpus_details
    
    return flattened


def safe_file_read(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read a file with error handling.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        str: File contents or None if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except (OSError, IOError, UnicodeDecodeError) as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def get_file_stats(directory_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get statistics about files in a directory.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        dict: File statistics
    """
    path = Path(directory_path)
    stats = {
        'total_files': 0,
        'total_size_mb': 0.0,
        'file_types': {},
        'largest_file': None,
        'largest_file_size': 0,
        'oldest_file': None,
        'newest_file': None,
        'oldest_date': None,
        'newest_date': None
    }
    
    if not path.exists():
        return stats
    
    total_size = 0
    oldest_time = float('inf')
    newest_time = 0
    
    for file_path in path.rglob('*'):
        if file_path.is_file():
            stats['total_files'] += 1
            
            try:
                file_stat = file_path.stat()
                file_size = file_stat.st_size
                mod_time = file_stat.st_mtime
                
                total_size += file_size
                
                # Track file types
                suffix = file_path.suffix.lower()
                if suffix:
                    stats['file_types'][suffix] = stats['file_types'].get(suffix, 0) + 1
                
                # Track largest file
                if file_size > stats['largest_file_size']:
                    stats['largest_file_size'] = file_size
                    stats['largest_file'] = str(file_path)
                
                # Track oldest and newest files
                if mod_time < oldest_time:
                    oldest_time = mod_time
                    stats['oldest_file'] = str(file_path)
                    stats['oldest_date'] = datetime.fromtimestamp(mod_time).isoformat()
                
                if mod_time > newest_time:
                    newest_time = mod_time
                    stats['newest_file'] = str(file_path)
                    stats['newest_date'] = datetime.fromtimestamp(mod_time).isoformat()
            
            except (OSError, IOError):
                # Skip files that can't be accessed
                continue
    
    stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
    
    return stats