"""
Node Factory for configurable node creation.

This module provides a configurable factory for creating different types of nodes
with consistent processing and validation.
"""

from typing import Dict, Any, Optional
from .BaseNodeProcessor import BaseNodeProcessor


class NodeFactory:
    """Factory class for creating nodes with different processors."""

    def __init__(self):
        """Initialize the NodeFactory."""
        self._processors = {}

    def register_processor(self, node_type: str, processor: BaseNodeProcessor) -> None:
        """
        Register a processor for a specific node type.

        Args:
            node_type: Type of node (e.g., 'frame', 'lexical_unit', 'frame_element')
            processor: BaseNodeProcessor instance for this node type
        """
        self._processors[node_type] = processor

    def get_processor(self, node_type: str) -> Optional[BaseNodeProcessor]:
        """
        Get processor for a node type.

        Args:
            node_type: Type of node

        Returns:
            BaseNodeProcessor instance or None if not registered
        """
        return self._processors.get(node_type)

    def create_node_data(self, node_type: str, raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create standardized node data using appropriate processor.

        Args:
            node_type: Type of node to create
            raw_data: Raw node data from corpus
            config: Optional configuration parameters

        Returns:
            Processed node data or None if processor not found
        """
        processor = self.get_processor(node_type)
        if not processor:
            print(f"Warning: No processor registered for node type '{node_type}'")
            return None

        config = config or {}
        try:
            return processor.process_node_data(raw_data, config)
        except Exception as e:
            print(f"Warning: Failed to process {node_type} node: {e}")
            return None

    def validate_node_type(self, node_type: str) -> bool:
        """
        Validate that a node type has a registered processor.

        Args:
            node_type: Type of node to validate

        Returns:
            True if processor is registered, False otherwise
        """
        return node_type in self._processors


class FrameNodeProcessor(BaseNodeProcessor):
    """Processor for frame nodes."""

    def process_node_data(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Process frame data into standardized format."""
        return {
            'name': raw_data.get('name', ''),
            'node_type': 'frame',
            'definition': raw_data.get('definition', ''),
            'id': raw_data.get('ID', raw_data.get('id', '')),
            'elements_count': len(raw_data.get('frame_elements', [])),
            'lexical_units_count': len(raw_data.get('lexical_units', [])),
            'corpus': config.get('corpus', 'unknown')
        }

    def create_node_name(self, node_data: Dict[str, Any], context: Optional[str] = None) -> str:
        """Create standardized frame node name."""
        return node_data.get('name', 'UnknownFrame')


class LexicalUnitNodeProcessor(BaseNodeProcessor):
    """Processor for lexical unit nodes."""

    def process_node_data(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Process lexical unit data into standardized format."""
        return {
            'name': raw_data.get('name', ''),
            'node_type': 'lexical_unit',
            'pos': raw_data.get('POS', raw_data.get('pos', '')),
            'id': raw_data.get('ID', raw_data.get('id', '')),
            'definition': raw_data.get('definition', ''),
            'corpus': config.get('corpus', 'unknown'),
            'frame': config.get('frame_name', '')
        }

    def create_node_name(self, node_data: Dict[str, Any], context: Optional[str] = None) -> str:
        """Create standardized lexical unit node name."""
        name = node_data.get('name', 'UnknownLU')
        if context:
            return f"{name}.{context}"
        return name


class FrameElementNodeProcessor(BaseNodeProcessor):
    """Processor for frame element nodes."""

    def process_node_data(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Process frame element data into standardized format."""
        return {
            'name': raw_data.get('name', ''),
            'node_type': 'frame_element',
            'core_type': raw_data.get('coreType', raw_data.get('core_type', '')),
            'id': raw_data.get('ID', raw_data.get('id', '')),
            'definition': raw_data.get('definition', ''),
            'corpus': config.get('corpus', 'unknown'),
            'frame': config.get('frame_name', '')
        }

    def create_node_name(self, node_data: Dict[str, Any], context: Optional[str] = None) -> str:
        """Create standardized frame element node name."""
        name = node_data.get('name', 'UnknownFE')
        if context:
            return f"{name}.{context}"
        return name


# Default factory instance with common processors registered
default_node_factory = NodeFactory()
default_node_factory.register_processor('frame', FrameNodeProcessor())
default_node_factory.register_processor('lexical_unit', LexicalUnitNodeProcessor())
default_node_factory.register_processor('frame_element', FrameElementNodeProcessor())