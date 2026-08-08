"""
PropBank Parser Module

Specialized parser for PropBank XML corpus files. Handles parsing of predicate frames,
rolesets, and annotated examples from XML files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional


class PropBankParser:
    """
    Parser for PropBank XML corpus files.
    
    Handles parsing of PropBank predicates, rolesets, roles, and examples
    with argument annotations.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize PropBank parser with corpus path.
        
        Args:
            corpus_path (Path): Path to PropBank corpus directory
        """
        self.corpus_path = corpus_path
        
    def parse_all_frames(self) -> Dict[str, Any]:
        """
        Parse all PropBank frame files in the corpus directory.
        
        Returns:
            dict: Complete PropBank frame data
        """
        propbank_data = {
            'predicates': {},
            'rolesets': {},
            'examples': {}
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return propbank_data
            
        # Find PropBank XML files
        xml_files = list(self.corpus_path.glob('**/*.xml'))
        
        for xml_file in xml_files:
            try:
                predicate_data = self.parse_predicate_file(xml_file)
                if predicate_data and 'lemma' in predicate_data:
                    # Flatten structure: extract rolesets from nested predicates
                    flattened_data = {
                        'lemma': predicate_data['lemma'],
                        'attributes': predicate_data['attributes'],
                        'note': predicate_data['note'],
                        'rolesets': []
                    }
                    # Collect rolesets from all nested predicates
                    for pred in predicate_data.get('predicates', []):
                        flattened_data['rolesets'].extend(pred.get('rolesets', []))
                    
                    propbank_data['predicates'][predicate_data['lemma']] = flattened_data
            except Exception as e:
                print(f"Error parsing PropBank file {xml_file}: {e}")
        
        return propbank_data
    
    def parse_predicate_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single PropBank predicate XML file.
        
        Args:
            file_path (Path): Path to PropBank XML file
            
        Returns:
            dict: Parsed predicate data or None if parsing failed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            if root.tag == 'frameset':
                return self._parse_frameset_element(root)
            else:
                print(f"Unexpected root element {root.tag} in {file_path}")
                return None
        except Exception as e:
            print(f"Error parsing PropBank file {file_path}: {e}")
            return None
    
    def _parse_frameset_element(self, frameset_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a frameset XML element.
        
        Args:
            frameset_element (ET.Element): Frameset XML element
            
        Returns:
            dict: Parsed frameset data
        """
        frameset_data = {
            'lemma': frameset_element.get('lemma', ''),
            'attributes': dict(frameset_element.attrib),
            'note': self._extract_text_content(frameset_element.find('.//note')),
            'predicates': self._parse_predicates(frameset_element)
        }
        
        return frameset_data
    
    def _parse_predicates(self, frameset_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse predicate elements from a frameset."""
        predicates = []
        
        for predicate in frameset_element.findall('.//predicate'):
            pred_data = {
                'lemma': predicate.get('lemma', ''),
                'attributes': dict(predicate.attrib),
                'note': self._extract_text_content(predicate.find('.//note')),
                'rolesets': self._parse_rolesets(predicate)
            }
            predicates.append(pred_data)
        
        return predicates
    
    def _parse_rolesets(self, predicate_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse roleset elements from a predicate."""
        rolesets = []
        
        for roleset in predicate_element.findall('.//roleset'):
            roleset_data = {
                'id': roleset.get('id', ''),
                'name': roleset.get('name', ''),
                'vncls': roleset.get('vncls', ''),
                'framnet': roleset.get('framnet', ''),  # Note: Some files use 'framnet' instead of 'framenet'
                'attributes': dict(roleset.attrib),
                'aliases': self._parse_aliases(roleset),
                'note': self._extract_text_content(roleset.find('.//note')),
                'roles': self._parse_roles(roleset),
                'examples': self._parse_examples(roleset)
            }
            rolesets.append(roleset_data)
        
        return rolesets
    
    def _parse_aliases(self, roleset_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse alias elements from a roleset."""
        aliases = []
        
        for alias in roleset_element.findall('.//alias'):
            alias_data = {
                'framenet': alias.get('framenet', ''),
                'pos': alias.get('pos', ''),
                'verbnet': alias.get('verbnet', ''),
                'attributes': dict(alias.attrib)
            }
            aliases.append(alias_data)
        
        return aliases
    
    def _parse_roles(self, roleset_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse role elements from a roleset."""
        roles = []
        
        for role in roleset_element.findall('.//role'):
            role_data = {
                'n': role.get('n', ''),
                'f': role.get('f', ''),
                'descr': role.get('descr', ''),
                'attributes': dict(role.attrib),
                'vnrole': self._parse_vnroles(role)
            }
            roles.append(role_data)
        
        return roles
    
    def _parse_vnroles(self, role_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse vnrole elements from a role."""
        vnroles = []
        
        for vnrole in role_element.findall('.//vnrole'):
            vnrole_data = {
                'vncls': vnrole.get('vncls', ''),
                'vntheta': vnrole.get('vntheta', ''),
                'attributes': dict(vnrole.attrib)
            }
            vnroles.append(vnrole_data)
        
        return vnroles
    
    def _parse_examples(self, roleset_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse example elements from a roleset."""
        examples = []
        
        for example in roleset_element.findall('.//example'):
            example_data = {
                'name': example.get('name', ''),
                'src': example.get('src', ''),
                'attributes': dict(example.attrib),
                'text': self._extract_text_content(example.find('.//text')),
                'args': self._parse_args(example),
                'rels': self._parse_rels(example)
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
    
    def _parse_rels(self, example_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse rel elements from an example."""
        rels = []
        
        for rel in example_element.findall('.//rel'):
            rel_data = {
                'f': rel.get('f', ''),
                'attributes': dict(rel.attrib),
                'text': rel.text.strip() if rel.text else ''
            }
            rels.append(rel_data)
        
        return rels
    
    def _extract_text_content(self, element: Optional[ET.Element]) -> str:
        """Extract text content from an XML element."""
        if element is not None and element.text:
            return element.text.strip()
        return ""
    
    def get_predicate_mappings(self, propbank_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract cross-corpus mappings from PropBank data.
        
        Args:
            propbank_data (dict): Parsed PropBank data
            
        Returns:
            dict: Mapping data for cross-corpus integration
        """
        mappings = {
            'verbnet_mappings': {},
            'framenet_mappings': {}
        }
        
        for lemma, predicate_data in propbank_data.get('predicates', {}).items():
            for predicate in predicate_data.get('predicates', []):
                for roleset in predicate.get('rolesets', []):
                    roleset_id = roleset.get('id', '')
                    
                    # Extract VerbNet mappings
                    vncls = roleset.get('vncls', '')
                    if vncls:
                        if roleset_id not in mappings['verbnet_mappings']:
                            mappings['verbnet_mappings'][roleset_id] = []
                        mappings['verbnet_mappings'][roleset_id].extend(
                            [cls.strip() for cls in vncls.split()]
                        )
                    
                    # Extract FrameNet mappings
                    framenet = roleset.get('framnet', '') or roleset.get('framenet', '')
                    if framenet:
                        mappings['framenet_mappings'][roleset_id] = framenet.strip()
                    
                    # Extract mappings from aliases
                    for alias in roleset.get('aliases', []):
                        vn_mapping = alias.get('verbnet', '')
                        fn_mapping = alias.get('framenet', '')
                        
                        if vn_mapping:
                            if roleset_id not in mappings['verbnet_mappings']:
                                mappings['verbnet_mappings'][roleset_id] = []
                            mappings['verbnet_mappings'][roleset_id].extend(
                                [cls.strip() for cls in vn_mapping.split()]
                            )
                        
                        if fn_mapping:
                            mappings['framenet_mappings'][roleset_id] = fn_mapping.strip()
        
        return mappings