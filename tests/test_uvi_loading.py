#!/usr/bin/env python3
"""
Unit tests for UVI (Unified Verb Index) loading functionality.

This module contains unit tests for the UVI class, focusing on corpus loading,
path detection, and basic functionality using mocks to avoid file system dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
import os

# Add src directory to path for importing UVI
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.UVI import UVI


class TestUVIInitialization(unittest.TestCase):
    """Test UVI class initialization and basic functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_corpora_path = "test_corpora"
        self.expected_corpora = [
            'verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet',
            'bso', 'semnet', 'reference_docs', 'vn_api'
        ]

    @patch('uvi.UVI.Path')
    def test_init_without_loading(self, mock_path):
        """Test UVI initialization without loading corpora."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.__str__ = MagicMock(return_value=self.test_corpora_path)
        mock_path.return_value = mock_path_instance
        
        # Mock corpus directory detection
        with patch.object(UVI, '_setup_corpus_paths') as mock_setup:
            with patch.object(UVI, '_load_all_corpora') as mock_load_all:
                uvi = UVI(corpora_path=self.test_corpora_path, load_all=False)
                
                # Verify initialization
                self.assertFalse(uvi.load_all)
                self.assertEqual(uvi.supported_corpora, self.expected_corpora)
                self.assertIsInstance(uvi.corpora_data, dict)
                self.assertIsInstance(uvi.corpus_paths, dict)
                self.assertIsInstance(uvi.loaded_corpora, set)
                
                # Verify setup was called but load_all was not
                mock_setup.assert_called_once()
                mock_load_all.assert_not_called()

    @patch('uvi.UVI.Path')
    def test_init_with_loading(self, mock_path):
        """Test UVI initialization with corpus loading."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        # Mock corpus directory detection and loading
        with patch.object(UVI, '_setup_corpus_paths') as mock_setup:
            with patch.object(UVI, '_load_all_corpora') as mock_load_all:
                uvi = UVI(corpora_path=self.test_corpora_path, load_all=True)
                
                # Verify both setup and load_all were called
                mock_setup.assert_called_once()
                mock_load_all.assert_called_once()

    @patch('uvi.UVI.Path')
    def test_init_with_nonexistent_path(self, mock_path):
        """Test UVI initialization with non-existent corpora path."""
        # Mock path non-existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            UVI(corpora_path=self.test_corpora_path, load_all=False)


class TestUVICorpusPathSetup(unittest.TestCase):
    """Test corpus path detection and setup."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_corpora_path = Path("test_corpora")

    def test_setup_corpus_paths_success(self):
        """Test successful corpus path detection."""
        with patch('uvi.UVI.Path') as mock_path_class:
            # Mock the main corpora path
            mock_main_path = MagicMock()
            mock_main_path.exists.return_value = True
            mock_path_class.return_value = mock_main_path
            
            # Mock individual corpus paths
            mock_verbnet_path = MagicMock()
            mock_verbnet_path.exists.return_value = True
            mock_framenet_path = MagicMock()
            mock_framenet_path.exists.return_value = True
            
            # Set up path division behavior
            mock_main_path.__truediv__ = MagicMock(side_effect=lambda x: {
                'verbnet': mock_verbnet_path,
                'framenet': mock_framenet_path,
                'verbnet3.4': Mock(exists=lambda: False),
                'vn': Mock(exists=lambda: False),
                'fn': Mock(exists=lambda: False),
                'framenet1.7': Mock(exists=lambda: False),
            }.get(x, Mock(exists=lambda: False)))
            
            uvi = UVI.__new__(UVI)  # Create instance without calling __init__
            uvi.corpora_path = mock_main_path
            uvi.corpus_paths = {}
            
            # Test path setup
            uvi._setup_corpus_paths()
            
            # Verify detected paths
            self.assertIn('verbnet', uvi.corpus_paths)
            self.assertIn('framenet', uvi.corpus_paths)

    @patch('builtins.print')  # Mock print to suppress warnings
    def test_setup_corpus_paths_missing_corpus(self, mock_print):
        """Test corpus path setup with missing corpus."""
        with patch('uvi.UVI.Path') as mock_path_class:
            # Mock the main corpora path
            mock_main_path = MagicMock()
            mock_main_path.exists.return_value = True
            mock_path_class.return_value = mock_main_path
            
            # All corpus subdirectories don't exist
            mock_main_path.__truediv__ = MagicMock(return_value=Mock(exists=lambda: False))
            
            uvi = UVI.__new__(UVI)  # Create instance without calling __init__
            uvi.corpora_path = mock_main_path
            uvi.corpus_paths = {}
            
            # Test path setup
            uvi._setup_corpus_paths()
            
            # Verify no paths were detected
            self.assertEqual(len(uvi.corpus_paths), 0)
            
            # Verify warning messages were printed
            self.assertTrue(mock_print.called)


class TestUVICorpusLoading(unittest.TestCase):
    """Test corpus loading functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.uvi = UVI.__new__(UVI)  # Create instance without calling __init__
        self.uvi.corpora_data = {}
        self.uvi.loaded_corpora = set()
        self.uvi.corpus_paths = {'verbnet': Path('test_verbnet')}
        self.uvi.supported_corpora = ['verbnet', 'framenet']

    @patch('builtins.print')  # Mock print to suppress error messages
    def test_load_all_corpora_success(self, mock_print):
        """Test loading all available corpora."""
        with patch.object(self.uvi, '_load_corpus') as mock_load:
            self.uvi._load_all_corpora()
            
            # Should attempt to load only corpora with paths
            mock_load.assert_called_once_with('verbnet')

    @patch('builtins.print')
    def test_load_all_corpora_with_error(self, mock_print):
        """Test loading corpora with error handling."""
        with patch.object(self.uvi, '_load_corpus', side_effect=Exception("Test error")):
            # Should not raise exception, but print error
            self.uvi._load_all_corpora()
            
            # Verify error was printed
            mock_print.assert_called()

    @patch('pathlib.Path.exists')
    def test_load_corpus_verbnet(self, mock_exists):
        """Test loading VerbNet corpus."""
        # Mock path existence
        mock_exists.return_value = True
        
        with patch.object(self.uvi, '_load_verbnet') as mock_load_vn:
            self.uvi._load_corpus('verbnet')
            
            # Verify VerbNet loader was called and corpus marked as loaded
            mock_load_vn.assert_called_once_with(Path('test_verbnet'))
            self.assertIn('verbnet', self.uvi.loaded_corpora)

    def test_load_corpus_missing_path(self):
        """Test loading corpus with missing path."""
        with self.assertRaises(FileNotFoundError):
            self.uvi._load_corpus('framenet')  # Not in corpus_paths


class TestUVIVerbNetParsing(unittest.TestCase):
    """Test VerbNet XML parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.uvi = UVI.__new__(UVI)
        self.uvi.corpora_data = {}
        self.uvi.loaded_corpora = set()
        
        # Sample VerbNet XML content
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="test-1.0">
            <MEMBERS>
                <MEMBER name="test" wn="test.v.01" grouping="test.01"/>
                <MEMBER name="example" wn="example.v.01" grouping="example.01"/>
            </MEMBERS>
            <THEMROLES>
                <THEMROLE type="Agent">
                    <SELRESTRS>
                        <SELRESTR Value="+" type="animate"/>
                    </SELRESTRS>
                </THEMROLE>
            </THEMROLES>
            <FRAMES>
                <FRAME primary="Basic" secondary="test">
                    <DESCRIPTION descriptionNumber="1.0"/>
                    <EXAMPLES>
                        <EXAMPLE>Test example sentence.</EXAMPLE>
                    </EXAMPLES>
                    <SYNTAX>
                        <NP value="Agent">
                            <SYNRESTRS>
                                <SYNRESTR Value="+" type="np"/>
                            </SYNRESTRS>
                        </NP>
                    </SYNTAX>
                    <SEMANTICS>
                        <PRED value="test">
                            <ARG type="Event" value="E"/>
                            <ARG type="ThemRole" value="Agent"/>
                        </PRED>
                    </SEMANTICS>
                </FRAME>
            </FRAMES>
        </VNCLASS>'''

    @patch('uvi.UVI.ET.parse')
    @patch('pathlib.Path.glob')
    @patch('builtins.print')
    def test_load_verbnet_success(self, mock_print, mock_glob, mock_parse):
        """Test successful VerbNet loading and parsing."""
        # Mock file discovery
        mock_xml_file = MagicMock()
        mock_xml_file.__str__ = lambda x: "test.xml"
        mock_glob.return_value = [mock_xml_file]
        
        # Mock XML parsing
        mock_tree = MagicMock()
        mock_root = ET.fromstring(self.sample_xml)
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree
        
        # Test VerbNet loading
        test_path = Path('test_verbnet')
        self.uvi._load_verbnet(test_path)
        
        # Verify data structure was created
        self.assertIn('verbnet', self.uvi.corpora_data)
        verbnet_data = self.uvi.corpora_data['verbnet']
        self.assertIn('classes', verbnet_data)
        self.assertIn('test-1.0', verbnet_data['classes'])
        
        # Verify class data structure
        test_class = verbnet_data['classes']['test-1.0']
        self.assertEqual(test_class['id'], 'test-1.0')
        self.assertEqual(len(test_class['members']), 2)
        self.assertEqual(len(test_class['themroles']), 1)
        self.assertEqual(len(test_class['frames']), 1)

    def test_parse_verbnet_class(self):
        """Test VerbNet class parsing."""
        root = ET.fromstring(self.sample_xml)
        
        class_data = self.uvi._parse_verbnet_class(root)
        
        # Verify basic class information
        self.assertEqual(class_data['id'], 'test-1.0')
        
        # Verify members
        self.assertEqual(len(class_data['members']), 2)
        self.assertEqual(class_data['members'][0]['name'], 'test')
        self.assertEqual(class_data['members'][1]['name'], 'example')
        
        # Verify thematic roles
        self.assertEqual(len(class_data['themroles']), 1)
        self.assertEqual(class_data['themroles'][0]['type'], 'Agent')
        self.assertEqual(len(class_data['themroles'][0]['selrestrs']), 1)
        
        # Verify frames
        self.assertEqual(len(class_data['frames']), 1)
        frame = class_data['frames'][0]
        self.assertEqual(frame['description']['primary'], 'Basic')
        self.assertEqual(len(frame['examples']), 1)
        self.assertEqual(len(frame['syntax']), 1)
        self.assertEqual(len(frame['semantics']), 1)

    @patch('pathlib.Path.glob')
    @patch('builtins.print')
    def test_load_verbnet_no_files(self, mock_print, mock_glob):
        """Test VerbNet loading with no XML files found."""
        # Mock no files found
        mock_glob.return_value = []
        
        test_path = Path('test_verbnet')
        self.uvi._load_verbnet(test_path)
        
        # Verify empty data structure was created
        self.assertIn('verbnet', self.uvi.corpora_data)
        verbnet_data = self.uvi.corpora_data['verbnet']
        self.assertEqual(len(verbnet_data['classes']), 0)


class TestUVIUtilityMethods(unittest.TestCase):
    """Test UVI utility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.uvi = UVI.__new__(UVI)
        self.uvi.loaded_corpora = {'verbnet', 'framenet'}
        self.uvi.supported_corpora = ['verbnet', 'framenet', 'propbank']
        self.uvi.corpus_paths = {
            'verbnet': Path('test_verbnet'),
            'framenet': Path('test_framenet')
        }
        self.uvi.corpora_data = {
            'verbnet': {'classes': {}},
            'framenet': {'frames': {}}
        }

    def test_get_loaded_corpora(self):
        """Test getting list of loaded corpora."""
        loaded = self.uvi.get_loaded_corpora()
        
        self.assertIsInstance(loaded, list)
        self.assertEqual(set(loaded), {'verbnet', 'framenet'})

    def test_is_corpus_loaded(self):
        """Test checking if corpus is loaded."""
        self.assertTrue(self.uvi.is_corpus_loaded('verbnet'))
        self.assertTrue(self.uvi.is_corpus_loaded('framenet'))
        self.assertFalse(self.uvi.is_corpus_loaded('propbank'))

    def test_get_corpus_info(self):
        """Test getting corpus information."""
        info = self.uvi.get_corpus_info()
        
        self.assertIsInstance(info, dict)
        
        # Check VerbNet info
        vn_info = info['verbnet']
        self.assertTrue(vn_info['loaded'])
        self.assertTrue(vn_info['data_available'])
        self.assertEqual(vn_info['path'], str(Path('test_verbnet')))
        
        # Check PropBank info (not loaded)
        pb_info = info['propbank']
        self.assertFalse(pb_info['loaded'])
        self.assertFalse(pb_info['data_available'])
        self.assertEqual(pb_info['path'], 'Not found')


class TestUVIPackageLevel(unittest.TestCase):
    """Test package-level functionality."""

    def test_package_imports(self):
        """Test package can be imported correctly."""
        try:
            import uvi
            from uvi import UVI
            
            # Test package metadata
            self.assertTrue(hasattr(uvi, 'get_version'))
            self.assertTrue(hasattr(uvi, 'get_supported_corpora'))
            
            # Test version and supported corpora
            version = uvi.get_version()
            corpora = uvi.get_supported_corpora()
            
            self.assertIsInstance(version, str)
            self.assertIsInstance(corpora, list)
            self.assertEqual(len(corpora), 9)  # All 9 supported corpora
            
        except ImportError as e:
            self.fail(f"Package import failed: {e}")


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestUVIInitialization,
        TestUVICorpusPathSetup,
        TestUVICorpusLoading,
        TestUVIVerbNetParsing,
        TestUVIUtilityMethods,
        TestUVIPackageLevel
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)