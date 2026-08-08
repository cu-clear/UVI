"""
Complete UVI Usage Demonstration

This script demonstrates all major features of the UVI (Unified Verb Index) package,
showing how to use the integrated corpus access system for comprehensive linguistic 
analysis and cross-corpus navigation.

Features demonstrated:
- Complete corpus loading and initialization
- Cross-corpus lemma search
- Semantic profile generation
- Corpus-specific data retrieval
- Cross-reference validation
- Data export functionality
- Hierarchical class analysis
- Reference data access
"""

import sys
from pathlib import Path
import json
import time

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, Presentation


def demo_initialization():
    """Demonstrate UVI initialization options."""
    print("="*60)
    print("UVI INITIALIZATION DEMO")
    print("="*60)
    
    # Get the corpora path (adjust as needed)
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    print(f"Initializing UVI with corpora path: {corpora_path}")
    
    # Initialize without loading all corpora first
    print("\n1. Quick initialization (load_all=False):")
    start_time = time.time()
    uvi = UVI(str(corpora_path), load_all=False)
    init_time = time.time() - start_time
    print(f"   Initialized in {init_time:.3f} seconds")
    print(f"   Loaded corpora: {uvi.get_loaded_corpora()}")
    
    # Show detected corpus paths
    print("\n2. Detected corpus paths:")
    corpus_paths = uvi.get_corpus_paths()
    for corpus, path in corpus_paths.items():
        status = "✓" if Path(path).exists() else "✗"
        print(f"   {status} {corpus}: {path}")
    
    return uvi


def demo_corpus_loading(uvi):
    """Demonstrate corpus loading capabilities."""
    print("\n" + "="*60)
    print("CORPUS LOADING DEMO")
    print("="*60)
    
    # Show supported corpora
    print("Supported corpora types:")
    for corpus in uvi.supported_corpora:
        print(f"   • {corpus}")
    
    # Try to load specific corpora
    print("\nLoading individual corpora:")
    test_corpora = ['verbnet', 'framenet', 'wordnet']
    
    for corpus_name in test_corpora:
        try:
            print(f"\nAttempting to load {corpus_name}...")
            uvi._load_corpus(corpus_name)
            
            if corpus_name in uvi.loaded_corpora:
                print(f"   ✓ Successfully loaded {corpus_name}")
            else:
                print(f"   ⚠ {corpus_name} not loaded (files may not exist)")
                
        except Exception as e:
            print(f"   ✗ Error loading {corpus_name}: {e}")
    
    print(f"\nCurrently loaded corpora: {list(uvi.loaded_corpora)}")


def demo_search_functionality(uvi):
    """Demonstrate search and query capabilities."""
    print("\n" + "="*60)
    print("SEARCH FUNCTIONALITY DEMO")
    print("="*60)
    
    # Test lemma search
    test_lemmas = ['run', 'walk', 'eat', 'think']
    
    for lemma in test_lemmas:
        print(f"\nSearching for lemma: '{lemma}'")
        try:
            # Try the main search method
            results = uvi.search_lemmas([lemma], logic='or')
            print(f"   Search results type: {type(results)}")
            if isinstance(results, dict) and results:
                print(f"   Found data in: {list(results.keys())}")
            else:
                print("   No results or method not fully implemented")
        except Exception as e:
            print(f"   Search error: {e}")
            print("   (This is expected if the method is not fully implemented)")
    
    # Test attribute search
    print("\nTesting attribute search:")
    attribute_types = ['themrole', 'predicate', 'frame_element']
    
    for attr_type in attribute_types:
        try:
            print(f"\nSearching by attribute type: {attr_type}")
            results = uvi.search_by_attribute(attr_type, 'Agent')
            print(f"   Results: {type(results)}")
        except Exception as e:
            print(f"   Attribute search for {attr_type}: {e}")


def demo_semantic_profiles(uvi):
    """Demonstrate semantic profile generation."""
    print("\n" + "="*60)
    print("SEMANTIC PROFILE DEMO")
    print("="*60)
    
    test_lemmas = ['run', 'give', 'break']
    
    for lemma in test_lemmas:
        print(f"\nGenerating semantic profile for: '{lemma}'")
        try:
            profile = uvi.get_complete_semantic_profile(lemma)
            print(f"   Profile type: {type(profile)}")
            
            if isinstance(profile, dict):
                print(f"   Profile keys: {list(profile.keys())}")
                # Show sample data if available
                for key, value in list(profile.items())[:3]:  # Show first 3 items
                    print(f"     {key}: {type(value)} ({len(str(value))} chars)")
            
        except Exception as e:
            print(f"   Profile generation error: {e}")
            print("   (Expected if method not fully implemented)")


def demo_corpus_specific_retrieval(uvi):
    """Demonstrate corpus-specific data retrieval."""
    print("\n" + "="*60)
    print("CORPUS-SPECIFIC RETRIEVAL DEMO")
    print("="*60)
    
    # Test VerbNet methods
    print("\n1. VerbNet Class Retrieval:")
    try:
        vn_class = uvi.get_verbnet_class('run-51.3.2')
        print(f"   VerbNet class result: {type(vn_class)}")
    except Exception as e:
        print(f"   VerbNet retrieval: {e}")
    
    # Test FrameNet methods
    print("\n2. FrameNet Frame Retrieval:")
    try:
        fn_frame = uvi.get_framenet_frame('Motion')
        print(f"   FrameNet frame result: {type(fn_frame)}")
    except Exception as e:
        print(f"   FrameNet retrieval: {e}")
    
    # Test PropBank methods
    print("\n3. PropBank Frame Retrieval:")
    try:
        pb_frame = uvi.get_propbank_frame('run')
        print(f"   PropBank frame result: {type(pb_frame)}")
    except Exception as e:
        print(f"   PropBank retrieval: {e}")
    
    # Test WordNet methods
    print("\n4. WordNet Synsets Retrieval:")
    try:
        wn_synsets = uvi.get_wordnet_synsets('run', pos='v')
        print(f"   WordNet synsets result: {type(wn_synsets)}")
    except Exception as e:
        print(f"   WordNet retrieval: {e}")


def demo_reference_data(uvi):
    """Demonstrate reference data access."""
    print("\n" + "="*60)
    print("REFERENCE DATA DEMO")
    print("="*60)
    
    reference_methods = [
        ('get_references', 'All references'),
        ('get_themrole_references', 'Thematic roles'),
        ('get_predicate_references', 'Predicates'),
        ('get_verb_specific_features', 'Verb-specific features'),
        ('get_syntactic_restrictions', 'Syntactic restrictions'),
        ('get_selectional_restrictions', 'Selectional restrictions')
    ]
    
    for method_name, description in reference_methods:
        print(f"\n{description}:")
        try:
            if hasattr(uvi, method_name):
                method = getattr(uvi, method_name)
                result = method()
                
                print(f"   Result type: {type(result)}")
                if isinstance(result, (list, dict)):
                    print(f"   Count: {len(result)}")
                    
                    # Show sample data
                    if isinstance(result, list) and result:
                        print(f"   Sample: {result[:3] if len(result) > 3 else result}")
                    elif isinstance(result, dict) and result:
                        sample_keys = list(result.keys())[:3]
                        print(f"   Sample keys: {sample_keys}")
                        
            else:
                print(f"   Method {method_name} not available")
                
        except Exception as e:
            print(f"   Error accessing {description}: {e}")


def demo_class_hierarchy(uvi):
    """Demonstrate class hierarchy methods."""
    print("\n" + "="*60)
    print("CLASS HIERARCHY DEMO")
    print("="*60)
    
    hierarchy_methods = [
        ('get_class_hierarchy_by_name', 'Hierarchy by name'),
        ('get_class_hierarchy_by_id', 'Hierarchy by ID'),
    ]
    
    for method_name, description in hierarchy_methods:
        print(f"\n{description}:")
        try:
            if hasattr(uvi, method_name):
                method = getattr(uvi, method_name)
                result = method()
                
                print(f"   Result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"   Top-level keys: {list(result.keys())[:5]}")
                    
            else:
                print(f"   Method {method_name} not available")
                
        except Exception as e:
            print(f"   Error with {description}: {e}")
    
    # Test specific class hierarchy
    print(f"\nSpecific class hierarchy:")
    try:
        if hasattr(uvi, 'get_full_class_hierarchy'):
            hierarchy = uvi.get_full_class_hierarchy('run-51.3.2')
            print(f"   Full hierarchy result: {type(hierarchy)}")
        else:
            print("   Method get_full_class_hierarchy not available")
    except Exception as e:
        print(f"   Full hierarchy error: {e}")


def demo_cross_corpus_integration(uvi):
    """Demonstrate cross-corpus integration features."""
    print("\n" + "="*60)
    print("CROSS-CORPUS INTEGRATION DEMO")
    print("="*60)
    
    # Test cross-reference search
    print("\n1. Cross-reference search:")
    try:
        if hasattr(uvi, 'search_by_cross_reference'):
            cross_refs = uvi.search_by_cross_reference('run-51.3.2', 'verbnet', 'framenet')
            print(f"   Cross-reference result: {type(cross_refs)}")
        else:
            print("   Cross-reference method not available")
    except Exception as e:
        print(f"   Cross-reference error: {e}")
    
    # Test semantic relationships
    print("\n2. Semantic relationships:")
    try:
        if hasattr(uvi, 'find_semantic_relationships'):
            relationships = uvi.find_semantic_relationships('run-51.3.2', 'verbnet')
            print(f"   Semantic relationships result: {type(relationships)}")
        else:
            print("   Semantic relationships method not available")
    except Exception as e:
        print(f"   Semantic relationships error: {e}")
    
    # Test cross-reference validation
    print("\n3. Cross-reference validation:")
    try:
        if hasattr(uvi, 'validate_cross_references'):
            validation = uvi.validate_cross_references('run-51.3.2', 'verbnet')
            print(f"   Validation result: {type(validation)}")
        else:
            print("   Validation method not available")
    except Exception as e:
        print(f"   Validation error: {e}")


def demo_data_export(uvi):
    """Demonstrate data export functionality."""
    print("\n" + "="*60)
    print("DATA EXPORT DEMO")
    print("="*60)
    
    # Test different export formats
    export_formats = ['json', 'xml', 'csv']
    
    for format_type in export_formats:
        print(f"\nExporting in {format_type.upper()} format:")
        try:
            if hasattr(uvi, 'export_resources'):
                export_result = uvi.export_resources(format=format_type)
                print(f"   Export result type: {type(export_result)}")
                print(f"   Export length: {len(export_result)} characters")
                
                # Show preview of exported data
                preview = export_result[:200] if len(export_result) > 200 else export_result
                print(f"   Preview: {repr(preview)}...")
                
            else:
                print(f"   Export method not available")
                
        except Exception as e:
            print(f"   Export error in {format_type}: {e}")
    
    # Test semantic profile export
    print(f"\nSemantic profile export:")
    try:
        if hasattr(uvi, 'export_semantic_profile'):
            profile_export = uvi.export_semantic_profile('run', format='json')
            print(f"   Profile export result: {type(profile_export)}")
        else:
            print("   Semantic profile export method not available")
    except Exception as e:
        print(f"   Profile export error: {e}")


def demo_presentation_integration():
    """Demonstrate Presentation class integration."""
    print("\n" + "="*60)
    print("PRESENTATION INTEGRATION DEMO")
    print("="*60)
    
    presentation = Presentation()
    
    print("1. Unique ID generation:")
    for i in range(3):
        uid = presentation.generate_unique_id()
        print(f"   ID {i+1}: {uid}")
    
    print("\n2. Element color generation:")
    elements = ['ARG0', 'ARG1', 'ARG2', 'ARGM-TMP', 'ARGM-LOC']
    colors = presentation.generate_element_colors(elements)
    for elem, color in colors.items():
        print(f"   {elem}: {color}")
    
    print("\n3. Data formatting:")
    sample_data = {'key1': 'value1', 'key2': [1, 2, 3], '_internal_id': '12345'}
    cleaned = presentation.strip_object_ids(sample_data)
    print(f"   Original: {sample_data}")
    print(f"   Cleaned: {cleaned}")
    
    print("\n4. JSON display formatting:")
    display_json = presentation.json_to_display(sample_data)
    print(f"   Display JSON: {display_json[:100]}...")


def demo_performance_characteristics(uvi):
    """Demonstrate performance characteristics."""
    print("\n" + "="*60)
    print("PERFORMANCE CHARACTERISTICS DEMO")
    print("="*60)
    
    # Test initialization performance
    print("1. Initialization performance:")
    start_time = time.time()
    temp_uvi = UVI(uvi.corpora_path, load_all=False)
    init_time = time.time() - start_time
    print(f"   Fast initialization: {init_time:.3f} seconds")
    
    # Test search performance
    print("\n2. Search performance:")
    search_terms = ['run', 'walk', 'eat', 'think', 'break']
    
    start_time = time.time()
    for term in search_terms:
        try:
            results = uvi.search_lemmas([term])
            # Just test the call, don't process results
        except Exception:
            pass  # Expected for unimplemented methods
    
    search_time = time.time() - start_time
    print(f"   Searched {len(search_terms)} terms in {search_time:.3f} seconds")
    
    # Test corpus path detection performance
    print("\n3. Corpus path detection performance:")
    start_time = time.time()
    corpus_paths = uvi.get_corpus_paths()
    detection_time = time.time() - start_time
    print(f"   Detected {len(corpus_paths)} corpus paths in {detection_time:.3f} seconds")


def demo_error_handling_and_recovery():
    """Demonstrate error handling and recovery scenarios."""
    print("\n" + "="*60)
    print("ERROR HANDLING AND RECOVERY DEMO")
    print("="*60)
    
    # Test with invalid path
    print("1. Invalid corpus path handling:")
    try:
        invalid_uvi = UVI('/nonexistent/path/to/corpora')
        print("   ✓ Invalid path handled gracefully")
        print(f"   Loaded corpora: {invalid_uvi.get_loaded_corpora()}")
    except Exception as e:
        print(f"   ✗ Exception with invalid path: {e}")
    
    # Test with empty search
    print("\n2. Empty search handling:")
    uvi = UVI('temp_dir', load_all=False)
    try:
        empty_results = uvi.search_lemmas([])
        print(f"   ✓ Empty search handled: {type(empty_results)}")
    except Exception as e:
        print(f"   Empty search exception: {e}")
    
    # Test with invalid method parameters
    print("\n3. Invalid parameter handling:")
    try:
        if hasattr(uvi, 'get_verbnet_class'):
            invalid_class = uvi.get_verbnet_class('invalid-class-id-12345')
            print(f"   ✓ Invalid class ID handled: {type(invalid_class)}")
    except Exception as e:
        print(f"   Invalid class ID exception: {e}")


def main():
    """Main demonstration function."""
    print("UVI (Unified Verb Index) Complete Usage Demonstration")
    print("This demo shows all major features and capabilities of the UVI package.")
    print("\nNote: Some features may show 'not implemented' errors - this is expected")
    print("for methods that are still in development.")
    
    try:
        # Initialize UVI
        uvi = demo_initialization()
        
        # Run all demonstrations
        demo_corpus_loading(uvi)
        demo_search_functionality(uvi)
        demo_semantic_profiles(uvi)
        demo_corpus_specific_retrieval(uvi)
        demo_reference_data(uvi)
        demo_class_hierarchy(uvi)
        demo_cross_corpus_integration(uvi)
        demo_data_export(uvi)
        demo_presentation_integration()
        demo_performance_characteristics(uvi)
        demo_error_handling_and_recovery()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("All major UVI features have been demonstrated.")
        print("Check the output above for feature availability and performance metrics.")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("This may indicate that some core components are not yet fully implemented.")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()