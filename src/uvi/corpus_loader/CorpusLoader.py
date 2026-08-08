"""
CorpusLoader Class

A standalone class for loading, parsing, and organizing all corpus data
from file sources (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, 
SemNet, Reference Docs, VN API) with cross-corpus integration.

This class implements comprehensive file-based corpus loading with proper
error handling, schema validation, and cross-corpus reference building.
"""

import xml.etree.ElementTree as ET
import json
import csv
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import logging
from .CorpusParser import CorpusParser
from .CorpusCollectionBuilder import CorpusCollectionBuilder
from .CorpusCollectionValidator import CorpusCollectionValidator
from .CorpusCollectionAnalyzer import CorpusCollectionAnalyzer


class CorpusLoader:
    """
    A standalone class for loading, parsing, and organizing all corpus data
    from file sources (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, 
    SemNet, Reference Docs, VN API) with cross-corpus integration.
    """
    
    def __init__(self, corpora_path: str = 'corpora/'):
        """
        Initialize CorpusLoader with corpus file paths.
        
        Args:
            corpora_path (str): Path to the corpora directory
        """
        self.corpora_path = Path(corpora_path)
        self.loaded_data = {}
        self.corpus_paths = {}
        self.load_status = {}
        self.build_metadata = {}
        self.reference_collections = {}
        self.cross_references = {}
        self.bso_mappings = {}
        self.parser = None  # Initialized after paths are detected
        self.builder = None  # Initialized after data is loaded
        self.validator = None  # Initialized after data is loaded
        self.analyzer = None  # Initialized after data is loaded
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Supported corpora with their expected directory names
        self.corpus_mappings = {
            'verbnet': ['verbnet', 'vn', 'verbnet3.4'],
            'framenet': ['framenet', 'fn', 'framenet1.7'],
            'propbank': ['propbank', 'pb', 'propbank3.4'],
            'ontonotes': ['ontonotes', 'on', 'ontonotes5.0'],
            'wordnet': ['wordnet', 'wn', 'wordnet3.1'],
            'bso': ['BSO', 'bso', 'basic_semantic_ontology'],
            'semnet': ['semnet20180205', 'semnet', 'semantic_network'],
            'reference_docs': ['reference_docs', 'ref_docs', 'docs'],
            'vn_api': ['vn_api', 'verbnet_api', 'vn']
        }
        
        # Auto-detect corpus paths
        self._detect_corpus_paths()
        
        # Initialize parser after paths are detected
        self._init_parser()
    
    def _detect_corpus_paths(self) -> None:
        """
        Automatically detect corpus paths from the base directory.
        """
        if not self.corpora_path.exists():
            self.logger.warning(f"Corpora directory not found: {self.corpora_path}")
            return
        
        for corpus_name, possible_dirs in self.corpus_mappings.items():
            corpus_path = None
            for dir_name in possible_dirs:
                candidate_path = self.corpora_path / dir_name
                if candidate_path.exists() and candidate_path.is_dir():
                    corpus_path = candidate_path
                    break
            
            if corpus_path:
                self.corpus_paths[corpus_name] = corpus_path
                self.logger.info(f"Found {corpus_name} corpus at: {corpus_path}")
            else:
                self.logger.warning(f"Corpus {corpus_name} not found in {self.corpora_path}")
    
    def get_corpus_paths(self) -> Dict[str, str]:
        """
        Get automatically detected corpus paths.
        
        Returns:
            dict: Paths to all detected corpus directories and files
        """
        return {name: str(path) for name, path in self.corpus_paths.items()}
    
    def load_all_corpora(self) -> Dict[str, Any]:
        """
        Load and parse all available corpus files.
        
        Returns:
            dict: Loading status and statistics for each corpus
        """
        self.logger.info("Starting to load all available corpora...")
        
        loading_results = {}
        
        for corpus_name in self.corpus_mappings.keys():
            if corpus_name in self.corpus_paths:
                try:
                    start_time = datetime.now()
                    result = self.load_corpus(corpus_name)
                    end_time = datetime.now()
                    
                    loading_results[corpus_name] = self._create_loading_result(
                        'success',
                        load_time=(end_time - start_time).total_seconds(),
                        data_keys=list(result.keys()) if isinstance(result, dict) else [],
                        timestamp=start_time.isoformat()
                    )
                    self.logger.info(f"Successfully loaded {corpus_name}")
                    
                except Exception as e:
                    loading_results[corpus_name] = self._create_loading_result(
                        'error',
                        error=str(e)
                    )
                    self.logger.error(f"Failed to load {corpus_name}: {e}")
            else:
                loading_results[corpus_name] = self._create_loading_result('not_found')
        
        # Build reference collections after loading
        self.build_reference_collections()
        
        return loading_results
    
    def load_corpus(self, corpus_name: str) -> Dict[str, Any]:
        """
        Load a specific corpus by name.
        
        Args:
            corpus_name (str): Name of corpus to load ('verbnet', 'framenet', etc.)
            
        Returns:
            dict: Parsed corpus data with metadata
        """
        if corpus_name not in self.corpus_paths:
            raise FileNotFoundError(f"Corpus {corpus_name} not found in configured paths")
        
        corpus_path = self.corpus_paths[corpus_name]
        
        # Ensure parser is initialized
        self._init_parser()
        
        # Parser method dispatch map
        parser_dispatch = {
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
        
        if corpus_name not in parser_dispatch:
            raise ValueError(f"Unsupported corpus type: {corpus_name}")
        
        # Call the appropriate parser method
        parser_method = getattr(self.parser, parser_dispatch[corpus_name])
        data = parser_method()
        
        # Store BSO mappings for later use if this was a BSO parse
        if corpus_name == 'bso':
            self.bso_mappings = data
        
        self.loaded_data[corpus_name] = data
        self._update_load_status(corpus_name, corpus_path)
        
        return data
    
    # Helper initialization methods
    
    def _init_component(self, component_name: str, component_class, *args):
        """
        Generic initialization method for lazy-loading components.
        
        Args:
            component_name (str): Name of the component attribute
            component_class: Class to instantiate
            *args: Arguments to pass to the constructor
        """
        if not getattr(self, component_name):
            setattr(self, component_name, component_class(*args))
    
    def _init_parser(self):
        """Initialize the CorpusParser if not already initialized."""
        self._init_component('parser', CorpusParser, self.corpus_paths, self.logger)
    
    def _init_builder(self):
        """Initialize the CorpusCollectionBuilder if not already initialized."""
        self._init_component('builder', CorpusCollectionBuilder, self.loaded_data, self.logger)
    
    def _init_validator(self):
        """Initialize the CorpusCollectionValidator if not already initialized."""
        self._init_component('validator', CorpusCollectionValidator, self.loaded_data, self.logger)
    
    def _init_analyzer(self):
        """Initialize the CorpusCollectionAnalyzer if not already initialized."""
        self._init_component('analyzer', CorpusCollectionAnalyzer, 
                           self.loaded_data, self.load_status, self.build_metadata, 
                           self.reference_collections, self.corpus_paths)
    
    # Common operation helper methods
    
    def _update_load_status(self, corpus_name: str, corpus_path: Path) -> None:
        """
        Update load status for a corpus with timestamp and path information.
        
        Args:
            corpus_name (str): Name of the corpus
            corpus_path (Path): Path to the corpus
        """
        self.load_status[corpus_name] = {
            'loaded': True,
            'timestamp': datetime.now().isoformat(),
            'path': str(corpus_path)
        }
    
    def _create_loading_result(self, status: str, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized loading result dictionary.
        
        Args:
            status (str): Status of the loading operation
            **kwargs: Additional key-value pairs to include
            
        Returns:
            dict: Standardized loading result
        """
        result = {
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        result.update(kwargs)
        return result
    
    def _build_with_reference_update(self, build_method_name: str) -> bool:
        """
        Generic method for building collections and updating references.
        
        Args:
            build_method_name (str): Name of the builder method to call
            
        Returns:
            bool: Success status
        """
        self._init_builder()
        build_method = getattr(self.builder, build_method_name)
        result = build_method()
        self.reference_collections = self.builder.reference_collections
        return result
    
    def build_reference_collections(self) -> Dict[str, bool]:
        """
        Build all reference collections for VerbNet components.
        
        Returns:
            dict: Status of reference collection builds
        """
        self._init_builder()
        results = self.builder.build_reference_collections()
        self.reference_collections = self.builder.reference_collections
        return results
    
    def build_predicate_definitions(self) -> bool:
        """
        Build predicate definitions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_with_reference_update('build_predicate_definitions')
    
    def build_themrole_definitions(self) -> bool:
        """
        Build thematic role definitions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_with_reference_update('build_themrole_definitions')
    
    def build_verb_specific_features(self) -> bool:
        """
        Build verb-specific features collection.
        
        Returns:
            bool: Success status
        """
        return self._build_with_reference_update('build_verb_specific_features')
    
    def build_syntactic_restrictions(self) -> bool:
        """
        Build syntactic restrictions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_with_reference_update('build_syntactic_restrictions')
    
    def build_selectional_restrictions(self) -> bool:
        """
        Build selectional restrictions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_with_reference_update('build_selectional_restrictions')
    
    # Validation methods
    
    def validate_collections(self) -> Dict[str, Any]:
        """
        Validate integrity of all collections.
        
        Returns:
            dict: Validation results for each collection
        """
        self._init_validator()
        return self.validator.validate_collections()
    
    def validate_cross_references(self) -> Dict[str, Any]:
        """
        Validate cross-references between collections.
        
        Returns:
            dict: Cross-reference validation results
        """
        self._init_validator()
        return self.validator.validate_cross_references()
    
    # Statistics methods
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all collections.
        
        Returns:
            dict: Statistics for each collection
        """
        self._init_analyzer()
        return self.analyzer.get_collection_statistics()
    
    def get_build_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about last build times and versions.
        
        Returns:
            dict: Build metadata
        """
        self._init_analyzer()
        return self.analyzer.get_build_metadata()