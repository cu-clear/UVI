"""
BSO (Basic Semantic Ontology) Parser Module

Specialized parser for BSO CSV mapping files. Handles parsing of mappings
between VerbNet classes and BSO semantic categories.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class BSOParser:
    """
    Parser for BSO (Basic Semantic Ontology) CSV mapping files.
    
    Handles parsing of mappings between VerbNet verb classes and BSO
    broad semantic categories.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize BSO parser with corpus path.
        
        Args:
            corpus_path (Path): Path to BSO corpus directory
        """
        self.corpus_path = corpus_path
        
        # Expected BSO mapping files
        self.bso_vn_file = corpus_path / "BSOVNMapping_withMembers.csv" if corpus_path else None
        self.vn_bso_file = corpus_path / "VNBSOMapping_withMembers.csv" if corpus_path else None
    
    def parse_all_mappings(self) -> Dict[str, Any]:
        """
        Parse all BSO mapping files.
        
        Returns:
            dict: Complete BSO mapping data
        """
        bso_data = {
            'bso_to_vn': {},
            'vn_to_bso': {},
            'categories': set(),
            'verbnet_classes': set()
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return bso_data
        
        # Parse BSO to VerbNet mappings
        if self.bso_vn_file and self.bso_vn_file.exists():
            try:
                bso_to_vn = self.parse_bso_to_vn_file(self.bso_vn_file)
                bso_data['bso_to_vn'] = bso_to_vn
                bso_data['categories'].update(bso_to_vn.keys())
            except Exception as e:
                print(f"Error parsing BSO to VN mapping file: {e}")
        
        # Parse VerbNet to BSO mappings
        if self.vn_bso_file and self.vn_bso_file.exists():
            try:
                vn_to_bso = self.parse_vn_to_bso_file(self.vn_bso_file)
                bso_data['vn_to_bso'] = vn_to_bso
                bso_data['verbnet_classes'].update(vn_to_bso.keys())
            except Exception as e:
                print(f"Error parsing VN to BSO mapping file: {e}")
        
        # Convert sets to lists for JSON serialization
        bso_data['categories'] = list(bso_data['categories'])
        bso_data['verbnet_classes'] = list(bso_data['verbnet_classes'])
        
        return bso_data
    
    def parse_bso_to_vn_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse BSO to VerbNet mapping file.
        
        Args:
            file_path (Path): Path to BSO to VN mapping CSV file
            
        Returns:
            dict: BSO category to VerbNet class mappings
        """
        bso_to_vn = {}
        
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            delimiter = ','
            if '\t' in sample:
                delimiter = '\t'
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row in reader:
                # Expected columns: BSO_Category, VerbNet_Class, Members, etc.
                bso_category = row.get('BSO_Category', '').strip()
                vn_class = (row.get('VerbNet_Class', '') or row.get('VN_Class', '')).strip()
                members = row.get('Members', '').strip()
                
                if bso_category and vn_class:
                    if bso_category not in bso_to_vn:
                        bso_to_vn[bso_category] = []
                    bso_to_vn[bso_category].append(vn_class)
        
        return bso_to_vn
    
    def parse_vn_to_bso_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse VerbNet to BSO mapping file.
        
        Args:
            file_path (Path): Path to VN to BSO mapping CSV file
            
        Returns:
            dict: VerbNet class to BSO category mappings
        """
        vn_to_bso = {}
        
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            delimiter = ','
            if '\t' in sample:
                delimiter = '\t'
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row in reader:
                # Expected columns: VerbNet_Class/VN_Class, BSO_Category, Members, etc.
                vn_class = (row.get('VerbNet_Class', '') or row.get('VN_Class', '')).strip()
                bso_category = row.get('BSO_Category', '').strip()
                members = row.get('Members', '').strip()
                
                if vn_class and bso_category:
                    # For simplicity, just store the BSO category string
                    vn_to_bso[vn_class] = bso_category
        
        return vn_to_bso
    
    def _parse_members_string(self, members_str: str) -> List[str]:
        """
        Parse a string containing verb members.
        
        Args:
            members_str (str): String containing verb members
            
        Returns:
            list: List of individual verb members
        """
        if not members_str:
            return []
        
        # Handle various delimiters
        members = []
        
        # Common separators in BSO files
        separators = [',', ';', ' ', '\t']
        
        # Split by the most common separator
        for sep in separators:
            if sep in members_str:
                parts = members_str.split(sep)
                members = [member.strip() for member in parts if member.strip()]
                break
        else:
            # If no separator found, treat as single member
            members = [members_str.strip()]
        
        # Clean up members (remove parenthetical info, extra whitespace)
        cleaned_members = []
        for member in members:
            # Remove parenthetical information like "(activity)"
            cleaned = re.sub(r'\([^)]*\)', '', member).strip()
            if cleaned:
                cleaned_members.append(cleaned)
        
        return cleaned_members
    
    def get_bso_categories_for_class(self, vn_class: str, bso_data: Dict[str, Any]) -> List[str]:
        """
        Get BSO categories for a VerbNet class.
        
        Args:
            vn_class (str): VerbNet class ID
            bso_data (dict): Parsed BSO data
            
        Returns:
            list: BSO categories for the class
        """
        vn_to_bso = bso_data.get('vn_to_bso', {})
        class_info = vn_to_bso.get(vn_class, {})
        
        categories = []
        for cat_info in class_info.get('bso_categories', []):
            categories.append(cat_info.get('category', ''))
        
        return categories
    
    def get_verbnet_classes_for_category(self, bso_category: str, bso_data: Dict[str, Any]) -> List[str]:
        """
        Get VerbNet classes for a BSO category.
        
        Args:
            bso_category (str): BSO category name
            bso_data (dict): Parsed BSO data
            
        Returns:
            list: VerbNet classes in the category
        """
        bso_to_vn = bso_data.get('bso_to_vn', {})
        category_info = bso_to_vn.get(bso_category, {})
        
        classes = []
        for class_info in category_info.get('verbnet_classes', []):
            classes.append(class_info.get('class_id', ''))
        
        return classes
    
    def get_category_statistics(self, bso_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate statistics for BSO categories.
        
        Args:
            bso_data (dict): Parsed BSO data
            
        Returns:
            dict: Statistics about BSO categories and mappings
        """
        stats = {
            'total_categories': len(bso_data.get('categories', [])),
            'total_verbnet_classes': len(bso_data.get('verbnet_classes', [])),
            'category_details': {},
            'class_distribution': {}
        }
        
        bso_to_vn = bso_data.get('bso_to_vn', {})
        
        for category, info in bso_to_vn.items():
            class_count = len(info.get('verbnet_classes', []))
            member_count = info.get('total_members', 0)
            
            stats['category_details'][category] = {
                'verbnet_classes': class_count,
                'total_members': member_count,
                'avg_members_per_class': member_count / class_count if class_count > 0 else 0
            }
        
        # Calculate class distribution across categories
        vn_to_bso = bso_data.get('vn_to_bso', {})
        for vn_class, info in vn_to_bso.items():
            category_count = len(info.get('bso_categories', []))
            stats['class_distribution'][vn_class] = category_count
        
        return stats