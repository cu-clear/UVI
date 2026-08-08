"""
ExportManager Helper Class

Data export with comprehensive analytics metadata via CorpusCollectionAnalyzer integration.
Enhances UVI export functionality with comprehensive analytics metadata, collection statistics,
and build metadata for enriched export capabilities.

This class enhances UVI's export methods (131 lines) with CorpusCollectionAnalyzer metadata
integration while maintaining full backward compatibility.
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionAnalyzer


class ExportManager(BaseHelper):
    """
    Data export with comprehensive analytics metadata via CorpusCollectionAnalyzer integration.
    
    Provides enhanced export capabilities with comprehensive analytics metadata, collection
    statistics, build metadata, and corpus health analysis. This class enhances UVI's export
    functionality while maintaining backward compatibility and adding powerful new features.
    
    Key Features:
    - Enhanced resource export with collection statistics and build metadata
    - Cross-corpus mappings export with mapping coverage analysis and validation status
    - Semantic profile export with profile completeness scoring and collection context
    - Collection analytics export with comprehensive statistics
    - Build metadata export with detailed build information
    - Corpus health report export with comprehensive analysis
    - Multiple export formats: JSON, XML, CSV
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize ExportManager with CorpusCollectionAnalyzer integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Initialize CorpusCollectionAnalyzer for comprehensive export metadata
        self.analytics = CorpusCollectionAnalyzer(
            loaded_data=uvi_instance.corpora_data,
            load_status=getattr(uvi_instance.corpus_loader, 'load_status', {}),
            build_metadata=getattr(uvi_instance.corpus_loader, 'build_metadata', {}),
            reference_collections=getattr(uvi_instance.corpus_loader, 'reference_collections', {}),
            corpus_paths=getattr(uvi_instance, 'corpus_paths', {})
        )
        
        # Export format handlers
        self.format_handlers = {
            'json': self._export_as_json,
            'xml': self._export_as_xml,
            'csv': self._export_as_csv
        }
        
    def export_resources(self, include_resources: Optional[List[str]] = None, 
                        format: str = 'json', include_mappings: bool = True, 
                        output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Enhanced resource export with CorpusCollectionAnalyzer metadata integration.
        
        Enhances UVI lines 2043-2106 with collection statistics and build metadata.
        Adds comprehensive metadata while maintaining backward compatibility.
        
        Args:
            include_resources (Optional[List[str]]): Resources to include, None for all
            format (str): Export format ('json', 'xml', 'csv')
            include_mappings (bool): Include cross-corpus mappings
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Export data as string or dict
        """
        # Default to all loaded resources if none specified
        if include_resources is None:
            include_resources = list(self.loaded_corpora)
            
        # Get comprehensive metadata from CorpusCollectionAnalyzer
        try:
            build_metadata = self.analytics.get_build_metadata()
            collection_stats = self.analytics.get_collection_statistics()
        except Exception as e:
            self.logger.warning(f"Could not get analytics metadata: {e}")
            build_metadata = {'timestamp': self._get_timestamp(), 'error': str(e)}
            collection_stats = {}
        
        export_data = {
            'export_metadata': {
                'export_type': 'resources',
                'format': format,
                'include_mappings': include_mappings,
                'export_timestamp': self._get_timestamp(),
                'included_resources': include_resources,
                'corpus_build_metadata': build_metadata.get('build_metadata', {}),
                'corpus_load_status': build_metadata.get('load_status', {}),
                'corpus_paths': build_metadata.get('corpus_paths', {}),
                'collection_statistics': {
                    resource: collection_stats.get(resource, {})
                    for resource in include_resources
                },
                'export_summary': {
                    'total_resources': len(include_resources),
                    'total_loaded_corpora': len(self.loaded_corpora),
                    'export_completeness': (len(include_resources) / len(self.loaded_corpora) * 100) if self.loaded_corpora else 0,
                    'analytics_version': '1.0'
                }
            },
            'resources': {}
        }
        
        # Export each requested resource with enhanced metadata
        for resource in include_resources:
            full_name = self._get_full_corpus_name(resource)
            if full_name in self.corpora_data:
                resource_data = self.corpora_data[full_name].copy()
                
                # Add CorpusCollectionAnalyzer statistics to each resource
                resource_stats = collection_stats.get(full_name, {})
                if resource_stats:
                    resource_data['analytics_metadata'] = {
                        'collection_statistics': resource_stats,
                        'resource_size': self._calculate_resource_size(resource_data),
                        'data_quality_score': self._calculate_data_quality_score(resource_data, full_name)
                    }
                
                # Add cross-corpus mappings if requested
                if include_mappings:
                    mappings = self._extract_resource_mappings(full_name)
                    if mappings:
                        resource_data['cross_corpus_mappings'] = mappings
                        resource_data['analytics_metadata']['mapping_coverage'] = self._calculate_mapping_coverage(mappings, resource_stats)
                
                export_data['resources'][resource] = resource_data
            else:
                self.logger.warning(f"Resource {resource} ({full_name}) not found in loaded data")
                
        # Handle output based on format and path
        return self._finalize_export(export_data, format, output_path)
        
    def export_cross_corpus_mappings(self, format: str = 'json', 
                                   output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Enhanced cross-corpus mappings with analytics metadata.
        
        Enhances UVI lines 2107-2137 with mapping coverage analysis and validation status.
        Adds comprehensive mapping analysis while maintaining compatibility.
        
        Args:
            format (str): Export format ('json', 'xml', 'csv')
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Mapping export data
        """
        try:
            build_metadata = self.analytics.get_build_metadata()
            collection_stats = self.analytics.get_collection_statistics()
        except Exception as e:
            self.logger.warning(f"Could not get analytics metadata: {e}")
            build_metadata = {'timestamp': self._get_timestamp()}
            collection_stats = {}
        
        mappings_data = {
            'export_metadata': {
                'export_type': 'cross_corpus_mappings',
                'format': format,
                'export_timestamp': self._get_timestamp(),
                'corpus_collection_statistics': collection_stats,
                'corpus_build_metadata': build_metadata,
                'mapping_analysis': {
                    'coverage_analysis': self._calculate_comprehensive_mapping_coverage(collection_stats),
                    'validation_status': self._get_mapping_validation_status(),
                    'mapping_density': self._calculate_mapping_density(collection_stats)
                }
            },
            'mappings': self._extract_all_cross_corpus_mappings()
        }
        
        return self._finalize_export(mappings_data, format, output_path)
        
    def export_semantic_profile(self, lemma: str, format: str = 'json', 
                              output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Enhanced semantic profile export with comprehensive analytics.
        
        Enhances UVI lines 2139-2174 with profile completeness scoring and collection context.
        Adds detailed analysis while maintaining profile format compatibility.
        
        Args:
            lemma (str): Lemma to build semantic profile for
            format (str): Export format ('json', 'xml', 'csv')
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Semantic profile export data
        """
        # Build complete semantic profile
        profile = self._build_complete_semantic_profile(lemma)
        
        # Get analytics context for the semantic profile
        try:
            build_metadata = self.analytics.get_build_metadata()
            collection_stats = self.analytics.get_collection_statistics()
        except Exception as e:
            self.logger.warning(f"Could not get analytics metadata: {e}")
            build_metadata = {'timestamp': self._get_timestamp()}
            collection_stats = {}
        
        export_data = {
            'export_metadata': {
                'export_type': 'semantic_profile',
                'target_lemma': lemma,
                'format': format,
                'export_timestamp': self._get_timestamp(),
                'corpus_coverage': {
                    corpus: profile.get(corpus) is not None
                    for corpus in collection_stats.keys()
                    if corpus != 'reference_collections'
                },
                'collection_sizes': collection_stats,
                'profile_analysis': {
                    'completeness': self._calculate_profile_completeness(profile, collection_stats),
                    'depth_analysis': self._analyze_profile_depth(profile),
                    'cross_corpus_connections': self._count_cross_corpus_connections(profile),
                    'semantic_richness_score': self._calculate_semantic_richness(profile)
                },
                'build_context': build_metadata
            },
            'semantic_profile': profile
        }
        
        return self._finalize_export(export_data, format, output_path)
        
    def export_collection_analytics(self, collection_types: Optional[List[str]] = None, 
                                   format: str = 'json', output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Export CorpusCollectionAnalyzer statistics with comprehensive analysis.
        
        New functionality that exposes CorpusCollectionAnalyzer capabilities.
        
        Args:
            collection_types (Optional[List[str]]): Specific collection types to export
            format (str): Export format ('json', 'xml', 'csv')
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Collection analytics export data
        """
        try:
            collection_stats = self.analytics.get_collection_statistics()
            build_metadata = self.analytics.get_build_metadata()
        except Exception as e:
            return self._error_export(f"Failed to get collection analytics: {e}", format, output_path)
            
        # Filter collection types if specified
        if collection_types:
            filtered_stats = {
                collection_type: collection_stats.get(collection_type, {})
                for collection_type in collection_types
            }
        else:
            filtered_stats = collection_stats
            
        analytics_data = {
            'export_metadata': {
                'export_type': 'collection_analytics',
                'format': format,
                'export_timestamp': self._get_timestamp(),
                'collection_types_included': list(filtered_stats.keys()),
                'analytics_version': 'CorpusCollectionAnalyzer_1.0'
            },
            'collection_statistics': filtered_stats,
            'build_metadata': build_metadata,
            'analytics_summary': {
                'total_collections_analyzed': len(filtered_stats),
                'total_corpus_items': self._calculate_total_items(filtered_stats),
                'collection_health_score': self._calculate_collection_health_score(filtered_stats),
                'data_completeness_score': self._calculate_data_completeness(filtered_stats)
            }
        }
        
        return self._finalize_export(analytics_data, format, output_path)
        
    def export_build_metadata(self, format: str = 'json', 
                            output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Export build and load metadata with detailed information.
        
        New functionality that exposes build and loading metadata.
        
        Args:
            format (str): Export format ('json', 'xml', 'csv')
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Build metadata export data
        """
        try:
            build_metadata = self.analytics.get_build_metadata()
        except Exception as e:
            return self._error_export(f"Failed to get build metadata: {e}", format, output_path)
            
        metadata_export = {
            'export_metadata': {
                'export_type': 'build_metadata',
                'format': format,
                'export_timestamp': self._get_timestamp()
            },
            'build_metadata': build_metadata,
            'metadata_analysis': {
                'total_corpora_paths': len(build_metadata.get('corpus_paths', {})),
                'load_success_rate': self._calculate_load_success_rate(build_metadata.get('load_status', {})),
                'build_completeness': self._assess_build_completeness(build_metadata),
                'system_information': {
                    'working_directory': str(Path.cwd()),
                    'export_capabilities': list(self.format_handlers.keys())
                }
            }
        }
        
        return self._finalize_export(metadata_export, format, output_path)
        
    def export_corpus_health_report(self, format: str = 'json', 
                                  output_path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Export comprehensive corpus health analysis.
        
        New functionality that provides comprehensive health analysis.
        
        Args:
            format (str): Export format ('json', 'xml', 'csv')
            output_path (Optional[str]): Path to save export file
            
        Returns:
            Union[str, Dict[str, Any]]: Corpus health report
        """
        try:
            collection_stats = self.analytics.get_collection_statistics()
            build_metadata = self.analytics.get_build_metadata()
        except Exception as e:
            return self._error_export(f"Failed to generate health report: {e}", format, output_path)
            
        health_report = {
            'export_metadata': {
                'export_type': 'corpus_health_report',
                'format': format,
                'export_timestamp': self._get_timestamp(),
                'report_version': '1.0'
            },
            'health_summary': {
                'overall_health_score': self._calculate_overall_health_score(collection_stats, build_metadata),
                'corpus_load_status': build_metadata.get('load_status', {}),
                'data_integrity_status': self._assess_data_integrity(collection_stats),
                'coverage_analysis': self._analyze_corpus_coverage(collection_stats)
            },
            'detailed_analysis': {
                'per_corpus_health': self._analyze_per_corpus_health(collection_stats),
                'cross_corpus_consistency': self._analyze_cross_corpus_consistency(collection_stats),
                'reference_collection_health': self._analyze_reference_collection_health(collection_stats),
                'recommendations': self._generate_health_recommendations(collection_stats, build_metadata)
            },
            'collection_statistics': collection_stats,
            'build_metadata': build_metadata
        }
        
        return self._finalize_export(health_report, format, output_path)
    
    # Private helper methods
    
    def _finalize_export(self, data: Dict[str, Any], format: str, 
                        output_path: Optional[str]) -> Union[str, Dict[str, Any]]:
        """Finalize export with format conversion and optional file writing."""
        try:
            # Convert to requested format
            if format.lower() in self.format_handlers:
                formatted_data = self.format_handlers[format.lower()](data)
            else:
                self.logger.warning(f"Unsupported format {format}, defaulting to JSON")
                formatted_data = self._export_as_json(data)
            
            # Write to file if path provided
            if output_path:
                self._write_export_file(formatted_data, output_path, format)
                return {
                    'export_successful': True,
                    'output_path': output_path,
                    'format': format,
                    'data_size': len(str(formatted_data))
                }
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Export finalization failed: {e}")
            return self._error_export(str(e), format, output_path)
            
    def _export_as_json(self, data: Dict[str, Any]) -> str:
        """Export data as JSON string."""
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        
    def _export_as_xml(self, data: Dict[str, Any], root_tag: str = 'uvi_export') -> str:
        """Export data as XML string."""
        root = ET.Element(root_tag)
        self._dict_to_xml_element(data, root)
        return ET.tostring(root, encoding='unicode')
        
    def _export_as_csv(self, data: Dict[str, Any]) -> str:
        """Export data as CSV string."""
        # Flatten the data structure for CSV export
        flattened = self._flatten_for_csv(data)
        
        if not flattened:
            return "# No data available for CSV export\n"
            
        # Generate CSV content
        output = []
        if isinstance(flattened[0], dict) and flattened:
            # Standard CSV with headers
            fieldnames = list(flattened[0].keys())
            output.append(','.join(fieldnames))
            
            for row in flattened:
                csv_row = []
                for field in fieldnames:
                    value = str(row.get(field, ''))
                    # Escape commas and quotes
                    if ',' in value or '"' in value or '\n' in value:
                        value = '"' + value.replace('"', '""') + '"'
                    csv_row.append(value)
                output.append(','.join(csv_row))
        else:
            # Simple key-value pairs
            output.append('Key,Value')
            for item in flattened:
                if isinstance(item, tuple) and len(item) == 2:
                    key, value = item
                    value = str(value).replace(',', ';').replace('\n', ' ')
                    output.append(f'{key},{value}')
                    
        return '\n'.join(output)
        
    def _dict_to_xml_element(self, data: Any, parent: ET.Element):
        """Convert dictionary data to XML elements recursively."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Clean key for XML compatibility
                clean_key = str(key).replace(' ', '_').replace('-', '_')
                child = ET.SubElement(parent, clean_key)
                self._dict_to_xml_element(value, child)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_elem = ET.SubElement(parent, f'item_{i}')
                self._dict_to_xml_element(item, item_elem)
        else:
            parent.text = str(data)
            
    def _flatten_for_csv(self, data: Dict[str, Any], prefix: str = '') -> List[Union[Dict[str, Any], tuple]]:
        """Flatten nested dictionary structure for CSV export."""
        flattened = []
        
        if isinstance(data, dict):
            # Check if this looks like a table structure
            if self._is_table_like(data):
                return self._extract_table_data(data)
                
            # Otherwise flatten key-value pairs
            for key, value in data.items():
                new_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, (dict, list)) and not self._is_simple_collection(value):
                    flattened.extend(self._flatten_for_csv(value, new_key))
                else:
                    flattened.append((new_key, self._serialize_value(value)))
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_key = f"{prefix}[{i}]" if prefix else f"item_{i}"
                if isinstance(item, (dict, list)):
                    flattened.extend(self._flatten_for_csv(item, new_key))
                else:
                    flattened.append((new_key, self._serialize_value(item)))
                    
        return flattened
        
    def _is_table_like(self, data: Dict) -> bool:
        """Check if dictionary structure looks like a table."""
        if 'resources' in data and isinstance(data['resources'], dict):
            return True
        if 'collection_statistics' in data and isinstance(data['collection_statistics'], dict):
            return True
        return False
        
    def _extract_table_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Extract table-like data from dictionary."""
        rows = []
        
        if 'resources' in data:
            for resource_name, resource_data in data['resources'].items():
                row = {'resource_name': resource_name}
                row.update(self._extract_flat_fields(resource_data))
                rows.append(row)
                
        elif 'collection_statistics' in data:
            for collection_name, collection_data in data['collection_statistics'].items():
                row = {'collection_name': collection_name}
                row.update(self._extract_flat_fields(collection_data))
                rows.append(row)
                
        return rows
        
    def _extract_flat_fields(self, data: Any, max_depth: int = 2) -> Dict[str, Any]:
        """Extract flat fields from nested data structure."""
        flat_fields = {}
        
        if isinstance(data, dict) and max_depth > 0:
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    flat_fields[key] = value
                elif isinstance(value, list) and all(isinstance(x, (str, int, float)) for x in value):
                    flat_fields[key] = ', '.join(map(str, value))
                elif isinstance(value, dict):
                    sub_fields = self._extract_flat_fields(value, max_depth - 1)
                    for sub_key, sub_value in sub_fields.items():
                        flat_fields[f"{key}.{sub_key}"] = sub_value
                else:
                    flat_fields[key] = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                    
        return flat_fields
        
    def _is_simple_collection(self, value: Any) -> bool:
        """Check if value is a simple collection that can be serialized inline."""
        if isinstance(value, list):
            return len(value) <= 5 and all(isinstance(x, (str, int, float)) for x in value)
        return False
        
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for CSV output."""
        if isinstance(value, list):
            if all(isinstance(x, (str, int, float)) for x in value):
                return ', '.join(map(str, value))
            else:
                return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return f"{{dict with {len(value)} keys}}"
        else:
            return str(value)
            
    def _write_export_file(self, data: str, output_path: str, format: str):
        """Write export data to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data)
                
            self.logger.info(f"Export written to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to write export file: {e}")
            raise
            
    def _error_export(self, error_message: str, format: str, 
                     output_path: Optional[str]) -> Dict[str, Any]:
        """Create error export response."""
        error_data = {
            'export_error': True,
            'error_message': error_message,
            'export_timestamp': self._get_timestamp(),
            'requested_format': format,
            'requested_output_path': output_path
        }
        
        if output_path:
            try:
                formatted_error = self.format_handlers.get(format.lower(), self._export_as_json)(error_data)
                self._write_export_file(formatted_error, output_path, format)
            except Exception:
                pass  # Don't compound the error
                
        return error_data
    
    # Analytics calculation methods
    
    def _calculate_resource_size(self, resource_data: Dict) -> Dict[str, Any]:
        """Calculate size metrics for a resource."""
        size_info = {
            'total_keys': len(resource_data),
            'estimated_memory_kb': len(str(resource_data)) / 1024
        }
        
        # Add resource-specific size metrics
        if 'classes' in resource_data:
            size_info['total_classes'] = len(resource_data['classes'])
        elif 'frames' in resource_data:
            size_info['total_frames'] = len(resource_data['frames'])
        elif 'predicates' in resource_data:
            size_info['total_predicates'] = len(resource_data['predicates'])
            
        return size_info
        
    def _calculate_data_quality_score(self, resource_data: Dict, corpus_name: str) -> float:
        """Calculate a data quality score for a resource."""
        score = 0.0
        max_score = 100.0
        
        # Basic structure check (30 points)
        expected_keys = {
            'verbnet': ['classes'],
            'framenet': ['frames'],
            'propbank': ['predicates']
        }.get(corpus_name, [])
        
        if expected_keys:
            present_keys = sum(1 for key in expected_keys if key in resource_data)
            score += (present_keys / len(expected_keys)) * 30
        else:
            score += 30  # Give full points for unknown corpus types
            
        # Data completeness (40 points)
        if resource_data:
            non_empty_values = sum(1 for v in resource_data.values() if v)
            score += (non_empty_values / len(resource_data)) * 40
        
        # Metadata presence (30 points)
        metadata_indicators = ['timestamp', 'version', 'source', 'build_info']
        present_metadata = sum(1 for indicator in metadata_indicators if indicator in resource_data)
        score += (present_metadata / len(metadata_indicators)) * 30
        
        return min(score, max_score)
        
    def _calculate_mapping_coverage(self, mappings: Dict, resource_stats: Dict) -> Dict[str, Any]:
        """Calculate mapping coverage statistics."""
        coverage = {
            'total_mappings': sum(len(m) if isinstance(m, list) else 1 for m in mappings.values()),
            'mapped_corpora': list(mappings.keys()),
            'coverage_percentage': 0.0
        }
        
        # Calculate coverage percentage if resource stats available
        if resource_stats:
            total_items = self._get_resource_item_count(resource_stats)
            if total_items > 0:
                coverage['coverage_percentage'] = (coverage['total_mappings'] / total_items) * 100
                
        return coverage
        
    def _get_resource_item_count(self, resource_stats: Dict) -> int:
        """Get total item count from resource statistics."""
        # Try different keys that might represent item counts
        for key in ['classes', 'frames', 'predicates', 'entries', 'synsets', 'total']:
            if key in resource_stats and isinstance(resource_stats[key], int):
                return resource_stats[key]
        return 0
        
    def _calculate_comprehensive_mapping_coverage(self, collection_stats: Dict) -> Dict[str, Any]:
        """Calculate comprehensive mapping coverage across all corpora."""
        coverage_analysis = {
            'per_corpus_coverage': {},
            'overall_coverage': 0.0,
            'mapping_density': {}
        }
        
        total_mappings = 0
        total_items = 0
        
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            corpus_mappings = self._count_corpus_mappings(corpus_name)
            corpus_items = self._get_resource_item_count(stats)
            
            if corpus_items > 0:
                coverage_pct = (corpus_mappings / corpus_items) * 100
                coverage_analysis['per_corpus_coverage'][corpus_name] = {
                    'mappings': corpus_mappings,
                    'total_items': corpus_items,
                    'coverage_percentage': coverage_pct
                }
                
                total_mappings += corpus_mappings
                total_items += corpus_items
                
        if total_items > 0:
            coverage_analysis['overall_coverage'] = (total_mappings / total_items) * 100
            
        return coverage_analysis
        
    def _get_mapping_validation_status(self) -> Dict[str, Any]:
        """Get validation status for cross-corpus mappings."""
        # This would integrate with ValidationManager if available
        return {
            'validation_available': False,
            'message': 'Mapping validation requires ValidationManager integration'
        }
        
    def _calculate_mapping_density(self, collection_stats: Dict) -> Dict[str, float]:
        """Calculate mapping density across collections."""
        density = {}
        
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            mappings = self._count_corpus_mappings(corpus_name)
            items = self._get_resource_item_count(stats)
            
            if items > 0:
                density[corpus_name] = mappings / items
            else:
                density[corpus_name] = 0.0
                
        return density
        
    def _count_corpus_mappings(self, corpus_name: str) -> int:
        """Count cross-corpus mappings for a specific corpus."""
        # This would count actual mappings in the corpus data
        # Placeholder implementation
        corpus_data = self._get_corpus_data(corpus_name)
        
        mapping_count = 0
        if corpus_data:
            # Count mappings in the corpus data structure
            mapping_count = self._count_mappings_in_data(corpus_data)
            
        return mapping_count
        
    def _count_mappings_in_data(self, data: Any, depth: int = 0) -> int:
        """Recursively count mapping-like structures in data."""
        if depth > 3:  # Prevent infinite recursion
            return 0
            
        count = 0
        
        if isinstance(data, dict):
            # Look for mapping indicators
            if 'mappings' in data:
                mappings = data['mappings']
                if isinstance(mappings, dict):
                    count += len(mappings)
                elif isinstance(mappings, list):
                    count += len(mappings)
                    
            # Recurse into other dictionary values
            for value in data.values():
                count += self._count_mappings_in_data(value, depth + 1)
                
        elif isinstance(data, list):
            for item in data:
                count += self._count_mappings_in_data(item, depth + 1)
                
        return count
        
    def _build_complete_semantic_profile(self, lemma: str) -> Dict[str, Any]:
        """Build complete semantic profile for a lemma across all corpora."""
        profile = {
            'lemma': lemma,
            'profile_timestamp': self._get_timestamp(),
            'corpus_entries': {}
        }
        
        # Search for lemma in each loaded corpus
        for corpus_name in self.loaded_corpora:
            corpus_profile = self._build_corpus_profile_for_lemma(lemma, corpus_name)
            if corpus_profile:
                profile['corpus_entries'][corpus_name] = corpus_profile
                
        return profile
        
    def _build_corpus_profile_for_lemma(self, lemma: str, corpus_name: str) -> Optional[Dict[str, Any]]:
        """Build semantic profile for lemma in specific corpus."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return None
            
        # Corpus-specific lemma search logic
        if corpus_name == 'verbnet':
            return self._search_verbnet_for_lemma(lemma, corpus_data)
        elif corpus_name == 'framenet':
            return self._search_framenet_for_lemma(lemma, corpus_data)
        elif corpus_name == 'propbank':
            return self._search_propbank_for_lemma(lemma, corpus_data)
        else:
            return self._generic_lemma_search(lemma, corpus_data, corpus_name)
            
    def _search_verbnet_for_lemma(self, lemma: str, verbnet_data: Dict) -> Optional[Dict]:
        """Search for lemma in VerbNet data."""
        matches = []
        classes = verbnet_data.get('classes', {})
        lemma_lower = lemma.lower()
        
        for class_id, class_data in classes.items():
            members = class_data.get('members', [])
            if any(lemma_lower in member.lower() for member in members):
                matches.append({
                    'class_id': class_id,
                    'class_data': class_data,
                    'match_type': 'member'
                })
                
        return {'matches': matches, 'total': len(matches)} if matches else None
        
    def _search_framenet_for_lemma(self, lemma: str, framenet_data: Dict) -> Optional[Dict]:
        """Search for lemma in FrameNet data."""
        matches = []
        frames = framenet_data.get('frames', {})
        lemma_lower = lemma.lower()
        
        for frame_name, frame_data in frames.items():
            lexical_units = frame_data.get('lexical_units', [])
            if any(lemma_lower in lu.get('name', '').lower() for lu in lexical_units):
                matches.append({
                    'frame_name': frame_name,
                    'frame_data': frame_data,
                    'match_type': 'lexical_unit'
                })
                
        return {'matches': matches, 'total': len(matches)} if matches else None
        
    def _search_propbank_for_lemma(self, lemma: str, propbank_data: Dict) -> Optional[Dict]:
        """Search for lemma in PropBank data."""
        predicates = propbank_data.get('predicates', {})
        lemma_lower = lemma.lower()
        
        if lemma_lower in predicates:
            return {
                'matches': [{'predicate': lemma, 'data': predicates[lemma_lower]}],
                'total': 1,
                'match_type': 'direct'
            }
        
        return None
        
    def _generic_lemma_search(self, lemma: str, corpus_data: Dict, corpus_name: str) -> Optional[Dict]:
        """Generic lemma search for unknown corpus types."""
        # Simple string matching across corpus data
        lemma_lower = lemma.lower()
        matches = []
        
        # Search through corpus data structure
        self._recursive_lemma_search(lemma_lower, corpus_data, matches, corpus_name)
        
        return {'matches': matches, 'total': len(matches)} if matches else None
        
    def _recursive_lemma_search(self, lemma: str, data: Any, matches: List, context: str, depth: int = 0):
        """Recursively search for lemma in data structure."""
        if depth > 5:  # Prevent deep recursion
            return
            
        if isinstance(data, str) and lemma in data.lower():
            matches.append({
                'context': context,
                'match_text': data[:100],
                'match_type': 'text'
            })
        elif isinstance(data, dict):
            for key, value in data.items():
                self._recursive_lemma_search(lemma, value, matches, f"{context}.{key}", depth + 1)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._recursive_lemma_search(lemma, item, matches, f"{context}[{i}]", depth + 1)
                
    def _calculate_profile_completeness(self, profile: Dict, collection_stats: Dict) -> Dict[str, float]:
        """Calculate completeness percentage of semantic profile across corpora."""
        completeness = {}
        
        corpus_entries = profile.get('corpus_entries', {})
        
        for corpus in collection_stats.keys():
            if corpus == 'reference_collections':
                continue
                
            if corpus in corpus_entries:
                entry_data = corpus_entries[corpus]
                # Score based on richness of data
                completeness[corpus] = self._score_profile_entry(entry_data)
            else:
                completeness[corpus] = 0.0
                
        # Overall completeness as average
        if completeness:
            completeness['overall'] = sum(completeness.values()) / len(completeness)
        else:
            completeness['overall'] = 0.0
        
        return completeness
        
    def _score_profile_entry(self, entry_data: Dict) -> float:
        """Score the richness/completeness of a profile entry."""
        if not entry_data:
            return 0.0
            
        score = 0.0
        
        # Base score for having any matches
        if entry_data.get('total', 0) > 0:
            score += 50.0
            
        # Additional score based on number of matches
        total_matches = entry_data.get('total', 0)
        if total_matches > 1:
            score += min(25.0, total_matches * 5)
            
        # Score for data richness
        matches = entry_data.get('matches', [])
        if matches and isinstance(matches[0], dict):
            avg_keys = sum(len(match) for match in matches) / len(matches)
            score += min(25.0, avg_keys * 3)
            
        return min(score, 100.0)
        
    def _analyze_profile_depth(self, profile: Dict) -> Dict[str, Any]:
        """Analyze the depth and breadth of a semantic profile."""
        corpus_entries = profile.get('corpus_entries', {})
        
        return {
            'total_corpora_covered': len(corpus_entries),
            'total_matches': sum(entry.get('total', 0) for entry in corpus_entries.values()),
            'average_matches_per_corpus': (
                sum(entry.get('total', 0) for entry in corpus_entries.values()) / len(corpus_entries)
                if corpus_entries else 0
            ),
            'richest_corpus': max(
                corpus_entries.items(),
                key=lambda x: x[1].get('total', 0),
                default=(None, {})
            )[0] if corpus_entries else None
        }
        
    def _count_cross_corpus_connections(self, profile: Dict) -> int:
        """Count cross-corpus connections in profile."""
        # This would analyze cross-references between corpus entries
        # Placeholder implementation
        corpus_entries = profile.get('corpus_entries', {})
        return len(corpus_entries) * (len(corpus_entries) - 1) // 2  # Possible connections
        
    def _calculate_semantic_richness(self, profile: Dict) -> float:
        """Calculate semantic richness score for profile."""
        corpus_entries = profile.get('corpus_entries', {})
        
        if not corpus_entries:
            return 0.0
            
        # Base richness on coverage and depth
        coverage_score = len(corpus_entries) * 20  # Max 100 for 5 corpora
        depth_score = min(50, sum(entry.get('total', 0) for entry in corpus_entries.values()) * 2)
        
        return min(coverage_score + depth_score, 100.0)
    
    # Analytics summary methods
    
    def _calculate_total_items(self, collection_stats: Dict) -> int:
        """Calculate total items across all collections."""
        total = 0
        for corpus_stats in collection_stats.values():
            if isinstance(corpus_stats, dict):
                total += self._get_resource_item_count(corpus_stats)
        return total
        
    def _calculate_collection_health_score(self, collection_stats: Dict) -> float:
        """Calculate overall health score for collections."""
        if not collection_stats:
            return 0.0
            
        scores = []
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            # Score based on presence and size of collections
            score = 0.0
            if isinstance(stats, dict) and stats:
                score += 50  # Base score for having data
                
                # Additional score based on size
                item_count = self._get_resource_item_count(stats)
                if item_count > 0:
                    score += min(50, item_count / 100 * 50)  # Scale up to 50 points
                    
            scores.append(score)
            
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_data_completeness(self, collection_stats: Dict) -> float:
        """Calculate data completeness score."""
        if not collection_stats:
            return 0.0
            
        total_corpora = len([k for k in collection_stats.keys() if k != 'reference_collections'])
        loaded_corpora = len([k for k, v in collection_stats.items() 
                            if k != 'reference_collections' and v])
        
        return (loaded_corpora / total_corpora * 100) if total_corpora > 0 else 0.0
        
    def _calculate_load_success_rate(self, load_status: Dict) -> float:
        """Calculate load success rate from load status."""
        if not load_status:
            return 0.0
            
        successful = sum(1 for status in load_status.values() if status == 'success')
        total = len(load_status)
        
        return (successful / total * 100) if total > 0 else 0.0
        
    def _assess_build_completeness(self, build_metadata: Dict) -> Dict[str, Any]:
        """Assess completeness of build metadata."""
        expected_fields = ['timestamp', 'build_metadata', 'load_status', 'corpus_paths']
        present_fields = [field for field in expected_fields if field in build_metadata]
        
        return {
            'expected_fields': len(expected_fields),
            'present_fields': len(present_fields),
            'completeness_percentage': len(present_fields) / len(expected_fields) * 100,
            'missing_fields': [field for field in expected_fields if field not in build_metadata]
        }
        
    def _calculate_overall_health_score(self, collection_stats: Dict, build_metadata: Dict) -> float:
        """Calculate overall health score combining various metrics."""
        scores = []
        
        # Collection health (40%)
        collection_health = self._calculate_collection_health_score(collection_stats)
        scores.append(collection_health * 0.4)
        
        # Load success rate (30%)
        load_success = self._calculate_load_success_rate(build_metadata.get('load_status', {}))
        scores.append(load_success * 0.3)
        
        # Data completeness (30%)
        data_completeness = self._calculate_data_completeness(collection_stats)
        scores.append(data_completeness * 0.3)
        
        return sum(scores)
        
    def _assess_data_integrity(self, collection_stats: Dict) -> str:
        """Assess data integrity status."""
        if not collection_stats:
            return 'no_data'
            
        # Simple integrity assessment
        corpora_with_data = sum(1 for stats in collection_stats.values() 
                              if isinstance(stats, dict) and stats)
        total_corpora = len(collection_stats)
        
        if corpora_with_data == total_corpora:
            return 'excellent'
        elif corpora_with_data > total_corpora * 0.8:
            return 'good'
        elif corpora_with_data > total_corpora * 0.5:
            return 'fair'
        else:
            return 'poor'
            
    def _analyze_corpus_coverage(self, collection_stats: Dict) -> Dict[str, Any]:
        """Analyze corpus coverage statistics."""
        coverage = {
            'total_corpora': len([k for k in collection_stats.keys() if k != 'reference_collections']),
            'corpora_with_data': 0,
            'coverage_by_corpus': {}
        }
        
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            has_data = isinstance(stats, dict) and bool(stats)
            coverage['coverage_by_corpus'][corpus_name] = has_data
            
            if has_data:
                coverage['corpora_with_data'] += 1
                
        coverage['coverage_percentage'] = (
            coverage['corpora_with_data'] / coverage['total_corpora'] * 100
            if coverage['total_corpora'] > 0 else 0
        )
        
        return coverage
        
    def _analyze_per_corpus_health(self, collection_stats: Dict) -> Dict[str, Dict[str, Any]]:
        """Analyze health status for each corpus."""
        health_analysis = {}
        
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            health = {
                'status': 'unknown',
                'data_present': isinstance(stats, dict) and bool(stats),
                'item_count': 0,
                'health_score': 0.0
            }
            
            if isinstance(stats, dict) and stats:
                health['item_count'] = self._get_resource_item_count(stats)
                
                if health['item_count'] > 0:
                    health['status'] = 'healthy'
                    health['health_score'] = min(100.0, health['item_count'] / 10)
                else:
                    health['status'] = 'loaded_no_items'
                    health['health_score'] = 25.0
            else:
                health['status'] = 'no_data'
                
            health_analysis[corpus_name] = health
            
        return health_analysis
        
    def _analyze_cross_corpus_consistency(self, collection_stats: Dict) -> Dict[str, Any]:
        """Analyze consistency across corpora."""
        # This would check for cross-corpus consistency
        return {
            'consistency_checks_performed': False,
            'message': 'Cross-corpus consistency analysis requires additional integration'
        }
        
    def _analyze_reference_collection_health(self, collection_stats: Dict) -> Dict[str, Any]:
        """Analyze health of reference collections."""
        ref_collections = collection_stats.get('reference_collections', {})
        
        if not ref_collections:
            return {
                'status': 'not_available',
                'health_score': 0.0
            }
            
        expected_collections = ['themroles', 'predicates', 'verb_specific_features', 
                              'syntactic_restrictions', 'selectional_restrictions']
        
        present_collections = [col for col in expected_collections if col in ref_collections]
        
        return {
            'status': 'available',
            'total_collections': len(ref_collections),
            'expected_collections': len(expected_collections),
            'present_collections': len(present_collections),
            'completeness_percentage': len(present_collections) / len(expected_collections) * 100,
            'health_score': len(present_collections) / len(expected_collections) * 100
        }
        
    def _generate_health_recommendations(self, collection_stats: Dict, 
                                       build_metadata: Dict) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        # Check for missing corpora
        load_status = build_metadata.get('load_status', {})
        failed_loads = [corpus for corpus, status in load_status.items() if status != 'success']
        
        if failed_loads:
            recommendations.append(f"Investigate failed corpus loads: {', '.join(failed_loads)}")
            
        # Check data completeness
        completeness = self._calculate_data_completeness(collection_stats)
        if completeness < 80:
            recommendations.append("Consider reloading corpora to improve data completeness")
            
        # Check collection health
        health_score = self._calculate_collection_health_score(collection_stats)
        if health_score < 70:
            recommendations.append("Review corpus data quality and consider validation checks")
            
        # Check reference collections
        ref_health = self._analyze_reference_collection_health(collection_stats)
        if ref_health.get('health_score', 0) < 80:
            recommendations.append("Rebuild reference collections to ensure completeness")
            
        if not recommendations:
            recommendations.append("Corpus collection health looks good!")
            
        return recommendations
    
    # Resource mapping methods
    
    def _extract_resource_mappings(self, corpus_name: str) -> Dict[str, Any]:
        """Extract cross-corpus mappings for a resource."""
        mappings = {}
        corpus_data = self._get_corpus_data(corpus_name)
        
        if not corpus_data:
            return mappings
            
        # Extract mappings based on corpus type
        if corpus_name == 'verbnet':
            mappings = self._extract_verbnet_mappings(corpus_data)
        elif corpus_name == 'framenet':
            mappings = self._extract_framenet_mappings(corpus_data)
        elif corpus_name == 'propbank':
            mappings = self._extract_propbank_mappings(corpus_data)
            
        return mappings
        
    def _extract_verbnet_mappings(self, verbnet_data: Dict) -> Dict[str, List]:
        """Extract mappings from VerbNet data."""
        mappings = {}
        classes = verbnet_data.get('classes', {})
        
        for class_id, class_data in classes.items():
            class_mappings = class_data.get('mappings', {})
            for target_corpus, target_mappings in class_mappings.items():
                if target_corpus not in mappings:
                    mappings[target_corpus] = []
                mappings[target_corpus].extend(target_mappings)
                
        return mappings
        
    def _extract_framenet_mappings(self, framenet_data: Dict) -> Dict[str, List]:
        """Extract mappings from FrameNet data."""
        mappings = {}
        frames = framenet_data.get('frames', {})
        
        for frame_name, frame_data in frames.items():
            frame_mappings = frame_data.get('mappings', {})
            for target_corpus, target_mappings in frame_mappings.items():
                if target_corpus not in mappings:
                    mappings[target_corpus] = []
                mappings[target_corpus].extend(target_mappings)
                
        return mappings
        
    def _extract_propbank_mappings(self, propbank_data: Dict) -> Dict[str, List]:
        """Extract mappings from PropBank data."""
        mappings = {}
        predicates = propbank_data.get('predicates', {})
        
        for pred_lemma, pred_data in predicates.items():
            pred_mappings = pred_data.get('mappings', {})
            for target_corpus, target_mappings in pred_mappings.items():
                if target_corpus not in mappings:
                    mappings[target_corpus] = []
                mappings[target_corpus].extend(target_mappings)
                
        return mappings
        
    def _extract_all_cross_corpus_mappings(self) -> Dict[str, Any]:
        """Extract all cross-corpus mappings from loaded corpora."""
        all_mappings = {}
        
        for corpus_name in self.loaded_corpora:
            corpus_mappings = self._extract_resource_mappings(corpus_name)
            if corpus_mappings:
                all_mappings[corpus_name] = corpus_mappings
                
        return all_mappings
    
    def __str__(self) -> str:
        """String representation of ExportManager."""
        return f"ExportManager(corpora={len(self.loaded_corpora)}, formats={list(self.format_handlers.keys())})"