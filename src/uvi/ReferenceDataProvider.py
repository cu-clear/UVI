"""
ReferenceDataProvider Helper Class

Reference data and field information access using CorpusCollectionBuilder integration.
Eliminates duplicate reference collection building code from UVI by delegating to 
CorpusCollectionBuilder for centralized, optimized collection building.

This class replaces UVI's duplicate reference building methods (lines 1459-1762) 
with CorpusCollectionBuilder delegation, eliminating 167+ lines of duplicate code.
"""

from typing import Dict, List, Optional, Union, Any, Set
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionBuilder


class ReferenceDataProvider(BaseHelper):
    """
    Reference data and field information access using CorpusCollectionBuilder integration.
    
    Provides comprehensive reference data access through CorpusCollectionBuilder delegation,
    eliminating duplicate collection building code from UVI. This class centralizes and
    optimizes reference collection building via CorpusCollectionBuilder's template methods.
    
    Key Features:
    - Themrole references via CorpusCollectionBuilder
    - Predicate references via CorpusCollectionBuilder  
    - Verb-specific feature lists via CorpusCollectionBuilder
    - Syntactic restriction lists via CorpusCollectionBuilder
    - Selectional restriction lists via CorpusCollectionBuilder
    - Field information access for themroles, predicates, constants
    - Centralized reference metadata management
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize ReferenceDataProvider with CorpusCollectionBuilder integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Initialize CorpusCollectionBuilder for reference data building
        self.collection_builder = CorpusCollectionBuilder(
            loaded_data=uvi_instance.corpora_data,
            logger=self.logger
        )
        
        # Cache for built collections to avoid rebuilding
        self._collections_cache = {}
        self._cache_timestamp = None
        
    def get_references(self) -> Dict[str, Any]:
        """
        Delegate to CorpusCollectionBuilder instead of duplicate logic.
        
        This replaces UVI method (lines 1459-1500) with CorpusCollectionBuilder delegation.
        Eliminates 42 lines of manual reference building code.
        
        Returns:
            Dict[str, Any]: All reference data collections with metadata
        """
        # Ensure reference collections are built via CorpusCollectionBuilder
        if not self.collection_builder.reference_collections:
            build_results = self.collection_builder.build_reference_collections()
            self.logger.info(f"Built reference collections: {list(build_results.keys())}")
        
        return {
            'gen_themroles': self.get_themrole_references(),
            'predicates': self.get_predicate_references(),  
            'vs_features': self.get_verb_specific_features(),
            'syn_res': self.get_syntactic_restrictions(),
            'sel_res': self.get_selectional_restrictions(),
            'metadata': {
                'total_collections': 5,
                'generated_at': self._get_timestamp(),
                'collection_builder_version': '1.0',
                'source': 'CorpusCollectionBuilder'
            }
        }
        
    def get_themrole_references(self) -> List[Dict[str, Any]]:
        """
        Use CorpusCollectionBuilder's built reference collections.
        
        This replaces UVI method (lines 1502-1563) with CorpusCollectionBuilder delegation.
        Eliminates 62 lines of manual VerbNet corpus extraction logic.
        
        Returns:
            List[Dict[str, Any]]: Themrole reference data from CorpusCollectionBuilder
        """
        self._ensure_references_built()
        
        themroles = self.collection_builder.reference_collections.get('themroles', {})
        
        # Format themroles for compatibility with UVI interface
        formatted_themroles = []
        for name, data in themroles.items():
            formatted_role = {
                'name': name,
                'type': 'themrole',
                'source': 'CorpusCollectionBuilder'
            }
            
            # Add data fields if they exist
            if isinstance(data, dict):
                formatted_role.update(data)
            elif isinstance(data, str):
                formatted_role['description'] = data
                
            formatted_themroles.append(formatted_role)
            
        return formatted_themroles
        
    def get_predicate_references(self) -> List[Dict[str, Any]]:
        """
        Use CorpusCollectionBuilder's built reference collections.
        
        This replaces UVI method (lines 1565-1626) with CorpusCollectionBuilder delegation.
        Eliminates 62 lines of manual VerbNet corpus extraction logic.
        
        Returns:
            List[Dict[str, Any]]: Predicate reference data from CorpusCollectionBuilder
        """
        self._ensure_references_built()
        
        predicates = self.collection_builder.reference_collections.get('predicates', {})
        
        # Format predicates for compatibility with UVI interface
        formatted_predicates = []
        for name, data in predicates.items():
            formatted_predicate = {
                'name': name,
                'type': 'predicate',
                'source': 'CorpusCollectionBuilder'
            }
            
            # Add data fields if they exist
            if isinstance(data, dict):
                formatted_predicate.update(data)
            elif isinstance(data, str):
                formatted_predicate['definition'] = data
                
            formatted_predicates.append(formatted_predicate)
            
        return formatted_predicates
        
    def get_verb_specific_features(self) -> List[str]:
        """
        Use CorpusCollectionBuilder's extracted features.
        
        This replaces UVI method (lines 1628-1662) with CorpusCollectionBuilder delegation.
        Eliminates 35 lines of manual VerbNet class iteration and feature extraction logic.
        
        Returns:
            List[str]: Verb-specific feature list from CorpusCollectionBuilder
        """
        self._ensure_references_built()
        
        features = self.collection_builder.reference_collections.get('verb_specific_features', [])
        
        # Ensure features are strings and deduplicated
        if isinstance(features, list):
            return sorted(list(set(str(f) for f in features if f)))
        else:
            self.logger.warning("Verb-specific features not found or invalid format")
            return []
        
    def get_syntactic_restrictions(self) -> List[str]:
        """
        Use CorpusCollectionBuilder's extracted restrictions.
        
        This replaces UVI method (lines 1664-1704) with CorpusCollectionBuilder delegation.
        Eliminates 41 lines of manual VerbNet frame iteration and synrestrs extraction logic.
        
        Returns:
            List[str]: Syntactic restriction list from CorpusCollectionBuilder
        """
        self._ensure_references_built()
        
        restrictions = self.collection_builder.reference_collections.get('syntactic_restrictions', [])
        
        # Ensure restrictions are strings and deduplicated
        if isinstance(restrictions, list):
            return sorted(list(set(str(r) for r in restrictions if r)))
        else:
            self.logger.warning("Syntactic restrictions not found or invalid format")
            return []
        
    def get_selectional_restrictions(self) -> List[str]:
        """
        Use CorpusCollectionBuilder's extracted restrictions.
        
        This replaces UVI method (lines 1706-1762) with CorpusCollectionBuilder delegation.
        Eliminates 57 lines of manual VerbNet frame iteration and selrestrs extraction logic.
        
        Returns:
            List[str]: Selectional restriction list from CorpusCollectionBuilder
        """
        self._ensure_references_built()
        
        restrictions = self.collection_builder.reference_collections.get('selectional_restrictions', [])
        
        # Ensure restrictions are strings and deduplicated
        if isinstance(restrictions, list):
            return sorted(list(set(str(r) for r in restrictions if r)))
        else:
            self.logger.warning("Selectional restrictions not found or invalid format")
            return []
            
    def get_themrole_fields(self, class_id: str, frame_desc_primary: Optional[str] = None, 
                           syntax_num: Optional[int] = None) -> Dict[str, Any]:
        """
        Get thematic role field information for a specific VerbNet class.
        
        Args:
            class_id (str): VerbNet class identifier
            frame_desc_primary (Optional[str]): Frame description primary
            syntax_num (Optional[int]): Syntax number
            
        Returns:
            Dict[str, Any]: Thematic role field information
        """
        # Get VerbNet class data
        verbnet_data = self._get_corpus_data('verbnet')
        if not verbnet_data or 'classes' not in verbnet_data:
            return {}
            
        classes = verbnet_data['classes']
        if class_id not in classes:
            return {}
            
        class_data = classes[class_id]
        themroles = class_data.get('themroles', [])
        
        # Build themrole field information
        themrole_fields = {
            'class_id': class_id,
            'total_themroles': len(themroles),
            'themroles': []
        }
        
        # Get reference themrole data for enrichment
        self._ensure_references_built()
        ref_themroles = self.collection_builder.reference_collections.get('themroles', {})
        
        for role in themroles:
            if isinstance(role, dict):
                role_info = role.copy()
                
                # Enrich with reference data if available
                role_type = role.get('type', '')
                if role_type in ref_themroles:
                    role_info['reference_data'] = ref_themroles[role_type]
                    
                themrole_fields['themroles'].append(role_info)
                
        return themrole_fields
        
    def get_predicate_fields(self, pred_name: str) -> Dict[str, Any]:
        """
        Get predicate field information for a specific predicate.
        
        Args:
            pred_name (str): Predicate name
            
        Returns:
            Dict[str, Any]: Predicate field information
        """
        self._ensure_references_built()
        ref_predicates = self.collection_builder.reference_collections.get('predicates', {})
        
        if pred_name in ref_predicates:
            pred_data = ref_predicates[pred_name]
            
            return {
                'predicate_name': pred_name,
                'reference_data': pred_data,
                'field_type': 'predicate',
                'source': 'CorpusCollectionBuilder'
            }
        else:
            return {
                'predicate_name': pred_name,
                'found': False,
                'message': 'Predicate not found in reference collections'
            }
            
    def get_constant_fields(self, constant_name: str) -> Dict[str, Any]:
        """
        Get constant field information for a specific constant.
        
        Args:
            constant_name (str): Constant name
            
        Returns:
            Dict[str, Any]: Constant field information
        """
        # Constants are typically found in reference docs or as part of predicate definitions
        constant_info = {
            'constant_name': constant_name,
            'field_type': 'constant',
            'found_in': []
        }
        
        # Search in reference data
        self._ensure_references_built()
        collections = self.collection_builder.reference_collections
        
        # Check in predicates
        predicates = collections.get('predicates', {})
        for pred_name, pred_data in predicates.items():
            if self._constant_in_data(constant_name, pred_data):
                constant_info['found_in'].append({
                    'collection': 'predicates',
                    'item': pred_name,
                    'data': pred_data
                })
                
        # Check in themroles
        themroles = collections.get('themroles', {})
        for role_name, role_data in themroles.items():
            if self._constant_in_data(constant_name, role_data):
                constant_info['found_in'].append({
                    'collection': 'themroles',
                    'item': role_name,
                    'data': role_data
                })
                
        constant_info['total_occurrences'] = len(constant_info['found_in'])
        constant_info['found'] = constant_info['total_occurrences'] > 0
        
        return constant_info
        
    def get_verb_specific_fields(self, feature_name: str) -> Dict[str, Any]:
        """
        Get verb-specific field information for a specific feature.
        
        Args:
            feature_name (str): Verb-specific feature name
            
        Returns:
            Dict[str, Any]: Verb-specific field information
        """
        features = self.get_verb_specific_features()
        
        feature_info = {
            'feature_name': feature_name,
            'field_type': 'verb_specific_feature',
            'found': feature_name in features,
            'total_features': len(features)
        }
        
        if feature_info['found']:
            # Find usage in VerbNet classes
            usage_info = self._find_feature_usage(feature_name)
            feature_info.update(usage_info)
            
        return feature_info
        
    def get_reference_collection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about reference collections from CorpusCollectionBuilder.
        
        Returns:
            Dict[str, Any]: Reference collection statistics
        """
        self._ensure_references_built()
        collections = self.collection_builder.reference_collections
        
        stats = {
            'collection_timestamp': self._get_timestamp(),
            'total_collections': len(collections),
            'collections': {}
        }
        
        for collection_name, collection_data in collections.items():
            if isinstance(collection_data, dict):
                stats['collections'][collection_name] = {
                    'type': 'dictionary',
                    'total_items': len(collection_data),
                    'sample_keys': list(collection_data.keys())[:5]
                }
            elif isinstance(collection_data, list):
                stats['collections'][collection_name] = {
                    'type': 'list',
                    'total_items': len(collection_data),
                    'sample_items': collection_data[:5]
                }
            else:
                stats['collections'][collection_name] = {
                    'type': type(collection_data).__name__,
                    'value': str(collection_data)[:100]
                }
                
        return stats
        
    def rebuild_reference_collections(self, force: bool = False) -> Dict[str, Any]:
        """
        Rebuild reference collections using CorpusCollectionBuilder.
        
        Args:
            force (bool): Force rebuild even if collections exist
            
        Returns:
            Dict[str, Any]: Rebuild results
        """
        if force or not self.collection_builder.reference_collections:
            try:
                build_results = self.collection_builder.build_reference_collections()
                
                # Clear cache to force refresh
                self._collections_cache = {}
                self._cache_timestamp = None
                
                return {
                    'rebuild_successful': True,
                    'rebuild_timestamp': self._get_timestamp(),
                    'build_results': build_results,
                    'collections_built': list(self.collection_builder.reference_collections.keys())
                }
                
            except Exception as e:
                self.logger.error(f"Failed to rebuild reference collections: {e}")
                return {
                    'rebuild_successful': False,
                    'error': str(e),
                    'rebuild_timestamp': self._get_timestamp()
                }
        else:
            return {
                'rebuild_successful': False,
                'message': 'Collections already exist, use force=True to rebuild',
                'existing_collections': list(self.collection_builder.reference_collections.keys())
            }
            
    def validate_reference_collections(self) -> Dict[str, Any]:
        """
        Validate reference collections using CorpusCollectionBuilder built data.
        
        Returns:
            Dict[str, Any]: Validation results for reference collections
        """
        self._ensure_references_built()
        collections = self.collection_builder.reference_collections
        
        validation_results = {
            'validation_timestamp': self._get_timestamp(),
            'total_collections': len(collections),
            'validation_results': {}
        }
        
        # Validate each collection
        for collection_name, collection_data in collections.items():
            collection_validation = {
                'collection_name': collection_name,
                'valid': True,
                'issues': [],
                'statistics': {}
            }
            
            if collection_name == 'themroles':
                collection_validation.update(self._validate_themrole_collection(collection_data))
            elif collection_name == 'predicates':
                collection_validation.update(self._validate_predicate_collection(collection_data))
            elif collection_name == 'verb_specific_features':
                collection_validation.update(self._validate_feature_collection(collection_data))
            elif collection_name in ['syntactic_restrictions', 'selectional_restrictions']:
                collection_validation.update(self._validate_restriction_collection(collection_data))
                
            validation_results['validation_results'][collection_name] = collection_validation
            
        # Overall validation status
        all_valid = all(
            result.get('valid', False) 
            for result in validation_results['validation_results'].values()
        )
        
        validation_results['overall_valid'] = all_valid
        validation_results['total_issues'] = sum(
            len(result.get('issues', [])) 
            for result in validation_results['validation_results'].values()
        )
        
        return validation_results
    
    # Private helper methods
    
    def _ensure_references_built(self):
        """Ensure CorpusCollectionBuilder reference collections are built."""
        if not self.collection_builder.reference_collections:
            try:
                self.collection_builder.build_reference_collections()
                self.logger.info("Reference collections built successfully")
            except Exception as e:
                self.logger.error(f"Failed to build reference collections: {e}")
                raise
                
    def _constant_in_data(self, constant_name: str, data: Any) -> bool:
        """Check if a constant appears in data structure."""
        constant_lower = constant_name.lower()
        
        if isinstance(data, str):
            return constant_lower in data.lower()
        elif isinstance(data, dict):
            return any(
                constant_lower in str(v).lower() 
                for v in data.values() 
                if isinstance(v, (str, int, float))
            )
        elif isinstance(data, list):
            return any(
                constant_lower in str(item).lower() 
                for item in data 
                if isinstance(item, (str, int, float))
            )
        
        return False
        
    def _find_feature_usage(self, feature_name: str) -> Dict[str, Any]:
        """Find usage of a verb-specific feature in VerbNet classes."""
        usage_info = {
            'usage_count': 0,
            'used_in_classes': [],
            'usage_contexts': []
        }
        
        verbnet_data = self._get_corpus_data('verbnet')
        if not verbnet_data or 'classes' not in verbnet_data:
            return usage_info
            
        classes = verbnet_data['classes']
        feature_lower = feature_name.lower()
        
        for class_id, class_data in classes.items():
            if self._feature_in_class(feature_lower, class_data):
                usage_info['usage_count'] += 1
                usage_info['used_in_classes'].append(class_id)
                
                # Extract context information
                context = self._extract_feature_context(feature_lower, class_data, class_id)
                if context:
                    usage_info['usage_contexts'].append(context)
                    
        return usage_info
        
    def _feature_in_class(self, feature_name: str, class_data: Dict) -> bool:
        """Check if a feature is used in a VerbNet class."""
        # Check in various places where features might appear
        search_areas = ['frames', 'themroles', 'members']
        
        for area in search_areas:
            if area in class_data:
                area_data = class_data[area]
                if self._search_in_structure(feature_name, area_data):
                    return True
                    
        return False
        
    def _search_in_structure(self, search_term: str, structure: Any) -> bool:
        """Recursively search for a term in a data structure."""
        if isinstance(structure, str):
            return search_term in structure.lower()
        elif isinstance(structure, dict):
            return any(
                self._search_in_structure(search_term, v) 
                for v in structure.values()
            )
        elif isinstance(structure, list):
            return any(
                self._search_in_structure(search_term, item) 
                for item in structure
            )
        
        return False
        
    def _extract_feature_context(self, feature_name: str, class_data: Dict, class_id: str) -> Dict[str, Any]:
        """Extract context information for feature usage in a class."""
        context = {
            'class_id': class_id,
            'contexts': []
        }
        
        # Search in different areas and extract context
        if 'frames' in class_data:
            for frame in class_data['frames']:
                if isinstance(frame, dict) and self._search_in_structure(feature_name, frame):
                    context['contexts'].append({
                        'area': 'frame',
                        'frame_data': frame
                    })
                    
        return context if context['contexts'] else None
        
    def _validate_themrole_collection(self, themroles: Dict) -> Dict[str, Any]:
        """Validate themrole collection from CorpusCollectionBuilder."""
        validation = {
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
                if field in role_data:
                    validation['statistics'][f'with_{field}'] += 1
                else:
                    validation['issues'].append(f"Themrole {role_name} missing field: {field}")
                    
        # Set overall validity based on issues
        if validation['issues']:
            validation['valid'] = len(validation['issues']) < len(themroles) * 0.5  # Allow some issues
            
        return validation
        
    def _validate_predicate_collection(self, predicates: Dict) -> Dict[str, Any]:
        """Validate predicate collection from CorpusCollectionBuilder."""
        validation = {
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
            if 'definition' in pred_data:
                validation['statistics']['with_definition'] += 1
            else:
                validation['issues'].append(f"Predicate {pred_name} missing definition")
                
        # Set overall validity
        if validation['issues']:
            validation['valid'] = len(validation['issues']) < len(predicates) * 0.3
            
        return validation
        
    def _validate_feature_collection(self, features: List) -> Dict[str, Any]:
        """Validate verb-specific feature collection from CorpusCollectionBuilder."""
        validation = {
            'valid': True,
            'issues': [],
            'statistics': {
                'total_features': len(features),
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
        for feature in features:
            if not feature or (isinstance(feature, str) and not feature.strip()):
                validation['statistics']['empty_features'] += 1
                validation['issues'].append('Empty or whitespace-only feature found')
                
        # Check for duplicates
        duplicates = len(features) - validation['statistics']['unique_features']
        if duplicates > 0:
            validation['issues'].append(f'{duplicates} duplicate features found')
            
        return validation
        
    def _validate_restriction_collection(self, restrictions: List) -> Dict[str, Any]:
        """Validate restriction collection from CorpusCollectionBuilder."""
        validation = {
            'valid': True,
            'issues': [],
            'statistics': {
                'total_restrictions': len(restrictions),
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
        for restriction in restrictions:
            if not restriction or (isinstance(restriction, str) and not restriction.strip()):
                validation['statistics']['empty_restrictions'] += 1
                validation['issues'].append('Empty or whitespace-only restriction found')
                
        # Check for duplicates
        duplicates = len(restrictions) - validation['statistics']['unique_restrictions']
        if duplicates > 0:
            validation['issues'].append(f'{duplicates} duplicate restrictions found')
            
        return validation
    
    def __str__(self) -> str:
        """String representation of ReferenceDataProvider."""
        collections_count = len(self.collection_builder.reference_collections) if self.collection_builder.reference_collections else 0
        return f"ReferenceDataProvider(collections={collections_count}, builder_enabled=True)"