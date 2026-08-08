"""
CorpusRetriever Helper Class

Corpus-specific data retrieval and access using CorpusParser integration.
Provides enhanced corpus data retrieval with CorpusCollectionBuilder reference data 
and CorpusParser-generated data access.

This class replaces UVI's duplicate parsing methods and provides enriched data
retrieval capabilities through CorpusParser and CorpusCollectionBuilder integration.
"""

from typing import Dict, List, Optional, Union, Any
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusParser, CorpusCollectionBuilder


class CorpusRetriever(BaseHelper):
    """
    Corpus-specific data retrieval and access using CorpusParser integration.
    
    Provides enhanced corpus data retrieval with reference data enrichment through
    CorpusCollectionBuilder and pre-parsed data access via CorpusParser. This class
    eliminates duplicate parsing logic from UVI and provides centralized data access.
    
    Key Features:
    - VerbNet class data with reference enrichment
    - FrameNet frame data with lexical unit access
    - PropBank frame data with example management
    - OntoNotes entry data with sense information
    - WordNet synset data with relation tracking
    - BSO category data with mapping access
    - SemNet semantic data retrieval
    - Generic corpus entry retrieval
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize CorpusRetriever with CorpusParser and CorpusCollectionBuilder integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Access to CorpusParser for pre-parsed data
        self.corpus_parser = getattr(uvi_instance, 'corpus_parser', None)
        
        # Access to CorpusCollectionBuilder for enriched data
        self.collection_builder = getattr(uvi_instance, 'collection_builder', None)
        if not self.collection_builder and hasattr(uvi_instance, 'reference_data_provider'):
            self.collection_builder = getattr(uvi_instance.reference_data_provider, 'collection_builder', None)
            
        # Initialize CorpusCollectionBuilder if not available
        if not self.collection_builder:
            try:
                self.collection_builder = CorpusCollectionBuilder(
                    loaded_data=uvi_instance.corpora_data,
                    logger=self.logger
                )
            except Exception as e:
                self.logger.warning(f"Could not initialize CorpusCollectionBuilder: {e}")
                self.collection_builder = None
    
    def get_verbnet_class(self, class_id: str, include_subclasses: bool = True, 
                         include_mappings: bool = True) -> Dict[str, Any]:
        """
        Enhanced VerbNet class retrieval with CorpusCollectionBuilder reference data.
        
        Uses CorpusParser-generated data instead of UVI duplicate parsing and enriches
        results with reference collection data.
        
        Args:
            class_id (str): VerbNet class ID to retrieve
            include_subclasses (bool): Include subclass information
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            Dict[str, Any]: Enhanced VerbNet class data with reference information
        """
        # Use CorpusParser-generated data
        verbnet_data = self._get_corpus_data('verbnet')
        if not verbnet_data:
            return {}
            
        classes = verbnet_data.get('classes', {})
        if class_id not in classes:
            return {}
            
        class_data = classes[class_id].copy()
        
        # Enrich with CorpusCollectionBuilder reference collections
        if self.collection_builder and hasattr(self.collection_builder, 'reference_collections'):
            try:
                # Ensure reference collections are built
                if not self.collection_builder.reference_collections:
                    self.collection_builder.build_reference_collections()
                    
                collections = self.collection_builder.reference_collections
                class_data['available_themroles'] = list(collections.get('themroles', {}).keys())
                class_data['available_predicates'] = list(collections.get('predicates', {}).keys())
                class_data['global_syntactic_restrictions'] = collections.get('syntactic_restrictions', [])
                class_data['global_selectional_restrictions'] = collections.get('selectional_restrictions', [])
            except Exception as e:
                self.logger.warning(f"Could not enrich VerbNet class with reference data: {e}")
        
        if include_subclasses:
            class_data['subclasses'] = self._get_subclass_data(class_id, classes)
            
        if include_mappings:
            class_data['mappings'] = self._get_class_mappings(class_id)
            
        return class_data
        
    def get_framenet_frame(self, frame_name: str, include_lexical_units: bool = True, 
                          include_mappings: bool = True) -> Dict[str, Any]:
        """
        Enhanced FrameNet frame retrieval using CorpusParser-generated data.
        
        Args:
            frame_name (str): FrameNet frame name to retrieve
            include_lexical_units (bool): Include lexical unit information
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            Dict[str, Any]: FrameNet frame data with optional components
        """
        framenet_data = self._get_corpus_data('framenet')
        if not framenet_data:
            return {}
            
        frames = framenet_data.get('frames', {})
        if frame_name not in frames:
            return {}
            
        frame_data = frames[frame_name].copy()
        
        if not include_lexical_units:
            frame_data.pop('lexical_units', None)
            
        if include_mappings:
            frame_data['mappings'] = self._get_frame_mappings(frame_name)
            
        return frame_data
        
    def get_propbank_frame(self, lemma: str, include_examples: bool = True, 
                          include_mappings: bool = True) -> Dict[str, Any]:
        """
        Enhanced PropBank frame retrieval using CorpusParser-generated data.
        
        Args:
            lemma (str): PropBank predicate lemma to retrieve
            include_examples (bool): Include roleset examples
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            Dict[str, Any]: PropBank predicate data with optional components
        """
        propbank_data = self._get_corpus_data('propbank')
        if not propbank_data:
            return {}
            
        predicates = propbank_data.get('predicates', {})
        if lemma not in predicates:
            return {}
            
        predicate_data = predicates[lemma].copy()
        
        if not include_examples:
            # Remove examples from rolesets
            for roleset in predicate_data.get('rolesets', []):
                roleset.pop('examples', None)
                
        if include_mappings:
            predicate_data['mappings'] = self._get_predicate_mappings(lemma)
            
        return predicate_data
        
    def get_ontonotes_entry(self, lemma: str, include_mappings: bool = True) -> Dict[str, Any]:
        """
        OntoNotes entry retrieval with mapping information.
        
        Args:
            lemma (str): OntoNotes lemma to retrieve
            include_mappings (bool): Include cross-corpus mappings
            
        Returns:
            Dict[str, Any]: OntoNotes entry data with optional mappings
        """
        ontonotes_data = self._get_corpus_data('ontonotes')
        if not ontonotes_data:
            return {}
            
        # OntoNotes structure depends on the parsing format
        entries = ontonotes_data.get('entries', {}) or ontonotes_data.get('senses', {})
        if lemma not in entries:
            return {}
            
        entry_data = entries[lemma].copy()
        
        if include_mappings:
            entry_data['mappings'] = self._get_ontonotes_mappings(lemma)
            
        return entry_data
        
    def get_wordnet_synsets(self, word: str, pos: Optional[str] = None, 
                           include_relations: bool = True) -> Dict[str, Any]:
        """
        WordNet synset retrieval with relation information.
        
        Args:
            word (str): Word to look up in WordNet
            pos (Optional[str]): Part of speech filter ('n', 'v', 'a', 'r')
            include_relations (bool): Include synset relations
            
        Returns:
            Dict[str, Any]: WordNet synset data with optional relations
        """
        wordnet_data = self._get_corpus_data('wordnet')
        if not wordnet_data:
            return {}
            
        # WordNet structure varies by parsing approach
        synsets = wordnet_data.get('synsets', {})
        word_synsets = {}
        
        # Search for synsets containing the word
        for synset_id, synset_data in synsets.items():
            if self._word_in_synset(word, synset_data, pos):
                word_synsets[synset_id] = synset_data.copy()
                
                if not include_relations:
                    # Remove relation information to reduce data size
                    for rel_key in ['hypernyms', 'hyponyms', 'meronyms', 'holonyms', 'similar_to']:
                        word_synsets[synset_id].pop(rel_key, None)
        
        return {
            'word': word,
            'pos_filter': pos,
            'total_synsets': len(word_synsets),
            'synsets': word_synsets
        }
        
    def get_bso_categories(self, verb_class: str, include_mappings: bool = True) -> Dict[str, Any]:
        """
        BSO category data retrieval with mapping information.
        
        Args:
            verb_class (str): Verb class to look up in BSO
            include_mappings (bool): Include VerbNet mappings
            
        Returns:
            Dict[str, Any]: BSO category data with optional mappings
        """
        bso_data = self._get_corpus_data('bso')
        if not bso_data:
            return {}
            
        categories = bso_data.get('categories', {}) or bso_data.get('mappings', {})
        if verb_class not in categories:
            return {}
            
        category_data = categories[verb_class].copy()
        
        if include_mappings:
            category_data['verbnet_mappings'] = self._get_bso_mappings(verb_class)
            
        return category_data
        
    def get_semnet_data(self, lemma: str, pos: Optional[str] = None) -> Dict[str, Any]:
        """
        SemNet semantic data retrieval.
        
        Args:
            lemma (str): Lemma to look up in SemNet
            pos (Optional[str]): Part of speech ('noun' or 'verb')
            
        Returns:
            Dict[str, Any]: SemNet semantic network data
        """
        semnet_data = self._get_corpus_data('semnet')
        if not semnet_data:
            return {}
            
        # SemNet has separate noun and verb networks
        networks = {}
        
        if pos is None or pos == 'verb':
            verb_network = semnet_data.get('verb_network', {})
            if lemma in verb_network:
                networks['verb'] = verb_network[lemma]
                
        if pos is None or pos == 'noun':
            noun_network = semnet_data.get('noun_network', {})
            if lemma in noun_network:
                networks['noun'] = noun_network[lemma]
        
        return {
            'lemma': lemma,
            'pos_filter': pos,
            'networks': networks,
            'total_networks': len(networks)
        }
        
    def get_corpus_entry(self, entry_id: str, corpus_name: str) -> Dict[str, Any]:
        """
        Generic corpus entry retrieval for any corpus type.
        
        Args:
            entry_id (str): Entry identifier
            corpus_name (str): Name of corpus to search in
            
        Returns:
            Dict[str, Any]: Generic corpus entry data
        """
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return {}
            
        # Try common entry structure patterns
        entry_containers = ['classes', 'frames', 'predicates', 'entries', 'synsets', 'categories']
        
        for container in entry_containers:
            if container in corpus_data and entry_id in corpus_data[container]:
                return {
                    'corpus': corpus_name,
                    'entry_id': entry_id,
                    'container': container,
                    'data': corpus_data[container][entry_id]
                }
                
        return {}
    
    # Private helper methods
    
    def _get_subclass_data(self, class_id: str, classes: Dict[str, Any]) -> Dict[str, Any]:
        """Get subclass information for a VerbNet class."""
        subclasses = {}
        
        for potential_subclass_id, class_data in classes.items():
            # Check if this class is a subclass of the target class
            if self._is_subclass(potential_subclass_id, class_id):
                subclasses[potential_subclass_id] = {
                    'members': class_data.get('members', []),
                    'themroles': class_data.get('themroles', []),
                    'frames': len(class_data.get('frames', []))
                }
                
        return subclasses
        
    def _is_subclass(self, potential_subclass: str, parent_class: str) -> bool:
        """Check if one VerbNet class is a subclass of another."""
        # VerbNet subclass relationship is typically indicated by class naming
        # e.g., "give-13.1-1" is a subclass of "give-13.1"
        if potential_subclass.startswith(parent_class + '-'):
            return True
        return False
        
    def _get_class_mappings(self, class_id: str) -> Dict[str, Any]:
        """Get cross-corpus mappings for a VerbNet class."""
        mappings = {}
        
        # Check for FrameNet mappings
        framenet_data = self._get_corpus_data('framenet')
        if framenet_data:
            mappings['framenet'] = self._find_verbnet_framenet_mappings(class_id, framenet_data)
            
        # Check for PropBank mappings
        propbank_data = self._get_corpus_data('propbank')
        if propbank_data:
            mappings['propbank'] = self._find_verbnet_propbank_mappings(class_id, propbank_data)
            
        # Check for BSO mappings
        bso_data = self._get_corpus_data('bso')
        if bso_data:
            mappings['bso'] = self._find_verbnet_bso_mappings(class_id, bso_data)
            
        return mappings
        
    def _get_frame_mappings(self, frame_name: str) -> Dict[str, Any]:
        """Get cross-corpus mappings for a FrameNet frame."""
        mappings = {}
        
        # Check for VerbNet mappings
        verbnet_data = self._get_corpus_data('verbnet')
        if verbnet_data:
            mappings['verbnet'] = self._find_framenet_verbnet_mappings(frame_name, verbnet_data)
            
        return mappings
        
    def _get_predicate_mappings(self, lemma: str) -> Dict[str, Any]:
        """Get cross-corpus mappings for a PropBank predicate."""
        mappings = {}
        
        # Check for VerbNet mappings
        verbnet_data = self._get_corpus_data('verbnet')
        if verbnet_data:
            mappings['verbnet'] = self._find_propbank_verbnet_mappings(lemma, verbnet_data)
            
        return mappings
        
    def _get_ontonotes_mappings(self, lemma: str) -> Dict[str, Any]:
        """Get cross-corpus mappings for an OntoNotes entry."""
        mappings = {}
        
        # OntoNotes mappings to other corpora
        verbnet_data = self._get_corpus_data('verbnet')
        if verbnet_data:
            mappings['verbnet'] = self._find_ontonotes_verbnet_mappings(lemma, verbnet_data)
            
        return mappings
        
    def _get_bso_mappings(self, verb_class: str) -> List[str]:
        """Get VerbNet mappings for a BSO category."""
        bso_data = self._get_corpus_data('bso')
        if not bso_data:
            return []
            
        # BSO typically contains direct VerbNet class mappings
        mappings_data = bso_data.get('verbnet_mappings', {})
        return mappings_data.get(verb_class, [])
        
    def _word_in_synset(self, word: str, synset_data: Dict[str, Any], pos_filter: Optional[str]) -> bool:
        """Check if a word appears in a WordNet synset."""
        if pos_filter and synset_data.get('pos') != pos_filter:
            return False
            
        # Check in various word lists
        word_lists = ['words', 'lemmas', 'synonyms']
        word_lower = word.lower()
        
        for word_list_key in word_lists:
            if word_list_key in synset_data:
                word_list = synset_data[word_list_key]
                if isinstance(word_list, list):
                    if any(w.lower() == word_lower for w in word_list):
                        return True
                elif isinstance(word_list, str):
                    if word_list.lower() == word_lower:
                        return True
                        
        return False
        
    # Mapping discovery methods (placeholder implementations)
    
    def _find_verbnet_framenet_mappings(self, class_id: str, framenet_data: Dict) -> List[str]:
        """Find FrameNet frames mapped to a VerbNet class."""
        # Placeholder - implement actual mapping discovery logic
        return []
        
    def _find_verbnet_propbank_mappings(self, class_id: str, propbank_data: Dict) -> List[str]:
        """Find PropBank predicates mapped to a VerbNet class."""
        # Placeholder - implement actual mapping discovery logic
        return []
        
    def _find_verbnet_bso_mappings(self, class_id: str, bso_data: Dict) -> List[str]:
        """Find BSO categories mapped to a VerbNet class."""
        # Placeholder - implement actual mapping discovery logic
        return []
        
    def _find_framenet_verbnet_mappings(self, frame_name: str, verbnet_data: Dict) -> List[str]:
        """Find VerbNet classes mapped to a FrameNet frame."""
        # Placeholder - implement actual mapping discovery logic
        return []
        
    def _find_propbank_verbnet_mappings(self, lemma: str, verbnet_data: Dict) -> List[str]:
        """Find VerbNet classes mapped to a PropBank predicate."""
        # Placeholder - implement actual mapping discovery logic
        return []
        
    def _find_ontonotes_verbnet_mappings(self, lemma: str, verbnet_data: Dict) -> List[str]:
        """Find VerbNet classes mapped to an OntoNotes entry."""
        # Placeholder - implement actual mapping discovery logic
        return []
    
    def __str__(self) -> str:
        """String representation of CorpusRetriever."""
        return f"CorpusRetriever(corpora={len(self.loaded_corpora)}, parser_enabled={self.corpus_parser is not None})"