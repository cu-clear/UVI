"""
PropBank Graph Builder.

This module contains the PropBankGraphBuilder class for constructing NetworkX graphs
from PropBank data, including predicates, rolesets, roles, examples, and aliases.
"""

import networkx as nx
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional, List

from .GraphBuilder import GraphBuilder


class PropBankGraphBuilder(GraphBuilder):
    """Builder class for creating PropBank semantic graphs."""
    
    def __init__(self):
        """Initialize the PropBankGraphBuilder."""
        super().__init__()
    
    def create_propbank_graph(
        self, 
        propbank_data: Dict[str, Any], 
        num_predicates: int = 6, 
        max_rolesets_per_predicate: int = 2,
        max_roles_per_roleset: int = 3,
        max_examples_per_roleset: int = 2,
        include_aliases: bool = True
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create a demo graph using actual PropBank predicates, their rolesets, roles, and examples.
        
        Args:
            propbank_data: PropBank data dictionary
            num_predicates: Maximum number of predicates to include
            max_rolesets_per_predicate: Maximum rolesets per predicate
            max_roles_per_roleset: Maximum roles per roleset
            max_examples_per_roleset: Maximum examples per roleset
            include_aliases: Whether to include alias nodes
            
        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating demo graph with {num_predicates} PropBank predicates and their rolesets...")
        
        predicates_data = propbank_data.get('predicates', {})
        if not predicates_data:
            print("No predicates data available")
            return None, {}
        
        # Select predicates that have rolesets for a more interesting demo
        selected_predicates = self._select_predicates_with_content(
            predicates_data, num_predicates
        )
        
        if not selected_predicates:
            print("No suitable predicates found")
            return None, {}
        
        print(f"Selected predicates: {selected_predicates}")
        
        # Create graph and hierarchy
        G = nx.DiGraph()
        hierarchy = {}
        
        # Add predicate nodes and their relationships
        self._add_predicates_to_graph(
            G, hierarchy, predicates_data, selected_predicates
        )
        
        # Add rolesets as child nodes
        self._add_rolesets_to_graph(
            G, hierarchy, predicates_data, selected_predicates, max_rolesets_per_predicate
        )
        
        # Add roles as child nodes of rolesets
        self._add_roles_to_graph(
            G, hierarchy, predicates_data, selected_predicates, max_roles_per_roleset
        )
        
        # Add examples as child nodes of rolesets
        self._add_examples_to_graph(
            G, hierarchy, predicates_data, selected_predicates, max_examples_per_roleset
        )
        
        # Add aliases if requested
        if include_aliases:
            self._add_aliases_to_graph(
                G, hierarchy, predicates_data, selected_predicates
            )
        
        # Create some connections between predicates for demo
        self._create_predicate_connections(G, hierarchy, selected_predicates)
        
        # Calculate node depths using base class method
        self.calculate_node_depths(G, hierarchy, selected_predicates)
        
        # Display statistics using base class method with custom stats
        custom_stats = self.get_node_counts_by_type(G)
        self.display_graph_statistics(G, hierarchy, custom_stats)
        
        return G, hierarchy
    
    def _select_predicates_with_content(
        self,
        predicates_data: Dict[str, Any],
        num_predicates: int
    ) -> List[str]:
        """Select predicates that have rolesets for demonstration."""
        predicates_with_rolesets = []
        predicates_checked = 0
        max_checks = min(50, len(predicates_data))
        
        for predicate_name, predicate_data in predicates_data.items():
            if predicates_checked >= max_checks:
                break
                
            predicates_checked += 1
            rolesets = predicate_data.get('rolesets', [])
            
            if rolesets and len(rolesets) > 0:
                predicates_with_rolesets.append(predicate_name)
                if len(predicates_with_rolesets) >= num_predicates:
                    break
        
        print(f"Checked {predicates_checked} predicates, found {len(predicates_with_rolesets)} predicates with rolesets")
        return predicates_with_rolesets[:num_predicates]
    
    def _add_predicates_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        predicates_data: Dict[str, Any],
        selected_predicates: List[str]
    ) -> None:
        """Add predicate nodes to the graph."""
        for predicate_name in selected_predicates:
            predicate_data = predicates_data.get(predicate_name, {})
            
            # Add predicate node
            self.add_node_with_hierarchy(
                G, hierarchy, predicate_name,
                node_type='predicate',
                info={
                    'node_type': 'predicate',
                    'lemma': predicate_data.get('lemma', predicate_name),
                    'rolesets': len(predicate_data.get('rolesets', [])),
                    'aliases': len(predicate_data.get('aliases', []))
                }
            )
    
    def _add_rolesets_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        predicates_data: Dict[str, Any],
        selected_predicates: List[str],
        max_rolesets_per_predicate: int
    ) -> None:
        """Add roleset nodes as children of predicate nodes."""
        for predicate_name in selected_predicates:
            predicate_data = predicates_data.get(predicate_name, {})
            rolesets = predicate_data.get('rolesets', [])
            
            # Add limited number of rolesets
            if rolesets and not isinstance(rolesets, slice):
                try:
                    # Safely slice the rolesets
                    rs_slice = rolesets[:max_rolesets_per_predicate]
                    if isinstance(rs_slice, slice):
                        continue
                    
                    for i, roleset in enumerate(rs_slice):
                        if isinstance(roleset, slice):
                            continue
                        if isinstance(roleset, dict):
                            rs_id = roleset.get('id', f'{predicate_name}.{i:02d}')
                            rs_name = roleset.get('name', f'roleset_{i}')
                            rs_note = roleset.get('note', '')
                            rs_roles = roleset.get('roles', [])
                            rs_examples = roleset.get('examples', [])
                        else:
                            rs_id = f'{predicate_name}.{i:02d}'
                            rs_name = str(roleset)
                            rs_note = ''
                            rs_roles = []
                            rs_examples = []
                        
                        # Create unique node name using roleset ID
                        rs_node_name = rs_id
                        
                        # Add roleset node
                        self.add_node_with_hierarchy(
                            G, hierarchy, rs_node_name,
                            node_type='roleset',
                            parents=[predicate_name],
                            info={
                                'node_type': 'roleset',
                                'id': rs_id,
                                'name': rs_name,
                                'note': rs_note,
                                'predicate': predicate_name,
                                'roles': rs_roles,
                                'examples': rs_examples
                            }
                        )
                except Exception as e:
                    print(f"Warning: Could not process rolesets for {predicate_name}: {e}")
                    continue
    
    def _add_roles_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        predicates_data: Dict[str, Any],
        selected_predicates: List[str],
        max_roles_per_roleset: int
    ) -> None:
        """Add role nodes as children of roleset nodes."""
        for predicate_name in selected_predicates:
            predicate_data = predicates_data.get(predicate_name, {})
            rolesets = predicate_data.get('rolesets', [])
            
            if rolesets and not isinstance(rolesets, slice):
                try:
                    for i, roleset in enumerate(rolesets):
                        if isinstance(roleset, slice):
                            continue
                        if isinstance(roleset, dict):
                            rs_id = roleset.get('id', f'{predicate_name}.{i:02d}')
                            rs_roles = roleset.get('roles', [])
                        else:
                            rs_id = f'{predicate_name}.{i:02d}'
                            rs_roles = []
                        
                        # Only process if this roleset is in our graph
                        if rs_id not in G.nodes():
                            continue
                        
                        # Add limited number of roles
                        if rs_roles and not isinstance(rs_roles, slice):
                            role_slice = rs_roles[:max_roles_per_roleset]
                            if isinstance(role_slice, slice):
                                continue
                            
                            for j, role in enumerate(role_slice):
                                if isinstance(role, slice):
                                    continue
                                if isinstance(role, dict):
                                    role_number = role.get('number', str(j))
                                    role_description = role.get('description', f'role_{j}')
                                    role_function = role.get('function', '')
                                    role_vnroles = role.get('vnroles', [])
                                else:
                                    role_number = str(j)
                                    role_description = str(role)
                                    role_function = ''
                                    role_vnroles = []
                                
                                # Create unique node name
                                role_node_name = f"Arg{role_number}@{rs_id}"
                                
                                # Add role node
                                self.add_node_with_hierarchy(
                                    G, hierarchy, role_node_name,
                                    node_type='role',
                                    parents=[rs_id],
                                    info={
                                        'node_type': 'role',
                                        'name': f"Arg{role_number}",
                                        'role_number': role_number,
                                        'description': role_description,
                                        'function': role_function,
                                        'predicate': predicate_name,
                                        'vnroles': role_vnroles
                                    }
                                )
                except Exception as e:
                    print(f"Warning: Could not process roles for {predicate_name}: {e}")
                    continue
    
    def _add_examples_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        predicates_data: Dict[str, Any],
        selected_predicates: List[str],
        max_examples_per_roleset: int
    ) -> None:
        """Add example nodes as children of roleset nodes."""
        for predicate_name in selected_predicates:
            predicate_data = predicates_data.get(predicate_name, {})
            rolesets = predicate_data.get('rolesets', [])
            
            if rolesets and not isinstance(rolesets, slice):
                try:
                    for i, roleset in enumerate(rolesets):
                        if isinstance(roleset, slice):
                            continue
                        if isinstance(roleset, dict):
                            rs_id = roleset.get('id', f'{predicate_name}.{i:02d}')
                            rs_examples = roleset.get('examples', [])
                        else:
                            rs_id = f'{predicate_name}.{i:02d}'
                            rs_examples = []
                        
                        # Only process if this roleset is in our graph
                        if rs_id not in G.nodes():
                            continue
                        
                        # Add limited number of examples
                        if rs_examples and not isinstance(rs_examples, slice):
                            ex_slice = rs_examples[:max_examples_per_roleset]
                            if isinstance(ex_slice, slice):
                                continue
                            
                            for j, example in enumerate(ex_slice):
                                if isinstance(example, slice):
                                    continue
                                if isinstance(example, dict):
                                    ex_name = example.get('name', f'example_{j}')
                                    ex_text = example.get('text', '')
                                    ex_arguments = example.get('arguments', [])
                                    ex_predicate = example.get('predicate', '')
                                else:
                                    ex_name = f'example_{j}'
                                    ex_text = str(example)
                                    ex_arguments = []
                                    ex_predicate = ''
                                
                                # Create unique node name
                                ex_node_name = f"{ex_name}#{rs_id}"
                                
                                # Add example node
                                self.add_node_with_hierarchy(
                                    G, hierarchy, ex_node_name,
                                    node_type='example',
                                    parents=[rs_id],
                                    info={
                                        'node_type': 'example',
                                        'name': ex_name,
                                        'text': ex_text,
                                        'arguments': ex_arguments,
                                        'predicate': ex_predicate,
                                        'roleset': rs_id
                                    }
                                )
                except Exception as e:
                    print(f"Warning: Could not process examples for {predicate_name}: {e}")
                    continue
    
    def _add_aliases_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        predicates_data: Dict[str, Any],
        selected_predicates: List[str]
    ) -> None:
        """Add alias nodes as children of predicate nodes."""
        for predicate_name in selected_predicates:
            predicate_data = predicates_data.get(predicate_name, {})
            aliases = predicate_data.get('aliases', [])
            
            # Add aliases
            if aliases and not isinstance(aliases, slice):
                try:
                    # Limit aliases to avoid too many nodes
                    alias_slice = aliases[:3]  # Max 3 aliases per predicate
                    if isinstance(alias_slice, slice):
                        continue
                    
                    for i, alias in enumerate(alias_slice):
                        if isinstance(alias, slice):
                            continue
                        if isinstance(alias, dict):
                            alias_name = alias.get('name', f'alias_{i}')
                            alias_pos = alias.get('pos', 'Unknown')
                        else:
                            alias_name = str(alias)
                            alias_pos = 'Unknown'
                        
                        # Create unique node name
                        alias_node_name = f"{alias_name}~{predicate_name}"
                        
                        # Add alias node
                        self.add_node_with_hierarchy(
                            G, hierarchy, alias_node_name,
                            node_type='alias',
                            parents=[predicate_name],
                            info={
                                'node_type': 'alias',
                                'name': alias_name,
                                'pos': alias_pos,
                                'predicate': predicate_name
                            }
                        )
                except Exception as e:
                    print(f"Warning: Could not process aliases for {predicate_name}: {e}")
                    continue
    
    def _create_predicate_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_predicates: List[str]
    ) -> None:
        """Create some demo connections between predicates."""
        # Connect predicates in a simple chain/hierarchy for demo purposes
        # In a real scenario, these would come from semantic relations data
        for i in range(1, len(selected_predicates)):
            if i == 1:
                # First connection: make second predicate child of first
                self.connect_nodes(G, hierarchy, selected_predicates[0], selected_predicates[i])
            elif i == len(selected_predicates) - 1 and len(selected_predicates) > 3:
                # Last connection: connect to middle predicate for more interesting structure
                mid_idx = len(selected_predicates) // 2
                self.connect_nodes(G, hierarchy, selected_predicates[mid_idx], selected_predicates[i])
            elif i < len(selected_predicates) - 1:
                # Middle predicates: create a chain
                prev_predicate = selected_predicates[i - 1] if i % 2 == 0 else selected_predicates[0]
                self.connect_nodes(G, hierarchy, prev_predicate, selected_predicates[i])
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """Display PropBank-specific node information."""
        if node in hierarchy:
            predicate_info = hierarchy[node].get('predicate_info', {})
            node_type = predicate_info.get('node_type', 'predicate')
            
            if node_type == 'predicate':
                rolesets = predicate_info.get('rolesets', 0)
                aliases = predicate_info.get('aliases', 0)
                print(f"  {node} (Predicate): {rolesets} rolesets, {aliases} aliases")
            elif node_type == 'roleset':
                predicate = predicate_info.get('predicate', 'Unknown')
                roles = predicate_info.get('roles', [])
                examples = predicate_info.get('examples', [])
                print(f"  {node} (Roleset): {len(roles)} roles, {len(examples)} examples from {predicate}")
            elif node_type == 'role':
                role_number = predicate_info.get('role_number', 'Unknown')
                predicate = predicate_info.get('predicate', 'Unknown')
                print(f"  {node} (Role Arg{role_number}): from {predicate}")
            elif node_type == 'example':
                roleset = predicate_info.get('roleset', 'Unknown')
                arguments = predicate_info.get('arguments', [])
                print(f"  {node} (Example): {len(arguments)} arguments from {roleset}")
            elif node_type == 'alias':
                pos = predicate_info.get('pos', 'Unknown')
                predicate = predicate_info.get('predicate', 'Unknown')
                print(f"  {node} (Alias): {pos} from {predicate}")
            else:
                super()._display_node_info(node, hierarchy)