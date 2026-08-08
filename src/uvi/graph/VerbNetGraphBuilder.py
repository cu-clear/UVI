"""
VerbNet Graph Builder.

This module contains the VerbNetGraphBuilder class for creating semantic graphs
from VerbNet's verb class hierarchies and their semantic relationships.
"""

import networkx as nx
from typing import Dict, Any, Tuple, Optional, List

from .GraphBuilder import GraphBuilder


class VerbNetGraphBuilder(GraphBuilder):
    """Specialized graph builder for VerbNet verb class hierarchies."""
    
    def __init__(self):
        """Initialize the VerbNetGraphBuilder."""
        super().__init__()
    
    def create_verbnet_graph(
        self,
        verbnet_data: Dict[str, Any],
        num_classes: int = 8,
        max_subclasses_per_class: int = 4,
        include_members: bool = True,
        max_members_per_class: int = 3
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create a semantic graph using VerbNet's verb class hierarchies.
        
        Args:
            verbnet_data: VerbNet data dictionary
            num_classes: Number of top-level verb classes to include
            max_subclasses_per_class: Maximum subclasses per class
            include_members: Whether to include member verbs
            max_members_per_class: Maximum member verbs to show per class
            
        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating VerbNet semantic graph with {num_classes} top-level classes...")
        
        # Get VerbNet classes
        vn_classes = verbnet_data.get('classes', {})
        
        if not vn_classes:
            print("No VerbNet classes available")
            return None, {}
        
        print(f"Found {len(vn_classes)} VerbNet classes")
        
        # Create graph and hierarchy
        G = nx.DiGraph()
        hierarchy = {}
        
        # Sort classes by ID to get consistent ordering
        sorted_classes = sorted(vn_classes.items())[:num_classes]
        root_nodes = []
        
        for class_id, class_data in sorted_classes:
            # Extract main class name (e.g., "put-9.1" -> "put")
            main_verb = class_id.split('-')[0]
            class_name = f"{main_verb}-{class_id.split('-')[1]}"
            
            # Add class node using base class method
            self.add_node_with_hierarchy(
                G, hierarchy, class_name,
                node_type='verb_class',
                info={
                    'node_type': 'verb_class',
                    'class_id': class_id,
                    'members': self._get_class_members(class_data, max_members_per_class),
                    'frames': self._get_class_frames(class_data),
                    'themroles': self._get_class_themroles(class_data)
                }
            )
            root_nodes.append(class_name)
            
            # Add subclasses
            subclasses = self._get_subclasses(class_data, max_subclasses_per_class)
            for subclass_id, subclass_data in subclasses:
                subclass_name = f"{main_verb}-{subclass_id.split('-')[-1]}"
                
                # Add subclass node
                self.add_node_with_hierarchy(
                    G, hierarchy, subclass_name,
                    node_type='verb_subclass',
                    parents=[class_name],
                    info={
                        'node_type': 'verb_subclass',
                        'class_id': subclass_id,
                        'parent_class': class_name,
                        'members': self._get_class_members(subclass_data, max_members_per_class),
                        'frames': self._get_class_frames(subclass_data)
                    }
                )
                
                # Add member verbs if requested
                if include_members:
                    members = self._get_class_members(subclass_data, max_members_per_class)
                    for member in members[:max_members_per_class]:
                        member_name = f"{member}"
                        
                        # Check if this member node already exists
                        if member_name not in G.nodes():
                            self.add_node_with_hierarchy(
                                G, hierarchy, member_name,
                                node_type='verb_member',
                                parents=[subclass_name],
                                info={
                                    'node_type': 'verb_member',
                                    'lemma': member,
                                    'parent_class': subclass_name
                                }
                            )
                        else:
                            # Just add the edge if node exists
                            self.connect_nodes(G, hierarchy, subclass_name, member_name)
            
            # Add member verbs for main class if requested and no subclasses
            if include_members and not subclasses:
                members = self._get_class_members(class_data, max_members_per_class)
                for member in members[:max_members_per_class]:
                    member_name = f"{member}"
                    
                    if member_name not in G.nodes():
                        self.add_node_with_hierarchy(
                            G, hierarchy, member_name,
                            node_type='verb_member',
                            parents=[class_name],
                            info={
                                'node_type': 'verb_member',
                                'lemma': member,
                                'parent_class': class_name
                            }
                        )
                    else:
                        self.connect_nodes(G, hierarchy, class_name, member_name)
        
        # Add some semantic connections between related classes
        self._add_semantic_connections(G, hierarchy, root_nodes, vn_classes)
        
        # Calculate node depths using base class method
        self.calculate_node_depths(G, hierarchy, root_nodes)
        
        # Display statistics using base class method with custom stats
        custom_stats = {
            'Verb Classes': len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'verb_class']),
            'Subclasses': len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'verb_subclass']),
            'Member Verbs': len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'verb_member'])
        }
        self.display_graph_statistics(G, hierarchy, custom_stats)
        
        return G, hierarchy
    
    def _get_class_members(self, class_data: Dict[str, Any], max_members: int = 5) -> List[str]:
        """Extract member verbs from a VerbNet class."""
        members = class_data.get('members', [])
        if isinstance(members, list):
            # Handle different member formats
            if members and isinstance(members[0], dict):
                return [m.get('name', m.get('lemma', 'unknown')) for m in members[:max_members]]
            return members[:max_members]
        return []
    
    def _get_class_frames(self, class_data: Dict[str, Any]) -> List[str]:
        """Extract frame descriptions from a VerbNet class."""
        frames = class_data.get('frames', [])
        frame_descriptions = []
        
        if isinstance(frames, list):
            for frame in frames[:3]:  # Limit to first 3 frames
                if isinstance(frame, dict):
                    # Try to get frame description or syntax
                    desc = frame.get('description', {})
                    if isinstance(desc, dict):
                        primary = desc.get('primary', '')
                        if primary:
                            frame_descriptions.append(primary)
                    elif isinstance(desc, str):
                        frame_descriptions.append(desc)
                    
                    # Fallback to syntax if no description
                    if not frame_descriptions:
                        syntax = frame.get('syntax', [])
                        if syntax:
                            frame_descriptions.append(f"Frame with {len(syntax)} syntactic elements")
        
        return frame_descriptions
    
    def _get_class_themroles(self, class_data: Dict[str, Any]) -> List[str]:
        """Extract thematic roles from a VerbNet class."""
        themroles = class_data.get('themroles', [])
        role_names = []
        
        if isinstance(themroles, list):
            for role in themroles:
                if isinstance(role, dict):
                    role_type = role.get('type', '')
                    if role_type:
                        role_names.append(role_type)
                elif isinstance(role, str):
                    role_names.append(role)
        
        return role_names
    
    def _get_subclasses(self, class_data: Dict[str, Any], max_subclasses: int) -> List[Tuple[str, Dict]]:
        """Get subclasses of a VerbNet class."""
        subclasses = []
        
        # Check for subclasses field
        if 'subclasses' in class_data:
            subclass_data = class_data['subclasses']
            if isinstance(subclass_data, dict):
                for subclass_id, subclass_info in list(subclass_data.items())[:max_subclasses]:
                    subclasses.append((subclass_id, subclass_info))
            elif isinstance(subclass_data, list):
                for subclass_info in subclass_data[:max_subclasses]:
                    if isinstance(subclass_info, dict):
                        subclass_id = subclass_info.get('id', subclass_info.get('class_id', 'unknown'))
                        subclasses.append((subclass_id, subclass_info))
        
        return subclasses
    
    def _add_semantic_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        root_nodes: List[str],
        vn_classes: Dict[str, Any]
    ) -> None:
        """Add semantic connections between related verb classes."""
        # Define some known semantic relationships between verb classes
        # These are example relationships - in a real implementation,
        # these would come from VerbNet's actual semantic relationships
        
        semantic_relations = [
            ('put-9', 'place-9'),      # putting and placing are related
            ('run-51', 'motion-51'),   # running is a type of motion
            ('say-37', 'tell-37'),     # saying and telling are related
            ('give-13', 'send-11'),    # giving and sending involve transfer
            ('break-45', 'destroy-44'), # breaking and destroying are related
        ]
        
        for source_pattern, target_pattern in semantic_relations:
            source_nodes = [n for n in root_nodes if source_pattern in n.lower()]
            target_nodes = [n for n in root_nodes if target_pattern in n.lower()]
            
            for source in source_nodes:
                for target in target_nodes:
                    if source != target and source in G.nodes() and target in G.nodes():
                        # Add a semantic relation edge
                        if not G.has_edge(source, target):
                            G.add_edge(source, target, relation_type='semantic')
                            # Note: We don't update hierarchy here as these are cross-connections
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """Display VerbNet-specific node information."""
        if node in hierarchy:
            node_data = hierarchy[node]
            node_info = node_data.get('node_info', node_data.get('verb_info', {}))
            
            if not node_info:
                # Check for frame_info or other info types
                for key in ['frame_info', 'synset_info', 'verb_info']:
                    if key in node_data:
                        node_info = node_data[key]
                        break
            
            node_type = node_info.get('node_type', 'unknown')
            
            if node_type == 'verb_class':
                members = node_info.get('members', [])
                children_count = len(hierarchy[node].get('children', []))
                print(f"  {node} (Verb Class): {len(members)} members, {children_count} subclasses")
            elif node_type == 'verb_subclass':
                parent = node_info.get('parent_class', 'Unknown')
                members = node_info.get('members', [])
                print(f"  {node} (Subclass of {parent}): {len(members)} members")
            elif node_type == 'verb_member':
                parent = node_info.get('parent_class', 'Unknown')
                print(f"  {node} (Member verb of {parent})")
            else:
                super()._display_node_info(node, hierarchy)