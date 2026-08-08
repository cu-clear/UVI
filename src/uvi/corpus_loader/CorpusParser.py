"""
CorpusParser Class

A specialized class for parsing various linguistic corpus formats (VerbNet, FrameNet, 
PropBank, OntoNotes, WordNet, BSO, SemNet, Reference Docs, VN API).

This class contains all parsing methods extracted from CorpusLoader as part of the 
refactoring plan to separate concerns and improve maintainability.
"""

import xml.etree.ElementTree as ET
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from functools import wraps


def error_handler(operation_name: str = "operation", default_return=None):
    """
    Decorator for common error handling patterns.
    
    Args:
        operation_name (str): Description of the operation for logging
        default_return: Value to return on error (defaults to None)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Get the file path from args if available for better error messages
                file_path = ""
                if args and hasattr(args[0], '__str__'):
                    file_path = f" {args[0]}"
                
                self.logger.error(f"Error during {operation_name}{file_path}: {e}")
                return default_return if default_return is not None else {}
        return wrapper
    return decorator


class CorpusParser:
    """
    A specialized class for parsing various linguistic corpus formats.
    
    This class handles the parsing of all corpus types including VerbNet, FrameNet,
    PropBank, OntoNotes, WordNet, BSO mappings, SemNet data, reference documentation,
    and VN API files.
    """
    
    def __init__(self, corpus_paths: Dict[str, Path], logger):
        """
        Initialize the CorpusParser with corpus paths and logger.
        
        Args:
            corpus_paths (Dict[str, Path]): Dictionary mapping corpus names to their paths
            logger: Logger instance for error reporting and information
        """
        self.corpus_paths = corpus_paths
        self.logger = logger
        self.bso_mappings = {}

    # Common file parsing utilities
    
    def _parse_xml_file(self, file_path: Path) -> Optional[ET.Element]:
        """
        Common XML file parsing utility.
        
        Args:
            file_path (Path): Path to XML file
            
        Returns:
            ET.Element: Root element of parsed XML, None if parsing failed
        """
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except Exception as e:
            self.logger.error(f"Error parsing XML file {file_path}: {e}")
            return None
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Common JSON file loading utility.
        
        Args:
            file_path (Path): Path to JSON file
            
        Returns:
            dict: Parsed JSON data, empty dict if loading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {e}")
            return {}
    
    def _load_csv_file(self, file_path: Path, delimiter: str = ',') -> List[Dict[str, str]]:
        """
        Common CSV/TSV file loading utility.
        
        Args:
            file_path (Path): Path to CSV/TSV file
            delimiter (str): Field delimiter (default: ',')
            
        Returns:
            list: List of row dictionaries, empty list if loading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            self.logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def _validate_file_path(self, corpus_name: str) -> Path:
        """
        Common file path validation utility.
        
        Args:
            corpus_name (str): Name of the corpus
            
        Returns:
            Path: Validated corpus path
            
        Raises:
            FileNotFoundError: If corpus path not configured
        """
        if corpus_name not in self.corpus_paths:
            raise FileNotFoundError(f"{corpus_name} corpus path not configured")
        return self.corpus_paths[corpus_name]
    
    def _create_statistics_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Create standardized statistics dictionary.
        
        Args:
            **kwargs: Statistics key-value pairs
            
        Returns:
            dict: Standardized statistics dictionary
        """
        return {k: v for k, v in kwargs.items() if v is not None}
    
    def _extract_xml_element_data(self, element: ET.Element, attributes: List[str]) -> Dict[str, str]:
        """
        Extract common XML element attributes as dictionary.
        
        Args:
            element (ET.Element): XML element
            attributes (List[str]): List of attribute names to extract
            
        Returns:
            dict: Dictionary mapping attribute names to values
        """
        return {attr: element.get(attr, '') for attr in attributes}
    
    def _extract_text_content(self, element: Optional[ET.Element]) -> str:
        """
        Extract text content from XML element safely.
        
        Args:
            element (ET.Element): XML element (can be None)
            
        Returns:
            str: Text content or empty string if element is None or has no text
        """
        return element.text.strip() if element is not None and element.text else ''

    # VerbNet parsing methods

    def parse_verbnet_files(self) -> Dict[str, Any]:
        """
        Parse all VerbNet XML files and build internal data structures.
        
        Returns:
            dict: Parsed VerbNet data with hierarchy and cross-references
        """
        verbnet_path = self._validate_file_path('verbnet')
        
        verbnet_data = {
            'classes': {},
            'hierarchy': {},
            'members': {},
            'statistics': {}
        }
        
        # Find all VerbNet XML files
        xml_files = list(verbnet_path.glob('*.xml'))
        if not xml_files:
            xml_files = list(verbnet_path.glob('**/*.xml'))
        
        xml_files = [f for f in xml_files if not f.name.startswith('.')]
        
        self.logger.info(f"Found {len(xml_files)} VerbNet XML files to process")
        
        parsed_count = 0
        error_count = 0
        
        for xml_file in xml_files:
            class_data = self._parse_verbnet_class(xml_file)
            if class_data and 'id' in class_data:
                verbnet_data['classes'][class_data['id']] = class_data
                
                # Build member index using common utility
                self._build_member_index(class_data, verbnet_data['members'])
                
                parsed_count += 1
            else:
                # Empty dict returned means parsing failed
                error_count += 1
        
        # Build class hierarchy
        verbnet_data['hierarchy'] = self._build_verbnet_hierarchy(verbnet_data['classes'])
        
        verbnet_data['statistics'] = self._create_statistics_dict(
            total_files=len(xml_files),
            parsed_files=parsed_count,
            error_files=error_count,
            total_classes=len(verbnet_data['classes']),
            total_members=len(verbnet_data['members'])
        )
        
        self.logger.info(f"VerbNet parsing complete: {parsed_count} classes loaded")
        
        return verbnet_data
    
    def _build_member_index(self, class_data: Dict[str, Any], members_index: Dict[str, List[str]]) -> None:
        """
        Build member index from class data.
        
        Args:
            class_data (dict): Class data containing members
            members_index (dict): Members index to update
        """
        for member in class_data.get('members', []):
            member_name = member.get('name', '')
            if member_name:
                if member_name not in members_index:
                    members_index[member_name] = []
                members_index[member_name].append(class_data['id'])
    
    @error_handler("parsing VerbNet class", {})
    def _parse_verbnet_class(self, xml_file_path: Path) -> Dict[str, Any]:
        """
        Parse a VerbNet class XML file.
        
        Args:
            xml_file_path (Path): Path to VerbNet XML file
            
        Returns:
            dict: Parsed VerbNet class data
        """
        root = self._parse_xml_file(xml_file_path)
        if root is None or root.tag != 'VNCLASS':
            return {}
        
        class_data = {
            'id': root.get('ID', ''),
            'members': [],
            'themroles': [],
            'frames': [],
            'subclasses': [],
            'source_file': str(xml_file_path)
        }
        
        # Extract members using common utility
        class_data['members'] = self._extract_members(root)
        
        # Extract thematic roles
        class_data['themroles'] = self._extract_themroles(root)
        
        # Extract frames
        class_data['frames'] = self._extract_frames(root)
        
        # Extract subclasses recursively
        for subclass in root.findall('.//VNSUBCLASS'):
            subclass_data = self._parse_verbnet_subclass(subclass)
            if subclass_data:
                class_data['subclasses'].append(subclass_data)
        
        return class_data
    
    def _extract_members(self, root: ET.Element) -> List[Dict[str, str]]:
        """
        Extract members from VerbNet XML element.
        
        Args:
            root (ET.Element): Root XML element
            
        Returns:
            list: List of member dictionaries
        """
        members = []
        for member in root.findall('.//MEMBER'):
            member_data = self._extract_xml_element_data(member, ['name', 'wn', 'grouping'])
            members.append(member_data)
        return members
    
    def _extract_themroles(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract thematic roles from VerbNet XML element.
        
        Args:
            root (ET.Element): Root XML element
            
        Returns:
            list: List of thematic role dictionaries
        """
        themroles = []
        for themrole in root.findall('.//THEMROLE'):
            role_data = {
                'type': themrole.get('type', ''),
                'selrestrs': []
            }
            
            # Extract selectional restrictions
            for selrestr in themrole.findall('.//SELRESTR'):
                selrestr_data = self._extract_xml_element_data(selrestr, ['Value', 'type'])
                role_data['selrestrs'].append(selrestr_data)
            
            themroles.append(role_data)
        return themroles
    
    def _extract_frames(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract frames from VerbNet XML element.
        
        Args:
            root (ET.Element): Root XML element
            
        Returns:
            list: List of frame dictionaries
        """
        frames = []
        for frame in root.findall('.//FRAME'):
            frame_data = {
                'description': self._extract_frame_description(frame),
                'examples': [],
                'syntax': [],
                'semantics': []
            }
            
            # Extract examples
            for example in frame.findall('.//EXAMPLE'):
                example_text = self._extract_text_content(example)
                if example_text:
                    frame_data['examples'].append(example_text)
            
            # Extract syntax and semantics
            frame_data['syntax'] = self._extract_syntax_elements(frame)
            frame_data['semantics'] = self._extract_semantics_elements(frame)
            
            frames.append(frame_data)
        return frames
    
    def _extract_syntax_elements(self, frame: ET.Element) -> List[List[Dict[str, Any]]]:
        """
        Extract syntax elements from frame.
        
        Args:
            frame (ET.Element): Frame XML element
            
        Returns:
            list: List of syntax element lists
        """
        syntax_elements = []
        for syntax in frame.findall('.//SYNTAX'):
            syntax_data = []
            for element in syntax:
                if element.tag == 'NP':
                    np_data = {
                        'type': 'NP',
                        'value': element.get('value', ''),
                        'synrestrs': []
                    }
                    for synrestr in element.findall('.//SYNRESTR'):
                        synrestr_data = self._extract_xml_element_data(synrestr, ['Value', 'type'])
                        np_data['synrestrs'].append(synrestr_data)
                    syntax_data.append(np_data)
                elif element.tag == 'VERB':
                    syntax_data.append({'type': 'VERB'})
                elif element.tag in ['PREP', 'ADV', 'ADJ']:
                    element_data = self._extract_xml_element_data(element, ['value'])
                    element_data['type'] = element.tag
                    syntax_data.append(element_data)
            
            syntax_elements.append(syntax_data)
        return syntax_elements
    
    def _extract_semantics_elements(self, frame: ET.Element) -> List[List[Dict[str, Any]]]:
        """
        Extract semantics elements from frame.
        
        Args:
            frame (ET.Element): Frame XML element
            
        Returns:
            list: List of semantics element lists
        """
        semantics_elements = []
        for semantics in frame.findall('.//SEMANTICS'):
            semantics_data = []
            for pred in semantics.findall('.//PRED'):
                pred_data = {
                    'value': pred.get('value', ''),
                    'args': []
                }
                for arg in pred.findall('.//ARG'):
                    arg_data = self._extract_xml_element_data(arg, ['type', 'value'])
                    pred_data['args'].append(arg_data)
                semantics_data.append(pred_data)
            
            semantics_elements.append(semantics_data)
        return semantics_elements
    
    def _parse_verbnet_subclass(self, subclass_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a VerbNet subclass element recursively.
        
        Args:
            subclass_element (ET.Element): VerbNet subclass XML element
            
        Returns:
            dict: Parsed subclass data
        """
        subclass_data = {
            'id': subclass_element.get('ID', ''),
            'members': [],
            'themroles': [],
            'frames': [],
            'subclasses': []
        }
        
        # Extract members
        for member in subclass_element.findall('MEMBERS/MEMBER'):
            member_data = self._extract_xml_element_data(member, ['name', 'wn', 'grouping'])
            subclass_data['members'].append(member_data)
        
        # Extract frames
        for frame in subclass_element.findall('FRAMES/FRAME'):
            frame_data = {
                'description': self._extract_frame_description(frame),
                'examples': [],
                'syntax': [],
                'semantics': []
            }
            
            # Extract examples
            for example in frame.findall('.//EXAMPLE'):
                example_text = self._extract_text_content(example)
                if example_text:
                    frame_data['examples'].append(example_text)
            
            subclass_data['frames'].append(frame_data)
        
        # Recursively extract nested subclasses
        for nested_subclass in subclass_element.findall('SUBCLASSES/VNSUBCLASS'):
            nested_data = self._parse_verbnet_subclass(nested_subclass)
            if nested_data:
                subclass_data['subclasses'].append(nested_data)
        
        return subclass_data
    
    def _extract_frame_description(self, frame_element: ET.Element) -> Dict[str, str]:
        """
        Extract frame description from VerbNet frame element.
        
        Args:
            frame_element (ET.Element): VerbNet frame XML element
            
        Returns:
            dict: Frame description data
        """
        description = {
            'primary': frame_element.get('primary', ''),
            'secondary': frame_element.get('secondary', ''),
            'descriptionNumber': frame_element.get('descriptionNumber', ''),
            'xtag': frame_element.get('xtag', '')
        }
        return description
    
    def _build_verbnet_hierarchy(self, classes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build VerbNet class hierarchy from parsed classes.
        
        Args:
            classes (dict): Dictionary of parsed VerbNet classes
            
        Returns:
            dict: Hierarchical organization of classes
        """
        hierarchy = {
            'by_name': {},
            'by_id': {},
            'parent_child': {}
        }
        
        # Group by first letter for name-based hierarchy
        for class_id, class_data in classes.items():
            if class_id:
                first_char = class_id[0].upper()
                if first_char not in hierarchy['by_name']:
                    hierarchy['by_name'][first_char] = []
                hierarchy['by_name'][first_char].append(class_id)
        
        # Group by numeric prefix for ID-based hierarchy
        for class_id in classes.keys():
            if class_id:
                # Extract numeric prefix (e.g., "10.1" from "accept-10.1")
                match = re.search(r'(\d+)', class_id)
                if match:
                    prefix = match.group(1)
                    if prefix not in hierarchy['by_id']:
                        hierarchy['by_id'][prefix] = []
                    hierarchy['by_id'][prefix].append(class_id)
        
        # Build parent-child relationships
        for class_id in classes.keys():
            if class_id and '-' in class_id:
                parts = class_id.split('-')
                if len(parts) > 1:
                    # Find potential parent (e.g., "accept-77" is parent of "accept-77.1")
                    base_id = parts[0]
                    numeric_part = parts[1]
                    if '.' in numeric_part:
                        parent_numeric = numeric_part.split('.')[0]
                        potential_parent = f"{base_id}-{parent_numeric}"
                        if potential_parent in classes:
                            if potential_parent not in hierarchy['parent_child']:
                                hierarchy['parent_child'][potential_parent] = []
                            hierarchy['parent_child'][potential_parent].append(class_id)
        
        return hierarchy

    # FrameNet parsing methods
    
    def parse_framenet_files(self) -> Dict[str, Any]:
        """
        Parse FrameNet XML files (frames, lexical units, full-text).
        
        Returns:
            dict: Parsed FrameNet data with frame relationships
        """
        framenet_path = self._validate_file_path('framenet')
        
        framenet_data = {
            'frames': {},
            'lexical_units': {},
            'frame_relations': {},
            'statistics': {}
        }
        
        # Parse frame index
        frame_index_path = framenet_path / 'frameIndex.xml'
        if frame_index_path.exists():
            framenet_data['frame_index'] = self._parse_framenet_frame_index(frame_index_path)
        
        # Parse individual frame files
        frame_dir = framenet_path / 'frame'
        parsed_count = 0
        if frame_dir.exists():
            frame_files = list(frame_dir.glob('*.xml'))
            
            for frame_file in frame_files:
                frame_data = self._parse_framenet_frame(frame_file)
                if frame_data and 'name' in frame_data:
                    framenet_data['frames'][frame_data['name']] = frame_data
                    parsed_count += 1
        
        # Parse lexical unit index
        lu_index_path = framenet_path / 'luIndex.xml'
        if lu_index_path.exists():
            framenet_data['lu_index'] = self._parse_framenet_lu_index(lu_index_path)
        
        # Parse frame relations
        fr_relation_path = framenet_path / 'frRelation.xml'
        if fr_relation_path.exists():
            framenet_data['frame_relations'] = self._parse_framenet_relations(fr_relation_path)
        
        framenet_data['statistics'] = self._create_statistics_dict(
            frames_parsed=parsed_count,
            total_frames=len(framenet_data['frames'])
        )
        
        self.logger.info(f"FrameNet parsing complete: {len(framenet_data['frames'])} frames loaded")
        
        return framenet_data
    
    @error_handler("parsing FrameNet frame index", {})
    def _parse_framenet_frame_index(self, index_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet frame index file.
        
        Args:
            index_path (Path): Path to frameIndex.xml
            
        Returns:
            dict: Parsed frame index data
        """
        root = self._parse_xml_file(index_path)
        if root is None:
            return {}
        
        frame_index = {}
        for frame in root.findall('.//frame'):
            frame_data = self._extract_xml_element_data(frame, ['ID', 'name', 'cDate'])
            frame_id = frame_data.get('ID')
            frame_name = frame_data.get('name')
            
            if frame_id and frame_name:
                frame_index[frame_name] = {
                    'id': frame_id,
                    'name': frame_name,
                    'cdate': frame_data.get('cDate', ''),
                    'file': f"{frame_name}.xml"
                }
        
        return frame_index
    
    @error_handler("parsing FrameNet frame", {})
    def _parse_framenet_frame(self, frame_file: Path) -> Dict[str, Any]:
        """
        Parse a FrameNet frame XML file.
        
        Args:
            frame_file (Path): Path to FrameNet frame XML file
            
        Returns:
            dict: Parsed FrameNet frame data
        """
        root = self._parse_xml_file(frame_file)
        if root is None:
            return {}
        
        # Define FrameNet namespace
        framenet_ns = {'fn': 'http://framenet.icsi.berkeley.edu'}
        
        frame_data = self._extract_xml_element_data(root, ['name', 'ID'])
        frame_data.update({
            'definition': self._extract_text_content(root.find('.//fn:definition', framenet_ns)),
            'frame_elements': {},
            'lexical_units': {},
            'frame_relations': [],
            'source_file': str(frame_file)
        })
        
        # Extract frame elements
        for fe in root.findall('.//fn:FE', framenet_ns):
            fe_data = self._extract_xml_element_data(fe, ['name', 'ID', 'coreType'])
            fe_name = fe_data.get('name')
            if fe_name:
                fe_data['definition'] = self._extract_text_content(fe.find('.//fn:definition', framenet_ns))
                frame_data['frame_elements'][fe_name] = fe_data
        
        # Extract lexical units
        for lu in root.findall('.//fn:lexUnit', framenet_ns):
            lu_data = self._extract_xml_element_data(lu, ['name', 'ID', 'POS', 'lemmaID'])
            lu_name = lu_data.get('name')
            if lu_name:
                lu_data['definition'] = self._extract_text_content(lu.find('.//fn:definition', framenet_ns))
                frame_data['lexical_units'][lu_name] = lu_data
        
        return frame_data
    
    @error_handler("parsing FrameNet LU index", {})
    def _parse_framenet_lu_index(self, index_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet lexical unit index.
        
        Args:
            index_path (Path): Path to luIndex.xml
            
        Returns:
            dict: Parsed lexical unit index
        """
        root = self._parse_xml_file(index_path)
        if root is None:
            return {}
        
        lu_index = {}
        for lu in root.findall('.//lu'):
            lu_data = self._extract_xml_element_data(lu, ['name', 'ID', 'POS', 'frame'])
            lu_name = lu_data.get('name')
            if lu_name:
                lu_index[lu_name] = lu_data
        
        return lu_index
    
    @error_handler("parsing FrameNet relations", {})
    def _parse_framenet_relations(self, relations_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet frame relations file.
        
        Args:
            relations_path (Path): Path to frRelation.xml
            
        Returns:
            dict: Parsed frame relations data
        """
        root = self._parse_xml_file(relations_path)
        if root is None:
            return {}
        
        relations_data = {
            'frame_relations': [],
            'fe_relations': []
        }
        
        # Define FrameNet namespace
        fn_namespace = {'fn': 'http://framenet.icsi.berkeley.edu'}
        
        # Try parsing with namespace first (real FrameNet data)
        frame_relation_types = root.findall('.//fn:frameRelationType', fn_namespace)
        if frame_relation_types:
            # Parse frame-to-frame relations with namespace support
            for relation_type in frame_relation_types:
                relation_type_name = relation_type.get('name', '')
                
                for relation in relation_type.findall('.//fn:frameRelation', fn_namespace):
                    relation_data = {
                        'type': relation_type_name,
                        'ID': relation.get('ID', ''),
                        'subID': relation.get('subID', ''),
                        'supID': relation.get('supID', ''),
                        'subFrameName': relation.get('subFrameName', ''),
                        'superFrameName': relation.get('superFrameName', '')
                    }
                    relations_data['frame_relations'].append(relation_data)
            
            # Parse frame element relations with namespace support
            for fe_relation in root.findall('.//fn:feRelation', fn_namespace):
                fe_relation_data = self._extract_xml_element_data(fe_relation, ['type', 'superFE', 'subFE', 'frameRelation'])
                relations_data['fe_relations'].append(fe_relation_data)
        else:
            # Fallback for non-namespaced XML (tests)
            for relation in root.findall('.//frameRelation'):
                relation_data = self._extract_xml_element_data(relation, ['type', 'superFrame', 'subFrame'])
                relations_data['frame_relations'].append(relation_data)
            
            # Parse frame element relations without namespace
            for fe_relation in root.findall('.//feRelation'):
                fe_relation_data = self._extract_xml_element_data(fe_relation, ['type', 'superFE', 'subFE', 'frameRelation'])
                relations_data['fe_relations'].append(fe_relation_data)
        
        return relations_data

    # PropBank parsing methods
    
    def parse_propbank_files(self) -> Dict[str, Any]:
        """
        Parse PropBank XML files and extract predicate structures.
        
        Returns:
            dict: Parsed PropBank data with role mappings
        """
        propbank_path = self._validate_file_path('propbank')
        
        propbank_data = {
            'predicates': {},
            'rolesets': {},
            'statistics': {}
        }
        
        # Find PropBank frame files
        frame_files = []
        for pattern in ['frames/*.xml', '**/frames/*.xml']:
            frame_files.extend(list(propbank_path.glob(pattern)))
        
        # Also check for verb frame files directly in the directory
        verb_files = list(propbank_path.glob('*-v.xml'))
        frame_files.extend(verb_files)
        
        # Remove duplicates and filter out non-frame files
        frame_files = list(set(frame_files))
        frame_files = [f for f in frame_files if 'frames' in str(f) or '-v.xml' in f.name]
        
        parsed_count = 0
        for frame_file in frame_files:
            predicate_data = self._parse_propbank_frame(frame_file)
            if predicate_data and 'lemma' in predicate_data:
                propbank_data['predicates'][predicate_data['lemma']] = predicate_data
                
                # Index rolesets
                self._index_rolesets(predicate_data, propbank_data['rolesets'])
                
                parsed_count += 1
        
        propbank_data['statistics'] = self._create_statistics_dict(
            files_processed=len(frame_files),
            predicates_parsed=parsed_count,
            total_rolesets=len(propbank_data['rolesets'])
        )
        
        self.logger.info(f"PropBank parsing complete: {parsed_count} predicates loaded")
        
        return propbank_data
    
    def _index_rolesets(self, predicate_data: Dict[str, Any], rolesets_index: Dict[str, Any]) -> None:
        """
        Index rolesets from predicate data.
        
        Args:
            predicate_data (dict): Predicate data containing rolesets
            rolesets_index (dict): Rolesets index to update
        """
        for roleset in predicate_data.get('rolesets', []):
            roleset_id = roleset.get('id')
            if roleset_id:
                rolesets_index[roleset_id] = roleset
    
    @error_handler("parsing PropBank frame", {})
    def _parse_propbank_frame(self, frame_file: Path) -> Dict[str, Any]:
        """
        Parse a PropBank frame XML file.
        
        Args:
            frame_file (Path): Path to PropBank XML file
            
        Returns:
            dict: Parsed PropBank frame data
        """
        root = self._parse_xml_file(frame_file)
        if root is None:
            return {}
        
        predicate_data = {
            'lemma': root.get('lemma', ''),
            'rolesets': [],
            'source_file': str(frame_file)
        }
        
        # Extract rolesets
        for roleset in root.findall('.//roleset'):
            roleset_data = self._extract_xml_element_data(roleset, ['id', 'name', 'vncls'])
            roleset_data.update({
                'roles': [],
                'examples': []
            })
            
            # Extract roles
            for role in roleset.findall('.//role'):
                role_data = self._extract_xml_element_data(role, ['n', 'descr', 'f', 'vnrole'])
                roleset_data['roles'].append(role_data)
            
            # Extract examples
            for example in roleset.findall('.//example'):
                example_data = self._extract_xml_element_data(example, ['name', 'src'])
                example_data.update({
                    'text': self._extract_text_content(example.find('text')),
                    'args': []
                })
                
                # Extract arguments
                for arg in example.findall('.//arg'):
                    arg_data = self._extract_xml_element_data(arg, ['n', 'f'])
                    arg_data['text'] = self._extract_text_content(arg)
                    example_data['args'].append(arg_data)
                
                roleset_data['examples'].append(example_data)
            
            predicate_data['rolesets'].append(roleset_data)
        
        return predicate_data

    # OntoNotes parsing methods
    
    def parse_ontonotes_files(self) -> Dict[str, Any]:
        """
        Parse OntoNotes XML sense inventory files.
        
        Returns:
            dict: Parsed OntoNotes data with cross-resource mappings
        """
        ontonotes_path = self._validate_file_path('ontonotes')
        
        ontonotes_data = {
            'sense_inventories': {},
            'statistics': {}
        }
        
        # Find OntoNotes sense files
        sense_files = []
        for pattern in ['*.xml', '**/*.xml', 'sense-inventories/*.xml']:
            sense_files.extend(list(ontonotes_path.glob(pattern)))
        
        parsed_count = 0
        for sense_file in sense_files:
            sense_data = self._parse_ontonotes_data(sense_file)
            if sense_data and 'lemma' in sense_data:
                ontonotes_data['sense_inventories'][sense_data['lemma']] = sense_data
                parsed_count += 1
        
        ontonotes_data['statistics'] = self._create_statistics_dict(
            files_processed=len(sense_files),
            sense_inventories_parsed=parsed_count
        )
        
        self.logger.info(f"OntoNotes parsing complete: {parsed_count} sense inventories loaded")
        
        return ontonotes_data
    
    @error_handler("parsing OntoNotes sense data", {})
    def _parse_ontonotes_data(self, sense_file: Path) -> Dict[str, Any]:
        """
        Parse OntoNotes sense inventory file.
        
        Args:
            sense_file (Path): Path to OntoNotes sense file
            
        Returns:
            dict: Parsed OntoNotes sense data
        """
        root = self._parse_xml_file(sense_file)
        if root is None:
            return {}
        
        sense_data = {
            'lemma': root.get('lemma', ''),
            'senses': [],
            'source_file': str(sense_file)
        }
        
        # Extract senses
        for sense in root.findall('.//sense'):
            sense_info = self._extract_xml_element_data(sense, ['n', 'name', 'group'])
            sense_info.update({
                'commentary': self._extract_text_content(sense.find('commentary')),
                'examples': [],
                'mappings': {}
            })
            
            # Extract examples
            for example in sense.findall('.//example'):
                example_text = self._extract_text_content(example)
                if example_text:
                    sense_info['examples'].append(example_text)
            
            # Extract mappings (WordNet, VerbNet, PropBank, etc.)
            mappings_elem = sense.find('mappings')
            if mappings_elem is not None:
                for mapping in mappings_elem:
                    mapping_type = mapping.tag
                    mapping_value = mapping.get('version', self._extract_text_content(mapping))
                    sense_info['mappings'][mapping_type] = mapping_value
            
            sense_data['senses'].append(sense_info)
        
        return sense_data

    # WordNet parsing methods
    
    def parse_wordnet_files(self) -> Dict[str, Any]:
        """
        Parse WordNet data files, indices, and exception lists.
        
        Returns:
            dict: Parsed WordNet data with synset relationships
        """
        wordnet_path = self._validate_file_path('wordnet')
        
        wordnet_data = {
            'synsets': {},
            'index': {},
            'exceptions': {},
            'statistics': {}
        }
        
        # Parse data files (data.verb, data.noun, etc.)
        data_files = list(wordnet_path.glob('data.*'))
        for data_file in data_files:
            pos = data_file.name.split('.')[1]
            synsets = self._parse_wordnet_data_file(data_file)
            if synsets:
                wordnet_data['synsets'][pos] = synsets
                self.logger.info(f"Parsed WordNet {pos} data: {len(synsets)} synsets")
        
        # Parse index files (index.verb, index.noun, etc.)
        index_files = list(wordnet_path.glob('index.*'))
        for index_file in index_files:
            pos = index_file.name.split('.')[1]
            if pos != 'sense':  # Skip index.sense for now
                index_data = self._parse_wordnet_index_file(index_file)
                if index_data:
                    wordnet_data['index'][pos] = index_data
                    self.logger.info(f"Parsed WordNet {pos} index: {len(index_data)} entries")
        
        # Parse exception files (verb.exc, noun.exc, etc.)
        exc_files = list(wordnet_path.glob('*.exc'))
        for exc_file in exc_files:
            pos = exc_file.name.split('.')[0]
            exceptions = self._parse_wordnet_exception_file(exc_file)
            if exceptions:
                wordnet_data['exceptions'][pos] = exceptions
                self.logger.info(f"Parsed WordNet {pos} exceptions: {len(exceptions)} entries")
        
        # Calculate statistics
        total_synsets = sum(len(synsets) for synsets in wordnet_data['synsets'].values())
        total_index_entries = sum(len(index) for index in wordnet_data['index'].values())
        
        wordnet_data['statistics'] = self._create_statistics_dict(
            total_synsets=total_synsets,
            total_index_entries=total_index_entries,
            synsets_by_pos={pos: len(synsets) for pos, synsets in wordnet_data['synsets'].items()},
            index_by_pos={pos: len(index) for pos, index in wordnet_data['index'].items()}
        )
        
        self.logger.info(f"WordNet parsing complete: {total_synsets} synsets, {total_index_entries} index entries")
        
        return wordnet_data
    
    @error_handler("parsing WordNet data file", {})
    def _parse_wordnet_data_file(self, data_file: Path) -> Dict[str, Any]:
        """
        Parse WordNet data file (e.g., data.verb).
        
        Args:
            data_file (Path): Path to WordNet data file
            
        Returns:
            dict: Parsed synset data
        """
        synsets = {}
        
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('  '):  # Skip copyright header
                    try:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            synset_info = parts[0].strip().split()
                            if len(synset_info) >= 6:
                                synset_offset = synset_info[0]
                                lex_filenum = synset_info[1]
                                ss_type = synset_info[2]
                                w_cnt = int(synset_info[3], 16)
                                
                                synset_data = {
                                    'offset': synset_offset,
                                    'lex_filenum': lex_filenum,
                                    'ss_type': ss_type,
                                    'words': [],
                                    'pointers': [],
                                    'gloss': parts[1].strip() if len(parts) > 1 else ''
                                }
                                
                                # Parse words
                                word_start = 4
                                for i in range(w_cnt):
                                    if word_start + i*2 < len(synset_info):
                                        word = synset_info[word_start + i*2]
                                        lex_id = synset_info[word_start + i*2 + 1]
                                        synset_data['words'].append({
                                            'word': word,
                                            'lex_id': lex_id
                                        })
                                
                                synsets[synset_offset] = synset_data
                                
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Skipping malformed line in {data_file}: {e}")
        
        return synsets
    
    @error_handler("parsing WordNet index file", {})
    def _parse_wordnet_index_file(self, index_file: Path) -> Dict[str, Any]:
        """
        Parse WordNet index file (e.g., index.verb).
        
        Args:
            index_file (Path): Path to WordNet index file
            
        Returns:
            dict: Parsed index data
        """
        index_data = {}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('  '):  # Skip copyright header
                    try:
                        parts = line.split()
                        if len(parts) >= 4:
                            lemma = parts[0]
                            pos = parts[1]
                            synset_cnt = int(parts[2])
                            p_cnt = int(parts[3])
                            
                            entry_data = {
                                'lemma': lemma,
                                'pos': pos,
                                'synset_cnt': synset_cnt,
                                'p_cnt': p_cnt,
                                'ptr_symbols': [],
                                'sense_cnt': 0,
                                'tagsense_cnt': 0,
                                'synset_offsets': []
                            }
                            
                            # Parse pointer symbols
                            for i in range(4, 4 + p_cnt):
                                if i < len(parts):
                                    entry_data['ptr_symbols'].append(parts[i])
                            
                            # Parse sense and tagsense counts
                            if 4 + p_cnt < len(parts):
                                entry_data['sense_cnt'] = int(parts[4 + p_cnt])
                            if 4 + p_cnt + 1 < len(parts):
                                entry_data['tagsense_cnt'] = int(parts[4 + p_cnt + 1])
                            
                            # Parse synset offsets
                            for i in range(4 + p_cnt + 2, len(parts)):
                                entry_data['synset_offsets'].append(parts[i])
                            
                            index_data[lemma] = entry_data
                            
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Skipping malformed line in {index_file}: {e}")
        
        return index_data
    
    @error_handler("parsing WordNet exception file", {})
    def _parse_wordnet_exception_file(self, exc_file: Path) -> Dict[str, List[str]]:
        """
        Parse WordNet exception file (e.g., verb.exc).
        
        Args:
            exc_file (Path): Path to WordNet exception file
            
        Returns:
            dict: Exception mappings
        """
        exceptions = {}
        
        with open(exc_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        inflected_form = parts[0]
                        base_forms = parts[1:]
                        exceptions[inflected_form] = base_forms
        
        return exceptions

    # BSO mapping methods
    
    def parse_bso_mappings(self) -> Dict[str, Any]:
        """
        Parse BSO CSV mapping files.
        
        Returns:
            dict: BSO category mappings to VerbNet classes
        """
        bso_path = self._validate_file_path('bso')
        
        bso_data = {
            'vn_to_bso': {},
            'bso_to_vn': {},
            'statistics': {}
        }
        
        # Find BSO mapping CSV files
        csv_files = list(bso_path.glob('*.csv'))
        
        for csv_file in csv_files:
            mappings = self.load_bso_mappings(csv_file)
            if mappings:  # Only process if mappings were loaded successfully
                self._process_bso_mappings(csv_file, mappings, bso_data)
                self.logger.info(f"Parsed BSO mapping file: {csv_file.name}")
        
        bso_data['statistics'] = self._create_statistics_dict(
            vn_to_bso_mappings=len(bso_data['vn_to_bso']),
            bso_categories=len(bso_data['bso_to_vn']),
            files_processed=len(csv_files)
        )
        
        # Store for later use
        self.bso_mappings = bso_data
        
        self.logger.info(f"BSO parsing complete: {len(bso_data['bso_to_vn'])} BSO categories")
        
        return bso_data
    
    def load_bso_mappings(self, csv_path: Path) -> List[Dict[str, str]]:
        """
        Load BSO (Basic Semantic Ontology) mappings from CSV.
        
        Args:
            csv_path (Path): Path to BSO mapping CSV file
            
        Returns:
            list: BSO mappings by class ID
        """
        return self._load_csv_file(csv_path)
    
    def _process_bso_mappings(self, csv_file: Path, mappings: List[Dict[str, str]], bso_data: Dict[str, Any]) -> None:
        """
        Process BSO mappings from CSV data.
        
        Args:
            csv_file (Path): CSV file being processed
            mappings (list): List of mapping dictionaries
            bso_data (dict): BSO data structure to update
        """
        if 'VNBSOMapping' in csv_file.name:
            # VerbNet to BSO mappings
            for mapping in mappings:
                vn_class = mapping.get('VN_Class', '')
                bso_category = mapping.get('BSO_Category', '')
                if vn_class and bso_category:
                    bso_data['vn_to_bso'][vn_class] = bso_category
                    
                    if bso_category not in bso_data['bso_to_vn']:
                        bso_data['bso_to_vn'][bso_category] = []
                    bso_data['bso_to_vn'][bso_category].append(vn_class)
        
        elif 'BSOVNMapping' in csv_file.name:
            # BSO to VerbNet mappings (with members)
            for mapping in mappings:
                bso_category = mapping.get('BSO_Category', '')
                vn_class = mapping.get('VN_Class', '')
                members = mapping.get('Members', '')
                
                if bso_category and vn_class:
                    if bso_category not in bso_data['bso_to_vn']:
                        bso_data['bso_to_vn'][bso_category] = []
                    
                    class_info = {
                        'class': vn_class,
                        'members': [m.strip() for m in members.split(',') if m.strip()] if members else []
                    }
                    bso_data['bso_to_vn'][bso_category].append(class_info)
    
    def apply_bso_mappings(self, verbnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply BSO mappings to VerbNet data.
        
        Args:
            verbnet_data (dict): VerbNet class data
            
        Returns:
            dict: VerbNet data with BSO mappings applied
        """
        if not self.bso_mappings or 'classes' not in verbnet_data:
            return verbnet_data
        
        # Apply BSO categories to VerbNet classes
        for class_id, class_data in verbnet_data['classes'].items():
            if class_id in self.bso_mappings.get('vn_to_bso', {}):
                class_data['bso_category'] = self.bso_mappings['vn_to_bso'][class_id]
        
        return verbnet_data

    # SemNet parsing methods
    
    def parse_semnet_data(self) -> Dict[str, Any]:
        """
        Parse SemNet JSON files for integrated semantic networks.
        
        Returns:
            dict: Parsed SemNet data for verbs and nouns
        """
        semnet_path = self._validate_file_path('semnet')
        
        semnet_data = {
            'verb_network': {},
            'noun_network': {},
            'statistics': {}
        }
        
        # Parse verb semantic network
        verb_semnet_path = semnet_path / 'verb-semnet.json'
        if verb_semnet_path.exists():
            verb_data = self._load_json_file(verb_semnet_path)
            if verb_data:
                semnet_data['verb_network'] = verb_data
                self.logger.info(f"Loaded verb semantic network: {len(verb_data)} entries")
        
        # Parse noun semantic network
        noun_semnet_path = semnet_path / 'noun-semnet.json'
        if noun_semnet_path.exists():
            noun_data = self._load_json_file(noun_semnet_path)
            if noun_data:
                semnet_data['noun_network'] = noun_data
                self.logger.info(f"Loaded noun semantic network: {len(noun_data)} entries")
        
        semnet_data['statistics'] = self._create_statistics_dict(
            verb_entries=len(semnet_data['verb_network']),
            noun_entries=len(semnet_data['noun_network'])
        )
        
        self.logger.info(f"SemNet parsing complete")
        
        return semnet_data

    # Reference documentation parsing methods
    
    def parse_reference_docs(self) -> Dict[str, Any]:
        """
        Parse reference documentation (JSON/TSV files).
        
        Returns:
            dict: Parsed reference definitions and constants
        """
        ref_path = self._validate_file_path('reference_docs')
        
        ref_data = {
            'predicates': {},
            'themroles': {},
            'constants': {},
            'verb_specific': {},
            'statistics': {}
        }
        
        # Parse predicate definitions
        pred_calc_path = ref_path / 'pred_calc_for_website_final.json'
        if pred_calc_path.exists():
            pred_data = self._load_json_file(pred_calc_path)
            if pred_data:
                ref_data['predicates'] = pred_data
                self.logger.info(f"Loaded predicate definitions: {len(pred_data)} entries")
        
        # Parse thematic role definitions
        themrole_path = ref_path / 'themrole_defs.json'
        if themrole_path.exists():
            themrole_data = self._load_json_file(themrole_path)
            if themrole_data:
                ref_data['themroles'] = themrole_data
                self.logger.info(f"Loaded thematic role definitions: {len(themrole_data)} entries")
        
        # Parse constants
        constants_path = ref_path / 'vn_constants.tsv'
        if constants_path.exists():
            constants = self._parse_tsv_file(constants_path)
            if constants:
                ref_data['constants'] = constants
                self.logger.info(f"Loaded constants: {len(constants)} entries")
        
        # Parse semantic predicates
        sem_pred_path = ref_path / 'vn_semantic_predicates.tsv'
        if sem_pred_path.exists():
            sem_predicates = self._parse_tsv_file(sem_pred_path)
            if sem_predicates:
                ref_data['semantic_predicates'] = sem_predicates
                self.logger.info(f"Loaded semantic predicates: {len(sem_predicates)} entries")
        
        # Parse verb-specific predicates
        vs_pred_path = ref_path / 'vn_verb_specific_predicates.tsv'
        if vs_pred_path.exists():
            vs_predicates = self._parse_tsv_file(vs_pred_path)
            if vs_predicates:
                ref_data['verb_specific'] = vs_predicates
                self.logger.info(f"Loaded verb-specific predicates: {len(vs_predicates)} entries")
        
        ref_data['statistics'] = self._create_statistics_dict(
            predicates=len(ref_data.get('predicates', {})),
            themroles=len(ref_data.get('themroles', {})),
            constants=len(ref_data.get('constants', {})),
            verb_specific=len(ref_data.get('verb_specific', {}))
        )
        
        self.logger.info(f"Reference docs parsing complete")
        
        return ref_data
    
    def _parse_tsv_file(self, tsv_path: Path) -> Dict[str, Any]:
        """
        Parse a TSV (Tab-Separated Values) file.
        
        Args:
            tsv_path (Path): Path to TSV file
            
        Returns:
            dict: Parsed TSV data
        """
        rows = self._load_csv_file(tsv_path, delimiter='\t')
        data = {}
        
        for i, row in enumerate(rows):
            # Use first column as key, or row index if no clear key
            key = next(iter(row.values())) if row else str(i)
            data[key] = row
        
        return data

    # VN API parsing methods
    
    def parse_vn_api_files(self) -> Dict[str, Any]:
        """
        Parse VN API enhanced XML files.
        
        Returns:
            dict: Parsed VN API data with enhanced features
        """
        try:
            # VN API might be the same as VerbNet in some configurations
            vn_api_path = self._validate_file_path('vn_api')
        except FileNotFoundError:
            if 'verbnet' in self.corpus_paths:
                self.logger.info("Using VerbNet path for VN API data")
                return self._enhance_api_data(self.parse_verbnet_files())
            else:
                raise FileNotFoundError("VN API corpus path not configured")
        
        # For now, use same parser as VerbNet but with API enhancements
        # This could be extended to handle API-specific features
        api_data = self.parse_verbnet_files()
        
        return self._enhance_api_data(api_data)
    
    def _enhance_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add API-specific enhancements to VerbNet data.
        
        Args:
            api_data (dict): Base VerbNet data
            
        Returns:
            dict: Enhanced API data
        """
        # Add API-specific metadata
        api_data['api_version'] = '1.0'
        api_data['enhanced_features'] = True
        
        return api_data