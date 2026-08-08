"""
WordNet Parser Module

Specialized parser for WordNet data files. Handles parsing of WordNet's custom
text-based format including data files, index files, and exception lists.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re


class WordNetParser:
    """
    Parser for WordNet data files.
    
    Handles parsing of WordNet's custom text-based format including synsets,
    word indices, semantic relations, and exception lists.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize WordNet parser with corpus path.
        
        Args:
            corpus_path (Path): Path to WordNet corpus directory
        """
        self.corpus_path = corpus_path
        
        # WordNet file mappings
        self.data_files = {
            'noun': corpus_path / 'data.noun' if corpus_path else None,
            'verb': corpus_path / 'data.verb' if corpus_path else None,
            'adj': corpus_path / 'data.adj' if corpus_path else None,
            'adv': corpus_path / 'data.adv' if corpus_path else None
        }
        
        self.index_files = {
            'noun': corpus_path / 'index.noun' if corpus_path else None,
            'verb': corpus_path / 'index.verb' if corpus_path else None,
            'adj': corpus_path / 'index.adj' if corpus_path else None,
            'adv': corpus_path / 'index.adv' if corpus_path else None
        }
        
        self.exception_files = {
            'noun': corpus_path / 'noun.exc' if corpus_path else None,
            'verb': corpus_path / 'verb.exc' if corpus_path else None,
            'adj': corpus_path / 'adj.exc' if corpus_path else None,
            'adv': corpus_path / 'adv.exc' if corpus_path else None
        }
        
        # WordNet relation types
        self.relation_types = {
            '!': 'antonym',
            '@': 'hypernym',
            '~': 'hyponym',
            '#m': 'member_holonym',
            '#s': 'substance_holonym',
            '#p': 'part_holonym',
            '%m': 'member_meronym',
            '%s': 'substance_meronym',
            '%p': 'part_meronym',
            '=': 'attribute',
            '+': 'derivationally_related',
            ';c': 'domain_topic',
            ';r': 'domain_region',
            ';u': 'exemplifies',
            '-c': 'member_topic',
            '-r': 'member_region',
            '-u': 'is_exemplified_by',
            '*': 'entailment',
            '>': 'cause',
            '^': 'also',
            '$': 'verb_group',
            '&': 'similar_to',
            '<': 'participle',
            '\\': 'pertainym'
        }
    
    def parse_all_data(self) -> Dict[str, Any]:
        """
        Parse all WordNet data files.
        
        Returns:
            dict: Complete WordNet data
        """
        wordnet_data = {
            'synsets': {},
            'index': {},
            'exceptions': {},
            'statistics': {}
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return wordnet_data
        
        # Parse data files (synsets)
        for pos, data_file in self.data_files.items():
            if data_file and data_file.exists():
                try:
                    synsets = self.parse_data_file(data_file, pos)
                    wordnet_data['synsets'][pos] = synsets
                except Exception as e:
                    print(f"Error parsing WordNet data file {data_file}: {e}")
        
        # Parse index files
        for pos, index_file in self.index_files.items():
            if index_file and index_file.exists():
                try:
                    index = self.parse_index_file(index_file, pos)
                    wordnet_data['index'][pos] = index
                except Exception as e:
                    print(f"Error parsing WordNet index file {index_file}: {e}")
        
        # Parse exception files
        for pos, exc_file in self.exception_files.items():
            if exc_file and exc_file.exists():
                try:
                    exceptions = self.parse_exception_file(exc_file)
                    wordnet_data['exceptions'][pos] = exceptions
                except Exception as e:
                    print(f"Error parsing WordNet exception file {exc_file}: {e}")
        
        # Generate statistics
        wordnet_data['statistics'] = self._generate_statistics(wordnet_data)
        
        return wordnet_data
    
    def parse_data_file(self, file_path: Path, pos: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse a WordNet data file to extract synsets.
        
        Args:
            file_path (Path): Path to data file
            pos (str): Part of speech
            
        Returns:
            dict: Parsed synsets keyed by synset offset
        """
        synsets = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments, empty lines, and copyright headers
                if (line and 
                    not line.startswith('  ') and 
                    not line.startswith('Princeton') and 
                    not line.startswith('Copyright') and
                    not 'Princeton' in line):
                    synset_data = self._parse_synset_line(line, pos)
                    if synset_data:
                        synsets[synset_data['synset_offset']] = synset_data
        
        return synsets
    
    def _parse_synset_line(self, line: str, pos: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single synset line from a data file.
        
        Args:
            line (str): Synset line from data file
            pos (str): Part of speech
            
        Returns:
            dict: Parsed synset data
        """
        try:
            parts = line.split(' ')
            if len(parts) < 6:
                return None
            
            synset_offset = parts[0]
            lex_filenum = parts[1]
            ss_type = parts[2]
            w_cnt = int(parts[3], 16)  # Hexadecimal
            
            # Parse words
            words = []
            word_start = 4
            for i in range(w_cnt):
                word = parts[word_start + i * 2]
                lex_id = parts[word_start + i * 2 + 1]
                words.append({'word': word, 'lex_id': lex_id})
            
            # Parse pointer count and pointers
            ptr_cnt_idx = word_start + w_cnt * 2
            p_cnt = int(parts[ptr_cnt_idx])
            
            pointers = []
            ptr_start = ptr_cnt_idx + 1
            for i in range(p_cnt):
                if ptr_start + i * 4 + 3 < len(parts):
                    pointer_symbol = parts[ptr_start + i * 4]
                    synset_offset_target = parts[ptr_start + i * 4 + 1]
                    pos_target = parts[ptr_start + i * 4 + 2]
                    source_target = parts[ptr_start + i * 4 + 3]
                    
                    pointers.append({
                        'symbol': pointer_symbol,
                        'relation_type': self.relation_types.get(pointer_symbol, pointer_symbol),
                        'synset_offset': synset_offset_target,
                        'pos': pos_target,
                        'source_target': source_target
                    })
            
            # Parse frames for verbs
            frames = []
            frame_start = ptr_start + p_cnt * 4
            if pos == 'verb' and frame_start < len(parts):
                try:
                    f_cnt = int(parts[frame_start])
                    for i in range(f_cnt):
                        if frame_start + 1 + i * 3 + 2 < len(parts):
                            frame_data = {
                                'f_num': parts[frame_start + 1 + i * 3 + 1],
                                'w_num': parts[frame_start + 1 + i * 3 + 2]
                            }
                            frames.append(frame_data)
                except (ValueError, IndexError):
                    pass
            
            # Extract gloss (definition)
            gloss_start = line.find('|')
            gloss = line[gloss_start + 1:].strip() if gloss_start != -1 else ""
            
            return {
                'synset_offset': synset_offset,
                'lex_filenum': lex_filenum,
                'ss_type': ss_type,
                'words': words,
                'pointers': pointers,
                'frames': frames,
                'gloss': gloss,
                'pos': pos
            }
        except Exception as e:
            print(f"Error parsing synset line: {e}")
            return None
    
    def parse_index_file(self, file_path: Path, pos: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse a WordNet index file.
        
        Args:
            file_path (Path): Path to index file
            pos (str): Part of speech
            
        Returns:
            dict: Parsed index entries keyed by lemma
        """
        index = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments, empty lines, and copyright headers
                if (line and 
                    not line.startswith('  ') and 
                    not line.startswith('Princeton') and 
                    not line.startswith('Copyright') and
                    not 'Princeton' in line):
                    index_entry = self._parse_index_line(line, pos)
                    if index_entry:
                        index[index_entry['lemma']] = index_entry
        
        return index
    
    def _parse_index_line(self, line: str, pos: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single index line.
        
        Args:
            line (str): Index line
            pos (str): Part of speech
            
        Returns:
            dict: Parsed index entry
        """
        try:
            parts = line.split(' ')
            if len(parts) < 4:
                return None
            
            lemma = parts[0]
            pos_tag = parts[1]
            synset_cnt = int(parts[2])
            p_cnt = int(parts[3])
            
            # Parse pointer symbols
            pointer_symbols = parts[4:4 + p_cnt]
            
            # Parse sense count and tagged sense count
            sense_cnt_idx = 4 + p_cnt
            try:
                sense_cnt = int(parts[sense_cnt_idx]) if sense_cnt_idx < len(parts) else 0
            except (ValueError, IndexError):
                sense_cnt = 0
            try:
                tagsense_cnt = int(parts[sense_cnt_idx + 1]) if sense_cnt_idx + 1 < len(parts) else 0
            except (ValueError, IndexError):
                tagsense_cnt = 0
            
            # Parse synset offsets
            synset_offsets = parts[sense_cnt_idx + 2:sense_cnt_idx + 2 + synset_cnt]
            
            return {
                'lemma': lemma,
                'pos': pos_tag,
                'synset_cnt': synset_cnt,
                'p_cnt': p_cnt,
                'pointer_symbols': pointer_symbols,
                'sense_cnt': sense_cnt,
                'tagsense_cnt': tagsense_cnt,
                'synset_offsets': synset_offsets
            }
        except Exception as e:
            print(f"Error parsing index line: {e}")
            return None
    
    def parse_exception_file(self, file_path: Path) -> Dict[str, List[str]]:
        """
        Parse a WordNet exception file.
        
        Args:
            file_path (Path): Path to exception file
            
        Returns:
            dict: Exception mappings
        """
        exceptions = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        surface_form = parts[0]
                        base_forms = parts[1:]
                        exceptions[surface_form] = base_forms
        
        return exceptions
    
    def get_synset_by_offset(self, offset: str, pos: str, wordnet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get synset by offset and POS.
        
        Args:
            offset (str): Synset offset
            pos (str): Part of speech
            wordnet_data (dict): Parsed WordNet data
            
        Returns:
            dict: Synset data or None if not found
        """
        synsets = wordnet_data.get('synsets', {}).get(pos, {})
        return synsets.get(offset)
    
    def get_synsets_for_word(self, word: str, pos: str, wordnet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all synsets for a word.
        
        Args:
            word (str): Word to look up
            pos (str): Part of speech
            wordnet_data (dict): Parsed WordNet data
            
        Returns:
            list: List of synsets containing the word
        """
        synsets = []
        
        # Check if word exists in index
        index = wordnet_data.get('index', {}).get(pos, {})
        index_entry = index.get(word.lower())
        
        if index_entry:
            synset_offsets = index_entry.get('synset_offsets', [])
            pos_synsets = wordnet_data.get('synsets', {}).get(pos, {})
            
            for offset in synset_offsets:
                synset = pos_synsets.get(offset)
                if synset:
                    synsets.append(synset)
        
        return synsets
    
    def get_related_synsets(self, synset: Dict[str, Any], relation_type: str, 
                           wordnet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get synsets related by a specific relation type.
        
        Args:
            synset (dict): Source synset
            relation_type (str): Type of relation
            wordnet_data (dict): Parsed WordNet data
            
        Returns:
            list: Related synsets
        """
        related = []
        
        for pointer in synset.get('pointers', []):
            if pointer.get('relation_type') == relation_type:
                target_offset = pointer.get('synset_offset')
                target_pos = pointer.get('pos')
                
                target_synset = self.get_synset_by_offset(target_offset, target_pos, wordnet_data)
                if target_synset:
                    related.append(target_synset)
        
        return related
    
    def _generate_statistics(self, wordnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics for WordNet data."""
        stats = {
            'synset_counts': {},
            'word_counts': {},
            'relation_counts': {}
        }
        
        for pos, synsets in wordnet_data.get('synsets', {}).items():
            stats['synset_counts'][pos] = len(synsets)
            
            word_set = set()
            relation_counts = {}
            
            for synset in synsets.values():
                # Count unique words
                for word_data in synset.get('words', []):
                    word_set.add(word_data.get('word', ''))
                
                # Count relations
                for pointer in synset.get('pointers', []):
                    relation = pointer.get('relation_type', 'unknown')
                    relation_counts[relation] = relation_counts.get(relation, 0) + 1
            
            stats['word_counts'][pos] = len(word_set)
            stats['relation_counts'][pos] = relation_counts
        
        return stats