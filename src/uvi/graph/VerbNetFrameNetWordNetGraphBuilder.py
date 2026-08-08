"""
VerbNet-FrameNet-WordNet Integrated Graph Builder.

This module contains the VerbNetFrameNetWordNetGraphBuilder class for creating
integrated semantic graphs that link VerbNet classes with FrameNet frames and
WordNet synsets using VerbNet's cross-corpus mappings.
"""

import networkx as nx
from typing import Dict, Any, Tuple, Optional, List, Set

from .GraphBuilder import GraphBuilder


class VerbNetFrameNetWordNetGraphBuilder(GraphBuilder):
    """Specialized graph builder for integrating VerbNet, FrameNet, and WordNet."""
    
    def __init__(self):
        """Initialize the VerbNetFrameNetWordNetGraphBuilder."""
        super().__init__()
    
    def create_integrated_graph(
        self,
        verbnet_data: Dict[str, Any],
        framenet_data: Dict[str, Any],
        wordnet_data: Dict[str, Any],
        num_vn_classes: int = 5,
        max_fn_frames_per_class: int = 2,
        max_wn_synsets_per_class: int = 2,
        include_members: bool = True,
        max_members_per_class: int = 3
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create an integrated semantic graph linking VerbNet, FrameNet, and WordNet.
        
        Args:
            verbnet_data: VerbNet data dictionary
            framenet_data: FrameNet data dictionary
            wordnet_data: WordNet data dictionary
            num_vn_classes: Number of VerbNet classes to include
            max_fn_frames_per_class: Maximum FrameNet frames per VerbNet class
            max_wn_synsets_per_class: Maximum WordNet synsets per VerbNet class
            include_members: Whether to include member verbs
            max_members_per_class: Maximum member verbs to show per class
            
        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating integrated VerbNet-FrameNet-WordNet graph...")
        print(f"  VerbNet classes: {num_vn_classes}")
        print(f"  Max FrameNet frames per class: {max_fn_frames_per_class}")
        print(f"  Max WordNet synsets per class: {max_wn_synsets_per_class}")
        
        # Get corpus data
        vn_classes = verbnet_data.get('classes', {})
        fn_frames = framenet_data.get('frames', {})
        wn_synsets = wordnet_data.get('synsets', {})
        
        if not vn_classes:
            print("No VerbNet classes available")
            return None, {}
        
        print(f"Found {len(vn_classes)} VerbNet classes")
        print(f"Found {len(fn_frames)} FrameNet frames")
        print(f"Found {sum(len(s) for s in wn_synsets.values())} WordNet synsets")
        
        # Create graph and hierarchy
        G = nx.DiGraph()
        hierarchy = {}
        
        # Track nodes by type for statistics
        vn_nodes = set()
        fn_nodes = set()
        wn_nodes = set()
        member_nodes = set()
        
        # Select VerbNet classes to include
        sorted_classes = sorted(vn_classes.items())[:num_vn_classes]
        
        for class_id, class_data in sorted_classes:
            # Extract main verb from class ID
            main_verb = class_id.split('-')[0]
            vn_class_name = f"VN:{main_verb}-{class_id.split('-')[1]}"
            
            # Add VerbNet class node
            self.add_node_with_hierarchy(
                G, hierarchy, vn_class_name,
                node_type='verbnet_class',
                info={
                    'node_type': 'verbnet_class',
                    'corpus': 'verbnet',
                    'class_id': class_id,
                    'members': self._get_class_members(class_data, max_members_per_class),
                    'themroles': self._get_class_themroles(class_data)
                }
            )
            vn_nodes.add(vn_class_name)
            
            # Add member verbs if requested
            if include_members:
                members = self._get_class_members(class_data, max_members_per_class)
                for member in members[:max_members_per_class]:
                    member_name = f"VERB:{member}"
                    
                    if member_name not in G.nodes():
                        self.add_node_with_hierarchy(
                            G, hierarchy, member_name,
                            node_type='verb_member',
                            parents=[vn_class_name],
                            info={
                                'node_type': 'verb_member',
                                'lemma': member,
                                'verbnet_class': vn_class_name
                            }
                        )
                        member_nodes.add(member_name)
                    else:
                        # Just add edge if node exists
                        self.connect_nodes(G, hierarchy, vn_class_name, member_name)
            
            # Find and add related FrameNet frames
            fn_mappings = self._get_framenet_mappings(class_data, fn_frames)
            for i, (frame_name, frame_data) in enumerate(fn_mappings[:max_fn_frames_per_class]):
                fn_node_name = f"FN:{frame_name}"
                
                if fn_node_name not in G.nodes():
                    # Add FrameNet frame node
                    self.add_node_with_hierarchy(
                        G, hierarchy, fn_node_name,
                        node_type='framenet_frame',
                        info={
                            'node_type': 'framenet_frame',
                            'corpus': 'framenet',
                            'frame_name': frame_name,
                            'definition': frame_data.get('definition', ''),
                            'lexical_units': len(frame_data.get('lexical_units', []))
                        }
                    )
                    fn_nodes.add(fn_node_name)
                
                # Connect VerbNet class to FrameNet frame
                self.connect_nodes(G, hierarchy, vn_class_name, fn_node_name)
                
                # Connect member verbs to FrameNet frame if they're lexical units
                if include_members:
                    lexical_units = self._get_frame_lexical_units(frame_data)
                    for member in members[:max_members_per_class]:
                        if self._is_lexical_unit(member, lexical_units):
                            member_name = f"VERB:{member}"
                            if member_name in G.nodes() and fn_node_name in G.nodes():
                                self.connect_nodes(G, hierarchy, member_name, fn_node_name)
            
            # Find and add related WordNet synsets
            wn_mappings = self._get_wordnet_mappings(class_data, wn_synsets, main_verb)
            for i, (synset_id, synset_words, synset_def) in enumerate(wn_mappings[:max_wn_synsets_per_class]):
                wn_node_name = f"WN:{synset_words[0] if synset_words else synset_id}"
                
                if wn_node_name not in G.nodes():
                    # Add WordNet synset node
                    self.add_node_with_hierarchy(
                        G, hierarchy, wn_node_name,
                        node_type='wordnet_synset',
                        info={
                            'node_type': 'wordnet_synset',
                            'corpus': 'wordnet',
                            'synset_id': synset_id,
                            'words': synset_words,
                            'definition': synset_def
                        }
                    )
                    wn_nodes.add(wn_node_name)
                
                # Connect VerbNet class to WordNet synset
                self.connect_nodes(G, hierarchy, vn_class_name, wn_node_name)
                
                # Connect member verbs to WordNet synset if they're in the synset
                if include_members:
                    for member in members[:max_members_per_class]:
                        if member in synset_words:
                            member_name = f"VERB:{member}"
                            if member_name in G.nodes() and wn_node_name in G.nodes():
                                self.connect_nodes(G, hierarchy, member_name, wn_node_name)
        
        # Add cross-corpus connections between FrameNet and WordNet
        self._add_cross_corpus_connections(G, hierarchy, fn_nodes, wn_nodes)
        
        # Calculate node depths
        root_nodes = [n for n in vn_nodes]  # VerbNet classes as roots
        self.calculate_node_depths(G, hierarchy, root_nodes)
        
        # Display statistics
        custom_stats = {
            'VerbNet Classes': len(vn_nodes),
            'FrameNet Frames': len(fn_nodes),
            'WordNet Synsets': len(wn_nodes),
            'Member Verbs': len(member_nodes),
            'Cross-corpus Links': self._count_cross_corpus_edges(G)
        }
        self.display_graph_statistics(G, hierarchy, custom_stats)
        
        return G, hierarchy
    
    def _get_class_members(self, class_data: Dict[str, Any], max_members: int = 5) -> List[str]:
        """Extract member verbs from a VerbNet class."""
        members = class_data.get('members', [])
        if isinstance(members, list):
            if members and isinstance(members[0], dict):
                return [m.get('name', m.get('lemma', 'unknown')) for m in members[:max_members]]
            return members[:max_members]
        return []
    
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
    
    def _get_framenet_mappings(
        self,
        vn_class_data: Dict[str, Any],
        fn_frames: Dict[str, Any]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Find FrameNet frames mapped to this VerbNet class."""
        mappings = []
        
        # Check for explicit FrameNet mappings in VerbNet data
        fn_mappings = vn_class_data.get('framenet_mappings', [])
        if fn_mappings:
            for mapping in fn_mappings[:3]:  # Limit to first 3
                if isinstance(mapping, dict):
                    frame_name = mapping.get('frame', mapping.get('frame_name', ''))
                elif isinstance(mapping, str):
                    frame_name = mapping
                else:
                    continue
                
                if frame_name in fn_frames:
                    mappings.append((frame_name, fn_frames[frame_name]))
        
        # If no explicit mappings, try to find frames by member verbs
        if not mappings:
            members = self._get_class_members(vn_class_data, 10)
            for frame_name, frame_data in fn_frames.items():
                if len(mappings) >= 3:
                    break
                
                lexical_units = self._get_frame_lexical_units(frame_data)
                # Check if any member verb is a lexical unit of this frame
                for member in members:
                    if self._is_lexical_unit(member, lexical_units):
                        mappings.append((frame_name, frame_data))
                        break
        
        # If still no mappings, use semantic similarity heuristics
        if not mappings:
            # Simple heuristic: match frames with similar names to class members
            class_id = vn_class_data.get('id', '')
            main_verb = class_id.split('-')[0] if '-' in class_id else ''
            
            for frame_name, frame_data in fn_frames.items():
                if len(mappings) >= 2:
                    break
                
                # Check if main verb appears in frame name or definition
                frame_name_lower = frame_name.lower()
                definition = frame_data.get('definition', '').lower()
                
                if main_verb and (main_verb.lower() in frame_name_lower or 
                                  main_verb.lower() in definition):
                    mappings.append((frame_name, frame_data))
        
        return mappings
    
    def _get_wordnet_mappings(
        self,
        vn_class_data: Dict[str, Any],
        wn_synsets: Dict[str, Any],
        main_verb: str
    ) -> List[Tuple[str, List[str], str]]:
        """Find WordNet synsets mapped to this VerbNet class."""
        mappings = []
        
        # Check for explicit WordNet mappings in VerbNet data
        wn_mappings = vn_class_data.get('wordnet_mappings', [])
        if wn_mappings:
            for mapping in wn_mappings[:3]:  # Limit to first 3
                synset_id = None
                if isinstance(mapping, dict):
                    synset_id = mapping.get('synset', mapping.get('synset_id', ''))
                elif isinstance(mapping, str):
                    synset_id = mapping
                
                if synset_id:
                    # Look for synset in verb synsets
                    verb_synsets = wn_synsets.get('verb', {})
                    if synset_id in verb_synsets:
                        synset_data = verb_synsets[synset_id]
                        words = self._get_synset_words(synset_data)
                        definition = synset_data.get('gloss', 'No definition')
                        mappings.append((synset_id, words, definition))
        
        # If no explicit mappings, try to find synsets by member verbs
        if not mappings:
            members = self._get_class_members(vn_class_data, 10)
            verb_synsets = wn_synsets.get('verb', {})
            
            for synset_id, synset_data in verb_synsets.items():
                if len(mappings) >= 3:
                    break
                
                words = self._get_synset_words(synset_data)
                # Check if any member verb is in this synset
                for member in members:
                    if member in words:
                        definition = synset_data.get('gloss', 'No definition')
                        mappings.append((synset_id, words, definition))
                        break
        
        # If still no mappings, try main verb
        if not mappings and main_verb:
            verb_synsets = wn_synsets.get('verb', {})
            count = 0
            for synset_id, synset_data in verb_synsets.items():
                if count >= 2:
                    break
                
                words = self._get_synset_words(synset_data)
                if main_verb in words:
                    definition = synset_data.get('gloss', 'No definition')
                    mappings.append((synset_id, words, definition))
                    count += 1
        
        return mappings
    
    def _get_synset_words(self, synset_data: Dict[str, Any]) -> List[str]:
        """Extract words from a WordNet synset."""
        words = synset_data.get('words', [])
        if isinstance(words, list) and words:
            if isinstance(words[0], dict):
                return [w.get('word', w.get('lemma', '')) for w in words]
            return words
        return []
    
    def _get_frame_lexical_units(self, frame_data: Dict[str, Any]) -> List[str]:
        """Extract lexical units from a FrameNet frame."""
        lexical_units = frame_data.get('lexical_units', [])
        lu_names = []
        
        if isinstance(lexical_units, list) and not isinstance(lexical_units, slice):
            for lu in lexical_units[:10]:  # Limit for efficiency
                if isinstance(lu, dict):
                    lu_name = lu.get('name', '')
                    # Extract just the word part (before the dot)
                    if '.' in lu_name:
                        lu_name = lu_name.split('.')[0]
                    if lu_name:
                        lu_names.append(lu_name)
                elif isinstance(lu, str):
                    if '.' in lu:
                        lu = lu.split('.')[0]
                    lu_names.append(lu)
        
        return lu_names
    
    def _is_lexical_unit(self, verb: str, lexical_units: List[str]) -> bool:
        """Check if a verb is among the lexical units."""
        verb_lower = verb.lower()
        return any(verb_lower == lu.lower() for lu in lexical_units)
    
    def _add_cross_corpus_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        fn_nodes: Set[str],
        wn_nodes: Set[str]
    ) -> None:
        """Add connections between FrameNet and WordNet based on semantic similarity."""
        # This is a simplified version - in practice, you'd use more sophisticated mapping
        
        # Connect frames and synsets that share lexical items
        for fn_node in fn_nodes:
            fn_info = hierarchy.get(fn_node, {}).get('frame_info', {})
            frame_name = fn_info.get('frame_name', '')
            
            for wn_node in wn_nodes:
                wn_info = hierarchy.get(wn_node, {}).get('synset_info', {})
                words = wn_info.get('words', [])
                
                # Simple heuristic: connect if frame name contains any synset word
                for word in words:
                    if word.lower() in frame_name.lower():
                        if not G.has_edge(fn_node, wn_node) and not G.has_edge(wn_node, fn_node):
                            G.add_edge(fn_node, wn_node, relation_type='semantic_similarity')
                        break
    
    def _count_cross_corpus_edges(self, G: nx.DiGraph) -> int:
        """Count edges between nodes from different corpora."""
        count = 0
        for edge in G.edges():
            source, target = edge
            # Check if nodes are from different corpora based on prefix
            source_corpus = source.split(':')[0] if ':' in source else ''
            target_corpus = target.split(':')[0] if ':' in target else ''
            
            if source_corpus and target_corpus and source_corpus != target_corpus:
                count += 1
        
        return count
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """Display integrated node information."""
        if node in hierarchy:
            node_data = hierarchy[node]
            
            # Find the info dictionary
            info = None
            for key in ['node_info', 'frame_info', 'synset_info', 'verb_info']:
                if key in node_data:
                    info = node_data[key]
                    break
            
            if not info:
                super()._display_node_info(node, hierarchy)
                return
            
            node_type = info.get('node_type', 'unknown')
            corpus = info.get('corpus', '')
            
            if node_type == 'verbnet_class':
                members = info.get('members', [])
                themroles = info.get('themroles', [])
                print(f"  {node} (VerbNet Class): {len(members)} members, {len(themroles)} thematic roles")
            elif node_type == 'framenet_frame':
                lexical_units = info.get('lexical_units', 0)
                print(f"  {node} (FrameNet Frame): {lexical_units} lexical units")
            elif node_type == 'wordnet_synset':
                words = info.get('words', [])
                print(f"  {node} (WordNet Synset): {len(words)} words")
            elif node_type == 'verb_member':
                lemma = info.get('lemma', 'unknown')
                print(f"  {node} (Member Verb): lemma='{lemma}'")
            else:
                super()._display_node_info(node, hierarchy)