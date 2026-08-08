"""
FrameNet Graph Builder.

This module contains the FrameNetGraphBuilder class for constructing NetworkX graphs
from FrameNet data, including frames, lexical units, and frame elements.

REFACTORED: Now uses the new pipeline architecture while maintaining backward compatibility.
"""

import networkx as nx
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional, List

from .GraphBuilder import GraphBuilder
from .FrameNetPipeline import FrameNetPipeline


class FrameNetGraphBuilder(GraphBuilder):
    """Builder class for creating FrameNet semantic graphs."""

    def __init__(self):
        """Initialize the FrameNetGraphBuilder."""
        super().__init__()
        # Use new pipeline architecture
        self._pipeline = FrameNetPipeline()
    
    def create_framenet_graph(
        self,
        framenet_data: Dict[str, Any],
        num_frames: int = 6,
        max_lus_per_frame: int = 3,
        max_fes_per_frame: int = 3
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create a demo graph using actual FrameNet frames, their lexical units, and frame elements.

        REFACTORED: Now uses unified pipeline architecture while maintaining identical interface.

        Args:
            framenet_data: FrameNet data dictionary
            num_frames: Maximum number of frames to include
            max_lus_per_frame: Maximum lexical units per frame
            max_fes_per_frame: Maximum frame elements per frame

        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        # Delegate to new pipeline architecture
        return self._pipeline.create_framenet_graph(
            framenet_data, num_frames, max_lus_per_frame, max_fes_per_frame
        )

    # BACKWARD COMPATIBILITY: Maintain access to individual methods for existing tests
    def _select_frames_with_content(self, frames_data: Dict[str, Any], num_frames: int) -> List[str]:
        """Backward compatibility method - delegates to pipeline."""
        return [item[0] for item in self._pipeline.data_processor.select_items_with_content(
            frames_data, num_frames, 'lexical_units', 1, True
        )]

    def _add_frame_elements_to_graph(self, G: nx.DiGraph, hierarchy: Dict[str, Any], frame_name: str, frame_data: Dict[str, Any], max_fes_per_frame: int) -> None:
        """Backward compatibility method for tests - individual frame processing."""
        self._pipeline._add_frame_elements(G, hierarchy, frame_name, frame_data,
                                         type('Config', (), {'max_fes_per_frame': max_fes_per_frame, 'corpus': 'framenet'})())

    def _add_lexical_units_to_graph(self, G: nx.DiGraph, hierarchy: Dict[str, Any], frame_name: str, frame_data: Dict[str, Any], max_lus_per_frame: int) -> None:
        """Backward compatibility method for tests - individual frame processing."""
        self._pipeline._add_lexical_units(G, hierarchy, frame_name, frame_data,
                                        type('Config', (), {'max_lus_per_frame': max_lus_per_frame, 'corpus': 'framenet'})())

    def _add_frame_connections(self, G: nx.DiGraph, hierarchy: Dict[str, Any], selected_frames: List[str]) -> None:
        """Backward compatibility method for tests."""
        config = type('Config', (), {'connection_strategy': 'sequential', 'include_connections': True})()
        self._pipeline.create_connections(G, hierarchy, selected_frames, config)

    def _create_frame_hierarchy_entry(self, frame_data: Dict[str, Any], frame_name: str) -> Dict[str, Any]:
        """Backward compatibility method for tests."""
        return {
            'parents': [],
            'children': [],
            'frame_info': {
                'name': frame_name,
                'id': frame_data.get('ID', ''),
                'definition': frame_data.get('definition', ''),
                'elements': len(frame_data.get('frame_elements', [])),
                'lexical_units': len(frame_data.get('lexical_units', [])),
                'node_type': 'frame'
            }
        }

    def _calculate_node_depths(self, G: nx.DiGraph, hierarchy: Dict[str, Any], selected_frames: List[str]) -> None:
        """Backward compatibility method for tests."""
        # Find actual root nodes (nodes with no incoming edges)
        root_nodes = [n for n in selected_frames if G.in_degree(n) == 0]
        if not root_nodes and selected_frames:
            # If no clear roots, use the first node
            root_nodes = [selected_frames[0]]

        self._pipeline.calculate_depths(G, hierarchy, root_nodes)