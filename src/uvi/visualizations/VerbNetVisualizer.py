"""
VerbNet Visualizer.

This module contains the VerbNetVisualizer class for creating interactive
VerbNet verb class hierarchy visualizations with specialized coloring and tooltips.
"""

from .InteractiveVisualizer import InteractiveVisualizer


class VerbNetVisualizer(InteractiveVisualizer):
    """Specialized visualizer for VerbNet verb class hierarchies."""
    
    def __init__(self, G, hierarchy, title="VerbNet Verb Class Hierarchy"):
        super().__init__(G, hierarchy, title)
    
    def get_dag_node_color(self, node):
        """Get color for a node based on VerbNet node type."""
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'unknown')
        
        if node == self.selected_node:
            return 'red'  # Highlight selected node
        elif node_type == 'verb_class':
            return 'lightblue'    # Top-level verb classes
        elif node_type == 'verb_subclass':
            return 'lightgreen'   # Subclasses
        elif node_type == 'verb_member':
            return 'lightyellow'  # Member verbs
        else:
            return 'lightgray'    # Unknown nodes
    
    def get_taxonomic_node_color(self, node):
        """Get color for a node based on depth in VerbNet hierarchy."""
        depth = self.G.nodes[node].get('depth', 0)
        node_type = self.G.nodes[node].get('node_type', 'unknown')
        
        if node == self.selected_node:
            return 'red'
        elif node_type == 'verb_member':
            return 'lightyellow'  # Member verbs always yellow
        elif depth == 0:
            return 'lightblue'    # Root verb classes
        elif depth == 1:
            return 'lightgreen'   # Subclasses
        elif depth == 2:
            return 'lightcoral'   # Deeper subclasses
        else:
            return 'wheat'        # Even deeper levels
    
    def get_node_info(self, node):
        """Get detailed information about a VerbNet node."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        
        # Try to find the node info in various possible locations
        node_info = data.get('node_info', data.get('verb_info', {}))
        if not node_info:
            for key in ['frame_info', 'synset_info', 'verb_info']:
                if key in data:
                    node_info = data[key]
                    break
        
        node_type = node_info.get('node_type', 'unknown')
        
        if node_type == 'verb_class':
            info = [f"VerbNet Class: {node}"]
            info.append(f"Class ID: {node_info.get('class_id', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            # Show members
            members = node_info.get('members', [])
            if members:
                if len(members) <= 5:
                    info.append(f"Members: {', '.join(members)}")
                else:
                    info.append(f"Members: {', '.join(members[:3])}")
                    info.append(f"  ... and {len(members)-3} more")
            
            # Show thematic roles
            themroles = node_info.get('themroles', [])
            if themroles:
                if len(themroles) <= 4:
                    info.append(f"Roles: {', '.join(themroles)}")
                else:
                    info.append(f"Roles: {', '.join(themroles[:4])}...")
            
            # Show subclasses
            children = data.get('children', [])
            if children:
                subclass_count = len([c for c in children if 'verb' not in c.lower() or '-' in c])
                if subclass_count > 0:
                    info.append(f"Subclasses: {subclass_count}")
            
            # Show frames
            frames = node_info.get('frames', [])
            if frames:
                info.append(f"Frames: {len(frames)}")
                if frames and len(frames[0]) < 60:
                    info.append(f"  e.g., {frames[0]}")
        
        elif node_type == 'verb_subclass':
            info = [f"VerbNet Subclass: {node}"]
            info.append(f"Class ID: {node_info.get('class_id', 'Unknown')}")
            info.append(f"Parent: {node_info.get('parent_class', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            # Show members
            members = node_info.get('members', [])
            if members:
                if len(members) <= 5:
                    info.append(f"Members: {', '.join(members)}")
                else:
                    info.append(f"Members: {', '.join(members[:3])}...")
                    info.append(f"  ({len(members)} total)")
            
            # Show frames
            frames = node_info.get('frames', [])
            if frames:
                info.append(f"Frames: {len(frames)}")
        
        elif node_type == 'verb_member':
            info = [f"Verb Member: {node}"]
            info.append(f"Lemma: {node_info.get('lemma', node)}")
            info.append(f"Parent Class: {node_info.get('parent_class', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            # Show all parent classes if verb appears in multiple
            parents = data.get('parents', [])
            if len(parents) > 1:
                info.append(f"Also in: {', '.join(parents[1:])}")
        
        else:
            # Unknown node type, show generic info
            info = [f"Node: {node}"]
            info.append(f"Type: {node_type}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            parents = data.get('parents', [])
            if parents:
                info.append(f"Parents: {', '.join(parents)}")
            
            children = data.get('children', [])
            if children:
                if len(children) <= 3:
                    info.append(f"Children: {', '.join(children)}")
                else:
                    info.append(f"Children: {len(children)} nodes")
        
        return '\n'.join(info)
    
    def select_node(self, node):
        """Select a node and highlight it with neighbor greying."""
        self.selected_node = node
        print(f"\n=== Selected Node: {node} ===")
        print(self.get_node_info(node))
        print("=" * 40)
        
        # Use consolidated highlighting from base class
        self._highlight_connected_nodes(node)
    
    def _get_visualizer_type(self):
        """Return visualizer type for configuration purposes."""
        return 'verbnet'
    
    def create_dag_legend(self):
        """Create legend for VerbNet DAG visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='Verb Classes'),
            Patch(facecolor='lightgreen', label='Subclasses'),
            Patch(facecolor='lightyellow', label='Member Verbs')
        ]
    
    def create_taxonomic_legend(self):
        """Create legend for VerbNet taxonomic visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='Root Classes (Depth 0)'),
            Patch(facecolor='lightgreen', label='Subclasses (Depth 1)'),
            Patch(facecolor='lightyellow', label='Member Verbs'),
            Patch(facecolor='lightcoral', label='Deeper Subclasses')
        ]