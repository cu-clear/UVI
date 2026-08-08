"""
Integrated VerbNet-FrameNet-WordNet-PropBank Semantic Graph Example.

This example demonstrates the integration of VerbNet, FrameNet, WordNet, and PropBank corpora
through their semantic mappings and cross-references. It shows how verb classes from
VerbNet connect to semantic frames in FrameNet, word senses in WordNet, and predicate
structures in PropBank.

This example demonstrates how to:
1. Load VerbNet, FrameNet, WordNet, and PropBank data using UVI
2. Create an integrated semantic graph linking the four corpora
3. Visualize cross-corpus mappings and relationships
4. Explore semantic connections between verb classes, frames, synsets, and predicates

Usage:
    python vn_fn_wn_graph.py

Features:
- Interactive visualization with corpus-specific node shapes and colors
- Hover over nodes to see detailed corpus information
- Click nodes to select and highlight connected semantic networks
- Cross-corpus connection visualization with different edge styles
- PropBank predicate-argument structures with distinct visual styling
- Save functionality to export the integrated graph
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.graph.VerbNetFrameNetWordNetGraphBuilder import VerbNetFrameNetWordNetGraphBuilder
from uvi.graph.PropBankGraphBuilder import PropBankGraphBuilder
from uvi.visualizations.UVIVisualizer import UVIVisualizer

# Import required packages
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def main():
    """Main function for integrated VerbNet-FrameNet-WordNet-PropBank visualization."""
    print("=" * 70)
    print("Integrated VerbNet-FrameNet-WordNet-PropBank Semantic Graph Demo")
    print("=" * 70)
    
    # Initialize UVI and load all four corpora
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading corpora from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        
        # Load the three corpora
        print("Loading VerbNet...")
        uvi._load_corpus('verbnet')
        
        print("Loading FrameNet...")
        uvi._load_corpus('framenet')
        
        print("Loading WordNet...")
        uvi._load_corpus('wordnet')
        
        print("Loading PropBank...")
        uvi._load_corpus('propbank')
        
        # Check that all corpora loaded successfully
        corpus_info = uvi.get_corpus_info()
        required_corpora = ['verbnet', 'framenet', 'wordnet', 'propbank']
        missing_corpora = []
        
        for corpus in required_corpora:
            if not corpus_info.get(corpus, {}).get('loaded', False):
                missing_corpora.append(corpus)
        
        if missing_corpora:
            print(f"ERROR: The following corpora failed to load: {', '.join(missing_corpora)}")
            print("Make sure all corpus data is available in the corpora directory")
            print("Note: PropBank is optional - the demo will work with VerbNet, FrameNet, and WordNet")
            # Only return if core corpora are missing
            core_missing = [c for c in missing_corpora if c in ['verbnet', 'framenet', 'wordnet']]
            if core_missing:
                return
        
        print("All corpora loaded successfully!")
        
        # Get corpus data
        verbnet_data = uvi.corpora_data['verbnet']
        framenet_data = uvi.corpora_data['framenet']
        wordnet_data = uvi.corpora_data['wordnet']
        propbank_data = uvi.corpora_data['propbank']
        
        # Display corpus statistics
        vn_classes = len(verbnet_data.get('classes', {}))
        fn_frames = len(framenet_data.get('frames', {}))
        wn_synsets = sum(len(s) for s in wordnet_data.get('synsets', {}).values())
        pb_predicates = len(propbank_data.get('predicates', {}))
        
        print(f"\nCorpus Statistics:")
        print(f"  VerbNet classes: {vn_classes}")
        print(f"  FrameNet frames: {fn_frames}")
        print(f"  WordNet synsets: {wn_synsets}")
        print(f"  PropBank predicates: {pb_predicates}")
        
        # Create integrated semantic graph
        print(f"\nCreating integrated semantic graph...")
        
        # First create the VerbNet-FrameNet-WordNet integrated graph
        vn_fn_wn_builder = VerbNetFrameNetWordNetGraphBuilder()
        G, hierarchy = vn_fn_wn_builder.create_integrated_graph(
            verbnet_data=verbnet_data,
            framenet_data=framenet_data,
            wordnet_data=wordnet_data,
            num_vn_classes=6,              # Number of VerbNet classes to include
            max_fn_frames_per_class=2,     # Max FrameNet frames per VerbNet class
            max_wn_synsets_per_class=2,    # Max WordNet synsets per VerbNet class
            include_members=True,          # Include member verbs
            max_members_per_class=3        # Max member verbs per class
        )
        
        # Add PropBank nodes to the integrated graph
        if G is not None and pb_predicates > 0:
            print(f"Adding PropBank predicates to integrated graph...")
            pb_builder = PropBankGraphBuilder()
            
            # Create a small PropBank subgraph
            pb_G, pb_hierarchy = pb_builder.create_propbank_graph(
                propbank_data,
                num_predicates=4,
                max_rolesets_per_predicate=2,
                max_roles_per_roleset=2,
                max_examples_per_roleset=1,
                include_aliases=True
            )
            
            if pb_G is not None and pb_G.number_of_nodes() > 0:
                print(f"  Adding {pb_G.number_of_nodes()} PropBank nodes...")
                
                # Add PropBank nodes to the main graph with PB: prefix
                for node in pb_G.nodes(data=True):
                    pb_node_id = f"PB:{node[0]}"
                    G.add_node(pb_node_id, **node[1])
                
                # Add PropBank edges
                for edge in pb_G.edges(data=True):
                    pb_source = f"PB:{edge[0]}"
                    pb_target = f"PB:{edge[1]}"
                    G.add_edge(pb_source, pb_target, **edge[2])
                
                # Add PropBank hierarchy data with PB: prefix
                for node, data in pb_hierarchy.items():
                    pb_node_id = f"PB:{node}"
                    hierarchy[pb_node_id] = data.copy()
                    
                    # Update parent/child references to include PB: prefix
                    if 'parents' in hierarchy[pb_node_id]:
                        hierarchy[pb_node_id]['parents'] = [f"PB:{p}" for p in hierarchy[pb_node_id]['parents']]
                    if 'children' in hierarchy[pb_node_id]:
                        hierarchy[pb_node_id]['children'] = [f"PB:{c}" for c in hierarchy[pb_node_id]['children']]
                
                print(f"  Successfully integrated PropBank data!")
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create integrated visualization graph")
            return
        
        print(f"\nCreated integrated graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Create interactive visualization
        print(f"\nLaunching interactive visualization...")
        print("\nVisualization Features:")
        print("- Blue squares: VerbNet verb classes")
        print("- Purple triangles: FrameNet semantic frames")  
        print("- Green diamonds: WordNet synsets")
        print("- Light steel blue hexagons: PropBank predicates")
        print("- Light blue pentagons: PropBank rolesets") 
        print("- Light coral triangles (down): PropBank semantic roles")
        print("- Light green triangles (left): PropBank examples")
        print("- Light yellow triangles (right): PropBank aliases")
        print("- Orange circles: Member verbs")
        print("- Different edge styles show cross-corpus connections")
        print("\nInteraction Instructions:")
        print("- Hover over nodes to see detailed corpus information")
        print("- Click on nodes to select and highlight semantic networks")
        print("- Use toolbar to zoom and pan around the graph")
        print("- Click 'Save PNG' to export current view")
        print("- Close window when finished exploring")
        
        # Create specialized integrated visualizer
        visualizer = UVIVisualizer(
            G, hierarchy, "Integrated VerbNet-FrameNet-WordNet-PropBank Semantic Graph"
        )
        
        fig = visualizer.create_interactive_plot()
        plt.show()
        
        print("\n" + "=" * 70)
        print("Integrated semantic graph demo complete!")
        print("\nThis demo showed how VerbNet verb classes connect to:")
        print("- FrameNet semantic frames through shared conceptual structures")
        print("- WordNet synsets through lexical semantic mappings")
        print("- PropBank predicates through predicate-argument structures")
        print("- Member verbs that bridge all four linguistic resources")
        print("- Cross-corpus semantic networks for comprehensive verb analysis")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure VerbNet, FrameNet, WordNet, and PropBank data are available in the corpora directory")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()