"""
VerbNet Semantic Graph Example.

A simple interactive visualization of VerbNet's verb class hierarchies
and their member verbs using NetworkX and matplotlib.

This example demonstrates how to:
1. Load VerbNet data using UVI
2. Display VerbNet verb classes, subclasses, and member verbs
3. Create an interactive graph visualization with hover tooltips and clickable nodes

Usage:
    python vn_graph.py

Features:
- Hover over nodes to see verb class details
- Click nodes to select and highlight them  
- Use toolbar to zoom and pan
- Click 'Save PNG' to export current view
- DAG layout optimized for hierarchical verb class data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.graph.VerbNetGraphBuilder import VerbNetGraphBuilder
from uvi.visualizations.VerbNetVisualizer import VerbNetVisualizer

# Import NetworkX and Matplotlib
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def main():
    """Main function for VerbNet semantic graph visualization."""
    print("=" * 50)
    print("VerbNet Verb Class Hierarchy Demo")
    print("=" * 50)
    
    # Initialize UVI and load VerbNet
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading VerbNet from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        uvi._load_corpus('verbnet')
        
        corpus_info = uvi.get_corpus_info()
        if not corpus_info.get('verbnet', {}).get('loaded', False):
            print("ERROR: VerbNet corpus not loaded")
            return
        
        print("VerbNet loaded successfully!")
        
        # Get VerbNet data
        verbnet_data = uvi.corpora_data['verbnet']
        vn_classes = verbnet_data.get('classes', {})
        print(f"Found {len(vn_classes)} VerbNet classes")
        
        # Create semantic graph using specialized VerbNet builder
        graph_builder = VerbNetGraphBuilder()
        G, hierarchy = graph_builder.create_verbnet_graph(
            verbnet_data, 
            num_classes=8,                    # Number of top-level classes to show
            max_subclasses_per_class=3,       # Max subclasses per class
            include_members=True,              # Show member verbs
            max_members_per_class=4            # Max member verbs per class
        )
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        print(f"\nCreating interactive visualization...")
        print("Instructions:")
        print("- Hover over nodes to see verb class details")
        print("- Click on nodes to select and highlight them")
        print("- Use toolbar to zoom and pan")
        print("- Click 'Save PNG' to export current view")
        print("- Close window when finished")
        
        # Create interactive visualization using specialized VerbNet visualizer
        interactive_graph = VerbNetVisualizer(
            G, hierarchy, "VerbNet Verb Class Hierarchy"
        )
        
        fig = interactive_graph.create_interactive_plot()
        plt.show()
        
        print("\n" + "=" * 50)
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure VerbNet data is available in the corpora directory")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()