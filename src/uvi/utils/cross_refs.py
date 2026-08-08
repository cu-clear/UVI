"""
Cross-Corpus Reference Utilities

Provides functionality for managing and validating cross-corpus references
between different linguistic resources including VerbNet, FrameNet, PropBank,
OntoNotes, and WordNet.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import re


class CrossReferenceManager:
    """
    Manager for cross-corpus references and mappings.
    
    Handles building, validating, and querying cross-references between
    different linguistic corpora.
    """
    
    def __init__(self, corpora_data: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize cross-reference manager."""
        self.corpora_data = corpora_data or {}
        self.cross_reference_index = {}
        self.cross_ref_index = {}  # Alias for backward compatibility
        self.mapping_confidence = {}
        self.validation_results = {}
    
    def build_cross_reference_index(self, corpus_data: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Build cross-reference index from corpus data.
        
        Args:
            corpus_data (dict, optional): Data from all loaded corpora. Uses self.corpora_data if not provided.
            
        Returns:
            dict: Cross-reference index
        """
        data = corpus_data or self.corpora_data
        result = self.build_index(data)
        self.cross_ref_index = result
        return result
    
    def build_index(self, corpus_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build comprehensive cross-reference index from all corpus data.
        
        Args:
            corpus_data (dict): Data from all loaded corpora
            
        Returns:
            dict: Cross-reference index
        """
        index = {
            'verbnet_to_propbank': {},
            'propbank_to_verbnet': {},
            'verbnet_to_framenet': {},
            'framenet_to_verbnet': {},
            'propbank_to_framenet': {},
            'framenet_to_propbank': {},
            'by_source': {},  # Source corpus -> target mappings
            'by_target': {},  # Target corpus -> source mappings
            'bidirectional': {},  # Bidirectional mappings
            'confidence_scores': {}
        }
        
        # Build mappings for each corpus
        for corpus_name, data in corpus_data.items():
            if corpus_name == 'verbnet':
                self._index_verbnet_references(data, index)
            elif corpus_name == 'framenet':
                self._index_framenet_references(data, index)
            elif corpus_name == 'propbank':
                self._index_propbank_references(data, index)
            elif corpus_name == 'ontonotes':
                self._index_ontonotes_references(data, index)
            elif corpus_name == 'wordnet':
                self._index_wordnet_references(data, index)
        
        self.cross_reference_index = index
        return index
    
    def _index_verbnet_references(self, verbnet_data: Dict[str, Any], index: Dict[str, Any]):
        """Index cross-references found in VerbNet data."""
        classes = verbnet_data.get('classes', {})
        
        for class_id, class_data in classes.items():
            source_key = f"verbnet:{class_id}"
            
            # Extract WordNet mappings from members
            for member in class_data.get('members', []):
                wn_mapping = member.get('wn', '')
                if wn_mapping:
                    self._add_mapping(index, source_key, f"wordnet:{wn_mapping}", 0.9)
            
            # Extract any explicit cross-references
            cross_refs = class_data.get('cross_references', {})
            for target_corpus, mappings in cross_refs.items():
                for mapping in mappings:
                    mapping_id = mapping if isinstance(mapping, str) else mapping.get('id', '')
                    confidence = 1.0 if isinstance(mapping, str) else mapping.get('confidence', 1.0)
                    
                    if mapping_id:
                        target_key = f"{target_corpus}:{mapping_id}"
                        self._add_mapping(index, source_key, target_key, confidence)
    
    def _index_framenet_references(self, framenet_data: Dict[str, Any], index: Dict[str, Any]):
        """Index cross-references found in FrameNet data."""
        frames = framenet_data.get('frames', {})
        
        for frame_name, frame_data in frames.items():
            source_key = f"framenet:{frame_name}"
            
            # Index frame relations as internal references
            frame_relations = frame_data.get('frame_relations', [])
            for relation in frame_relations:
                for related_frame in relation.get('related_frames', []):
                    related_name = related_frame.get('name', '')
                    if related_name:
                        target_key = f"framenet:{related_name}"
                        relation_type = relation.get('type', 'related')
                        self._add_mapping(index, source_key, target_key, 1.0, {'relation': relation_type})
    
    def _index_propbank_references(self, propbank_data: Dict[str, Any], index: Dict[str, Any]):
        """Index cross-references found in PropBank data."""
        predicates = propbank_data.get('predicates', {})
        
        for lemma, predicate_data in predicates.items():
            for predicate in predicate_data.get('predicates', []):
                for roleset in predicate.get('rolesets', []):
                    roleset_id = roleset.get('id', '')
                    if not roleset_id:
                        continue
                        
                    source_key = f"propbank:{roleset_id}"
                    
                    # VerbNet mappings
                    vncls = roleset.get('vncls', '')
                    if vncls:
                        for vn_class in vncls.split():
                            target_key = f"verbnet:{vn_class.strip()}"
                            self._add_mapping(index, source_key, target_key, 0.95)
                    
                    # FrameNet mappings
                    framenet_ref = roleset.get('framnet', '') or roleset.get('framenet', '')
                    if framenet_ref:
                        target_key = f"framenet:{framenet_ref.strip()}"
                        self._add_mapping(index, source_key, target_key, 0.9)
                    
                    # Check aliases for additional mappings
                    for alias in roleset.get('aliases', []):
                        vn_mapping = alias.get('verbnet', '')
                        fn_mapping = alias.get('framenet', '')
                        
                        if vn_mapping:
                            for vn_class in vn_mapping.split():
                                target_key = f"verbnet:{vn_class.strip()}"
                                self._add_mapping(index, source_key, target_key, 0.85)
                        
                        if fn_mapping:
                            target_key = f"framenet:{fn_mapping.strip()}"
                            self._add_mapping(index, source_key, target_key, 0.85)
    
    def _index_ontonotes_references(self, ontonotes_data: Dict[str, Any], index: Dict[str, Any]):
        """Index cross-references found in OntoNotes data."""
        senses = ontonotes_data.get('senses', {})
        
        for lemma, sense_data in senses.items():
            for i, sense in enumerate(sense_data.get('senses', [])):
                sense_id = f"{lemma}.{sense.get('n', str(i+1))}"
                source_key = f"ontonotes:{sense_id}"
                
                mappings = sense.get('mappings', {})
                for target_corpus, mapping_list in mappings.items():
                    for mapping_id in mapping_list:
                        target_key = f"{target_corpus}:{mapping_id}"
                        self._add_mapping(index, source_key, target_key, 0.8)
    
    def _index_wordnet_references(self, wordnet_data: Dict[str, Any], index: Dict[str, Any]):
        """Index cross-references found in WordNet data."""
        # WordNet primarily serves as a target for other resources
        # Index synset relations as internal references
        for pos, synsets in wordnet_data.get('synsets', {}).items():
            for offset, synset in synsets.items():
                source_key = f"wordnet:{pos}:{offset}"
                
                # Index semantic relations
                for pointer in synset.get('pointers', []):
                    relation_type = pointer.get('relation_type', '')
                    target_offset = pointer.get('synset_offset', '')
                    target_pos = pointer.get('pos', '')
                    
                    if target_offset and target_pos:
                        target_key = f"wordnet:{target_pos}:{target_offset}"
                        self._add_mapping(index, source_key, target_key, 1.0, {'relation': relation_type})
    
    def _add_mapping(self, index: Dict[str, Any], source: str, target: str, 
                     confidence: float, metadata: Optional[Dict[str, Any]] = None):
        """Add a mapping to the cross-reference index."""
        # Add to by_source index
        if source not in index['by_source']:
            index['by_source'][source] = []
        
        mapping_info = {
            'target': target,
            'confidence': confidence
        }
        if metadata:
            mapping_info.update(metadata)
        
        index['by_source'][source].append(mapping_info)
        
        # Add to by_target index
        if target not in index['by_target']:
            index['by_target'][target] = []
        
        reverse_mapping_info = {
            'source': source,
            'confidence': confidence
        }
        if metadata:
            reverse_mapping_info.update(metadata)
        
        index['by_target'][target].append(reverse_mapping_info)
        
        # Store confidence score
        mapping_key = f"{source}->{target}"
        index['confidence_scores'][mapping_key] = confidence
    
    def find_mappings(self, source_id: str, source_corpus: str, 
                     target_corpus: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find mappings from a source entry to target corpora.
        
        Args:
            source_id (str): ID of source entry
            source_corpus (str): Source corpus name
            target_corpus (str): Target corpus name (optional)
            
        Returns:
            list: List of mappings with confidence scores
        """
        source_key = f"{source_corpus}:{source_id}"
        mappings = self.cross_reference_index.get('by_source', {}).get(source_key, [])
        
        if target_corpus:
            # Filter by target corpus
            filtered_mappings = []
            target_prefix = f"{target_corpus}:"
            for mapping in mappings:
                if mapping.get('target', '').startswith(target_prefix):
                    filtered_mappings.append(mapping)
            return filtered_mappings
        
        return mappings
    
    def find_reverse_mappings(self, target_id: str, target_corpus: str, 
                             source_corpus: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find reverse mappings from target to source entries.
        
        Args:
            target_id (str): ID of target entry
            target_corpus (str): Target corpus name
            source_corpus (str): Source corpus name (optional)
            
        Returns:
            list: List of reverse mappings
        """
        target_key = f"{target_corpus}:{target_id}"
        mappings = self.cross_reference_index.get('by_target', {}).get(target_key, [])
        
        if source_corpus:
            # Filter by source corpus
            filtered_mappings = []
            source_prefix = f"{source_corpus}:"
            for mapping in mappings:
                if mapping.get('source', '').startswith(source_prefix):
                    filtered_mappings.append(mapping)
            return filtered_mappings
        
        return mappings
    
    def validate_mapping(self, source_id: str, source_corpus: str, 
                        target_id: str, target_corpus: str, 
                        corpus_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a specific cross-corpus mapping.
        
        Args:
            source_id (str): Source entry ID
            source_corpus (str): Source corpus name
            target_id (str): Target entry ID
            target_corpus (str): Target corpus name
            corpus_data (dict): All corpus data for validation
            
        Returns:
            dict: Validation results
        """
        validation = {
            'valid': False,
            'exists_in_source': False,
            'exists_in_target': False,
            'mapping_found': False,
            'confidence': 0.0,
            'errors': [],
            'warnings': []
        }
        
        # Check if source entry exists
        source_data = corpus_data.get(source_corpus, {})
        source_exists = self._entry_exists(source_id, source_data, source_corpus)
        validation['exists_in_source'] = source_exists
        
        if not source_exists:
            validation['errors'].append(f"Source entry {source_id} not found in {source_corpus}")
        
        # Check if target entry exists
        target_data = corpus_data.get(target_corpus, {})
        target_exists = self._entry_exists(target_id, target_data, target_corpus)
        validation['exists_in_target'] = target_exists
        
        if not target_exists:
            validation['errors'].append(f"Target entry {target_id} not found in {target_corpus}")
        
        # Check if mapping exists in index
        mappings = self.find_mappings(source_id, source_corpus, target_corpus)
        mapping_found = any(target_id in mapping.get('target', '') for mapping in mappings)
        validation['mapping_found'] = mapping_found
        
        if mapping_found:
            # Find confidence score
            mapping_key = f"{source_corpus}:{source_id}->{target_corpus}:{target_id}"
            validation['confidence'] = self.cross_reference_index.get('confidence_scores', {}).get(mapping_key, 0.0)
        else:
            validation['warnings'].append("Mapping not found in cross-reference index")
        
        validation['valid'] = source_exists and target_exists and mapping_found
        
        return validation
    
    def _entry_exists(self, entry_id: str, corpus_data: Dict[str, Any], corpus_name: str) -> bool:
        """Check if an entry exists in corpus data."""
        if corpus_name == 'verbnet':
            return entry_id in corpus_data.get('classes', {})
        elif corpus_name == 'framenet':
            return entry_id in corpus_data.get('frames', {})
        elif corpus_name == 'propbank':
            # Check if it's a roleset ID
            for predicate_data in corpus_data.get('predicates', {}).values():
                for predicate in predicate_data.get('predicates', []):
                    for roleset in predicate.get('rolesets', []):
                        if roleset.get('id') == entry_id:
                            return True
            return False
        elif corpus_name == 'ontonotes':
            # Check sense entries
            return entry_id in corpus_data.get('senses', {})
        elif corpus_name == 'wordnet':
            # Check synsets across all POS
            for pos_synsets in corpus_data.get('synsets', {}).values():
                if entry_id in pos_synsets:
                    return True
            return False
        
        return False

    def find_cross_references(self, entry_id: str, source_corpus: str) -> List[Dict[str, Any]]:
        """
        Find cross-references for a specific entry.
        
        Args:
            entry_id (str): ID of the entry
            source_corpus (str): Source corpus name
            
        Returns:
            list: List of cross-references
        """
        return self.find_mappings(entry_id, source_corpus)

    def validate_cross_reference(self, source_id: str, source_corpus: str,
                                target_id: str, target_corpus: str) -> Dict[str, Any]:
        """
        Validate a cross-reference between two entries.
        
        Args:
            source_id (str): Source entry ID
            source_corpus (str): Source corpus name
            target_id (str): Target entry ID
            target_corpus (str): Target corpus name
            
        Returns:
            dict: Validation results
        """
        return self.validate_mapping(source_id, source_corpus, target_id, target_corpus, self.corpora_data)

    def get_mapping_confidence(self, source_id: str, source_corpus: str,
                              target_id: str, target_corpus: str) -> float:
        """
        Get confidence score for a mapping.
        
        Args:
            source_id (str): Source entry ID
            source_corpus (str): Source corpus name  
            target_id (str): Target entry ID
            target_corpus (str): Target corpus name
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        mapping_key = f"{source_corpus}:{source_id}->{target_corpus}:{target_id}"
        return self.cross_reference_index.get('confidence_scores', {}).get(mapping_key, 0.0)


def build_cross_reference_index(corpus_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build cross-reference index from corpus data.
    
    Args:
        corpus_data (dict): Data from all loaded corpora
        
    Returns:
        dict: Cross-reference index
    """
    manager = CrossReferenceManager()
    return manager.build_index(corpus_data)


def validate_cross_references(index: Dict[str, Dict[str, Any]], 
                             corpus_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate cross-references between corpora.
    
    Args:
        index (dict): Cross-reference index
        corpus_data (dict): Data from all loaded corpora
        
    Returns:
        dict: Validation results
    """
    # Index is already provided, no need to build it again
    
    validation_results = {
        'total_mappings': 0,
        'valid_mappings': 0,
        'invalid_mappings': 0,
        'validation_details': {},
        'corpus_pairs': {}
    }
    
    # Count total mappings
    for source, mappings in index.get('by_source', {}).items():
        validation_results['total_mappings'] += len(mappings)
    
    # Sample mappings for validation if requested
    mappings_to_validate = []
    for source, mappings in index.get('by_source', {}).items():
        for mapping in mappings:
            mappings_to_validate.append((source, mapping.get('target', '')))
    
    # For testing, we don't need sampling - validate all mappings
    # if sample_size and sample_size < len(mappings_to_validate):
    #     import random
    #     mappings_to_validate = random.sample(mappings_to_validate, sample_size)
    
    # Validate each mapping
    for source_full, target_full in mappings_to_validate:
        # Parse source and target
        source_parts = source_full.split(':', 1)
        target_parts = target_full.split(':', 1)
        
        if len(source_parts) == 2 and len(target_parts) == 2:
            source_corpus, source_id = source_parts
            target_corpus, target_id = target_parts
            
            validation = manager.validate_mapping(
                source_id, source_corpus, target_id, target_corpus, corpus_data
            )
            
            pair_key = f"{source_corpus}->{target_corpus}"
            if pair_key not in validation_results['corpus_pairs']:
                validation_results['corpus_pairs'][pair_key] = {
                    'total': 0, 'valid': 0, 'invalid': 0
                }
            
            validation_results['corpus_pairs'][pair_key]['total'] += 1
            
            if validation['valid']:
                validation_results['valid_mappings'] += 1
                validation_results['corpus_pairs'][pair_key]['valid'] += 1
            else:
                validation_results['invalid_mappings'] += 1
                validation_results['corpus_pairs'][pair_key]['invalid'] += 1
            
            # Store detailed results for invalid mappings
            if not validation['valid']:
                mapping_key = f"{source_full}->{target_full}"
                validation_results['validation_details'][mapping_key] = validation
    
    return validation_results


def find_semantic_path(start_entry: Tuple[str, str], end_entry: Tuple[str, str], 
                      cross_ref_index: Dict[str, Any], max_depth: int = 3) -> List[List[str]]:
    """
    Find semantic relationship paths between entries across corpora.
    
    Args:
        start_entry (tuple): (corpus, entry_id) for starting point
        end_entry (tuple): (corpus, entry_id) for target
        cross_ref_index (dict): Cross-reference index
        max_depth (int): Maximum path length to explore
        
    Returns:
        list: List of semantic relationship paths
    """
    start_key = f"{start_entry[0]}:{start_entry[1]}"
    end_key = f"{end_entry[0]}:{end_entry[1]}"
    
    # Use BFS to find shortest paths
    from collections import deque
    
    queue = deque([(start_key, [start_key])])
    visited = set()
    paths = []
    
    by_source = cross_ref_index.get('by_source', {})
    
    while queue and len(paths) < 10:  # Limit number of paths
        current_key, path = queue.popleft()
        
        if len(path) > max_depth:
            continue
        
        if current_key in visited:
            continue
        
        visited.add(current_key)
        
        # Check if we reached the target
        if current_key == end_key:
            paths.append(path)
            continue
        
        # Explore neighbors
        for mapping in by_source.get(current_key, []):
            neighbor = mapping.get('target', '')
            if neighbor and neighbor not in visited:
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))
    
    return paths