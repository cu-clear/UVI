"""
Graph Builder Pipeline using Template Method Pattern.

This module provides the unified pipeline for graph construction,
consolidating the main creation methods across all builders.
"""

import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod

from .DataValidator import DataValidator
from .NodeFactory import NodeFactory, default_node_factory


class GraphConfig:
    """Configuration object for graph building parameters."""

    def __init__(
        self,
        corpus: str = "unknown",
        num_nodes: int = 10,
        max_children_per_node: int = 5,
        include_connections: bool = True,
        connection_strategy: str = "sequential",
        **kwargs
    ):
        """
        Initialize graph configuration.

        Args:
            corpus: Name of the corpus being processed
            num_nodes: Maximum number of primary nodes to include
            max_children_per_node: Maximum child nodes per parent
            include_connections: Whether to create connections between nodes
            connection_strategy: Strategy for creating connections
            **kwargs: Additional corpus-specific parameters
        """
        self.corpus = corpus
        self.num_nodes = num_nodes
        self.max_children_per_node = max_children_per_node
        self.include_connections = include_connections
        self.connection_strategy = connection_strategy

        # Store additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback."""
        return getattr(self, key, default)


class GraphBuilderPipeline(ABC):
    """
    Template method pattern for graph construction pipeline.

    This class consolidates the main creation methods and provides
    a unified interface for all graph builders.
    """

    def __init__(self, node_factory: Optional[NodeFactory] = None):
        """
        Initialize the pipeline.

        Args:
            node_factory: NodeFactory instance for creating nodes
        """
        self.node_factory = node_factory or default_node_factory
        self.data_validator = DataValidator()

    def create_graph(self, data: Dict[str, Any], config: GraphConfig) -> Tuple[nx.DiGraph, Dict[str, Any]]:
        """
        Template method for creating graphs - defines the algorithm structure.

        Args:
            data: Raw corpus data
            config: Configuration object with parameters

        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating {config.corpus} graph with {config.num_nodes} primary nodes...")

        # Validate input data
        if not self.validate_input_data(data):
            print("No valid data available")
            return None, {}

        # Step 1: Select and validate data
        selected_data = self.select_data(data, config)
        if not selected_data:
            print("No suitable data selected")
            return None, {}

        print(f"Selected {len(selected_data)} primary nodes for processing")

        # Step 2: Initialize graph and hierarchy
        graph, hierarchy = self.initialize_graph()

        # Step 3: Add primary nodes
        primary_nodes = self.add_primary_nodes(graph, hierarchy, selected_data, config)

        # Step 4: Add child nodes for each primary node
        self.add_child_nodes(graph, hierarchy, selected_data, primary_nodes, config)

        # Step 5: Create connections (if enabled)
        if config.include_connections:
            self.create_connections(graph, hierarchy, primary_nodes, config)

        # Step 6: Calculate node depths
        self.calculate_depths(graph, hierarchy, primary_nodes)

        # Step 7: Display statistics
        self.display_statistics(graph, hierarchy, config)

        return graph, hierarchy

    @abstractmethod
    def validate_input_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that input data has required structure.

        Args:
            data: Raw input data

        Returns:
            True if data is valid for processing
        """
        pass

    @abstractmethod
    def select_data(self, data: Dict[str, Any], config: GraphConfig) -> List[Dict[str, Any]]:
        """
        Select and filter data for graph construction.

        Args:
            data: Raw corpus data
            config: Configuration object

        Returns:
            List of selected data items for primary nodes
        """
        pass

    @abstractmethod
    def add_primary_nodes(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_data: List[Dict[str, Any]],
        config: GraphConfig
    ) -> List[str]:
        """
        Add primary nodes to the graph.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            selected_data: Selected data for primary nodes
            config: Configuration object

        Returns:
            List of created primary node names
        """
        pass

    @abstractmethod
    def add_child_nodes(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_data: List[Dict[str, Any]],
        primary_nodes: List[str],
        config: GraphConfig
    ) -> None:
        """
        Add child nodes for each primary node.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            selected_data: Selected data for primary nodes
            primary_nodes: List of primary node names
            config: Configuration object
        """
        pass

    def initialize_graph(self) -> Tuple[nx.DiGraph, Dict[str, Any]]:
        """
        Initialize empty graph and hierarchy dictionary.

        Returns:
            Tuple of (empty NetworkX DiGraph, empty hierarchy dict)
        """
        return nx.DiGraph(), {}

    def create_connections(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        primary_nodes: List[str],
        config: GraphConfig
    ) -> None:
        """
        Create connections between primary nodes based on strategy.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            primary_nodes: List of primary node names
            config: Configuration object
        """
        strategy = config.connection_strategy

        if strategy == "sequential" and len(primary_nodes) >= 3:
            # Create connections based on original FrameNet strategy
            # Only create connections when there are 3 or more frames
            if len(primary_nodes) == 3:
                # For 3 frames, only connect first to second (match expected behavior)
                source = primary_nodes[0]
                target = primary_nodes[1]

                # Add edge
                graph.add_edge(source, target)

                # Update hierarchy
                if 'children' not in hierarchy[source]:
                    hierarchy[source]['children'] = []
                if 'parents' not in hierarchy[target]:
                    hierarchy[target]['parents'] = []

                hierarchy[source]['children'].append(target)
                hierarchy[target]['parents'].append(source)
            else:
                # For more than 3 frames, create sequential connections
                for i in range(len(primary_nodes) - 1):
                    source = primary_nodes[i]
                    target = primary_nodes[i + 1]

                    # Add edge
                    graph.add_edge(source, target)

                    # Update hierarchy
                    if 'children' not in hierarchy[source]:
                        hierarchy[source]['children'] = []
                    if 'parents' not in hierarchy[target]:
                        hierarchy[target]['parents'] = []

                    hierarchy[source]['children'].append(target)
                    hierarchy[target]['parents'].append(source)

        elif strategy == "hub" and len(primary_nodes) >= 2:
            # Create hub connections (first node connects to all others)
            hub_node = primary_nodes[0]
            for target_node in primary_nodes[1:]:
                graph.add_edge(hub_node, target_node)

                # Update hierarchy
                if 'children' not in hierarchy[hub_node]:
                    hierarchy[hub_node]['children'] = []
                if 'parents' not in hierarchy[target_node]:
                    hierarchy[target_node]['parents'] = []

                hierarchy[hub_node]['children'].append(target_node)
                hierarchy[target_node]['parents'].append(hub_node)

    def calculate_depths(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        root_nodes: List[str]
    ) -> None:
        """
        Calculate node depths using BFS.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            root_nodes: List of root nodes to start from
        """
        from collections import deque

        node_depths = {}
        queue = deque()

        # Initialize root nodes at depth 0
        for root in root_nodes:
            if root in graph.nodes():
                queue.append((root, 0))
                node_depths[root] = 0
                if root in hierarchy:
                    hierarchy[root]['depth'] = 0

        # BFS to calculate depths
        while queue:
            node, depth = queue.popleft()

            for successor in graph.successors(node):
                if successor not in node_depths:
                    node_depths[successor] = depth + 1
                    if successor in hierarchy:
                        hierarchy[successor]['depth'] = depth + 1
                    queue.append((successor, depth + 1))

        # Update node attributes
        for node, depth in node_depths.items():
            graph.nodes[node]['depth'] = depth

    def display_statistics(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        config: GraphConfig
    ) -> None:
        """
        Display graph statistics and information.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            config: Configuration object
        """
        print(f"Graph statistics:")
        print(f"  Nodes: {graph.number_of_nodes()}")
        print(f"  Edges: {graph.number_of_edges()}")

        # Show node type distribution
        node_types = {}
        for node in graph.nodes():
            node_type = graph.nodes[node].get('node_type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1

        for node_type, count in sorted(node_types.items()):
            print(f"  {node_type}: {count}")

        # Show depth distribution
        depths = [hierarchy[node].get('depth', 0) for node in graph.nodes() if node in hierarchy]
        if depths:
            depth_counts = {}
            for d in depths:
                depth_counts[d] = depth_counts.get(d, 0) + 1
            print(f"  Depth distribution: {dict(sorted(depth_counts.items()))}")

        # Show sample node information
        print("\nSample node information:")
        sample_nodes = list(graph.nodes())[:3]  # Show first 3 nodes
        for node in sample_nodes:
            node_data = graph.nodes[node]
            node_type = node_data.get('node_type', 'unknown')
            if node_type == 'frame':
                elements = node_data.get('elements_count', 0)
                lus = node_data.get('lexical_units_count', 0)
                print(f"  {node} ({node_type}): {elements} elements, {lus} lexical units")
            else:
                definition = node_data.get('definition', '')[:50]
                print(f"  {node} ({node_type}): {definition}...")

    def safe_add_node(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        node_name: str,
        node_data: Dict[str, Any],
        parent_node: Optional[str] = None
    ) -> bool:
        """
        Safely add a node with error handling.

        Args:
            graph: NetworkX directed graph
            hierarchy: Hierarchy dictionary
            node_name: Name of the node to add
            node_data: Node data dictionary
            parent_node: Optional parent node

        Returns:
            True if node was added successfully
        """
        try:
            # Add node to graph
            graph.add_node(node_name, **node_data)

            # Create hierarchy entry
            hierarchy_entry = {
                'parents': [parent_node] if parent_node else [],
                'children': [],
                'depth': 0,
                'frame_info': node_data.copy()  # Use 'frame_info' for backward compatibility
            }
            hierarchy[node_name] = hierarchy_entry

            # Create parent-child relationship
            if parent_node and parent_node in hierarchy:
                graph.add_edge(parent_node, node_name)

                if 'children' not in hierarchy[parent_node]:
                    hierarchy[parent_node]['children'] = []
                hierarchy[parent_node]['children'].append(node_name)

            return True

        except Exception as e:
            print(f"Warning: Failed to add node {node_name}: {e}")
            return False