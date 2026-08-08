"""
Example usage of the CorpusLoader class.

This script demonstrates how to use the CorpusLoader to load and examine
linguistic corpora data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.corpus_loader import CorpusLoader


def main():
    print("=" * 60)
    print("CorpusLoader Example")
    print("=" * 60)
    
    # Initialize CorpusLoader
    corpora_path = Path(__file__).parent.parent / 'corpora'
    loader = CorpusLoader(str(corpora_path))
    
    print(f"\nInitialized CorpusLoader with path: {corpora_path}")
    
    # Show detected corpus paths
    print("\n1. Detected Corpus Paths:")
    paths = loader.get_corpus_paths()
    for corpus_name, path in paths.items():
        print(f"   {corpus_name}: {path}")
    
    # Load all available corpora
    print("\n2. Loading All Available Corpora:")
    loading_results = loader.load_all_corpora()
    
    for corpus_name, result in loading_results.items():
        status = result.get('status', 'unknown')
        if status == 'success':
            load_time = result.get('load_time', 0)
            print(f"   [OK] {corpus_name}: loaded in {load_time:.2f}s")
        elif status == 'error':
            error = result.get('error', 'unknown error')
            print(f"   [ERROR] {corpus_name}: {error}")
        else:
            print(f"   [-] {corpus_name}: {status}")
    
    # Show collection statistics
    print("\n3. Collection Statistics:")
    stats = loader.get_collection_statistics()
    for corpus_name, corpus_stats in stats.items():
        if corpus_name != 'reference_collections':
            if isinstance(corpus_stats, dict) and 'error' not in corpus_stats:
                print(f"   {corpus_name}:")
                for key, value in corpus_stats.items():
                    print(f"     {key}: {value}")
            elif 'error' not in corpus_stats:
                print(f"   {corpus_name}: {corpus_stats}")
    
    # Show reference collections
    if 'reference_collections' in stats:
        print("\n4. Reference Collections Built:")
        ref_stats = stats['reference_collections']
        for collection_name, count in ref_stats.items():
            print(f"   {collection_name}: {count} items")
    
    # Show some sample data if VerbNet is loaded
    if 'verbnet' in loader.loaded_data:
        verbnet_data = loader.loaded_data['verbnet']
        classes = verbnet_data.get('classes', {})
        
        if classes:
            print("\n5. Sample VerbNet Data:")
            # Show first few classes
            sample_classes = list(classes.keys())[:3]
            for class_id in sample_classes:
                class_data = classes[class_id]
                member_count = len(class_data.get('members', []))
                frame_count = len(class_data.get('frames', []))
                print(f"   Class {class_id}:")
                print(f"     Members: {member_count}")
                print(f"     Frames: {frame_count}")
                
                # Show a few members
                members = class_data.get('members', [])[:3]
                if members:
                    member_names = [m.get('name', '') for m in members]
                    print(f"     Sample members: {', '.join(member_names)}")
    
    # Show some sample data if FrameNet is loaded
    if 'framenet' in loader.loaded_data:
        framenet_data = loader.loaded_data['framenet']
        frames = framenet_data.get('frames', {})
        
        if frames:
            print("\n6. Sample FrameNet Data:")
            # Show first few frames
            sample_frames = list(frames.keys())[:3]
            for frame_name in sample_frames:
                frame_data = frames[frame_name]
                lu_count = len(frame_data.get('lexical_units', {}))
                fe_count = len(frame_data.get('frame_elements', {}))
                print(f"   Frame {frame_name}:")
                print(f"     Lexical Units: {lu_count}")
                print(f"     Frame Elements: {fe_count}")
                
                # Show definition if available
                definition = frame_data.get('definition', '')
                if definition:
                    # Truncate long definitions
                    if len(definition) > 100:
                        definition = definition[:97] + "..."
                    print(f"     Definition: {definition}")
    
    # Validate collections
    print("\n7. Collection Validation:")
    validation_results = loader.validate_collections()
    for corpus_name, validation in validation_results.items():
        status = validation.get('status', 'unknown')
        error_count = len(validation.get('errors', []))
        warning_count = len(validation.get('warnings', []))
        
        if status == 'valid':
            print(f"   [OK] {corpus_name}: valid")
        elif status == 'valid_with_warnings':
            print(f"   [WARN] {corpus_name}: valid with {warning_count} warnings")
        elif status == 'invalid':
            print(f"   [ERROR] {corpus_name}: invalid ({error_count} errors)")
        else:
            print(f"   [-] {corpus_name}: {status}")
    
    print("\n" + "=" * 60)
    print("CorpusLoader example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()