"""
FrameNet Parser Module

Specialized parser for FrameNet XML corpus files. Handles parsing of frames,
lexical units, frame elements, and frame relations from XML files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional


class FrameNetParser:
    """
    Parser for FrameNet XML corpus files.
    
    Handles parsing of frames, lexical units, frame elements, frame-to-frame
    relations, and full-text annotations.
    """
    
    # FrameNet namespace mapping
    NAMESPACES = {
        'fn': 'http://framenet.icsi.berkeley.edu'
    }
    
    def __init__(self, corpus_path: Path):
        """
        Initialize FrameNet parser with corpus path.
        
        Args:
            corpus_path (Path): Path to FrameNet corpus directory
        """
        self.corpus_path = corpus_path
        self.frame_dir = corpus_path / "frame" if corpus_path else None
        
    def _strip_namespace(self, tag: str) -> str:
        """
        Strip namespace from XML tag.
        
        Args:
            tag (str): XML tag with or without namespace
            
        Returns:
            str: Tag without namespace
        """
        if '}' in tag:
            return tag.split('}')[1]
        return tag
    
    def _get_namespaced_tag(self, tag: str) -> str:
        """
        Get the expected namespaced tag for FrameNet XML.
        
        Args:
            tag (str): Base tag name
            
        Returns:
            str: Namespaced tag
        """
        return f"{{{self.NAMESPACES['fn']}}}{tag}"
    
    def _find_element(self, parent: ET.Element, tag: str) -> Optional[ET.Element]:
        """
        Find child element handling both namespaced and non-namespaced XML.
        
        Args:
            parent (ET.Element): Parent element to search in
            tag (str): Tag name to search for
            
        Returns:
            Optional[ET.Element]: Found element or None
        """
        # Try without namespace first
        element = parent.find(f".//{tag}")
        if element is not None:
            return element
            
        # Try with namespace
        namespaced_tag = self._get_namespaced_tag(tag)
        return parent.find(f".//{namespaced_tag}")
    
    def _find_elements(self, parent: ET.Element, tag: str) -> List[ET.Element]:
        """
        Find all child elements handling both namespaced and non-namespaced XML.
        
        Args:
            parent (ET.Element): Parent element to search in
            tag (str): Tag name to search for
            
        Returns:
            List[ET.Element]: List of found elements
        """
        # Try without namespace first
        elements = parent.findall(f".//{tag}")
        if elements:
            return elements
            
        # Try with namespace
        namespaced_tag = self._get_namespaced_tag(tag)
        return parent.findall(f".//{namespaced_tag}")
        
    def parse_all_frames(self) -> Dict[str, Any]:
        """
        Parse all FrameNet frame files in the corpus directory.
        
        Returns:
            dict: Complete FrameNet frame data
        """
        framenet_data = {
            'frames': {},
            'frame_relations': {},
            'lexical_units': {},
            'frame_elements': {}
        }
        
        if not self.frame_dir or not self.frame_dir.exists():
            return framenet_data
            
        # Parse frame index if available
        frame_index_path = self.corpus_path / "frameIndex.xml"
        if frame_index_path.exists():
            framenet_data['frame_index'] = self.parse_frame_index(frame_index_path)
        
        # Parse frame relation data
        frame_relation_path = self.corpus_path / "frRelation.xml"
        if frame_relation_path.exists():
            framenet_data['frame_relations'] = self.parse_frame_relations(frame_relation_path)
        
        # Parse individual frame files
        xml_files = list(self.frame_dir.glob('*.xml'))
        
        for xml_file in xml_files:
            if xml_file.name.endswith('.xsl'):
                continue
                
            try:
                frame_data = self.parse_frame_file(xml_file)
                if frame_data and 'name' in frame_data:
                    framenet_data['frames'][frame_data['name']] = frame_data
            except Exception as e:
                print(f"Error parsing FrameNet file {xml_file}: {e}")
        
        return framenet_data
    
    def parse_frame_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single FrameNet frame XML file.
        
        Args:
            file_path (Path): Path to FrameNet XML file
            
        Returns:
            dict: Parsed frame data or None if parsing failed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Handle both namespaced and non-namespaced XML
            root_tag = self._strip_namespace(root.tag)
            if root_tag == 'frame':
                return self._parse_frame_element(root)
            else:
                print(f"Unexpected root element {root.tag} in {file_path}")
                return None
        except Exception as e:
            print(f"Error parsing FrameNet file {file_path}: {e}")
            return None
    
    def _parse_frame_element(self, frame_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a frame XML element.
        
        Args:
            frame_element (ET.Element): Frame XML element
            
        Returns:
            dict: Parsed frame data
        """
        frame_data = {
            'name': frame_element.get('name', ''),
            'ID': frame_element.get('ID', ''),
            'attributes': dict(frame_element.attrib),
            'definition': self._extract_text_content(self._find_element(frame_element, 'definition')),
            'frame_elements': self._parse_frame_elements(frame_element),
            'lexical_units': self._parse_lexical_units(frame_element),
            'frame_relations': self._parse_frame_relations_in_frame(frame_element),
            'semtypes': self._parse_semtypes(frame_element)
        }
        
        return frame_data
    
    def _parse_frame_elements(self, frame_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse FE (Frame Element) elements from a frame."""
        frame_elements = []
        
        for fe in self._find_elements(frame_element, 'FE'):
            fe_data = {
                'name': fe.get('name', ''),
                'ID': fe.get('ID', ''),
                'coreType': fe.get('coreType', ''),
                'attributes': dict(fe.attrib),
                'definition': self._extract_text_content(fe.find('.//definition')),
                'semtypes': self._parse_semtypes(fe)
            }
            frame_elements.append(fe_data)
        
        return frame_elements
    
    def _parse_lexical_units(self, frame_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse lexUnit elements from a frame."""
        lexical_units = []
        
        for lexunit in frame_element.findall('.//lexUnit'):
            lu_data = {
                'name': lexunit.get('name', ''),
                'ID': lexunit.get('ID', ''),
                'POS': lexunit.get('POS', ''),
                'lemmaID': lexunit.get('lemmaID', ''),
                'attributes': dict(lexunit.attrib),
                'definition': self._extract_text_content(lexunit.find('.//definition')),
                'semtypes': self._parse_semtypes(lexunit)
            }
            lexical_units.append(lu_data)
        
        return lexical_units
    
    def _parse_frame_relations_in_frame(self, frame_element: ET.Element) -> List[Dict[str, Any]]:
        """Parse frameRelation elements from within a frame."""
        relations = []
        
        for relation in frame_element.findall('.//frameRelation'):
            rel_data = {
                'type': relation.get('type', ''),
                'attributes': dict(relation.attrib),
                'related_frames': []
            }
            
            for related_frame in relation.findall('.//relatedFrame'):
                related_data = {
                    'name': related_frame.get('name', ''),
                    'ID': related_frame.get('ID', ''),
                    'attributes': dict(related_frame.attrib)
                }
                rel_data['related_frames'].append(related_data)
            
            relations.append(rel_data)
        
        return relations
    
    def _parse_semtypes(self, element: ET.Element) -> List[Dict[str, Any]]:
        """Parse semType elements from an element."""
        semtypes = []
        
        for semtype in element.findall('.//semType'):
            semtype_data = {
                'name': semtype.get('name', ''),
                'ID': semtype.get('ID', ''),
                'attributes': dict(semtype.attrib)
            }
            semtypes.append(semtype_data)
        
        return semtypes
    
    def _extract_text_content(self, element: Optional[ET.Element]) -> str:
        """Extract text content from an XML element."""
        if element is not None and element.text:
            return element.text.strip()
        return ""
    
    def parse_frame_index(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse the frameIndex.xml file.
        
        Args:
            file_path (Path): Path to frameIndex.xml
            
        Returns:
            dict: Parsed frame index data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            index_data = {
                'frames': []
            }
            
            for frame in root.findall('.//frame'):
                frame_info = {
                    'name': frame.get('name', ''),
                    'ID': frame.get('ID', ''),
                    'attributes': dict(frame.attrib)
                }
                index_data['frames'].append(frame_info)
            
            return index_data
        except Exception as e:
            print(f"Error parsing frame index: {e}")
            return {}
    
    def parse_frame_relations(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse the frRelation.xml file.
        
        Args:
            file_path (Path): Path to frRelation.xml
            
        Returns:
            dict: Parsed frame relation data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            relations_data = {
                'frame_relations': []
            }
            
            for relation in root.findall('.//frameRelation'):
                relation_info = {
                    'type': relation.get('type', ''),
                    'supFrame': relation.get('supFrame', ''),
                    'subFrame': relation.get('subFrame', ''),
                    'attributes': dict(relation.attrib)
                }
                relations_data['frame_relations'].append(relation_info)
            
            return relations_data
        except Exception as e:
            print(f"Error parsing frame relations: {e}")
            return {}
    
    def parse_lexical_unit_index(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse the luIndex.xml file if available.
        
        Args:
            file_path (Path): Path to luIndex.xml
            
        Returns:
            dict: Parsed lexical unit index data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            lu_index_data = {
                'lexical_units': []
            }
            
            for lu in root.findall('.//lu'):
                lu_info = {
                    'name': lu.get('name', ''),
                    'ID': lu.get('ID', ''),
                    'frame': lu.get('frame', ''),
                    'frameID': lu.get('frameID', ''),
                    'POS': lu.get('POS', ''),
                    'attributes': dict(lu.attrib)
                }
                lu_index_data['lexical_units'].append(lu_info)
            
            return lu_index_data
        except Exception as e:
            print(f"Error parsing lexical unit index: {e}")
            return {}
    
    def parse_fulltext_index(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse the fulltextIndex.xml file if available.
        
        Args:
            file_path (Path): Path to fulltextIndex.xml
            
        Returns:
            dict: Parsed fulltext index data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            ft_index_data = {
                'documents': []
            }
            
            for doc in root.findall('.//document'):
                doc_info = {
                    'name': doc.get('name', ''),
                    'ID': doc.get('ID', ''),
                    'description': self._extract_text_content(doc.find('.//description')),
                    'attributes': dict(doc.attrib)
                }
                ft_index_data['documents'].append(doc_info)
            
            return ft_index_data
        except Exception as e:
            print(f"Error parsing fulltext index: {e}")
            return {}