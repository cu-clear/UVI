"""
Interactive FrameNet Graph Visualization.

This module contains the InteractiveFrameNetGraph class that provides interactive
FrameNet semantic graph visualizations with hover, click, and zoom functionality.
"""

from .InteractiveVisualizer import InteractiveVisualizer


class FrameNetVisualizer(InteractiveVisualizer):
    """Interactive FrameNet graph visualization with hover, click, and zoom functionality."""
    
    def __init__(self, G, hierarchy, title="FrameNet Frame Hierarchy"):
        super().__init__(G, hierarchy, title)
    
    def get_dag_node_color(self, node):
        """Get color for a node based on FrameNet node type."""
        # Check if node has type information
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'frame')
        
        # Different colors for different FrameNet node types
        if node_type == 'lexical_unit':
            return 'lightyellow'  # Lexical units get yellow color
        elif node_type == 'frame_element':
            return 'lightpink'    # Frame elements get pink color
        else:
            return 'lightblue'    # All frames get single blue color
    
    def get_node_info(self, node):
        """Get detailed information about a FrameNet node."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        frame_info = data.get('frame_info', {})
        node_type = frame_info.get('node_type', 'frame')
        
        # Different display format for different FrameNet node types
        if node_type == 'lexical_unit':
            info = [f"Lexical Unit: {frame_info.get('name', node)}"]
            info.append(f"Frame: {frame_info.get('frame', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            info.append(f"POS: {frame_info.get('pos', 'Unknown')}")
            
            definition = frame_info.get('definition', '')
            if definition and len(definition.strip()) > 0:
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
        elif node_type == 'frame_element':
            info = [f"Frame Element: {frame_info.get('name', node)}"]
            info.append(f"Frame: {frame_info.get('frame', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            info.append(f"Core Type: {frame_info.get('core_type', 'Unknown')}")
            info.append(f"ID: {frame_info.get('id', 'Unknown')}")
            
            definition = frame_info.get('definition', '')
            if definition and len(definition.strip()) > 0:
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
        else:
            # Frame node
            info = [f"Frame: {node}"]
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            parents = data.get('parents', [])
            if parents:
                # Limit parents display to avoid overly long tooltips
                if len(parents) <= 3:
                    info.append(f"Parents: {', '.join(parents)}")
                elif len(parents) <= 6:
                    info.append(f"Parents: {', '.join(parents[:3])}")
                    info.append(f"  ... and {len(parents)-3} more")
                else:
                    # For nodes with many parents, just show count
                    info.append(f"Parents: {len(parents)} parent nodes")
            
            children = data.get('children', [])
            if children:
                # Limit children display to avoid overly long tooltips
                if len(children) <= 3:
                    info.append(f"Children: {', '.join(children)}")
                elif len(children) <= 6:
                    info.append(f"Children: {', '.join(children[:3])}")
                    info.append(f"  ... and {len(children)-3} more")
                else:
                    # For nodes with many children, just show count
                    info.append(f"Children: {len(children)} child nodes")
            
            # Add frame definition if available
            definition = frame_info.get('definition', '')
            if definition and len(definition.strip()) > 0:
                # Truncate long definitions for tooltip readability
                if len(definition) > 80:
                    definition = definition[:77] + "..."
                info.append(f"Definition: {definition}")
        
        # Join and ensure tooltip doesn't become too long overall
        result = '\n'.join(info)
        if len(result) > 300:
            # If tooltip is still too long, truncate and add notice
            lines = result.split('\n')
            truncated_lines = []
            char_count = 0
            
            for line in lines:
                if char_count + len(line) + 1 <= 280:  # Leave room for truncation notice
                    truncated_lines.append(line)
                    char_count += len(line) + 1
                else:
                    truncated_lines.append("... (tooltip truncated)")
                    break
            
            result = '\n'.join(truncated_lines)
        
        return result
    
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
        return 'framenet'
    
    def create_dag_legend(self):
        """Create legend elements for FrameNet DAG visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='Frame'),
            Patch(facecolor='lightyellow', label='Lexical Units'),
            Patch(facecolor='lightpink', label='Frame Elements')
        ]