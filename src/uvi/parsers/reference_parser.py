"""
Reference Documentation Parser Module

Specialized parser for reference documentation files. Handles parsing of
predicate definitions, thematic roles, constants, and verb-specific features
from JSON and TSV files.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


class ReferenceParser:
    """
    Parser for reference documentation files.
    
    Handles parsing of VerbNet reference documentation including predicate
    definitions, thematic role definitions, constants, and verb-specific features.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize reference parser with corpus path.
        
        Args:
            corpus_path (Path): Path to reference docs directory
        """
        self.corpus_path = corpus_path
        
        # Expected reference files
        self.predicate_file = corpus_path / "pred_calc_for_website_final.json" if corpus_path else None
        self.themrole_file = corpus_path / "themrole_defs.json" if corpus_path else None
        self.constants_file = corpus_path / "vn_constants.tsv" if corpus_path else None
        self.semantic_predicates_file = corpus_path / "vn_semantic_predicates.tsv" if corpus_path else None
        self.verb_specific_file = corpus_path / "vn_verb_specific_predicates.tsv" if corpus_path else None
    
    def parse_all_references(self) -> Dict[str, Any]:
        """
        Parse all reference documentation files.
        
        Returns:
            dict: Complete reference documentation data
        """
        reference_data = {
            'predicates': {},
            'themroles': {},
            'constants': {},
            'semantic_predicates': {},
            'verb_specific_predicates': {}
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return reference_data
        
        # Parse predicate definitions
        if self.predicate_file and self.predicate_file.exists():
            try:
                predicates = self.parse_predicate_file(self.predicate_file)
                reference_data['predicates'] = predicates
            except Exception as e:
                print(f"Error parsing predicate file: {e}")
        
        # Parse thematic role definitions
        if self.themrole_file and self.themrole_file.exists():
            try:
                themroles = self.parse_themrole_file(self.themrole_file)
                reference_data['themroles'] = themroles
            except Exception as e:
                print(f"Error parsing thematic role file: {e}")
        
        # Parse constants
        if self.constants_file and self.constants_file.exists():
            try:
                constants = self.parse_constants_file(self.constants_file)
                reference_data['constants'] = constants
            except Exception as e:
                print(f"Error parsing constants file: {e}")
        
        # Parse semantic predicates
        if self.semantic_predicates_file and self.semantic_predicates_file.exists():
            try:
                semantic_predicates = self.parse_semantic_predicates_file(self.semantic_predicates_file)
                reference_data['semantic_predicates'] = semantic_predicates
            except Exception as e:
                print(f"Error parsing semantic predicates file: {e}")
        
        # Parse verb-specific predicates
        if self.verb_specific_file and self.verb_specific_file.exists():
            try:
                verb_specific = self.parse_verb_specific_file(self.verb_specific_file)
                reference_data['verb_specific_predicates'] = verb_specific
            except Exception as e:
                print(f"Error parsing verb-specific predicates file: {e}")
        
        return reference_data
    
    def parse_predicate_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse predicate definitions JSON file.
        
        Args:
            file_path (Path): Path to predicate definitions JSON file
            
        Returns:
            dict: Parsed predicate definitions
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        predicates = {}
        
        # Process predicate data
        for predicate_name, predicate_info in raw_data.items():
            predicates[predicate_name] = self._process_predicate_definition(predicate_name, predicate_info)
        
        return predicates
    
    def _process_predicate_definition(self, predicate_name: str, predicate_info: Any) -> Dict[str, Any]:
        """
        Process a single predicate definition.
        
        Args:
            predicate_name (str): Name of the predicate
            predicate_info: Raw predicate information
            
        Returns:
            dict: Processed predicate definition
        """
        if isinstance(predicate_info, dict):
            return {
                'name': predicate_name,
                'definition': predicate_info.get('definition', ''),
                'description': predicate_info.get('description', ''),
                'arguments': predicate_info.get('arguments', []),
                'examples': predicate_info.get('examples', []),
                'usage': predicate_info.get('usage', ''),
                'category': predicate_info.get('category', ''),
                'attributes': {k: v for k, v in predicate_info.items() 
                             if k not in ['definition', 'description', 'arguments', 'examples', 'usage', 'category']}
            }
        else:
            return {
                'name': predicate_name,
                'definition': str(predicate_info),
                'description': '',
                'arguments': [],
                'examples': [],
                'usage': '',
                'category': '',
                'attributes': {}
            }
    
    def parse_themrole_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse thematic role definitions JSON file.
        
        Args:
            file_path (Path): Path to thematic role definitions JSON file
            
        Returns:
            dict: Parsed thematic role definitions
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        themroles = {}
        
        # Process thematic role data
        for role_name, role_info in raw_data.items():
            themroles[role_name] = self._process_themrole_definition(role_name, role_info)
        
        return themroles
    
    def _process_themrole_definition(self, role_name: str, role_info: Any) -> Dict[str, Any]:
        """
        Process a single thematic role definition.
        
        Args:
            role_name (str): Name of the thematic role
            role_info: Raw role information
            
        Returns:
            dict: Processed thematic role definition
        """
        if isinstance(role_info, dict):
            return {
                'name': role_name,
                'definition': role_info.get('definition', ''),
                'description': role_info.get('description', ''),
                'examples': role_info.get('examples', []),
                'selectional_restrictions': role_info.get('selectional_restrictions', []),
                'typical_syntactic_positions': role_info.get('syntactic_positions', []),
                'attributes': {k: v for k, v in role_info.items() 
                             if k not in ['definition', 'description', 'examples', 
                                        'selectional_restrictions', 'syntactic_positions']}
            }
        else:
            return {
                'name': role_name,
                'definition': str(role_info),
                'description': '',
                'examples': [],
                'selectional_restrictions': [],
                'typical_syntactic_positions': [],
                'attributes': {}
            }
    
    def parse_constants_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse constants TSV file.
        
        Args:
            file_path (Path): Path to constants TSV file
            
        Returns:
            dict: Parsed constants
        """
        constants = {}
        
        with open(file_path, 'r', encoding='utf-8', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            
            for row in reader:
                constant_name = row.get('constant', '').strip()
                if constant_name:
                    constants[constant_name] = {
                        'name': constant_name,
                        'definition': row.get('definition', '').strip(),
                        'type': row.get('type', '').strip(),
                        'domain': row.get('domain', '').strip(),
                        'examples': self._parse_examples_string(row.get('examples', '')),
                        'attributes': {k: v.strip() for k, v in row.items() 
                                     if k not in ['constant', 'definition', 'type', 'domain', 'examples'] and v.strip()}
                    }
        
        return constants
    
    def parse_semantic_predicates_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse semantic predicates TSV file.
        
        Args:
            file_path (Path): Path to semantic predicates TSV file
            
        Returns:
            dict: Parsed semantic predicates
        """
        semantic_predicates = {}
        
        with open(file_path, 'r', encoding='utf-8', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            
            for row in reader:
                predicate_name = row.get('predicate', '').strip()
                if predicate_name:
                    semantic_predicates[predicate_name] = {
                        'name': predicate_name,
                        'definition': row.get('definition', '').strip(),
                        'argument_structure': row.get('argument_structure', '').strip(),
                        'semantic_class': row.get('semantic_class', '').strip(),
                        'examples': self._parse_examples_string(row.get('examples', '')),
                        'attributes': {k: v.strip() for k, v in row.items() 
                                     if k not in ['predicate', 'definition', 'argument_structure', 
                                                'semantic_class', 'examples'] and v.strip()}
                    }
        
        return semantic_predicates
    
    def parse_verb_specific_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse verb-specific predicates TSV file.
        
        Args:
            file_path (Path): Path to verb-specific predicates TSV file
            
        Returns:
            dict: Parsed verb-specific predicates
        """
        verb_specific = {}
        
        with open(file_path, 'r', encoding='utf-8', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            
            for row in reader:
                predicate_name = row.get('predicate', '').strip()
                if predicate_name:
                    verb_specific[predicate_name] = {
                        'name': predicate_name,
                        'definition': row.get('definition', '').strip(),
                        'verb_class': row.get('verb_class', '').strip(),
                        'specific_usage': row.get('specific_usage', '').strip(),
                        'examples': self._parse_examples_string(row.get('examples', '')),
                        'attributes': {k: v.strip() for k, v in row.items() 
                                     if k not in ['predicate', 'definition', 'verb_class', 
                                                'specific_usage', 'examples'] and v.strip()}
                    }
        
        return verb_specific
    
    def _parse_examples_string(self, examples_str: str) -> List[str]:
        """
        Parse a string containing examples.
        
        Args:
            examples_str (str): String containing examples
            
        Returns:
            list: List of individual examples
        """
        if not examples_str or not examples_str.strip():
            return []
        
        # Common separators in example strings
        separators = [';', '|', '\n', '\\n']
        
        examples = [examples_str.strip()]
        
        for sep in separators:
            if sep in examples_str:
                examples = [ex.strip() for ex in examples_str.split(sep) if ex.strip()]
                break
        
        return examples
    
    def get_predicate_definition(self, predicate_name: str, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get definition for a specific predicate.
        
        Args:
            predicate_name (str): Name of the predicate
            reference_data (dict): Parsed reference data
            
        Returns:
            dict: Predicate definition or None if not found
        """
        predicates = reference_data.get('predicates', {})
        return predicates.get(predicate_name)
    
    def get_themrole_definition(self, role_name: str, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get definition for a specific thematic role.
        
        Args:
            role_name (str): Name of the thematic role
            reference_data (dict): Parsed reference data
            
        Returns:
            dict: Thematic role definition or None if not found
        """
        themroles = reference_data.get('themroles', {})
        return themroles.get(role_name)
    
    def get_constant_definition(self, constant_name: str, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get definition for a specific constant.
        
        Args:
            constant_name (str): Name of the constant
            reference_data (dict): Parsed reference data
            
        Returns:
            dict: Constant definition or None if not found
        """
        constants = reference_data.get('constants', {})
        return constants.get(constant_name)
    
    def search_definitions(self, query: str, reference_data: Dict[str, Any], 
                          search_categories: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for definitions across all reference categories.
        
        Args:
            query (str): Search query
            reference_data (dict): Parsed reference data
            search_categories (list): Categories to search in (default: all)
            
        Returns:
            dict: Search results grouped by category
        """
        if not search_categories:
            search_categories = ['predicates', 'themroles', 'constants', 
                               'semantic_predicates', 'verb_specific_predicates']
        
        results = {}
        query_lower = query.lower()
        
        for category in search_categories:
            category_data = reference_data.get(category, {})
            category_results = []
            
            for item_name, item_data in category_data.items():
                # Search in name
                if query_lower in item_name.lower():
                    category_results.append(item_data)
                    continue
                
                # Search in definition
                definition = item_data.get('definition', '')
                if query_lower in definition.lower():
                    category_results.append(item_data)
                    continue
                
                # Search in description
                description = item_data.get('description', '')
                if query_lower in description.lower():
                    category_results.append(item_data)
            
            if category_results:
                results[category] = category_results
        
        return results