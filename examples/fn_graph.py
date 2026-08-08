"""
FrameNet Interactive Semantic Graph Example.

A simple interactive visualization of FrameNet frames using NetworkX and matplotlib.
Since this FrameNet corpus doesn't include frame relations, this example demonstrates
the visualization capabilities using a small subset of actual FrameNet frames
as nodes without hierarchical connections.

This example demonstrates how to:
1. Load FrameNet data using UVI
2. Display actual frame information
3. Create an interactive graph visualization with hover tooltips and clickable nodes

Usage:
    python semantic_graph.py

Features:
- Hover over nodes to see frame details
- Click nodes to select and highlight them
- Use toolbar to zoom and pan
- Spring-force layout
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.visualizations import FrameNetVisualizer
from uvi.graph import FrameNetGraphBuilder

# Import Matplotlib
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install matplotlib")
    print(f"Error: {e}")
    sys.exit(1)



def main():
    """Simple main function for interactive FrameNet visualization."""
    print("=" * 50)
    print("FrameNet Interactive Semantic Graph Demo")
    print("=" * 50)
    
    # Initialize UVI and load FrameNet
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading FrameNet from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        uvi._load_corpus('framenet')
        
        corpus_info = uvi.get_corpus_info()
        if not corpus_info.get('framenet', {}).get('loaded', False):
            print("ERROR: FrameNet corpus not loaded")
            return
        
        print("FrameNet loaded successfully!")
        
        # Get FrameNet data
        framenet_data = uvi.corpora_data['framenet']
        total_frames = len(framenet_data.get('frames', {}))
        print(f"Found {total_frames} frames in FrameNet")
        
        # Create demo graph with actual FrameNet frames, lexical units, and frame elements
        graph_builder = FrameNetGraphBuilder()
        G, hierarchy = graph_builder.create_framenet_graph(
            framenet_data, num_frames=5, max_lus_per_frame=2, max_fes_per_frame=2
        )
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        print(f"\\nCreating interactive visualization...")
        print("Instructions:")
        print("- Hover over nodes to see frame details")
        print("- Click on nodes to select and highlight them")
        print("- Use toolbar to zoom and pan")
        print("- Close window when finished")
        
        # Create interactive visualization
        interactive_graph = FrameNetVisualizer(
            G, hierarchy, "FrameNet Frames Demo"
        )
        
        fig = interactive_graph.create_interactive_plot()
        plt.show()
        
        print("\\n" + "=" * 50)
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure FrameNet data is available in the corpora directory")


if __name__ == '__main__':
    main()