"""
VerbNet Parser Module

Specialized parser for VerbNet XML corpus files. Handles parsing of VerbNet classes,
members, frames, thematic roles, syntax, and semantics from XML files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
try:
    from lxml import etree
except ImportError:
    etree = None


class VerbNetParser:
    """
    Parser for VerbNet XML corpus files.
    
    Handles parsing of VerbNet class hierarchy, members, frames, thematic roles,
    syntactic restrictions, selectional restrictions, and semantic predicates.
    """
    
    def __init__(self, corpus_path: Path):
        """
        Initialize VerbNet parser with corpus path.
        
        Args:
            corpus_path (Path): Path to VerbNet corpus directory
        """
        self.corpus_path = corpus_path
        self.schema_path = corpus_path / "vn_schema-3.xsd" if corpus_path else None
        
    def parse_all_classes(self) -> Dict[str, Any]:
        """
        Parse all VerbNet class files in the corpus directory.
        
        Returns:
            dict: Complete VerbNet class data with hierarchy
        """
        verbnet_data = {
            'classes': {},
            'hierarchy': {},
            'members_index': {}
        }
        
        if not self.corpus_path or not self.corpus_path.exists():
            return verbnet_data
            
        # Find all VerbNet XML files
        xml_files = list(self.corpus_path.glob('*.xml'))
        
        for xml_file in xml_files:
            if xml_file.name.endswith('.dtd') or xml_file.name.endswith('.xsd'):
                continue
                
            try:
                class_data = self.parse_class_file(xml_file)
                if class_data and 'id' in class_data:
                    verbnet_data['classes'][class_data['id']] = class_data
                    self._index_members(class_data, verbnet_data['members_index'])
            except Exception as e:
                print(f"Error parsing VerbNet file {xml_file}: {e}")
        
        # Build hierarchy
        verbnet_data['hierarchy'] = self._build_class_hierarchy(verbnet_data['classes'])
        
        return verbnet_data
    
    def parse_class_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single VerbNet class XML file.
        
        Args:
            file_path (Path): Path to VerbNet XML file
            
        Returns:
            dict: Parsed class data or None if parsing failed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            if root.tag == 'VNCLASS':
                return self._parse_vnclass_element(root)
            else:
                print(f"Unexpected root element {root.tag} in {file_path}")
                return None
        except Exception as e:
            print(f"Error parsing VerbNet file {file_path}: {e}")
            return None
    
    def _parse_vnclass_element(self, class_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a VNCLASS XML element.
        
        Args:
            class_element (ET.Element): VNCLASS XML element
            
        Returns:
            dict: Parsed class data
        """
        class_data = {
            'id': class_element.get('ID', ''),
            'attributes': dict(class_element.attrib),
            'members': self._parse_members(class_element),
            'themroles': self._parse_themroles(class_element),
            'frames': self._parse_frames(class_element),
            'subclasses': self._parse_subclasses(class_element)
        }
        
        return class_data
    
    def _parse_members(self, class_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse MEMBER elements from a VerbNet class."""
        members = []
        
        for member in class_element.findall('.//MEMBER'):
            member_data = {
                'name': member.get('name', ''),
                'wn': member.get('wn', ''),
                'grouping': member.get('grouping', ''),
                'attributes': dict(member.attrib)
            }
            members.append(member_data)
        
        return members
    
    def _parse_themroles(self, class_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse THEMROLE elements from a VerbNet class."""
        themroles = []
        
        for themrole in class_element.findall('.//THEMROLE'):
            role_data = {
                'type': themrole.get('type', ''),
                'attributes': dict(themrole.attrib),
                'selrestrs': self._parse_selrestrs(themrole)
            }
            themroles.append(role_data)
        
        return themroles
    
    def _parse_selrestrs(self, element: ET.Element) -> List[Dict[str, Any]]:
        """Parse selectional restrictions from an element."""
        selrestrs = []
        
        for selrestr in element.findall('.//SELRESTR'):
            selrestr_data = {
                'Value': selrestr.get('Value', ''),
                'type': selrestr.get('type', ''),
                'attributes': dict(selrestr.attrib)
            }
            selrestrs.append(selrestr_data)
        
        return selrestrs
    
    def _parse_frames(self, class_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse FRAME elements from a VerbNet class."""
        frames = []
        
        for frame in class_element.findall('.//FRAME'):
            frame_data = {
                'description': dict(frame.attrib),
                'examples': self._parse_examples(frame),
                'syntax': self._parse_syntax(frame),
                'semantics': self._parse_semantics(frame)
            }
            frames.append(frame_data)
        
        return frames
    
    def _parse_examples(self, frame: ET.Element) -> List[str]:
        """Parse EXAMPLE elements from a frame."""
        examples = []
        
        for example in frame.findall('.//EXAMPLE'):
            if example.text:
                examples.append(example.text.strip())
        
        return examples
    
    def _parse_syntax(self, frame: ET.Element) -> List[Dict[str, Any]]:
        """Parse SYNTAX elements from a frame."""
        syntax_elements = []
        
        for syntax in frame.findall('.//SYNTAX'):
            for child in syntax:
                if child.tag in ['NP', 'VERB', 'PREP', 'ADJ', 'ADV', 'LEX']:
                    element_data = {
                        'tag': child.tag,
                        'value': child.get('value', ''),
                        'attributes': dict(child.attrib),
                        'synrestrs': self._parse_synrestrs(child)
                    }
                    syntax_elements.append(element_data)
        
        return syntax_elements
    
    def _parse_synrestrs(self, element: ET.Element) -> List[Dict[str, Any]]:
        """Parse syntactic restrictions from an element."""
        synrestrs = []
        
        for synrestr in element.findall('.//SYNRESTR'):
            synrestr_data = {
                'Value': synrestr.get('Value', ''),
                'type': synrestr.get('type', ''),
                'attributes': dict(synrestr.attrib)
            }
            synrestrs.append(synrestr_data)
        
        return synrestrs
    
    def _parse_semantics(self, frame: ET.Element) -> List[Dict[str, Any]]:
        """Parse SEMANTICS elements from a frame."""
        semantics = []
        
        for sem_element in frame.findall('.//SEMANTICS'):
            for pred in sem_element.findall('.//PRED'):
                pred_data = {
                    'value': pred.get('value', ''),
                    'bool': pred.get('bool'),
                    'attributes': dict(pred.attrib),
                    'args': self._parse_pred_args(pred)
                }
                semantics.append(pred_data)
        
        return semantics
    
    def _parse_pred_args(self, pred: ET.Element) -> List[Dict[str, Any]]:
        """Parse predicate arguments from a PRED element."""
        args = []
        
        for arg in pred.findall('.//ARG'):
            arg_data = {
                'type': arg.get('type', ''),
                'value': arg.get('value', ''),
                'attributes': dict(arg.attrib)
            }
            args.append(arg_data)
        
        return args
    
    def _parse_subclasses(self, class_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse VNSUBCLASS elements recursively."""
        subclasses = []
        
        for subclass in class_element.findall('.//VNSUBCLASS'):
            subclass_data = self._parse_vnclass_element(subclass)
            subclasses.append(subclass_data)
        
        return subclasses
    
    def _index_members(self, class_data: Dict[str, Any], members_index: Dict[str, List[str]]):
        """Build index of members to class IDs."""
        for member in class_data.get('members', []):
            member_name = member.get('name', '').lower()
            if member_name:
                if member_name not in members_index:
                    members_index[member_name] = []
                members_index[member_name].append(class_data.get('id', ''))
        
        # Index members from subclasses
        for subclass in class_data.get('subclasses', []):
            self._index_members(subclass, members_index)
    
    def _build_class_hierarchy(self, classes: Dict[str, Any]) -> Dict[str, Any]:
        """Build hierarchical structure of VerbNet classes."""
        hierarchy = {
            'by_name': {},
            'by_id': {},
            'parent_child': {}
        }
        
        # Build hierarchy mappings
        for class_id, class_data in classes.items():
            # Extract numerical prefix for ID-based hierarchy
            parts = class_id.split('-')
            if parts:
                numeric_prefix = parts[0]
                if numeric_prefix not in hierarchy['by_id']:
                    hierarchy['by_id'][numeric_prefix] = []
                hierarchy['by_id'][numeric_prefix].append(class_id)
            
            # Extract first letter for name-based hierarchy
            first_letter = class_id[0].upper() if class_id else 'A'
            if first_letter not in hierarchy['by_name']:
                hierarchy['by_name'][first_letter] = []
            hierarchy['by_name'][first_letter].append(class_id)
            
            # Build parent-child relationships
            if '-' in class_id:
                parent_id = '-'.join(class_id.split('-')[:-1])
                if parent_id in classes:
                    if parent_id not in hierarchy['parent_child']:
                        hierarchy['parent_child'][parent_id] = []
                    hierarchy['parent_child'][parent_id].append(class_id)
        
        return hierarchy
    
    def validate_against_schema(self, xml_file: Path) -> Dict[str, Any]:
        """
        Validate VerbNet XML file against schema.
        
        Args:
            xml_file (Path): Path to XML file to validate
            
        Returns:
            dict: Validation results
        """
        if etree is None:
            return {'valid': None, 'errors': ['lxml library not available for schema validation']}
            
        if not self.schema_path or not self.schema_path.exists():
            return {'valid': None, 'errors': ['Schema file not found']}
        
        try:
            with open(self.schema_path, 'r') as schema_file:
                schema_doc = etree.parse(schema_file)
                schema = etree.XMLSchema(schema_doc)
            
            with open(xml_file, 'r') as xml_file_handle:
                xml_doc = etree.parse(xml_file_handle)
            
            is_valid = schema.validate(xml_doc)
            errors = [str(error) for error in schema.error_log] if not is_valid else []
            
            return {'valid': is_valid, 'errors': errors}
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}