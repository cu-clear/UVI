"""
Schema Validation Utilities

Provides validation functionality for corpus files against their schemas
including DTD and XSD validation for XML files and JSON schema validation.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import xml.etree.ElementTree as ET
try:
    from lxml import etree
except ImportError:
    etree = None
import json


class SchemaValidator:
    """
    Utility class for validating corpus files against their schemas.
    
    Supports DTD validation, XSD validation, and JSON schema validation
    for different corpus formats.
    """
    
    def __init__(self, schema_base_path: Optional[Path] = None):
        """
        Initialize schema validator.
        
        Args:
            schema_base_path (Path): Base path for schema files
        """
        self.schema_base_path = schema_base_path
        self.cached_schemas = {}
    
    def validate_verbnet_xml(self, xml_file: Path, schema_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate VerbNet XML file against its schema.
        
        Args:
            xml_file (Path): Path to VerbNet XML file
            schema_file (Path): Path to schema file (DTD or XSD)
            
        Returns:
            dict: Validation results
        """
        if not schema_file:
            # Try to find schema file automatically
            schema_file = self._find_verbnet_schema(xml_file.parent)
        
        if not schema_file or not schema_file.exists():
            return {
                'valid': None,
                'error': 'Schema file not found',
                'warnings': []
            }
        
        if schema_file.suffix.lower() == '.dtd':
            return validate_xml_against_dtd(xml_file, schema_file)
        elif schema_file.suffix.lower() == '.xsd':
            return validate_xml_against_xsd(xml_file, schema_file)
        else:
            return {
                'valid': False,
                'error': f'Unsupported schema format: {schema_file.suffix}',
                'warnings': []
            }
    
    def validate_framenet_xml(self, xml_file: Path, schema_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate FrameNet XML file against its schema.
        
        Args:
            xml_file (Path): Path to FrameNet XML file
            schema_file (Path): Path to schema file
            
        Returns:
            dict: Validation results
        """
        if not schema_file:
            # FrameNet typically uses DTD validation
            schema_file = self._find_framenet_schema(xml_file.parent)
        
        if not schema_file or not schema_file.exists():
            return self._basic_xml_validation(xml_file)
        
        return validate_xml_against_dtd(xml_file, schema_file)
    
    def validate_propbank_xml(self, xml_file: Path, schema_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate PropBank XML file against its schema.
        
        Args:
            xml_file (Path): Path to PropBank XML file
            schema_file (Path): Path to schema file
            
        Returns:
            dict: Validation results
        """
        if not schema_file:
            schema_file = self._find_propbank_schema(xml_file.parent)
        
        if not schema_file or not schema_file.exists():
            return self._basic_xml_validation(xml_file)
        
        if schema_file.suffix.lower() == '.dtd':
            return validate_xml_against_dtd(xml_file, schema_file)
        elif schema_file.suffix.lower() == '.xsd':
            return validate_xml_against_xsd(xml_file, schema_file)
        else:
            return self._basic_xml_validation(xml_file)
    
    def validate_ontonotes_xml(self, xml_file: Path) -> Dict[str, Any]:
        """
        Validate OntoNotes XML file (basic validation).
        
        Args:
            xml_file (Path): Path to OntoNotes XML file
            
        Returns:
            dict: Validation results
        """
        return self._basic_xml_validation(xml_file)
    
    def validate_json_file(self, json_file: Path, schema_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate JSON file against schema.
        
        Args:
            json_file (Path): Path to JSON file
            schema_file (Path): Path to JSON schema file
            
        Returns:
            dict: Validation results
        """
        try:
            # Basic JSON syntax validation
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not schema_file or not schema_file.exists():
                return {
                    'valid': True,
                    'error': None,
                    'warnings': ['No schema file provided - only syntax validation performed']
                }
            
            # TODO: Implement JSON schema validation if needed
            return {
                'valid': True,
                'error': None,
                'warnings': ['JSON schema validation not implemented']
            }
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'error': f'JSON syntax error: {e}',
                'warnings': []
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating JSON file: {e}',
                'warnings': []
            }
    
    def _basic_xml_validation(self, xml_file: Path) -> Dict[str, Any]:
        """
        Perform basic XML well-formedness validation.
        
        Args:
            xml_file (Path): Path to XML file
            
        Returns:
            dict: Validation results
        """
        try:
            ET.parse(xml_file)
            return {
                'valid': True,
                'error': None,
                'warnings': ['No schema validation - only well-formedness checked']
            }
        except ET.ParseError as e:
            return {
                'valid': False,
                'error': f'XML parse error: {e}',
                'warnings': []
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating XML file: {e}',
                'warnings': []
            }
    
    def _find_verbnet_schema(self, corpus_dir: Path) -> Optional[Path]:
        """Find VerbNet schema file in corpus directory."""
        # Common VerbNet schema file names
        schema_names = ['vn_schema-3.xsd', 'vn_class-3.dtd', 'verbnet.xsd', 'verbnet.dtd']
        
        for schema_name in schema_names:
            schema_path = corpus_dir / schema_name
            if schema_path.exists():
                return schema_path
        
        return None
    
    def _find_framenet_schema(self, corpus_dir: Path) -> Optional[Path]:
        """Find FrameNet schema file in corpus directory."""
        # Look for FrameNet DTD files
        dtd_files = list(corpus_dir.glob('*.dtd'))
        if dtd_files:
            return dtd_files[0]
        
        return None
    
    def _find_propbank_schema(self, corpus_dir: Path) -> Optional[Path]:
        """Find PropBank schema file in corpus directory."""
        # Look for PropBank schema files
        schema_files = list(corpus_dir.glob('*.dtd')) + list(corpus_dir.glob('*.xsd'))
        if schema_files:
            return schema_files[0]
        
        return None


def validate_xml_against_dtd(xml_file: Path, dtd_file: Path) -> Dict[str, Any]:
    """
    Validate XML file against DTD schema.
    
    Args:
        xml_file (Path): Path to XML file
        dtd_file (Path): Path to DTD file
        
    Returns:
        dict: Validation results
    """
    if etree is None:
        return {
            'valid': None,
            'error': 'lxml not available for DTD validation',
            'warnings': []
        }
        
    try:
        # Parse DTD
        with open(dtd_file, 'r', encoding='utf-8') as dtd_f:
            dtd = etree.DTD(dtd_f)
        
        # Parse XML
        with open(xml_file, 'r', encoding='utf-8') as xml_f:
            xml_doc = etree.parse(xml_f)
        
        # Validate
        is_valid = dtd.validate(xml_doc)
        error = None
        
        if not is_valid:
            error_list = [str(error) for error in dtd.error_log]
            error = '; '.join(error_list) if error_list else 'Validation failed'
        
        return {
            'valid': is_valid,
            'error': error,
            'warnings': []
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'DTD validation error: {e}',
            'warnings': []
        }


def validate_xml_against_xsd(xml_file: Path, xsd_file: Path) -> Dict[str, Any]:
    """
    Validate XML file against XSD schema.
    
    Args:
        xml_file (Path): Path to XML file
        xsd_file (Path): Path to XSD file
        
    Returns:
        dict: Validation results
    """
    if etree is None:
        return {
            'valid': None,
            'error': 'lxml library not available for XSD validation',
            'warnings': []
        }
        
    try:
        # Parse XSD
        with open(xsd_file, 'r', encoding='utf-8') as xsd_f:
            schema_doc = etree.parse(xsd_f)
            schema = etree.XMLSchema(schema_doc)
        
        # Parse XML
        with open(xml_file, 'r', encoding='utf-8') as xml_f:
            xml_doc = etree.parse(xml_f)
        
        # Validate
        is_valid = schema.validate(xml_doc)
        error = None
        
        if not is_valid:
            error_list = [str(error) for error in schema.error_log]
            error = '; '.join(error_list) if error_list else 'Validation failed'
        
        return {
            'valid': is_valid,
            'error': error,
            'warnings': []
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'XSD validation error: {e}',
            'warnings': []
        }


def validate_corpus_files(corpus_path: Path, corpus_type: str) -> Dict[str, Any]:
    """
    Validate all files in a corpus directory.
    
    Args:
        corpus_path (Path): Path to corpus directory
        corpus_type (str): Type of corpus (verbnet, framenet, etc.)
        
    Returns:
        dict: Validation results for all files
    """
    validator = SchemaValidator()
    results = {
        'corpus_type': corpus_type,
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'file_results': {}
    }
    
    if not corpus_path.exists():
        results['errors'] = [f'Corpus directory not found: {corpus_path}']
        return results
    
    # Find files to validate based on corpus type
    if corpus_type == 'verbnet':
        files_to_validate = list(corpus_path.glob('*.xml'))
    elif corpus_type == 'framenet':
        files_to_validate = list((corpus_path / 'frame').glob('*.xml')) if (corpus_path / 'frame').exists() else []
    elif corpus_type == 'propbank':
        files_to_validate = list(corpus_path.glob('**/*.xml'))
    elif corpus_type == 'ontonotes':
        files_to_validate = list(corpus_path.glob('**/*.xml'))
    elif corpus_type in ['semnet', 'reference_docs']:
        files_to_validate = list(corpus_path.glob('*.json'))
    else:
        files_to_validate = []
    
    results['total_files'] = len(files_to_validate)
    
    for file_path in files_to_validate:
        try:
            if corpus_type == 'verbnet':
                file_result = validator.validate_verbnet_xml(file_path)
            elif corpus_type == 'framenet':
                file_result = validator.validate_framenet_xml(file_path)
            elif corpus_type == 'propbank':
                file_result = validator.validate_propbank_xml(file_path)
            elif corpus_type == 'ontonotes':
                file_result = validator.validate_ontonotes_xml(file_path)
            elif corpus_type in ['semnet', 'reference_docs']:
                file_result = validator.validate_json_file(file_path)
            else:
                file_result = {'valid': None, 'error': 'Unknown corpus type', 'warnings': []}
            
            results['file_results'][str(file_path)] = file_result
            
            if file_result.get('valid') is True:
                results['valid_files'] += 1
            elif file_result.get('valid') is False:
                results['invalid_files'] += 1
                
        except Exception as e:
            results['file_results'][str(file_path)] = {
                'valid': False,
                'error': f'Validation error: {e}',
                'warnings': []
            }
            results['invalid_files'] += 1
    
    return results