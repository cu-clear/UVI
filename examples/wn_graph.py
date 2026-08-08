"""
WordNet Semantic Graph Example.

A simple interactive visualization of WordNet's top-level ontological categories
and their immediate children using NetworkX and matplotlib.

This example demonstrates how to:
1. Load WordNet data using UVI
2. Display WordNet synsets and their hierarchical relationships
3. Create an interactive graph visualization with hover tooltips and clickable nodes

Usage:
    python wn_graph.py

Features:
- Hover over nodes to see synset details
- Click nodes to select and highlight them  
- Use toolbar to zoom and pan
- Click 'Save PNG' to export current view
- Spring-force layout optimized for hierarchical data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.graph.WordNetGraphBuilder import WordNetGraphBuilder
from uvi.visualizations.WordNetVisualizer import WordNetVisualizer

# Import NetworkX and Matplotlib
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def main():
    """Main function for WordNet semantic graph visualization."""
    print("=" * 50)
    print("WordNet Semantic Graph Demo")
    print("=" * 50)
    
    # Initialize UVI and load WordNet
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading WordNet from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        uvi._load_corpus('wordnet')
        
        corpus_info = uvi.get_corpus_info()
        if not corpus_info.get('wordnet', {}).get('loaded', False):
            print("ERROR: WordNet corpus not loaded")
            return
        
        print("WordNet loaded successfully!")
        
        # Get WordNet data
        wordnet_data = uvi.corpora_data['wordnet']
        noun_synsets = wordnet_data.get('synsets', {}).get('noun', {})
        print(f"Found {len(noun_synsets)} noun synsets")
        
        # Create semantic graph using specialized WordNet builder
        graph_builder = WordNetGraphBuilder()
        G, hierarchy = graph_builder.create_wordnet_graph(
            wordnet_data, num_categories=5, max_children_per_category=3
        )
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        print(f"\nCreating interactive visualization...")
        print("Instructions:")
        print("- Hover over nodes to see synset details")
        print("- Click on nodes to select and highlight them")
        print("- Use toolbar to zoom and pan")
        print("- Click 'Save PNG' to export current view")
        print("- Close window when finished")
        
        # Create interactive visualization using specialized WordNet visualizer
        interactive_graph = WordNetVisualizer(
            G, hierarchy, "WordNet Semantic Categories"
        )
        
        fig = interactive_graph.create_interactive_plot()
        plt.show()
        
        print("\n" + "=" * 50)
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure WordNet data is available in the corpora directory")


if __name__ == '__main__':
    main()