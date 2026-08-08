"""
VerbNet API Parser Module

Specialized parser for VerbNet API enhanced XML files. Handles parsing of
enhanced VerbNet data with additional API-specific features and metadata.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
from .verbnet_parser import VerbNetParser


class VNAPIParser(VerbNetParser):
    """
    Parser for VerbNet API enhanced XML files.
    
    Extends the standard VerbNet parser to handle API-specific enhancements
    including additional metadata, cross-references, and extended semantic
    information.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize VerbNet API parser with corpus path.
        
        Args:
            corpus_path (Path): Path to VN API corpus directory
        """
        super().__init__(corpus_path)
        self.api_version = "unknown"
        self.api_metadata = {}
    
    def parse_all_classes(self) -> Dict[str, Any]:
        """
        Parse all VerbNet API class files with enhanced features.
        
        Returns:
            dict: Complete VerbNet API class data with enhancements
        """
        # Start with standard VerbNet parsing
        vn_api_data = super().parse_all_classes()
        
        # Add API-specific enhancements
        vn_api_data.update({
            'api_metadata': {},
            'cross_references': {},
            'enhanced_semantics': {},
            'usage_statistics': {}
        })
        
        if not self.corpus_path or not self.corpus_path.exists():
            return vn_api_data
        
        # Parse API metadata file if available
        metadata_file = self.corpus_path / "api_metadata.xml"
        if metadata_file.exists():
            try:
                vn_api_data['api_metadata'] = self.parse_api_metadata(metadata_file)
                self.api_metadata = vn_api_data['api_metadata']
            except Exception as e:
                print(f"Error parsing API metadata: {e}")
        
        # Enhance existing class data with API features
        for class_id, class_data in vn_api_data.get('classes', {}).items():
            enhanced_class = self._enhance_class_with_api_features(class_data)
            vn_api_data['classes'][class_id] = enhanced_class
        
        # Build enhanced cross-references
        vn_api_data['cross_references'] = self._build_enhanced_cross_references(vn_api_data)
        
        return vn_api_data
    
    def _parse_vnclass_element(self, class_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a VNCLASS XML element with API enhancements.
        
        Args:
            class_element (ET.Element): VNCLASS XML element
            
        Returns:
            dict: Parsed class data with API enhancements
        """
        # Start with standard VerbNet parsing
        class_data = super()._parse_vnclass_element(class_element)
        
        # Add API-specific enhancements
        class_data.update({
            'api_version': class_element.get('api_version', self.api_version),
            'last_updated': class_element.get('last_updated', ''),
            'cross_references': self._parse_api_cross_references(class_element),
            'enhanced_semantics': self._parse_enhanced_semantics(class_element),
            'usage_notes': self._parse_usage_notes(class_element),
            'related_resources': self._parse_related_resources(class_element)
        })
        
        return class_data
    
    def _parse_api_cross_references(self, class_element: ET.Element) -> Dict[str, List[str]]:
        """Parse API-specific cross-references."""
        cross_refs = {
            'wordnet': [],
            'framenet': [],
            'propbank': [],
            'ontonotes': [],
            'external_apis': []
        }
        
        # Look for API cross-reference elements
        for xref in class_element.findall('.//API_XREF'):
            xref_type = xref.get('type', '').lower()
            xref_value = xref.get('value', '')
            
            if xref_type in cross_refs and xref_value:
                cross_refs[xref_type].append(xref_value)
        
        # Also check for enhanced mapping elements
        for mapping in class_element.findall('.//ENHANCED_MAPPING'):
            resource = mapping.get('resource', '').lower()
            mapping_id = mapping.get('id', '')
            confidence = float(mapping.get('confidence', 0.0))
            
            if resource in cross_refs and mapping_id:
                cross_refs[resource].append({
                    'id': mapping_id,
                    'confidence': confidence,
                    'mapping_type': mapping.get('type', 'automatic')
                })
        
        return cross_refs
    
    def _parse_enhanced_semantics(self, class_element: ET.Element) -> Dict[str, Any]:
        """Parse enhanced semantic information from API data."""
        enhanced_semantics = {
            'semantic_categories': [],
            'conceptual_structure': [],
            'causal_relations': [],
            'aspectual_properties': {}
        }
        
        # Parse semantic categories
        for sem_cat in class_element.findall('.//SEMANTIC_CATEGORY'):
            cat_data = {
                'category': sem_cat.get('name', ''),
                'confidence': float(sem_cat.get('confidence', 1.0)),
                'source': sem_cat.get('source', 'api')
            }
            enhanced_semantics['semantic_categories'].append(cat_data)
        
        # Parse conceptual structure
        for concept in class_element.findall('.//CONCEPTUAL_STRUCTURE'):
            concept_data = {
                'structure': concept.get('structure', ''),
                'representation': concept.text.strip() if concept.text else '',
                'formalism': concept.get('formalism', 'predicate_logic')
            }
            enhanced_semantics['conceptual_structure'].append(concept_data)
        
        # Parse causal relations
        for causal in class_element.findall('.//CAUSAL_RELATION'):
            causal_data = {
                'type': causal.get('type', ''),
                'cause': causal.get('cause', ''),
                'effect': causal.get('effect', ''),
                'strength': float(causal.get('strength', 0.5))
            }
            enhanced_semantics['causal_relations'].append(causal_data)
        
        # Parse aspectual properties
        aspectual = class_element.find('.//ASPECTUAL_PROPERTIES')
        if aspectual is not None:
            enhanced_semantics['aspectual_properties'] = {
                'telicity': aspectual.get('telicity', ''),
                'durativity': aspectual.get('durativity', ''),
                'dynamicity': aspectual.get('dynamicity', ''),
                'volitionality': aspectual.get('volitionality', '')
            }
        
        return enhanced_semantics
    
    def _parse_usage_notes(self, class_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse usage notes and linguistic commentary."""
        usage_notes = []
        
        for note in class_element.findall('.//USAGE_NOTE'):
            note_data = {
                'type': note.get('type', 'general'),
                'content': note.text.strip() if note.text else '',
                'author': note.get('author', ''),
                'date': note.get('date', ''),
                'examples': []
            }
            
            # Parse examples within usage notes
            for example in note.findall('.//EXAMPLE'):
                example_data = {
                    'text': example.text.strip() if example.text else '',
                    'source': example.get('source', ''),
                    'grammaticality': example.get('grammaticality', 'acceptable')
                }
                note_data['examples'].append(example_data)
            
            usage_notes.append(note_data)
        
        return usage_notes
    
    def _parse_related_resources(self, class_element: ET.Element) -> Dict[str, List[Dict[str, Any]]]:
        """Parse related external resources and APIs."""
        related_resources = {
            'external_apis': [],
            'research_papers': [],
            'linguistic_analyses': []
        }
        
        for resource in class_element.findall('.//RELATED_RESOURCE'):
            resource_type = resource.get('type', '').lower()
            
            resource_data = {
                'title': resource.get('title', ''),
                'url': resource.get('url', ''),
                'description': resource.text.strip() if resource.text else '',
                'relevance': float(resource.get('relevance', 0.5))
            }
            
            if resource_type in related_resources:
                related_resources[resource_type].append(resource_data)
            else:
                # Default to external APIs for unknown types
                related_resources['external_apis'].append(resource_data)
        
        return related_resources
    
    def _enhance_class_with_api_features(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance standard VerbNet class data with API-specific features.
        
        Args:
            class_data (dict): Standard VerbNet class data
            
        Returns:
            dict: Enhanced class data
        """
        # Add API-specific enhancements to existing data
        if 'frames' in class_data:
            enhanced_frames = []
            for frame in class_data['frames']:
                enhanced_frame = self._enhance_frame_with_api_features(frame)
                enhanced_frames.append(enhanced_frame)
            class_data['frames'] = enhanced_frames
        
        if 'themroles' in class_data:
            enhanced_roles = []
            for role in class_data['themroles']:
                enhanced_role = self._enhance_themrole_with_api_features(role)
                enhanced_roles.append(enhanced_role)
            class_data['themroles'] = enhanced_roles
        
        return class_data
    
    def _enhance_frame_with_api_features(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance frame data with API-specific features."""
        # Add frequency information, corpus statistics, etc.
        frame_data.update({
            'frequency': 0,  # Could be populated from corpus statistics
            'corpus_examples_count': len(frame_data.get('examples', [])),
            'semantic_complexity': self._calculate_semantic_complexity(frame_data)
        })
        
        return frame_data
    
    def _enhance_themrole_with_api_features(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance thematic role data with API-specific features."""
        # Add selectional restriction statistics, frequency, etc.
        role_data.update({
            'selectional_restriction_count': len(role_data.get('selrestrs', [])),
            'prototypicality': 0.5  # Could be calculated from corpus data
        })
        
        return role_data
    
    def _calculate_semantic_complexity(self, frame_data: Dict[str, Any]) -> float:
        """Calculate semantic complexity score for a frame."""
        complexity = 0.0
        
        # Factor in number of semantic predicates
        semantics = frame_data.get('semantics', [])
        complexity += len(semantics) * 0.1
        
        # Factor in argument structure complexity
        for pred in semantics:
            args = pred.get('args', [])
            complexity += len(args) * 0.05
        
        return min(complexity, 1.0)  # Cap at 1.0
    
    def _build_enhanced_cross_references(self, vn_api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive cross-reference mappings."""
        cross_references = {
            'by_resource': {},
            'by_class': {},
            'confidence_scores': {}
        }
        
        for class_id, class_data in vn_api_data.get('classes', {}).items():
            class_cross_refs = class_data.get('cross_references', {})
            
            for resource, refs in class_cross_refs.items():
                if resource not in cross_references['by_resource']:
                    cross_references['by_resource'][resource] = {}
                
                for ref in refs:
                    if isinstance(ref, dict):
                        ref_id = ref.get('id', str(ref))
                        confidence = ref.get('confidence', 1.0)
                    else:
                        ref_id = str(ref)
                        confidence = 1.0
                    
                    if ref_id not in cross_references['by_resource'][resource]:
                        cross_references['by_resource'][resource][ref_id] = []
                    
                    cross_references['by_resource'][resource][ref_id].append({
                        'class_id': class_id,
                        'confidence': confidence
                    })
            
            cross_references['by_class'][class_id] = class_cross_refs
        
        return cross_references
    
    def parse_api_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse API metadata file.
        
        Args:
            file_path (Path): Path to API metadata XML file
            
        Returns:
            dict: API metadata
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            metadata = {
                'api_version': root.get('version', 'unknown'),
                'build_date': root.get('build_date', ''),
                'data_sources': [],
                'enhancement_methods': [],
                'statistics': {}
            }
            
            # Parse data sources
            for source in root.findall('.//DATA_SOURCE'):
                source_data = {
                    'name': source.get('name', ''),
                    'version': source.get('version', ''),
                    'description': source.text.strip() if source.text else ''
                }
                metadata['data_sources'].append(source_data)
            
            # Parse enhancement methods
            for method in root.findall('.//ENHANCEMENT_METHOD'):
                method_data = {
                    'name': method.get('name', ''),
                    'type': method.get('type', ''),
                    'description': method.text.strip() if method.text else ''
                }
                metadata['enhancement_methods'].append(method_data)
            
            # Parse statistics
            stats_elem = root.find('.//STATISTICS')
            if stats_elem is not None:
                for stat in stats_elem:
                    stat_name = stat.tag.lower()
                    stat_value = stat.text.strip() if stat.text else '0'
                    try:
                        metadata['statistics'][stat_name] = float(stat_value)
                    except ValueError:
                        metadata['statistics'][stat_name] = stat_value
            
            return metadata
        except Exception as e:
            print(f"Error parsing API metadata: {e}")
            return {}