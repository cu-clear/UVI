"""
Cross-Corpus Navigation Example

This script demonstrates the cross-corpus integration capabilities of the UVI package,
showing how to navigate between different linguistic corpora and discover semantic
relationships across resources.

Features demonstrated:
- Cross-corpus lemma mapping
- Semantic relationship discovery
- Cross-reference validation
- Multi-corpus semantic analysis
- Relationship path finding
- Cross-corpus data correlation
"""

import sys
from pathlib import Path
import json
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, Presentation


def demo_basic_cross_corpus_navigation():
    """Demonstrate basic cross-corpus navigation capabilities."""
    print("="*70)
    print("BASIC CROSS-CORPUS NAVIGATION")
    print("="*70)
    
    corpora_path = Path(__file__).parent.parent / 'corpora'
    uvi = UVI(str(corpora_path), load_all=False)
    
    # Show available corpora for navigation
    corpus_paths = uvi.get_corpus_paths()
    loaded_corpora = uvi.get_loaded_corpora()
    
    print(f"Available corpora for navigation:")
    for corpus, path in corpus_paths.items():
        status = "✓ LOADED" if corpus in loaded_corpora else "○ AVAILABLE"
        exists = "✓" if Path(path).exists() else "✗"
        print(f"  {exists} {corpus:<15} - {status}")
    
    print(f"\nSupported corpus types: {', '.join(uvi.supported_corpora)}")
    
    return uvi


def demo_cross_reference_search(uvi):
    """Demonstrate cross-reference search between corpora."""
    print("\n" + "="*70)
    print("CROSS-REFERENCE SEARCH")
    print("="*70)
    
    # Test cross-reference mappings between different corpus types
    cross_ref_tests = [
        ('run-51.3.2', 'verbnet', 'framenet'),
        ('eat-39.1', 'verbnet', 'propbank'),
        ('Motion', 'framenet', 'verbnet'),
        ('run.01', 'propbank', 'verbnet'),
        ('walk', 'wordnet', 'verbnet')
    ]
    
    for source_id, source_corpus, target_corpus in cross_ref_tests:
        print(f"\nSearching for cross-references:")
        print(f"  Source: {source_id} in {source_corpus}")
        print(f"  Target: {target_corpus}")
        
        try:
            if hasattr(uvi, 'search_by_cross_reference'):
                results = uvi.search_by_cross_reference(source_id, source_corpus, target_corpus)
                
                print(f"  Result type: {type(results)}")
                if isinstance(results, list):
                    print(f"  Found {len(results)} cross-references")
                    for i, ref in enumerate(results[:3]):  # Show first 3
                        print(f"    {i+1}. {ref}")
                elif isinstance(results, dict):
                    print(f"  Cross-reference data keys: {list(results.keys())}")
                else:
                    print(f"  Cross-reference result: {results}")
                    
            else:
                print("  ⚠ Cross-reference search method not available")
                print("    This feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Cross-reference search failed: {e}")


def demo_semantic_relationship_discovery(uvi):
    """Demonstrate semantic relationship discovery across corpora."""
    print("\n" + "="*70)
    print("SEMANTIC RELATIONSHIP DISCOVERY")
    print("="*70)
    
    # Test semantic relationship finding
    test_entries = [
        ('run-51.3.2', 'verbnet'),
        ('Motion', 'framenet'),
        ('run.01', 'propbank'),
        ('walk', 'wordnet')
    ]
    
    for entry_id, corpus in test_entries:
        print(f"\nDiscovering semantic relationships for:")
        print(f"  Entry: {entry_id} ({corpus})")
        
        try:
            if hasattr(uvi, 'find_semantic_relationships'):
                relationships = uvi.find_semantic_relationships(
                    entry_id, corpus, 
                    relationship_types=['hyponym', 'hypernym', 'synonym', 'similar'],
                    depth=2
                )
                
                print(f"  Relationship result type: {type(relationships)}")
                
                if isinstance(relationships, dict):
                    print(f"  Relationship categories: {list(relationships.keys())}")
                    
                    # Show sample relationships
                    for rel_type, relations in list(relationships.items())[:2]:
                        if relations:
                            print(f"    {rel_type}: {len(relations)} found")
                            for rel in relations[:2]:  # Show first 2
                                print(f"      - {rel}")
                
                elif isinstance(relationships, list):
                    print(f"  Found {len(relationships)} relationships")
                    for rel in relationships[:3]:
                        print(f"    - {rel}")
                        
            else:
                print("  ⚠ Semantic relationship discovery not available")
                print("    This advanced feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Relationship discovery failed: {e}")


def demo_cross_corpus_lemma_analysis(uvi):
    """Demonstrate comprehensive lemma analysis across all corpora."""
    print("\n" + "="*70)
    print("CROSS-CORPUS LEMMA ANALYSIS")
    print("="*70)
    
    test_lemmas = ['run', 'eat', 'think', 'break']
    
    for lemma in test_lemmas:
        print(f"\n{'='*50}")
        print(f"ANALYZING LEMMA: '{lemma}'")
        print(f"{'='*50}")
        
        # Get complete semantic profile
        try:
            if hasattr(uvi, 'get_complete_semantic_profile'):
                profile = uvi.get_complete_semantic_profile(lemma)
                
                print(f"Semantic profile type: {type(profile)}")
                
                if isinstance(profile, dict):
                    print(f"Available data sources: {list(profile.keys())}")
                    
                    # Show data from each corpus if available
                    corpus_data_types = [
                        ('verbnet', 'VerbNet classes'),
                        ('framenet', 'FrameNet frames'),
                        ('propbank', 'PropBank rolesets'),
                        ('wordnet', 'WordNet synsets'),
                        ('ontonotes', 'OntoNotes senses')
                    ]
                    
                    for corpus_key, description in corpus_data_types:
                        if corpus_key in profile:
                            data = profile[corpus_key]
                            print(f"  {description}: {type(data)} ({len(str(data))} chars)")
                            
                            # Show sample data structure
                            if isinstance(data, list) and data:
                                print(f"    Sample entry: {data[0] if len(str(data[0])) < 100 else str(data[0])[:100] + '...'}")
                            elif isinstance(data, dict) and data:
                                sample_key = list(data.keys())[0]
                                print(f"    Sample key: {sample_key}")
                        else:
                            print(f"  {description}: Not available")
                
                else:
                    print(f"Profile data: {profile}")
                    
            else:
                print("⚠ Complete semantic profile method not available")
                
                # Fall back to individual corpus methods
                print("Trying individual corpus methods...")
                
                corpus_methods = [
                    ('get_verbnet_class', f'{lemma}-51.3.2', 'VerbNet'),
                    ('get_framenet_frame', 'Motion', 'FrameNet'),
                    ('get_propbank_frame', lemma, 'PropBank'),
                    ('get_wordnet_synsets', lemma, 'WordNet')
                ]
                
                for method_name, param, corpus_name in corpus_methods:
                    if hasattr(uvi, method_name):
                        try:
                            method = getattr(uvi, method_name)
                            result = method(param) if param else method()
                            print(f"  {corpus_name}: {type(result)} data available")
                        except Exception as e:
                            print(f"  {corpus_name}: {e}")
                    else:
                        print(f"  {corpus_name}: Method {method_name} not available")
                
        except Exception as e:
            print(f"Semantic profile error: {e}")


def demo_relationship_path_finding(uvi):
    """Demonstrate finding semantic paths between entries across corpora."""
    print("\n" + "="*70)
    print("SEMANTIC RELATIONSHIP PATH FINDING")
    print("="*70)
    
    # Test paths between different entries
    path_tests = [
        (('verbnet', 'run-51.3.2'), ('framenet', 'Motion')),
        (('propbank', 'run.01'), ('wordnet', 'run')),
        (('verbnet', 'eat-39.1'), ('framenet', 'Ingestion')),
        (('wordnet', 'walk'), ('verbnet', 'walk-51.3.2'))
    ]
    
    for start_entry, end_entry in path_tests:
        start_corpus, start_id = start_entry
        end_corpus, end_id = end_entry
        
        print(f"\nFinding semantic path:")
        print(f"  From: {start_id} ({start_corpus})")
        print(f"  To:   {end_id} ({end_corpus})")
        
        try:
            if hasattr(uvi, 'trace_semantic_path'):
                paths = uvi.trace_semantic_path(start_entry, end_entry, max_depth=3)
                
                print(f"  Path result type: {type(paths)}")
                
                if isinstance(paths, list):
                    print(f"  Found {len(paths)} possible paths")
                    
                    for i, path in enumerate(paths[:2]):  # Show first 2 paths
                        print(f"    Path {i+1}: {path}")
                        
                elif isinstance(paths, dict):
                    print(f"  Path data: {list(paths.keys())}")
                    
                else:
                    print(f"  Path result: {paths}")
                    
            else:
                print("  ⚠ Semantic path tracing not available")
                print("    This advanced feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Path finding failed: {e}")


def demo_cross_corpus_validation(uvi):
    """Demonstrate cross-corpus data validation."""
    print("\n" + "="*70)
    print("CROSS-CORPUS DATA VALIDATION")
    print("="*70)
    
    # Test validation of cross-references
    validation_tests = [
        ('run-51.3.2', 'verbnet'),
        ('Motion', 'framenet'),
        ('run.01', 'propbank'),
        ('run', 'wordnet')
    ]
    
    for entry_id, source_corpus in validation_tests:
        print(f"\nValidating cross-references for:")
        print(f"  Entry: {entry_id} ({source_corpus})")
        
        try:
            if hasattr(uvi, 'validate_cross_references'):
                validation = uvi.validate_cross_references(entry_id, source_corpus)
                
                print(f"  Validation result type: {type(validation)}")
                
                if isinstance(validation, dict):
                    print(f"  Validation categories: {list(validation.keys())}")
                    
                    # Show validation status
                    for category, status in validation.items():
                        if isinstance(status, bool):
                            status_symbol = "✓" if status else "✗"
                            print(f"    {category}: {status_symbol}")
                        elif isinstance(status, dict):
                            print(f"    {category}: {len(status)} items")
                        else:
                            print(f"    {category}: {status}")
                            
                else:
                    print(f"  Validation result: {validation}")
                    
            else:
                print("  ⚠ Cross-reference validation not available")
                print("    This feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Validation failed: {e}")


def demo_multi_corpus_search_patterns(uvi):
    """Demonstrate searching by patterns across multiple corpora."""
    print("\n" + "="*70)
    print("MULTI-CORPUS PATTERN SEARCH")
    print("="*70)
    
    # Test semantic pattern searches
    pattern_tests = [
        ('themrole', 'Agent', ['verbnet', 'framenet']),
        ('predicate', 'motion', ['verbnet', 'propbank']),
        ('syntactic_frame', 'NP V NP', ['verbnet']),
        ('frame_element', 'Theme', ['framenet']),
        ('semantic_type', 'animate', ['verbnet', 'wordnet'])
    ]
    
    for pattern_type, pattern_value, target_resources in pattern_tests:
        print(f"\nSearching for semantic pattern:")
        print(f"  Pattern type: {pattern_type}")
        print(f"  Pattern value: {pattern_value}")
        print(f"  Target resources: {target_resources}")
        
        try:
            if hasattr(uvi, 'search_by_semantic_pattern'):
                results = uvi.search_by_semantic_pattern(
                    pattern_type, pattern_value, target_resources
                )
                
                print(f"  Search result type: {type(results)}")
                
                if isinstance(results, dict):
                    print(f"  Found matches in: {list(results.keys())}")
                    
                    # Show sample matches
                    for resource, matches in list(results.items())[:2]:
                        if matches:
                            print(f"    {resource}: {len(matches) if isinstance(matches, list) else type(matches)} matches")
                            if isinstance(matches, list):
                                for match in matches[:2]:
                                    print(f"      - {match}")
                                    
                elif isinstance(results, list):
                    print(f"  Found {len(results)} total matches")
                    for result in results[:3]:
                        print(f"    - {result}")
                        
            else:
                print("  ⚠ Semantic pattern search not available")
                print("    This advanced feature may still be in development")
                
        except Exception as e:
            print(f"  ✗ Pattern search failed: {e}")


def demo_cross_corpus_data_correlation(uvi):
    """Demonstrate data correlation analysis across corpora."""
    print("\n" + "="*70)
    print("CROSS-CORPUS DATA CORRELATION")
    print("="*70)
    
    # Analyze correlations between different corpus types
    lemma = 'run'
    
    print(f"Analyzing correlations for lemma: '{lemma}'")
    
    # Try to gather data from different corpora
    corpus_data = {}
    
    # VerbNet data
    try:
        if hasattr(uvi, 'get_verbnet_class'):
            vn_data = uvi.get_verbnet_class('run-51.3.2')
            corpus_data['verbnet'] = vn_data
            print(f"  VerbNet data: {type(vn_data)}")
    except Exception as e:
        print(f"  VerbNet data: {e}")
    
    # FrameNet data
    try:
        if hasattr(uvi, 'get_framenet_frame'):
            fn_data = uvi.get_framenet_frame('Motion')
            corpus_data['framenet'] = fn_data
            print(f"  FrameNet data: {type(fn_data)}")
    except Exception as e:
        print(f"  FrameNet data: {e}")
    
    # PropBank data
    try:
        if hasattr(uvi, 'get_propbank_frame'):
            pb_data = uvi.get_propbank_frame(lemma)
            corpus_data['propbank'] = pb_data
            print(f"  PropBank data: {type(pb_data)}")
    except Exception as e:
        print(f"  PropBank data: {e}")
    
    # WordNet data
    try:
        if hasattr(uvi, 'get_wordnet_synsets'):
            wn_data = uvi.get_wordnet_synsets(lemma, pos='v')
            corpus_data['wordnet'] = wn_data
            print(f"  WordNet data: {type(wn_data)}")
    except Exception as e:
        print(f"  WordNet data: {e}")
    
    # Analyze correlations if we have data
    if len(corpus_data) > 1:
        print(f"\nCorrelation analysis:")
        print(f"  Available data sources: {list(corpus_data.keys())}")
        
        # Look for common semantic features
        common_features = []
        
        for corpus1 in corpus_data:
            for corpus2 in corpus_data:
                if corpus1 != corpus2:
                    print(f"    Comparing {corpus1} ↔ {corpus2}")
                    
                    # This would be where actual correlation analysis happens
                    # For now, just show that we have the framework
                    data1 = corpus_data[corpus1]
                    data2 = corpus_data[corpus2]
                    
                    if isinstance(data1, dict) and isinstance(data2, dict):
                        common_keys = set(data1.keys()) & set(data2.keys())
                        if common_keys:
                            print(f"      Common keys: {list(common_keys)}")
                        else:
                            print(f"      No common keys found")
                    else:
                        print(f"      Data types: {type(data1)} vs {type(data2)}")
    else:
        print(f"\nInsufficient data for correlation analysis ({len(corpus_data)} sources)")


def demo_presentation_integration_for_navigation():
    """Demonstrate Presentation class integration for cross-corpus visualization."""
    print("\n" + "="*70)
    print("PRESENTATION INTEGRATION FOR NAVIGATION")
    print("="*70)
    
    presentation = Presentation()
    
    # Generate colors for different corpora
    corpus_names = ['verbnet', 'framenet', 'propbank', 'wordnet', 'ontonotes', 'bso', 'semnet']
    corpus_colors = presentation.generate_element_colors(corpus_names)
    
    print("Corpus color scheme for visualization:")
    for corpus, color in corpus_colors.items():
        print(f"  {corpus:<12} : {color}")
    
    # Generate colors for semantic roles
    semantic_roles = ['Agent', 'Patient', 'Theme', 'Instrument', 'Location', 'Time']
    role_colors = presentation.generate_element_colors(semantic_roles, seed=42)
    
    print(f"\nSemantic role color scheme:")
    for role, color in role_colors.items():
        print(f"  {role:<12} : {color}")
    
    # Demonstrate unique ID generation for cross-references
    print(f"\nUnique IDs for cross-reference tracking:")
    for i in range(5):
        uid = presentation.generate_unique_id()
        print(f"  Cross-ref-{i+1}: {uid}")
    
    # Demonstrate data formatting for display
    mock_cross_ref_data = {
        'source': {'corpus': 'verbnet', 'id': 'run-51.3.2'},
        'targets': [
            {'corpus': 'framenet', 'id': 'Motion', 'confidence': 0.95},
            {'corpus': 'propbank', 'id': 'run.01', 'confidence': 0.88},
            {'corpus': 'wordnet', 'id': 'run.v.01', 'confidence': 0.92}
        ],
        '_internal_mapping_id': 'map_12345',
        '_system_timestamp': '2024-01-01T00:00:00Z'
    }
    
    print(f"\nData formatting for cross-reference display:")
    print(f"  Original data keys: {list(mock_cross_ref_data.keys())}")
    
    cleaned_data = presentation.strip_object_ids(mock_cross_ref_data)
    print(f"  Cleaned data keys: {list(cleaned_data.keys())}")
    
    display_json = presentation.json_to_display(cleaned_data)
    print(f"  Display JSON length: {len(display_json)} characters")
    print(f"  Display preview: {display_json[:150]}...")


def main():
    """Main cross-corpus navigation demonstration."""
    print("UVI Cross-Corpus Navigation Demonstration")
    print("This demo shows how to navigate between different linguistic corpora")
    print("and discover semantic relationships across resources.")
    
    print("\nNOTE: Some advanced features may show 'not implemented' messages.")
    print("This is expected for features still in development.")
    
    try:
        # Initialize UVI
        uvi = demo_basic_cross_corpus_navigation()
        
        # Run all navigation demonstrations
        demo_cross_reference_search(uvi)
        demo_semantic_relationship_discovery(uvi)
        demo_cross_corpus_lemma_analysis(uvi)
        demo_relationship_path_finding(uvi)
        demo_cross_corpus_validation(uvi)
        demo_multi_corpus_search_patterns(uvi)
        demo_cross_corpus_data_correlation(uvi)
        demo_presentation_integration_for_navigation()
        
        print(f"\n{'='*70}")
        print("CROSS-CORPUS NAVIGATION DEMO COMPLETED")
        print(f"{'='*70}")
        print("This demonstration showed the framework for cross-corpus integration.")
        print("As methods are fully implemented, these features will become fully functional.")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("This may indicate that some core components are not yet fully implemented.")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()