#!/usr/bin/env python3
"""
Example usage of Presentation and CorpusMonitor classes.

This script demonstrates how to use the new Presentation and CorpusMonitor
classes for formatting corpus data and monitoring file changes.
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path so we can import uvi
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, Presentation, CorpusMonitor


def demo_presentation():
    """Demonstrate the Presentation class functionality."""
    print("=== Presentation Class Demo ===")
    
    # Initialize presentation formatter
    presenter = Presentation()
    
    # Demo 1: Generate unique IDs
    print("\n1. Generating unique IDs:")
    for i in range(3):
        unique_id = presenter.generate_unique_id()
        print(f"   ID {i+1}: {unique_id}")
    
    # Demo 2: Element colors
    print("\n2. Generating element colors:")
    elements = ['ARG0', 'ARG1', 'ARG2', 'PRED', 'THEME', 'AGENT']
    colors = presenter.generate_element_colors(elements, seed=42)
    for element, color in colors.items():
        print(f"   {element}: {color}")
    
    # Demo 3: Format thematic role display
    print("\n3. Formatting thematic role:")
    themrole_data = {
        'name': 'Agent',
        'type': 'animate',
        'selectional_restrictions': ['+animate', '+concrete']
    }
    formatted = presenter.format_themrole_display(themrole_data)
    print(f"   Formatted: {formatted}")
    
    # Demo 4: Format predicate display
    print("\n4. Formatting predicate:")
    predicate_data = {
        'name': 'motion',
        'args': ['Theme', 'Goal'],
        'description': 'Represents motion from one location to another'
    }
    formatted = presenter.format_predicate_display(predicate_data)
    print(f"   Formatted: {formatted}")
    
    # Demo 5: JSON to display
    print("\n5. Converting data to display JSON:")
    sample_data = {
        'class_id': 'run-51.3.2',
        '_internal_id': 123,
        'members': ['run', 'jog', 'sprint'],
        'object_id': 'mongo_obj_456'
    }
    clean_json = presenter.json_to_display(sample_data)
    print(f"   Clean JSON: {clean_json}")
    
    # Demo 6: PropBank example formatting
    print("\n6. Formatting PropBank example:")
    example = {
        'text': 'John ran quickly to the store',
        'args': [
            {'text': 'John', 'type': 'ARG0'},
            {'text': 'quickly', 'type': 'ARGM-MNR'},
            {'text': 'to the store', 'type': 'ARG4'}
        ]
    }
    formatted_example = presenter.format_propbank_example(example)
    print(f"   Original: {example['text']}")
    print(f"   Colored: {formatted_example.get('colored_text', 'N/A')}")


def demo_corpus_monitor():
    """Demonstrate the CorpusMonitor class functionality."""
    print("\n=== CorpusMonitor Class Demo ===")
    
    # For demo purposes, create a mock corpus loader
    class MockCorpusLoader:
        def load_corpus(self, corpus_type):
            print(f"   Mock: Loading {corpus_type} corpus")
            time.sleep(0.1)  # Simulate loading time
            return {'status': 'loaded', 'corpus': corpus_type}
        
        def rebuild_corpus(self, corpus_type):
            print(f"   Mock: Rebuilding {corpus_type} corpus")
            time.sleep(0.2)  # Simulate rebuild time
            return True
    
    # Initialize monitor with mock loader
    mock_loader = MockCorpusLoader()
    monitor = CorpusMonitor(mock_loader)
    
    # Demo 1: Configure watch paths
    print("\n1. Configuring watch paths:")
    corpora_path = Path(__file__).parent.parent / 'corpora'
    watch_paths = monitor.set_watch_paths(
        verbnet_path=str(corpora_path / 'verbnet'),
        framenet_path=str(corpora_path / 'framenet'),
        reference_docs_path=str(corpora_path / 'reference_docs')
    )
    for corpus, path in watch_paths.items():
        print(f"   {corpus}: {path}")
    
    # Demo 2: Configure rebuild strategy
    print("\n2. Setting rebuild strategy:")
    strategy = monitor.set_rebuild_strategy('batch', batch_timeout=30)
    print(f"   Strategy: {strategy}")
    
    # Demo 3: Manual rebuild trigger
    print("\n3. Triggering manual rebuild:")
    result = monitor.trigger_rebuild('verbnet', 'Manual demo rebuild')
    print(f"   Result: Success={result['success']}, Duration={result['duration']:.3f}s")
    
    # Demo 4: Batch rebuild
    print("\n4. Triggering batch rebuild:")
    batch_result = monitor.batch_rebuild(['verbnet', 'framenet'])
    print(f"   Batch success: {batch_result['total_success']}")
    print(f"   Total duration: {batch_result['duration']:.3f}s")
    
    # Demo 5: Get logs
    print("\n5. Recent events:")
    recent_events = monitor.get_change_log(limit=5)
    for event in recent_events[-3:]:  # Show last 3 events
        print(f"   {event['timestamp']}: {event['event_type']}")
    
    # Demo 6: Monitoring status
    print(f"\n6. Monitoring status: {monitor.is_monitoring()}")
    
    # Demo 7: Error recovery configuration
    print("\n7. Configuring error recovery:")
    error_config = monitor.set_error_recovery_strategy(max_retries=2, retry_delay=5)
    print(f"   Config: {error_config}")


def demo_integration():
    """Demonstrate integration between UVI, Presentation, and CorpusMonitor."""
    print("\n=== Integration Demo ===")
    
    try:
        # Initialize UVI
        corpora_path = Path(__file__).parent.parent / 'corpora'
        print(f"\n1. Initializing UVI with corpora path: {corpora_path}")
        
        # Note: This will only work if UVI class is implemented
        # For now, we'll create a mock
        class MockUVI:
            def get_verbnet_class(self, class_id, **kwargs):
                return {
                    'class_id': class_id,
                    'members': ['run', 'jog', 'sprint'],
                    'frames': [
                        {'description': 'Agent runs to Goal'},
                        {'description': 'Agent runs from Source'}
                    ]
                }
        
        uvi = MockUVI()
        presenter = Presentation()
        
        # Demo integrated usage
        print("\n2. Using Presentation with UVI data:")
        class_data = uvi.get_verbnet_class('run-51.3.2')
        if class_data:
            html = presenter.generate_sanitized_class_html('run-51.3.2', uvi)
            print(f"   Generated HTML length: {len(html)} characters")
            print(f"   HTML preview: {html[:200]}...")
        
        print("\n3. Integration complete!")
        
    except Exception as e:
        print(f"   Integration demo error: {str(e)}")
        print("   This is expected if UVI class is not fully implemented yet.")


def main():
    """Main demonstration function."""
    print("UVI Presentation and CorpusMonitor Demo")
    print("=" * 50)
    
    try:
        demo_presentation()
        demo_corpus_monitor()
        demo_integration()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()