"""
Unit Tests for UVI Utility Modules

Comprehensive test suite for utility modules in the UVI package covering:
- Schema validation utilities
- Cross-corpus reference management
- File system utilities
- Error handling and edge cases
"""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import tempfile
import shutil
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any

import sys
import os
# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.utils.validation import SchemaValidator, validate_xml_against_dtd, validate_xml_against_xsd
from uvi.utils.cross_refs import CrossReferenceManager, build_cross_reference_index, validate_cross_references
from uvi.utils.file_utils import CorpusFileManager, detect_corpus_structure, safe_file_read


class TestSchemaValidator(unittest.TestCase):
    """Test schema validation utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_schema_path = Path(self.test_dir) / 'schemas'
        self.test_schema_path.mkdir()
        
        # Create sample XML for testing
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="test-1.1">
            <MEMBERS>
                <MEMBER name="test" wn="test%2:30:00"/>
            </MEMBERS>
            <THEMROLES>
                <THEMROLE type="Agent"/>
            </THEMROLES>
        </VNCLASS>"""
        
        self.xml_file_path = Path(self.test_dir) / 'test.xml'
        with open(self.xml_file_path, 'w') as f:
            f.write(self.sample_xml)
        
        # Create sample DTD
        self.sample_dtd = """<!ELEMENT VNCLASS (MEMBERS, THEMROLES)>
        <!ATTLIST VNCLASS ID CDATA #REQUIRED>
        <!ELEMENT MEMBERS (MEMBER)*>
        <!ELEMENT MEMBER EMPTY>
        <!ATTLIST MEMBER name CDATA #REQUIRED wn CDATA #IMPLIED>
        <!ELEMENT THEMROLES (THEMROLE)*>
        <!ELEMENT THEMROLE EMPTY>
        <!ATTLIST THEMROLE type CDATA #REQUIRED>"""
        
        self.dtd_file_path = self.test_schema_path / 'vn_class.dtd'
        with open(self.dtd_file_path, 'w') as f:
            f.write(self.sample_dtd)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_validator_initialization(self):
        """Test schema validator initialization."""
        validator = SchemaValidator(self.test_schema_path)
        
        self.assertEqual(validator.schema_base_path, self.test_schema_path)
        self.assertIsInstance(validator.cached_schemas, dict)
    
    def test_validator_initialization_no_path(self):
        """Test schema validator initialization without path."""
        validator = SchemaValidator()
        
        self.assertIsNone(validator.schema_base_path)
        self.assertIsInstance(validator.cached_schemas, dict)
    
    def test_validate_verbnet_xml_with_schema(self):
        """Test VerbNet XML validation with schema."""
        validator = SchemaValidator(self.test_schema_path)
        
        # Mock the schema finding and validation
        with patch.object(validator, '_find_verbnet_schema', return_value=self.dtd_file_path):
            with patch('uvi.utils.validation.validate_xml_against_dtd') as mock_validate:
                mock_validate.return_value = {'valid': True, 'errors': []}
                
                result = validator.validate_verbnet_xml(self.xml_file_path)
                
                self.assertIsInstance(result, dict)
                mock_validate.assert_called_once()
    
    def test_validate_verbnet_xml_no_schema(self):
        """Test VerbNet XML validation without schema."""
        validator = SchemaValidator()
        
        with patch.object(validator, '_find_verbnet_schema', return_value=None):
            result = validator.validate_verbnet_xml(self.xml_file_path)
            
            self.assertIsInstance(result, dict)
            self.assertIn('error', result)
    
    def test_find_verbnet_schema(self):
        """Test finding VerbNet schema files."""
        validator = SchemaValidator(self.test_schema_path)
        
        # Create various schema files
        (self.test_schema_path / 'vn_schema-3.xsd').touch()
        (self.test_schema_path / 'vn_class-3.dtd').touch()
        
        schema_file = validator._find_verbnet_schema(self.test_schema_path)
        
        self.assertIsNotNone(schema_file)
        self.assertTrue(schema_file.exists())


class TestValidationFunctions(unittest.TestCase):
    """Test standalone validation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample valid XML
        self.valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <element attribute="value">Content</element>
        </root>"""
        
        self.xml_file = Path(self.test_dir) / 'valid.xml'
        with open(self.xml_file, 'w') as f:
            f.write(self.valid_xml)
        
        # Sample invalid XML
        self.invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <unclosed>Content
        </root>"""
        
        self.invalid_xml_file = Path(self.test_dir) / 'invalid.xml'
        with open(self.invalid_xml_file, 'w') as f:
            f.write(self.invalid_xml)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_validate_xml_against_dtd_mock(self):
        """Test XML validation against DTD (mocked)."""
        # Mock lxml since it might not be available
        with patch('uvi.utils.validation.etree') as mock_etree:
            mock_etree.parse.return_value = Mock()
            mock_etree.DTD.return_value.validate.return_value = True
            mock_etree.DTD.return_value.error_log.last_error = None
            
            result = validate_xml_against_dtd(self.xml_file, Path('dummy.dtd'))
            
            self.assertIsInstance(result, dict)
            self.assertIn('valid', result)
    
    def test_validate_xml_against_dtd_no_lxml(self):
        """Test XML validation when lxml is not available."""
        with patch('uvi.utils.validation.etree', None):
            result = validate_xml_against_dtd(self.xml_file, Path('dummy.dtd'))
            
            self.assertIsInstance(result, dict)
            self.assertIn('error', result)
            self.assertIn('lxml not available', result['error'])
    
    def test_validate_xml_against_xsd_mock(self):
        """Test XML validation against XSD (mocked)."""
        with patch('uvi.utils.validation.etree') as mock_etree:
            mock_schema = Mock()
            mock_schema.validate.return_value = True
            mock_schema.error_log.last_error = None
            mock_etree.XMLSchema.return_value = mock_schema
            mock_etree.parse.return_value = Mock()
            
            result = validate_xml_against_xsd(self.xml_file, Path('dummy.xsd'))
            
            self.assertIsInstance(result, dict)
            self.assertIn('valid', result)
    
    def test_validate_xml_with_nonexistent_files(self):
        """Test validation with nonexistent files."""
        nonexistent_xml = Path(self.test_dir) / 'nonexistent.xml'
        nonexistent_schema = Path(self.test_dir) / 'nonexistent.dtd'
        
        result = validate_xml_against_dtd(nonexistent_xml, nonexistent_schema)
        
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)


class TestCrossReferenceManager(unittest.TestCase):
    """Test cross-corpus reference management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample corpus data for cross-references
        self.verbnet_data = {
            'classes': {
                'run-51.3.2': {
                    'id': 'run-51.3.2',
                    'members': [{'name': 'run', 'wn': 'run%2:38:00'}]
                }
            }
        }
        
        self.propbank_data = {
            'predicates': {
                'run': {
                    'lemma': 'run',
                    'rolesets': [{'id': 'run.01', 'vncls': '51.3.2'}]
                }
            }
        }
        
        self.framenet_data = {
            'frames': {
                'Self_motion': {
                    'name': 'Self_motion',
                    'lexical_units': {'run': {'name': 'run'}}
                }
            }
        }
        
        self.corpora_data = {
            'verbnet': self.verbnet_data,
            'propbank': self.propbank_data,
            'framenet': self.framenet_data
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_cross_reference_manager_initialization(self):
        """Test cross-reference manager initialization."""
        manager = CrossReferenceManager(self.corpora_data)
        
        self.assertEqual(manager.corpora_data, self.corpora_data)
        self.assertIsInstance(manager.cross_ref_index, dict)
    
    def test_build_cross_reference_index(self):
        """Test building cross-reference index."""
        manager = CrossReferenceManager(self.corpora_data)
        index = manager.build_cross_reference_index()
        
        self.assertIsInstance(index, dict)
        # Should have some cross-references
        self.assertGreater(len(index), 0)
    
    def test_find_cross_references(self):
        """Test finding cross-references for an entry."""
        manager = CrossReferenceManager(self.corpora_data)
        
        cross_refs = manager.find_cross_references('run-51.3.2', 'verbnet')
        
        self.assertIsInstance(cross_refs, list)
        # May be empty depending on implementation, but should return a list
    
    def test_validate_cross_reference(self):
        """Test validating a cross-reference."""
        manager = CrossReferenceManager(self.corpora_data)
        
        result = manager.validate_cross_reference('run-51.3.2', 'verbnet', 'run.01', 'propbank')
        
        self.assertIsInstance(result, dict)
        self.assertIn('valid', result)
    
    def test_get_mapping_confidence(self):
        """Test getting mapping confidence score."""
        manager = CrossReferenceManager(self.corpora_data)
        
        confidence = manager.get_mapping_confidence('run-51.3.2', 'verbnet', 'run.01', 'propbank')
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


class TestCrossReferenceBuilding(unittest.TestCase):
    """Test cross-reference building functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = {
            'verbnet': {
                'classes': {
                    'run-51.3.2': {'id': 'run-51.3.2', 'members': [{'name': 'run'}]}
                }
            },
            'propbank': {
                'predicates': {
                    'run': {'lemma': 'run', 'rolesets': [{'id': 'run.01', 'vncls': '51.3.2'}]}
                }
            }
        }
    
    def test_build_cross_reference_index_function(self):
        """Test standalone cross-reference index building function."""
        index = build_cross_reference_index(self.sample_data)
        
        self.assertIsInstance(index, dict)
        # Should contain some mappings
        self.assertIn('verbnet_to_propbank', index)
        self.assertIn('propbank_to_verbnet', index)
    
    def test_validate_cross_references_function(self):
        """Test standalone cross-reference validation function."""
        index = build_cross_reference_index(self.sample_data)
        validation_results = validate_cross_references(index, self.sample_data)
        
        self.assertIsInstance(validation_results, dict)
        self.assertIn('total_mappings', validation_results)
        self.assertIn('valid_mappings', validation_results)
        self.assertIn('invalid_mappings', validation_results)


class TestCorpusFileManager(unittest.TestCase):
    """Test corpus file management utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.corpus_path = Path(self.test_dir) / 'corpora'
        self.corpus_path.mkdir()
        
        # Create mock corpus structure
        (self.corpus_path / 'verbnet').mkdir()
        (self.corpus_path / 'verbnet' / 'test.xml').touch()
        (self.corpus_path / 'framenet').mkdir()
        (self.corpus_path / 'framenet' / 'frame').mkdir()
        (self.corpus_path / 'framenet' / 'frame' / 'Test.xml').touch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_file_manager_initialization(self):
        """Test file manager initialization."""
        manager = CorpusFileManager(self.corpus_path)
        
        self.assertEqual(manager.base_path, self.corpus_path)
        self.assertIsInstance(manager.corpus_paths, dict)
    
    def test_detect_corpus_files(self):
        """Test detecting corpus files."""
        manager = CorpusFileManager(self.corpus_path)
        
        verbnet_files = manager.detect_corpus_files('verbnet', '*.xml')
        self.assertIsInstance(verbnet_files, list)
        self.assertGreater(len(verbnet_files), 0)
        
        framenet_files = manager.detect_corpus_files('framenet', '**/*.xml')
        self.assertIsInstance(framenet_files, list)
        self.assertGreater(len(framenet_files), 0)
    
    def test_get_corpus_statistics(self):
        """Test getting corpus file statistics."""
        manager = CorpusFileManager(self.corpus_path)
        
        stats = manager.get_corpus_statistics('verbnet')
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_files', stats)
        self.assertIn('xml_files', stats)
        self.assertIn('total_size', stats)
    
    def test_validate_corpus_structure(self):
        """Test validating corpus directory structure."""
        manager = CorpusFileManager(self.corpus_path)
        
        is_valid = manager.validate_corpus_structure('verbnet', ['*.xml'])
        self.assertTrue(is_valid)
        
        is_valid = manager.validate_corpus_structure('verbnet', ['*.json'])
        self.assertFalse(is_valid)  # No JSON files in verbnet
    
    def test_safe_file_read_function(self):
        """Test safe file reading function."""
        # Create test file with content
        test_file = Path(self.test_dir) / 'test.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Test content\nLine 2')
        
        # Test successful read
        content = safe_file_read(test_file)
        self.assertIsInstance(content, str)
        self.assertIn('Test content', content)
        
        # Test reading nonexistent file
        nonexistent = Path(self.test_dir) / 'nonexistent.txt'
        content = safe_file_read(nonexistent)
        self.assertIsNone(content)
    
    def test_safe_file_read_with_encoding_error(self):
        """Test safe file reading with encoding errors."""
        # Create file with binary content
        test_file = Path(self.test_dir) / 'binary.txt'
        with open(test_file, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        
        # Should handle encoding errors gracefully
        content = safe_file_read(test_file, encoding='utf-8')
        self.assertIsNone(content)


class TestDetectCorpusStructure(unittest.TestCase):
    """Test corpus structure detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.corpus_path = Path(self.test_dir) / 'corpora'
        self.corpus_path.mkdir()
        
        # Create various corpus structures
        verbnet_dir = self.corpus_path / 'verbnet'
        verbnet_dir.mkdir()
        (verbnet_dir / 'class1.xml').touch()
        (verbnet_dir / 'class2.xml').touch()
        (verbnet_dir / 'vn_schema-3.xsd').touch()
        
        framenet_dir = self.corpus_path / 'framenet'
        framenet_dir.mkdir()
        (framenet_dir / 'frameIndex.xml').touch()
        frame_subdir = framenet_dir / 'frame'
        frame_subdir.mkdir()
        (frame_subdir / 'Frame1.xml').touch()
        
        wordnet_dir = self.corpus_path / 'wordnet'
        wordnet_dir.mkdir()
        (wordnet_dir / 'data.verb').touch()
        (wordnet_dir / 'index.verb').touch()
        (wordnet_dir / 'verb.exc').touch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_corpus_structure(self):
        """Test corpus structure detection function."""
        structure = detect_corpus_structure(self.corpus_path)
        
        self.assertIsInstance(structure, dict)
        
        # Should detect VerbNet
        self.assertIn('verbnet', structure)
        self.assertIn('xml_files', structure['verbnet'])
        self.assertIn('schema_files', structure['verbnet'])
        
        # Should detect FrameNet
        self.assertIn('framenet', structure)
        self.assertIn('xml_files', structure['framenet'])
        
        # Should detect WordNet
        self.assertIn('wordnet', structure)
        self.assertIn('data_files', structure['wordnet'])
        self.assertIn('index_files', structure['wordnet'])
    
    def test_detect_corpus_structure_empty(self):
        """Test corpus structure detection with empty directory."""
        empty_dir = Path(self.test_dir) / 'empty'
        empty_dir.mkdir()
        
        structure = detect_corpus_structure(empty_dir)
        
        self.assertIsInstance(structure, dict)
        self.assertEqual(len(structure), 0)
    
    def test_detect_corpus_structure_nonexistent(self):
        """Test corpus structure detection with nonexistent directory."""
        nonexistent = Path(self.test_dir) / 'nonexistent'
        
        structure = detect_corpus_structure(nonexistent)
        
        self.assertIsInstance(structure, dict)
        self.assertEqual(len(structure), 0)


class TestUtilsErrorHandling(unittest.TestCase):
    """Test error handling in utility modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_schema_validator_with_invalid_xml(self):
        """Test schema validator with invalid XML."""
        validator = SchemaValidator()
        
        # Create invalid XML file
        invalid_xml = Path(self.test_dir) / 'invalid.xml'
        with open(invalid_xml, 'w') as f:
            f.write('<unclosed><tag>')
        
        result = validator.validate_verbnet_xml(invalid_xml)
        
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
    
    def test_cross_reference_manager_with_empty_data(self):
        """Test cross-reference manager with empty data."""
        empty_data = {}
        manager = CrossReferenceManager(empty_data)
        
        index = manager.build_cross_reference_index()
        self.assertIsInstance(index, dict)
        
        cross_refs = manager.find_cross_references('nonexistent', 'verbnet')
        self.assertIsInstance(cross_refs, list)
        self.assertEqual(len(cross_refs), 0)
    
    def test_file_manager_with_nonexistent_corpus(self):
        """Test file manager with nonexistent corpus."""
        nonexistent_path = Path(self.test_dir) / 'nonexistent'
        manager = CorpusFileManager(nonexistent_path)
        
        files = manager.detect_corpus_files('verbnet', '*.xml')
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 0)
        
        stats = manager.get_corpus_statistics('verbnet')
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats.get('total_files', 0), 0)
    
    def test_safe_file_read_permission_error(self):
        """Test safe file reading with permission errors."""
        # This test is platform-specific and might not work on all systems
        test_file = Path(self.test_dir) / 'restricted.txt'
        with open(test_file, 'w') as f:
            f.write('content')
        
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            content = safe_file_read(test_file)
            self.assertIsNone(content)


class TestUtilsIntegration(unittest.TestCase):
    """Test integration between utility modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.corpus_path = Path(self.test_dir) / 'corpora'
        self.corpus_path.mkdir()
        
        # Create sample corpus data
        self.sample_data = {
            'verbnet': {
                'classes': {
                    'test-1.1': {'id': 'test-1.1', 'members': [{'name': 'test'}]}
                }
            },
            'framenet': {
                'frames': {
                    'Test_Frame': {'name': 'Test_Frame', 'lexical_units': {'test': {}}}
                }
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_file_manager_with_cross_references(self):
        """Test using file manager with cross-reference manager."""
        # Set up file manager
        file_manager = CorpusFileManager(self.corpus_path)
        
        # Set up cross-reference manager
        cross_ref_manager = CrossReferenceManager(self.sample_data)
        index = cross_ref_manager.build_cross_reference_index()
        
        # Should work together without errors
        self.assertIsInstance(index, dict)
        
        corpus_stats = file_manager.get_corpus_statistics('verbnet')
        self.assertIsInstance(corpus_stats, dict)
    
    def test_schema_validation_with_file_detection(self):
        """Test schema validation with file detection."""
        # Create schema and XML files
        (self.corpus_path / 'verbnet').mkdir()
        
        xml_content = """<?xml version="1.0"?><VNCLASS ID="test-1.1"><MEMBERS/><THEMROLES/></VNCLASS>"""
        xml_file = self.corpus_path / 'verbnet' / 'test.xml'
        with open(xml_file, 'w') as f:
            f.write(xml_content)
        
        # Use file manager to detect files
        file_manager = CorpusFileManager(self.corpus_path)
        xml_files = file_manager.detect_corpus_files('verbnet', '*.xml')
        
        self.assertGreater(len(xml_files), 0)
        
        # Use validator on detected files
        validator = SchemaValidator()
        for xml_file_path in xml_files:
            result = validator.validate_verbnet_xml(Path(xml_file_path))
            self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()