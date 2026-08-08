"""
UVI (Unified Verb Index) Package

A comprehensive standalone class providing integrated access to all nine linguistic 
corpora (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, SemNet, Reference Docs, 
VN API) with cross-resource navigation, semantic validation, and hierarchical analysis 
capabilities.

This class implements the universal interface patterns and shared semantic frameworks 
documented in corpora/OVERVIEW.md, enabling seamless cross-corpus integration and validation.
"""

import xml.etree.ElementTree as ET
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import os
from .corpus_loader import CorpusLoader, CorpusParser
from .BaseHelper import BaseHelper
from .SearchEngine import SearchEngine
from .CorpusRetriever import CorpusRetriever
from .CrossReferenceManager import CrossReferenceManager
from .ReferenceDataProvider import ReferenceDataProvider
from .ValidationManager import ValidationManager
from .ExportManager import ExportManager
from .AnalyticsManager import AnalyticsManager
from .ParsingEngine import ParsingEngine


class UVI:
    """
    Unified Verb Index: A comprehensive standalone class providing integrated access 
    to all nine linguistic corpora (VerbNet, FrameNet, PropBank, OntoNotes, WordNet,
    BSO, SemNet, Reference Docs, VN API) with cross-resource navigation, semantic 
    validation, and hierarchical analysis capabilities.
    
    This class implements the universal interface patterns and shared semantic 
    frameworks documented in corpora/OVERVIEW.md, enabling seamless cross-corpus
    integration and validation.
    """
    
    def __init__(self, corpora_path: str = 'corpora/', load_all: bool = True):
        """
        Initialize UVI with corpus file paths for standalone operation.
        
        Args:
            corpora_path (str): Path to the corpora directory containing all corpus files
            load_all (bool): Load all corpora on initialization
        """
        self.corpora_path = Path(corpora_path)
        self.load_all = load_all
        
        # Validate corpora path exists
        if not self.corpora_path.exists():
            raise FileNotFoundError(f"Corpora directory not found: {corpora_path}")
        
        # Initialize CorpusLoader for data access
        self.corpus_loader = CorpusLoader(str(corpora_path))
        
        # Initialize corpus data storage
        self.corpora_data = {}
        self.loaded_corpora = set()
        self.corpus_paths = {}
        
        # Setup corpus paths
        self._setup_corpus_paths()
        
        # Supported corpus types
        self.supported_corpora = [
            'verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet',
            'bso', 'semnet', 'reference_docs', 'vn_api'
        ]
        
        # Initialize CorpusParser for enhanced parsing operations
        self.corpus_parser = CorpusParser(self.corpus_paths, self._get_logger())
        
        # Initialize all helper classes with CorpusLoader integration
        self._initialize_helper_classes()
        
        # Load corpora if requested
        if load_all:
            self._load_all_corpora()
    
    
    
    def _load_corpus(self, corpus_name: str) -> None:
        """
        Load a specific corpus by name.
        
        Args:
            corpus_name (str): Name of corpus to load
        """
        # Check if corpus path exists
        if not hasattr(self, 'corpus_paths') or corpus_name not in self.corpus_paths:
            raise FileNotFoundError(f"Corpus path for {corpus_name} not found")
        
        corpus_path = self.corpus_paths[corpus_name]
        if not corpus_path or not Path(corpus_path).exists():
            raise FileNotFoundError(f"Corpus directory does not exist: {corpus_path}")
        
        try:
            # Use specific loader based on corpus type
            if corpus_name == 'verbnet':
                self._load_verbnet(Path(corpus_path))
                self.loaded_corpora.add(corpus_name)  # Ensure it's marked as loaded
            else:
                # Use generic corpus loader
                if hasattr(self, 'corpus_loader'):
                    corpus_data = self.corpus_loader.load_corpus(corpus_name)
                    self.corpora_data[corpus_name] = corpus_data
                    self.loaded_corpora.add(corpus_name)
                else:
                    raise AttributeError("CorpusLoader not initialized")
                    
            print(f"Successfully loaded {corpus_name} corpus")
        except (FileNotFoundError, AttributeError):
            # Re-raise validation errors
            raise
        except Exception as e:
            print(f"Error loading {corpus_name}: {e}")
            raise
    
    def _setup_corpus_paths(self) -> None:
        """
        Set up corpus directory paths by auto-detecting corpus locations.
        """
        if not hasattr(self, 'corpus_paths'):
            self.corpus_paths = {}
            
        base_path = self.corpora_path
        
        # Define expected corpus directory names
        corpus_directories = {
            'verbnet': 'verbnet',
            'framenet': 'framenet', 
            'propbank': 'propbank',
            'ontonotes': 'ontonotes',
            'wordnet': 'wordnet',
            'bso': 'BSO',
            'semnet': 'semnet20180205',
            'reference_docs': 'reference_docs'
        }
        
        # Check each expected corpus directory
        for corpus_name, dir_name in corpus_directories.items():
            corpus_path = base_path / dir_name
            if corpus_path.exists() and corpus_path.is_dir():
                self.corpus_paths[corpus_name] = str(corpus_path)
                print(f"Found {corpus_name} corpus at: {corpus_path}")
            else:
                print(f"Corpus not found: {corpus_path}")
    
    def _get_logger(self):
        """Get logger instance for UVI operations."""
        import logging
        logger = logging.getLogger('uvi')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def _initialize_helper_classes(self) -> None:
        """
        Initialize all helper classes with CorpusLoader integration.
        
        This creates the modular architecture described in TODO.md, where each helper
        class specializes in specific functionality while maintaining unified access.
        """
        # Initialize helper classes in dependency order
        try:
            # Core parsing and analytics (no dependencies on other helpers)
            self.parsing_engine = ParsingEngine(self)
            self.analytics_manager = AnalyticsManager(self)
            
            # Reference data provider (depends on CorpusCollectionBuilder)
            self.reference_data_provider = ReferenceDataProvider(self)
            
            # Validation manager (depends on CorpusCollectionValidator)
            self.validation_manager = ValidationManager(self)
            
            # Search engine (depends on CorpusCollectionAnalyzer)
            self.search_engine = SearchEngine(self)
            
            # Corpus retriever (depends on CorpusParser and CorpusCollectionBuilder)
            self.corpus_retriever = CorpusRetriever(self)
            
            # Cross-reference manager (depends on CorpusCollectionValidator)
            self.cross_reference_manager = CrossReferenceManager(self)
            
            # Export manager (depends on CorpusCollectionAnalyzer)
            self.export_manager = ExportManager(self)
            
            print("Successfully initialized all helper classes with CorpusLoader integration")
            
        except Exception as e:
            print(f"Warning: Failed to initialize some helper classes: {e}")
            # Continue without helpers - UVI will still function with core capabilities
        
    def _load_all_corpora(self) -> None:
        """
        Load all available corpora that have valid paths.
        """
        if not hasattr(self, 'corpus_paths'):
            self._setup_corpus_paths()
            
        # Load each available corpus
        for corpus_name in self.corpus_paths.keys():
            try:
                self._load_corpus(corpus_name)
            except Exception as e:
                print(f"Failed to load {corpus_name}: {e}")
                continue
    
    
    # Utility methods
    def get_loaded_corpora(self) -> List[str]:
        """
        Get list of successfully loaded corpora.
        
        Returns:
            list: Names of loaded corpora
        """
        return list(self.loaded_corpora)
    
    def is_corpus_loaded(self, corpus_name: str) -> bool:
        """
        Check if a corpus is loaded.
        
        Args:
            corpus_name (str): Name of corpus to check
            
        Returns:
            bool: True if corpus is loaded
        """
        return corpus_name in self.loaded_corpora
    
    def get_corpus_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all detected and loaded corpora.
        
        Returns:
            dict: Corpus information including paths and load status
        """
        corpus_info = {}
        for corpus_name in self.supported_corpora:
            corpus_info[corpus_name] = {
                'path': str(self.corpus_paths.get(corpus_name, 'Not found')),
                'loaded': corpus_name in self.loaded_corpora,
                'data_available': corpus_name in self.corpora_data
            }
        return corpus_info
    
    def get_corpus_paths(self) -> Dict[str, str]:
        """
        Get dictionary of detected corpus paths.
        
        Returns:
            dict: Mapping of corpus names to their file system paths
        """
        return self.corpus_paths.copy()
    
    # Universal Search and Query Methods
    
    def search_lemmas(self, lemmas: List[str], include_resources: Optional[List[str]] = None, 
                     logic: str = 'or', sort_behavior: str = 'alpha') -> Dict[str, Any]:
        """
        Search for lemmas across all linguistic resources with cross-corpus integration.
        
        Args:
            lemmas (list): List of lemmas to search
            include_resources (list): Resources to include ['verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet', 'bso', 'semnet', 'reference_docs', 'vn_api']
                                     If None, includes all available resources
            logic (str): 'and' or 'or' logic for multi-lemma search
            sort_behavior (str): 'alpha' or 'num' sorting
            
        Returns:
            dict: Comprehensive cross-resource results with mappings
        """
        # Validate input parameters
        if not lemmas:
            return {}  # Return empty result for empty input
        
        if include_resources is None:
            include_resources = list(self.loaded_corpora)
        else:
            # Validate that requested resources are loaded
            unavailable = set(include_resources) - self.loaded_corpora
            if unavailable:
                print(f"Warning: Requested resources not loaded: {unavailable}")
            include_resources = [r for r in include_resources if r in self.loaded_corpora]
        
        # Normalize lemmas to lowercase for consistent search
        normalized_lemmas = [lemma.lower().strip() for lemma in lemmas]
        
        # Initialize results structure
        results = {
            'query': {
                'lemmas': lemmas,
                'normalized_lemmas': normalized_lemmas,
                'logic': logic,
                'sort_behavior': sort_behavior,
                'resources': include_resources
            },
            'matches': {},
            'cross_references': {},
            'statistics': {}
        }
        
        # Search each corpus
        for corpus_name in include_resources:
            corpus_results = self._search_lemmas_in_corpus(normalized_lemmas, corpus_name, logic)
            if corpus_results:
                results['matches'][corpus_name] = corpus_results
        
        # Apply sorting
        results['matches'] = self._sort_search_results(results['matches'], sort_behavior)
        
        # Add cross-references between corpora
        results['cross_references'] = self._find_cross_corpus_lemma_mappings(normalized_lemmas, include_resources)
        
        # Calculate statistics
        results['statistics'] = self._calculate_search_statistics(results['matches'])
        
        return results
    
    def search_by_semantic_pattern(self, pattern_type: str, pattern_value: str, 
                                  target_resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search across corpora using shared semantic patterns (thematic roles, predicates, etc.).
        
        Args:
            pattern_type (str): Type of pattern ('themrole', 'predicate', 'syntactic_frame', 
                               'selectional_restriction', 'semantic_type', 'frame_element')
            pattern_value (str): Pattern value to search
            target_resources (list): Resources to search in (default: all)
            
        Returns:
            dict: Cross-corpus matches with semantic relationships
        """
        # Validate input parameters
        if not pattern_value:
            raise ValueError("Pattern value cannot be empty")
        
        valid_pattern_types = {
            'themrole', 'predicate', 'syntactic_frame', 'selectional_restriction',
            'semantic_type', 'frame_element', 'vs_feature', 'selrestr', 'synrestr'
        }
        
        if pattern_type not in valid_pattern_types:
            raise ValueError(f"Invalid pattern type. Must be one of: {valid_pattern_types}")
        
        if target_resources is None:
            target_resources = list(self.loaded_corpora)
        else:
            target_resources = [r for r in target_resources if r in self.loaded_corpora]
        
        # Initialize results structure
        results = {
            'query': {
                'pattern_type': pattern_type,
                'pattern_value': pattern_value,
                'target_resources': target_resources
            },
            'matches': {},
            'semantic_relationships': {},
            'statistics': {}
        }
        
        # Search for pattern in each corpus
        for corpus_name in target_resources:
            corpus_matches = self._search_semantic_pattern_in_corpus(pattern_type, pattern_value, corpus_name)
            if corpus_matches:
                results['matches'][corpus_name] = corpus_matches
        
        # Find semantic relationships between matches
        results['semantic_relationships'] = self._find_pattern_relationships(results['matches'], pattern_type)
        
        # Calculate statistics
        results['statistics'] = self._calculate_pattern_statistics(results['matches'], pattern_type)
        
        return results
    
    def search_by_cross_reference(self, source_id: str, source_corpus: str, 
                                 target_corpus: str) -> List[Dict[str, Any]]:
        """
        Navigate between corpora using cross-reference mappings.
        
        Args:
            source_id (str): Entry ID in source corpus
            source_corpus (str): Source corpus name
            target_corpus (str): Target corpus name
            
        Returns:
            list: Related entries in target corpus with mapping confidence
        """
        # Validate input parameters
        if not source_id or not source_corpus or not target_corpus:
            raise ValueError("All parameters (source_id, source_corpus, target_corpus) are required")
        
        if source_corpus not in self.loaded_corpora:
            raise ValueError(f"Source corpus '{source_corpus}' not loaded")
        
        if target_corpus not in self.loaded_corpora:
            raise ValueError(f"Target corpus '{target_corpus}' not loaded")
        
        related_entries = []
        
        # Get source entry
        source_entry = self._get_corpus_entry(source_id, source_corpus)
        if not source_entry:
            return related_entries
        
        # Use cross-reference manager if available
        if hasattr(self, '_cross_ref_manager') and self._cross_ref_manager:
            try:
                cross_refs = self._cross_ref_manager.find_cross_references(source_id, source_corpus)
                # Filter for target corpus
                for ref in cross_refs:
                    target_key = ref.get('target', '')
                    if target_key.startswith(f"{target_corpus}:"):
                        target_id = target_key.split(':', 1)[1]
                        target_entry = self._get_corpus_entry(target_id, target_corpus)
                        if target_entry:
                            related_entries.append({
                                'id': target_id,
                                'corpus': target_corpus,
                                'data': target_entry,
                                'confidence': ref.get('confidence', 0.0),
                                'mapping_type': 'cross_reference'
                            })
            except Exception:
                # If cross-reference manager fails, return empty list
                pass
        
        return related_entries
    
    def search_by_attribute(self, attribute_type: str, query_string: str, 
                           corpus_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search by specific linguistic attributes across multiple corpora.
        
        Args:
            attribute_type (str): Type of attribute ('themrole', 'predicate', 'vs_feature', 
                                 'selrestr', 'synrestr', 'frame_element', 'semantic_type')
            query_string (str): Attribute value to search
            corpus_filter (list): Limit search to specific corpora
            
        Returns:
            dict: Matched entries grouped by corpus with cross-references
        """
        # Validate input parameters
        if not query_string:
            raise ValueError("Query string cannot be empty")
        
        valid_attribute_types = {
            'themrole', 'predicate', 'vs_feature', 'selrestr', 'synrestr', 
            'frame_element', 'semantic_type', 'pos', 'member', 'class_id'
        }
        
        if attribute_type not in valid_attribute_types:
            raise ValueError(f"Invalid attribute type. Must be one of: {valid_attribute_types}")
        
        if corpus_filter is None:
            corpus_filter = list(self.loaded_corpora)
        else:
            corpus_filter = [c for c in corpus_filter if c in self.loaded_corpora]
        
        # Initialize results structure
        results = {
            'query': {
                'attribute_type': attribute_type,
                'query_string': query_string,
                'corpus_filter': corpus_filter
            },
            'matches': {},
            'cross_references': {},
            'statistics': {}
        }
        
        # Search each corpus for the attribute
        for corpus_name in corpus_filter:
            corpus_matches = self._search_attribute_in_corpus(attribute_type, query_string, corpus_name)
            if corpus_matches:
                results['matches'][corpus_name] = corpus_matches
        
        # Find cross-references between matched entries
        results['cross_references'] = self._find_attribute_cross_references(results['matches'], attribute_type)
        
        # Calculate statistics
        results['statistics'] = self._calculate_attribute_statistics(results['matches'], attribute_type)
        
        return results
    
    def find_semantic_relationships(self, entry_id: str, corpus: str, 
                                   relationship_types: Optional[List[str]] = None, 
                                   depth: int = 2) -> Dict[str, Any]:
        """
        Discover semantic relationships across the corpus collection.
        
        Args:
            entry_id (str): Starting entry ID
            corpus (str): Starting corpus
            relationship_types (list): Types of relationships to explore
            depth (int): Maximum relationship depth to explore
            
        Returns:
            dict: Semantic relationship graph with paths and distances
        """
        # Validate input parameters
        if not entry_id or not corpus:
            raise ValueError("Entry ID and corpus are required")
        
        if corpus not in self.loaded_corpora:
            raise ValueError(f"Corpus '{corpus}' not loaded")
        
        if depth < 1 or depth > 5:
            raise ValueError("Depth must be between 1 and 5")
        
        if relationship_types is None:
            relationship_types = [
                'cross_corpus_mapping', 'shared_lemma', 'semantic_similarity',
                'hierarchical', 'thematic_role', 'predicate_similarity'
            ]
        
        # Initialize results structure
        results = {
            'query': {
                'entry_id': entry_id,
                'corpus': corpus,
                'relationship_types': relationship_types,
                'depth': depth
            },
            'starting_entry': {},
            'relationship_graph': {},
            'paths': [],
            'statistics': {}
        }
        
        # Get starting entry
        starting_entry = self._get_corpus_entry(entry_id, corpus)
        if not starting_entry:
            return results
        
        results['starting_entry'] = {
            'id': entry_id,
            'corpus': corpus,
            'data': starting_entry
        }
        
        # Build relationship graph using breadth-first search
        visited = set([(entry_id, corpus)])
        current_depth = 0
        current_level = [(entry_id, corpus, starting_entry)]
        relationship_graph = {}
        
        while current_level and current_depth < depth:
            next_level = []
            current_depth += 1
            
            for current_id, current_corpus, current_entry in current_level:
                current_key = f"{current_corpus}:{current_id}"
                if current_key not in relationship_graph:
                    relationship_graph[current_key] = {
                        'entry': {'id': current_id, 'corpus': current_corpus, 'data': current_entry},
                        'relationships': []
                    }
                
                # Find relationships for this entry
                for rel_type in relationship_types:
                    related_entries = self._find_relationship_by_type(current_entry, current_corpus, rel_type)
                    
                    for related_entry in related_entries:
                        related_key = f"{related_entry['corpus']}:{related_entry['id']}"
                        entry_pair = (related_entry['id'], related_entry['corpus'])
                        
                        # Add to relationship graph
                        relationship_info = {
                            'type': rel_type,
                            'target': related_key,
                            'confidence': related_entry.get('confidence', 0.5),
                            'depth': current_depth
                        }
                        relationship_graph[current_key]['relationships'].append(relationship_info)
                        
                        # Add to next level if not visited
                        if entry_pair not in visited and current_depth < depth:
                            visited.add(entry_pair)
                            next_level.append((related_entry['id'], related_entry['corpus'], related_entry['data']))
            
            current_level = next_level
        
        results['relationship_graph'] = relationship_graph
        
        # Find paths from starting entry to all other entries
        results['paths'] = self._find_semantic_paths(relationship_graph, f"{corpus}:{entry_id}")
        
        # Calculate statistics
        results['statistics'] = self._calculate_relationship_statistics(relationship_graph, depth)
        
        return results
    
    # Corpus-Specific Retrieval Methods
    
    def get_verbnet_class(self, class_id: str, include_subclasses: bool = True, 
                         include_mappings: bool = True) -> Dict[str, Any]:
        """
        Retrieve comprehensive VerbNet class information with cross-corpus integration.
        
        Args:
            class_id (str): VerbNet class identifier
            include_subclasses (bool): Include hierarchical subclass information
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            dict: VerbNet class data with integrated cross-references
        """
        if 'verbnet' not in self.corpora_data:
            return {}
        
        verbnet_data = self.corpora_data['verbnet']
        classes = verbnet_data.get('classes', {})
        
        if class_id not in classes:
            return {}
        
        class_data = classes[class_id].copy()
        
        if include_subclasses:
            # Add subclass information
            subclass_ids = self.get_subclass_ids(class_id)
            if subclass_ids:
                class_data['subclasses'] = []
                for subclass_id in subclass_ids:
                    if subclass_id in classes:
                        subclass_data = {
                            'id': subclass_id,
                            'data': classes[subclass_id]
                        }
                        class_data['subclasses'].append(subclass_data)
        
        if include_mappings:
            # Add cross-corpus mappings
            mappings = {}
            
            # Add FrameNet mappings if available
            if 'framenet' in self.corpora_data and 'mappings' in class_data:
                frame_mappings = class_data.get('mappings', {}).get('framenet', [])
                if frame_mappings:
                    mappings['framenet'] = frame_mappings
            
            # Add PropBank mappings if available  
            if 'propbank' in self.corpora_data and 'mappings' in class_data:
                pb_mappings = class_data.get('mappings', {}).get('propbank', [])
                if pb_mappings:
                    mappings['propbank'] = pb_mappings
            
            # Add WordNet mappings if available
            if 'wordnet' in self.corpora_data and 'wordnet_keys' in class_data:
                wn_keys = class_data.get('wordnet_keys', [])
                if wn_keys:
                    mappings['wordnet'] = wn_keys
            
            # Add BSO mappings if available
            if 'bso' in self.corpora_data:
                bso_categories = self.corpus_loader.bso_mappings.get(class_id, [])
                if bso_categories:
                    mappings['bso'] = bso_categories
            
            if mappings:
                class_data['cross_corpus_mappings'] = mappings
        
        return class_data
    
    def get_framenet_frame(self, frame_name: str, include_lexical_units: bool = True, 
                          include_relations: bool = True) -> Dict[str, Any]:
        """
        Retrieve comprehensive FrameNet frame information.
        
        Args:
            frame_name (str): FrameNet frame name
            include_lexical_units (bool): Include all lexical units
            include_relations (bool): Include frame-to-frame relations
            
        Returns:
            dict: FrameNet frame data with semantic relations
        """
        if 'framenet' not in self.corpora_data:
            return {}
        
        framenet_data = self.corpora_data['framenet']
        frames = framenet_data.get('frames', {})
        
        if frame_name not in frames:
            return {}
        
        frame_data = frames[frame_name].copy()
        
        if include_lexical_units:
            # Get lexical units for this frame
            lexical_units = framenet_data.get('lexical_units', {})
            frame_lus = []
            for lu_name, lu_data in lexical_units.items():
                if lu_data.get('frame_name') == frame_name:
                    frame_lus.append({
                        'name': lu_name,
                        'data': lu_data
                    })
            if frame_lus:
                frame_data['lexical_units'] = frame_lus
        
        if include_relations:
            # Get frame-to-frame relations
            relations = framenet_data.get('frame_relations', {})
            frame_relations = {
                'inherits_from': [],
                'is_inherited_by': [],
                'uses': [],
                'is_used_by': [],
                'subframe_of': [],
                'has_subframes': [],
                'precedes': [],
                'is_preceded_by': [],
                'perspective_on': [],
                'is_perspectivized_in': [],
                'see_also': []
            }
            
            # Check all relations for this frame
            for relation_type, relation_list in relations.items():
                if relation_type in frame_relations:
                    for relation in relation_list:
                        if relation.get('super_frame') == frame_name:
                            frame_relations[relation_type].append(relation.get('sub_frame'))
                        elif relation.get('sub_frame') == frame_name:
                            # Create reverse relation
                            reverse_map = {
                                'inherits_from': 'is_inherited_by',
                                'uses': 'is_used_by', 
                                'subframe_of': 'has_subframes',
                                'precedes': 'is_preceded_by',
                                'perspective_on': 'is_perspectivized_in'
                            }
                            reverse_type = reverse_map.get(relation_type)
                            if reverse_type:
                                frame_relations[reverse_type].append(relation.get('super_frame'))
            
            # Remove empty relations
            frame_relations = {k: v for k, v in frame_relations.items() if v}
            if frame_relations:
                frame_data['frame_relations'] = frame_relations
        
        return frame_data
    
    def get_propbank_frame(self, lemma: str, include_examples: bool = True, 
                          include_mappings: bool = True) -> Dict[str, Any]:
        """
        Retrieve PropBank frame information with cross-corpus integration.
        
        Args:
            lemma (str): PropBank lemma
            include_examples (bool): Include annotated examples
            include_mappings (bool): Include VerbNet/FrameNet mappings
            
        Returns:
            dict: PropBank frame data with cross-references
        """
        if 'propbank' not in self.corpora_data:
            return {}
        
        propbank_data = self.corpora_data['propbank']
        predicates = propbank_data.get('predicates', {})
        
        if lemma not in predicates:
            return {}
        
        predicate_data = predicates[lemma].copy()
        
        if include_examples:
            # Include annotated examples if available
            examples = propbank_data.get('examples', {})
            predicate_examples = []
            for example_id, example_data in examples.items():
                if example_data.get('lemma') == lemma:
                    predicate_examples.append({
                        'id': example_id,
                        'data': example_data
                    })
            if predicate_examples:
                predicate_data['annotated_examples'] = predicate_examples
        
        if include_mappings:
            # Add cross-corpus mappings
            mappings = {}
            
            # Add VerbNet mappings
            if 'verbnet_mappings' in predicate_data:
                vn_mappings = predicate_data.get('verbnet_mappings', [])
                if vn_mappings:
                    mappings['verbnet'] = vn_mappings
            
            # Add FrameNet mappings  
            if 'framenet_mappings' in predicate_data:
                fn_mappings = predicate_data.get('framenet_mappings', [])
                if fn_mappings:
                    mappings['framenet'] = fn_mappings
            
            # Look for reverse mappings in other corpora
            if 'verbnet' in self.corpora_data:
                verbnet_classes = self.corpora_data['verbnet'].get('classes', {})
                for class_id, class_data in verbnet_classes.items():
                    if 'propbank_mappings' in class_data:
                        pb_mappings = class_data.get('propbank_mappings', [])
                        for mapping in pb_mappings:
                            if mapping.get('lemma') == lemma:
                                if 'verbnet' not in mappings:
                                    mappings['verbnet'] = []
                                mappings['verbnet'].append({
                                    'class_id': class_id,
                                    'mapping': mapping
                                })
            
            if mappings:
                predicate_data['cross_corpus_mappings'] = mappings
        
        return predicate_data
    
    def get_ontonotes_entry(self, lemma: str, include_mappings: bool = True) -> Dict[str, Any]:
        """
        Retrieve OntoNotes sense inventory with cross-resource mappings.
        
        Args:
            lemma (str): OntoNotes lemma
            include_mappings (bool): Include all cross-resource mappings
            
        Returns:
            dict: OntoNotes entry data with integrated references
        """
        if 'ontonotes' not in self.corpora_data:
            return {}
        
        ontonotes_data = self.corpora_data['ontonotes']
        senses = ontonotes_data.get('senses', {})
        
        if lemma not in senses:
            return {}
        
        sense_data = senses[lemma].copy()
        
        if include_mappings:
            # Add cross-resource mappings
            mappings = {}
            
            # Add VerbNet mappings if available
            if 'verbnet_mappings' in sense_data:
                vn_mappings = sense_data.get('verbnet_mappings', [])
                if vn_mappings:
                    mappings['verbnet'] = vn_mappings
            
            # Add PropBank mappings
            if 'propbank_mappings' in sense_data:
                pb_mappings = sense_data.get('propbank_mappings', [])
                if pb_mappings:
                    mappings['propbank'] = pb_mappings
            
            # Add FrameNet mappings
            if 'framenet_mappings' in sense_data:
                fn_mappings = sense_data.get('framenet_mappings', [])
                if fn_mappings:
                    mappings['framenet'] = fn_mappings
            
            # Add WordNet mappings
            if 'wordnet_mappings' in sense_data:
                wn_mappings = sense_data.get('wordnet_mappings', [])
                if wn_mappings:
                    mappings['wordnet'] = wn_mappings
            
            # Look for sense groupings
            groupings = ontonotes_data.get('groupings', {})
            if lemma in groupings:
                sense_groupings = groupings[lemma]
                if sense_groupings:
                    mappings['groupings'] = sense_groupings
            
            # Add cross-references to related entries
            related_entries = []
            if 'related_lemmas' in sense_data:
                for related_lemma in sense_data['related_lemmas']:
                    if related_lemma in senses:
                        related_entries.append({
                            'lemma': related_lemma,
                            'relation': 'related'
                        })
            
            if related_entries:
                mappings['related_entries'] = related_entries
            
            if mappings:
                sense_data['cross_resource_mappings'] = mappings
        
        return sense_data
    
    def get_wordnet_synsets(self, word: str, pos: Optional[str] = None, 
                           include_relations: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve WordNet synset information with semantic relations.
        
        Args:
            word (str): Word to look up
            pos (str): Part of speech filter (optional)
            include_relations (bool): Include hypernyms, hyponyms, etc.
            
        Returns:
            list: WordNet synsets with relation hierarchies
        """
        if 'wordnet' not in self.corpora_data:
            return []
        
        wordnet_data = self.corpora_data['wordnet']
        synsets = wordnet_data.get('synsets', {})
        word_synsets = []
        
        # Find synsets containing the word
        for synset_id, synset_data in synsets.items():
            words = synset_data.get('words', [])
            synset_pos = synset_data.get('pos', '')
            
            # Check if word is in this synset
            word_found = False
            for w in words:
                if isinstance(w, dict):
                    if w.get('lemma', '').lower() == word.lower():
                        word_found = True
                        break
                elif isinstance(w, str) and w.lower() == word.lower():
                    word_found = True
                    break
            
            if word_found:
                # Apply POS filter if specified
                if pos is None or synset_pos == pos:
                    synset_result = synset_data.copy()
                    synset_result['synset_id'] = synset_id
                    
                    if include_relations:
                        # Add semantic relations
                        relations = {}
                        
                        # Get hypernyms (more general concepts)
                        if 'hypernyms' in synset_data:
                            relations['hypernyms'] = synset_data['hypernyms']
                        
                        # Get hyponyms (more specific concepts)
                        if 'hyponyms' in synset_data:
                            relations['hyponyms'] = synset_data['hyponyms']
                        
                        # Get meronyms (part-of relations)
                        if 'meronyms' in synset_data:
                            relations['meronyms'] = synset_data['meronyms']
                        
                        # Get holonyms (has-part relations)
                        if 'holonyms' in synset_data:
                            relations['holonyms'] = synset_data['holonyms']
                        
                        # Get similar concepts
                        if 'similar_to' in synset_data:
                            relations['similar_to'] = synset_data['similar_to']
                        
                        # Get antonyms
                        if 'antonyms' in synset_data:
                            relations['antonyms'] = synset_data['antonyms']
                        
                        # Get also relations
                        if 'also' in synset_data:
                            relations['also'] = synset_data['also']
                        
                        # Get entailment relations  
                        if 'entails' in synset_data:
                            relations['entails'] = synset_data['entails']
                        
                        # Get cause relations
                        if 'causes' in synset_data:
                            relations['causes'] = synset_data['causes']
                        
                        if relations:
                            synset_result['semantic_relations'] = relations
                    
                    word_synsets.append(synset_result)
        
        # Sort by frequency or relevance if available
        if word_synsets:
            # Sort by synset offset or relevance score if available
            word_synsets.sort(key=lambda x: x.get('offset', x.get('synset_id', '')))
        
        return word_synsets
    
    def get_bso_categories(self, verb_class: Optional[str] = None, 
                          semantic_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve BSO broad semantic organization mappings.
        
        Args:
            verb_class (str): VerbNet class to get BSO categories for
            semantic_category (str): BSO category to get verb classes for
            
        Returns:
            dict: BSO mappings with member verb information
        """
        if 'bso' not in self.corpora_data:
            return {}
        
        bso_data = self.corpora_data['bso']
        mappings = bso_data.get('mappings', {})
        
        result = {}
        
        if verb_class:
            # Get BSO categories for a specific VerbNet class
            if verb_class in mappings:
                class_mappings = mappings[verb_class]
                result = {
                    'verb_class': verb_class,
                    'bso_categories': class_mappings,
                    'mapping_type': 'class_to_categories'
                }
                
                # Add member verb information if available
                if 'verbnet' in self.corpora_data:
                    verbnet_classes = self.corpora_data['verbnet'].get('classes', {})
                    if verb_class in verbnet_classes:
                        members = verbnet_classes[verb_class].get('members', [])
                        if members:
                            result['member_verbs'] = members
            
        elif semantic_category:
            # Get VerbNet classes for a specific BSO category
            category_classes = []
            for class_id, categories in mappings.items():
                if isinstance(categories, list) and semantic_category in categories:
                    category_classes.append(class_id)
                elif isinstance(categories, dict) and semantic_category in categories.values():
                    category_classes.append(class_id)
                elif isinstance(categories, str) and categories == semantic_category:
                    category_classes.append(class_id)
            
            if category_classes:
                result = {
                    'semantic_category': semantic_category,
                    'verb_classes': category_classes,
                    'mapping_type': 'category_to_classes'
                }
                
                # Add detailed class information
                if 'verbnet' in self.corpora_data:
                    verbnet_classes = self.corpora_data['verbnet'].get('classes', {})
                    class_details = []
                    for class_id in category_classes:
                        if class_id in verbnet_classes:
                            class_info = {
                                'class_id': class_id,
                                'members': verbnet_classes[class_id].get('members', []),
                                'description': verbnet_classes[class_id].get('description', '')
                            }
                            class_details.append(class_info)
                    if class_details:
                        result['class_details'] = class_details
        
        else:
            # Return all BSO mappings
            result = {
                'all_mappings': mappings,
                'mapping_type': 'complete'
            }
            
            # Add summary statistics
            total_classes = len(mappings)
            all_categories = set()
            for categories in mappings.values():
                if isinstance(categories, list):
                    all_categories.update(categories)
                elif isinstance(categories, dict):
                    all_categories.update(categories.values())
                elif isinstance(categories, str):
                    all_categories.add(categories)
            
            result['statistics'] = {
                'total_verbnet_classes': total_classes,
                'total_bso_categories': len(all_categories),
                'unique_categories': list(all_categories)
            }
        
        return result
    
    def get_semnet_data(self, lemma: str, pos: str = 'verb') -> Dict[str, Any]:
        """
        Retrieve SemNet integrated semantic network data.
        
        Args:
            lemma (str): Lemma to look up
            pos (str): Part of speech ('verb' or 'noun')
            
        Returns:
            dict: Integrated semantic network information
        """
        if 'semnet' not in self.corpora_data:
            return {}
        
        semnet_data = self.corpora_data['semnet']
        
        # Look in the appropriate part-of-speech section
        pos_data = semnet_data.get(pos + 's', {})  # 'verbs' or 'nouns'
        
        if lemma not in pos_data:
            return {}
        
        entry_data = pos_data[lemma].copy()
        
        result = {
            'lemma': lemma,
            'pos': pos,
            'semnet_data': entry_data
        }
        
        # Add semantic network relationships
        if 'relations' in entry_data:
            relations = entry_data['relations']
            processed_relations = {}
            
            for relation_type, related_items in relations.items():
                if isinstance(related_items, list):
                    # Expand related items with their data if available
                    expanded_items = []
                    for item in related_items:
                        if isinstance(item, dict):
                            expanded_items.append(item)
                        elif isinstance(item, str):
                            # Try to find the related item's data
                            if item in pos_data:
                                expanded_items.append({
                                    'lemma': item,
                                    'data': pos_data[item]
                                })
                            else:
                                # Check other POS if not found
                                other_pos = 'nouns' if pos == 'verb' else 'verbs'
                                other_pos_data = semnet_data.get(other_pos, {})
                                if item in other_pos_data:
                                    expanded_items.append({
                                        'lemma': item,
                                        'pos': other_pos[:-1],  # remove 's'
                                        'data': other_pos_data[item]
                                    })
                                else:
                                    expanded_items.append({'lemma': item})
                    processed_relations[relation_type] = expanded_items
                else:
                    processed_relations[relation_type] = related_items
            
            result['semantic_relations'] = processed_relations
        
        # Add semantic features if available
        if 'semantic_features' in entry_data:
            result['semantic_features'] = entry_data['semantic_features']
        
        # Add domain information if available  
        if 'domain' in entry_data:
            result['domain'] = entry_data['domain']
        
        # Add frequency information if available
        if 'frequency' in entry_data:
            result['frequency'] = entry_data['frequency']
        
        # Add integrated mappings to other corpora if available
        integrated_mappings = {}
        if 'verbnet_classes' in entry_data:
            integrated_mappings['verbnet'] = entry_data['verbnet_classes']
        if 'framenet_frames' in entry_data:
            integrated_mappings['framenet'] = entry_data['framenet_frames']  
        if 'propbank_frames' in entry_data:
            integrated_mappings['propbank'] = entry_data['propbank_frames']
        if 'wordnet_synsets' in entry_data:
            integrated_mappings['wordnet'] = entry_data['wordnet_synsets']
        
        if integrated_mappings:
            result['cross_corpus_mappings'] = integrated_mappings
        
        return result
    
    def get_reference_definitions(self, reference_type: str, 
                                 name: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve reference documentation (predicates, themroles, constants).
        
        Args:
            reference_type (str): Type of reference ('predicate', 'themrole', 'constant', 'verb_specific')
            name (str): Specific reference name (optional)
            
        Returns:
            dict: Reference definitions and usage information
        """
        if 'reference_docs' not in self.corpora_data:
            return {}
        
        reference_data = self.corpora_data['reference_docs']
        
        # Valid reference types
        valid_types = ['predicate', 'themrole', 'constant', 'verb_specific']
        
        if reference_type not in valid_types:
            return {'error': f'Invalid reference type. Must be one of: {valid_types}'}
        
        # Map reference types to data keys
        type_mapping = {
            'predicate': 'predicates',
            'themrole': 'themroles', 
            'constant': 'constants',
            'verb_specific': 'verb_specific_features'
        }
        
        data_key = type_mapping[reference_type]
        type_data = reference_data.get(data_key, {})
        
        if name:
            # Return specific reference definition
            if name in type_data:
                result = {
                    'reference_type': reference_type,
                    'name': name,
                    'definition': type_data[name]
                }
                
                # Add usage examples if available
                usage_data = reference_data.get('usage_examples', {})
                if reference_type in usage_data and name in usage_data[reference_type]:
                    result['usage_examples'] = usage_data[reference_type][name]
                
                # Add related references
                related_data = reference_data.get('related_references', {})
                if reference_type in related_data and name in related_data[reference_type]:
                    result['related_references'] = related_data[reference_type][name]
                
                return result
            else:
                return {'error': f'{reference_type} "{name}" not found in reference documentation'}
        
        else:
            # Return all definitions for the reference type
            result = {
                'reference_type': reference_type,
                'all_definitions': type_data,
                'count': len(type_data)
            }
            
            # Add summary information
            if type_data:
                result['names'] = list(type_data.keys())
                
                # Add categorization if available
                categories_data = reference_data.get('categories', {})
                if reference_type in categories_data:
                    result['categories'] = categories_data[reference_type]
                
                # Add frequency information if available
                frequency_data = reference_data.get('frequency', {})
                if reference_type in frequency_data:
                    result['frequency_info'] = frequency_data[reference_type]
            
            return result
    
    # Cross-Corpus Integration Methods
    
    def get_complete_semantic_profile(self, lemma: str) -> Dict[str, Any]:
        """
        Get comprehensive semantic information from all loaded corpora.
        
        Args:
            lemma (str): Lemma to analyze
            
        Returns:
            dict: Integrated semantic profile across all resources
        """
        profile = {
            'lemma': lemma,
            'verbnet': {},
            'framenet': {},
            'propbank': {},
            'ontonotes': {},
            'wordnet': [],
            'bso': {},
            'semnet': {},
            'cross_references': {}
        }
        
        # Build cross-reference index if not already built
        if not hasattr(self, '_cross_ref_manager'):
            self._initialize_cross_reference_system()
        
        # Gather VerbNet information
        if 'verbnet' in self.corpora_data:
            profile['verbnet'] = self._get_verbnet_profile(lemma)
        
        # Gather FrameNet information
        if 'framenet' in self.corpora_data:
            profile['framenet'] = self._get_framenet_profile(lemma)
        
        # Gather PropBank information
        if 'propbank' in self.corpora_data:
            profile['propbank'] = self._get_propbank_profile(lemma)
        
        # Gather OntoNotes information
        if 'ontonotes' in self.corpora_data:
            profile['ontonotes'] = self._get_ontonotes_profile(lemma)
        
        # Gather WordNet information
        if 'wordnet' in self.corpora_data:
            profile['wordnet'] = self._get_wordnet_profile(lemma)
        
        # Gather BSO information
        if 'bso' in self.corpora_data:
            profile['bso'] = self._get_bso_profile(lemma)
        
        # Gather SemNet information
        if 'semnet' in self.corpora_data:
            profile['semnet'] = self._get_semnet_profile(lemma)
        
        # Build cross-reference mappings
        profile['cross_references'] = self._build_cross_references_for_lemma(lemma, profile)
        
        # Calculate confidence scores for profile integration
        profile['integration_confidence'] = self._calculate_profile_confidence(profile)
        
        return profile
    
    def validate_cross_references(self, entry_id: str, source_corpus: str) -> Dict[str, Any]:
        """
        Validate cross-references between corpora for data integrity.
        
        Args:
            entry_id (str): Entry ID to validate
            source_corpus (str): Source corpus name
            
        Returns:
            dict: Validation results for all cross-references
        """
        if not hasattr(self, '_cross_ref_manager'):
            self._initialize_cross_reference_system()
        
        validation_results = {
            'entry_id': entry_id,
            'source_corpus': source_corpus,
            'validation_timestamp': self._get_timestamp(),
            'total_references': 0,
            'valid_references': 0,
            'invalid_references': 0,
            'missing_targets': [],
            'confidence_scores': {},
            'detailed_results': {},
            'schema_validation': {}
        }
        
        # Find all mappings from this entry
        mappings = self._cross_ref_manager.find_mappings(entry_id, source_corpus)
        validation_results['total_references'] = len(mappings)
        
        # Validate each mapping
        for mapping in mappings:
            target_key = mapping.get('target', '')
            if not target_key:
                continue
            
            # Parse target corpus and ID
            target_parts = target_key.split(':', 1)
            if len(target_parts) != 2:
                continue
            
            target_corpus, target_id = target_parts
            
            # Validate the mapping
            validation = self._cross_ref_manager.validate_mapping(
                entry_id, source_corpus, target_id, target_corpus, self.corpora_data
            )
            
            mapping_key = f"{source_corpus}:{entry_id}->{target_corpus}:{target_id}"
            validation_results['detailed_results'][mapping_key] = validation
            
            if validation['valid']:
                validation_results['valid_references'] += 1
            else:
                validation_results['invalid_references'] += 1
                if not validation['exists_in_target']:
                    validation_results['missing_targets'].append(target_key)
            
            # Store confidence score
            validation_results['confidence_scores'][mapping_key] = validation.get('confidence', 0.0)
        
        # Perform schema validation on the source entry
        validation_results['schema_validation'] = self._validate_entry_schema(entry_id, source_corpus)
        
        # Calculate overall validation score
        if validation_results['total_references'] > 0:
            validation_results['validation_score'] = validation_results['valid_references'] / validation_results['total_references']
        else:
            validation_results['validation_score'] = 1.0
        
        return validation_results
    
    def find_related_entries(self, entry_id: str, source_corpus: str, 
                            target_corpus: str) -> List[Dict[str, Any]]:
        """
        Find related entries in target corpus using cross-reference mappings.
        
        Args:
            entry_id (str): Source entry ID
            source_corpus (str): Source corpus name
            target_corpus (str): Target corpus name
            
        Returns:
            list: Related entries with mapping confidence scores
        """
        if not hasattr(self, '_cross_ref_manager'):
            self._initialize_cross_reference_system()
        
        # Find direct mappings
        direct_mappings = self._cross_ref_manager.find_mappings(entry_id, source_corpus, target_corpus)
        related_entries = []
        
        for mapping in direct_mappings:
            target_key = mapping.get('target', '')
            if not target_key:
                continue
            
            # Parse target ID
            target_parts = target_key.split(':', 1)
            if len(target_parts) != 2:
                continue
            
            _, target_id = target_parts
            
            # Get detailed information about the target entry
            entry_info = {
                'entry_id': target_id,
                'corpus': target_corpus,
                'confidence': mapping.get('confidence', 0.0),
                'mapping_type': 'direct',
                'relationship': mapping.get('relation', 'mapped'),
                'entry_data': self._get_entry_data(target_id, target_corpus)
            }
            
            related_entries.append(entry_info)
        
        # Find indirect mappings through semantic relationships
        indirect_entries = self._find_indirect_mappings(entry_id, source_corpus, target_corpus)
        
        # Add indirect mappings with lower confidence
        for indirect_entry in indirect_entries:
            indirect_entry['mapping_type'] = 'indirect'
            indirect_entry['confidence'] *= 0.7  # Reduce confidence for indirect mappings
            related_entries.append(indirect_entry)
        
        # Sort by confidence score (highest first)
        related_entries.sort(key=lambda x: x.get('confidence', 0.0), reverse=True)
        
        # Add similarity scores based on semantic content
        for entry in related_entries:
            entry['semantic_similarity'] = self._calculate_semantic_similarity(
                entry_id, source_corpus, entry['entry_id'], target_corpus
            )
        
        return related_entries
    
    def trace_semantic_path(self, start_entry: Tuple[str, str], end_entry: Tuple[str, str], 
                           max_depth: int = 3) -> List[List[str]]:
        """
        Find semantic relationship path between entries across corpora.
        
        Args:
            start_entry (tuple): (corpus, entry_id) for starting point
            end_entry (tuple): (corpus, entry_id) for target
            max_depth (int): Maximum path length to explore
            
        Returns:
            list: Semantic relationship paths with confidence scores
        """
        if not hasattr(self, '_cross_ref_manager'):
            self._initialize_cross_reference_system()
        
        # Build semantic relationship graph if not already built
        if not hasattr(self, '_semantic_graph'):
            self._build_semantic_graph()
        
        from .utils.cross_refs import find_semantic_path
        
        # Find paths using cross-reference index
        paths = find_semantic_path(
            start_entry, end_entry, 
            self._cross_ref_manager.cross_reference_index, 
            max_depth
        )
        
        # Enhance paths with detailed information and confidence scores
        enhanced_paths = []
        for path in paths:
            enhanced_path = {
                'path': path,
                'length': len(path) - 1,
                'confidence': self._calculate_path_confidence(path),
                'relationships': self._extract_path_relationships(path),
                'semantic_types': self._extract_path_semantic_types(path)
            }
            enhanced_paths.append(enhanced_path)
        
        # Sort by confidence and path length
        enhanced_paths.sort(key=lambda x: (x['confidence'], -x['length']), reverse=True)
        
        return enhanced_paths
    
    # Reference Data Methods
    
    def get_references(self) -> Dict[str, Any]:
        """
        Get all reference data extracted from corpus files.
        
        Returns:
            dict: Contains gen_themroles, predicates, vs_features, syn_res, sel_res
        """
        references = {}
        
        # Get thematic role references
        themroles = self.get_themrole_references()
        if themroles:
            references['gen_themroles'] = themroles
        
        # Get predicate references
        predicates = self.get_predicate_references()
        if predicates:
            references['predicates'] = predicates
        
        # Get verb-specific features
        vs_features = self.get_verb_specific_features()
        if vs_features:
            references['vs_features'] = vs_features
        
        # Get syntactic restrictions
        syn_restrictions = self.get_syntactic_restrictions()
        if syn_restrictions:
            references['syn_res'] = syn_restrictions
        
        # Get selectional restrictions
        sel_restrictions = self.get_selectional_restrictions()
        if sel_restrictions:
            references['sel_res'] = sel_restrictions
        
        # Add reference collection metadata
        if references:
            references['metadata'] = {
                'total_collections': len(references),
                'generated_at': self.corpus_loader.build_metadata.get('last_build_time', 'unknown')
            }
        
        return references
    
    def get_themrole_references(self) -> List[Dict[str, Any]]:
        """
        Get all thematic role references from corpora files.
        
        Returns:
            list: Sorted list of thematic roles with descriptions
        """
        themroles = []
        
        # Get thematic roles from reference collections
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'themroles' in ref_collections:
                for role_name, role_data in ref_collections['themroles'].items():
                    themrole_entry = {
                        'name': role_name,
                        'description': role_data.get('description', ''),
                        'type': role_data.get('type', 'thematic'),
                        'examples': role_data.get('examples', [])
                    }
                    
                    # Add usage count if available
                    if 'usage_count' in role_data:
                        themrole_entry['usage_count'] = role_data['usage_count']
                    
                    # Add related roles if available
                    if 'related_roles' in role_data:
                        themrole_entry['related_roles'] = role_data['related_roles']
                    
                    themroles.append(themrole_entry)
        
        # Also collect from VerbNet corpus if available
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            vn_themroles = set()
            
            # Extract themroles from VerbNet classes
            classes = verbnet_data.get('classes', {})
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    if 'semantics' in frame:
                        semantics = frame['semantics']
                        for pred in semantics.get('predicates', []):
                            for arg in pred.get('args', []):
                                if arg.get('type') == 'ThemRole':
                                    role_value = arg.get('value', '')
                                    if role_value and role_value not in vn_themroles:
                                        vn_themroles.add(role_value)
                                        # Only add if not already in reference collections
                                        if not any(tr['name'] == role_value for tr in themroles):
                                            themroles.append({
                                                'name': role_value,
                                                'description': f'Thematic role extracted from VerbNet corpus',
                                                'type': 'thematic',
                                                'source': 'verbnet_extraction'
                                            })
        
        # Sort by name
        themroles.sort(key=lambda x: x['name'].lower())
        
        return themroles
    
    def get_predicate_references(self) -> List[Dict[str, Any]]:
        """
        Get all predicate references from reference documentation.
        
        Returns:
            list: Sorted list of predicates with definitions and usage
        """
        predicates = []
        
        # Get predicates from reference collections
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'predicates' in ref_collections:
                for pred_name, pred_data in ref_collections['predicates'].items():
                    predicate_entry = {
                        'name': pred_name,
                        'definition': pred_data.get('definition', ''),
                        'category': pred_data.get('category', 'semantic'),
                        'arity': pred_data.get('arity', 'variable'),
                        'examples': pred_data.get('examples', [])
                    }
                    
                    # Add usage count if available
                    if 'usage_count' in pred_data:
                        predicate_entry['usage_count'] = pred_data['usage_count']
                    
                    # Add argument types if available
                    if 'arg_types' in pred_data:
                        predicate_entry['arg_types'] = pred_data['arg_types']
                    
                    predicates.append(predicate_entry)
        
        # Also collect from VerbNet corpus if available
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            vn_predicates = set()
            
            # Extract predicates from VerbNet classes
            classes = verbnet_data.get('classes', {})
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    if 'semantics' in frame:
                        semantics = frame['semantics']
                        for pred in semantics.get('predicates', []):
                            pred_name = pred.get('value', '')
                            if pred_name and pred_name not in vn_predicates:
                                vn_predicates.add(pred_name)
                                # Only add if not already in reference collections
                                if not any(p['name'] == pred_name for p in predicates):
                                    predicates.append({
                                        'name': pred_name,
                                        'definition': f'Semantic predicate extracted from VerbNet corpus',
                                        'category': 'semantic',
                                        'source': 'verbnet_extraction',
                                        'arity': len(pred.get('args', []))
                                    })
        
        # Sort by name
        predicates.sort(key=lambda x: x['name'].lower())
        
        return predicates
    
    def get_verb_specific_features(self) -> List[str]:
        """
        Get all verb-specific features from VerbNet corpus files.
        
        Returns:
            list: Sorted list of verb-specific features
        """
        vs_features = set()
        
        # Get from reference collections first
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'verb_specific_features' in ref_collections:
                vs_features.update(ref_collections['verb_specific_features'].keys())
        
        # Extract from VerbNet corpus if available
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_id, class_data in classes.items():
                # Check members for verb-specific features
                members = class_data.get('members', [])
                for member in members:
                    if isinstance(member, dict):
                        features = member.get('features', [])
                        if isinstance(features, list):
                            for feature in features:
                                if isinstance(feature, str):
                                    vs_features.add(feature)
                                elif isinstance(feature, dict) and 'name' in feature:
                                    vs_features.add(feature['name'])
        
        # Convert to sorted list
        return sorted(list(vs_features))
    
    def get_syntactic_restrictions(self) -> List[str]:
        """
        Get all syntactic restrictions from VerbNet corpus files.
        
        Returns:
            list: Sorted list of syntactic restrictions
        """
        syn_restrictions = set()
        
        # Get from reference collections first
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'syntactic_restrictions' in ref_collections:
                syn_restrictions.update(ref_collections['syntactic_restrictions'].keys())
        
        # Extract from VerbNet corpus if available
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    # Check syntax section for restrictions
                    if 'syntax' in frame:
                        syntax = frame['syntax']
                        for np in syntax.get('np', []):
                            # Look for syntactic restrictions in NPs
                            if 'synrestrs' in np:
                                synrestrs = np['synrestrs']
                                if isinstance(synrestrs, list):
                                    for restr in synrestrs:
                                        if isinstance(restr, dict):
                                            restr_type = restr.get('type', '')
                                            if restr_type:
                                                syn_restrictions.add(restr_type)
                                        elif isinstance(restr, str):
                                            syn_restrictions.add(restr)
        
        # Convert to sorted list
        return sorted(list(syn_restrictions))
    
    def get_selectional_restrictions(self) -> List[str]:
        """
        Get all selectional restrictions from VerbNet corpus files.
        
        Returns:
            list: Sorted list of selectional restrictions
        """
        sel_restrictions = set()
        
        # Get from reference collections first
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'selectional_restrictions' in ref_collections:
                sel_restrictions.update(ref_collections['selectional_restrictions'].keys())
        
        # Extract from VerbNet corpus if available
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    # Check syntax section for selectional restrictions
                    if 'syntax' in frame:
                        syntax = frame['syntax']
                        for np in syntax.get('np', []):
                            # Look for selectional restrictions in NPs
                            if 'selrestrs' in np:
                                selrestrs = np['selrestrs']
                                if isinstance(selrestrs, list):
                                    for restr in selrestrs:
                                        if isinstance(restr, dict):
                                            restr_type = restr.get('type', '')
                                            if restr_type:
                                                sel_restrictions.add(restr_type)
                                            # Also add value if present
                                            restr_value = restr.get('value', '')
                                            if restr_value:
                                                sel_restrictions.add(restr_value)
                                        elif isinstance(restr, str):
                                            sel_restrictions.add(restr)
                            
                            # Also check for restrictions in the role
                            if 'role' in np and 'selrestrs' in np['role']:
                                role_selrestrs = np['role']['selrestrs']
                                if isinstance(role_selrestrs, list):
                                    for restr in role_selrestrs:
                                        if isinstance(restr, dict):
                                            restr_type = restr.get('type', '')
                                            if restr_type:
                                                sel_restrictions.add(restr_type)
                                        elif isinstance(restr, str):
                                            sel_restrictions.add(restr)
        
        # Convert to sorted list
        return sorted(list(sel_restrictions))
    
    # Helper Methods for Export
    
    def _extract_resource_mappings(self, resource_name: str) -> Dict[str, Any]:
        """Extract cross-corpus mappings for a specific resource."""
        mappings = {}
        
        if resource_name not in self.corpora_data:
            return mappings
        
        resource_data = self.corpora_data[resource_name]
        
        # Extract mappings based on resource type
        if resource_name == 'verbnet':
            classes = resource_data.get('classes', {})
            for class_id, class_data in classes.items():
                if 'mappings' in class_data or 'wordnet_keys' in class_data:
                    if class_id not in mappings:
                        mappings[class_id] = {}
                    if 'mappings' in class_data:
                        mappings[class_id].update(class_data['mappings'])
                    if 'wordnet_keys' in class_data:
                        mappings[class_id]['wordnet'] = class_data['wordnet_keys']
        
        elif resource_name == 'propbank':
            predicates = resource_data.get('predicates', {})
            for pred_id, pred_data in predicates.items():
                pred_mappings = {}
                for mapping_type in ['verbnet_mappings', 'framenet_mappings']:
                    if mapping_type in pred_data:
                        pred_mappings[mapping_type.replace('_mappings', '')] = pred_data[mapping_type]
                if pred_mappings:
                    mappings[pred_id] = pred_mappings
        
        elif resource_name == 'ontonotes':
            senses = resource_data.get('senses', {})
            for sense_id, sense_data in senses.items():
                sense_mappings = {}
                for mapping_type in ['verbnet_mappings', 'propbank_mappings', 'framenet_mappings', 'wordnet_mappings']:
                    if mapping_type in sense_data:
                        sense_mappings[mapping_type.replace('_mappings', '')] = sense_data[mapping_type]
                if sense_mappings:
                    mappings[sense_id] = sense_mappings
        
        return mappings
    
    def _dict_to_xml(self, data: Dict[str, Any], root_tag: str = 'root') -> str:
        """Convert dictionary to XML format."""
        def dict_to_xml_recursive(d, parent_tag):
            xml_str = f"<{parent_tag}>"
            for key, value in d.items():
                if isinstance(value, dict):
                    xml_str += dict_to_xml_recursive(value, key)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            xml_str += dict_to_xml_recursive(item, key)
                        else:
                            xml_str += f"<{key}>{str(item)}</{key}>"
                else:
                    xml_str += f"<{key}>{str(value)}</{key}>"
            xml_str += f"</{parent_tag}>"
            return xml_str
        
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{dict_to_xml_recursive(data, root_tag)}'
    
    def _dict_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to CSV format (flattened)."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Resource', 'Key', 'Value'])
        
        for resource, resource_data in data.get('resources', {}).items():
            flat_data = self.flatten_dict(resource_data)
            for key, value in flat_data.items():
                writer.writerow([resource, key, value])
        
        return output.getvalue()
    
    # Flatten the data
    def flatten_dict(d:dict, parent_key='') -> Dict[str, str]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    def _flatten_profile_to_csv(self, profile: Dict[str, Any], lemma: str) -> str:
        """Convert semantic profile to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Lemma', 'Corpus', 'Data_Type', 'Key', 'Value'])
        
        # Flatten profile data
        for corpus, corpus_data in profile.items():
            if corpus == 'lemma':
                continue
            if isinstance(corpus_data, dict):
                for data_type, data_value in corpus_data.items():
                    if isinstance(data_value, dict):
                        for key, value in data_value.items():
                            writer.writerow([lemma, corpus, data_type, key, str(value)])
                    else:
                        writer.writerow([lemma, corpus, data_type, '', str(data_value)])
            else:
                writer.writerow([lemma, corpus, '', '', str(corpus_data)])
        
        return output.getvalue()
    
    # Schema Validation Methods
    
    def validate_corpus_schemas(self, corpus_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate corpus files against their schemas (DTD/XSD/custom).
        
        Args:
            corpus_names (list): Corpora to validate (default: all loaded)
            
        Returns:
            dict: Validation results for each corpus
        """
        if corpus_names is None:
            corpus_names = list(self.loaded_corpora)
        
        validation_results = {
            'validation_timestamp': self._get_timestamp(),
            'total_corpora': len(corpus_names),
            'validated_corpora': 0,
            'failed_corpora': 0,
            'corpus_results': {}
        }
        
        # Initialize schema validator
        # Schema validation will be implemented later
        
        for corpus_name in corpus_names:
            if corpus_name not in self.corpus_paths:
                validation_results['corpus_results'][corpus_name] = {
                    'status': 'skipped',
                    'error': f'Corpus path not found for {corpus_name}'
                }
                continue
            
            corpus_path = self.corpus_paths[corpus_name]
            
            try:
                if corpus_name in ['verbnet', 'framenet', 'propbank', 'ontonotes', 'vn_api']:
                    # XML-based corpora
                    result = self._validate_xml_corpus_files(corpus_name, corpus_path, validator)
                elif corpus_name in ['semnet', 'reference_docs']:
                    # JSON-based corpora
                    result = self._validate_json_corpus_files(corpus_name, corpus_path, validator)
                elif corpus_name in ['bso']:
                    # CSV-based corpora
                    result = self._validate_csv_corpus_files(corpus_name, corpus_path)
                elif corpus_name == 'wordnet':
                    # Special text-based format
                    result = self._validate_wordnet_files(corpus_path)
                else:
                    result = {
                        'status': 'skipped',
                        'warning': f'No validation method for corpus type: {corpus_name}'
                    }
                
                validation_results['corpus_results'][corpus_name] = result
                
                if result.get('status') == 'valid' or result.get('valid_files', 0) > 0:
                    validation_results['validated_corpora'] += 1
                else:
                    validation_results['failed_corpora'] += 1
                    
            except Exception as e:
                validation_results['corpus_results'][corpus_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                validation_results['failed_corpora'] += 1
        
        return validation_results
    
    def validate_xml_corpus(self, corpus_name: str) -> Dict[str, Any]:
        """
        Validate XML corpus files against DTD/XSD schemas.
        
        Args:
            corpus_name (str): Name of XML-based corpus to validate
            
        Returns:
            dict: Detailed validation results with error locations
        """
        if corpus_name not in self.corpus_paths:
            return {
                'valid': False,
                'error': f'Corpus {corpus_name} not found'
            }
        
        if corpus_name not in ['verbnet', 'framenet', 'propbank', 'ontonotes', 'vn_api']:
            return {
                'valid': False,
                'error': f'Corpus {corpus_name} is not XML-based'
            }
        
        corpus_path = self.corpus_paths[corpus_name]
        # Schema validation will be implemented later
        validator = None
        
        return self._validate_xml_corpus_files(corpus_name, corpus_path, validator)
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """
        Check internal consistency and completeness of all loaded corpora.
        
        Returns:
            dict: Comprehensive data integrity report
        """
        integrity_report = {
            'check_timestamp': self._get_timestamp(),
            'total_corpora': len(self.loaded_corpora),
            'integrity_score': 0.0,
            'corpus_integrity': {},
            'cross_reference_integrity': {},
            'data_consistency': {},
            'missing_data': {},
            'recommendations': []
        }
        
        total_checks = 0
        passed_checks = 0
        
        # Check each loaded corpus
        for corpus_name in self.loaded_corpora:
            corpus_integrity = self._check_corpus_integrity(corpus_name)
            integrity_report['corpus_integrity'][corpus_name] = corpus_integrity
            
            total_checks += corpus_integrity.get('total_checks', 0)
            passed_checks += corpus_integrity.get('passed_checks', 0)
        
        # Check cross-reference integrity
        if hasattr(self, '_cross_ref_manager'):
            cross_ref_integrity = self._check_cross_reference_integrity()
            integrity_report['cross_reference_integrity'] = cross_ref_integrity
            
            total_checks += cross_ref_integrity.get('total_checks', 0)
            passed_checks += cross_ref_integrity.get('passed_checks', 0)
        
        # Check data consistency across corpora
        consistency_check = self._check_data_consistency()
        integrity_report['data_consistency'] = consistency_check
        
        total_checks += consistency_check.get('total_checks', 0)
        passed_checks += consistency_check.get('passed_checks', 0)
        
        # Check for missing critical data
        missing_data_check = self._check_missing_data()
        integrity_report['missing_data'] = missing_data_check
        
        # Calculate overall integrity score
        if total_checks > 0:
            integrity_report['integrity_score'] = passed_checks / total_checks
        
        # Generate recommendations based on findings
        integrity_report['recommendations'] = self._generate_integrity_recommendations(integrity_report)
        
        return integrity_report
    
    # Data Export Methods
    
    def export_resources(self, include_resources: Optional[List[str]] = None, 
                        format: str = 'json', include_mappings: bool = True) -> str:
        """
        Export selected linguistic resources in specified format.
        
        Args:
            include_resources (list): Resources to include ['vn', 'fn', 'pb', 'on', 'wn', 'bso', 'semnet', 'ref']
            format (str): Export format ('json', 'xml', 'csv')
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            str: Exported data in specified format
        """
        # Default to all loaded resources if none specified
        if include_resources is None:
            include_resources = list(self.loaded_corpora)
        
        # Map short names to full corpus names
        resource_mapping = {
            'vn': 'verbnet',
            'fn': 'framenet', 
            'pb': 'propbank',
            'on': 'ontonotes',
            'wn': 'wordnet',
            'bso': 'bso',
            'semnet': 'semnet',
            'ref': 'reference_docs',
            'vn_api': 'vn_api'
        }
        
        export_data = {
            'export_metadata': {
                'format': format,
                'include_mappings': include_mappings,
                'export_timestamp': self.corpus_loader.build_metadata.get('last_build_time', 'unknown'),
                'included_resources': include_resources
            },
            'resources': {}
        }
        
        # Export each requested resource
        for resource in include_resources:
            full_name = resource_mapping.get(resource, resource)
            if full_name in self.corpora_data:
                resource_data = self.corpora_data[full_name].copy()
                
                # Add cross-corpus mappings if requested
                if include_mappings:
                    mappings = self._extract_resource_mappings(full_name)
                    if mappings:
                        resource_data['cross_corpus_mappings'] = mappings
                
                export_data['resources'][resource] = resource_data
        
        # Format the export based on requested format
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format.lower() == 'xml':
            return self._dict_to_xml(export_data, 'uvi_export')
        elif format.lower() == 'csv':
            return self._dict_to_csv(export_data)
        else:
            return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def export_cross_corpus_mappings(self) -> Dict[str, Any]:
        """
        Export comprehensive cross-corpus mapping data.
        
        Returns:
            dict: Complete mapping relationships between all corpora
        """
        mappings = {
            'export_metadata': {
                'export_type': 'cross_corpus_mappings',
                'export_timestamp': self.corpus_loader.build_metadata.get('last_build_time', 'unknown'),
                'loaded_corpora': list(self.loaded_corpora)
            },
            'mappings': {}
        }
        
        # Extract mappings between all loaded corpora
        for corpus_name in self.loaded_corpora:
            corpus_mappings = self._extract_resource_mappings(corpus_name)
            if corpus_mappings:
                mappings['mappings'][corpus_name] = corpus_mappings
        
        # Add BSO mappings if available
        if hasattr(self.corpus_loader, 'bso_mappings') and self.corpus_loader.bso_mappings:
            mappings['bso_mappings'] = self.corpus_loader.bso_mappings
        
        # Add cross-reference data if available
        if hasattr(self.corpus_loader, 'cross_references') and self.corpus_loader.cross_references:
            mappings['cross_references'] = self.corpus_loader.cross_references
        
        return mappings
    
    def export_semantic_profile(self, lemma: str, format: str = 'json') -> str:
        """
        Export complete semantic profile for a lemma across all corpora.
        
        Args:
            lemma (str): Lemma to export profile for
            format (str): Export format
            
        Returns:
            str: Comprehensive semantic profile
        """
        # Get complete semantic profile for the lemma
        profile = self.get_complete_semantic_profile(lemma)
        
        # Add export metadata
        export_data = {
            'export_metadata': {
                'lemma': lemma,
                'format': format,
                'export_timestamp': self.corpus_loader.build_metadata.get('last_build_time', 'unknown'),
                'loaded_corpora': list(self.loaded_corpora)
            },
            'semantic_profile': profile
        }
        
        # Format the export based on requested format
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format.lower() == 'xml':
            return self._dict_to_xml(export_data, 'semantic_profile_export')
        elif format.lower() == 'csv':
            return self._flatten_profile_to_csv(profile, lemma)
        else:
            return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Class Hierarchy Methods
    
    def get_class_hierarchy_by_name(self) -> Dict[str, List[str]]:
        """
        Get VerbNet class hierarchy organized alphabetically.
        
        Returns:
            dict: Class hierarchy organized by first letter
        """
        if 'verbnet' not in self.corpora_data:
            return {}
        
        hierarchy = self.corpora_data['verbnet'].get('hierarchy', {})
        return hierarchy.get('by_name', {})
    
    def get_class_hierarchy_by_id(self) -> Dict[str, List[str]]:
        """
        Get VerbNet class hierarchy organized by numerical ID.
        
        Returns:
            dict: Class hierarchy organized by numerical prefix
        """
        if 'verbnet' not in self.corpora_data:
            return {}
        
        hierarchy = self.corpora_data['verbnet'].get('hierarchy', {})
        return hierarchy.get('by_id', {})
    
    def get_subclass_ids(self, parent_class_id: str) -> Optional[List[str]]:
        """
        Get subclass IDs for a parent VerbNet class.
        
        Args:
            parent_class_id (str): Parent class ID
            
        Returns:
            list: List of subclass IDs or None
        """
        if 'verbnet' not in self.corpora_data:
            return None
        
        hierarchy = self.corpora_data['verbnet'].get('hierarchy', {})
        parent_child = hierarchy.get('parent_child', {})
        return parent_child.get(parent_class_id)
    
    def get_full_class_hierarchy(self, class_id: str) -> Dict[str, Any]:
        """
        Get complete class hierarchy for a given class.
        
        Args:
            class_id (str): VerbNet class ID
            
        Returns:
            dict: Hierarchical structure of the class
        """
        if 'verbnet' not in self.corpora_data:
            return {}
        
        verbnet_data = self.corpora_data['verbnet']
        classes = verbnet_data.get('classes', {})
        
        if class_id not in classes:
            return {}
        
        # Build complete hierarchy structure
        hierarchy = {
            'class_id': class_id,
            'class_data': classes[class_id].copy(),
            'parent_classes': [],
            'child_classes': [],
            'sibling_classes': [],
            'top_level_parent': None,
            'hierarchy_level': 0
        }
        
        # Find parent classes by traversing up the hierarchy
        current_id = class_id
        level = 0
        while True:
            parent_id = self.get_top_parent_id(current_id)
            if parent_id == current_id or level > 10:  # Prevent infinite loops
                break
            hierarchy['parent_classes'].append({
                'class_id': parent_id,
                'level': level + 1,
                'data': classes.get(parent_id, {})
            })
            current_id = parent_id
            level += 1
        
        # Set top level parent
        if hierarchy['parent_classes']:
            hierarchy['top_level_parent'] = hierarchy['parent_classes'][-1]['class_id']
        else:
            hierarchy['top_level_parent'] = class_id
        
        hierarchy['hierarchy_level'] = level
        
        # Find direct child classes
        child_ids = self.get_subclass_ids(class_id)
        if child_ids:
            for child_id in child_ids:
                if child_id in classes:
                    hierarchy['child_classes'].append({
                        'class_id': child_id,
                        'data': classes[child_id]
                    })
        
        # Find sibling classes (same parent)
        if hierarchy['parent_classes']:
            parent_id = hierarchy['parent_classes'][0]['class_id']
            sibling_ids = self.get_subclass_ids(parent_id)
            if sibling_ids:
                for sibling_id in sibling_ids:
                    if sibling_id != class_id and sibling_id in classes:
                        hierarchy['sibling_classes'].append({
                            'class_id': sibling_id,
                            'data': classes[sibling_id]
                        })
        
        return hierarchy
    
    # Cross-Corpus Integration Helper Methods
    
    def _initialize_cross_reference_system(self) -> None:
        """Initialize the cross-reference management system."""
        from .utils.cross_refs import CrossReferenceManager
        
        self._cross_ref_manager = CrossReferenceManager()
        self._cross_ref_manager.build_index(self.corpora_data)
    
    def _build_semantic_graph(self) -> None:
        """Build semantic relationship graph from all corpus data."""
        self._semantic_graph = {
            'nodes': {},
            'edges': [],
            'relationship_types': set(),
            'confidence_weights': {}
        }
        
        # Build nodes from all corpus entries
        for corpus_name, corpus_data in self.corpora_data.items():
            self._add_corpus_nodes_to_graph(corpus_name, corpus_data)
        
        # Build edges from cross-references
        if hasattr(self, '_cross_ref_manager'):
            self._add_cross_reference_edges_to_graph()
        
        # Add semantic relationship edges
        self._add_semantic_relationship_edges()
    
    def _add_corpus_nodes_to_graph(self, corpus_name: str, corpus_data: Dict[str, Any]) -> None:
        """Add corpus entries as nodes to the semantic graph."""
        if corpus_name == 'verbnet':
            for class_id, class_data in corpus_data.get('classes', {}).items():
                node_key = f"verbnet:{class_id}"
                self._semantic_graph['nodes'][node_key] = {
                    'corpus': corpus_name,
                    'id': class_id,
                    'type': 'verb_class',
                    'semantic_info': self._extract_semantic_info(class_data, 'verbnet')
                }
        
        elif corpus_name == 'framenet':
            for frame_name, frame_data in corpus_data.get('frames', {}).items():
                node_key = f"framenet:{frame_name}"
                self._semantic_graph['nodes'][node_key] = {
                    'corpus': corpus_name,
                    'id': frame_name,
                    'type': 'frame',
                    'semantic_info': self._extract_semantic_info(frame_data, 'framenet')
                }
        
        elif corpus_name == 'propbank':
            for lemma, predicate_data in corpus_data.get('predicates', {}).items():
                for predicate in predicate_data.get('predicates', []):
                    for roleset in predicate.get('rolesets', []):
                        roleset_id = roleset.get('id', '')
                        if roleset_id:
                            node_key = f"propbank:{roleset_id}"
                            self._semantic_graph['nodes'][node_key] = {
                                'corpus': corpus_name,
                                'id': roleset_id,
                                'type': 'roleset',
                                'semantic_info': self._extract_semantic_info(roleset, 'propbank')
                            }
        
        # Add similar logic for other corpora...
    
    def _add_cross_reference_edges_to_graph(self) -> None:
        """Add cross-reference mappings as edges to the semantic graph."""
        cross_ref_index = self._cross_ref_manager.cross_reference_index
        
        for source, mappings in cross_ref_index.get('by_source', {}).items():
            for mapping in mappings:
                target = mapping.get('target', '')
                confidence = mapping.get('confidence', 0.0)
                relation = mapping.get('relation', 'mapped')
                
                if source in self._semantic_graph['nodes'] and target in self._semantic_graph['nodes']:
                    edge = {
                        'source': source,
                        'target': target,
                        'type': 'cross_reference',
                        'relation': relation,
                        'confidence': confidence
                    }
                    self._semantic_graph['edges'].append(edge)
                    self._semantic_graph['relationship_types'].add(relation)
    
    def _add_semantic_relationship_edges(self) -> None:
        """Add semantic relationships within corpora as edges."""
        # Add VerbNet class hierarchy relationships
        if 'verbnet' in self.corpora_data:
            self._add_verbnet_hierarchy_edges()
        
        # Add FrameNet frame relationships  
        if 'framenet' in self.corpora_data:
            self._add_framenet_relation_edges()
        
        # Add WordNet semantic relationships
        if 'wordnet' in self.corpora_data:
            self._add_wordnet_relation_edges()
    
    def _add_verbnet_hierarchy_edges(self) -> None:
        """Add VerbNet class hierarchy as semantic edges."""
        verbnet_data = self.corpora_data.get('verbnet', {})
        hierarchy = verbnet_data.get('hierarchy', {}).get('parent_child', {})
        
        for parent_id, children in hierarchy.items():
            parent_key = f"verbnet:{parent_id}"
            for child_id in children:
                child_key = f"verbnet:{child_id}"
                
                if parent_key in self._semantic_graph['nodes'] and child_key in self._semantic_graph['nodes']:
                    edge = {
                        'source': parent_key,
                        'target': child_key,
                        'type': 'semantic_relation',
                        'relation': 'subclass',
                        'confidence': 1.0
                    }
                    self._semantic_graph['edges'].append(edge)
                    self._semantic_graph['relationship_types'].add('subclass')
    
    def _add_framenet_relation_edges(self) -> None:
        """Add FrameNet frame relationships as semantic edges."""
        framenet_data = self.corpora_data.get('framenet', {})
        
        for frame_name, frame_data in framenet_data.get('frames', {}).items():
            source_key = f"framenet:{frame_name}"
            
            for relation in frame_data.get('frame_relations', []):
                relation_type = relation.get('type', 'related')
                for related_frame in relation.get('related_frames', []):
                    target_frame = related_frame.get('name', '')
                    if target_frame:
                        target_key = f"framenet:{target_frame}"
                        
                        if source_key in self._semantic_graph['nodes'] and target_key in self._semantic_graph['nodes']:
                            edge = {
                                'source': source_key,
                                'target': target_key,
                                'type': 'semantic_relation',
                                'relation': relation_type,
                                'confidence': 1.0
                            }
                            self._semantic_graph['edges'].append(edge)
                            self._semantic_graph['relationship_types'].add(relation_type)
    
    def _add_wordnet_relation_edges(self) -> None:
        """Add WordNet semantic relationships as edges."""
        wordnet_data = self.corpora_data.get('wordnet', {})
        
        for pos, synsets in wordnet_data.get('synsets', {}).items():
            for offset, synset in synsets.items():
                source_key = f"wordnet:{pos}:{offset}"
                
                for pointer in synset.get('pointers', []):
                    relation_type = pointer.get('relation_type', '')
                    target_offset = pointer.get('synset_offset', '')
                    target_pos = pointer.get('pos', '')
                    
                    if target_offset and target_pos:
                        target_key = f"wordnet:{target_pos}:{target_offset}"
                        
                        if source_key in self._semantic_graph['nodes'] and target_key in self._semantic_graph['nodes']:
                            edge = {
                                'source': source_key,
                                'target': target_key,
                                'type': 'semantic_relation',
                                'relation': relation_type,
                                'confidence': 1.0
                            }
                            self._semantic_graph['edges'].append(edge)
                            self._semantic_graph['relationship_types'].add(relation_type)
    
    def _get_verbnet_profile(self, lemma: str) -> Dict[str, Any]:
        """Get VerbNet information for a lemma."""
        verbnet_data = self.corpora_data.get('verbnet', {})
        members_index = verbnet_data.get('members_index', {})
        classes_data = verbnet_data.get('classes', {})
        
        profile = {
            'classes': [],
            'total_classes': 0,
            'semantic_roles': set(),
            'syntactic_frames': [],
            'predicates': set()
        }
        
        # Find classes containing this lemma
        lemma_classes = members_index.get(lemma.lower(), [])
        profile['total_classes'] = len(lemma_classes)
        
        for class_id in lemma_classes:
            class_data = classes_data.get(class_id, {})
            if class_data:
                class_info = {
                    'class_id': class_id,
                    'class_name': class_data.get('name', ''),
                    'semantic_roles': class_data.get('themroles', []),
                    'frames': class_data.get('frames', []),
                    'predicates': class_data.get('predicates', [])
                }
                profile['classes'].append(class_info)
                
                # Aggregate semantic information
                for role in class_data.get('themroles', []):
                    profile['semantic_roles'].add(role.get('type', ''))
                
                for frame in class_data.get('frames', []):
                    profile['syntactic_frames'].append(frame.get('description', ''))
                
                for pred in class_data.get('predicates', []):
                    profile['predicates'].add(pred.get('value', ''))
        
        # Convert sets to lists for JSON serialization
        profile['semantic_roles'] = list(profile['semantic_roles'])
        profile['predicates'] = list(profile['predicates'])
        
        return profile
    
    def _get_framenet_profile(self, lemma: str) -> Dict[str, Any]:
        """Get FrameNet information for a lemma."""
        framenet_data = self.corpora_data.get('framenet', {})
        frames = framenet_data.get('frames', {})
        lexical_units = framenet_data.get('lexical_units', {})
        
        profile = {
            'frames': [],
            'lexical_units': [],
            'total_frames': 0,
            'frame_elements': set(),
            'semantic_types': set()
        }
        
        # Find lexical units for this lemma
        lemma_lus = []
        for lu_id, lu_data in lexical_units.items():
            if lu_data.get('name', '').split('.')[0].lower() == lemma.lower():
                lemma_lus.append(lu_data)
        
        profile['lexical_units'] = lemma_lus
        
        # Find frames containing this lemma
        lemma_frames = []
        for frame_name, frame_data in frames.items():
            frame_lus = frame_data.get('lexical_units', [])
            for lu in frame_lus:
                if lu.get('name', '').split('.')[0].lower() == lemma.lower():
                    lemma_frames.append({
                        'frame_name': frame_name,
                        'frame_data': frame_data
                    })
                    
                    # Aggregate frame elements
                    for fe in frame_data.get('frame_elements', []):
                        profile['frame_elements'].add(fe.get('name', ''))
                    
                    # Aggregate semantic types
                    for st in frame_data.get('semantic_types', []):
                        profile['semantic_types'].add(st)
                    
                    break
        
        profile['frames'] = lemma_frames
        profile['total_frames'] = len(lemma_frames)
        
        # Convert sets to lists
        profile['frame_elements'] = list(profile['frame_elements'])
        profile['semantic_types'] = list(profile['semantic_types'])
        
        return profile
    
    def _get_propbank_profile(self, lemma: str) -> Dict[str, Any]:
        """Get PropBank information for a lemma."""
        propbank_data = self.corpora_data.get('propbank', {})
        predicates = propbank_data.get('predicates', {})
        
        profile = {
            'predicates': [],
            'rolesets': [],
            'total_rolesets': 0,
            'argument_roles': set(),
            'examples': []
        }
        
        # Find predicate data for this lemma
        predicate_data = predicates.get(lemma.lower(), {})
        if predicate_data:
            for predicate in predicate_data.get('predicates', []):
                pred_info = {
                    'lemma': predicate.get('lemma', ''),
                    'rolesets': []
                }
                
                for roleset in predicate.get('rolesets', []):
                    roleset_info = {
                        'id': roleset.get('id', ''),
                        'name': roleset.get('name', ''),
                        'roles': roleset.get('roles', []),
                        'examples': roleset.get('examples', [])
                    }
                    pred_info['rolesets'].append(roleset_info)
                    profile['rolesets'].append(roleset_info)
                    
                    # Aggregate argument roles
                    for role in roleset.get('roles', []):
                        profile['argument_roles'].add(role.get('n', ''))
                    
                    # Aggregate examples
                    profile['examples'].extend(roleset.get('examples', []))
                
                profile['predicates'].append(pred_info)
        
        profile['total_rolesets'] = len(profile['rolesets'])
        profile['argument_roles'] = list(profile['argument_roles'])
        
        return profile
    
    def _get_ontonotes_profile(self, lemma: str) -> Dict[str, Any]:
        """Get OntoNotes information for a lemma."""
        ontonotes_data = self.corpora_data.get('ontonotes', {})
        senses = ontonotes_data.get('senses', {})
        
        profile = {
            'senses': [],
            'total_senses': 0,
            'mappings': {},
            'groupings': []
        }
        
        # Find sense data for this lemma
        sense_data = senses.get(lemma.lower(), {})
        if sense_data:
            lemma_senses = sense_data.get('senses', [])
            profile['senses'] = lemma_senses
            profile['total_senses'] = len(lemma_senses)
            
            # Aggregate mappings
            for sense in lemma_senses:
                for target_corpus, mapping_list in sense.get('mappings', {}).items():
                    if target_corpus not in profile['mappings']:
                        profile['mappings'][target_corpus] = []
                    profile['mappings'][target_corpus].extend(mapping_list)
            
            profile['groupings'] = sense_data.get('groupings', [])
        
        return profile
    
    def _get_wordnet_profile(self, lemma: str) -> List[Dict[str, Any]]:
        """Get WordNet information for a lemma."""
        wordnet_data = self.corpora_data.get('wordnet', {})
        index = wordnet_data.get('index', {})
        synsets = wordnet_data.get('synsets', {})
        
        profile = []
        
        # Find synsets for this lemma
        for pos in ['n', 'v', 'a', 'r']:  # noun, verb, adjective, adverb
            lemma_entry = index.get(pos, {}).get(lemma.lower(), {})
            if lemma_entry:
                synset_offsets = lemma_entry.get('synset_offsets', [])
                
                for offset in synset_offsets:
                    synset_data = synsets.get(pos, {}).get(offset, {})
                    if synset_data:
                        synset_info = {
                            'pos': pos,
                            'offset': offset,
                            'gloss': synset_data.get('gloss', ''),
                            'words': synset_data.get('words', []),
                            'pointers': synset_data.get('pointers', []),
                            'relations': self._extract_wordnet_relations(synset_data)
                        }
                        profile.append(synset_info)
        
        return profile
    
    def _get_bso_profile(self, lemma: str) -> Dict[str, Any]:
        """Get BSO information for a lemma."""
        bso_data = self.corpora_data.get('bso', {})
        
        profile = {
            'categories': [],
            'verbnet_mappings': [],
            'semantic_organization': {}
        }
        
        # Find VerbNet classes for this lemma first
        if 'verbnet' in self.corpora_data:
            verbnet_classes = self.get_member_classes(lemma)
            
            # Map VerbNet classes to BSO categories
            vn_to_bso = bso_data.get('vn_to_bso', {})
            for vn_class in verbnet_classes:
                bso_categories = vn_to_bso.get(vn_class, [])
                profile['categories'].extend(bso_categories)
                profile['verbnet_mappings'].append({
                    'verbnet_class': vn_class,
                    'bso_categories': bso_categories
                })
        
        # Remove duplicates
        profile['categories'] = list(set(profile['categories']))
        
        return profile
    
    def _get_semnet_profile(self, lemma: str) -> Dict[str, Any]:
        """Get SemNet information for a lemma."""
        semnet_data = self.corpora_data.get('semnet', {})
        verb_network = semnet_data.get('verb_network', {})
        
        profile = {
            'network_connections': [],
            'semantic_neighbors': [],
            'network_statistics': {}
        }
        
        # Find network connections for this lemma
        lemma_data = verb_network.get(lemma.lower(), {})
        if lemma_data:
            profile['network_connections'] = lemma_data.get('connections', [])
            profile['semantic_neighbors'] = lemma_data.get('neighbors', [])
            profile['network_statistics'] = lemma_data.get('statistics', {})
        
        return profile
    
    def _build_cross_references_for_lemma(self, lemma: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Build cross-references between corpora for a specific lemma."""
        cross_refs = {}
        
        if not hasattr(self, '_cross_ref_manager'):
            return cross_refs
        
        # Find cross-references for VerbNet classes
        for vn_class_info in profile.get('verbnet', {}).get('classes', []):
            class_id = vn_class_info.get('class_id', '')
            if class_id:
                mappings = self._cross_ref_manager.find_mappings(class_id, 'verbnet')
                cross_refs[f'verbnet:{class_id}'] = mappings
        
        # Find cross-references for PropBank rolesets
        for roleset in profile.get('propbank', {}).get('rolesets', []):
            roleset_id = roleset.get('id', '')
            if roleset_id:
                mappings = self._cross_ref_manager.find_mappings(roleset_id, 'propbank')
                cross_refs[f'propbank:{roleset_id}'] = mappings
        
        # Find cross-references for FrameNet frames
        for frame_info in profile.get('framenet', {}).get('frames', []):
            frame_name = frame_info.get('frame_name', '')
            if frame_name:
                mappings = self._cross_ref_manager.find_mappings(frame_name, 'framenet')
                cross_refs[f'framenet:{frame_name}'] = mappings
        
        return cross_refs
    
    def _calculate_profile_confidence(self, profile: Dict[str, Any]) -> float:
        """Calculate confidence score for semantic profile integration."""
        total_score = 0.0
        total_weight = 0.0
        
        # Weight by number of resources with data
        corpus_weights = {
            'verbnet': 0.2,
            'framenet': 0.2,
            'propbank': 0.2,
            'ontonotes': 0.15,
            'wordnet': 0.15,
            'bso': 0.05,
            'semnet': 0.05
        }
        
        for corpus, weight in corpus_weights.items():
            corpus_data = profile.get(corpus, {})
            if corpus_data and self._has_meaningful_data(corpus_data):
                total_score += weight
            total_weight += weight
        
        # Bonus for cross-references
        cross_refs = profile.get('cross_references', {})
        if cross_refs:
            cross_ref_bonus = min(len(cross_refs) * 0.05, 0.2)
            total_score += cross_ref_bonus
            total_weight += 0.2
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _has_meaningful_data(self, corpus_data: Any) -> bool:
        """Check if corpus data contains meaningful information."""
        if isinstance(corpus_data, dict):
            return bool(corpus_data) and any(
                isinstance(v, (list, dict)) and v for v in corpus_data.values()
            )
        elif isinstance(corpus_data, list):
            return len(corpus_data) > 0
        else:
            return bool(corpus_data)
    
    def _get_entry_data(self, entry_id: str, corpus: str) -> Dict[str, Any]:
        """Get detailed data for a specific entry in a corpus."""
        corpus_data = self.corpora_data.get(corpus, {})
        
        if corpus == 'verbnet':
            return corpus_data.get('classes', {}).get(entry_id, {})
        elif corpus == 'framenet':
            return corpus_data.get('frames', {}).get(entry_id, {})
        elif corpus == 'propbank':
            # Search for roleset in predicates
            for predicate_data in corpus_data.get('predicates', {}).values():
                for predicate in predicate_data.get('predicates', []):
                    for roleset in predicate.get('rolesets', []):
                        if roleset.get('id') == entry_id:
                            return roleset
        elif corpus == 'ontonotes':
            return corpus_data.get('senses', {}).get(entry_id, {})
        elif corpus == 'wordnet':
            # Parse wordnet entry format (pos:offset)
            if ':' in entry_id:
                pos, offset = entry_id.split(':', 1)
                return corpus_data.get('synsets', {}).get(pos, {}).get(offset, {})
        
        return {}
    
    def _get_corpus_entry(self, entry_id: str, corpus_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific entry from a corpus by its ID.
        
        Args:
            entry_id (str): ID of the entry to retrieve
            corpus_name (str): Name of the corpus
            
        Returns:
            dict: Entry data if found, None otherwise
        """
        if corpus_name not in self.loaded_corpora:
            return None
            
        corpus_data = self.corpora_data.get(corpus_name, {})
        
        if corpus_name == 'verbnet':
            return corpus_data.get('classes', {}).get(entry_id)
        elif corpus_name == 'framenet':
            return corpus_data.get('frames', {}).get(entry_id)
        elif corpus_name == 'propbank':
            lemma = entry_id.split('.')[0] if '.' in entry_id else entry_id
            return corpus_data.get('frames', {}).get(lemma, {}).get('rolesets', {}).get(entry_id)
        elif corpus_name == 'ontonotes':
            return corpus_data.get('senses', {}).get(entry_id)
        elif corpus_name == 'wordnet':
            # For WordNet, entry_id might be in format "pos:offset"
            if ':' in entry_id:
                pos, offset = entry_id.split(':', 1)
                return corpus_data.get('synsets', {}).get(pos, {}).get(offset)
            else:
                # Search all POS for the entry
                for pos_synsets in corpus_data.get('synsets', {}).values():
                    if entry_id in pos_synsets:
                        return pos_synsets[entry_id]
        elif corpus_name == 'bso':
            return corpus_data.get('categories', {}).get(entry_id)
        elif corpus_name == 'semnet':
            return corpus_data.get('verbs', {}).get(entry_id)
        elif corpus_name == 'reference_docs':
            return corpus_data.get('documents', {}).get(entry_id)
            
        return None
    
    def _find_indirect_mappings(self, entry_id: str, source_corpus: str, target_corpus: str) -> List[Dict[str, Any]]:
        """Find indirect mappings through intermediate corpora."""
        indirect_entries = []
        
        if not hasattr(self, '_cross_ref_manager'):
            return indirect_entries
        
        # Find all direct mappings from source
        all_direct_mappings = self._cross_ref_manager.find_mappings(entry_id, source_corpus)
        
        # For each direct mapping, find mappings to target corpus
        for mapping in all_direct_mappings:
            intermediate_key = mapping.get('target', '')
            if not intermediate_key:
                continue
            
            # Parse intermediate corpus and ID
            parts = intermediate_key.split(':', 1)
            if len(parts) != 2:
                continue
            
            intermediate_corpus, intermediate_id = parts
            
            if intermediate_corpus == target_corpus:
                continue  # This is a direct mapping, not indirect
            
            # Find mappings from intermediate to target
            intermediate_mappings = self._cross_ref_manager.find_mappings(
                intermediate_id, intermediate_corpus, target_corpus
            )
            
            for int_mapping in intermediate_mappings:
                target_key = int_mapping.get('target', '')
                if target_key:
                    target_parts = target_key.split(':', 1)
                    if len(target_parts) == 2:
                        _, target_id = target_parts
                        
                        entry_info = {
                            'entry_id': target_id,
                            'corpus': target_corpus,
                            'confidence': mapping.get('confidence', 0.0) * int_mapping.get('confidence', 0.0),
                            'intermediate_corpus': intermediate_corpus,
                            'intermediate_id': intermediate_id,
                            'entry_data': self._get_entry_data(target_id, target_corpus)
                        }
                        indirect_entries.append(entry_info)
        
        return indirect_entries
    
    def _calculate_semantic_similarity(self, entry1_id: str, corpus1: str, 
                                     entry2_id: str, corpus2: str) -> float:
        """Calculate semantic similarity between two entries."""
        # Get entry data
        entry1_data = self._get_entry_data(entry1_id, corpus1)
        entry2_data = self._get_entry_data(entry2_id, corpus2)
        
        if not entry1_data or not entry2_data:
            return 0.0
        
        # Extract semantic features
        features1 = self._extract_semantic_features(entry1_data, corpus1)
        features2 = self._extract_semantic_features(entry2_data, corpus2)
        
        # Calculate similarity based on common features
        return self._calculate_feature_similarity(features1, features2)
    
    def _extract_semantic_features(self, entry_data: Dict[str, Any], corpus: str) -> Dict[str, Any]:
        """Extract semantic features from entry data."""
        features = {
            'semantic_roles': [],
            'predicates': [],
            'frame_elements': [],
            'semantic_types': [],
            'arguments': []
        }
        
        if corpus == 'verbnet':
            features['semantic_roles'] = [role.get('type', '') for role in entry_data.get('themroles', [])]
            features['predicates'] = [pred.get('value', '') for pred in entry_data.get('predicates', [])]
        elif corpus == 'framenet':
            features['frame_elements'] = [fe.get('name', '') for fe in entry_data.get('frame_elements', [])]
            features['semantic_types'] = entry_data.get('semantic_types', [])
        elif corpus == 'propbank':
            features['arguments'] = [role.get('n', '') for role in entry_data.get('roles', [])]
        
        return features
    
    def _calculate_feature_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """Calculate similarity between two feature sets."""
        total_similarity = 0.0
        feature_count = 0
        
        for feature_type in features1.keys():
            if feature_type in features2:
                list1 = features1[feature_type]
                list2 = features2[feature_type]
                
                if list1 and list2:
                    # Calculate Jaccard similarity
                    set1 = set(list1)
                    set2 = set(list2)
                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    
                    if union > 0:
                        similarity = intersection / union
                        total_similarity += similarity
                        feature_count += 1
        
        return total_similarity / feature_count if feature_count > 0 else 0.0
    
    def _calculate_path_confidence(self, path: List[str]) -> float:
        """Calculate confidence score for a semantic path."""
        if len(path) <= 1:
            return 1.0
        
        total_confidence = 1.0
        
        # Get confidence scores for each edge in the path
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            mapping_key = f"{source}->{target}"
            edge_confidence = self._cross_ref_manager.cross_reference_index.get(
                'confidence_scores', {}
            ).get(mapping_key, 0.5)  # Default confidence if not found
            
            total_confidence *= edge_confidence
        
        # Apply path length penalty
        length_penalty = 1.0 / (len(path) - 1)
        return total_confidence * length_penalty
    
    def _extract_path_relationships(self, path: List[str]) -> List[str]:
        """Extract relationship types for each edge in a path."""
        relationships = []
        
        if not hasattr(self, '_semantic_graph'):
            return relationships
        
        edges = self._semantic_graph.get('edges', [])
        
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Find the edge between these nodes
            for edge in edges:
                if edge.get('source') == source and edge.get('target') == target:
                    relationships.append(edge.get('relation', 'unknown'))
                    break
            else:
                relationships.append('unknown')
        
        return relationships
    
    def _extract_path_semantic_types(self, path: List[str]) -> List[str]:
        """Extract semantic types for each node in a path."""
        semantic_types = []
        
        if not hasattr(self, '_semantic_graph'):
            return semantic_types
        
        nodes = self._semantic_graph.get('nodes', {})
        
        for node_key in path:
            node = nodes.get(node_key, {})
            semantic_type = node.get('type', 'unknown')
            semantic_types.append(semantic_type)
        
        return semantic_types
    
    def _extract_semantic_info(self, data: Dict[str, Any], corpus: str) -> Dict[str, Any]:
        """Extract semantic information from entry data for graph nodes."""
        semantic_info = {}
        
        if corpus == 'verbnet':
            semantic_info = {
                'themroles': [role.get('type', '') for role in data.get('themroles', [])],
                'predicates': [pred.get('value', '') for pred in data.get('predicates', [])],
                'frames': len(data.get('frames', []))
            }
        elif corpus == 'framenet':
            semantic_info = {
                'frame_elements': [fe.get('name', '') for fe in data.get('frame_elements', [])],
                'semantic_types': data.get('semantic_types', []),
                'lexical_units': len(data.get('lexical_units', []))
            }
        elif corpus == 'propbank':
            semantic_info = {
                'roles': [role.get('n', '') for role in data.get('roles', [])],
                'examples': len(data.get('examples', []))
            }
        
        return semantic_info
    
    def _extract_wordnet_relations(self, synset_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract WordNet semantic relations from synset data."""
        relations = {}
        
        for pointer in synset_data.get('pointers', []):
            relation_type = pointer.get('relation_type', '')
            target_offset = pointer.get('synset_offset', '')
            target_pos = pointer.get('pos', '')
            
            if relation_type and target_offset and target_pos:
                if relation_type not in relations:
                    relations[relation_type] = []
                relations[relation_type].append(f"{target_pos}:{target_offset}")
        
        return relations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for validation results."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _validate_entry_schema(self, entry_id: str, corpus: str) -> Dict[str, Any]:
        """Validate a specific entry against its corpus schema."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Get entry data
        entry_data = self._get_entry_data(entry_id, corpus)
        if not entry_data:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Entry {entry_id} not found in {corpus}")
            return validation_result
        
        # Perform basic schema validation based on corpus type
        if corpus == 'verbnet':
            validation_result = self._validate_verbnet_entry_schema(entry_data)
        elif corpus == 'framenet':
            validation_result = self._validate_framenet_entry_schema(entry_data)
        elif corpus == 'propbank':
            validation_result = self._validate_propbank_entry_schema(entry_data)
        # Add other corpus validations as needed
        
        return validation_result
    
    def _validate_verbnet_entry_schema(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate VerbNet entry against expected schema."""
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check required fields
        required_fields = ['name', 'members', 'themroles', 'frames']
        for field in required_fields:
            if field not in entry_data:
                validation['errors'].append(f"Missing required field: {field}")
                validation['valid'] = False
        
        # Check themroles structure
        if 'themroles' in entry_data:
            for i, role in enumerate(entry_data['themroles']):
                if not isinstance(role, dict) or 'type' not in role:
                    validation['warnings'].append(f"Invalid themrole structure at index {i}")
        
        return validation
    
    def _validate_framenet_entry_schema(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FrameNet entry against expected schema."""
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for core frame elements
        if 'frame_elements' in entry_data:
            core_elements = [fe for fe in entry_data['frame_elements'] if fe.get('core', False)]
            if not core_elements:
                validation['warnings'].append("No core frame elements found")
        
        return validation
    
    def _validate_propbank_entry_schema(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PropBank entry against expected schema."""
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check required roleset fields
        required_fields = ['id', 'name', 'roles']
        for field in required_fields:
            if field not in entry_data:
                validation['errors'].append(f"Missing required roleset field: {field}")
                validation['valid'] = False
        
        return validation
    
    def _validate_xml_corpus_files(self, corpus_name: str, corpus_path: Path, 
                                 validator: Optional[Any]) -> Dict[str, Any]:
        """Validate XML files for a corpus."""
        from .utils.validation import validate_corpus_files
        return validate_corpus_files(corpus_path, corpus_name)
    
    def _validate_json_corpus_files(self, corpus_name: str, corpus_path: Path, 
                                  validator: Optional[Any]) -> Dict[str, Any]:
        """Validate JSON files for a corpus."""
        result = {'status': 'valid', 'valid_files': 0, 'invalid_files': 0, 'file_results': {}}
        
        json_files = list(corpus_path.glob('*.json'))
        for json_file in json_files:
            file_result = validator.validate_json_file(json_file)
            result['file_results'][str(json_file)] = file_result
            
            if file_result.get('valid'):
                result['valid_files'] += 1
            else:
                result['invalid_files'] += 1
                result['status'] = 'invalid'
        
        return result
    
    def _validate_csv_corpus_files(self, corpus_name: str, corpus_path: Path) -> Dict[str, Any]:
        """Validate CSV files for a corpus."""
        result = {'status': 'valid', 'valid_files': 0, 'invalid_files': 0, 'file_results': {}}
        
        csv_files = list(corpus_path.glob('*.csv'))
        for csv_file in csv_files:
            try:
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Try to read header
                    
                result['file_results'][str(csv_file)] = {'valid': True, 'errors': [], 'warnings': []}
                result['valid_files'] += 1
                
            except Exception as e:
                result['file_results'][str(csv_file)] = {
                    'valid': False, 
                    'errors': [f"CSV validation error: {e}"], 
                    'warnings': []
                }
                result['invalid_files'] += 1
                result['status'] = 'invalid'
        
        return result
    
    def _validate_wordnet_files(self, corpus_path: Path) -> Dict[str, Any]:
        """Validate WordNet data files."""
        result = {'status': 'valid', 'valid_files': 0, 'invalid_files': 0, 'file_results': {}}
        
        # Look for standard WordNet files
        wn_files = ['index.noun', 'index.verb', 'index.adj', 'index.adv', 
                   'data.noun', 'data.verb', 'data.adj', 'data.adv']
        
        for wn_file in wn_files:
            file_path = corpus_path / wn_file
            if file_path.exists():
                try:
                    # Basic file readability test
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.readline()  # Try to read first line
                    
                    result['file_results'][str(file_path)] = {'valid': True, 'errors': [], 'warnings': []}
                    result['valid_files'] += 1
                    
                except Exception as e:
                    result['file_results'][str(file_path)] = {
                        'valid': False, 
                        'errors': [f"File read error: {e}"], 
                        'warnings': []
                    }
                    result['invalid_files'] += 1
                    result['status'] = 'invalid'
        
        return result
    
    def _check_corpus_integrity(self, corpus_name: str) -> Dict[str, Any]:
        """Check integrity of a specific corpus."""
        integrity = {
            'corpus': corpus_name,
            'total_checks': 0,
            'passed_checks': 0,
            'issues': []
        }
        
        corpus_data = self.corpora_data.get(corpus_name, {})
        
        if corpus_name == 'verbnet':
            integrity.update(self._check_verbnet_integrity(corpus_data))
        elif corpus_name == 'framenet':
            integrity.update(self._check_framenet_integrity(corpus_data))
        elif corpus_name == 'propbank':
            integrity.update(self._check_propbank_integrity(corpus_data))
        # Add other corpus integrity checks
        
        return integrity
    
    def _check_verbnet_integrity(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check VerbNet data integrity."""
        checks = {'total_checks': 0, 'passed_checks': 0, 'issues': []}
        
        classes = corpus_data.get('classes', {})
        members_index = corpus_data.get('members_index', {})
        
        # Check 1: All members in index should exist in classes
        checks['total_checks'] += 1
        member_class_consistency = True
        
        for member, class_list in members_index.items():
            for class_id in class_list:
                if class_id not in classes:
                    checks['issues'].append(f"Member {member} references non-existent class {class_id}")
                    member_class_consistency = False
        
        if member_class_consistency:
            checks['passed_checks'] += 1
        
        # Check 2: All class members should be in members index
        checks['total_checks'] += 1
        class_member_consistency = True
        
        for class_id, class_data in classes.items():
            for member_data in class_data.get('members', []):
                member_name = member_data.get('name', '').lower()
                if member_name and class_id not in members_index.get(member_name, []):
                    checks['issues'].append(f"Class {class_id} member {member_name} not in members index")
                    class_member_consistency = False
        
        if class_member_consistency:
            checks['passed_checks'] += 1
        
        return checks
    
    def _check_framenet_integrity(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check FrameNet data integrity."""
        checks = {'total_checks': 0, 'passed_checks': 0, 'issues': []}
        
        frames = corpus_data.get('frames', {})
        
        # Check frame relation consistency
        checks['total_checks'] += 1
        relation_consistency = True
        
        for frame_name, frame_data in frames.items():
            for relation in frame_data.get('frame_relations', []):
                for related_frame in relation.get('related_frames', []):
                    related_name = related_frame.get('name', '')
                    if related_name and related_name not in frames:
                        checks['issues'].append(f"Frame {frame_name} references non-existent frame {related_name}")
                        relation_consistency = False
        
        if relation_consistency:
            checks['passed_checks'] += 1
        
        return checks
    
    def _check_propbank_integrity(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PropBank data integrity."""
        checks = {'total_checks': 0, 'passed_checks': 0, 'issues': []}
        
        predicates = corpus_data.get('predicates', {})
        
        # Check roleset ID uniqueness
        checks['total_checks'] += 1
        roleset_ids = set()
        id_uniqueness = True
        
        for lemma, predicate_data in predicates.items():
            for predicate in predicate_data.get('predicates', []):
                for roleset in predicate.get('rolesets', []):
                    roleset_id = roleset.get('id', '')
                    if roleset_id:
                        if roleset_id in roleset_ids:
                            checks['issues'].append(f"Duplicate roleset ID: {roleset_id}")
                            id_uniqueness = False
                        roleset_ids.add(roleset_id)
        
        if id_uniqueness:
            checks['passed_checks'] += 1
        
        return checks
    
    def _check_cross_reference_integrity(self) -> Dict[str, Any]:
        """Check cross-reference integrity."""
        checks = {'total_checks': 0, 'passed_checks': 0, 'issues': []}
        
        cross_ref_index = self._cross_ref_manager.cross_reference_index
        
        # Check bidirectional consistency
        checks['total_checks'] += 1
        bidirectional_consistency = True
        
        by_source = cross_ref_index.get('by_source', {})
        by_target = cross_ref_index.get('by_target', {})
        
        for source, mappings in by_source.items():
            for mapping in mappings:
                target = mapping.get('target', '')
                if target:
                    # Check if reverse mapping exists
                    reverse_mappings = by_target.get(target, [])
                    reverse_found = any(rm.get('source') == source for rm in reverse_mappings)
                    if not reverse_found:
                        checks['issues'].append(f"Missing reverse mapping for {source} -> {target}")
                        bidirectional_consistency = False
        
        if bidirectional_consistency:
            checks['passed_checks'] += 1
        
        return checks
    
    def _check_data_consistency(self) -> Dict[str, Any]:
        """Check consistency of data across corpora."""
        checks = {'total_checks': 0, 'passed_checks': 0, 'issues': []}
        
        # Check lemma consistency across corpora
        checks['total_checks'] += 1
        lemma_consistency = True
        
        # Get lemmas from different corpora
        verbnet_lemmas = set()
        propbank_lemmas = set()
        
        if 'verbnet' in self.corpora_data:
            members_index = self.corpora_data['verbnet'].get('members_index', {})
            verbnet_lemmas = set(members_index.keys())
        
        if 'propbank' in self.corpora_data:
            predicates = self.corpora_data['propbank'].get('predicates', {})
            propbank_lemmas = set(predicates.keys())
        
        # Check for lemmas in VerbNet but not PropBank (and vice versa)
        vn_only = verbnet_lemmas - propbank_lemmas
        pb_only = propbank_lemmas - verbnet_lemmas
        
        if len(vn_only) > len(verbnet_lemmas) * 0.5:  # More than 50% mismatch
            checks['issues'].append(f"Large mismatch: {len(vn_only)} lemmas only in VerbNet")
            lemma_consistency = False
        
        if len(pb_only) > len(propbank_lemmas) * 0.5:
            checks['issues'].append(f"Large mismatch: {len(pb_only)} lemmas only in PropBank")
            lemma_consistency = False
        
        if lemma_consistency:
            checks['passed_checks'] += 1
        
        return checks
    
    def _check_missing_data(self) -> Dict[str, Any]:
        """Check for missing critical data."""
        missing_data = {'critical_missing': [], 'warnings': []}
        
        # Check for empty corpora
        for corpus_name in self.loaded_corpora:
            corpus_data = self.corpora_data.get(corpus_name, {})
            if not corpus_data or not any(corpus_data.values()):
                missing_data['critical_missing'].append(f"Corpus {corpus_name} has no data")
        
        # Check for missing cross-references
        if not hasattr(self, '_cross_ref_manager'):
            missing_data['warnings'].append("Cross-reference system not initialized")
        elif not self._cross_ref_manager.cross_reference_index.get('by_source'):
            missing_data['warnings'].append("No cross-reference mappings found")
        
        return missing_data
    
    def _generate_integrity_recommendations(self, integrity_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on integrity check results."""
        recommendations = []
        
        # Low integrity score recommendations
        if integrity_report.get('integrity_score', 1.0) < 0.7:
            recommendations.append("Consider reloading corpus data to resolve integrity issues")
        
        # Missing data recommendations
        missing_data = integrity_report.get('missing_data', {})
        if missing_data.get('critical_missing'):
            recommendations.append("Critical data is missing - verify corpus file paths and permissions")
        
        # Cross-reference recommendations
        cross_ref_issues = integrity_report.get('cross_reference_integrity', {}).get('issues', [])
        if cross_ref_issues:
            recommendations.append("Rebuild cross-reference index to resolve mapping inconsistencies")
        
        # Corpus-specific recommendations
        for corpus, corpus_integrity in integrity_report.get('corpus_integrity', {}).items():
            if corpus_integrity.get('passed_checks', 0) < corpus_integrity.get('total_checks', 1):
                recommendations.append(f"Review {corpus} data for consistency issues")
        
        return recommendations
    
    # Utility Methods
    
    def get_top_parent_id(self, class_id: str) -> str:
        """
        Extract top-level parent ID from a class ID.
        
        Args:
            class_id (str): VerbNet class ID
            
        Returns:
            str: Top parent ID
        """
        if '-' not in class_id:
            return class_id
        
        # For format like "run-51.3.2-1", extract "51" (the numerical class)
        parts = class_id.split('-')
        if len(parts) >= 2:
            # parts[1] should be something like "51.3.2"
            numerical_part = parts[1].split('.')[0]  # Get "51"
            return numerical_part
        
        return class_id
    
    def get_member_classes(self, member_name: str) -> List[str]:
        """
        Get all VerbNet classes containing a specific member.
        
        Args:
            member_name (str): Member verb name
            
        Returns:
            list: Sorted list of class IDs containing the member
        """
        if 'verbnet' not in self.corpora_data:
            return []
        
        verbnet_data = self.corpora_data['verbnet']
        members_index = verbnet_data.get('members_index', {})
        return sorted(members_index.get(member_name.lower(), []))
    
    # Field Information Methods
    
    def get_themrole_fields(self, class_id: str, frame_desc_primary: str, 
                           frame_desc_secondary: str, themrole_name: str) -> Dict[str, Any]:
        """
        Get detailed themrole field information.
        
        Args:
            class_id (str): VerbNet class ID
            frame_desc_primary (str): Primary frame description
            frame_desc_secondary (str): Secondary frame description
            themrole_name (str): Thematic role name
            
        Returns:
            dict: Themrole field details
        """
        if 'verbnet' not in self.corpora_data:
            return {}
        
        verbnet_data = self.corpora_data['verbnet']
        classes = verbnet_data.get('classes', {})
        
        if class_id not in classes:
            return {}
        
        class_data = classes[class_id]
        frames = class_data.get('frames', [])
        
        # Find the specific frame that matches the descriptions
        target_frame = None
        for frame in frames:
            desc_primary = frame.get('description_primary', '')
            desc_secondary = frame.get('description_secondary', '')
            
            if (desc_primary == frame_desc_primary and 
                desc_secondary == frame_desc_secondary):
                target_frame = frame
                break
        
        if not target_frame:
            return {}
        
        # Look for the themrole in the frame's syntax
        themrole_fields = {
            'class_id': class_id,
            'frame_description_primary': frame_desc_primary,
            'frame_description_secondary': frame_desc_secondary,
            'themrole_name': themrole_name,
            'found': False,
            'selectional_restrictions': [],
            'syntactic_restrictions': [],
            'role_type': '',
            'position': None
        }
        
        # Check syntax section for the themrole
        if 'syntax' in target_frame:
            syntax = target_frame['syntax']
            for i, np in enumerate(syntax.get('np', [])):
                role = np.get('role', {})
                if isinstance(role, dict) and role.get('value') == themrole_name:
                    themrole_fields['found'] = True
                    themrole_fields['position'] = i
                    themrole_fields['role_type'] = role.get('type', 'ThemRole')
                    
                    # Get selectional restrictions
                    if 'selrestrs' in np:
                        selrestrs = np['selrestrs']
                        if isinstance(selrestrs, list):
                            for restr in selrestrs:
                                if isinstance(restr, dict):
                                    themrole_fields['selectional_restrictions'].append(restr)
                    
                    # Get syntactic restrictions
                    if 'synrestrs' in np:
                        synrestrs = np['synrestrs']
                        if isinstance(synrestrs, list):
                            for restr in synrestrs:
                                if isinstance(restr, dict):
                                    themrole_fields['syntactic_restrictions'].append(restr)
                    
                    break
        
        # Add definition from reference collections if available
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'themroles' in ref_collections and themrole_name in ref_collections['themroles']:
                ref_data = ref_collections['themroles'][themrole_name]
                themrole_fields['definition'] = ref_data.get('description', '')
                themrole_fields['examples'] = ref_data.get('examples', [])
        
        return themrole_fields
    
    def get_predicate_fields(self, pred_name: str) -> Dict[str, Any]:
        """
        Get predicate field information.
        
        Args:
            pred_name (str): Predicate name
            
        Returns:
            dict: Predicate field details
        """
        predicate_fields = {
            'predicate_name': pred_name,
            'found': False,
            'arity': 0,
            'arg_types': [],
            'usage_examples': [],
            'definition': '',
            'category': 'semantic'
        }
        
        # Get from reference collections first
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'predicates' in ref_collections and pred_name in ref_collections['predicates']:
                ref_data = ref_collections['predicates'][pred_name]
                predicate_fields['found'] = True
                predicate_fields['definition'] = ref_data.get('definition', '')
                predicate_fields['arity'] = ref_data.get('arity', 0)
                predicate_fields['arg_types'] = ref_data.get('arg_types', [])
                predicate_fields['usage_examples'] = ref_data.get('examples', [])
                predicate_fields['category'] = ref_data.get('category', 'semantic')
        
        # Also look for usage in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            usage_examples = []
            
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    if 'semantics' in frame:
                        semantics = frame['semantics']
                        for pred in semantics.get('predicates', []):
                            if pred.get('value') == pred_name:
                                usage_examples.append({
                                    'class_id': class_id,
                                    'frame_description': frame.get('description_primary', ''),
                                    'args': pred.get('args', []),
                                    'predicate_data': pred
                                })
                                
                                if not predicate_fields['found']:
                                    predicate_fields['found'] = True
                                    predicate_fields['arity'] = len(pred.get('args', []))
            
            if usage_examples:
                predicate_fields['usage_examples'].extend(usage_examples)
        
        return predicate_fields
    
    def get_constant_fields(self, constant_name: str) -> Dict[str, Any]:
        """
        Get constant field information.
        
        Args:
            constant_name (str): Constant name
            
        Returns:
            dict: Constant field details
        """
        constant_fields = {
            'constant_name': constant_name,
            'found': False,
            'value': '',
            'type': 'constant',
            'definition': '',
            'usage_examples': []
        }
        
        # Get from reference collections
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if 'constants' in ref_collections and constant_name in ref_collections['constants']:
                ref_data = ref_collections['constants'][constant_name]
                constant_fields['found'] = True
                constant_fields['definition'] = ref_data.get('definition', '')
                constant_fields['value'] = ref_data.get('value', constant_name)
                constant_fields['type'] = ref_data.get('type', 'constant')
                constant_fields['usage_examples'] = ref_data.get('examples', [])
        
        # Look for usage in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            usage_examples = []
            
            for class_id, class_data in classes.items():
                frames = class_data.get('frames', [])
                for frame in frames:
                    if 'semantics' in frame:
                        semantics = frame['semantics']
                        for pred in semantics.get('predicates', []):
                            for arg in pred.get('args', []):
                                if (arg.get('type') == 'Constant' and 
                                    arg.get('value') == constant_name):
                                    usage_examples.append({
                                        'class_id': class_id,
                                        'frame_description': frame.get('description_primary', ''),
                                        'predicate': pred.get('value', ''),
                                        'context': pred
                                    })
                                    
                                    if not constant_fields['found']:
                                        constant_fields['found'] = True
            
            if usage_examples:
                constant_fields['usage_examples'].extend(usage_examples)
        
        return constant_fields
    
    def get_verb_specific_fields(self, feature_name: str) -> Dict[str, Any]:
        """
        Get verb-specific field information.
        
        Args:
            feature_name (str): Feature name
            
        Returns:
            dict: Verb-specific field details
        """
        vs_fields = {
            'feature_name': feature_name,
            'found': False,
            'definition': '',
            'feature_type': 'verb_specific',
            'affected_verbs': [],
            'usage_examples': []
        }
        
        # Get from reference collections
        if hasattr(self.corpus_loader, 'reference_collections'):
            ref_collections = self.corpus_loader.reference_collections
            if ('verb_specific_features' in ref_collections and 
                feature_name in ref_collections['verb_specific_features']):
                ref_data = ref_collections['verb_specific_features'][feature_name]
                vs_fields['found'] = True
                vs_fields['definition'] = ref_data.get('definition', '')
                vs_fields['feature_type'] = ref_data.get('type', 'verb_specific')
                vs_fields['usage_examples'] = ref_data.get('examples', [])
        
        # Look for usage in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            affected_verbs = []
            usage_examples = []
            
            for class_id, class_data in classes.items():
                members = class_data.get('members', [])
                for member in members:
                    if isinstance(member, dict):
                        features = member.get('features', [])
                        if isinstance(features, list):
                            for feature in features:
                                feature_match = False
                                if isinstance(feature, str) and feature == feature_name:
                                    feature_match = True
                                elif isinstance(feature, dict) and feature.get('name') == feature_name:
                                    feature_match = True
                                
                                if feature_match:
                                    verb_name = member.get('name', member.get('lemma', ''))
                                    if verb_name:
                                        affected_verbs.append({
                                            'verb': verb_name,
                                            'class_id': class_id,
                                            'feature_data': feature
                                        })
                                        usage_examples.append({
                                            'class_id': class_id,
                                            'verb': verb_name,
                                            'feature_context': feature
                                        })
                                    
                                    if not vs_fields['found']:
                                        vs_fields['found'] = True
            
            if affected_verbs:
                vs_fields['affected_verbs'] = affected_verbs
                vs_fields['usage_examples'].extend(usage_examples)
        
        return vs_fields
    
    # Internal corpus loading methods (for testing)
    
    def _load_verbnet(self, verbnet_path) -> None:
        """
        Load VerbNet corpus from XML files.
        
        Args:
            verbnet_path: Path to VerbNet corpus directory (str or Path)
        """
        verbnet_path = Path(verbnet_path)  # Ensure it's a Path object
        verbnet_data = {
            'classes': {},
            'hierarchy': {'by_name': {}, 'by_id': {}},
            'members': {}
        }
        
        try:
            # Find all XML files in the VerbNet directory
            xml_files = list(verbnet_path.glob('*.xml'))
            
            if not xml_files:
                print(f"No VerbNet XML files found in {verbnet_path}")
                self.corpora_data['verbnet'] = verbnet_data
                return
            
            # Parse each XML file
            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    if root.tag == 'VNCLASS':
                        class_data = self._parse_verbnet_class(root)
                        if class_data:
                            class_id = class_data['id']
                            verbnet_data['classes'][class_id] = class_data
                            
                            # Build hierarchy
                            self._build_class_hierarchy(class_id, verbnet_data)
                            
                            # Build member mappings
                            for member in class_data.get('members', []):
                                member_name = member.get('name', '')
                                if member_name:
                                    if member_name not in verbnet_data['members']:
                                        verbnet_data['members'][member_name] = []
                                    verbnet_data['members'][member_name].append(class_id)
                                    
                except Exception as e:
                    print(f"Error parsing VerbNet file {xml_file}: {e}")
                    continue
            
            print(f"Successfully loaded {len(verbnet_data['classes'])} VerbNet classes")
            
        except Exception as e:
            print(f"Error loading VerbNet corpus: {e}")
        
        self.corpora_data['verbnet'] = verbnet_data
        if hasattr(self, 'loaded_corpora'):
            self.loaded_corpora.add('verbnet')
    
    def _parse_verbnet_class(self, root: ET.Element) -> Dict[str, Any]:
        """
        Parse a VerbNet class from XML root element.
        
        Args:
            root (ET.Element): XML root element for VerbNet class
            
        Returns:
            dict: Parsed VerbNet class data
        """
        class_data = {
            'id': root.get('ID', ''),
            'members': [],
            'themroles': [],
            'frames': []
        }
        
        try:
            # Parse members
            members_elem = root.find('MEMBERS')
            if members_elem is not None:
                for member in members_elem.findall('MEMBER'):
                    member_data = {
                        'name': member.get('name', ''),
                        'wn': member.get('wn', ''),
                        'grouping': member.get('grouping', '')
                    }
                    class_data['members'].append(member_data)
            
            # Parse thematic roles
            themroles_elem = root.find('THEMROLES')
            if themroles_elem is not None:
                for themrole in themroles_elem.findall('THEMROLE'):
                    themrole_data = {
                        'type': themrole.get('type', ''),
                        'selrestrs': []
                    }
                    
                    # Parse selectional restrictions
                    selrestrs_elem = themrole.find('SELRESTRS')
                    if selrestrs_elem is not None:
                        for selrestr in selrestrs_elem.findall('.//SELRESTR'):
                            selrestr_data = {
                                'Value': selrestr.get('Value', ''),
                                'type': selrestr.get('type', '')
                            }
                            themrole_data['selrestrs'].append(selrestr_data)
                    
                    class_data['themroles'].append(themrole_data)
            
            # Parse frames
            frames_elem = root.find('FRAMES')
            if frames_elem is not None:
                for frame in frames_elem.findall('FRAME'):
                    # Get description from FRAME attributes or DESCRIPTION element
                    primary = frame.get('primary', '')
                    secondary = frame.get('secondary', '')
                    
                    # Check for DESCRIPTION element as fallback
                    desc_elem = frame.find('DESCRIPTION')
                    if desc_elem is not None:
                        primary = primary or desc_elem.get('primary', '')
                        secondary = secondary or desc_elem.get('secondary', '')
                    
                    frame_data = {
                        'description': {
                            'primary': primary,
                            'secondary': secondary
                        },
                        'examples': [],
                        'syntax': [],
                        'semantics': []
                    }
                    
                    # Parse examples
                    examples_elem = frame.find('EXAMPLES')
                    if examples_elem is not None:
                        for example in examples_elem.findall('EXAMPLE'):
                            frame_data['examples'].append(example.text or '')
                    
                    # Parse syntax
                    syntax_elem = frame.find('SYNTAX')
                    if syntax_elem is not None:
                        for synelem in syntax_elem:
                            syn_data = {
                                'tag': synelem.tag,
                                'value': synelem.get('value', ''),
                                'restrictions': []
                            }
                            # Add any restrictions
                            for restr in synelem.findall('.//SYNRESTR'):
                                syn_data['restrictions'].append({
                                    'Value': restr.get('Value', ''),
                                    'type': restr.get('type', '')
                                })
                            frame_data['syntax'].append(syn_data)
                    
                    # Parse semantics
                    semantics_elem = frame.find('SEMANTICS')
                    if semantics_elem is not None:
                        for pred in semantics_elem.findall('PRED'):
                            pred_data = {
                                'value': pred.get('value', ''),
                                'args': []
                            }
                            for arg in pred.findall('ARG'):
                                arg_data = {
                                    'type': arg.get('type', ''),
                                    'value': arg.get('value', '')
                                }
                                pred_data['args'].append(arg_data)
                            frame_data['semantics'].append(pred_data)
                    
                    class_data['frames'].append(frame_data)
        
        except Exception as e:
            print(f"Error parsing VerbNet class {class_data['id']}: {e}")
        
        return class_data
    
    def _build_class_hierarchy(self, class_id: str, verbnet_data: Dict[str, Any]) -> None:
        """
        Build class hierarchy entries for a VerbNet class.
        
        Args:
            class_id (str): VerbNet class ID
            verbnet_data (dict): VerbNet data structure to update
        """
        if not class_id:
            return
        
        # Build by name hierarchy (first letter)
        first_char = class_id[0].upper()
        if first_char not in verbnet_data['hierarchy']['by_name']:
            verbnet_data['hierarchy']['by_name'][first_char] = []
        if class_id not in verbnet_data['hierarchy']['by_name'][first_char]:
            verbnet_data['hierarchy']['by_name'][first_char].append(class_id)
        
        # Build by ID hierarchy (numerical prefix)
        id_parts = class_id.split('-')
        if len(id_parts) > 1:
            try:
                numeric_part = id_parts[1].split('.')[0]
                if numeric_part not in verbnet_data['hierarchy']['by_id']:
                    verbnet_data['hierarchy']['by_id'][numeric_part] = []
                if class_id not in verbnet_data['hierarchy']['by_id'][numeric_part]:
                    verbnet_data['hierarchy']['by_id'][numeric_part].append(class_id)
            except (IndexError, ValueError):
                pass

    # Helper methods for search functionality
    
    def _search_lemmas_in_corpus(self, normalized_lemmas: List[str], corpus_name: str, logic: str) -> Dict[str, Any]:
        """
        Search for lemmas in a specific corpus.
        
        Args:
            normalized_lemmas (list): List of normalized lemmas to search
            corpus_name (str): Name of corpus to search
            logic (str): 'and' or 'or' logic for multi-lemma search
            
        Returns:
            dict: Search results for the corpus
        """
        if corpus_name not in self.corpora_data:
            return {}
        
        corpus_data = self.corpora_data[corpus_name]
        matches = {}
        
        if corpus_name == 'verbnet':
            matches = self._search_lemmas_in_verbnet(normalized_lemmas, corpus_data, logic)
        elif corpus_name == 'framenet':
            matches = self._search_lemmas_in_framenet(normalized_lemmas, corpus_data, logic)
        elif corpus_name == 'propbank':
            matches = self._search_lemmas_in_propbank(normalized_lemmas, corpus_data, logic)
        elif corpus_name == 'ontonotes':
            matches = self._search_lemmas_in_ontonotes(normalized_lemmas, corpus_data, logic)
        elif corpus_name == 'wordnet':
            matches = self._search_lemmas_in_wordnet(normalized_lemmas, corpus_data, logic)
        
        return matches
    
    def _search_lemmas_in_verbnet(self, normalized_lemmas: List[str], verbnet_data: Dict[str, Any], logic: str) -> Dict[str, Any]:
        """Search lemmas in VerbNet corpus data."""
        matches = {}
        classes = verbnet_data.get('classes', {})
        members_dict = verbnet_data.get('members', {})
        
        for lemma in normalized_lemmas:
            lemma_matches = []
            
            # Search in member index
            if lemma in members_dict:
                for class_id in members_dict[lemma]:
                    if class_id in classes:
                        match_info = {
                            'type': 'member',
                            'class_id': class_id,
                            'class_data': classes[class_id],
                            'confidence': 1.0
                        }
                        lemma_matches.append(match_info)
            
            # Search in class names (partial match)
            for class_id, class_data in classes.items():
                if lemma in class_id.lower():
                    match_info = {
                        'type': 'class_name',
                        'class_id': class_id,
                        'class_data': class_data,
                        'confidence': 0.8
                    }
                    lemma_matches.append(match_info)
            
            if lemma_matches:
                matches[lemma] = lemma_matches
        
        return matches
    
    def _search_lemmas_in_framenet(self, normalized_lemmas: List[str], framenet_data: Dict[str, Any], logic: str) -> Dict[str, Any]:
        """Search lemmas in FrameNet corpus data."""
        matches = {}
        frames = framenet_data.get('frames', {})
        
        for lemma in normalized_lemmas:
            lemma_matches = []
            
            for frame_name, frame_data in frames.items():
                # Search in lexical units
                lexical_units = frame_data.get('lexical_units', {})
                for lu_name, lu_data in lexical_units.items():
                    if lemma in lu_name.lower():
                        match_info = {
                            'type': 'lexical_unit',
                            'frame_name': frame_name,
                            'lu_name': lu_name,
                            'lu_data': lu_data,
                            'frame_data': frame_data,
                            'confidence': 1.0 if lemma == lu_name.lower() else 0.7
                        }
                        lemma_matches.append(match_info)
                
                # Search in frame names
                if lemma in frame_name.lower():
                    match_info = {
                        'type': 'frame_name',
                        'frame_name': frame_name,
                        'frame_data': frame_data,
                        'confidence': 0.6
                    }
                    lemma_matches.append(match_info)
            
            if lemma_matches:
                matches[lemma] = lemma_matches
        
        return matches
    
    def _search_lemmas_in_propbank(self, normalized_lemmas: List[str], propbank_data: Dict[str, Any], logic: str) -> Dict[str, Any]:
        """Search lemmas in PropBank corpus data."""
        matches = {}
        predicates = propbank_data.get('predicates', {})
        
        for lemma in normalized_lemmas:
            lemma_matches = []
            
            # Direct lemma match
            if lemma in predicates:
                match_info = {
                    'type': 'predicate',
                    'lemma': lemma,
                    'predicate_data': predicates[lemma],
                    'confidence': 1.0
                }
                lemma_matches.append(match_info)
            
            # Partial match in predicate names
            for pred_lemma, pred_data in predicates.items():
                if lemma in pred_lemma.lower() and lemma != pred_lemma.lower():
                    match_info = {
                        'type': 'predicate_partial',
                        'lemma': pred_lemma,
                        'predicate_data': pred_data,
                        'confidence': 0.7
                    }
                    lemma_matches.append(match_info)
            
            if lemma_matches:
                matches[lemma] = lemma_matches
        
        return matches
    
    def _search_lemmas_in_ontonotes(self, normalized_lemmas: List[str], ontonotes_data: Dict[str, Any], logic: str) -> Dict[str, Any]:
        """Search lemmas in OntoNotes corpus data."""
        matches = {}
        sense_inventories = ontonotes_data.get('sense_inventories', {})
        
        for lemma in normalized_lemmas:
            if lemma in sense_inventories:
                match_info = {
                    'type': 'sense_inventory',
                    'lemma': lemma,
                    'sense_data': sense_inventories[lemma],
                    'confidence': 1.0
                }
                matches[lemma] = [match_info]
        
        return matches
    
    def _search_lemmas_in_wordnet(self, normalized_lemmas: List[str], wordnet_data: Dict[str, Any], logic: str) -> Dict[str, Any]:
        """Search lemmas in WordNet corpus data."""
        matches = {}
        index_data = wordnet_data.get('index', {})
        
        for lemma in normalized_lemmas:
            lemma_matches = []
            
            # Search in verb index
            verb_index = index_data.get('verb', {})
            if lemma in verb_index:
                match_info = {
                    'type': 'verb_index',
                    'lemma': lemma,
                    'index_data': verb_index[lemma],
                    'confidence': 1.0
                }
                lemma_matches.append(match_info)
            
            # Search in other POS indices
            for pos, pos_index in index_data.items():
                if pos != 'verb' and lemma in pos_index:
                    match_info = {
                        'type': f'{pos}_index',
                        'lemma': lemma,
                        'index_data': pos_index[lemma],
                        'confidence': 0.8
                    }
                    lemma_matches.append(match_info)
            
            if lemma_matches:
                matches[lemma] = lemma_matches
        
        return matches
    
    def _sort_search_results(self, matches: Dict[str, Any], sort_behavior: str) -> Dict[str, Any]:
        """Sort search results according to specified behavior."""
        if sort_behavior == 'alpha':
            # Sort corpora alphabetically
            return dict(sorted(matches.items()))
        elif sort_behavior == 'num':
            # Sort by number of matches (descending)
            return dict(sorted(matches.items(), key=lambda x: len(x[1]), reverse=True))
        else:
            return matches
    
    def _find_cross_corpus_lemma_mappings(self, normalized_lemmas: List[str], include_resources: List[str]) -> Dict[str, Any]:
        """Find mappings between corpora for the searched lemmas."""
        mappings = {}
        
        for lemma in normalized_lemmas:
            lemma_mappings = {}
            
            # VerbNet-PropBank mappings
            if 'verbnet' in include_resources and 'propbank' in include_resources:
                vn_pb_mappings = self._find_verbnet_propbank_lemma_mappings(lemma)
                if vn_pb_mappings:
                    lemma_mappings['verbnet_propbank'] = vn_pb_mappings
            
            # Add other cross-corpus mappings as needed
            
            if lemma_mappings:
                mappings[lemma] = lemma_mappings
        
        return mappings
    
    def _find_verbnet_propbank_lemma_mappings(self, lemma: str) -> List[Dict[str, Any]]:
        """Find VerbNet-PropBank mappings for a specific lemma."""
        mappings = []
        
        if 'verbnet' in self.corpora_data and 'propbank' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            propbank_data = self.corpora_data['propbank']
            
            # Get VerbNet classes containing this lemma
            members_dict = verbnet_data.get('members', {})
            if lemma in members_dict:
                vn_classes = members_dict[lemma]
                
                # Check if PropBank has this lemma
                predicates = propbank_data.get('predicates', {})
                if lemma in predicates:
                    pb_data = predicates[lemma]
                    
                    # Look for VerbNet class references in PropBank rolesets
                    for roleset in pb_data.get('rolesets', []):
                        vncls = roleset.get('vncls', '')
                        if vncls:
                            mapping_info = {
                                'verbnet_classes': vn_classes,
                                'propbank_roleset': roleset['id'],
                                'verbnet_class_reference': vncls,
                                'confidence': 0.9
                            }
                            mappings.append(mapping_info)
        
        return mappings
    
    def _calculate_search_statistics(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for search results."""
        stats = {
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            corpus_total = sum(len(lemma_matches) for lemma_matches in corpus_matches.values())
            stats['total_matches_by_corpus'][corpus_name] = corpus_total
            stats['total_matches_overall'] += corpus_total
        
        return stats
    
    def _search_semantic_pattern_in_corpus(self, pattern_type: str, pattern_value: str, corpus_name: str) -> List[Dict[str, Any]]:
        """Search for semantic patterns in a specific corpus."""
        matches = []
        
        if corpus_name not in self.corpora_data:
            return matches
        
        corpus_data = self.corpora_data[corpus_name]
        
        if corpus_name == 'verbnet':
            matches = self._search_pattern_in_verbnet(pattern_type, pattern_value, corpus_data)
        elif corpus_name == 'framenet':
            matches = self._search_pattern_in_framenet(pattern_type, pattern_value, corpus_data)
        elif corpus_name == 'propbank':
            matches = self._search_pattern_in_propbank(pattern_type, pattern_value, corpus_data)
        elif corpus_name == 'reference_docs':
            matches = self._search_pattern_in_reference_docs(pattern_type, pattern_value, corpus_data)
        
        return matches
    
    def _search_pattern_in_verbnet(self, pattern_type: str, pattern_value: str, verbnet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for patterns in VerbNet data."""
        matches = []
        classes = verbnet_data.get('classes', {})
        
        for class_id, class_data in classes.items():
            if pattern_type == 'themrole':
                # Search thematic roles
                for themrole in class_data.get('themroles', []):
                    if themrole.get('type', '').lower() == pattern_value.lower():
                        matches.append({
                            'class_id': class_id,
                            'match_type': 'themrole',
                            'match_data': themrole,
                            'context': class_data,
                            'confidence': 1.0
                        })
            
            elif pattern_type == 'predicate':
                # Search semantic predicates
                for frame in class_data.get('frames', []):
                    for semantics_group in frame.get('semantics', []):
                        for pred in semantics_group:
                            if pattern_value.lower() in pred.get('value', '').lower():
                                matches.append({
                                    'class_id': class_id,
                                    'match_type': 'predicate',
                                    'match_data': pred,
                                    'context': {'frame': frame, 'class': class_data},
                                    'confidence': 1.0 if pred.get('value', '').lower() == pattern_value.lower() else 0.7
                                })
            
            elif pattern_type == 'selectional_restriction':
                # Search selectional restrictions
                for themrole in class_data.get('themroles', []):
                    for selrestr in themrole.get('selrestrs', []):
                        if pattern_value.lower() in selrestr.get('Value', '').lower():
                            matches.append({
                                'class_id': class_id,
                                'match_type': 'selectional_restriction',
                                'match_data': selrestr,
                                'context': {'themrole': themrole, 'class': class_data},
                                'confidence': 1.0 if selrestr.get('Value', '').lower() == pattern_value.lower() else 0.7
                            })
        
        return matches
    
    def _search_pattern_in_framenet(self, pattern_type: str, pattern_value: str, framenet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for patterns in FrameNet data."""
        matches = []
        frames = framenet_data.get('frames', {})
        
        for frame_name, frame_data in frames.items():
            if pattern_type == 'frame_element':
                # Search frame elements
                frame_elements = frame_data.get('frame_elements', {})
                for fe_name, fe_data in frame_elements.items():
                    if pattern_value.lower() in fe_name.lower():
                        matches.append({
                            'frame_name': frame_name,
                            'match_type': 'frame_element',
                            'match_data': fe_data,
                            'context': frame_data,
                            'confidence': 1.0 if fe_name.lower() == pattern_value.lower() else 0.7
                        })
            
            elif pattern_type == 'semantic_type':
                # Search in frame definition for semantic types
                definition = frame_data.get('definition', '').lower()
                if pattern_value.lower() in definition:
                    matches.append({
                        'frame_name': frame_name,
                        'match_type': 'semantic_type_in_definition',
                        'match_data': {'definition': definition},
                        'context': frame_data,
                        'confidence': 0.6
                    })
        
        return matches
    
    def _search_pattern_in_propbank(self, pattern_type: str, pattern_value: str, propbank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for patterns in PropBank data."""
        matches = []
        predicates = propbank_data.get('predicates', {})
        
        if pattern_type == 'themrole':
            for lemma, pred_data in predicates.items():
                for roleset in pred_data.get('rolesets', []):
                    for role in roleset.get('roles', []):
                        role_descr = role.get('descr', '').lower()
                        if pattern_value.lower() in role_descr:
                            matches.append({
                                'lemma': lemma,
                                'roleset_id': roleset.get('id'),
                                'match_type': 'role_description',
                                'match_data': role,
                                'context': {'roleset': roleset, 'predicate': pred_data},
                                'confidence': 0.7
                            })
        
        return matches
    
    def _search_pattern_in_reference_docs(self, pattern_type: str, pattern_value: str, ref_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for patterns in reference documentation."""
        matches = []
        
        if pattern_type == 'predicate':
            predicates = ref_data.get('predicates', {})
            for pred_name, pred_info in predicates.items():
                if pattern_value.lower() in pred_name.lower():
                    matches.append({
                        'match_type': 'predicate_definition',
                        'match_data': pred_info,
                        'predicate_name': pred_name,
                        'confidence': 1.0 if pred_name.lower() == pattern_value.lower() else 0.7
                    })
        
        elif pattern_type == 'themrole':
            themroles = ref_data.get('themroles', {})
            for role_name, role_info in themroles.items():
                if pattern_value.lower() in role_name.lower():
                    matches.append({
                        'match_type': 'themrole_definition',
                        'match_data': role_info,
                        'role_name': role_name,
                        'confidence': 1.0 if role_name.lower() == pattern_value.lower() else 0.7
                    })
        
        return matches
    
    # Additional helper methods for cross-references and relationships
    
    def _find_pattern_relationships(self, matches: Dict[str, Any], pattern_type: str) -> Dict[str, Any]:
        """Find relationships between pattern matches across corpora."""
        relationships = {}
        
        # Find relationships between VerbNet and FrameNet matches
        if 'verbnet' in matches and 'framenet' in matches:
            vn_matches = matches['verbnet']
            fn_matches = matches['framenet']
            
            relationships['verbnet_framenet'] = self._find_vn_fn_pattern_relationships(vn_matches, fn_matches, pattern_type)
        
        return relationships
    
    def _find_vn_fn_pattern_relationships(self, vn_matches: List[Dict[str, Any]], fn_matches: List[Dict[str, Any]], pattern_type: str) -> List[Dict[str, Any]]:
        """Find relationships between VerbNet and FrameNet pattern matches."""
        relationships = []
        
        for vn_match in vn_matches:
            for fn_match in fn_matches:
                # Check if they share semantic similarity
                relationship = {
                    'verbnet_match': vn_match,
                    'framenet_match': fn_match,
                    'relationship_type': f'shared_{pattern_type}',
                    'confidence': 0.6
                }
                relationships.append(relationship)
        
        return relationships
    
    def _calculate_pattern_statistics(self, matches: Dict[str, Any], pattern_type: str) -> Dict[str, Any]:
        """Calculate statistics for pattern search results."""
        stats = {
            'pattern_type': pattern_type,
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            total_matches = len(corpus_matches)
            stats['total_matches_by_corpus'][corpus_name] = total_matches
            stats['total_matches_overall'] += total_matches
        
        return stats
    
    def _search_attribute_in_corpus(self, attribute_type: str, query_string: str, corpus_name: str) -> List[Dict[str, Any]]:
        """Search for specific attributes in a corpus."""
        matches = []
        
        if corpus_name not in self.corpora_data:
            return matches
        
        corpus_data = self.corpora_data[corpus_name]
        
        if corpus_name == 'verbnet':
            matches = self._search_verbnet_attributes(attribute_type, query_string, corpus_data)
        elif corpus_name == 'framenet':
            matches = self._search_framenet_attributes(attribute_type, query_string, corpus_data)
        elif corpus_name == 'propbank':
            matches = self._search_propbank_attributes(attribute_type, query_string, corpus_data)
        
        return matches
    
    def _search_verbnet_attributes(self, attribute_type: str, query_string: str, verbnet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search VerbNet for specific attributes."""
        matches = []
        classes = verbnet_data.get('classes', {})
        
        for class_id, class_data in classes.items():
            if attribute_type == 'class_id':
                if query_string.lower() in class_id.lower():
                    matches.append({
                        'match_type': 'class_id',
                        'class_id': class_id,
                        'match_data': class_data,
                        'confidence': 1.0 if query_string.lower() == class_id.lower() else 0.7
                    })
            elif attribute_type == 'member':
                for member in class_data.get('members', []):
                    if query_string.lower() in member.get('name', '').lower():
                        matches.append({
                            'match_type': 'member',
                            'class_id': class_id,
                            'member_data': member,
                            'class_data': class_data,
                            'confidence': 1.0 if query_string.lower() == member.get('name', '').lower() else 0.7
                        })
        
        return matches
    
    def _search_framenet_attributes(self, attribute_type: str, query_string: str, framenet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search FrameNet for specific attributes."""
        matches = []
        frames = framenet_data.get('frames', {})
        
        for frame_name, frame_data in frames.items():
            if attribute_type == 'frame_element':
                frame_elements = frame_data.get('frame_elements', {})
                for fe_name, fe_data in frame_elements.items():
                    if query_string.lower() in fe_name.lower():
                        matches.append({
                            'match_type': 'frame_element',
                            'frame_name': frame_name,
                            'fe_name': fe_name,
                            'fe_data': fe_data,
                            'confidence': 1.0 if query_string.lower() == fe_name.lower() else 0.7
                        })
        
        return matches
    
    def _search_propbank_attributes(self, attribute_type: str, query_string: str, propbank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search PropBank for specific attributes."""
        matches = []
        predicates = propbank_data.get('predicates', {})
        
        for lemma, pred_data in predicates.items():
            if attribute_type == 'predicate':
                if query_string.lower() in lemma.lower():
                    matches.append({
                        'match_type': 'predicate',
                        'lemma': lemma,
                        'predicate_data': pred_data,
                        'confidence': 1.0 if query_string.lower() == lemma.lower() else 0.7
                    })
        
        return matches
    
    def _find_attribute_cross_references(self, matches: Dict[str, Any], attribute_type: str) -> Dict[str, Any]:
        """Find cross-references between attribute matches."""
        cross_refs = {}
        
        # Find relationships between matches across corpora
        if len(matches) > 1:
            corpus_names = list(matches.keys())
            for i, corpus1 in enumerate(corpus_names):
                for corpus2 in corpus_names[i+1:]:
                    ref_key = f"{corpus1}_{corpus2}"
                    cross_refs[ref_key] = self._find_attribute_relationships(
                        matches[corpus1], matches[corpus2], attribute_type
                    )
        
        return cross_refs
    
    def _find_attribute_relationships(self, matches1: List[Dict[str, Any]], matches2: List[Dict[str, Any]], attribute_type: str) -> List[Dict[str, Any]]:
        """Find relationships between attribute matches from two corpora."""
        relationships = []
        
        # Simple heuristic: matches are related if they share common elements
        for match1 in matches1:
            for match2 in matches2:
                relationship = {
                    'match1': match1,
                    'match2': match2,
                    'relationship_type': f'shared_{attribute_type}',
                    'confidence': 0.5
                }
                relationships.append(relationship)
        
        return relationships
    
    def _calculate_attribute_statistics(self, matches: Dict[str, Any], attribute_type: str) -> Dict[str, Any]:
        """Calculate statistics for attribute search results."""
        stats = {
            'attribute_type': attribute_type,
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            total_matches = len(corpus_matches)
            stats['total_matches_by_corpus'][corpus_name] = total_matches
            stats['total_matches_overall'] += total_matches
        
        return stats