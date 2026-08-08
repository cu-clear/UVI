"""
OntoNotes Parser Module

Specialized parser for OntoNotes XML and HTML corpus files. Handles parsing of
sense inventories and cross-resource mappings.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class OntoNotesParser:
    """
    Parser for OntoNotes XML and HTML corpus files.
    
    Handles parsing of OntoNotes sense inventories with cross-resource mappings
    to WordNet, VerbNet, FrameNet, and PropBank.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize OntoNotes parser with corpus path.
        
        Args:
            corpus_path (Path): Path to OntoNotes corpus directory
        """
        self.corpus_path = corpus_path
        
    def parse_all_senses(self) -> Dict[str, Any]:
        """
        Parse all OntoNotes sense files in the corpus directory.
        
        Returns:
            dict: Complete OntoNotes sense data
        """
        ontonotes_data = {
            'sense_inventories': {},
            'mappings': {
                'wordnet': {},
                'verbnet': {},
                'framenet': {},
                'propbank': {}
            }
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return ontonotes_data
            
        # Find OntoNotes files (both XML and HTML)
        xml_files = list(self.corpus_path.glob('**/*.xml'))
        html_files = list(self.corpus_path.glob('**/*.html'))
        
        for xml_file in xml_files:
            try:
                sense_data = self.parse_sense_file_xml(xml_file)
                if sense_data and 'lemma' in sense_data:
                    ontonotes_data['sense_inventories'][sense_data['lemma']] = sense_data
                    self._extract_mappings(sense_data, ontonotes_data['mappings'])
            except Exception as e:
                print(f"Error parsing OntoNotes XML file {xml_file}: {e}")
        
        for html_file in html_files:
            try:
                sense_data = self.parse_sense_file_html(html_file)
                if sense_data and 'lemma' in sense_data:
                    ontonotes_data['sense_inventories'][sense_data['lemma']] = sense_data
                    self._extract_mappings(sense_data, ontonotes_data['mappings'])
            except Exception as e:
                print(f"Error parsing OntoNotes HTML file {html_file}: {e}")
        
        return ontonotes_data
    
    def parse_sense_file_xml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single OntoNotes sense XML file.
        
        Args:
            file_path (Path): Path to OntoNotes XML file
            
        Returns:
            dict: Parsed sense data or None if parsing failed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            if root.tag == 'inventory':
                return self._parse_inventory_element(root)
            else:
                print(f"Unexpected root element {root.tag} in {file_path}")
                return None
        except Exception as e:
            print(f"Error parsing OntoNotes XML file {file_path}: {e}")
            return None
    
    def parse_sense_file_html(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single OntoNotes sense HTML file.
        
        Args:
            file_path (Path): Path to OntoNotes HTML file
            
        Returns:
            dict: Parsed sense data or None if parsing failed
        """
        if BeautifulSoup is None:
            print(f"BeautifulSoup not available for HTML parsing: {file_path}")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            return self._parse_html_content(soup)
        except Exception as e:
            print(f"Error parsing OntoNotes HTML file {file_path}: {e}")
            return None
    
    def _parse_inventory_element(self, inventory_element: ET.Element) -> Dict[str, Any]:
        """
        Parse an inventory XML element.
        
        Args:
            inventory_element (ET.Element): Inventory XML element
            
        Returns:
            dict: Parsed inventory data
        """
        inventory_data = {
            'lemma': inventory_element.get('lemma', ''),
            'attributes': dict(inventory_element.attrib),
            'commentary': self._extract_text_content(inventory_element.find('.//commentary')),
            'senses': self._parse_senses(inventory_element)
        }
        
        return inventory_data
    
    def _parse_senses(self, inventory_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse sense elements from an inventory."""
        senses = []
        
        for sense in inventory_element.findall('.//sense'):
            sense_data = {
                'n': sense.get('n', ''),
                'name': sense.get('name', ''),
                'group': sense.get('group', ''),
                'attributes': dict(sense.attrib),
                'commentary': self._extract_text_content(sense.find('.//commentary')),
                'examples': self._parse_examples(sense),
                'mappings': self._parse_mappings(sense)
            }
            senses.append(sense_data)
        
        return senses
    
    def _parse_examples(self, sense_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse example elements from a sense."""
        examples = []
        
        for example in sense_element.findall('.//example'):
            example_data = {
                'name': example.get('name', ''),
                'src': example.get('src', ''),
                'attributes': dict(example.attrib),
                'text': self._extract_text_content(example.find('.//text')),
                'args': self._parse_args(example)
            }
            examples.append(example_data)
        
        return examples
    
    def _parse_args(self, example_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse arg elements from an example."""
        args = []
        
        for arg in example_element.findall('.//arg'):
            arg_data = {
                'n': arg.get('n', ''),
                'f': arg.get('f', ''),
                'attributes': dict(arg.attrib),
                'text': arg.text.strip() if arg.text else ''
            }
            args.append(arg_data)
        
        return args
    
    def _parse_mappings(self, sense_element: ET.Element) -> Dict[str, List[str]]:
        """Parse mapping elements from a sense."""
        mappings = {
            'wordnet': [],
            'verbnet': [],
            'framenet': [],
            'propbank': []
        }
        
        for mapping in sense_element.findall('.//mapping'):
            mapping_type = mapping.get('type', '').lower()
            mapping_value = mapping.get('value', '')
            
            if mapping_type in mappings and mapping_value:
                mappings[mapping_type].append(mapping_value)
        
        return mappings
    
    def _parse_html_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parse OntoNotes HTML content using BeautifulSoup.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of HTML content
            
        Returns:
            dict: Parsed HTML sense data
        """
        # Extract lemma from title or heading
        lemma = ""
        title_tag = soup.find('title')
        if title_tag:
            lemma = self._extract_lemma_from_title(title_tag.get_text())
        
        # Extract senses from HTML structure
        senses = []
        sense_divs = soup.find_all('div', class_='sense')
        
        for i, sense_div in enumerate(sense_divs):
            sense_data = {
                'n': str(i + 1),
                'name': sense_div.get('id', ''),
                'commentary': self._extract_html_commentary(sense_div),
                'examples': self._extract_html_examples(sense_div),
                'mappings': self._extract_html_mappings(sense_div)
            }
            senses.append(sense_data)
        
        return {
            'lemma': lemma,
            'senses': senses,
            'source': 'html'
        }
    
    def _extract_lemma_from_title(self, title_text: str) -> str:
        """Extract lemma from HTML title text."""
        # Common patterns in OntoNotes HTML titles
        patterns = [
            r'^([^-]+)',  # Everything before first dash
            r'(\w+)',     # First word
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title_text.strip())
            if match:
                return match.group(1).strip().lower()
        
        return title_text.strip().lower()
    
    def _extract_html_commentary(self, sense_div) -> str:
        """Extract commentary text from HTML sense div."""
        commentary_p = sense_div.find('p', class_='commentary')
        if commentary_p:
            return commentary_p.get_text().strip()
        
        # Fallback: look for any paragraph with commentary-like content
        for p in sense_div.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 20 and not text.startswith('Example'):
                return text
        
        return ""
    
    def _extract_html_examples(self, sense_div) -> List[Dict[str, Any]]:
        """Extract examples from HTML sense div."""
        examples = []
        example_divs = sense_div.find_all('div', class_='example')
        
        for i, example_div in enumerate(example_divs):
            example_data = {
                'name': f'example_{i+1}',
                'text': example_div.get_text().strip(),
                'attributes': dict(example_div.attrs) if example_div.attrs else {}
            }
            examples.append(example_data)
        
        return examples
    
    def _extract_html_mappings(self, sense_div) -> Dict[str, List[str]]:
        """Extract cross-resource mappings from HTML sense div."""
        mappings = {
            'wordnet': [],
            'verbnet': [],
            'framenet': [],
            'propbank': []
        }
        
        # Look for mapping information in various HTML structures
        mapping_div = sense_div.find('div', class_='mappings')
        if mapping_div:
            text = mapping_div.get_text()
            
            # Extract WordNet synsets
            wn_matches = re.findall(r'WN:\s*([^\s,]+)', text)
            mappings['wordnet'].extend(wn_matches)
            
            # Extract VerbNet classes
            vn_matches = re.findall(r'VN:\s*([^\s,]+)', text)
            mappings['verbnet'].extend(vn_matches)
            
            # Extract FrameNet frames
            fn_matches = re.findall(r'FN:\s*([^\s,]+)', text)
            mappings['framenet'].extend(fn_matches)
            
            # Extract PropBank rolesets
            pb_matches = re.findall(r'PB:\s*([^\s,]+)', text)
            mappings['propbank'].extend(pb_matches)
        
        return mappings
    
    def _extract_mappings(self, sense_data: Dict[str, Any], global_mappings: Dict[str, Dict]):
        """Extract and index mappings for quick lookup."""
        lemma = sense_data.get('lemma', '')
        
        for sense in sense_data.get('senses', []):
            sense_id = f"{lemma}.{sense.get('n', '1')}"
            sense_mappings = sense.get('mappings', {})
            
            for resource, values in sense_mappings.items():
                if resource in global_mappings:
                    for value in values:
                        if value not in global_mappings[resource]:
                            global_mappings[resource][value] = []
                        global_mappings[resource][value].append(sense_id)
    
    def _extract_text_content(self, element: Optional[ET.Element]) -> str:
        """Extract text content from an XML element."""
        if element is not None and element.text:
            return element.text.strip()
        return ""