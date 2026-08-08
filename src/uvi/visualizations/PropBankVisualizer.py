"""
Interactive PropBank Graph Visualization.

This module contains the PropBankVisualizer class that provides interactive
PropBank semantic graph visualizations with hover, click, and zoom functionality.
"""

from .InteractiveVisualizer import InteractiveVisualizer


class PropBankVisualizer(InteractiveVisualizer):
    """Interactive PropBank graph visualization with hover, click, and zoom functionality."""
    
    def __init__(self, G, hierarchy, title="PropBank Predicate-Argument Structure"):
        super().__init__(G, hierarchy, title)
    
    def get_dag_node_color(self, node):
        """Get color for a node based on PropBank node type."""
        # Check if node has type information
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'predicate')
        
        # Different colors for different PropBank node types
        if node_type == 'role':
            return 'lightcoral'   # Semantic roles get coral color
        elif node_type == 'roleset':
            return 'lightblue'    # Rolesets get blue color
        elif node_type == 'example':
            return 'lightgreen'   # Examples get green color
        elif node_type == 'alias':
            return 'lightyellow'  # Aliases get yellow color
        else:
            return 'lightsteelblue'  # Predicates get steel blue color
    
    def get_node_info(self, node):
        """Get detailed information about a PropBank node."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        predicate_info = data.get('predicate_info', {})
        node_type = predicate_info.get('node_type', 'predicate')
        
        # Different display format for different PropBank node types
        if node_type == 'role':
            info = [f"Semantic Role: {predicate_info.get('name', node)}"]
            info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
            info.append(f"Role Number: {predicate_info.get('role_number', 'Unknown')}")
            info.append(f"Function: {predicate_info.get('function', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            description = predicate_info.get('description', '')
            if description and len(description.strip()) > 0:
                if len(description) > 100:
                    description = description[:97] + "..."
                info.append(f"Description: {description}")
                
            # Add VerbNet classes if available
            vnroles = predicate_info.get('vnroles', [])
            if vnroles:
                if len(vnroles) <= 3:
                    info.append(f"VN Classes: {', '.join(vnroles)}")
                else:
                    info.append(f"VN Classes: {len(vnroles)} classes")
                    
        elif node_type == 'roleset':
            info = [f"Roleset: {predicate_info.get('name', node)}"]
            info.append(f"ID: {predicate_info.get('id', 'Unknown')}")
            info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            # Show role count
            roles = predicate_info.get('roles', [])
            if roles:
                info.append(f"Roles: {len(roles)} semantic roles")
            
            # Show example count
            examples = predicate_info.get('examples', [])
            if examples:
                info.append(f"Examples: {len(examples)} annotated examples")
            
            # Add description/note if available
            note = predicate_info.get('note', '')
            if note and len(note.strip()) > 0:
                if len(note) > 80:
                    note = note[:77] + "..."
                info.append(f"Note: {note}")
                
        elif node_type == 'example':
            info = [f"Example: {predicate_info.get('name', node)}"]
            info.append(f"Roleset: {predicate_info.get('roleset', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            # Show text snippet
            text = predicate_info.get('text', '')
            if text and len(text.strip()) > 0:
                if len(text) > 120:
                    text = text[:117] + "..."
                info.append(f"Text: {text}")
            
            # Show argument count
            arguments = predicate_info.get('arguments', [])
            if arguments:
                info.append(f"Arguments: {len(arguments)} marked arguments")
                
        elif node_type == 'alias':
            info = [f"Alias: {predicate_info.get('name', node)}"]
            info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
            info.append(f"Type: {predicate_info.get('pos', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
        else:
            # Predicate node
            info = [f"Predicate: {node}"]
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
            
            # Add lemma if different from node name
            lemma = predicate_info.get('lemma', '')
            if lemma and lemma != node:
                info.append(f"Lemma: {lemma}")
        
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
        return 'propbank'
    
    def create_dag_legend(self):
        """Create legend elements for PropBank DAG visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightsteelblue', label='Predicates'),
            Patch(facecolor='lightblue', label='Rolesets'),
            Patch(facecolor='lightcoral', label='Semantic Roles'),
            Patch(facecolor='lightgreen', label='Examples'),
            Patch(facecolor='lightyellow', label='Aliases')
        ]