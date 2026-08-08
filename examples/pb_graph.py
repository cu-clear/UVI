"""
PropBank Semantic Graph Example.

A simple interactive visualization of PropBank's predicate-argument structures
and their semantic roles using NetworkX and matplotlib.

This example demonstrates how to:
1. Load PropBank data using UVI
2. Display PropBank predicates, rolesets, roles, examples, and aliases
3. Create an interactive graph visualization with hover tooltips and clickable nodes

Usage:
    python pb_graph.py

Features:
- Hover over nodes to see predicate-argument structure details
- Click nodes to select and highlight them  
- Use toolbar to zoom and pan
- Click 'Save PNG' to export current view
- DAG layout optimized for hierarchical predicate-argument data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.graph.PropBankGraphBuilder import PropBankGraphBuilder
from uvi.visualizations.PropBankVisualizer import PropBankVisualizer

# Import NetworkX and Matplotlib
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def main():
    """Main function for PropBank semantic graph visualization."""
    print("=" * 50)
    print("PropBank Predicate-Argument Structure Demo")
    print("=" * 50)
    
    # Initialize UVI and load PropBank
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading PropBank from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        uvi._load_corpus('propbank')
        
        corpus_info = uvi.get_corpus_info()
        if not corpus_info.get('propbank', {}).get('loaded', False):
            print("ERROR: PropBank corpus not loaded")
            return
        
        print("PropBank loaded successfully!")
        
        # Get PropBank data
        propbank_data = uvi.corpora_data['propbank']
        pb_predicates = propbank_data.get('predicates', {})
        print(f"Found {len(pb_predicates)} PropBank predicates")
        
        # Create semantic graph using specialized PropBank builder
        graph_builder = PropBankGraphBuilder()
        G, hierarchy = graph_builder.create_propbank_graph(
            propbank_data, 
            num_predicates=6,                      # Number of predicates to show
            max_rolesets_per_predicate=2,          # Max rolesets per predicate
            max_roles_per_roleset=3,               # Max roles per roleset
            max_examples_per_roleset=2,            # Max examples per roleset
            include_aliases=True                   # Include alias nodes
        )
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        print(f"\nCreating interactive visualization...")
        print("Instructions:")
        print("- Hover over nodes to see predicate-argument details")
        print("- Click on nodes to select and highlight them")
        print("- Use toolbar to zoom and pan")
        print("- Click 'Save PNG' to export current view")
        print("- Close window when finished")
        
        # Create interactive visualization using specialized PropBank visualizer
        interactive_graph = PropBankVisualizer(
            G, hierarchy, "PropBank Predicate-Argument Structure"
        )
        
        fig = interactive_graph.create_interactive_plot()
        plt.show()
        
        print("\n" + "=" * 50)
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure PropBank data is available in the corpora directory")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()