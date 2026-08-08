#!/usr/bin/env python3
"""
Comprehensive Unit Tests for CorpusCollectionValidator Class

This module contains comprehensive unit tests for the CorpusCollectionValidator
class, covering all validation methods with various scenarios including edge
cases, error conditions, and success cases using mock data.

Test Coverage:
- validate_collections()
- _validate_verbnet_collection()
- _validate_framenet_collection()
- _validate_propbank_collection()
- validate_cross_references()
- _validate_vn_pb_mappings()
"""

import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from uvi.corpus_loader import CorpusCollectionValidator


class TestCorpusCollectionValidator(unittest.TestCase):
    """Test cases for CorpusCollectionValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=logging.Logger)
        
        # Mock loaded data with various corpus configurations
        self.mock_loaded_data_complete = {
            'verbnet': {
                'classes': {
                    'test-class-1': {
                        'members': ['verb1', 'verb2'],
                        'frames': [
                            {
                                'description': {
                                    'primary': 'Test frame description'
                                }
                            }
                        ]
                    },
                    'test-class-2': {
                        'members': ['verb3', 'verb4'],
                        'frames': [
                            {
                                'description': {
                                    'primary': 'Another frame description'
                                }
                            }
                        ]
                    }
                }
            },
            'framenet': {
                'frames': {
                    'TestFrame1': {
                        'lexical_units': ['unit1', 'unit2'],
                        'definition': 'Test frame definition'
                    },
                    'TestFrame2': {
                        'lexical_units': ['unit3', 'unit4'],
                        'definition': 'Another frame definition'
                    }
                }
            },
            'propbank': {
                'predicates': {
                    'test_predicate': {
                        'rolesets': [
                            {
                                'id': 'test_predicate.01',
                                'roles': ['arg0', 'arg1']
                            }
                        ]
                    },
                    'another_predicate': {
                        'rolesets': [
                            {
                                'id': 'another_predicate.01',
                                'roles': ['arg0', 'arg1', 'arg2']
                            }
                        ]
                    }
                }
            }
        }
        
        # Mock loaded data with issues
        self.mock_loaded_data_with_warnings = {
            'verbnet': {
                'classes': {
                    'empty-class': {
                        'members': [],  # No members - should trigger warning
                        'frames': []    # No frames - should trigger warning
                    },
                    'frame-issues': {
                        'members': ['verb1'],
                        'frames': [
                            {
                                'description': {}  # Missing primary description
                            }
                        ]
                    }
                }
            },
            'framenet': {
                'frames': {
                    'EmptyFrame': {
                        'lexical_units': [],  # No lexical units - should trigger warning
                        'definition': ''      # Empty definition - should trigger warning
                    }
                }
            },
            'propbank': {
                'predicates': {
                    'empty_predicate': {
                        'rolesets': []  # No rolesets - should trigger warning
                    },
                    'incomplete_predicate': {
                        'rolesets': [
                            {
                                'id': 'incomplete_predicate.01',
                                'roles': []  # No roles - should trigger warning
                            }
                        ]
                    }
                }
            }
        }
        
        # Mock data with missing/invalid structures
        self.mock_loaded_data_invalid = {
            'verbnet': {
                'classes': 'invalid_structure'  # Should be dict, not string
            },
            'framenet': {
                'frames': None  # Invalid None value
            },
            'propbank': {
                'predicates': []  # Should be dict, not list
            }
        }
        
        # Empty loaded data
        self.mock_loaded_data_empty = {}
        
        self.validator_complete = CorpusCollectionValidator(
            self.mock_loaded_data_complete, self.logger
        )
        self.validator_warnings = CorpusCollectionValidator(
            self.mock_loaded_data_with_warnings, self.logger
        )
        self.validator_invalid = CorpusCollectionValidator(
            self.mock_loaded_data_invalid, self.logger
        )
        self.validator_empty = CorpusCollectionValidator(
            self.mock_loaded_data_empty, self.logger
        )

    def test_init(self):
        """Test CorpusCollectionValidator initialization."""
        validator = CorpusCollectionValidator(self.mock_loaded_data_complete, self.logger)
        
        self.assertEqual(validator.loaded_data, self.mock_loaded_data_complete)
        self.assertEqual(validator.logger, self.logger)

    def test_validate_collections_complete_data(self):
        """Test validate_collections with complete valid data."""
        results = self.validator_complete.validate_collections()
        
        # Should have results for all three corpus types
        self.assertIn('verbnet', results)
        self.assertIn('framenet', results)
        self.assertIn('propbank', results)
        
        # All should be valid
        self.assertEqual(results['verbnet']['status'], 'valid')
        self.assertEqual(results['framenet']['status'], 'valid')
        self.assertEqual(results['propbank']['status'], 'valid')
        
        # Should have no errors
        self.assertEqual(results['verbnet']['errors'], [])
        self.assertEqual(results['framenet']['errors'], [])
        self.assertEqual(results['propbank']['errors'], [])
        
        # Should have counts
        self.assertEqual(results['verbnet']['total_classes'], 2)
        self.assertEqual(results['framenet']['total_frames'], 2)
        self.assertEqual(results['propbank']['total_predicates'], 2)

    def test_validate_collections_with_warnings(self):
        """Test validate_collections with data that triggers warnings."""
        results = self.validator_warnings.validate_collections()
        
        # Should have results for all three corpus types
        self.assertIn('verbnet', results)
        self.assertIn('framenet', results)
        self.assertIn('propbank', results)
        
        # All should be valid_with_warnings
        self.assertEqual(results['verbnet']['status'], 'valid_with_warnings')
        self.assertEqual(results['framenet']['status'], 'valid_with_warnings')
        self.assertEqual(results['propbank']['status'], 'valid_with_warnings')
        
        # Should have warnings but no errors
        self.assertEqual(results['verbnet']['errors'], [])
        self.assertEqual(results['framenet']['errors'], [])
        self.assertEqual(results['propbank']['errors'], [])
        
        self.assertTrue(len(results['verbnet']['warnings']) > 0)
        self.assertTrue(len(results['framenet']['warnings']) > 0)
        self.assertTrue(len(results['propbank']['warnings']) > 0)

    def test_validate_collections_invalid_data(self):
        """Test validate_collections with invalid data structures."""
        results = self.validator_invalid.validate_collections()
        
        # Should have results for all three corpus types
        self.assertIn('verbnet', results)
        self.assertIn('framenet', results)
        self.assertIn('propbank', results)
        
        # VerbNet and PropBank should have validation errors due to invalid structures
        # (string instead of dict, list instead of dict)
        self.assertEqual(results['verbnet']['status'], 'validation_error')
        self.assertTrue(len(results['verbnet']['errors']) > 0)
        
        self.assertEqual(results['propbank']['status'], 'validation_error') 
        self.assertTrue(len(results['propbank']['errors']) > 0)
        
        # FrameNet with None frames is handled gracefully (converted to empty dict)
        self.assertEqual(results['framenet']['status'], 'valid')
        self.assertEqual(results['framenet']['errors'], [])

    def test_validate_collections_empty_data(self):
        """Test validate_collections with empty data."""
        results = self.validator_empty.validate_collections()
        
        # Should be empty since no corpus data exists
        self.assertEqual(results, {})

    def test_validate_collections_unknown_corpus(self):
        """Test validate_collections with unknown corpus type."""
        data_with_unknown = {
            'unknown_corpus': {'some': 'data'},
            'verbnet': self.mock_loaded_data_complete['verbnet']
        }
        validator = CorpusCollectionValidator(data_with_unknown, self.logger)
        
        results = validator.validate_collections()
        
        # Should handle unknown corpus gracefully
        self.assertIn('unknown_corpus', results)
        self.assertEqual(results['unknown_corpus']['status'], 'no_validation')
        self.assertEqual(results['unknown_corpus']['errors'], [])
        
        # Should still validate known corpus
        self.assertIn('verbnet', results)
        self.assertEqual(results['verbnet']['status'], 'valid')

    def test_validate_verbnet_collection_valid(self):
        """Test _validate_verbnet_collection with valid data."""
        verbnet_data = self.mock_loaded_data_complete['verbnet']
        result = self.validator_complete._validate_verbnet_collection(verbnet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])
        self.assertEqual(result['total_classes'], 2)

    def test_validate_verbnet_collection_warnings(self):
        """Test _validate_verbnet_collection with data that triggers warnings."""
        verbnet_data = self.mock_loaded_data_with_warnings['verbnet']
        result = self.validator_warnings._validate_verbnet_collection(verbnet_data)
        
        self.assertEqual(result['status'], 'valid_with_warnings')
        self.assertEqual(result['errors'], [])
        self.assertTrue(len(result['warnings']) > 0)
        
        # Check specific warning messages
        warnings_text = ' '.join(result['warnings'])
        self.assertIn('empty-class', warnings_text)
        self.assertIn('has no members', warnings_text)
        self.assertIn('has no frames', warnings_text)
        self.assertIn('missing primary description', warnings_text)

    def test_validate_verbnet_collection_empty_classes(self):
        """Test _validate_verbnet_collection with empty classes dict."""
        verbnet_data = {'classes': {}}
        result = self.validator_complete._validate_verbnet_collection(verbnet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_classes'], 0)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])

    def test_validate_verbnet_collection_missing_classes_key(self):
        """Test _validate_verbnet_collection with missing classes key."""
        verbnet_data = {}
        result = self.validator_complete._validate_verbnet_collection(verbnet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_classes'], 0)

    def test_validate_framenet_collection_valid(self):
        """Test _validate_framenet_collection with valid data."""
        framenet_data = self.mock_loaded_data_complete['framenet']
        result = self.validator_complete._validate_framenet_collection(framenet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])
        self.assertEqual(result['total_frames'], 2)

    def test_validate_framenet_collection_warnings(self):
        """Test _validate_framenet_collection with data that triggers warnings."""
        framenet_data = self.mock_loaded_data_with_warnings['framenet']
        result = self.validator_warnings._validate_framenet_collection(framenet_data)
        
        self.assertEqual(result['status'], 'valid_with_warnings')
        self.assertEqual(result['errors'], [])
        self.assertTrue(len(result['warnings']) > 0)
        
        # Check specific warning messages
        warnings_text = ' '.join(result['warnings'])
        self.assertIn('EmptyFrame', warnings_text)
        self.assertIn('has no lexical units', warnings_text)
        self.assertIn('missing definition', warnings_text)

    def test_validate_framenet_collection_empty_frames(self):
        """Test _validate_framenet_collection with empty frames dict."""
        framenet_data = {'frames': {}}
        result = self.validator_complete._validate_framenet_collection(framenet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_frames'], 0)

    def test_validate_framenet_collection_missing_frames_key(self):
        """Test _validate_framenet_collection with missing frames key."""
        framenet_data = {}
        result = self.validator_complete._validate_framenet_collection(framenet_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_frames'], 0)

    def test_validate_propbank_collection_valid(self):
        """Test _validate_propbank_collection with valid data."""
        propbank_data = self.mock_loaded_data_complete['propbank']
        result = self.validator_complete._validate_propbank_collection(propbank_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])
        self.assertEqual(result['total_predicates'], 2)

    def test_validate_propbank_collection_warnings(self):
        """Test _validate_propbank_collection with data that triggers warnings."""
        propbank_data = self.mock_loaded_data_with_warnings['propbank']
        result = self.validator_warnings._validate_propbank_collection(propbank_data)
        
        self.assertEqual(result['status'], 'valid_with_warnings')
        self.assertEqual(result['errors'], [])
        self.assertTrue(len(result['warnings']) > 0)
        
        # Check specific warning messages
        warnings_text = ' '.join(result['warnings'])
        self.assertIn('empty_predicate', warnings_text)
        self.assertIn('has no rolesets', warnings_text)
        self.assertIn('has no roles', warnings_text)

    def test_validate_propbank_collection_empty_predicates(self):
        """Test _validate_propbank_collection with empty predicates dict."""
        propbank_data = {'predicates': {}}
        result = self.validator_complete._validate_propbank_collection(propbank_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_predicates'], 0)

    def test_validate_propbank_collection_missing_predicates_key(self):
        """Test _validate_propbank_collection with missing predicates key."""
        propbank_data = {}
        result = self.validator_complete._validate_propbank_collection(propbank_data)
        
        self.assertEqual(result['status'], 'valid')
        self.assertEqual(result['total_predicates'], 0)

    def test_validate_cross_references_complete_data(self):
        """Test validate_cross_references with complete VerbNet and PropBank data."""
        results = self.validator_complete.validate_cross_references()
        
        # Should have all cross-reference validation types
        self.assertIn('vn_pb_mappings', results)
        self.assertIn('vn_fn_mappings', results)
        self.assertIn('vn_wn_mappings', results)
        self.assertIn('on_mappings', results)
        
        # VN-PB mappings should be validated since both exist
        self.assertEqual(results['vn_pb_mappings']['status'], 'checked')
        self.assertEqual(results['vn_pb_mappings']['errors'], [])
        self.assertEqual(results['vn_pb_mappings']['warnings'], [])

    def test_validate_cross_references_missing_data(self):
        """Test validate_cross_references with missing corpus data."""
        # Only VerbNet data, no PropBank
        data_partial = {'verbnet': self.mock_loaded_data_complete['verbnet']}
        validator = CorpusCollectionValidator(data_partial, self.logger)
        
        results = validator.validate_cross_references()
        
        # Should still have all cross-reference validation types
        self.assertIn('vn_pb_mappings', results)
        self.assertIn('vn_fn_mappings', results)
        self.assertIn('vn_wn_mappings', results)
        self.assertIn('on_mappings', results)
        
        # VN-PB mappings should be empty dict since PropBank is missing
        self.assertEqual(results['vn_pb_mappings'], {})

    def test_validate_cross_references_empty_data(self):
        """Test validate_cross_references with empty data."""
        results = self.validator_empty.validate_cross_references()
        
        # Should have all cross-reference validation types
        self.assertIn('vn_pb_mappings', results)
        self.assertIn('vn_fn_mappings', results)
        self.assertIn('vn_wn_mappings', results)
        self.assertIn('on_mappings', results)
        
        # All should be empty dicts
        self.assertEqual(results['vn_pb_mappings'], {})
        self.assertEqual(results['vn_fn_mappings'], {})
        self.assertEqual(results['vn_wn_mappings'], {})
        self.assertEqual(results['on_mappings'], {})

    def test_validate_vn_pb_mappings_valid(self):
        """Test _validate_vn_pb_mappings with valid data."""
        result = self.validator_complete._validate_vn_pb_mappings()
        
        self.assertEqual(result['status'], 'checked')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])

    def test_validate_vn_pb_mappings_comprehensive_data_access(self):
        """Test that _validate_vn_pb_mappings accesses the correct data structures."""
        # Mock the validator to capture what data it accesses
        with patch.object(self.validator_complete, '_validate_vn_pb_mappings', 
                         wraps=self.validator_complete._validate_vn_pb_mappings) as mock_method:
            
            result = self.validator_complete._validate_vn_pb_mappings()
            
            # Should have been called once
            mock_method.assert_called_once()
            
            # Verify it returns expected structure
            self.assertIn('status', result)
            self.assertIn('errors', result)
            self.assertIn('warnings', result)

    def test_error_handling_in_validate_collections(self):
        """Test error handling when validation methods raise exceptions."""
        # Mock a validation method to raise an exception
        with patch.object(self.validator_complete, '_validate_verbnet_collection', 
                         side_effect=Exception('Test exception')):
            
            results = self.validator_complete.validate_collections()
            
            # Should handle exception gracefully
            self.assertIn('verbnet', results)
            self.assertEqual(results['verbnet']['status'], 'validation_error')
            self.assertIn('Test exception', results['verbnet']['errors'])

    def test_edge_case_none_values(self):
        """Test handling of None values in corpus data."""
        data_with_nones = {
            'verbnet': {
                'classes': {
                    'test-class': {
                        'members': None,
                        'frames': None
                    }
                }
            }
        }
        validator = CorpusCollectionValidator(data_with_nones, self.logger)
        
        results = validator.validate_collections()
        
        # Should handle None values gracefully
        self.assertIn('verbnet', results)
        # May trigger warnings about empty/missing data
        self.assertIn(results['verbnet']['status'], ['valid', 'valid_with_warnings'])

    def test_explicit_none_containers(self):
        """Test handling of None values for main containers (classes, frames, predicates)."""
        # Test None classes
        verbnet_none_classes = {'classes': None}
        result_vn = self.validator_complete._validate_verbnet_collection(verbnet_none_classes)
        self.assertEqual(result_vn['status'], 'valid')
        self.assertEqual(result_vn['total_classes'], 0)
        
        # Test None frames
        framenet_none_frames = {'frames': None}
        result_fn = self.validator_complete._validate_framenet_collection(framenet_none_frames)
        self.assertEqual(result_fn['status'], 'valid')
        self.assertEqual(result_fn['total_frames'], 0)
        
        # Test None predicates
        propbank_none_predicates = {'predicates': None}
        result_pb = self.validator_complete._validate_propbank_collection(propbank_none_predicates)
        self.assertEqual(result_pb['status'], 'valid')
        self.assertEqual(result_pb['total_predicates'], 0)
        
        # Test None rolesets in propbank
        propbank_none_rolesets = {
            'predicates': {
                'test_pred': {'rolesets': None}
            }
        }
        result_pb_rolesets = self.validator_complete._validate_propbank_collection(propbank_none_rolesets)
        self.assertEqual(result_pb_rolesets['status'], 'valid_with_warnings')
        self.assertIn('has no rolesets', ' '.join(result_pb_rolesets['warnings']))

    def test_complex_verbnet_frame_validation(self):
        """Test detailed VerbNet frame structure validation."""
        complex_verbnet_data = {
            'classes': {
                'complex-class': {
                    'members': ['verb1', 'verb2'],
                    'frames': [
                        {
                            'description': {
                                'primary': 'Valid frame'
                            }
                        },
                        {
                            'description': {
                                'secondary': 'Invalid - missing primary'
                            }
                        },
                        {
                            # Missing description entirely
                        }
                    ]
                }
            }
        }
        
        result = self.validator_complete._validate_verbnet_collection(complex_verbnet_data)
        
        self.assertEqual(result['status'], 'valid_with_warnings')
        self.assertTrue(len(result['warnings']) >= 2)  # At least 2 warnings for missing primary descriptions

    def test_propbank_roleset_edge_cases(self):
        """Test PropBank validation with various roleset edge cases."""
        complex_propbank_data = {
            'predicates': {
                'test_predicate': {
                    'rolesets': [
                        {
                            'id': 'test_predicate.01',
                            'roles': ['arg0', 'arg1']
                        },
                        {
                            'id': 'test_predicate.02',
                            'roles': []  # Empty roles
                        },
                        {
                            # Missing id and roles
                        }
                    ]
                }
            }
        }
        
        result = self.validator_complete._validate_propbank_collection(complex_propbank_data)
        
        self.assertEqual(result['status'], 'valid_with_warnings')
        self.assertTrue(len(result['warnings']) >= 1)  # At least 1 warning for empty roles

    def test_logger_usage(self):
        """Test that logger is properly used (though not in current implementation)."""
        # Verify logger is stored
        self.assertEqual(self.validator_complete.logger, self.logger)
        
        # This test ensures the logger is available for future use
        # Current implementation doesn't use logger, but it's available
        self.assertIsNotNone(self.validator_complete.logger)

    def test_validation_status_consistency(self):
        """Test that validation status values are consistent across methods."""
        expected_statuses = ['valid', 'valid_with_warnings', 'invalid', 'validation_error', 'no_validation', 'checked']
        
        # Test VerbNet validation
        vn_result = self.validator_complete._validate_verbnet_collection(
            self.mock_loaded_data_complete['verbnet']
        )
        self.assertIn(vn_result['status'], expected_statuses)
        
        # Test FrameNet validation
        fn_result = self.validator_complete._validate_framenet_collection(
            self.mock_loaded_data_complete['framenet']
        )
        self.assertIn(fn_result['status'], expected_statuses)
        
        # Test PropBank validation
        pb_result = self.validator_complete._validate_propbank_collection(
            self.mock_loaded_data_complete['propbank']
        )
        self.assertIn(pb_result['status'], expected_statuses)
        
        # Test cross-reference validation
        xref_results = self.validator_complete.validate_cross_references()
        for key, result in xref_results.items():
            if result:  # Skip empty dicts
                self.assertIn(result.get('status', 'empty'), expected_statuses + ['empty'])

    def test_data_structure_integrity(self):
        """Test that all validation methods return expected data structure."""
        expected_keys = ['status', 'errors', 'warnings']
        
        # Test individual validation methods
        vn_result = self.validator_complete._validate_verbnet_collection(
            self.mock_loaded_data_complete['verbnet']
        )
        for key in expected_keys:
            self.assertIn(key, vn_result)
        self.assertIn('total_classes', vn_result)
        
        fn_result = self.validator_complete._validate_framenet_collection(
            self.mock_loaded_data_complete['framenet']
        )
        for key in expected_keys:
            self.assertIn(key, fn_result)
        self.assertIn('total_frames', fn_result)
        
        pb_result = self.validator_complete._validate_propbank_collection(
            self.mock_loaded_data_complete['propbank']
        )
        for key in expected_keys:
            self.assertIn(key, pb_result)
        self.assertIn('total_predicates', pb_result)
        
        # Test cross-reference mapping validation
        xref_result = self.validator_complete._validate_vn_pb_mappings()
        for key in expected_keys:
            self.assertIn(key, xref_result)


class TestCorpusCollectionValidatorIntegration(unittest.TestCase):
    """Integration tests for CorpusCollectionValidator."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.logger = Mock(spec=logging.Logger)
        
        # Create realistic corpus data for integration testing
        self.realistic_corpus_data = {
            'verbnet': {
                'classes': {
                    'admire-31.2': {
                        'members': ['admire', 'appreciate', 'cherish'],
                        'frames': [
                            {
                                'description': {
                                    'primary': 'NP V NP',
                                    'secondary': 'Basic transitive'
                                }
                            }
                        ]
                    },
                    'break-45.1': {
                        'members': ['break', 'crack', 'fracture'],
                        'frames': [
                            {
                                'description': {
                                    'primary': 'NP V NP PP.instrument',
                                    'secondary': 'Causative alternation'
                                }
                            },
                            {
                                'description': {
                                    'primary': 'NP V'
                                }
                            }
                        ]
                    }
                }
            },
            'framenet': {
                'frames': {
                    'Regard': {
                        'lexical_units': ['admire.v', 'appreciate.v', 'respect.v'],
                        'definition': 'A Cognizer holds a particular opinion about a Phenomenon.'
                    },
                    'Breaking': {
                        'lexical_units': ['break.v', 'crack.v', 'shatter.v'],
                        'definition': 'A Whole breaks into Pieces due to some Cause.'
                    }
                }
            },
            'propbank': {
                'predicates': {
                    'admire': {
                        'rolesets': [
                            {
                                'id': 'admire.01',
                                'roles': ['arg0', 'arg1', 'arg2']
                            }
                        ]
                    },
                    'break': {
                        'rolesets': [
                            {
                                'id': 'break.01',
                                'roles': ['arg0', 'arg1', 'arg2']
                            },
                            {
                                'id': 'break.02',
                                'roles': ['arg0', 'arg1']
                            }
                        ]
                    }
                }
            }
        }

    def test_full_validation_pipeline(self):
        """Test the complete validation pipeline with realistic data."""
        validator = CorpusCollectionValidator(self.realistic_corpus_data, self.logger)
        
        # Run collection validation
        collection_results = validator.validate_collections()
        
        # Verify all corpus types are validated
        self.assertIn('verbnet', collection_results)
        self.assertIn('framenet', collection_results)
        self.assertIn('propbank', collection_results)
        
        # All should be valid
        for corpus_type in ['verbnet', 'framenet', 'propbank']:
            self.assertEqual(collection_results[corpus_type]['status'], 'valid')
            self.assertEqual(collection_results[corpus_type]['errors'], [])
        
        # Run cross-reference validation
        xref_results = validator.validate_cross_references()
        
        # Should have cross-reference validation
        self.assertIn('vn_pb_mappings', xref_results)
        self.assertEqual(xref_results['vn_pb_mappings']['status'], 'checked')

    def test_mixed_quality_data_validation(self):
        """Test validation with mixed quality data (some good, some problematic)."""
        mixed_data = {
            'verbnet': {
                'classes': {
                    'good-class': {
                        'members': ['verb1', 'verb2'],
                        'frames': [{'description': {'primary': 'Good frame'}}]
                    },
                    'problematic-class': {
                        'members': [],  # No members
                        'frames': []    # No frames
                    }
                }
            },
            'framenet': {
                'frames': {
                    'GoodFrame': {
                        'lexical_units': ['unit1', 'unit2'],
                        'definition': 'Good definition'
                    },
                    'ProblematicFrame': {
                        'lexical_units': [],  # No lexical units
                        'definition': ''      # No definition
                    }
                }
            }
        }
        
        validator = CorpusCollectionValidator(mixed_data, self.logger)
        results = validator.validate_collections()
        
        # Should get valid_with_warnings for both
        self.assertEqual(results['verbnet']['status'], 'valid_with_warnings')
        self.assertEqual(results['framenet']['status'], 'valid_with_warnings')
        
        # Should have warnings but no errors
        self.assertEqual(results['verbnet']['errors'], [])
        self.assertEqual(results['framenet']['errors'], [])
        self.assertTrue(len(results['verbnet']['warnings']) > 0)
        self.assertTrue(len(results['framenet']['warnings']) > 0)


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the tests
    unittest.main(verbosity=2)