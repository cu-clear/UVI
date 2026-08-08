"""
CorpusCollectionValidator Class

A class for validating corpus collection integrity and cross-references.
This class is responsible for validating VerbNet, FrameNet, PropBank collections
and their cross-references.

Extracted from CorpusLoader as part of the refactoring plan to separate concerns.
"""

from typing import Dict, Any, List, Callable
import logging


class CorpusCollectionValidator:
    """
    A class for validating corpus collection integrity and cross-references.
    """
    
    def __init__(self, loaded_data: Dict[str, Any], logger: logging.Logger):
        """
        Initialize CorpusCollectionValidator with loaded data and logger.
        
        Args:
            loaded_data (dict): Dictionary containing all loaded corpus data
            logger (logging.Logger): Logger instance for error reporting
        """
        self.loaded_data = loaded_data
        self.logger = logger
    
    def _ensure_not_none(self, data: Any, default: Any) -> Any:
        """
        Null-safety helper: return default if data is None.
        
        Args:
            data: Data to check for None
            default: Default value to return if data is None
            
        Returns:
            Original data if not None, otherwise default
        """
        return default if data is None else data
    
    def _determine_validation_status(self, errors: List[str], warnings: List[str]) -> str:
        """
        Determine validation status based on errors and warnings.
        
        Args:
            errors: List of validation errors
            warnings: List of validation warnings
            
        Returns:
            Status string: 'invalid', 'valid_with_warnings', or 'valid'
        """
        if errors:
            return 'invalid'
        elif warnings:
            return 'valid_with_warnings'
        else:
            return 'valid'
    
    def _build_validation_result(self, errors: List[str], warnings: List[str], 
                               additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build a standardized validation result dictionary.
        
        Args:
            errors: List of validation errors
            warnings: List of validation warnings
            additional_info: Optional additional information to include
            
        Returns:
            Standardized validation result dictionary
        """
        result = {
            'status': self._determine_validation_status(errors, warnings),
            'errors': errors,
            'warnings': warnings
        }
        
        if additional_info:
            result.update(additional_info)
            
        return result
    
    def _validate_collection_with_callback(self, collection_data: Dict[str, Any], 
                                         collection_key: str,
                                         validator_callback: Callable[[str, Any, List[str], List[str]], None],
                                         count_key: str) -> Dict[str, Any]:
        """
        Common validation framework for collections.
        
        Args:
            collection_data: Data for the collection to validate
            collection_key: Key to extract the main collection from data
            validator_callback: Function to validate individual items
            count_key: Key name for the count in the result
            
        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []
        
        # Ensure collection is not None
        collection = self._ensure_not_none(collection_data.get(collection_key, {}), {})
        
        # Validate each item in the collection
        for item_id, item_data in collection.items():
            validator_callback(item_id, item_data, errors, warnings)
        
        # Build result with count information
        additional_info = {count_key: len(collection)}
        return self._build_validation_result(errors, warnings, additional_info)
    
    def validate_collections(self) -> Dict[str, Any]:
        """
        Validate integrity of all collections.
        
        Returns:
            dict: Validation results for each collection
        """
        validation_results = {}
        
        for corpus_name, corpus_data in self.loaded_data.items():
            try:
                if corpus_name == 'verbnet':
                    validation_results[corpus_name] = self._validate_verbnet_collection(corpus_data)
                elif corpus_name == 'framenet':
                    validation_results[corpus_name] = self._validate_framenet_collection(corpus_data)
                elif corpus_name == 'propbank':
                    validation_results[corpus_name] = self._validate_propbank_collection(corpus_data)
                else:
                    validation_results[corpus_name] = {'status': 'no_validation', 'errors': []}
                    
            except Exception as e:
                validation_results[corpus_name] = {
                    'status': 'validation_error',
                    'errors': [str(e)]
                }
        
        return validation_results
    
    def _validate_verbnet_class(self, class_id: str, class_data: Any, 
                               errors: List[str], warnings: List[str]) -> None:
        """
        Validate a single VerbNet class.
        
        Args:
            class_id: ID of the class being validated
            class_data: Data for the class
            errors: List to append errors to
            warnings: List to append warnings to
        """
        if not class_data.get('members'):
            warnings.append(f"Class {class_id} has no members")
        
        if not class_data.get('frames'):
            warnings.append(f"Class {class_id} has no frames")
        
        # Validate frame structure
        frames = self._ensure_not_none(class_data.get('frames', []), [])
        for i, frame in enumerate(frames):
            if not frame.get('description', {}).get('primary'):
                warnings.append(f"Class {class_id} frame {i} missing primary description")
    
    def _validate_verbnet_collection(self, verbnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate VerbNet collection integrity.
        
        Args:
            verbnet_data (dict): VerbNet data to validate
            
        Returns:
            dict: Validation results
        """
        return self._validate_collection_with_callback(
            verbnet_data, 'classes', self._validate_verbnet_class, 'total_classes'
        )
    
    def _validate_framenet_frame(self, frame_name: str, frame_data: Any, 
                                errors: List[str], warnings: List[str]) -> None:
        """
        Validate a single FrameNet frame.
        
        Args:
            frame_name: Name of the frame being validated
            frame_data: Data for the frame
            errors: List to append errors to
            warnings: List to append warnings to
        """
        if not frame_data.get('lexical_units'):
            warnings.append(f"Frame {frame_name} has no lexical units")
        
        if not frame_data.get('definition'):
            warnings.append(f"Frame {frame_name} missing definition")
    
    def _validate_framenet_collection(self, framenet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate FrameNet collection integrity.
        
        Args:
            framenet_data (dict): FrameNet data to validate
            
        Returns:
            dict: Validation results
        """
        return self._validate_collection_with_callback(
            framenet_data, 'frames', self._validate_framenet_frame, 'total_frames'
        )
    
    def _validate_propbank_predicate(self, lemma: str, predicate_data: Any, 
                                    errors: List[str], warnings: List[str]) -> None:
        """
        Validate a single PropBank predicate.
        
        Args:
            lemma: Lemma of the predicate being validated
            predicate_data: Data for the predicate
            errors: List to append errors to
            warnings: List to append warnings to
        """
        if not predicate_data.get('rolesets'):
            warnings.append(f"Predicate {lemma} has no rolesets")
        
        rolesets = self._ensure_not_none(predicate_data.get('rolesets', []), [])
        for roleset in rolesets:
            if not roleset.get('roles'):
                warnings.append(f"Roleset {roleset.get('id', 'unknown')} has no roles")
    
    def _validate_propbank_collection(self, propbank_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PropBank collection integrity.
        
        Args:
            propbank_data (dict): PropBank data to validate
            
        Returns:
            dict: Validation results
        """
        return self._validate_collection_with_callback(
            propbank_data, 'predicates', self._validate_propbank_predicate, 'total_predicates'
        )
    
    def validate_cross_references(self) -> Dict[str, Any]:
        """
        Validate cross-references between collections.
        
        Returns:
            dict: Cross-reference validation results
        """
        validation_results = {
            'vn_pb_mappings': {},
            'vn_fn_mappings': {},
            'vn_wn_mappings': {},
            'on_mappings': {}
        }
        
        # Validate VerbNet-PropBank mappings
        if 'verbnet' in self.loaded_data and 'propbank' in self.loaded_data:
            validation_results['vn_pb_mappings'] = self._validate_vn_pb_mappings()
        
        # Add other cross-reference validations as needed
        
        return validation_results
    
    def _validate_vn_pb_mappings(self) -> Dict[str, Any]:
        """
        Validate VerbNet-PropBank mappings.
        
        Returns:
            dict: VN-PB mapping validation results
        """
        errors = []
        warnings = []
        
        verbnet_data = self.loaded_data['verbnet']
        propbank_data = self.loaded_data['propbank']
        
        vn_classes = verbnet_data.get('classes', {})
        pb_predicates = propbank_data.get('predicates', {})
        
        # Check for missing cross-references
        # This is a placeholder - actual validation would depend on mapping structure
        
        return self._build_validation_result(errors, warnings, {'status': 'checked'})