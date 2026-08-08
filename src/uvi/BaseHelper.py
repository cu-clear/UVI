"""
BaseHelper Abstract Class

Abstract base class for all UVI helper classes. Provides common functionality
and integration patterns for accessing CorpusLoader components and UVI data.

All helper classes inherit from this base to ensure consistent access patterns
and shared dependency management.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Set
import logging
from datetime import datetime


class BaseHelper(ABC):
    """
    Abstract base class for all UVI helper classes.
    
    Provides common functionality and integration patterns for accessing
    CorpusLoader components and UVI data. All helper classes inherit from
    this base to ensure consistent access patterns and shared dependency
    management.
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize BaseHelper with access to UVI instance and its components.
        
        Args:
            uvi_instance: The main UVI instance containing all corpus data and components
        """
        self.uvi = uvi_instance
        self.corpora_data = uvi_instance.corpora_data
        self.loaded_corpora = uvi_instance.loaded_corpora
        self.corpus_loader = uvi_instance.corpus_loader
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the helper class."""
        logger = logging.getLogger(f"uvi.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        return datetime.now().isoformat()
        
    def _get_full_corpus_name(self, corpus_name: str) -> str:
        """
        Convert abbreviated corpus name to full name if needed.
        
        Args:
            corpus_name (str): Potentially abbreviated corpus name
            
        Returns:
            str: Full corpus name
        """
        # Mapping for common abbreviations
        abbreviation_map = {
            'vn': 'verbnet',
            'fn': 'framenet', 
            'pb': 'propbank',
            'on': 'ontonotes',
            'wn': 'wordnet',
            'ref': 'reference_docs',
            'api': 'vn_api'
        }
        
        return abbreviation_map.get(corpus_name.lower(), corpus_name.lower())
        
    def _validate_corpus_loaded(self, corpus_name: str) -> bool:
        """
        Validate that a corpus is loaded and available.
        
        Args:
            corpus_name (str): Name of corpus to validate
            
        Returns:
            bool: True if corpus is loaded and has data
        """
        full_name = self._get_full_corpus_name(corpus_name)
        return (full_name in self.loaded_corpora and 
                full_name in self.corpora_data and
                bool(self.corpora_data[full_name]))
                
    def _get_corpus_data(self, corpus_name: str) -> Dict[str, Any]:
        """
        Get corpus data with validation.
        
        Args:
            corpus_name (str): Name of corpus to retrieve
            
        Returns:
            Dict[str, Any]: Corpus data or empty dict if not available
        """
        full_name = self._get_full_corpus_name(corpus_name)
        if self._validate_corpus_loaded(full_name):
            return self.corpora_data[full_name]
        else:
            self.logger.warning(f"Corpus {full_name} is not loaded or has no data")
            return {}
            
    def _get_available_corpora(self) -> List[str]:
        """
        Get list of currently loaded and available corpora.
        
        Returns:
            List[str]: List of loaded corpus names
        """
        return list(self.loaded_corpora)
        
    def _ensure_corpus_loaded(self, corpus_name: str) -> bool:
        """
        Ensure a corpus is loaded, attempt to load if not.
        
        Args:
            corpus_name (str): Name of corpus to ensure is loaded
            
        Returns:
            bool: True if corpus is now loaded, False otherwise
        """
        full_name = self._get_full_corpus_name(corpus_name)
        
        if self._validate_corpus_loaded(full_name):
            return True
            
        # Attempt to load the corpus
        try:
            if hasattr(self.uvi, '_load_corpus'):
                self.uvi._load_corpus(full_name)
                return self._validate_corpus_loaded(full_name)
            else:
                self.logger.error(f"Cannot load corpus {full_name}: UVI load method not available")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load corpus {full_name}: {str(e)}")
            return False
            
    def _safe_get(self, data: Dict, *keys, default=None) -> Any:
        """
        Safely get nested dictionary values.
        
        Args:
            data (Dict): Dictionary to traverse
            *keys: Keys to traverse in order
            default: Default value if key path doesn't exist
            
        Returns:
            Any: Value at key path or default
        """
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data
        
    def _filter_dict_keys(self, data: Dict, allowed_keys: Set[str]) -> Dict:
        """
        Filter dictionary to only include specified keys.
        
        Args:
            data (Dict): Source dictionary
            allowed_keys (Set[str]): Set of allowed keys
            
        Returns:
            Dict: Filtered dictionary
        """
        return {k: v for k, v in data.items() if k in allowed_keys}
        
    def _merge_dicts(self, *dicts: Dict) -> Dict:
        """
        Merge multiple dictionaries with later ones taking precedence.
        
        Args:
            *dicts: Dictionaries to merge
            
        Returns:
            Dict: Merged dictionary
        """
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result
        
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the helper class."""
        pass
        
    def __repr__(self) -> str:
        """Detailed representation of the helper class."""
        return f"{self.__class__.__name__}(loaded_corpora={len(self.loaded_corpora)})"