"""
CorpusCollectionAnalyzer Class

A specialized class for analyzing corpus collection data and providing
statistics and metadata about loaded corpora and their relationships.

This class is part of the CorpusLoader refactoring to separate concerns
and improve maintainability.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime


class CorpusCollectionAnalyzer:
    """
    A specialized class for analyzing corpus collection data and providing
    statistics and metadata.
    
    This class handles the analysis of loaded corpus data, generating
    statistics and metadata reports for all loaded collections.
    """
    
    # Mapping of corpus types to their collection fields that need size calculation
    _CORPUS_COLLECTION_FIELDS = {
        'verbnet': ['classes', 'members'],
        'framenet': ['frames', 'lexical_units'],
        'propbank': ['predicates', 'rolesets']
    }
    
    def __init__(self, loaded_data: Dict[str, Any], load_status: Dict[str, Any], 
                 build_metadata: Dict[str, Any], reference_collections: Dict[str, Any],
                 corpus_paths: Dict[str, str]):
        """
        Initialize the CorpusCollectionAnalyzer.
        
        Args:
            loaded_data: Dictionary containing all loaded corpus data
            load_status: Dictionary tracking load status of each corpus
            build_metadata: Dictionary containing build timestamps and metadata
            reference_collections: Dictionary of built reference collections
            corpus_paths: Dictionary mapping corpus names to their file paths
        """
        self.loaded_data = loaded_data
        self.load_status = load_status
        self.build_metadata = build_metadata
        self.reference_collections = reference_collections
        self.corpus_paths = corpus_paths
    
    def _get_collection_size(self, collection: Any) -> int:
        """
        Get the size of a collection, handling different collection types safely.
        
        Args:
            collection: The collection to measure
            
        Returns:
            int: Size of the collection, 0 if not a measurable collection
        """
        return len(collection) if isinstance(collection, (list, dict, set)) else 0
    
    def _calculate_collection_sizes(self, corpus_data: Dict[str, Any], 
                                   field_names: List[str]) -> Dict[str, int]:
        """
        Calculate sizes for specified collection fields in corpus data.
        
        Args:
            corpus_data: The corpus data dictionary
            field_names: List of field names to calculate sizes for
            
        Returns:
            dict: Mapping of field names to their collection sizes
        """
        return {
            field: self._get_collection_size(corpus_data.get(field, {}))
            for field in field_names
        }
    
    def _build_corpus_statistics(self, corpus_name: str, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build statistics for a specific corpus using a common pattern.
        
        Args:
            corpus_name: Name of the corpus
            corpus_data: The corpus data dictionary
            
        Returns:
            dict: Complete statistics for the corpus
        """
        # Get base statistics from corpus data
        stats = corpus_data.get('statistics', {}).copy()
        
        # Add computed collection sizes if this corpus type has defined fields
        if corpus_name in self._CORPUS_COLLECTION_FIELDS:
            collection_fields = self._CORPUS_COLLECTION_FIELDS[corpus_name]
            collection_sizes = self._calculate_collection_sizes(corpus_data, collection_fields)
            stats.update(collection_sizes)
        
        return stats
    
    def _get_corpus_statistics_with_error_handling(self, corpus_name: str, 
                                                  corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get corpus statistics with consistent error handling.
        
        Args:
            corpus_name: Name of the corpus
            corpus_data: The corpus data dictionary
            
        Returns:
            dict: Statistics or error information
        """
        try:
            return self._build_corpus_statistics(corpus_name, corpus_data)
        except Exception as e:
            return {'error': str(e)}
    
    def _build_reference_collection_statistics(self) -> Dict[str, int]:
        """
        Build statistics for reference collections.
        
        Returns:
            dict: Statistics for all reference collections
        """
        return {
            name: self._get_collection_size(collection)
            for name, collection in self.reference_collections.items()
        }
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all collections.
        
        Returns:
            dict: Statistics for each collection
        """
        statistics = {}
        
        # Process each corpus with consistent error handling
        for corpus_name, corpus_data in self.loaded_data.items():
            statistics[corpus_name] = self._get_corpus_statistics_with_error_handling(
                corpus_name, corpus_data
            )
        
        # Add reference collection statistics
        statistics['reference_collections'] = self._build_reference_collection_statistics()
        
        return statistics
    
    def get_build_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about last build times and versions.
        
        Returns:
            dict: Build metadata
        """
        return {
            'build_metadata': self.build_metadata,
            'load_status': self.load_status,
            'corpus_paths': self.corpus_paths,
            'timestamp': datetime.now().isoformat()
        }