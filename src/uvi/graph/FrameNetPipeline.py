"""
FrameNet-specific implementation of the GraphBuilderPipeline.

This module demonstrates the new unified architecture by implementing
a FrameNet graph builder using the pipeline pattern.
"""

import networkx as nx
from typing import Dict, Any, List, Optional, Tuple

from .GraphBuilderPipeline import GraphBuilderPipeline, GraphConfig
from .UnifiedDataProcessor import UnifiedDataProcessor
from .NodeFactory import default_node_factory
from .DataValidator import DataValidationError


class FrameNetGraphConfig(GraphConfig):
    """FrameNet-specific configuration."""

    def __init__(
        self,
        num_frames: int = 6,
        max_lus_per_frame: int = 3,
        max_fes_per_frame: int = 3,
        **kwargs
    ):
        """
        Initialize FrameNet configuration.

        Args:
            num_frames: Maximum number of frames to include
            max_lus_per_frame: Maximum lexical units per frame
            max_fes_per_frame: Maximum frame elements per frame
            **kwargs: Additional parameters
        """
        super().__init__(
            corpus="framenet",
            num_nodes=num_frames,
            max_children_per_node=max(max_lus_per_frame, max_fes_per_frame),
            **kwargs
        )
        self.num_frames = num_frames
        self.max_lus_per_frame = max_lus_per_frame
        self.max_fes_per_frame = max_fes_per_frame


class FrameNetPipeline(GraphBuilderPipeline):
    """FrameNet implementation of the graph builder pipeline."""

    def __init__(self):
        """Initialize the FrameNet pipeline."""
        super().__init__()
        self.data_processor = UnifiedDataProcessor()

    def validate_input_data(self, data: Dict[str, Any]) -> bool:
        """Validate FrameNet data structure."""
        try:
            return self.data_processor.validate_corpus_structure(data, 'framenet')
        except DataValidationError as e:
            print(f"FrameNet data validation failed: {e}")
            return False

    def select_data(self, data: Dict[str, Any], config: FrameNetGraphConfig) -> List[Dict[str, Any]]:
        """Select frames with lexical units for processing."""
        frames_data = self.data_validator.safe_get(data, 'frames', default={})

        # Select frames that have lexical units
        selected_frames = self.data_processor.select_items_with_content(
            frames_data,
            max_items=config.num_frames,
            content_path='lexical_units',
            min_content_count=1,
            fallback_to_any=True
        )

        # Convert to list of dictionaries with names included
        frame_list = []
        for frame_name, frame_data in selected_frames:
            frame_dict = frame_data.copy()
            frame_dict['name'] = frame_name
            frame_list.append(frame_dict)

        return frame_list

    def add_primary_nodes(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_data: List[Dict[str, Any]],
        config: FrameNetGraphConfig
    ) -> List[str]:
        """Add frame nodes as primary nodes."""
        primary_nodes = []

        for frame_data in selected_data:
            try:
                # Process frame data using node factory
                processed_data = self.node_factory.create_node_data('frame', frame_data, {
                    'corpus': config.corpus
                })

                if processed_data:
                    frame_name = processed_data['name']

                    # Add node safely
                    if self.safe_add_node(graph, hierarchy, frame_name, processed_data):
                        primary_nodes.append(frame_name)

            except Exception as e:
                print(f"Warning: Failed to add frame {frame_data.get('name', 'unknown')}: {e}")
                continue

        return primary_nodes

    def add_child_nodes(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_data: List[Dict[str, Any]],
        primary_nodes: List[str],
        config: FrameNetGraphConfig
    ) -> None:
        """Add lexical units and frame elements as child nodes."""
        # Create mapping of frame names to data for efficient lookup
        frame_data_map = {frame_data['name']: frame_data for frame_data in selected_data}

        for frame_name in primary_nodes:
            frame_data = frame_data_map.get(frame_name, {})

            # Add lexical units
            self._add_lexical_units(graph, hierarchy, frame_name, frame_data, config)

            # Add frame elements
            self._add_frame_elements(graph, hierarchy, frame_name, frame_data, config)

    def _add_lexical_units(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frame_name: str,
        frame_data: Dict[str, Any],
        config: FrameNetGraphConfig
    ) -> None:
        """Add lexical units for a frame."""
        # Extract lexical units using unified processor
        lexical_units = self.data_processor.extract_child_items(
            frame_data,
            child_path='lexical_units',
            max_children=config.max_lus_per_frame,
            required_fields=['name']
        )

        for lu_name, lu_data in lexical_units:
            try:
                # Process LU data using node factory
                processed_data = self.node_factory.create_node_data('lexical_unit', lu_data, {
                    'corpus': config.corpus,
                    'frame_name': frame_name
                })

                if processed_data:
                    # Create standardized node name
                    lu_node_name = f"{processed_data['name']}.{frame_name}"

                    # Add node safely
                    self.safe_add_node(graph, hierarchy, lu_node_name, processed_data, frame_name)

            except Exception as e:
                print(f"Warning: Failed to add lexical unit {lu_name}: {e}")
                continue

    def _add_frame_elements(
        self,
        graph: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frame_name: str,
        frame_data: Dict[str, Any],
        config: FrameNetGraphConfig
    ) -> None:
        """Add frame elements for a frame."""
        # Extract frame elements using unified processor
        frame_elements = self.data_processor.extract_child_items(
            frame_data,
            child_path='frame_elements',
            max_children=config.max_fes_per_frame,
            required_fields=['name']
        )

        for fe_name, fe_data in frame_elements:
            try:
                # Process FE data using node factory
                processed_data = self.node_factory.create_node_data('frame_element', fe_data, {
                    'corpus': config.corpus,
                    'frame_name': frame_name
                })

                if processed_data:
                    # Create standardized node name
                    fe_node_name = f"{processed_data['name']}.{frame_name}"

                    # Add node safely
                    self.safe_add_node(graph, hierarchy, fe_node_name, processed_data, frame_name)

            except Exception as e:
                print(f"Warning: Failed to add frame element {fe_name}: {e}")
                continue

    def create_framenet_graph(
        self,
        framenet_data: Dict[str, Any],
        num_frames: int = 6,
        max_lus_per_frame: int = 3,
        max_fes_per_frame: int = 3
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create FrameNet graph with backward compatibility.

        This method maintains the same interface as the original FrameNetGraphBuilder
        for backward compatibility while using the new pipeline architecture.

        Args:
            framenet_data: FrameNet data dictionary
            num_frames: Maximum number of frames to include
            max_lus_per_frame: Maximum lexical units per frame
            max_fes_per_frame: Maximum frame elements per frame

        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        config = FrameNetGraphConfig(
            num_frames=num_frames,
            max_lus_per_frame=max_lus_per_frame,
            max_fes_per_frame=max_fes_per_frame
        )

        return self.create_graph(framenet_data, config)