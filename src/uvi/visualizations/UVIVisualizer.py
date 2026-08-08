"""
UVI (Unified Verb Index) Visualizer.

This module contains the UVIVisualizer class for creating
interactive visualizations of integrated semantic graphs that link VerbNet,
FrameNet, WordNet, and PropBank corpora.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
import networkx as nx
from typing import Dict, Any, Optional

from .InteractiveVisualizer import InteractiveVisualizer


class UVIVisualizer(InteractiveVisualizer):
    """Unified Verb Index (UVI) visualizer for integrated VerbNet-FrameNet-WordNet-PropBank graphs."""
    
    def __init__(self, G, hierarchy, title="Integrated Semantic Graph"):
        """
        Initialize the integrated visualizer.
        
        Args:
            G: NetworkX DiGraph containing integrated corpus nodes
            hierarchy: Hierarchy data with node information
            title: Title for visualizations
        """
        super().__init__(G, hierarchy, title)
        self.selected_node = None
        self.annotation = None
        self.node_positions = None
        self.ax = None
        self.fig = None
    
    def get_dag_node_color(self, node):
        """Get color for a node based on its corpus type."""
        # Determine corpus from node prefix
        if node.startswith('VN:'):
            return '#4A90E2'  # Blue for VerbNet
        elif node.startswith('FN:'):
            return '#7B68EE'  # Purple for FrameNet
        elif node.startswith('WN:'):
            return '#50C878'  # Green for WordNet
        elif node.startswith('PB:'):
            # PropBank nodes - check node type for specific colors
            node_data = self.G.nodes.get(node, {})
            node_type = node_data.get('node_type', 'predicate')
            if node_type == 'role':
                return '#F08080'  # Light coral for semantic roles
            elif node_type == 'roleset':
                return '#ADD8E6'  # Light blue for rolesets
            elif node_type == 'example':
                return '#90EE90'  # Light green for examples
            elif node_type == 'alias':
                return '#FFFFE0'  # Light yellow for aliases
            else:
                return '#B0C4DE'  # Light steel blue for predicates
        elif node.startswith('VERB:'):
            return '#FFB84D'  # Orange for member verbs
        else:
            return 'lightgray'  # Default
    
    def get_taxonomic_node_color(self, node):
        """Get color for taxonomic visualization based on corpus."""
        # Same as DAG colors for consistency
        return self.get_dag_node_color(node)
    
    def get_node_info(self, node):
        """Get detailed information about a node from any corpus."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        info = []
        
        # Determine node type and corpus
        node_info = None
        for key in ['node_info', 'frame_info', 'synset_info', 'verb_info']:
            if key in data:
                node_info = data[key]
                break
        
        if not node_info:
            return super().get_node_info(node)
        
        node_type = node_info.get('node_type', 'unknown')
        corpus = node_info.get('corpus', '')
        
        # Format based on node type
        if node_type == 'verbnet_class':
            info.append(f"VerbNet Class: {node}")
            info.append(f"Class ID: {node_info.get('class_id', 'Unknown')}")
            
            members = node_info.get('members', [])
            if members:
                if len(members) <= 5:
                    info.append(f"Members: {', '.join(members)}")
                else:
                    info.append(f"Members: {', '.join(members[:3])}... ({len(members)} total)")
            
            themroles = node_info.get('themroles', [])
            if themroles:
                if len(themroles) <= 5:
                    info.append(f"Thematic Roles: {', '.join(themroles)}")
                else:
                    info.append(f"Thematic Roles: {len(themroles)} roles")
        
        elif node_type == 'framenet_frame':
            info.append(f"FrameNet Frame: {node}")
            info.append(f"Frame: {node_info.get('frame_name', 'Unknown')}")
            
            definition = node_info.get('definition', '')
            if definition:
                # Truncate long definitions
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
            
            lexical_units = node_info.get('lexical_units', 0)
            info.append(f"Lexical Units: {lexical_units}")
        
        elif node_type == 'wordnet_synset':
            info.append(f"WordNet Synset: {node}")
            info.append(f"Synset ID: {node_info.get('synset_id', 'Unknown')}")
            
            words = node_info.get('words', [])
            if words:
                if len(words) <= 5:
                    info.append(f"Words: {', '.join(words)}")
                else:
                    info.append(f"Words: {', '.join(words[:3])}... ({len(words)} total)")
            
            definition = node_info.get('definition', '')
            if definition:
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
        
        elif node_type == 'verb_member':
            info.append(f"Member Verb: {node}")
            info.append(f"Lemma: {node_info.get('lemma', 'Unknown')}")
            
            vn_class = node_info.get('verbnet_class', '')
            if vn_class:
                info.append(f"VerbNet Class: {vn_class}")
        
        else:
            # Check for PropBank nodes by prefix
            if node.startswith('PB:'):
                predicate_info = data.get('predicate_info', {})
                pb_node_type = predicate_info.get('node_type', 'predicate')
                
                if pb_node_type == 'role':
                    info = [f"PropBank Role: {predicate_info.get('name', node)}"]
                    info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
                    info.append(f"Role Number: {predicate_info.get('role_number', 'Unknown')}")
                    info.append(f"Function: {predicate_info.get('function', 'Unknown')}")
                    
                    description = predicate_info.get('description', '')
                    if description and len(description.strip()) > 0:
                        if len(description) > 100:
                            description = description[:97] + "..."
                        info.append(f"Description: {description}")
                        
                    vnroles = predicate_info.get('vnroles', [])
                    if vnroles:
                        if len(vnroles) <= 3:
                            info.append(f"VN Classes: {', '.join(vnroles)}")
                        else:
                            info.append(f"VN Classes: {len(vnroles)} classes")
                            
                elif pb_node_type == 'roleset':
                    info = [f"PropBank Roleset: {predicate_info.get('name', node)}"]
                    info.append(f"ID: {predicate_info.get('id', 'Unknown')}")
                    info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
                    
                    roles = predicate_info.get('roles', [])
                    if roles:
                        info.append(f"Roles: {len(roles)} semantic roles")
                    
                    examples = predicate_info.get('examples', [])
                    if examples:
                        info.append(f"Examples: {len(examples)} annotated examples")
                    
                    note = predicate_info.get('note', '')
                    if note and len(note.strip()) > 0:
                        if len(note) > 80:
                            note = note[:77] + "..."
                        info.append(f"Note: {note}")
                        
                elif pb_node_type == 'example':
                    info = [f"PropBank Example: {predicate_info.get('name', node)}"]
                    info.append(f"Roleset: {predicate_info.get('roleset', 'Unknown')}")
                    
                    text = predicate_info.get('text', '')
                    if text and len(text.strip()) > 0:
                        if len(text) > 120:
                            text = text[:117] + "..."
                        info.append(f"Text: {text}")
                    
                    arguments = predicate_info.get('arguments', [])
                    if arguments:
                        info.append(f"Arguments: {len(arguments)} marked arguments")
                        
                elif pb_node_type == 'alias':
                    info = [f"PropBank Alias: {predicate_info.get('name', node)}"]
                    info.append(f"Predicate: {predicate_info.get('predicate', 'Unknown')}")
                    info.append(f"Type: {predicate_info.get('pos', 'Unknown')}")
                    
                else:
                    # PropBank predicate node
                    info = [f"PropBank Predicate: {node}"]
                    lemma = predicate_info.get('lemma', '')
                    if lemma and lemma != node:
                        info.append(f"Lemma: {lemma}")
            else:
                return super().get_node_info(node)
        
        # Add connection information
        parents = data.get('parents', [])
        children = data.get('children', [])
        
        if parents:
            if len(parents) <= 3:
                info.append(f"Connected from: {', '.join(parents)}")
            else:
                info.append(f"Connected from: {len(parents)} nodes")
        
        if children:
            if len(children) <= 3:
                info.append(f"Connected to: {', '.join(children)}")
            else:
                info.append(f"Connected to: {len(children)} nodes")
        
        return '\n'.join(info)
    
    def create_dag_legend(self):
        """Create legend elements for integrated DAG visualization."""
        return [
            mpatches.Patch(facecolor='#4A90E2', label='VerbNet Classes'),
            mpatches.Patch(facecolor='#7B68EE', label='FrameNet Frames'),
            mpatches.Patch(facecolor='#50C878', label='WordNet Synsets'),
            mpatches.Patch(facecolor='#B0C4DE', label='PropBank Predicates'),
            mpatches.Patch(facecolor='#ADD8E6', label='PropBank Rolesets'),
            mpatches.Patch(facecolor='#F08080', label='PropBank Roles'),
            mpatches.Patch(facecolor='#90EE90', label='PropBank Examples'),
            mpatches.Patch(facecolor='#FFFFE0', label='PropBank Aliases'),
            mpatches.Patch(facecolor='#FFB84D', label='Member Verbs'),
            mpatches.Patch(facecolor='lightgray', label='Other Nodes')
        ]
    
    def create_taxonomic_legend(self):
        """Create legend elements for taxonomic visualization."""
        # Same as DAG legend for this integrated view
        return self.create_dag_legend()
    
    def create_interactive_plot(self):
        """Create an interactive matplotlib plot with hover and click functionality."""
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Create layout - use spring layout with adjustments for clarity
        self.node_positions = self.create_dag_layout()
        
        # Draw the graph
        self._draw_graph()
        
        # Add title and legend
        self.ax.set_title(f"{self.title}\n(VerbNet-FrameNet-WordNet Integration)", 
                         fontsize=16, fontweight='bold')
        self.ax.axis('off')
        
        # Add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        # Add interaction instructions
        instructions = (
            "Hover: Show node details | "
            "Click: Select/highlight node | "
            "Toolbar: Zoom/Pan"
        )
        self.fig.text(0.5, 0.02, instructions, ha='center', fontsize=10, color='gray')
        
        # Add corpus labels
        self._add_corpus_labels()
        
        # Set up event handlers
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # save button removed - use matplotlib toolbar for saving
        
        plt.tight_layout()
        return self.fig
    
    def _draw_graph(self):
        """Draw the integrated graph with corpus-specific styling."""
        # Separate nodes by corpus for different styling
        vn_nodes = [n for n in self.G.nodes() if n.startswith('VN:')]
        fn_nodes = [n for n in self.G.nodes() if n.startswith('FN:')]
        wn_nodes = [n for n in self.G.nodes() if n.startswith('WN:')]
        pb_nodes = [n for n in self.G.nodes() if n.startswith('PB:')]
        verb_nodes = [n for n in self.G.nodes() if n.startswith('VERB:')]
        other_nodes = [n for n in self.G.nodes() 
                      if not any(n.startswith(p) for p in ['VN:', 'FN:', 'WN:', 'PB:', 'VERB:'])]
        
        # Draw nodes by corpus with different styles
        if vn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=vn_nodes,
                                 node_color='#4A90E2',
                                 node_size=3000,
                                 node_shape='s',  # Square for VerbNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if fn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=fn_nodes,
                                 node_color='#7B68EE',
                                 node_size=2500,
                                 node_shape='^',  # Triangle for FrameNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if wn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=wn_nodes,
                                 node_color='#50C878',
                                 node_size=2500,
                                 node_shape='d',  # Diamond for WordNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if pb_nodes:
            # Group PropBank nodes by type for different styling
            pb_predicates = [n for n in pb_nodes if self.G.nodes.get(n, {}).get('node_type', 'predicate') == 'predicate']
            pb_rolesets = [n for n in pb_nodes if self.G.nodes.get(n, {}).get('node_type', 'predicate') == 'roleset']
            pb_roles = [n for n in pb_nodes if self.G.nodes.get(n, {}).get('node_type', 'predicate') == 'role']
            pb_examples = [n for n in pb_nodes if self.G.nodes.get(n, {}).get('node_type', 'predicate') == 'example']
            pb_aliases = [n for n in pb_nodes if self.G.nodes.get(n, {}).get('node_type', 'predicate') == 'alias']
            pb_other = [n for n in pb_nodes if n not in pb_predicates + pb_rolesets + pb_roles + pb_examples + pb_aliases]
            
            if pb_predicates:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_predicates,
                                     node_color='#B0C4DE',
                                     node_size=2800,
                                     node_shape='h',  # Hexagon for PropBank predicates
                                     alpha=0.9,
                                     ax=self.ax)
            
            if pb_rolesets:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_rolesets,
                                     node_color='#ADD8E6',
                                     node_size=2300,
                                     node_shape='p',  # Pentagon for PropBank rolesets
                                     alpha=0.9,
                                     ax=self.ax)
            
            if pb_roles:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_roles,
                                     node_color='#F08080',
                                     node_size=2000,
                                     node_shape='v',  # Triangle down for PropBank roles
                                     alpha=0.9,
                                     ax=self.ax)
            
            if pb_examples:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_examples,
                                     node_color='#90EE90',
                                     node_size=1800,
                                     node_shape='<',  # Triangle left for PropBank examples
                                     alpha=0.9,
                                     ax=self.ax)
            
            if pb_aliases:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_aliases,
                                     node_color='#FFFFE0',
                                     node_size=1600,
                                     node_shape='>',  # Triangle right for PropBank aliases
                                     alpha=0.9,
                                     ax=self.ax)
            
            if pb_other:
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=pb_other,
                                     node_color='#B0C4DE',
                                     node_size=2000,
                                     node_shape='h',  # Default to hexagon
                                     alpha=0.9,
                                     ax=self.ax)
        
        if verb_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=verb_nodes,
                                 node_color='#FFB84D',
                                 node_size=1500,
                                 node_shape='o',  # Circle for verbs
                                 alpha=0.9,
                                 ax=self.ax)
        
        if other_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=other_nodes,
                                 node_color='lightgray',
                                 node_size=1500,
                                 alpha=0.7,
                                 ax=self.ax)
        
        # Draw edges with different styles for different connection types
        edge_colors = []
        edge_styles = []
        edge_widths = []
        
        for edge in self.G.edges(data=True):
            source, target, attrs = edge
            relation_type = attrs.get('relation_type', 'default')
            
            # Style based on connection type
            if relation_type == 'semantic_similarity':
                edge_colors.append('purple')
                edge_styles.append(':')  # Dotted for similarity
                edge_widths.append(1.5)
            elif source.startswith('VN:') and target.startswith('FN:'):
                edge_colors.append('blue')
                edge_styles.append('-')  # Solid for VN-FN
                edge_widths.append(2)
            elif source.startswith('VN:') and target.startswith('WN:'):
                edge_colors.append('green')
                edge_styles.append('-')  # Solid for VN-WN
                edge_widths.append(2)
            elif source.startswith('FN:') and target.startswith('WN:'):
                edge_colors.append('purple')
                edge_styles.append('--')  # Dashed for FN-WN
                edge_widths.append(1.5)
            else:
                edge_colors.append('gray')
                edge_styles.append('-')
                edge_widths.append(1)
        
        # Draw edges
        nx.draw_networkx_edges(self.G, self.node_positions,
                             edge_color=edge_colors,
                             width=edge_widths,
                             alpha=0.6,
                             arrows=True,
                             arrowsize=15,
                             arrowstyle='->',
                             ax=self.ax)
        
        # Draw labels with adjusted positions to avoid overlap
        label_pos = {}
        for node, (x, y) in self.node_positions.items():
            # Adjust label position based on node type
            if node.startswith('VN:'):
                label_pos[node] = (x, y - 0.08)
            elif node.startswith('FN:'):
                label_pos[node] = (x, y + 0.08)
            elif node.startswith('WN:'):
                label_pos[node] = (x + 0.08, y)
            else:
                label_pos[node] = (x, y)
        
        # Format labels (remove corpus prefix for display, use full synset names for WordNet)
        labels = {}
        for node in self.G.nodes():
            if ':' in node:
                corpus, name = node.split(':', 1)
                if corpus == 'WN':
                    # For WordNet nodes, try to get full synset name
                    labels[node] = self._get_full_wordnet_label(node, name)
                else:
                    labels[node] = name
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(self.G, label_pos,
                              labels=labels,
                              font_size=8,
                              font_weight='bold',
                              ax=self.ax)
    
    def _add_corpus_labels(self):
        """Add corpus section labels to the visualization."""
        # Corpus labels removed to prevent legend overflow
        # Color information is now conveyed through node shapes and legend
        pass
    
    def _on_hover(self, event):
        """Handle mouse hover events to show node information."""
        if event.inaxes != self.ax:
            self.hide_tooltip()
            return
        
        # Find closest node to mouse position
        closest_node = None
        min_dist = float('inf')
        
        for node, (x, y) in self.node_positions.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < min_dist and dist < 0.1:  # Threshold for hover detection
                min_dist = dist
                closest_node = node
        
        # Update tooltip without changing title
        if closest_node:
            self.show_tooltip(event.xdata, event.ydata, closest_node)
        else:
            self.hide_tooltip()
    
    def _get_visualizer_type(self):
        """Return visualizer type for configuration purposes."""
        return 'combined'
    
    
    def _on_click(self, event):
        """Handle mouse click events to select nodes."""
        if event.inaxes != self.ax:
            return
        
        # Find clicked node
        clicked_node = None
        min_dist = float('inf')
        
        for node, (x, y) in self.node_positions.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < min_dist and dist < 0.1:
                min_dist = dist
                clicked_node = node
        
        if clicked_node:
            self.selected_node = clicked_node
            print(f"\nSelected: {clicked_node}")
            print(self.get_node_info(clicked_node))
            print("-" * 50)
            
            # Highlight selected node and its connections
            self._highlight_node(clicked_node)
    
    def _get_node_shape(self, node):
        """Get the appropriate shape for a node based on its corpus."""
        if node.startswith('VN:'):
            return 's'  # Square for VerbNet
        elif node.startswith('FN:'):
            return '^'  # Triangle for FrameNet
        elif node.startswith('WN:'):
            return 'd'  # Diamond for WordNet
        elif node.startswith('PB:'):
            # PropBank nodes - different shapes by type
            node_data = self.G.nodes.get(node, {})
            node_type = node_data.get('node_type', 'predicate')
            if node_type == 'roleset':
                return 'p'  # Pentagon for rolesets
            elif node_type == 'role':
                return 'v'  # Triangle down for roles
            elif node_type == 'example':
                return '<'  # Triangle left for examples
            elif node_type == 'alias':
                return '>'  # Triangle right for aliases
            else:
                return 'h'  # Hexagon for predicates
        else:
            return 'o'  # Circle for verbs/other nodes
    
    def _get_full_wordnet_label(self, node, short_name):
        """Get full synset name for WordNet nodes."""
        if node not in self.hierarchy:
            return short_name
            
        data = self.hierarchy[node]
        synset_info = data.get('synset_info', {})
        synset_id = synset_info.get('synset_id', '')
        
        # If we have a synset ID, use it as the full label
        if synset_id and synset_id != 'Unknown':
            return synset_id
        else:
            # Fallback to short name
            return short_name
    
    def _highlight_node(self, node):
        """Highlight a selected node and its connections while preserving shapes."""
        # Clear and redraw with highlighting
        self.ax.clear()
        
        # Get connected nodes
        predecessors = set(self.G.predecessors(node))
        successors = set(self.G.successors(node))
        connected = predecessors | successors | {node}
        
        # Draw non-connected nodes with lower alpha, preserving shapes
        unconnected = set(self.G.nodes()) - connected
        if unconnected:
            # Group by shape to draw efficiently
            shape_groups = {}
            for n in unconnected:
                shape = self._get_node_shape(n)
                if shape not in shape_groups:
                    shape_groups[shape] = []
                shape_groups[shape].append(n)
            
            for shape, nodes in shape_groups.items():
                nx.draw_networkx_nodes(self.G, self.node_positions,
                                     nodelist=nodes,
                                     node_color='lightgray',
                                     node_size=1000,
                                     node_shape=shape,
                                     alpha=0.3,
                                     ax=self.ax)
        
        # Draw connected nodes with original colors and shapes
        for n in connected:
            color = self.get_dag_node_color(n)
            size = 3500 if n == node else 2000
            shape = self._get_node_shape(n)
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=[n],
                                 node_color=color,
                                 node_size=size,
                                 node_shape=shape,
                                 alpha=1.0,
                                 ax=self.ax)
        
        # Draw edges
        for edge in self.G.edges():
            if edge[0] in connected and edge[1] in connected:
                nx.draw_networkx_edges(self.G, self.node_positions,
                                     edgelist=[edge],
                                     edge_color='red' if node in edge else 'black',
                                     width=3 if node in edge else 1.5,
                                     alpha=0.8,
                                     arrows=True,
                                     arrowsize=20,
                                     ax=self.ax)
            else:
                nx.draw_networkx_edges(self.G, self.node_positions,
                                     edgelist=[edge],
                                     edge_color='lightgray',
                                     width=0.5,
                                     alpha=0.2,
                                     arrows=True,
                                     ax=self.ax)
        
        # Draw labels with full synset names for WordNet
        labels = {}
        for n in self.G.nodes():
            if ':' in n:
                corpus, name = n.split(':', 1)
                if corpus == 'WN':
                    labels[n] = self._get_full_wordnet_label(n, name)
                else:
                    labels[n] = name
            else:
                labels[n] = n
        
        nx.draw_networkx_labels(self.G, self.node_positions,
                              labels=labels,
                              font_size=10 if node in connected else 6,
                              font_weight='bold' if n == node else 'normal',
                              ax=self.ax)
        
        self.ax.set_title(f"{self.title} - Selected: {node}", 
                         fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Re-add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        self.fig.canvas.draw_idle()
    
