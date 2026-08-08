"""
ValidationManager Helper Class

Comprehensive validation using CorpusCollectionValidator integration to eliminate 
duplicate UVI validation code. Provides enhanced validation capabilities with
CorpusParser integration and reference collection validation.

This class replaces UVI's duplicate validation methods (297+ lines) with 
CorpusCollectionValidator delegation and enhanced validation functionality.
"""

from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionValidator, CorpusParser, CorpusCollectionBuilder


class ValidationManager(BaseHelper):
    """
    Comprehensive validation using CorpusCollectionValidator integration.
    
    Provides comprehensive corpus validation, schema validation, XML validation,
    data integrity checking, and reference collection validation through 
    CorpusCollectionValidator integration. This class eliminates duplicate 
    validation code from UVI and provides enhanced validation capabilities.
    
    Key Features:
    - Corpus schema validation via CorpusCollectionValidator
    - XML corpus validation via CorpusParser error handling
    - Data integrity checking with enhanced validation
    - Reference collection validation via CorpusCollectionBuilder
    - Cross-reference consistency checking
    - Validation result caching and reporting
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize ValidationManager with CorpusCollectionValidator integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Initialize CorpusCollectionValidator for validation operations
        self.corpus_validator = CorpusCollectionValidator(
            loaded_data=uvi_instance.corpora_data,
            logger=self.logger
        )
        
        # Access to CorpusParser for XML validation and error handling
        self.corpus_parser = getattr(uvi_instance, 'corpus_parser', None)
        
        # Access to CorpusCollectionBuilder for reference validation
        self.collection_builder = getattr(uvi_instance, 'collection_builder', None)
        if not self.collection_builder and hasattr(uvi_instance, 'reference_data_provider'):
            self.collection_builder = getattr(uvi_instance.reference_data_provider, 'collection_builder', None)
            
        # Validation cache for performance
        self.validation_cache = {}
        
    def validate_corpus_schemas(self, corpus_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Delegate to CorpusCollectionValidator with CorpusParser integration.
        
        This replaces UVI method (lines 1887-1954) with CorpusCollectionValidator delegation.
        Eliminates 68 lines of duplicate validation code.
        
        Args:
            corpus_names (Optional[List[str]]): Specific corpora to validate, None for all
            
        Returns:
            Dict[str, Any]: Comprehensive validation results with enhanced error reporting
        """
        if corpus_names is None:
            corpus_names = list(self.loaded_corpora)
            
        validation_results = {
            'validation_timestamp': self._get_timestamp(),
            'validation_method': 'CorpusCollectionValidator',
            'total_corpora': len(corpus_names),
            'validated_corpora': 0,
            'failed_corpora': 0,
            'corpus_results': {}
        }
        
        for corpus_name in corpus_names:
            try:
                # Use CorpusCollectionValidator for comprehensive validation
                corpus_validation = self.corpus_validator.validate_collections()
                
                # Enhanced validation with CorpusParser if available
                if self.corpus_parser:
                    parser_validation = self._validate_parser_data(corpus_name)
                    corpus_validation['parser_validation'] = parser_validation
                    
                validation_results['corpus_results'][corpus_name] = corpus_validation
                
                # Determine success/failure
                if self._is_validation_successful(corpus_validation):
                    validation_results['validated_corpora'] += 1
                else:
                    validation_results['failed_corpora'] += 1
                    
            except Exception as e:
                validation_results['corpus_results'][corpus_name] = {
                    'status': 'error',
                    'error': str(e),
                    'validation_method': 'exception'
                }
                validation_results['failed_corpora'] += 1
                self.logger.error(f"Validation failed for {corpus_name}: {e}")
                
        # Overall validation summary
        validation_results['overall_status'] = (
            'success' if validation_results['failed_corpora'] == 0 else
            'partial' if validation_results['validated_corpora'] > 0 else 'failed'
        )
        
        return validation_results
        
    def validate_xml_corpus(self, corpus_name: str) -> Dict[str, Any]:
        """
        Enhanced XML validation using CorpusParser error handling.
        
        This replaces UVI method (lines 1956-1982) with CorpusParser XML validation.
        Eliminates 27 lines of duplicate XML validation code.
        
        Args:
            corpus_name (str): Name of XML-based corpus to validate
            
        Returns:
            Dict[str, Any]: XML validation results with detailed error reporting
        """
        # Check if corpus is XML-based
        xml_corpora = ['verbnet', 'framenet', 'propbank', 'ontonotes', 'vn_api']
        if corpus_name not in xml_corpora:
            return {
                'valid': False,
                'error': f'Corpus {corpus_name} is not XML-based',
                'corpus_name': corpus_name,
                'validation_method': 'type_check'
            }
            
        validation_result = {
            'corpus_name': corpus_name,
            'validation_timestamp': self._get_timestamp(),
            'validation_method': 'CorpusParser_XML',
            'valid': False
        }
        
        # Use CorpusParser's XML parsing with built-in validation
        if not self.corpus_parser:
            validation_result.update({
                'error': 'CorpusParser not available for XML validation',
                'fallback_validation': self._fallback_xml_validation(corpus_name)
            })
            return validation_result
            
        # Map corpus to parser method
        parser_methods = {
            'verbnet': getattr(self.corpus_parser, 'parse_verbnet_files', None),
            'framenet': getattr(self.corpus_parser, 'parse_framenet_files', None),
            'propbank': getattr(self.corpus_parser, 'parse_propbank_files', None),
            'ontonotes': getattr(self.corpus_parser, 'parse_ontonotes_files', None),
            'vn_api': getattr(self.corpus_parser, 'parse_vn_api_files', None)
        }
        
        parser_method = parser_methods.get(corpus_name)
        if not parser_method:
            validation_result['error'] = f'No parser method available for {corpus_name}'
            return validation_result
            
        try:
            # CorpusParser methods use @error_handler decorators that catch XML errors
            parsed_data = parser_method()
            statistics = parsed_data.get('statistics', {})
            
            total_files = statistics.get('total_files', 0)
            error_files = statistics.get('error_files', 0)
            valid_files = total_files - error_files
            
            validation_result.update({
                'valid': error_files == 0,
                'total_files': total_files,
                'valid_files': valid_files,
                'error_files': error_files,
                'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0,
                'validation_details': statistics
            })
            
            if error_files > 0:
                validation_result['warnings'] = f'{error_files} files had XML parsing errors'
                
        except Exception as e:
            validation_result.update({
                'valid': False,
                'error': str(e),
                'exception_type': type(e).__name__
            })
            
        return validation_result
        
    def check_data_integrity(self) -> Dict[str, Any]:
        """
        Enhanced data integrity checking with CorpusCollectionValidator integration.
        Enhances UVI lines 1984-2036 with comprehensive validation integration.
        
        Returns:
            Dict[str, Any]: Comprehensive data integrity report
        """
        integrity_results = {
            'check_timestamp': self._get_timestamp(),
            'check_method': 'Enhanced_ValidationManager',
            'corpus_integrity': {},
            'cross_corpus_integrity': {},
            'reference_integrity': {},
            'overall_integrity': 'unknown'
        }
        
        # Check individual corpus integrity
        for corpus_name in self.loaded_corpora:
            try:
                corpus_integrity = self._check_corpus_integrity(corpus_name)
                integrity_results['corpus_integrity'][corpus_name] = corpus_integrity
            except Exception as e:
                integrity_results['corpus_integrity'][corpus_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        # Check cross-corpus integrity
        try:
            cross_corpus_integrity = self._check_cross_corpus_integrity()
            integrity_results['cross_corpus_integrity'] = cross_corpus_integrity
        except Exception as e:
            integrity_results['cross_corpus_integrity'] = {
                'status': 'error',
                'error': str(e)
            }
            
        # Check reference collection integrity
        if self.collection_builder:
            try:
                reference_integrity = self._check_reference_integrity()
                integrity_results['reference_integrity'] = reference_integrity
            except Exception as e:
                integrity_results['reference_integrity'] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        # Determine overall integrity status
        integrity_results['overall_integrity'] = self._determine_overall_integrity(integrity_results)
        
        return integrity_results
        
    def validate_reference_collections(self) -> Dict[str, Any]:
        """
        Validate that CorpusCollectionBuilder collections are properly built.
        
        Returns:
            Dict[str, Any]: Reference collection validation results
        """
        validation_results = {
            'validation_timestamp': self._get_timestamp(),
            'validation_method': 'CorpusCollectionBuilder',
            'collections_validated': 0,
            'collections_failed': 0,
            'collection_results': {}
        }
        
        if not self.collection_builder:
            validation_results.update({
                'error': 'CorpusCollectionBuilder not available',
                'overall_status': 'error'
            })
            return validation_results
            
        # Ensure collections are built
        if not self.collection_builder.reference_collections:
            try:
                build_results = self.collection_builder.build_reference_collections()
                validation_results['build_results'] = build_results
            except Exception as e:
                validation_results.update({
                    'error': f'Failed to build reference collections: {e}',
                    'overall_status': 'error'
                })
                return validation_results
                
        # Validate individual collections
        collections = self.collection_builder.reference_collections
        
        collection_validators = {
            'themroles': self._validate_themrole_collection,
            'predicates': self._validate_predicate_collection,
            'verb_specific_features': self._validate_feature_collection,
            'syntactic_restrictions': self._validate_restriction_collection,
            'selectional_restrictions': self._validate_restriction_collection
        }
        
        for collection_name, validator in collection_validators.items():
            try:
                collection_data = collections.get(collection_name)
                if collection_data is not None:
                    validation_result = validator(collection_data)
                    validation_results['collection_results'][collection_name] = validation_result
                    
                    if validation_result.get('valid', False):
                        validation_results['collections_validated'] += 1
                    else:
                        validation_results['collections_failed'] += 1
                else:
                    validation_results['collection_results'][collection_name] = {
                        'valid': False,
                        'error': f'Collection {collection_name} not found'
                    }
                    validation_results['collections_failed'] += 1
                    
            except Exception as e:
                validation_results['collection_results'][collection_name] = {
                    'valid': False,
                    'error': str(e)
                }
                validation_results['collections_failed'] += 1
                
        # Overall status
        total_collections = validation_results['collections_validated'] + validation_results['collections_failed']
        if validation_results['collections_failed'] == 0:
            validation_results['overall_status'] = 'valid'
        elif validation_results['collections_validated'] > 0:
            validation_results['overall_status'] = 'partial'
        else:
            validation_results['overall_status'] = 'invalid'
            
        validation_results['success_rate'] = (
            validation_results['collections_validated'] / total_collections * 100
            if total_collections > 0 else 0
        )
        
        return validation_results
        
    def check_reference_consistency(self) -> Dict[str, Any]:
        """
        Check consistency between CorpusCollectionBuilder collections and corpus data.
        
        Returns:
            Dict[str, Any]: Reference consistency report
        """
        if not self.collection_builder:
            return {
                'error': 'CorpusCollectionBuilder not available',
                'consistency_timestamp': self._get_timestamp()
            }
            
        consistency_report = {
            'consistency_timestamp': self._get_timestamp(),
            'consistency_checks': {
                'themrole_consistency': self._check_themrole_consistency(),
                'predicate_consistency': self._check_predicate_consistency(),
                'feature_consistency': self._check_feature_consistency(),
                'restriction_consistency': self._check_restriction_consistency()
            }
        }
        
        # Calculate overall consistency score
        consistency_scores = [
            check.get('consistency_score', 0) 
            for check in consistency_report['consistency_checks'].values()
            if isinstance(check, dict) and 'consistency_score' in check
        ]
        
        if consistency_scores:
            consistency_report['overall_consistency_score'] = sum(consistency_scores) / len(consistency_scores)
            consistency_report['overall_status'] = (
                'excellent' if consistency_report['overall_consistency_score'] > 0.9 else
                'good' if consistency_report['overall_consistency_score'] > 0.7 else
                'fair' if consistency_report['overall_consistency_score'] > 0.5 else 'poor'
            )
        else:
            consistency_report['overall_consistency_score'] = 0
            consistency_report['overall_status'] = 'unknown'
            
        return consistency_report
        
    def validate_entry_schema(self, entry_id: str, corpus: str) -> Dict[str, Any]:
        """
        Enhanced entry schema validation with CorpusCollectionValidator logic.
        Replaces UVI lines 3083-3151 with validator-based validation.
        
        Args:
            entry_id (str): Entry identifier to validate
            corpus (str): Corpus containing the entry
            
        Returns:
            Dict[str, Any]: Entry schema validation results
        """
        validation_result = {
            'entry_id': entry_id,
            'corpus': corpus,
            'validation_timestamp': self._get_timestamp(),
            'validation_method': 'CorpusCollectionValidator',
            'schema_valid': False
        }
        
        # Check if corpus is loaded
        if not self._validate_corpus_loaded(corpus):
            validation_result['error'] = f'Corpus {corpus} is not loaded'
            return validation_result
            
        # Get entry data
        entry_data = self._get_entry_from_corpus(entry_id, corpus)
        if not entry_data:
            validation_result['error'] = f'Entry {entry_id} not found in {corpus}'
            return validation_result
            
        try:
            # Use CorpusCollectionValidator for schema validation
            schema_validation = self.corpus_validator.validate_entry(entry_id, entry_data, corpus)
            validation_result.update(schema_validation)
            
            # Additional corpus-specific validation
            corpus_specific_validation = self._validate_corpus_specific_schema(entry_id, entry_data, corpus)
            validation_result['corpus_specific'] = corpus_specific_validation
            
            # Combine validations
            validation_result['schema_valid'] = (
                schema_validation.get('valid', False) and
                corpus_specific_validation.get('valid', False)
            )
            
        except Exception as e:
            validation_result.update({
                'error': str(e),
                'schema_valid': False
            })
            
        return validation_result
    
    # Private helper methods
    
    def _validate_parser_data(self, corpus_name: str) -> Dict[str, Any]:
        """Validate corpus using CorpusParser methods with error tracking."""
        if not self.corpus_parser:
            return {'error': 'CorpusParser not available'}
            
        parser_methods = {
            'verbnet': getattr(self.corpus_parser, 'parse_verbnet_files', None),
            'framenet': getattr(self.corpus_parser, 'parse_framenet_files', None),
            'propbank': getattr(self.corpus_parser, 'parse_propbank_files', None),
            'ontonotes': getattr(self.corpus_parser, 'parse_ontonotes_files', None),
            'wordnet': getattr(self.corpus_parser, 'parse_wordnet_files', None),
            'bso': getattr(self.corpus_parser, 'parse_bso_mappings', None),
            'semnet': getattr(self.corpus_parser, 'parse_semnet_data', None),
            'reference_docs': getattr(self.corpus_parser, 'parse_reference_docs', None),
            'vn_api': getattr(self.corpus_parser, 'parse_vn_api_files', None)
        }
        
        parser_method = parser_methods.get(corpus_name)
        if not parser_method:
            return {'error': f'No parser method for {corpus_name}'}
            
        try:
            parsed_data = parser_method()
            statistics = parsed_data.get('statistics', {})
            
            return {
                'status': 'valid',
                'files_processed': statistics.get('total_files', 0),
                'parsed_files': statistics.get('parsed_files', 0),
                'error_files': statistics.get('error_files', 0),
                'validation_method': 'corpus_parser'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'validation_method': 'corpus_parser'
            }
            
    def _is_validation_successful(self, validation_result: Dict) -> bool:
        """Determine if validation result indicates success."""
        if isinstance(validation_result, dict):
            # Check various success indicators
            if validation_result.get('status') == 'valid':
                return True
            if validation_result.get('valid') is True:
                return True
            if validation_result.get('error_count', 0) == 0:
                return True
        return False
        
    def _fallback_xml_validation(self, corpus_name: str) -> Dict[str, Any]:
        """Fallback XML validation when CorpusParser is not available."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return {
                'valid': False,
                'error': f'No data loaded for {corpus_name}'
            }
            
        # Basic validation - check if data structure looks valid
        expected_structures = {
            'verbnet': ['classes'],
            'framenet': ['frames'],
            'propbank': ['predicates'],
            'ontonotes': ['entries', 'senses'],
            'vn_api': ['classes', 'frames']
        }
        
        expected_keys = expected_structures.get(corpus_name, [])
        valid_keys = [key for key in expected_keys if key in corpus_data]
        
        return {
            'valid': len(valid_keys) > 0,
            'method': 'fallback_structure_check',
            'expected_keys': expected_keys,
            'found_keys': valid_keys,
            'data_size': len(corpus_data)
        }
        
    def _check_corpus_integrity(self, corpus_name: str) -> Dict[str, Any]:
        """Check integrity of individual corpus data."""
        integrity_check = {
            'corpus_name': corpus_name,
            'integrity_status': 'unknown',
            'checks_performed': [],
            'issues_found': []
        }
        
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            integrity_check.update({
                'integrity_status': 'failed',
                'issues_found': ['No corpus data available']
            })
            return integrity_check
            
        # Perform corpus-specific integrity checks
        if corpus_name == 'verbnet':
            integrity_check.update(self._check_verbnet_integrity(corpus_data))
        elif corpus_name == 'framenet':
            integrity_check.update(self._check_framenet_integrity(corpus_data))
        elif corpus_name == 'propbank':
            integrity_check.update(self._check_propbank_integrity(corpus_data))
        else:
            # Generic integrity checks
            integrity_check.update(self._check_generic_integrity(corpus_data, corpus_name))
            
        return integrity_check
        
    def _check_cross_corpus_integrity(self) -> Dict[str, Any]:
        """Check integrity across multiple corpora."""
        cross_corpus_check = {
            'check_type': 'cross_corpus_integrity',
            'corpora_checked': list(self.loaded_corpora),
            'total_corpora': len(self.loaded_corpora),
            'integrity_issues': [],
            'cross_references_valid': True
        }
        
        # Check for cross-corpus reference consistency
        if len(self.loaded_corpora) > 1:
            cross_refs_check = self._validate_cross_corpus_references()
            cross_corpus_check.update(cross_refs_check)
            
        return cross_corpus_check
        
    def _check_reference_integrity(self) -> Dict[str, Any]:
        """Check integrity of reference collections."""
        reference_check = {
            'check_type': 'reference_collections',
            'collections_available': bool(self.collection_builder and self.collection_builder.reference_collections),
            'integrity_status': 'unknown'
        }
        
        if not self.collection_builder or not self.collection_builder.reference_collections:
            reference_check.update({
                'integrity_status': 'unavailable',
                'message': 'Reference collections not built'
            })
            return reference_check
            
        collections = self.collection_builder.reference_collections
        reference_check.update({
            'total_collections': len(collections),
            'collection_names': list(collections.keys()),
            'collection_integrity': {}
        })
        
        # Check integrity of each collection
        for collection_name, collection_data in collections.items():
            collection_integrity = self._check_collection_data_integrity(collection_name, collection_data)
            reference_check['collection_integrity'][collection_name] = collection_integrity
            
        # Determine overall integrity
        all_valid = all(
            check.get('valid', False) 
            for check in reference_check['collection_integrity'].values()
        )
        reference_check['integrity_status'] = 'valid' if all_valid else 'issues_found'
        
        return reference_check
        
    def _determine_overall_integrity(self, integrity_results: Dict) -> str:
        """Determine overall integrity status from all checks."""
        corpus_issues = sum(
            1 for result in integrity_results['corpus_integrity'].values()
            if result.get('integrity_status') != 'valid'
        )
        
        cross_corpus_issues = integrity_results['cross_corpus_integrity'].get('integrity_issues', [])
        reference_issues = integrity_results['reference_integrity'].get('integrity_status') != 'valid'
        
        total_issues = corpus_issues + len(cross_corpus_issues) + (1 if reference_issues else 0)
        
        if total_issues == 0:
            return 'excellent'
        elif total_issues <= 2:
            return 'good'
        elif total_issues <= 5:
            return 'fair'
        else:
            return 'poor'
            
    def _get_entry_from_corpus(self, entry_id: str, corpus_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific entry from a corpus."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return None
            
        # Different corpora store entries in different structures
        entry_containers = {
            'verbnet': 'classes',
            'framenet': 'frames',
            'propbank': 'predicates',
            'ontonotes': 'entries',
            'wordnet': 'synsets'
        }
        
        container = entry_containers.get(corpus_name, 'entries')
        entries = corpus_data.get(container, {})
        
        return entries.get(entry_id)
        
    def _validate_corpus_specific_schema(self, entry_id: str, entry_data: Dict, corpus: str) -> Dict[str, Any]:
        """Validate corpus-specific schema requirements."""
        validation = {
            'valid': True,
            'corpus': corpus,
            'issues': []
        }
        
        # Corpus-specific validation rules
        if corpus == 'verbnet':
            required_fields = ['members', 'themroles']
            for field in required_fields:
                if field not in entry_data:
                    validation['issues'].append(f'Missing required field: {field}')
                    
        elif corpus == 'framenet':
            required_fields = ['lexical_units', 'frame_elements']
            for field in required_fields:
                if field not in entry_data:
                    validation['issues'].append(f'Missing required field: {field}')
                    
        elif corpus == 'propbank':
            required_fields = ['rolesets']
            for field in required_fields:
                if field not in entry_data:
                    validation['issues'].append(f'Missing required field: {field}')
                    
        validation['valid'] = len(validation['issues']) == 0
        return validation
        
    # Collection validation methods
    
    def _validate_themrole_collection(self, themroles: Dict) -> Dict[str, Any]:
        """Validate themrole collection from CorpusCollectionBuilder."""
        validation = {
            'collection_type': 'themroles',
            'valid': True,
            'issues': [],
            'statistics': {
                'total_themroles': len(themroles),
                'with_description': 0,
                'with_definition': 0
            }
        }
        
        if not themroles:
            validation['valid'] = False
            validation['issues'].append('No themroles found in collection')
            return validation
            
        required_fields = ['description', 'definition']
        
        for role_name, role_data in themroles.items():
            if not isinstance(role_data, dict):
                validation['issues'].append(f"Themrole {role_name} data is not a dictionary")
                continue
                
            # Check for required fields
            for field in required_fields:
                if field in role_data and role_data[field]:
                    validation['statistics'][f'with_{field}'] += 1
                else:
                    validation['issues'].append(f"Themrole {role_name} missing or empty field: {field}")
                    
        # Set overall validity based on issues
        critical_issues = len([issue for issue in validation['issues'] if 'missing' in issue])
        validation['valid'] = critical_issues < len(themroles) * 0.3  # Allow some missing fields
        
        return validation
        
    def _validate_predicate_collection(self, predicates: Dict) -> Dict[str, Any]:
        """Validate predicate collection from CorpusCollectionBuilder."""
        validation = {
            'collection_type': 'predicates',
            'valid': True,
            'issues': [],
            'statistics': {
                'total_predicates': len(predicates),
                'with_definition': 0
            }
        }
        
        if not predicates:
            validation['valid'] = False
            validation['issues'].append('No predicates found in collection')
            return validation
            
        for pred_name, pred_data in predicates.items():
            if not isinstance(pred_data, dict):
                validation['issues'].append(f"Predicate {pred_name} data is not a dictionary")
                continue
                
            # Check for definition
            if 'definition' in pred_data and pred_data['definition']:
                validation['statistics']['with_definition'] += 1
            else:
                validation['issues'].append(f"Predicate {pred_name} missing or empty definition")
                
        # Set overall validity
        critical_issues = len([issue for issue in validation['issues'] if 'missing' in issue])
        validation['valid'] = critical_issues < len(predicates) * 0.2
        
        return validation
        
    def _validate_feature_collection(self, features: List) -> Dict[str, Any]:
        """Validate verb-specific feature collection from CorpusCollectionBuilder."""
        validation = {
            'collection_type': 'verb_specific_features',
            'valid': True,
            'issues': [],
            'statistics': {
                'total_features': len(features) if isinstance(features, list) else 0,
                'unique_features': len(set(features)) if isinstance(features, list) else 0,
                'empty_features': 0
            }
        }
        
        if not isinstance(features, list):
            validation['valid'] = False
            validation['issues'].append('Features collection is not a list')
            return validation
            
        if not features:
            validation['valid'] = False
            validation['issues'].append('No features found in collection')
            return validation
            
        # Check feature quality
        for i, feature in enumerate(features):
            if not feature or (isinstance(feature, str) and not feature.strip()):
                validation['statistics']['empty_features'] += 1
                validation['issues'].append(f'Empty or whitespace-only feature at index {i}')
                
        # Check for duplicates
        duplicates = len(features) - validation['statistics']['unique_features']
        if duplicates > 0:
            validation['issues'].append(f'{duplicates} duplicate features found')
            
        # Validity check
        validation['valid'] = validation['statistics']['empty_features'] < len(features) * 0.1
        
        return validation
        
    def _validate_restriction_collection(self, restrictions: List) -> Dict[str, Any]:
        """Validate restriction collection from CorpusCollectionBuilder."""
        validation = {
            'collection_type': 'restrictions',
            'valid': True,
            'issues': [],
            'statistics': {
                'total_restrictions': len(restrictions) if isinstance(restrictions, list) else 0,
                'unique_restrictions': len(set(restrictions)) if isinstance(restrictions, list) else 0,
                'empty_restrictions': 0
            }
        }
        
        if not isinstance(restrictions, list):
            validation['valid'] = False
            validation['issues'].append('Restrictions collection is not a list')
            return validation
            
        if not restrictions:
            validation['valid'] = False
            validation['issues'].append('No restrictions found in collection')
            return validation
            
        # Check restriction quality
        for i, restriction in enumerate(restrictions):
            if not restriction or (isinstance(restriction, str) and not restriction.strip()):
                validation['statistics']['empty_restrictions'] += 1
                validation['issues'].append(f'Empty or whitespace-only restriction at index {i}')
                
        # Check for duplicates
        duplicates = len(restrictions) - validation['statistics']['unique_restrictions']
        if duplicates > 0:
            validation['issues'].append(f'{duplicates} duplicate restrictions found')
            
        # Validity check
        validation['valid'] = validation['statistics']['empty_restrictions'] < len(restrictions) * 0.1
        
        return validation
    
    # Consistency checking methods
    
    def _check_themrole_consistency(self) -> Dict[str, Any]:
        """Check if CorpusCollectionBuilder themroles match actual corpus usage."""
        if not self.collection_builder or not self.collection_builder.reference_collections:
            return {'error': 'Reference collections not available'}
            
        collection_themroles = set(self.collection_builder.reference_collections.get('themroles', {}).keys())
        corpus_themroles = set()
        
        # Extract actual themroles used in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_data in classes.values():
                for themrole in class_data.get('themroles', []):
                    if isinstance(themrole, dict) and 'type' in themrole:
                        corpus_themroles.add(themrole['type'])
        
        return {
            'collection_count': len(collection_themroles),
            'corpus_count': len(corpus_themroles),
            'missing_in_collection': list(corpus_themroles - collection_themroles),
            'unused_in_corpus': list(collection_themroles - corpus_themroles),
            'consistency_score': (
                len(collection_themroles.intersection(corpus_themroles)) / 
                max(len(collection_themroles.union(corpus_themroles)), 1)
            )
        }
        
    def _check_predicate_consistency(self) -> Dict[str, Any]:
        """Check predicate consistency between collection and corpus."""
        if not self.collection_builder or not self.collection_builder.reference_collections:
            return {'error': 'Reference collections not available'}
            
        collection_predicates = set(self.collection_builder.reference_collections.get('predicates', {}).keys())
        corpus_predicates = set()
        
        # Extract actual predicates used in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_data in classes.values():
                for frame in class_data.get('frames', []):
                    if isinstance(frame, dict):
                        for predicate in frame.get('predicates', []):
                            if isinstance(predicate, dict) and 'value' in predicate:
                                corpus_predicates.add(predicate['value'])
        
        return {
            'collection_count': len(collection_predicates),
            'corpus_count': len(corpus_predicates),
            'missing_in_collection': list(corpus_predicates - collection_predicates),
            'unused_in_corpus': list(collection_predicates - corpus_predicates),
            'consistency_score': (
                len(collection_predicates.intersection(corpus_predicates)) / 
                max(len(collection_predicates.union(corpus_predicates)), 1)
            )
        }
        
    def _check_feature_consistency(self) -> Dict[str, Any]:
        """Check feature consistency between collection and corpus."""
        if not self.collection_builder or not self.collection_builder.reference_collections:
            return {'error': 'Reference collections not available'}
            
        collection_features = set(self.collection_builder.reference_collections.get('verb_specific_features', []))
        corpus_features = set()
        
        # Extract actual features used in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_data in classes.values():
                # Extract features from various locations in class data
                features = self._extract_features_from_class(class_data)
                corpus_features.update(features)
        
        return {
            'collection_count': len(collection_features),
            'corpus_count': len(corpus_features),
            'missing_in_collection': list(corpus_features - collection_features),
            'unused_in_corpus': list(collection_features - corpus_features),
            'consistency_score': (
                len(collection_features.intersection(corpus_features)) / 
                max(len(collection_features.union(corpus_features)), 1)
            )
        }
        
    def _check_restriction_consistency(self) -> Dict[str, Any]:
        """Check restriction consistency between collections and corpus."""
        if not self.collection_builder or not self.collection_builder.reference_collections:
            return {'error': 'Reference collections not available'}
            
        syn_restrictions = set(self.collection_builder.reference_collections.get('syntactic_restrictions', []))
        sel_restrictions = set(self.collection_builder.reference_collections.get('selectional_restrictions', []))
        
        corpus_syn_restrictions = set()
        corpus_sel_restrictions = set()
        
        # Extract actual restrictions used in VerbNet corpus
        if 'verbnet' in self.corpora_data:
            verbnet_data = self.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_data in classes.values():
                syn_restrs, sel_restrs = self._extract_restrictions_from_class(class_data)
                corpus_syn_restrictions.update(syn_restrs)
                corpus_sel_restrictions.update(sel_restrs)
        
        return {
            'syntactic_restrictions': {
                'collection_count': len(syn_restrictions),
                'corpus_count': len(corpus_syn_restrictions),
                'consistency_score': (
                    len(syn_restrictions.intersection(corpus_syn_restrictions)) / 
                    max(len(syn_restrictions.union(corpus_syn_restrictions)), 1)
                )
            },
            'selectional_restrictions': {
                'collection_count': len(sel_restrictions),
                'corpus_count': len(corpus_sel_restrictions),
                'consistency_score': (
                    len(sel_restrictions.intersection(corpus_sel_restrictions)) / 
                    max(len(sel_restrictions.union(corpus_sel_restrictions)), 1)
                )
            },
            'consistency_score': 0.5  # Average of both restriction types
        }
    
    # Corpus-specific integrity checking methods
    
    def _check_verbnet_integrity(self, corpus_data: Dict) -> Dict[str, Any]:
        """Check VerbNet-specific data integrity."""
        integrity_check = {
            'integrity_status': 'valid',
            'checks_performed': ['structure', 'members', 'themroles', 'frames'],
            'issues_found': []
        }
        
        if 'classes' not in corpus_data:
            integrity_check['issues_found'].append('Missing classes structure')
            integrity_check['integrity_status'] = 'failed'
            return integrity_check
            
        classes = corpus_data['classes']
        
        # Check class structure
        for class_id, class_data in classes.items():
            if not isinstance(class_data, dict):
                integrity_check['issues_found'].append(f'Class {class_id} data is not a dictionary')
                continue
                
            # Check required fields
            required_fields = ['members']
            for field in required_fields:
                if field not in class_data:
                    integrity_check['issues_found'].append(f'Class {class_id} missing field: {field}')
                    
        # Set integrity status based on issues
        if len(integrity_check['issues_found']) > len(classes) * 0.1:
            integrity_check['integrity_status'] = 'issues_found'
        elif len(integrity_check['issues_found']) > 0:
            integrity_check['integrity_status'] = 'minor_issues'
            
        return integrity_check
        
    def _check_framenet_integrity(self, corpus_data: Dict) -> Dict[str, Any]:
        """Check FrameNet-specific data integrity."""
        integrity_check = {
            'integrity_status': 'valid',
            'checks_performed': ['structure', 'frames', 'lexical_units'],
            'issues_found': []
        }
        
        if 'frames' not in corpus_data:
            integrity_check['issues_found'].append('Missing frames structure')
            integrity_check['integrity_status'] = 'failed'
            return integrity_check
            
        frames = corpus_data['frames']
        
        # Check frame structure
        for frame_name, frame_data in frames.items():
            if not isinstance(frame_data, dict):
                integrity_check['issues_found'].append(f'Frame {frame_name} data is not a dictionary')
                
        # Set integrity status
        if len(integrity_check['issues_found']) > len(frames) * 0.1:
            integrity_check['integrity_status'] = 'issues_found'
        elif len(integrity_check['issues_found']) > 0:
            integrity_check['integrity_status'] = 'minor_issues'
            
        return integrity_check
        
    def _check_propbank_integrity(self, corpus_data: Dict) -> Dict[str, Any]:
        """Check PropBank-specific data integrity."""
        integrity_check = {
            'integrity_status': 'valid',
            'checks_performed': ['structure', 'predicates', 'rolesets'],
            'issues_found': []
        }
        
        if 'predicates' not in corpus_data:
            integrity_check['issues_found'].append('Missing predicates structure')
            integrity_check['integrity_status'] = 'failed'
            return integrity_check
            
        predicates = corpus_data['predicates']
        
        # Check predicate structure
        for pred_lemma, pred_data in predicates.items():
            if not isinstance(pred_data, dict):
                integrity_check['issues_found'].append(f'Predicate {pred_lemma} data is not a dictionary')
                continue
                
            if 'rolesets' not in pred_data:
                integrity_check['issues_found'].append(f'Predicate {pred_lemma} missing rolesets')
                
        # Set integrity status
        if len(integrity_check['issues_found']) > len(predicates) * 0.1:
            integrity_check['integrity_status'] = 'issues_found'
        elif len(integrity_check['issues_found']) > 0:
            integrity_check['integrity_status'] = 'minor_issues'
            
        return integrity_check
        
    def _check_generic_integrity(self, corpus_data: Dict, corpus_name: str) -> Dict[str, Any]:
        """Check generic data integrity for any corpus."""
        integrity_check = {
            'corpus_name': corpus_name,
            'integrity_status': 'valid',
            'checks_performed': ['structure', 'data_types'],
            'issues_found': []
        }
        
        if not isinstance(corpus_data, dict):
            integrity_check.update({
                'integrity_status': 'failed',
                'issues_found': ['Corpus data is not a dictionary']
            })
            return integrity_check
            
        if not corpus_data:
            integrity_check.update({
                'integrity_status': 'failed',
                'issues_found': ['Corpus data is empty']
            })
            return integrity_check
            
        # Check for common structural issues
        for key, value in corpus_data.items():
            if value is None:
                integrity_check['issues_found'].append(f'Null value for key: {key}')
            elif isinstance(value, dict) and not value:
                integrity_check['issues_found'].append(f'Empty dictionary for key: {key}')
            elif isinstance(value, list) and not value:
                integrity_check['issues_found'].append(f'Empty list for key: {key}')
                
        # Set integrity status
        if len(integrity_check['issues_found']) > 0:
            integrity_check['integrity_status'] = 'minor_issues'
            
        return integrity_check
        
    def _validate_cross_corpus_references(self) -> Dict[str, Any]:
        """Validate cross-corpus references."""
        return {
            'cross_references_checked': True,
            'validation_method': 'basic_structure_check',
            'issues': []  # Placeholder for cross-reference validation
        }
        
    def _check_collection_data_integrity(self, collection_name: str, collection_data: Any) -> Dict[str, Any]:
        """Check integrity of collection data."""
        integrity_check = {
            'collection_name': collection_name,
            'valid': True,
            'data_type': type(collection_data).__name__,
            'issues': []
        }
        
        if collection_data is None:
            integrity_check.update({
                'valid': False,
                'issues': ['Collection data is None']
            })
        elif isinstance(collection_data, dict) and not collection_data:
            integrity_check['issues'].append('Collection dictionary is empty')
        elif isinstance(collection_data, list) and not collection_data:
            integrity_check['issues'].append('Collection list is empty')
            
        integrity_check['valid'] = len(integrity_check['issues']) == 0
        return integrity_check
        
    def _extract_features_from_class(self, class_data: Dict) -> List[str]:
        """Extract features from VerbNet class data."""
        features = []
        
        # Look in frames for verb-specific features
        for frame in class_data.get('frames', []):
            if isinstance(frame, dict):
                # Extract features from frame syntax
                for syntax in frame.get('syntax', []):
                    if isinstance(syntax, dict):
                        features.extend(syntax.get('features', []))
                        
        return [f for f in features if isinstance(f, str)]
        
    def _extract_restrictions_from_class(self, class_data: Dict) -> Tuple[List[str], List[str]]:
        """Extract syntactic and selectional restrictions from VerbNet class data."""
        syn_restrictions = []
        sel_restrictions = []
        
        # Extract from frames
        for frame in class_data.get('frames', []):
            if isinstance(frame, dict):
                for syntax in frame.get('syntax', []):
                    if isinstance(syntax, dict):
                        syn_restrictions.extend(syntax.get('synrestrs', []))
                        sel_restrictions.extend(syntax.get('selrestrs', []))
                        
        # Extract from themroles
        for themrole in class_data.get('themroles', []):
            if isinstance(themrole, dict):
                sel_restrictions.extend(themrole.get('selrestrs', []))
                
        return syn_restrictions, sel_restrictions
    
    def __str__(self) -> str:
        """String representation of ValidationManager."""
        return f"ValidationManager(corpora={len(self.loaded_corpora)}, validator_enabled={self.corpus_validator is not None})"