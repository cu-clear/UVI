"""
Base Node Processor Interface.

This module provides the abstract base class and interface for node processing
across all graph builders, eliminating duplication in node creation patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import networkx as nx


class BaseNodeProcessor(ABC):
    """Abstract base class for processing and creating nodes in semantic graphs."""

    def __init__(self):
        """Initialize the BaseNodeProcessor."""
        pass

    @abstractmethod
    def process_node_data(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw node data into standardized format.

        Args:
            raw_data: Raw node data from corpus
            config: Configuration parameters for processing

        Returns:
            Processed node data in standardized format
        """
        pass

    @abstractmethod
    def create_node_name(self, node_data: Dict[str, Any], context: Optional[str] = None) -> str:
        """
        Create a standardized node name from node data.

        Args:
            node_data: Processed node data
            context: Optional context for name generation (e.g., parent frame)

        Returns:
            Standardized node name
        """
        pass

    def add_nodes_batch(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        nodes_data: List[Dict[str, Any]],
        parent_node: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add multiple nodes to graph in batch with standardized processing.

        Args:
            graph: NetworkX directed graph to add nodes to
            hierarchy: Hierarchy dictionary to update
            nodes_data: List of raw node data dictionaries
            parent_node: Optional parent node name for hierarchical relationships
            config: Optional configuration for processing

        Returns:
            List of created node names
        """
        config = config or {}
        created_nodes = []

        for node_data in nodes_data:
            try:
                # Process the raw data
                processed_data = self.process_node_data(node_data, config)

                # Create standardized node name
                node_name = self.create_node_name(processed_data, parent_node)

                # Add node to graph
                graph.add_node(node_name, **processed_data)

                # Create hierarchy entry
                hierarchy_entry = self._create_hierarchy_entry(processed_data, parent_node)
                hierarchy[node_name] = hierarchy_entry

                # Create parent-child relationships
                if parent_node and parent_node in hierarchy:
                    # Add edge in graph
                    graph.add_edge(parent_node, node_name)

                    # Update hierarchy relationships
                    if 'children' not in hierarchy[parent_node]:
                        hierarchy[parent_node]['children'] = []
                    hierarchy[parent_node]['children'].append(node_name)

                    if 'parents' not in hierarchy[node_name]:
                        hierarchy[node_name]['parents'] = []
                    hierarchy[node_name]['parents'].append(parent_node)

                created_nodes.append(node_name)

            except Exception as e:
                # Log error but continue processing other nodes
                print(f"Warning: Failed to process node {node_data}: {e}")
                continue

        return created_nodes

    def _create_hierarchy_entry(self, processed_data: Dict[str, Any], parent_node: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a standardized hierarchy entry for a node.

        Args:
            processed_data: Processed node data
            parent_node: Optional parent node name

        Returns:
            Standardized hierarchy entry
        """
        return {
            'parents': [parent_node] if parent_node else [],
            'children': [],
            'depth': 0,  # Will be calculated later
            'frame_info': processed_data.copy()  # Use 'frame_info' for backward compatibility
        }

    def validate_node_data(self, node_data: Dict[str, Any]) -> bool:
        """
        Validate that node data contains required fields.

        Args:
            node_data: Node data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'node_type']
        return all(field in node_data for field in required_fields)

    def safe_get_attribute(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Safely get nested attribute from data dictionary.

        Args:
            data: Data dictionary
            path: Dot-separated path to attribute (e.g., 'frame.elements.count')
            default: Default value if path not found

        Returns:
            Value at path or default
        """
        try:
            keys = path.split('.')
            result = data
            for key in keys:
                result = result[key]
            return result
        except (KeyError, TypeError):
            return default