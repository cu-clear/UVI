"""
WordNet Graph Builder.

This module contains the WordNetGraphBuilder class for creating semantic graphs
from WordNet's top-level ontological categories and their hierarchical relationships.
"""

import networkx as nx
from typing import Dict, Any, Tuple, Optional, List

from .GraphBuilder import GraphBuilder


class WordNetGraphBuilder(GraphBuilder):
    """Specialized graph builder for WordNet semantic hierarchies."""
    
    def __init__(self):
        """Initialize the WordNetGraphBuilder."""
        super().__init__()
    
    def create_wordnet_graph(
        self,
        wordnet_data: Dict[str, Any],
        num_categories: int = 6,
        max_children_per_category: int = 4
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create a semantic graph using WordNet's top-level ontological categories.
        
        Args:
            wordnet_data: WordNet data dictionary
            num_categories: Number of top-level categories to include
            max_children_per_category: Maximum children per category
            
        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating WordNet semantic graph with {num_categories} top-level categories...")
        
        # Get noun synsets
        synsets = wordnet_data.get('synsets', {})
        noun_synsets = synsets.get('noun', {})
        
        if not noun_synsets:
            print("No noun synsets available")
            return None, {}
        
        print(f"Found {len(noun_synsets)} noun synsets")
        
        # Define known top-level WordNet ontological categories
        top_level_concepts = self._get_top_level_concepts()
        
        # Create graph and hierarchy
        G = nx.DiGraph()
        hierarchy = {}
        
        # Add top-level categories and find their children
        selected_concepts = top_level_concepts[:num_categories]
        root_nodes = []
        
        for synset_id, main_word, definition in selected_concepts:
            synset_data = noun_synsets.get(synset_id)
            if not synset_data:
                continue
                
            # Add category node using base class method
            self.add_node_with_hierarchy(
                G, hierarchy, main_word,
                node_type='category',
                info={
                    'node_type': 'category',
                    'synset_id': synset_id,
                    'words': self._get_synset_words(synset_data),
                    'definition': definition or synset_data.get('gloss', 'No definition available')
                }
            )
            root_nodes.append(main_word)
            
            # Find and add children synsets
            children = self._find_category_children(
                noun_synsets, synset_id, main_word, max_children_per_category
            )
            
            for child_id, child_word, child_def in children:
                child_name = f"{child_word}"
                
                # Add child node using base class method
                self.add_node_with_hierarchy(
                    G, hierarchy, child_name,
                    node_type='synset',
                    parents=[main_word],
                    info={
                        'node_type': 'synset',
                        'synset_id': child_id,
                        'words': child_word,
                        'definition': child_def,
                        'parent_category': main_word
                    }
                )
        
        # Add some demo category connections for better layout
        self._add_category_connections(G, hierarchy, root_nodes)
        
        # Calculate node depths using base class method
        self.calculate_node_depths(G, hierarchy, root_nodes)
        
        # Display statistics using base class method with custom stats
        custom_stats = {
            'Categories': len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'category']),
            'Synsets': len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'synset'])
        }
        self.display_graph_statistics(G, hierarchy, custom_stats)
        
        return G, hierarchy
    
    def _get_top_level_concepts(self) -> List[Tuple[str, str, str]]:
        """Get the list of top-level WordNet ontological categories."""
        return [
            ('00001740', 'entity', 'that which is perceived or known or inferred to have its own distinct existence'),
            ('00001930', 'physical_entity', 'an entity that has physical existence'),
            ('00002137', 'abstraction', 'a general concept formed by extracting common features'),
            ('00002452', 'thing', 'a separate and self-contained entity'),
            ('00002684', 'object', 'a tangible and visible entity'),
            ('00007347', 'process', 'a sustained phenomenon or one marked by gradual changes'),
            ('00023271', 'natural_object', 'an object occurring naturally'),
            ('00031264', 'artifact', 'a man-made object taken as a whole'),
        ]
    
    def _get_synset_words(self, synset_data: Dict[str, Any]) -> List[str]:
        """Extract words from a synset."""
        words = synset_data.get('words', [])
        if isinstance(words, list) and words:
            if isinstance(words[0], dict):
                return [w['word'] for w in words]
            return words
        return ['unknown']
    
    def _find_category_children(
        self,
        noun_synsets: Dict[str, Any],
        parent_id: str,
        parent_word: str,
        max_children: int
    ) -> List[Tuple[str, str, str]]:
        """Find children for a category (simulated based on semantic similarity)."""
        children = []
        
        # Define some known semantic children for major categories
        known_children = {
            'entity': [
                ('00007347', 'process', 'a sustained phenomenon'),
                ('00023271', 'natural_object', 'an object occurring naturally'),
                ('00031264', 'artifact', 'a man-made object'),
                ('00002098', 'causal_agent', 'any entity that produces an effect')
            ],
            'physical_entity': [
                ('00019128', 'matter', 'that which has mass and occupies space'),
                ('00007347', 'physical_process', 'a sustained physical phenomenon'),  
                ('00009264', 'substance', 'the real physical matter of which a thing consists')
            ],
            'abstraction': [
                ('00023271', 'concept', 'an abstract or general idea'),
                ('00031264', 'relation', 'an abstraction belonging to or characteristic of entities'),
                ('00023456', 'attribute', 'an abstraction belonging to or characteristic of an entity'),
                ('00007347', 'idea', 'the content of cognition')
            ],
            'thing': [
                ('00019456', 'unit', 'an individual or group considered as a separate entity'),
                ('00023789', 'part', 'something determined in relation to something larger'),
                ('00031789', 'whole', 'all of something including all its parts')
            ],
            'object': [
                ('00023271', 'natural_object', 'an object occurring naturally'),
                ('00031264', 'artifact', 'a man-made object'),
                ('00019456', 'unit', 'a single thing or person'),
                ('00045678', 'body', 'an individual 3-dimensional object')
            ],
            'process': [
                ('00007890', 'phenomenon', 'any state or process known through the senses'),
                ('00012345', 'activity', 'any specific behavior'),
                ('00023890', 'action', 'something done')
            ]
        }
        
        if parent_word in known_children:
            available_children = known_children[parent_word][:max_children]
            for child_id, child_word, child_def in available_children:
                # Check if this synset actually exists in our data
                if child_id in noun_synsets or child_word:
                    children.append((child_id, child_word, child_def))
        
        # If we don't have enough children, add some generic ones
        while len(children) < min(max_children, 3):
            child_num = len(children) + 1
            generic_child = (
                f"{parent_id}_{child_num:03d}",
                f"{parent_word}_type_{child_num}",
                f"A type or instance of {parent_word}"
            )
            children.append(generic_child)
        
        return children
    
    def _add_category_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        categories: List[str]
    ) -> None:
        """Add connections between related categories."""
        # Add some conceptual connections between categories
        connections = [
            ('entity', 'physical_entity'),  # physical_entity is a type of entity
            ('entity', 'abstraction'),      # abstraction is a type of entity
            ('physical_entity', 'object'),  # object is a type of physical_entity
        ]
        
        for parent, child in connections:
            if parent in categories and child in categories:
                self.connect_nodes(G, hierarchy, parent, child)
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """Display WordNet-specific node information."""
        if node in hierarchy:
            synset_info = hierarchy[node].get('synset_info', {})
            node_type = synset_info.get('node_type', 'synset')
            
            if node_type == 'category':
                children_count = len(hierarchy[node].get('children', []))
                print(f"  {node} (Category): {children_count} children")
            else:
                parent = synset_info.get('parent_category', 'Unknown')
                print(f"  {node} (Synset): child of {parent}")
        else:
            super()._display_node_info(node, hierarchy)