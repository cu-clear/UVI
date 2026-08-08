"""
Integrated example showing UVI and CorpusLoader working together.

This example demonstrates how to use both the UVI main class and the
CorpusLoader class to access linguistic corpora data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, CorpusLoader


def main():
    print("=" * 60)
    print("UVI Integrated Example")
    print("=" * 60)
    
    # Initialize with corpora path
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    print(f"\nCorpora path: {corpora_path}")
    
    # Method 1: Using CorpusLoader directly
    print("\n1. Using CorpusLoader directly:")
    loader = CorpusLoader(str(corpora_path))
    
    # Load specific corpus
    if 'verbnet' in loader.corpus_paths:
        verbnet_data = loader.load_corpus('verbnet')
        classes_count = len(verbnet_data.get('classes', {}))
        print(f"   Loaded VerbNet: {classes_count} classes")
        
        # Show sample class data
        classes = verbnet_data.get('classes', {})
        if classes:
            sample_class_id = list(classes.keys())[0]
            sample_class = classes[sample_class_id]
            print(f"   Sample class: {sample_class_id}")
            print(f"     Members: {len(sample_class.get('members', []))}")
            print(f"     Frames: {len(sample_class.get('frames', []))}")
    
    # Method 2: Using UVI class (which may use CorpusLoader internally)
    print("\n2. Using UVI class:")
    try:
        uvi = UVI(str(corpora_path), load_all=False)  # Don't auto-load all
        
        # Show detected corpora
        corpus_info = uvi.get_corpus_info()
        loaded_count = sum(1 for info in corpus_info.values() if info['loaded'])
        available_count = sum(1 for info in corpus_info.values() if info['path'] != 'Not found')
        
        print(f"   Available corpora: {available_count}")
        print(f"   Loaded corpora: {loaded_count}")
        
        # Show what's available
        for corpus_name, info in corpus_info.items():
            status = "loaded" if info['loaded'] else ("available" if info['path'] != 'Not found' else "not found")
            print(f"     {corpus_name}: {status}")
            
    except Exception as e:
        print(f"   UVI initialization failed: {e}")
    
    # Method 3: Show reference collections from CorpusLoader
    print("\n3. Reference Collections from CorpusLoader:")
    if 'reference_docs' in loader.corpus_paths:
        ref_data = loader.load_corpus('reference_docs')
        stats = ref_data.get('statistics', {})
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Method 4: Show data format examples
    print("\n4. Data Format Examples:")
    
    # VerbNet class structure
    if 'verbnet' in loader.loaded_data:
        verbnet_data = loader.loaded_data['verbnet']
        classes = verbnet_data.get('classes', {})
        if classes:
            sample_class_id = list(classes.keys())[0]
            sample_class = classes[sample_class_id]
            
            print(f"   VerbNet class structure for {sample_class_id}:")
            print(f"     Keys: {list(sample_class.keys())}")
            
            members = sample_class.get('members', [])
            if members:
                print(f"     First member: {members[0]}")
            
            frames = sample_class.get('frames', [])
            if frames:
                print(f"     First frame keys: {list(frames[0].keys())}")
    
    # FrameNet frame structure
    if 'framenet' in loader.corpus_paths:
        try:
            framenet_data = loader.load_corpus('framenet')
            frames = framenet_data.get('frames', {})
            if frames:
                sample_frame_name = list(frames.keys())[0]
                sample_frame = frames[sample_frame_name]
                
                print(f"   FrameNet frame structure for {sample_frame_name}:")
                print(f"     Keys: {list(sample_frame.keys())}")
                
                if sample_frame.get('definition'):
                    definition = sample_frame['definition']
                    if len(definition) > 80:
                        definition = definition[:77] + "..."
                    print(f"     Definition: {definition}")
        except Exception as e:
            print(f"   FrameNet loading failed: {e}")
    
    print("\n" + "=" * 60)
    print("Integration example completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()