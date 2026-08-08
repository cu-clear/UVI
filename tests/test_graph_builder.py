"""
Unit tests for GraphBuilder class.

This module contains comprehensive tests for the GraphBuilder class
to ensure proper graph construction from FrameNet data.
"""

import unittest
from unittest.mock import Mock, patch
import networkx as nx
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.graph.FrameNetGraphBuilder import FrameNetGraphBuilder as GraphBuilder


class TestGraphBuilder(unittest.TestCase):
    """Test cases for GraphBuilder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.builder = GraphBuilder()
        
        # Create mock FrameNet data
        self.mock_framenet_data = {
            'frames': {
                'Motion': {
                    'name': 'Motion',
                    'ID': '001',
                    'definition': 'Physical movement of entities',
                    'lexical_units': {
                        'move.v': {
                            'name': 'move.v',
                            'ID': 'LU001',
                            'POS': 'V',
                            'definition': 'To change position'
                        },
                        'walk.v': {
                            'name': 'walk.v', 
                            'ID': 'LU002',
                            'POS': 'V',
                            'definition': 'To move on foot'
                        }
                    },
                    'frame_elements': {
                        'Agent': {
                            'name': 'Agent',
                            'ID': 'FE001',
                            'coreType': 'Core',
                            'definition': 'The entity that moves'
                        },
                        'Path': {
                            'name': 'Path',
                            'ID': 'FE002', 
                            'coreType': 'Peripheral',
                            'definition': 'The route of motion'
                        }
                    }
                },
                'Transportation': {
                    'name': 'Transportation',
                    'ID': '002',
                    'definition': 'Movement using vehicles',
                    'lexical_units': {
                        'drive.v': {
                            'name': 'drive.v',
                            'ID': 'LU003',
                            'POS': 'V',
                            'definition': 'To operate a vehicle'
                        }
                    },
                    'frame_elements': {
                        'Driver': {
                            'name': 'Driver',
                            'ID': 'FE003',
                            'coreType': 'Core',
                            'definition': 'The operator of the vehicle'
                        }
                    }
                },
                'EmptyFrame': {
                    'name': 'EmptyFrame',
                    'ID': '003',
                    'definition': 'Frame with no lexical units',
                    'lexical_units': {},
                    'frame_elements': {}
                }
            }
        }
    
    def test_init(self):
        """Test GraphBuilder initialization."""
        builder = GraphBuilder()
        self.assertIsInstance(builder, GraphBuilder)
    
    def test_create_framenet_graph_success(self):
        """Test successful graph creation."""
        G, hierarchy = self.builder.create_framenet_graph(
            self.mock_framenet_data, num_frames=2, max_lus_per_frame=2, max_fes_per_frame=2
        )
        
        # Check that graph was created
        self.assertIsInstance(G, nx.DiGraph)
        self.assertIsInstance(hierarchy, dict)
        
        # Check that frames are in the graph
        self.assertIn('Motion', G.nodes())
        self.assertIn('Transportation', G.nodes())
        
        # Check that lexical units are in the graph
        self.assertIn('move.v.Motion', G.nodes())
        self.assertIn('walk.v.Motion', G.nodes())
        self.assertIn('drive.v.Transportation', G.nodes())
        
        # Check that frame elements are in the graph
        self.assertIn('Agent.Motion', G.nodes())
        self.assertIn('Path.Motion', G.nodes())
        self.assertIn('Driver.Transportation', G.nodes())
        
        # Check node types
        self.assertEqual(G.nodes['Motion']['node_type'], 'frame')
        self.assertEqual(G.nodes['move.v.Motion']['node_type'], 'lexical_unit')
        self.assertEqual(G.nodes['Agent.Motion']['node_type'], 'frame_element')
    
    def test_create_framenet_graph_empty_data(self):
        """Test graph creation with empty data."""
        empty_data = {'frames': {}}
        G, hierarchy = self.builder.create_framenet_graph(empty_data)
        
        self.assertIsNone(G)
        self.assertEqual(hierarchy, {})
    
    def test_create_framenet_graph_no_frames(self):
        """Test graph creation with no frames key."""
        no_frames_data = {}
        G, hierarchy = self.builder.create_framenet_graph(no_frames_data)
        
        self.assertIsNone(G)
        self.assertEqual(hierarchy, {})
    
    def test_select_frames_with_content(self):
        """Test frame selection based on content."""
        frames_data = self.mock_framenet_data['frames']
        selected = self.builder._select_frames_with_content(frames_data, 2)
        
        # Should select frames with lexical units first
        self.assertIn('Motion', selected)
        self.assertIn('Transportation', selected)
        self.assertEqual(len(selected), 2)
    
    def test_select_frames_with_content_fallback(self):
        """Test frame selection fallback to any frames."""
        # Create data with no lexical units
        frames_data = {
            'Frame1': {'lexical_units': {}},
            'Frame2': {'lexical_units': {}}
        }
        selected = self.builder._select_frames_with_content(frames_data, 2)
        
        # Should fallback to any frames
        self.assertEqual(len(selected), 2)
        self.assertIn('Frame1', selected)
        self.assertIn('Frame2', selected)
    
    def test_create_frame_hierarchy_entry(self):
        """Test frame hierarchy entry creation."""
        frame_data = self.mock_framenet_data['frames']['Motion']
        entry = self.builder._create_frame_hierarchy_entry(frame_data, 'Motion')
        
        # Check structure
        self.assertIn('parents', entry)
        self.assertIn('children', entry)
        self.assertIn('frame_info', entry)
        
        # Check frame info
        frame_info = entry['frame_info']
        self.assertEqual(frame_info['name'], 'Motion')
        self.assertEqual(frame_info['id'], '001')
        self.assertEqual(frame_info['definition'], 'Physical movement of entities')
        self.assertEqual(frame_info['elements'], 2)  # Agent, Path
        self.assertEqual(frame_info['lexical_units'], 2)  # move.v, walk.v
        self.assertEqual(frame_info['node_type'], 'frame')
        
        # Check initial empty lists
        self.assertEqual(entry['parents'], [])
        self.assertEqual(entry['children'], [])
    
    def test_add_lexical_units_to_graph(self):
        """Test adding lexical units to graph."""
        G = nx.DiGraph()
        hierarchy = {}
        
        # Add frame first
        G.add_node('Motion', node_type='frame')
        hierarchy['Motion'] = {'children': []}
        
        frame_data = self.mock_framenet_data['frames']['Motion']
        self.builder._add_lexical_units_to_graph(
            G, hierarchy, 'Motion', frame_data, max_lus_per_frame=1
        )
        
        # Check that lexical unit was added
        lu_nodes = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'lexical_unit']
        self.assertEqual(len(lu_nodes), 1)
        
        # Check edge was created
        lu_node = lu_nodes[0]
        self.assertTrue(G.has_edge('Motion', lu_node))
        
        # Check hierarchy was updated
        self.assertIn(lu_node, hierarchy['Motion']['children'])
        self.assertIn(lu_node, hierarchy)
        
        # Check lexical unit hierarchy entry
        lu_hierarchy = hierarchy[lu_node]
        self.assertEqual(lu_hierarchy['parents'], ['Motion'])
        self.assertEqual(lu_hierarchy['children'], [])
        self.assertEqual(lu_hierarchy['frame_info']['frame'], 'Motion')
        self.assertEqual(lu_hierarchy['frame_info']['node_type'], 'lexical_unit')
    
    def test_add_frame_elements_to_graph(self):
        """Test adding frame elements to graph."""
        G = nx.DiGraph()
        hierarchy = {}
        
        # Add frame first
        G.add_node('Motion', node_type='frame')
        hierarchy['Motion'] = {'children': []}
        
        frame_data = self.mock_framenet_data['frames']['Motion']
        self.builder._add_frame_elements_to_graph(
            G, hierarchy, 'Motion', frame_data, max_fes_per_frame=1
        )
        
        # Check that frame element was added
        fe_nodes = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'frame_element']
        self.assertEqual(len(fe_nodes), 1)
        
        # Check edge was created
        fe_node = fe_nodes[0]
        self.assertTrue(G.has_edge('Motion', fe_node))
        
        # Check hierarchy was updated
        self.assertIn(fe_node, hierarchy['Motion']['children'])
        self.assertIn(fe_node, hierarchy)
        
        # Check frame element hierarchy entry
        fe_hierarchy = hierarchy[fe_node]
        self.assertEqual(fe_hierarchy['parents'], ['Motion'])
        self.assertEqual(fe_hierarchy['children'], [])
        self.assertEqual(fe_hierarchy['frame_info']['frame'], 'Motion')
        self.assertEqual(fe_hierarchy['frame_info']['node_type'], 'frame_element')
        self.assertIn('core_type', fe_hierarchy['frame_info'])
    
    def test_add_frame_connections(self):
        """Test adding frame-to-frame connections."""
        G = nx.DiGraph()
        hierarchy = {
            'Motion': {'children': [], 'parents': []},
            'Transportation': {'children': [], 'parents': []},
            'EmptyFrame': {'children': [], 'parents': []}
        }
        
        # Add frame nodes
        for frame in hierarchy.keys():
            G.add_node(frame, node_type='frame')
        
        selected_frames = ['Motion', 'Transportation', 'EmptyFrame']
        self.builder._add_frame_connections(G, hierarchy, selected_frames)
        
        # Check that connections were added (only middle frame should have connections)
        self.assertTrue(G.has_edge('Motion', 'Transportation'))
        self.assertFalse(G.has_edge('Transportation', 'EmptyFrame'))  # Last frame doesn't connect forward
        
        # Check hierarchy was updated
        self.assertIn('Transportation', hierarchy['Motion']['children'])
        self.assertIn('Motion', hierarchy['Transportation']['parents'])
    
    def test_calculate_node_depths(self):
        """Test depth calculation using BFS."""
        G = nx.DiGraph()
        hierarchy = {}
        
        # Create a simple graph: A -> B -> C
        nodes = ['A', 'B', 'C']
        for node in nodes:
            G.add_node(node, node_type='frame')
            hierarchy[node] = {'depth': 0}
        
        G.add_edge('A', 'B')
        G.add_edge('B', 'C')
        
        self.builder._calculate_node_depths(G, hierarchy, nodes)
        
        # Check depths
        self.assertEqual(hierarchy['A']['depth'], 0)
        self.assertEqual(hierarchy['B']['depth'], 1)
        self.assertEqual(hierarchy['C']['depth'], 2)
        
        # Check that node attributes were updated
        self.assertEqual(G.nodes['A']['depth'], 0)
        self.assertEqual(G.nodes['B']['depth'], 1)
        self.assertEqual(G.nodes['C']['depth'], 2)
    
    def test_calculate_node_depths_no_roots(self):
        """Test depth calculation when no clear roots exist."""
        G = nx.DiGraph()
        hierarchy = {}
        
        # Create a graph with no clear root (all nodes have incoming edges)
        nodes = ['A', 'B']
        for node in nodes:
            G.add_node(node, node_type='frame')
            hierarchy[node] = {'depth': 0}
        
        G.add_edge('A', 'B')
        G.add_edge('B', 'A')  # Cycle
        
        selected_frames = ['A', 'B']
        self.builder._calculate_node_depths(G, hierarchy, selected_frames)
        
        # Should use first frame as root
        self.assertEqual(hierarchy['A']['depth'], 0)
    
    @patch('builtins.print')
    def test_display_graph_statistics(self, mock_print):
        """Test graph statistics display."""
        G = nx.DiGraph()
        G.add_nodes_from(['A', 'B', 'C'])
        G.add_edges_from([('A', 'B'), ('B', 'C')])
        
        hierarchy = {
            'A': {'depth': 0, 'frame_info': {'node_type': 'frame', 'elements': 5, 'lexical_units': 3}},
            'B': {'depth': 1, 'frame_info': {'node_type': 'lexical_unit', 'pos': 'V', 'frame': 'A'}},
            'C': {'depth': 2, 'frame_info': {'node_type': 'frame_element', 'core_type': 'Core', 'frame': 'A'}}
        }
        
        self.builder.display_graph_statistics(G, hierarchy)
        
        # Check that print was called with expected content
        mock_print.assert_called()
        calls = [call.args[0] for call in mock_print.call_args_list]
        
        # Check for expected output strings
        self.assertTrue(any('Graph statistics:' in call for call in calls))
        self.assertTrue(any('Nodes: 3' in call for call in calls))
        self.assertTrue(any('Edges: 2' in call for call in calls))
        self.assertTrue(any('Depth distribution:' in call for call in calls))
        self.assertTrue(any('Sample node information:' in call for call in calls))
    
    def test_max_limits_respected(self):
        """Test that max limits are respected for lexical units and frame elements."""
        G, hierarchy = self.builder.create_framenet_graph(
            self.mock_framenet_data, num_frames=1, max_lus_per_frame=1, max_fes_per_frame=1
        )
        
        # Count lexical units for Motion frame (should be limited to 1)
        motion_lus = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'lexical_unit']
        self.assertEqual(len(motion_lus), 1)
        
        # Count frame elements for Motion frame (should be limited to 1)
        motion_fes = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'frame_element']
        self.assertEqual(len(motion_fes), 1)
    
    def test_edge_creation(self):
        """Test that edges are created correctly between nodes."""
        G, hierarchy = self.builder.create_framenet_graph(
            self.mock_framenet_data, num_frames=2, max_lus_per_frame=1, max_fes_per_frame=1
        )
        
        # Check frame-to-lexical-unit edges
        motion_lus = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'lexical_unit']
        for lu in motion_lus:
            self.assertTrue(G.has_edge('Motion', lu))
        
        # Check frame-to-frame-element edges
        motion_fes = [n for n in G.nodes() if '.Motion' in n and G.nodes[n].get('node_type') == 'frame_element']
        for fe in motion_fes:
            self.assertTrue(G.has_edge('Motion', fe))
        
        # Check frame-to-frame edges (demo connections)
        # Note: Frame connections are only created for middle frames (i > 0 and i < len-1)
        # So with 2 frames, no connections are created. Test with 3+ frames for connections.
        frame_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'frame']
        if len(frame_nodes) >= 3:
            # Should have at least one frame-to-frame connection with 3+ frames
            frame_edges = [(u, v) for u, v in G.edges() if 
                          G.nodes[u].get('node_type') == 'frame' and G.nodes[v].get('node_type') == 'frame']
            self.assertGreater(len(frame_edges), 0)
        else:
            # With fewer than 3 frames, no frame-to-frame connections are created
            frame_edges = [(u, v) for u, v in G.edges() if 
                          G.nodes[u].get('node_type') == 'frame' and G.nodes[v].get('node_type') == 'frame']
            self.assertEqual(len(frame_edges), 0)
    
    def test_frame_to_frame_connections(self):
        """Test frame-to-frame connections with 3 frames."""
        # Create data with 3 frames to test frame connections
        three_frame_data = {
            'frames': {
                'Frame1': {'lexical_units': {'lu1': {'name': 'lu1', 'POS': 'V'}}, 'frame_elements': {}},
                'Frame2': {'lexical_units': {'lu2': {'name': 'lu2', 'POS': 'V'}}, 'frame_elements': {}},
                'Frame3': {'lexical_units': {'lu3': {'name': 'lu3', 'POS': 'V'}}, 'frame_elements': {}}
            }
        }
        
        G, hierarchy = self.builder.create_framenet_graph(
            three_frame_data, num_frames=3, max_lus_per_frame=1, max_fes_per_frame=1
        )
        
        # Should have frame-to-frame connection (Frame1 -> Frame2)
        frame_edges = [(u, v) for u, v in G.edges() if 
                      G.nodes[u].get('node_type') == 'frame' and G.nodes[v].get('node_type') == 'frame']
        self.assertGreater(len(frame_edges), 0)
        
        # Check specific connection exists (first frame to second frame)
        self.assertTrue(G.has_edge('Frame1', 'Frame2'))
    
    def test_hierarchy_consistency(self):
        """Test that hierarchy parent-child relationships are consistent."""
        G, hierarchy = self.builder.create_framenet_graph(
            self.mock_framenet_data, num_frames=2, max_lus_per_frame=2, max_fes_per_frame=2
        )
        
        for node, data in hierarchy.items():
            # Check that all parents list this node as a child
            for parent in data.get('parents', []):
                if parent in hierarchy:
                    self.assertIn(node, hierarchy[parent].get('children', []))
            
            # Check that all children list this node as a parent
            for child in data.get('children', []):
                if child in hierarchy:
                    self.assertIn(node, hierarchy[child].get('parents', []))


if __name__ == '__main__':
    unittest.main()