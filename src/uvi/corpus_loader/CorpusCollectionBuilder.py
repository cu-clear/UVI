"""
CorpusCollectionBuilder Class

A specialized class for building reference collections from loaded corpus data.
This class extracts reference data building methods from the CorpusLoader class
to provide focused functionality for constructing reference collections.

This class builds collections for:
- Predicate definitions
- Thematic role definitions  
- Verb-specific features
- Syntactic restrictions
- Selectional restrictions
"""

from typing import Dict, Any, List, Set, Callable, Optional
import logging


class CorpusCollectionBuilder:
    """
    A specialized class for building reference collections from loaded corpus data.
    
    This class handles the construction of various reference collections that are
    derived from the loaded corpus data, including predicate definitions, thematic
    role definitions, verb-specific features, syntactic restrictions, and 
    selectional restrictions.
    """
    
    def __init__(self, loaded_data: Dict[str, Any], logger: logging.Logger):
        """
        Initialize CorpusCollectionBuilder with loaded corpus data and logger.
        
        Args:
            loaded_data (Dict[str, Any]): Dictionary containing all loaded corpus data
            logger (logging.Logger): Logger instance for logging operations
        """
        self.loaded_data = loaded_data
        self.logger = logger
        self.reference_collections = {}
    
    def _validate_reference_docs_available(self) -> bool:
        """
        Validate that reference_docs are available in loaded data.
        
        Returns:
            bool: True if reference_docs are available, False otherwise
        """
        return 'reference_docs' in self.loaded_data
    
    def _validate_verbnet_available(self) -> bool:
        """
        Validate that verbnet data is available in loaded data.
        
        Returns:
            bool: True if verbnet data is available, False otherwise
        """
        return 'verbnet' in self.loaded_data
    
    def _build_from_reference_docs(self, 
                                   collection_key: str, 
                                   data_key: str, 
                                   collection_name: str,
                                   transform_func: Optional[Callable] = None) -> bool:
        """
        Common template method for building collections from reference docs.
        
        Args:
            collection_key (str): Key to store the collection under
            data_key (str): Key to extract data from reference_docs
            collection_name (str): Human-readable name for logging
            transform_func (Callable, optional): Function to transform extracted data
            
        Returns:
            bool: Success status
        """
        try:
            if not self._validate_reference_docs_available():
                self.logger.warning(f"Reference docs not loaded, cannot build {collection_name}")
                return False
                
            ref_data = self.loaded_data['reference_docs']
            data = ref_data.get(data_key, {})
            
            # Apply transformation if provided
            if transform_func:
                data = transform_func(data)
            
            self.reference_collections[collection_key] = data
            self.logger.info(f"Built {collection_name}: {len(data)} items")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building {collection_name}: {e}")
            return False
    
    def _extract_from_verbnet_classes(self, 
                                      extractor_func: Callable,
                                      collection_key: str,
                                      collection_name: str,
                                      sort_result: bool = True) -> bool:
        """
        Common template method for extracting data from VerbNet classes.
        
        Args:
            extractor_func (Callable): Function that extracts data from class_data
            collection_key (str): Key to store the collection under
            collection_name (str): Human-readable name for logging
            sort_result (bool): Whether to sort the final result list
            
        Returns:
            bool: Success status
        """
        try:
            extracted_data = set()
            
            # Extract from VerbNet data if available
            if self._validate_verbnet_available():
                verbnet_data = self.loaded_data['verbnet']
                classes = verbnet_data.get('classes', {})
                
                for class_data in classes.values():
                    extracted_data.update(extractor_func(class_data))
            
            # Convert to sorted list if requested
            result = sorted(list(extracted_data)) if sort_result else list(extracted_data)
            
            self.reference_collections[collection_key] = result
            self.logger.info(f"Built {collection_name}: {len(result)} items")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building {collection_name}: {e}")
            return False
    
    def _extract_verb_features_from_class(self, class_data: Dict[str, Any]) -> Set[str]:
        """
        Extract verb-specific features from a VerbNet class.
        
        Args:
            class_data (Dict[str, Any]): VerbNet class data
            
        Returns:
            Set[str]: Set of extracted features
        """
        features = set()
        for frame in class_data.get('frames', []):
            for semantics_group in frame.get('semantics', []):
                for pred in semantics_group:
                    if pred.get('value'):
                        features.add(pred['value'])
        return features
    
    def _extract_syntactic_restrictions_from_class(self, class_data: Dict[str, Any]) -> Set[str]:
        """
        Extract syntactic restrictions from a VerbNet class.
        
        Args:
            class_data (Dict[str, Any]): VerbNet class data
            
        Returns:
            Set[str]: Set of extracted restrictions
        """
        restrictions = set()
        for frame in class_data.get('frames', []):
            for syntax_group in frame.get('syntax', []):
                for element in syntax_group:
                    for synrestr in element.get('synrestrs', []):
                        if synrestr.get('Value'):
                            restrictions.add(synrestr['Value'])
        return restrictions
    
    def _extract_selectional_restrictions_from_class(self, class_data: Dict[str, Any]) -> Set[str]:
        """
        Extract selectional restrictions from a VerbNet class.
        
        Args:
            class_data (Dict[str, Any]): VerbNet class data
            
        Returns:
            Set[str]: Set of extracted restrictions
        """
        restrictions = set()
        for themrole in class_data.get('themroles', []):
            for selrestr in themrole.get('selrestrs', []):
                if selrestr.get('Value'):
                    restrictions.add(selrestr['Value'])
        return restrictions
    
    def build_reference_collections(self) -> Dict[str, bool]:
        """
        Build all reference collections for VerbNet components.
        
        Returns:
            dict: Status of reference collection builds
        """
        results = {
            'predicate_definitions': self.build_predicate_definitions(),
            'themrole_definitions': self.build_themrole_definitions(),
            'verb_specific_features': self.build_verb_specific_features(),
            'syntactic_restrictions': self.build_syntactic_restrictions(),
            'selectional_restrictions': self.build_selectional_restrictions()
        }
        
        self.logger.info(f"Reference collections build complete: {sum(results.values())}/{len(results)} successful")
        
        return results
    
    def build_predicate_definitions(self) -> bool:
        """
        Build predicate definitions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_from_reference_docs(
            collection_key='predicates',
            data_key='predicates',
            collection_name='predicate definitions'
        )
    
    def build_themrole_definitions(self) -> bool:
        """
        Build thematic role definitions collection.
        
        Returns:
            bool: Success status
        """
        return self._build_from_reference_docs(
            collection_key='themroles',
            data_key='themroles',
            collection_name='thematic role definitions'
        )
    
    def build_verb_specific_features(self) -> bool:
        """
        Build verb-specific features collection.
        
        Returns:
            bool: Success status
        """
        try:
            features = set()
            
            # Extract from VerbNet data if available
            if self._validate_verbnet_available():
                verbnet_data = self.loaded_data['verbnet']
                classes = verbnet_data.get('classes', {})
                
                for class_data in classes.values():
                    features.update(self._extract_verb_features_from_class(class_data))
            
            # Extract from reference docs if available
            if self._validate_reference_docs_available():
                ref_data = self.loaded_data['reference_docs']
                vs_features = ref_data.get('verb_specific', {})
                features.update(vs_features.keys())
            
            result = sorted(list(features))
            self.reference_collections['verb_specific_features'] = result
            self.logger.info(f"Built verb-specific features: {len(result)} features")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building verb-specific features: {e}")
            return False
    
    def build_syntactic_restrictions(self) -> bool:
        """
        Build syntactic restrictions collection.
        
        Returns:
            bool: Success status
        """
        return self._extract_from_verbnet_classes(
            extractor_func=self._extract_syntactic_restrictions_from_class,
            collection_key='syntactic_restrictions',
            collection_name='syntactic restrictions'
        )
    
    def build_selectional_restrictions(self) -> bool:
        """
        Build selectional restrictions collection.
        
        Returns:
            bool: Success status
        """
        return self._extract_from_verbnet_classes(
            extractor_func=self._extract_selectional_restrictions_from_class,
            collection_key='selectional_restrictions',
            collection_name='selectional restrictions'
        )