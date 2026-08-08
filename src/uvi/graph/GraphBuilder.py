"""
Base Graph Builder.

This module contains the base GraphBuilder class with common functionality
for constructing NetworkX graphs from various corpus data.
"""

import networkx as nx
from collections import deque
from typing import Dict, Any, List, Optional, Tuple


class GraphBuilder:
    """Base class for building semantic graphs from corpus data."""
    
    def __init__(self):
        """Initialize the GraphBuilder."""
        pass
    
    def calculate_node_depths(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        root_nodes: Optional[List[str]] = None
    ) -> None:
        """
        Calculate the depth of each node in the graph using BFS.
        
        Args:
            G: NetworkX directed graph
            hierarchy: Hierarchy dictionary to update with depths
            root_nodes: Optional list of root nodes to start from.
                       If None, will find nodes with no incoming edges.
        """
        node_depths = {}
        queue = deque()
        
        # Determine root nodes if not provided
        if root_nodes is None:
            root_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
            if not root_nodes and G.number_of_nodes() > 0:
                # If no clear roots, use the first node
                root_nodes = [list(G.nodes())[0]]
        
        # Initialize queue with root nodes at depth 0
        for root in root_nodes:
            if root in G.nodes():
                queue.append((root, 0))
                node_depths[root] = 0
                if root in hierarchy:
                    hierarchy[root]['depth'] = 0
        
        # BFS to calculate depths
        while queue:
            node, depth = queue.popleft()
            
            # Add successors to queue with incremented depth
            for successor in G.successors(node):
                if successor not in node_depths:
                    node_depths[successor] = depth + 1
                    if successor in hierarchy:
                        hierarchy[successor]['depth'] = depth + 1
                    queue.append((successor, depth + 1))
        
        # Update node attributes with calculated depths
        for node, depth in node_depths.items():
            G.nodes[node]['depth'] = depth
    
    def display_graph_statistics(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        custom_stats: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Display graph statistics and sample information.
        
        Args:
            G: NetworkX directed graph
            hierarchy: Hierarchy dictionary with node information
            custom_stats: Optional dictionary of custom statistics to display
        """
        print(f"Graph statistics:")
        print(f"  Nodes: {G.number_of_nodes()}")
        print(f"  Edges: {G.number_of_edges()}")
        
        # Display custom statistics if provided
        if custom_stats:
            for key, value in custom_stats.items():
                print(f"  {key}: {value}")
        
        # Show depth distribution
        depths = [hierarchy[node].get('depth', 0) for node in G.nodes() if node in hierarchy]
        if depths:
            depth_counts = {}
            for d in depths:
                depth_counts[d] = depth_counts.get(d, 0) + 1
            print(f"  Depth distribution: {dict(sorted(depth_counts.items()))}")
        
        # Show sample node information
        print(f"\nSample node information:")
        sample_nodes = list(G.nodes())[:min(3, G.number_of_nodes())]
        for node in sample_nodes:
            self._display_node_info(node, hierarchy)
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """
        Display information about a single node.
        Override this method in subclasses for custom display.
        
        Args:
            node: Node name
            hierarchy: Hierarchy dictionary with node information
        """
        if node in hierarchy:
            node_data = hierarchy[node]
            info = f"  {node}"
            
            # Add node type if available
            if 'frame_info' in node_data:
                node_type = node_data['frame_info'].get('node_type', 'unknown')
                info += f" ({node_type})"
            elif 'synset_info' in node_data:
                node_type = node_data['synset_info'].get('node_type', 'unknown')
                info += f" ({node_type})"
            
            # Add children count if available
            children = node_data.get('children', [])
            if children:
                info += f": {len(children)} children"
            
            print(info)
    
    def create_hierarchy_entry(
        self,
        parents: List[str] = None,
        children: List[str] = None,
        depth: int = 0,
        info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a standard hierarchy entry for a node.
        
        Args:
            parents: List of parent node names
            children: List of child node names
            depth: Depth of the node in the hierarchy
            info: Additional information about the node
        
        Returns:
            Dictionary with hierarchy information
        """
        entry = {
            'parents': parents or [],
            'children': children or [],
            'depth': depth
        }
        
        # Add additional info based on type
        if info:
            if 'node_type' in info:
                # Determine info key based on corpus type
                if info['node_type'] in ['frame', 'lexical_unit', 'frame_element']:
                    entry['frame_info'] = info
                elif info['node_type'] in ['category', 'synset']:
                    entry['synset_info'] = info
                else:
                    entry['node_info'] = info
            else:
                entry['node_info'] = info
        
        return entry
    
    def add_node_with_hierarchy(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        node_name: str,
        node_type: str = None,
        parents: List[str] = None,
        info: Dict[str, Any] = None
    ) -> None:
        """
        Add a node to both the graph and hierarchy.
        
        Args:
            G: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            node_name: Name of the node to add
            node_type: Type of the node
            parents: List of parent nodes
            info: Additional node information
        """
        # Add node to graph
        if node_type:
            G.add_node(node_name, node_type=node_type)
        else:
            G.add_node(node_name)
        
        # Create hierarchy entry
        if info is None:
            info = {}
        if node_type:
            info['node_type'] = node_type
        
        hierarchy[node_name] = self.create_hierarchy_entry(
            parents=parents,
            info=info
        )
        
        # Add edges from parents
        if parents:
            for parent in parents:
                if parent in G.nodes():
                    G.add_edge(parent, node_name)
                    if parent in hierarchy:
                        if node_name not in hierarchy[parent]['children']:
                            hierarchy[parent]['children'].append(node_name)
    
    def connect_nodes(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        parent: str,
        child: str
    ) -> None:
        """
        Connect two nodes in the graph and update hierarchy.
        
        Args:
            G: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            parent: Parent node name
            child: Child node name
        """
        if parent in G.nodes() and child in G.nodes():
            if not G.has_edge(parent, child):
                G.add_edge(parent, child)
                
                # Update hierarchy
                if parent in hierarchy and child not in hierarchy[parent]['children']:
                    hierarchy[parent]['children'].append(child)
                if child in hierarchy and parent not in hierarchy[child]['parents']:
                    hierarchy[child]['parents'].append(parent)
    
    def get_node_counts_by_type(
        self,
        G: nx.DiGraph,
        type_attribute: str = 'node_type'
    ) -> Dict[str, int]:
        """
        Count nodes by their type attribute.
        
        Args:
            G: NetworkX directed graph
            type_attribute: Name of the node attribute containing type
        
        Returns:
            Dictionary mapping node types to counts
        """
        type_counts = {}
        for node in G.nodes():
            node_type = G.nodes[node].get(type_attribute, 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts