"""
UVI Data Export Examples

This script demonstrates all data export capabilities of the UVI package,
showing how to export linguistic data in different formats and for different
use cases.

Features demonstrated:
- Multi-format data export (JSON, XML, CSV)
- Selective corpus export
- Semantic profile export
- Cross-corpus mapping export
- Filtered and targeted exports
- Export validation and formatting
"""

import sys
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import csv
import io
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, Presentation


def demo_basic_export_formats():
    """Demonstrate basic export functionality in different formats."""
    print("="*70)
    print("BASIC DATA EXPORT FORMATS")
    print("="*70)
    
    corpora_path = Path(__file__).parent.parent / 'corpora'
    uvi = UVI(str(corpora_path), load_all=False)
    
    # Test different export formats
    export_formats = ['json', 'xml', 'csv']
    
    for format_type in export_formats:
        print(f"\n{format_type.upper()} Export:")
        print("-" * 30)
        
        try:
            if hasattr(uvi, 'export_resources'):
                # Try basic export
                export_result = uvi.export_resources(format=format_type)
                
                print(f"  Export successful: {type(export_result)}")
                print(f"  Data length: {len(export_result)} characters")
                
                # Show preview based on format
                preview_length = 200
                if len(export_result) > preview_length:
                    preview = export_result[:preview_length] + "..."
                else:
                    preview = export_result
                
                print(f"  Preview: {repr(preview)}")
                
                # Validate format if possible
                if format_type == 'json' and export_result.strip():
                    try:
                        json_data = json.loads(export_result)
                        print(f"  ✓ Valid JSON with {len(json_data) if isinstance(json_data, (dict, list)) else 'N/A'} top-level items")
                    except json.JSONDecodeError as e:
                        print(f"  ⚠ JSON validation failed: {e}")
                
                elif format_type == 'xml' and export_result.strip():
                    try:
                        xml_root = ET.fromstring(export_result)
                        print(f"  ✓ Valid XML with root element: <{xml_root.tag}>")
                    except ET.ParseError as e:
                        print(f"  ⚠ XML validation failed: {e}")
                
                elif format_type == 'csv' and export_result.strip():
                    try:
                        csv_reader = csv.reader(io.StringIO(export_result))
                        rows = list(csv_reader)
                        print(f"  ✓ Valid CSV with {len(rows)} rows")
                        if rows:
                            print(f"    Header: {rows[0] if len(rows) > 0 else 'N/A'}")
                    except csv.Error as e:
                        print(f"  ⚠ CSV validation failed: {e}")
                        
            else:
                print("  ⚠ Export method not available")
                print("    This feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Export failed: {e}")
    
    return uvi


def demo_selective_corpus_export(uvi):
    """Demonstrate selective corpus export with filtering."""
    print("\n" + "="*70)
    print("SELECTIVE CORPUS EXPORT")
    print("="*70)
    
    # Test exporting specific corpora
    corpus_selections = [
        ['verbnet'],
        ['framenet', 'propbank'],
        ['wordnet', 'ontonotes'],
        ['verbnet', 'framenet', 'propbank', 'wordnet'],  # Core linguistic resources
        ['bso', 'semnet', 'reference_docs']  # Supporting resources
    ]
    
    for selection in corpus_selections:
        print(f"\nExporting corpora: {', '.join(selection)}")
        print("-" * 50)
        
        for format_type in ['json', 'xml']:
            try:
                if hasattr(uvi, 'export_resources'):
                    export_result = uvi.export_resources(
                        include_resources=selection,
                        format=format_type,
                        include_mappings=True
                    )
                    
                    print(f"  {format_type.upper()}: {len(export_result)} chars")
                    
                    # Show structure for JSON
                    if format_type == 'json' and export_result.strip():
                        try:
                            data = json.loads(export_result)
                            if isinstance(data, dict):
                                print(f"    Exported sections: {list(data.keys())}")
                        except json.JSONDecodeError:
                            print(f"    JSON parsing failed (may be empty)")
                            
                else:
                    print(f"  {format_type.upper()}: Export method not available")
                    
            except Exception as e:
                print(f"  {format_type.upper()}: Export error - {e}")


def demo_semantic_profile_export(uvi):
    """Demonstrate semantic profile export for specific lemmas."""
    print("\n" + "="*70)
    print("SEMANTIC PROFILE EXPORT")
    print("="*70)
    
    # Test semantic profile export for different lemmas
    test_lemmas = ['run', 'eat', 'think', 'break', 'give']
    
    for lemma in test_lemmas:
        print(f"\nExporting semantic profile for: '{lemma}'")
        print("-" * 40)
        
        try:
            if hasattr(uvi, 'export_semantic_profile'):
                # Test different formats
                for format_type in ['json', 'xml']:
                    try:
                        profile_export = uvi.export_semantic_profile(lemma, format=format_type)
                        print(f"  {format_type.upper()} profile: {len(profile_export)} characters")
                        
                        # Show preview
                        preview = profile_export[:150] if len(profile_export) > 150 else profile_export
                        print(f"    Preview: {repr(preview)}...")
                        
                        # Validate format
                        if format_type == 'json' and profile_export.strip():
                            try:
                                profile_data = json.loads(profile_export)
                                print(f"    ✓ Valid JSON profile")
                                if isinstance(profile_data, dict):
                                    print(f"    Profile sections: {list(profile_data.keys())}")
                            except json.JSONDecodeError:
                                print(f"    ⚠ JSON validation failed")
                                
                    except Exception as e:
                        print(f"  {format_type.upper()} profile export: {e}")
                        
            else:
                print("  ⚠ Semantic profile export method not available")
                
                # Try alternative approach using complete semantic profile
                if hasattr(uvi, 'get_complete_semantic_profile'):
                    print("  Trying alternative semantic profile method...")
                    try:
                        profile = uvi.get_complete_semantic_profile(lemma)
                        
                        # Convert to JSON manually
                        json_export = json.dumps(profile, indent=2, default=str)
                        print(f"    Manual JSON export: {len(json_export)} characters")
                        
                        # Show structure
                        if isinstance(profile, dict):
                            print(f"    Profile sections: {list(profile.keys())}")
                            
                    except Exception as e:
                        print(f"    Alternative profile method: {e}")
                        
        except Exception as e:
            print(f"  Profile export failed: {e}")


def demo_cross_corpus_mapping_export(uvi):
    """Demonstrate export of cross-corpus mappings."""
    print("\n" + "="*70)
    print("CROSS-CORPUS MAPPING EXPORT")
    print("="*70)
    
    try:
        if hasattr(uvi, 'export_cross_corpus_mappings'):
            print("Exporting comprehensive cross-corpus mappings...")
            
            mappings = uvi.export_cross_corpus_mappings()
            
            print(f"  Mapping result type: {type(mappings)}")
            
            if isinstance(mappings, dict):
                print(f"  Mapping categories: {list(mappings.keys())}")
                
                # Show sample mapping data
                for category, mapping_data in list(mappings.items())[:3]:
                    print(f"    {category}:")
                    if isinstance(mapping_data, dict):
                        print(f"      {len(mapping_data)} mappings")
                        # Show sample mapping
                        for key, value in list(mapping_data.items())[:2]:
                            print(f"        {key} -> {value}")
                    elif isinstance(mapping_data, list):
                        print(f"      {len(mapping_data)} mapping entries")
                        if mapping_data:
                            print(f"        Sample: {mapping_data[0]}")
                    else:
                        print(f"      Data type: {type(mapping_data)}")
                        
                # Export mappings in different formats
                print(f"\nExporting mappings in different formats:")
                
                # JSON format
                try:
                    json_mappings = json.dumps(mappings, indent=2, default=str)
                    print(f"  JSON format: {len(json_mappings)} characters")
                    
                    # Save to file
                    output_path = Path(__file__).parent / 'cross_corpus_mappings.json'
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(json_mappings)
                    print(f"    Saved to: {output_path}")
                    
                except Exception as e:
                    print(f"  JSON export error: {e}")
                
                # CSV format for tabular mappings
                try:
                    csv_output = io.StringIO()
                    csv_writer = csv.writer(csv_output)
                    
                    # Write header
                    csv_writer.writerow(['Source Corpus', 'Source ID', 'Target Corpus', 'Target ID', 'Confidence'])
                    
                    # Convert mappings to CSV rows
                    row_count = 0
                    for category, mapping_data in mappings.items():
                        if isinstance(mapping_data, dict):
                            for source, targets in list(mapping_data.items())[:10]:  # Limit for demo
                                if isinstance(targets, list):
                                    for target in targets:
                                        if isinstance(target, dict):
                                            csv_writer.writerow([
                                                category.split('_')[0] if '_' in category else category,
                                                source,
                                                target.get('corpus', 'unknown'),
                                                target.get('id', target.get('target_id', 'unknown')),
                                                target.get('confidence', 'N/A')
                                            ])
                                            row_count += 1
                    
                    csv_content = csv_output.getvalue()
                    print(f"  CSV format: {len(csv_content)} characters, {row_count} rows")
                    
                    # Save CSV
                    csv_path = Path(__file__).parent / 'cross_corpus_mappings.csv'
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    print(f"    Saved to: {csv_path}")
                    
                except Exception as e:
                    print(f"  CSV export error: {e}")
                    
            else:
                print(f"  Mapping data: {mappings}")
                
        else:
            print("⚠ Cross-corpus mapping export method not available")
            print("  This advanced feature may still be in development")
            
    except Exception as e:
        print(f"Cross-corpus mapping export failed: {e}")


def demo_filtered_export(uvi):
    """Demonstrate filtered and targeted export functionality."""
    print("\n" + "="*70)
    print("FILTERED AND TARGETED EXPORT")
    print("="*70)
    
    # Test exports with different filtering criteria
    filter_tests = [
        {
            'name': 'Motion verbs only',
            'criteria': {'semantic_class': 'motion', 'pos': 'verb'}
        },
        {
            'name': 'High-frequency lemmas',
            'criteria': {'frequency': '>1000'}
        },
        {
            'name': 'Cross-referenced entries only',
            'criteria': {'has_cross_references': True}
        },
        {
            'name': 'VerbNet classes with examples',
            'criteria': {'corpus': 'verbnet', 'has_examples': True}
        }
    ]
    
    for test in filter_tests:
        print(f"\nFiltered export: {test['name']}")
        print(f"Criteria: {test['criteria']}")
        print("-" * 50)
        
        # Since specific filtering methods may not be implemented,
        # demonstrate the framework and expected behavior
        
        try:
            # Check if there's a general filtering method
            if hasattr(uvi, 'export_filtered_resources'):
                result = uvi.export_filtered_resources(
                    filters=test['criteria'],
                    format='json'
                )
                print(f"  Filtered export: {len(result)} characters")
                
            else:
                print("  ⚠ Filtered export method not available")
                print("    Would use filtering criteria to select relevant data")
                
                # Demonstrate how this would work conceptually
                if test['criteria'].get('corpus') == 'verbnet':
                    print("    -> Would export only VerbNet data")
                elif test['criteria'].get('semantic_class') == 'motion':
                    print("    -> Would search for motion-related entries")
                elif test['criteria'].get('has_cross_references'):
                    print("    -> Would include only entries with mappings")
                    
        except Exception as e:
            print(f"  Filtered export error: {e}")


def demo_export_validation_and_quality(uvi):
    """Demonstrate export validation and quality checking."""
    print("\n" + "="*70)
    print("EXPORT VALIDATION AND QUALITY")
    print("="*70)
    
    # Test export with validation
    validation_tests = [
        ('json', 'JSON schema validation'),
        ('xml', 'XML schema validation'),
        ('csv', 'CSV format validation')
    ]
    
    for format_type, description in validation_tests:
        print(f"\n{description}:")
        print("-" * 40)
        
        try:
            if hasattr(uvi, 'export_resources'):
                export_data = uvi.export_resources(format=format_type)
                
                print(f"  Export size: {len(export_data)} characters")
                
                # Perform format-specific validation
                if format_type == 'json':
                    validation_result = validate_json_export(export_data)
                elif format_type == 'xml':
                    validation_result = validate_xml_export(export_data)
                elif format_type == 'csv':
                    validation_result = validate_csv_export(export_data)
                
                print(f"  Validation result: {validation_result}")
                
            else:
                print("  Export method not available")
                
        except Exception as e:
            print(f"  Validation test failed: {e}")


def validate_json_export(json_data: str) -> Dict[str, Any]:
    """Validate JSON export data."""
    try:
        parsed = json.loads(json_data)
        
        validation = {
            'valid': True,
            'type': type(parsed).__name__,
            'size': len(str(parsed)),
            'structure': 'valid'
        }
        
        if isinstance(parsed, dict):
            validation['keys'] = list(parsed.keys())[:5]  # First 5 keys
            validation['key_count'] = len(parsed)
        elif isinstance(parsed, list):
            validation['item_count'] = len(parsed)
            if parsed:
                validation['item_type'] = type(parsed[0]).__name__
        
        return validation
        
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'error': str(e),
            'error_type': 'JSON parsing error'
        }


def validate_xml_export(xml_data: str) -> Dict[str, Any]:
    """Validate XML export data."""
    try:
        root = ET.fromstring(xml_data)
        
        return {
            'valid': True,
            'root_tag': root.tag,
            'child_count': len(root),
            'has_attributes': bool(root.attrib),
            'depth': get_xml_depth(root)
        }
        
    except ET.ParseError as e:
        return {
            'valid': False,
            'error': str(e),
            'error_type': 'XML parsing error'
        }


def validate_csv_export(csv_data: str) -> Dict[str, Any]:
    """Validate CSV export data."""
    try:
        csv_reader = csv.reader(io.StringIO(csv_data))
        rows = list(csv_reader)
        
        validation = {
            'valid': True,
            'row_count': len(rows),
            'column_count': len(rows[0]) if rows else 0,
            'has_header': True if rows else False
        }
        
        if rows:
            validation['header'] = rows[0]
            
            # Check consistency
            column_counts = [len(row) for row in rows]
            validation['consistent_columns'] = len(set(column_counts)) == 1
            
        return validation
        
    except csv.Error as e:
        return {
            'valid': False,
            'error': str(e),
            'error_type': 'CSV parsing error'
        }


def get_xml_depth(element, depth=0):
    """Calculate the maximum depth of an XML element tree."""
    if not list(element):
        return depth
    return max(get_xml_depth(child, depth + 1) for child in element)


def demo_export_file_operations():
    """Demonstrate saving exports to files."""
    print("\n" + "="*70)
    print("EXPORT FILE OPERATIONS")
    print("="*70)
    
    corpora_path = Path(__file__).parent.parent / 'corpora'
    uvi = UVI(str(corpora_path), load_all=False)
    
    # Create output directory
    output_dir = Path(__file__).parent / 'export_output'
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    # Export to different file formats
    export_tasks = [
        ('uvi_complete_export.json', 'json', None),
        ('uvi_verbnet_only.xml', 'xml', ['verbnet']),
        ('uvi_core_corpora.json', 'json', ['verbnet', 'framenet', 'propbank']),
        ('uvi_mappings.csv', 'csv', None)
    ]
    
    for filename, format_type, corpus_filter in export_tasks:
        print(f"\nExporting to: {filename}")
        print(f"  Format: {format_type}")
        print(f"  Corpora: {corpus_filter or 'all'}")
        
        try:
            if hasattr(uvi, 'export_resources'):
                # Perform export
                if corpus_filter:
                    export_data = uvi.export_resources(
                        include_resources=corpus_filter,
                        format=format_type
                    )
                else:
                    export_data = uvi.export_resources(format=format_type)
                
                # Save to file
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                
                print(f"  ✓ Saved: {len(export_data)} characters")
                print(f"  Path: {file_path}")
                
                # Validate saved file
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    print(f"  File size: {file_size} bytes")
                
            else:
                print("  ⚠ Export method not available")
                
        except Exception as e:
            print(f"  ✗ Export failed: {e}")
    
    print(f"\nExport files saved to: {output_dir}")
    if output_dir.exists():
        files = list(output_dir.glob('*'))
        print(f"Created {len(files)} export files:")
        for file_path in files:
            size = file_path.stat().st_size
            print(f"  - {file_path.name}: {size} bytes")


def demo_presentation_integration_for_export():
    """Demonstrate Presentation class integration for export formatting."""
    print("\n" + "="*70)
    print("PRESENTATION INTEGRATION FOR EXPORT")
    print("="*70)
    
    presentation = Presentation()
    
    # Create sample data for export formatting
    sample_corpus_data = {
        'verbnet_classes': [
            {'id': 'run-51.3.2', 'members': ['run', 'jog', 'sprint']},
            {'id': 'walk-51.3.2', 'members': ['walk', 'stroll', 'march']}
        ],
        'framenet_frames': [
            {'name': 'Motion', 'elements': ['Theme', 'Goal', 'Source']},
            {'name': 'Ingestion', 'elements': ['Ingestor', 'Ingestibles']}
        ],
        '_internal_metadata': {
            'timestamp': '2024-01-01T00:00:00Z',
            'version': '1.0'
        }
    }
    
    print("Sample corpus data for export:")
    print(f"  Keys: {list(sample_corpus_data.keys())}")
    
    # Clean data for export
    cleaned_data = presentation.strip_object_ids(sample_corpus_data)
    print(f"\nCleaned data (internal IDs removed):")
    print(f"  Keys: {list(cleaned_data.keys())}")
    
    # Format for JSON display
    json_display = presentation.json_to_display(cleaned_data)
    print(f"\nJSON display format:")
    print(f"  Length: {len(json_display)} characters")
    print(f"  Preview: {json_display[:200]}...")
    
    # Generate consistent colors for export visualization
    corpus_types = ['verbnet', 'framenet', 'propbank', 'wordnet']
    colors = presentation.generate_element_colors(corpus_types)
    
    print(f"\nColor scheme for export visualization:")
    for corpus, color in colors.items():
        print(f"  {corpus}: {color}")
    
    # Generate unique IDs for export tracking
    print(f"\nUnique export IDs:")
    for i in range(3):
        export_id = presentation.generate_unique_id()
        print(f"  Export-{i+1}: {export_id}")


def main():
    """Main export examples demonstration."""
    print("UVI Data Export Examples")
    print("This demo shows comprehensive data export capabilities")
    print("for the UVI linguistic corpus package.")
    
    print("\nNOTE: Some export features may show 'not implemented' messages.")
    print("This is expected for features still in development.")
    
    try:
        # Initialize UVI
        uvi = demo_basic_export_formats()
        
        # Run all export demonstrations
        demo_selective_corpus_export(uvi)
        demo_semantic_profile_export(uvi)
        demo_cross_corpus_mapping_export(uvi)
        demo_filtered_export(uvi)
        demo_export_validation_and_quality(uvi)
        demo_export_file_operations()
        demo_presentation_integration_for_export()
        
        print(f"\n{'='*70}")
        print("EXPORT EXAMPLES DEMO COMPLETED")
        print(f"{'='*70}")
        print("This demonstration showed the comprehensive export framework.")
        print("Check the 'export_output' directory for generated files.")
        print("As methods are fully implemented, all export features will become functional.")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("This may indicate that some core components are not yet fully implemented.")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()