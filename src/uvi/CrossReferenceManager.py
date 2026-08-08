"""
CrossReferenceManager Helper Class

Cross-corpus integration with validation-aware relationship mapping using 
CorpusCollectionValidator integration. Provides comprehensive cross-corpus 
navigation and semantic relationship discovery with validation capabilities.

This class replaces UVI's duplicate cross-reference validation methods and enhances
functionality with CorpusCollectionValidator integration.
"""

from typing import Dict, List, Optional, Union, Any, Set, Tuple
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionValidator


class CrossReferenceManager(BaseHelper):
    """
    Cross-corpus integration with validation-aware relationship mapping.
    
    Provides comprehensive cross-corpus navigation, semantic relationship discovery,
    and validation-aware cross-reference management through CorpusCollectionValidator
    integration. This class eliminates duplicate validation code from UVI and provides
    enhanced cross-corpus functionality.
    
    Key Features:
    - Cross-corpus navigation with validation
    - Semantic relationship discovery with validation-aware mapping
    - Validated cross-reference building from validated data only
    - Semantic path tracing between corpora
    - Comprehensive semantic profiling across resources
    - Indirect mapping discovery through validation chains
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize CrossReferenceManager with CorpusCollectionValidator integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Initialize CorpusCollectionValidator for validation-aware operations
        self.corpus_validator = CorpusCollectionValidator(
            loaded_data=uvi_instance.corpora_data,
            logger=self.logger
        )
        
        # Cross-reference index for efficient lookups
        self.cross_reference_index = {}
        self.semantic_graph = {}
        self.validation_cache = {}
        
        # Initialize cross-reference system with validator
        self._initialize_cross_reference_system_with_validator()
    
    def search_by_cross_reference(self, source_id: str, source_corpus: str, 
                                target_corpus: str) -> Dict[str, Any]:
        """
        Cross-corpus navigation with validation-aware mapping.
        
        Args:
            source_id (str): Source entry identifier
            source_corpus (str): Source corpus name
            target_corpus (str): Target corpus name
            
        Returns:
            Dict[str, Any]: Cross-reference search results with validation status
        """
        # Validate source corpus and entry
        if not self._validate_corpus_loaded(source_corpus):
            return {
                'error': f'Source corpus {source_corpus} is not loaded',
                'source_id': source_id,
                'source_corpus': source_corpus,
                'target_corpus': target_corpus
            }
            
        # Validate target corpus
        if not self._validate_corpus_loaded(target_corpus):
            return {
                'error': f'Target corpus {target_corpus} is not loaded',
                'source_id': source_id,
                'source_corpus': source_corpus,
                'target_corpus': target_corpus
            }
            
        # Validate source entry exists
        source_entry = self._get_entry_from_corpus(source_id, source_corpus)
        if not source_entry:
            return {
                'error': f'Source entry {source_id} not found in {source_corpus}',
                'source_id': source_id,
                'source_corpus': source_corpus,
                'target_corpus': target_corpus
            }
            
        # Search for cross-references
        direct_mappings = self._find_direct_mappings(source_id, source_corpus, target_corpus)
        indirect_mappings = self._find_indirect_mappings(source_id, source_corpus, target_corpus)
        
        # Validate found mappings
        validated_mappings = self._validate_cross_reference_mappings(
            direct_mappings + indirect_mappings, source_corpus, target_corpus
        )
        
        return {
            'source_id': source_id,
            'source_corpus': source_corpus,
            'target_corpus': target_corpus,
            'source_entry': source_entry,
            'direct_mappings': direct_mappings,
            'indirect_mappings': indirect_mappings,
            'validated_mappings': validated_mappings,
            'total_mappings': len(validated_mappings),
            'validation_status': 'validated' if validated_mappings else 'no_valid_mappings',
            'timestamp': self._get_timestamp()
        }
        
    def find_semantic_relationships(self, entry_id: str, corpus: str, 
                                  relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enhanced semantic relationship discovery with CorpusCollectionValidator validation.
        
        Args:
            entry_id (str): Entry identifier to find relationships for
            corpus (str): Source corpus name
            relationship_types (Optional[List[str]]): Specific relationship types to find
            
        Returns:
            Dict[str, Any]: Semantic relationships with validation status
        """
        if not self._validate_corpus_loaded(corpus):
            return {
                'error': f'Corpus {corpus} is not loaded',
                'entry_id': entry_id,
                'corpus': corpus
            }
            
        # Default relationship types
        if relationship_types is None:
            relationship_types = ['semantic', 'syntactic', 'thematic', 'lexical', 'cross_corpus']
            
        # Validate entry exists and get its data
        entry_data = self._get_entry_from_corpus(entry_id, corpus)
        if not entry_data:
            return {
                'error': f'Entry {entry_id} not found in {corpus}',
                'entry_id': entry_id,
                'corpus': corpus
            }
            
        relationships = {}
        
        for relationship_type in relationship_types:
            try:
                # Use corpus validator to ensure relationships are valid
                type_relationships = self._find_relationships_by_type(
                    entry_id, corpus, entry_data, relationship_type
                )
                
                # Validate relationships using CorpusCollectionValidator
                validated_relationships = self._validate_relationships(
                    type_relationships, relationship_type, corpus
                )
                
                if validated_relationships:
                    relationships[relationship_type] = validated_relationships
                    
            except Exception as e:
                self.logger.warning(f"Error finding {relationship_type} relationships: {e}")
                
        return {
            'entry_id': entry_id,
            'corpus': corpus,
            'entry_data': entry_data,
            'relationship_types': relationship_types,
            'relationships': relationships,
            'total_relationships': sum(len(rels) for rels in relationships.values()),
            'validation_status': 'validated',
            'timestamp': self._get_timestamp()
        }
        
    def validate_cross_references(self, entry_id: str, source_corpus: str) -> Dict[str, Any]:
        """
        Replace UVI duplicate with CorpusCollectionValidator delegation.
        This replaces UVI lines 1274-1337 with validator-based validation.
        
        Args:
            entry_id (str): Entry to validate cross-references for
            source_corpus (str): Source corpus containing the entry
            
        Returns:
            Dict[str, Any]: Comprehensive cross-reference validation results
        """
        validation_results = {
            'entry_id': entry_id,
            'source_corpus': source_corpus,
            'validation_timestamp': self._get_timestamp(),
            'cross_reference_validation': {},
            'overall_status': 'unknown'
        }
        
        # Validate source corpus and entry
        if not self._validate_corpus_loaded(source_corpus):
            validation_results['overall_status'] = 'error'
            validation_results['error'] = f'Source corpus {source_corpus} not loaded'
            return validation_results
            
        entry_data = self._get_entry_from_corpus(entry_id, source_corpus)
        if not entry_data:
            validation_results['overall_status'] = 'error'
            validation_results['error'] = f'Entry {entry_id} not found in {source_corpus}'
            return validation_results
            
        # Use CorpusCollectionValidator to validate cross-references
        try:
            # Validate corpus collections first
            collection_validation = self.corpus_validator.validate_collections()
            validation_results['collection_validation'] = collection_validation
            
            # Validate cross-references for each target corpus
            target_corpora = [c for c in self.loaded_corpora if c != source_corpus]
            
            for target_corpus in target_corpora:
                target_validation = self._validate_cross_references_to_target(
                    entry_id, source_corpus, target_corpus, entry_data
                )
                validation_results['cross_reference_validation'][target_corpus] = target_validation
                
            # Determine overall status
            all_valid = all(
                target_val.get('status') == 'valid' 
                for target_val in validation_results['cross_reference_validation'].values()
            )
            
            validation_results['overall_status'] = 'valid' if all_valid else 'partial_valid'
            
        except Exception as e:
            validation_results['overall_status'] = 'error'
            validation_results['validation_error'] = str(e)
            self.logger.error(f"Cross-reference validation failed: {e}")
            
        return validation_results
        
    def find_related_entries(self, entry_id: str, source_corpus: str, 
                           max_depth: int = 2) -> Dict[str, Any]:
        """
        Enhanced related entry discovery with validation-aware traversal.
        Enhances UVI lines 1349-1400 with validation-aware discovery.
        
        Args:
            entry_id (str): Starting entry for related entry search
            source_corpus (str): Source corpus name
            max_depth (int): Maximum depth for relationship traversal
            
        Returns:
            Dict[str, Any]: Related entries with validation-aware traversal
        """
        if not self._validate_corpus_loaded(source_corpus):
            return {
                'error': f'Corpus {source_corpus} not loaded',
                'entry_id': entry_id,
                'source_corpus': source_corpus
            }
            
        # Use validation-aware traversal
        visited = set()
        related_entries = {}
        queue = [(entry_id, source_corpus, 0)]  # (entry_id, corpus, depth)
        
        while queue:
            current_id, current_corpus, depth = queue.pop(0)
            
            if depth > max_depth or (current_id, current_corpus) in visited:
                continue
                
            visited.add((current_id, current_corpus))
            
            # Find relationships using validation
            relationships = self.find_semantic_relationships(current_id, current_corpus)
            
            if 'relationships' in relationships:
                depth_key = f'depth_{depth}'
                if depth_key not in related_entries:
                    related_entries[depth_key] = {}
                    
                related_entries[depth_key][f'{current_corpus}:{current_id}'] = {
                    'entry_id': current_id,
                    'corpus': current_corpus,
                    'relationships': relationships['relationships'],
                    'validation_status': relationships.get('validation_status')
                }
                
                # Add related entries to queue for next depth level
                if depth < max_depth:
                    for rel_type, rel_list in relationships['relationships'].items():
                        for rel_entry in rel_list:
                            if isinstance(rel_entry, dict):
                                rel_id = rel_entry.get('id') or rel_entry.get('entry_id')
                                rel_corpus = rel_entry.get('corpus', current_corpus)
                                if rel_id and (rel_id, rel_corpus) not in visited:
                                    queue.append((rel_id, rel_corpus, depth + 1))
        
        return {
            'source_entry': f'{source_corpus}:{entry_id}',
            'max_depth': max_depth,
            'total_depths_explored': len(related_entries),
            'total_entries_found': sum(len(entries) for entries in related_entries.values()),
            'related_entries': related_entries,
            'validation_approach': 'validation_aware_traversal',
            'timestamp': self._get_timestamp()
        }
        
    def trace_semantic_path(self, start_entry: Tuple[str, str], end_entry: Tuple[str, str], 
                          max_hops: int = 5) -> Dict[str, Any]:
        """
        Semantic path tracing between entries across corpora.
        
        Args:
            start_entry (Tuple[str, str]): (entry_id, corpus) for starting point
            end_entry (Tuple[str, str]): (entry_id, corpus) for ending point
            max_hops (int): Maximum number of hops to explore
            
        Returns:
            Dict[str, Any]: Semantic path information between entries
        """
        start_id, start_corpus = start_entry
        end_id, end_corpus = end_entry
        
        # Validate both start and end entries
        if not self._validate_corpus_loaded(start_corpus) or not self._validate_corpus_loaded(end_corpus):
            return {
                'error': 'One or more corpora not loaded',
                'start_entry': start_entry,
                'end_entry': end_entry
            }
            
        # Use breadth-first search for path finding
        visited = set()
        queue = [[(start_id, start_corpus)]]  # List of paths
        
        while queue:
            path = queue.pop(0)
            current_id, current_corpus = path[-1]
            
            if len(path) > max_hops or (current_id, current_corpus) in visited:
                continue
                
            visited.add((current_id, current_corpus))
            
            # Check if we reached the target
            if current_id == end_id and current_corpus == end_corpus:
                return {
                    'path_found': True,
                    'path_length': len(path) - 1,
                    'semantic_path': path,
                    'start_entry': start_entry,
                    'end_entry': end_entry,
                    'max_hops': max_hops,
                    'timestamp': self._get_timestamp()
                }
                
            # Find next steps using cross-references
            cross_refs = self._get_all_cross_references(current_id, current_corpus)
            
            for ref_id, ref_corpus in cross_refs:
                if (ref_id, ref_corpus) not in visited:
                    new_path = path + [(ref_id, ref_corpus)]
                    queue.append(new_path)
        
        return {
            'path_found': False,
            'paths_explored': len(visited),
            'start_entry': start_entry,
            'end_entry': end_entry,
            'max_hops': max_hops,
            'message': 'No semantic path found within hop limit',
            'timestamp': self._get_timestamp()
        }
        
    def get_complete_semantic_profile(self, lemma: str) -> Dict[str, Any]:
        """
        Comprehensive semantic profiling across all available resources.
        
        Args:
            lemma (str): Lemma to build semantic profile for
            
        Returns:
            Dict[str, Any]: Complete semantic profile across all corpora
        """
        profile = {
            'lemma': lemma,
            'profile_timestamp': self._get_timestamp(),
            'corpus_coverage': {},
            'cross_corpus_connections': {},
            'semantic_summary': {}
        }
        
        # Search for lemma in all loaded corpora
        for corpus_name in self.loaded_corpora:
            corpus_profile = self._build_corpus_profile(lemma, corpus_name)
            if corpus_profile:
                profile['corpus_coverage'][corpus_name] = corpus_profile
                
        # Find cross-corpus connections
        profile['cross_corpus_connections'] = self._find_cross_corpus_connections(
            lemma, profile['corpus_coverage']
        )
        
        # Build semantic summary
        profile['semantic_summary'] = self._build_semantic_summary(
            lemma, profile['corpus_coverage'], profile['cross_corpus_connections']
        )
        
        return profile
    
    # Private helper methods
    
    def _initialize_cross_reference_system_with_validator(self):
        """
        Initialize cross-reference system with CorpusCollectionValidator.
        Replaces UVI lines 2298-2397 with validator-based initialization.
        """
        try:
            # Validate corpus collections before building cross-references
            validation_results = self.corpus_validator.validate_collections()
            
            # Only build cross-references from validated corpora
            valid_corpora = [
                corpus for corpus, status in validation_results.items()
                if isinstance(status, dict) and status.get('valid', False)
            ]
            
            self._build_validated_cross_references(valid_corpora)
            
            self.logger.info(f"Cross-reference system initialized with {len(valid_corpora)} validated corpora")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cross-reference system: {e}")
            
    def _build_validated_cross_references(self, valid_corpora: List[str]):
        """Build cross-references from validated data only."""
        self.cross_reference_index = {}
        
        for source_corpus in valid_corpora:
            self.cross_reference_index[source_corpus] = {}
            
            source_data = self._get_corpus_data(source_corpus)
            if not source_data:
                continue
                
            # Build cross-references for each entry in the corpus
            entries = self._get_corpus_entries(source_corpus, source_data)
            
            for entry_id, entry_data in entries.items():
                cross_refs = self._extract_cross_references_from_entry(
                    entry_id, entry_data, source_corpus, valid_corpora
                )
                if cross_refs:
                    self.cross_reference_index[source_corpus][entry_id] = cross_refs
                    
    def _get_corpus_entries(self, corpus_name: str, corpus_data: Dict) -> Dict[str, Any]:
        """Get all entries from a corpus."""
        # Different corpora store entries in different structures
        entry_containers = {
            'verbnet': 'classes',
            'framenet': 'frames',
            'propbank': 'predicates',
            'ontonotes': 'entries',
            'wordnet': 'synsets'
        }
        
        container = entry_containers.get(corpus_name, 'entries')
        return corpus_data.get(container, {})
        
    def _extract_cross_references_from_entry(self, entry_id: str, entry_data: Dict, 
                                           source_corpus: str, valid_corpora: List[str]) -> Dict[str, List]:
        """Extract cross-references from an entry to other corpora."""
        cross_refs = {}
        
        # Look for mapping information in entry data
        mappings = entry_data.get('mappings', {})
        
        for target_corpus in valid_corpora:
            if target_corpus != source_corpus and target_corpus in mappings:
                cross_refs[target_corpus] = mappings[target_corpus]
                
        # Look for implicit cross-references based on shared attributes
        implicit_refs = self._find_implicit_cross_references(
            entry_id, entry_data, source_corpus, valid_corpora
        )
        
        for target_corpus, refs in implicit_refs.items():
            if target_corpus not in cross_refs:
                cross_refs[target_corpus] = refs
            else:
                cross_refs[target_corpus].extend(refs)
                
        return cross_refs
        
    def _find_implicit_cross_references(self, entry_id: str, entry_data: Dict,
                                      source_corpus: str, valid_corpora: List[str]) -> Dict[str, List]:
        """Find implicit cross-references based on shared semantic content."""
        implicit_refs = {}
        
        # Extract semantic features from the entry
        semantic_features = self._extract_semantic_features(entry_data, source_corpus)
        
        # Search for matching features in other corpora
        for target_corpus in valid_corpora:
            if target_corpus != source_corpus:
                matching_entries = self._find_entries_with_matching_features(
                    semantic_features, target_corpus
                )
                if matching_entries:
                    implicit_refs[target_corpus] = matching_entries
                    
        return implicit_refs
        
    def _extract_semantic_features(self, entry_data: Dict, corpus_name: str) -> Set[str]:
        """Extract semantic features from an entry for cross-reference matching."""
        features = set()
        
        # Extract features based on corpus type
        if corpus_name == 'verbnet':
            # Extract themroles, predicates, and syntactic patterns
            features.update(role.get('type', '') for role in entry_data.get('themroles', []))
            features.update(pred.get('value', '') for pred in entry_data.get('predicates', []))
            features.update(entry_data.get('members', []))
            
        elif corpus_name == 'framenet':
            # Extract frame elements, core elements, and lexical units
            features.update(fe.get('name', '') for fe in entry_data.get('frame_elements', []))
            features.update(lu.get('name', '') for lu in entry_data.get('lexical_units', []))
            
        elif corpus_name == 'propbank':
            # Extract argument roles and examples
            for roleset in entry_data.get('rolesets', []):
                features.update(role.get('description', '') for role in roleset.get('roles', []))
                features.update(ex.get('text', '') for ex in roleset.get('examples', []))
                
        # Clean and filter features
        features = {f.lower().strip() for f in features if f and isinstance(f, str)}
        features = {f for f in features if len(f) > 2}  # Remove very short features
        
        return features
        
    def _find_entries_with_matching_features(self, features: Set[str], 
                                           target_corpus: str) -> List[str]:
        """Find entries in target corpus that share semantic features."""
        matching_entries = []
        target_data = self._get_corpus_data(target_corpus)
        
        if not target_data:
            return matching_entries
            
        target_entries = self._get_corpus_entries(target_corpus, target_data)
        
        for entry_id, entry_data in target_entries.items():
            target_features = self._extract_semantic_features(entry_data, target_corpus)
            
            # Check for feature overlap
            overlap = features.intersection(target_features)
            if len(overlap) >= 2:  # Require at least 2 matching features
                matching_entries.append(entry_id)
                
        return matching_entries
        
    def _get_entry_from_corpus(self, entry_id: str, corpus_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific entry from a corpus."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return None
            
        entries = self._get_corpus_entries(corpus_name, corpus_data)
        return entries.get(entry_id)
        
    def _find_direct_mappings(self, source_id: str, source_corpus: str, 
                            target_corpus: str) -> List[str]:
        """Find direct mappings from cross-reference index."""
        if (source_corpus in self.cross_reference_index and 
            source_id in self.cross_reference_index[source_corpus] and
            target_corpus in self.cross_reference_index[source_corpus][source_id]):
            return self.cross_reference_index[source_corpus][source_id][target_corpus]
        return []
        
    def _find_indirect_mappings(self, source_id: str, source_corpus: str, 
                              target_corpus: str) -> List[str]:
        """Find indirect mappings through intermediate corpora."""
        indirect_mappings = []
        
        # Find intermediate corpora that have mappings from source
        intermediate_mappings = self.cross_reference_index.get(source_corpus, {}).get(source_id, {})
        
        for intermediate_corpus, intermediate_ids in intermediate_mappings.items():
            if intermediate_corpus != target_corpus:
                # Check if intermediate entries map to target corpus
                for intermediate_id in intermediate_ids:
                    target_mappings = self._find_direct_mappings(
                        intermediate_id, intermediate_corpus, target_corpus
                    )
                    indirect_mappings.extend(target_mappings)
                    
        return list(set(indirect_mappings))  # Remove duplicates
        
    def _validate_cross_reference_mappings(self, mappings: List[str], 
                                         source_corpus: str, target_corpus: str) -> List[Dict[str, Any]]:
        """Validate cross-reference mappings using CorpusCollectionValidator."""
        validated_mappings = []
        
        for mapping_id in mappings:
            try:
                # Check if target entry exists and is valid
                target_entry = self._get_entry_from_corpus(mapping_id, target_corpus)
                if target_entry:
                    # Use validator to check entry validity
                    validation_result = self._validate_single_mapping(
                        mapping_id, target_entry, target_corpus
                    )
                    
                    if validation_result.get('valid', False):
                        validated_mappings.append({
                            'mapping_id': mapping_id,
                            'target_corpus': target_corpus,
                            'validation_status': 'valid',
                            'target_entry': target_entry
                        })
                        
            except Exception as e:
                self.logger.warning(f"Could not validate mapping {mapping_id}: {e}")
                
        return validated_mappings
        
    def _validate_single_mapping(self, entry_id: str, entry_data: Dict, 
                               corpus_name: str) -> Dict[str, Any]:
        """Validate a single cross-reference mapping."""
        try:
            # Use corpus validator if available
            return self.corpus_validator.validate_entry(entry_id, entry_data, corpus_name)
        except Exception as e:
            self.logger.warning(f"Validation failed for {entry_id}: {e}")
            return {'valid': False, 'error': str(e)}
            
    def _validate_cross_references_to_target(self, entry_id: str, source_corpus: str,
                                           target_corpus: str, entry_data: Dict) -> Dict[str, Any]:
        """Validate cross-references from entry to specific target corpus."""
        validation_result = {
            'target_corpus': target_corpus,
            'status': 'unknown',
            'mappings_found': 0,
            'valid_mappings': 0,
            'invalid_mappings': 0,
            'mapping_details': []
        }
        
        try:
            # Find mappings to target corpus
            direct_mappings = self._find_direct_mappings(entry_id, source_corpus, target_corpus)
            
            validation_result['mappings_found'] = len(direct_mappings)
            
            # Validate each mapping
            for mapping_id in direct_mappings:
                target_entry = self._get_entry_from_corpus(mapping_id, target_corpus)
                
                if target_entry:
                    mapping_validation = self._validate_single_mapping(
                        mapping_id, target_entry, target_corpus
                    )
                    
                    if mapping_validation.get('valid', False):
                        validation_result['valid_mappings'] += 1
                        validation_result['mapping_details'].append({
                            'mapping_id': mapping_id,
                            'status': 'valid'
                        })
                    else:
                        validation_result['invalid_mappings'] += 1
                        validation_result['mapping_details'].append({
                            'mapping_id': mapping_id,
                            'status': 'invalid',
                            'error': mapping_validation.get('error')
                        })
                else:
                    validation_result['invalid_mappings'] += 1
                    validation_result['mapping_details'].append({
                        'mapping_id': mapping_id,
                        'status': 'not_found'
                    })
                    
            # Determine overall status
            if validation_result['valid_mappings'] == validation_result['mappings_found']:
                validation_result['status'] = 'valid'
            elif validation_result['valid_mappings'] > 0:
                validation_result['status'] = 'partial_valid'
            else:
                validation_result['status'] = 'invalid'
                
        except Exception as e:
            validation_result['status'] = 'error'
            validation_result['error'] = str(e)
            
        return validation_result
        
    def _find_relationships_by_type(self, entry_id: str, corpus: str, entry_data: Dict,
                                  relationship_type: str) -> List[Dict[str, Any]]:
        """Find relationships of a specific type for an entry."""
        relationships = []
        
        if relationship_type == 'semantic':
            relationships.extend(self._find_semantic_relationships(entry_id, corpus, entry_data))
        elif relationship_type == 'syntactic':
            relationships.extend(self._find_syntactic_relationships(entry_id, corpus, entry_data))
        elif relationship_type == 'thematic':
            relationships.extend(self._find_thematic_relationships(entry_id, corpus, entry_data))
        elif relationship_type == 'lexical':
            relationships.extend(self._find_lexical_relationships(entry_id, corpus, entry_data))
        elif relationship_type == 'cross_corpus':
            relationships.extend(self._find_cross_corpus_relationships(entry_id, corpus, entry_data))
            
        return relationships
        
    def _validate_relationships(self, relationships: List[Dict[str, Any]], 
                              relationship_type: str, corpus: str) -> List[Dict[str, Any]]:
        """Validate relationships using CorpusCollectionValidator."""
        validated = []
        
        for relationship in relationships:
            try:
                # Validate relationship target exists
                target_id = relationship.get('target_id')
                target_corpus = relationship.get('target_corpus', corpus)
                
                if target_id and self._get_entry_from_corpus(target_id, target_corpus):
                    validated.append(relationship)
                    
            except Exception as e:
                self.logger.warning(f"Could not validate {relationship_type} relationship: {e}")
                
        return validated
        
    def _find_semantic_relationships(self, entry_id: str, corpus: str, 
                                   entry_data: Dict) -> List[Dict[str, Any]]:
        """Find semantic relationships for an entry."""
        # Placeholder - implement semantic relationship discovery
        return []
        
    def _find_syntactic_relationships(self, entry_id: str, corpus: str, 
                                    entry_data: Dict) -> List[Dict[str, Any]]:
        """Find syntactic relationships for an entry."""
        # Placeholder - implement syntactic relationship discovery
        return []
        
    def _find_thematic_relationships(self, entry_id: str, corpus: str, 
                                   entry_data: Dict) -> List[Dict[str, Any]]:
        """Find thematic relationships for an entry."""
        # Placeholder - implement thematic relationship discovery
        return []
        
    def _find_lexical_relationships(self, entry_id: str, corpus: str, 
                                  entry_data: Dict) -> List[Dict[str, Any]]:
        """Find lexical relationships for an entry."""
        # Placeholder - implement lexical relationship discovery
        return []
        
    def _find_cross_corpus_relationships(self, entry_id: str, corpus: str, 
                                       entry_data: Dict) -> List[Dict[str, Any]]:
        """Find cross-corpus relationships for an entry."""
        cross_corpus_rels = []
        
        # Use cross-reference index to find relationships
        if corpus in self.cross_reference_index and entry_id in self.cross_reference_index[corpus]:
            cross_refs = self.cross_reference_index[corpus][entry_id]
            
            for target_corpus, target_ids in cross_refs.items():
                for target_id in target_ids:
                    cross_corpus_rels.append({
                        'relationship_type': 'cross_corpus_mapping',
                        'target_id': target_id,
                        'target_corpus': target_corpus,
                        'source_id': entry_id,
                        'source_corpus': corpus
                    })
                    
        return cross_corpus_rels
        
    def _get_all_cross_references(self, entry_id: str, corpus: str) -> List[Tuple[str, str]]:
        """Get all cross-references for an entry as (id, corpus) tuples."""
        cross_refs = []
        
        if corpus in self.cross_reference_index and entry_id in self.cross_reference_index[corpus]:
            cross_ref_data = self.cross_reference_index[corpus][entry_id]
            
            for target_corpus, target_ids in cross_ref_data.items():
                for target_id in target_ids:
                    cross_refs.append((target_id, target_corpus))
                    
        return cross_refs
        
    def _build_corpus_profile(self, lemma: str, corpus_name: str) -> Optional[Dict[str, Any]]:
        """Build semantic profile for lemma in specific corpus."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return None
            
        # Search for lemma in corpus
        matches = self._search_lemma_in_corpus(lemma, corpus_name, corpus_data)
        
        if not matches:
            return None
            
        return {
            'corpus': corpus_name,
            'lemma': lemma,
            'matches': matches,
            'total_matches': len(matches),
            'profile_timestamp': self._get_timestamp()
        }
        
    def _search_lemma_in_corpus(self, lemma: str, corpus_name: str, 
                              corpus_data: Dict) -> List[Dict[str, Any]]:
        """Search for lemma occurrences in corpus data."""
        matches = []
        entries = self._get_corpus_entries(corpus_name, corpus_data)
        
        lemma_lower = lemma.lower()
        
        for entry_id, entry_data in entries.items():
            if self._lemma_matches_entry(lemma_lower, entry_data, corpus_name):
                matches.append({
                    'entry_id': entry_id,
                    'corpus': corpus_name,
                    'entry_data': entry_data
                })
                
        return matches
        
    def _lemma_matches_entry(self, lemma: str, entry_data: Dict, corpus_name: str) -> bool:
        """Check if lemma matches an entry in the corpus."""
        # Corpus-specific matching logic
        if corpus_name == 'verbnet':
            members = entry_data.get('members', [])
            return any(lemma in member.lower() for member in members)
        elif corpus_name == 'framenet':
            lexical_units = entry_data.get('lexical_units', [])
            return any(lemma in lu.get('name', '').lower() for lu in lexical_units)
        elif corpus_name == 'propbank':
            return lemma in entry_data.get('lemma', '').lower()
            
        return False
        
    def _find_cross_corpus_connections(self, lemma: str, 
                                     corpus_coverage: Dict[str, Dict]) -> Dict[str, Any]:
        """Find cross-corpus connections for lemma."""
        connections = {}
        
        corpus_names = list(corpus_coverage.keys())
        
        for i, source_corpus in enumerate(corpus_names):
            for target_corpus in corpus_names[i+1:]:
                source_matches = corpus_coverage[source_corpus]['matches']
                target_matches = corpus_coverage[target_corpus]['matches']
                
                corpus_connections = []
                
                for source_match in source_matches:
                    source_id = source_match['entry_id']
                    
                    # Find cross-references to target corpus
                    cross_refs = self._find_direct_mappings(source_id, source_corpus, target_corpus)
                    
                    for target_id in cross_refs:
                        if any(tm['entry_id'] == target_id for tm in target_matches):
                            corpus_connections.append({
                                'source_entry': source_id,
                                'target_entry': target_id,
                                'connection_type': 'direct_mapping'
                            })
                            
                if corpus_connections:
                    connection_key = f"{source_corpus}_to_{target_corpus}"
                    connections[connection_key] = corpus_connections
                    
        return connections
        
    def _build_semantic_summary(self, lemma: str, corpus_coverage: Dict, 
                              cross_corpus_connections: Dict) -> Dict[str, Any]:
        """Build comprehensive semantic summary."""
        return {
            'lemma': lemma,
            'total_corpora_coverage': len(corpus_coverage),
            'total_corpus_matches': sum(cc['total_matches'] for cc in corpus_coverage.values()),
            'total_cross_corpus_connections': sum(len(conns) for conns in cross_corpus_connections.values()),
            'coverage_percentage': (len(corpus_coverage) / len(self.loaded_corpora)) * 100,
            'summary_timestamp': self._get_timestamp()
        }
    
    def __str__(self) -> str:
        """String representation of CrossReferenceManager."""
        return f"CrossReferenceManager(corpora={len(self.loaded_corpora)}, cross_refs={len(self.cross_reference_index)})"