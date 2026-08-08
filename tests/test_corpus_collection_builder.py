"""
Comprehensive unit tests for the CorpusCollectionBuilder class.

This test suite covers all key methods of the CorpusCollectionBuilder class
with mock data and various error handling scenarios.
"""

import unittest
from unittest.mock import Mock, patch
import logging
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from uvi.corpus_loader import CorpusCollectionBuilder


class TestCorpusCollectionBuilder(unittest.TestCase):
    """Test suite for CorpusCollectionBuilder class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = Mock(spec=logging.Logger)
        
        # Mock loaded data with comprehensive test data
        self.mock_loaded_data = {
            'reference_docs': {
                'predicates': {
                    'cause': {'description': 'Causation predicate'},
                    'motion': {'description': 'Motion predicate'},
                    'location': {'description': 'Location predicate'}
                },
                'themroles': {
                    'Agent': {'description': 'Entity that performs action'},
                    'Theme': {'description': 'Entity that undergoes action'},
                    'Location': {'description': 'Where action takes place'}
                },
                'verb_specific': {
                    'feature1': {'description': 'Test feature 1'},
                    'feature2': {'description': 'Test feature 2'}
                }
            },
            'verbnet': {
                'classes': {
                    'class-1': {
                        'frames': [
                            {
                                'syntax': [[
                                    {'synrestrs': [
                                        {'Value': 'np'},
                                        {'Value': 'pp'}
                                    ]}
                                ]],
                                'semantics': [[
                                    {'value': 'motion_verb'},
                                    {'value': 'caused_motion'}
                                ]]
                            }
                        ],
                        'themroles': [
                            {
                                'selrestrs': [
                                    {'Value': 'animate'},
                                    {'Value': 'concrete'}
                                ]
                            }
                        ]
                    },
                    'class-2': {
                        'frames': [
                            {
                                'syntax': [[
                                    {'synrestrs': [
                                        {'Value': 'vp'},
                                        {'Value': 'adj'}
                                    ]}
                                ]],
                                'semantics': [[
                                    {'value': 'state_verb'},
                                    {'value': 'mental_state'}
                                ]]
                            }
                        ],
                        'themroles': [
                            {
                                'selrestrs': [
                                    {'Value': 'human'},
                                    {'Value': 'abstract'}
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        # Create builder instance
        self.builder = CorpusCollectionBuilder(self.mock_loaded_data, self.mock_logger)
    
    def test_init(self):
        """Test CorpusCollectionBuilder initialization."""
        self.assertEqual(self.builder.loaded_data, self.mock_loaded_data)
        self.assertEqual(self.builder.logger, self.mock_logger)
        self.assertEqual(self.builder.reference_collections, {})
    
    def test_build_reference_collections_success(self):
        """Test successful build of all reference collections."""
        results = self.builder.build_reference_collections()
        
        # Verify all methods return True
        expected_results = {
            'predicate_definitions': True,
            'themrole_definitions': True,
            'verb_specific_features': True,
            'syntactic_restrictions': True,
            'selectional_restrictions': True
        }
        self.assertEqual(results, expected_results)
        
        # Verify logger was called with success message
        self.mock_logger.info.assert_called_with("Reference collections build complete: 5/5 successful")
    
    def test_build_predicate_definitions_success(self):
        """Test successful building of predicate definitions."""
        result = self.builder.build_predicate_definitions()
        
        self.assertTrue(result)
        self.assertIn('predicates', self.builder.reference_collections)
        self.assertEqual(len(self.builder.reference_collections['predicates']), 3)
        self.assertIn('cause', self.builder.reference_collections['predicates'])
        self.mock_logger.info.assert_called_with("Built predicate definitions: 3 items")
    
    def test_build_predicate_definitions_no_reference_docs(self):
        """Test building predicate definitions when reference docs are missing."""
        builder = CorpusCollectionBuilder({}, self.mock_logger)
        result = builder.build_predicate_definitions()
        
        self.assertFalse(result)
        self.mock_logger.warning.assert_called_with("Reference docs not loaded, cannot build predicate definitions")
    
    def test_build_predicate_definitions_exception(self):
        """Test handling of exceptions in build_predicate_definitions."""
        # Create mock data that will cause an exception
        bad_data = {'reference_docs': None}
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        result = builder.build_predicate_definitions()
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
        # Verify error message contains expected text
        call_args = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error building predicate definitions:", call_args)
    
    def test_build_themrole_definitions_success(self):
        """Test successful building of thematic role definitions."""
        result = self.builder.build_themrole_definitions()
        
        self.assertTrue(result)
        self.assertIn('themroles', self.builder.reference_collections)
        self.assertEqual(len(self.builder.reference_collections['themroles']), 3)
        self.assertIn('Agent', self.builder.reference_collections['themroles'])
        self.mock_logger.info.assert_called_with("Built thematic role definitions: 3 items")
    
    def test_build_themrole_definitions_no_reference_docs(self):
        """Test building thematic role definitions when reference docs are missing."""
        builder = CorpusCollectionBuilder({}, self.mock_logger)
        result = builder.build_themrole_definitions()
        
        self.assertFalse(result)
        self.mock_logger.warning.assert_called_with("Reference docs not loaded, cannot build thematic role definitions")
    
    def test_build_themrole_definitions_exception(self):
        """Test handling of exceptions in build_themrole_definitions."""
        bad_data = {'reference_docs': None}
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        result = builder.build_themrole_definitions()
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
        call_args = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error building thematic role definitions:", call_args)
    
    def test_build_verb_specific_features_success(self):
        """Test successful building of verb-specific features."""
        result = self.builder.build_verb_specific_features()
        
        self.assertTrue(result)
        self.assertIn('verb_specific_features', self.builder.reference_collections)
        features = self.builder.reference_collections['verb_specific_features']
        
        # Should contain features from both VerbNet data and reference docs
        expected_features = ['caused_motion', 'feature1', 'feature2', 'mental_state', 'motion_verb', 'state_verb']
        self.assertEqual(sorted(features), expected_features)
        self.mock_logger.info.assert_called_with("Built verb-specific features: 6 features")
    
    def test_build_verb_specific_features_verbnet_only(self):
        """Test building verb-specific features with only VerbNet data."""
        data = {'verbnet': self.mock_loaded_data['verbnet']}
        builder = CorpusCollectionBuilder(data, self.mock_logger)
        
        result = builder.build_verb_specific_features()
        
        self.assertTrue(result)
        features = builder.reference_collections['verb_specific_features']
        expected_features = ['caused_motion', 'mental_state', 'motion_verb', 'state_verb']
        self.assertEqual(sorted(features), expected_features)
    
    def test_build_verb_specific_features_reference_only(self):
        """Test building verb-specific features with only reference docs."""
        data = {'reference_docs': self.mock_loaded_data['reference_docs']}
        builder = CorpusCollectionBuilder(data, self.mock_logger)
        
        result = builder.build_verb_specific_features()
        
        self.assertTrue(result)
        features = builder.reference_collections['verb_specific_features']
        expected_features = ['feature1', 'feature2']
        self.assertEqual(sorted(features), expected_features)
    
    def test_build_verb_specific_features_no_data(self):
        """Test building verb-specific features with no relevant data."""
        builder = CorpusCollectionBuilder({}, self.mock_logger)
        
        result = builder.build_verb_specific_features()
        
        self.assertTrue(result)  # Should still succeed but with empty list
        self.assertEqual(builder.reference_collections['verb_specific_features'], [])
        self.mock_logger.info.assert_called_with("Built verb-specific features: 0 features")
    
    def test_build_verb_specific_features_exception(self):
        """Test handling of exceptions in build_verb_specific_features."""
        bad_data = {'verbnet': {'classes': None}}
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        result = builder.build_verb_specific_features()
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
        call_args = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error building verb-specific features:", call_args)
    
    def test_build_syntactic_restrictions_success(self):
        """Test successful building of syntactic restrictions."""
        result = self.builder.build_syntactic_restrictions()
        
        self.assertTrue(result)
        self.assertIn('syntactic_restrictions', self.builder.reference_collections)
        restrictions = self.builder.reference_collections['syntactic_restrictions']
        expected_restrictions = ['adj', 'np', 'pp', 'vp']
        self.assertEqual(sorted(restrictions), expected_restrictions)
        self.mock_logger.info.assert_called_with("Built syntactic restrictions: 4 items")
    
    def test_build_syntactic_restrictions_no_verbnet(self):
        """Test building syntactic restrictions with no VerbNet data."""
        builder = CorpusCollectionBuilder({}, self.mock_logger)
        
        result = builder.build_syntactic_restrictions()
        
        self.assertTrue(result)
        self.assertEqual(builder.reference_collections['syntactic_restrictions'], [])
        self.mock_logger.info.assert_called_with("Built syntactic restrictions: 0 items")
    
    def test_build_syntactic_restrictions_exception(self):
        """Test handling of exceptions in build_syntactic_restrictions."""
        bad_data = {'verbnet': {'classes': {'bad_class': {'frames': [{'syntax': None}]}}}}
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        result = builder.build_syntactic_restrictions()
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
        call_args = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error building syntactic restrictions:", call_args)
    
    def test_build_selectional_restrictions_success(self):
        """Test successful building of selectional restrictions."""
        result = self.builder.build_selectional_restrictions()
        
        self.assertTrue(result)
        self.assertIn('selectional_restrictions', self.builder.reference_collections)
        restrictions = self.builder.reference_collections['selectional_restrictions']
        expected_restrictions = ['abstract', 'animate', 'concrete', 'human']
        self.assertEqual(sorted(restrictions), expected_restrictions)
        self.mock_logger.info.assert_called_with("Built selectional restrictions: 4 items")
    
    def test_build_selectional_restrictions_no_verbnet(self):
        """Test building selectional restrictions with no VerbNet data."""
        builder = CorpusCollectionBuilder({}, self.mock_logger)
        
        result = builder.build_selectional_restrictions()
        
        self.assertTrue(result)
        self.assertEqual(builder.reference_collections['selectional_restrictions'], [])
        self.mock_logger.info.assert_called_with("Built selectional restrictions: 0 items")
    
    def test_build_selectional_restrictions_exception(self):
        """Test handling of exceptions in build_selectional_restrictions."""
        bad_data = {'verbnet': {'classes': {'bad_class': {'themroles': None}}}}
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        result = builder.build_selectional_restrictions()
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
        call_args = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error building selectional restrictions:", call_args)
    
    def test_build_reference_collections_partial_failure(self):
        """Test build_reference_collections when some methods fail."""
        # Create a builder with partial data that will cause some methods to fail
        partial_data = {
            'reference_docs': {
                'predicates': {'test': 'predicate'}
                # Missing themroles - but this will still succeed with empty dict
            }
        }
        builder = CorpusCollectionBuilder(partial_data, self.mock_logger)
        
        results = builder.build_reference_collections()
        
        # All should succeed - missing themroles key results in empty dict, which is valid
        self.assertTrue(results['predicate_definitions'])
        self.assertTrue(results['themrole_definitions'])  # Empty dict is still successful
        self.assertTrue(results['verb_specific_features'])  # Should succeed with empty data
        self.assertTrue(results['syntactic_restrictions'])  # Should succeed with empty data
        self.assertTrue(results['selectional_restrictions'])  # Should succeed with empty data
        
        # Logger should report 5/5 successful
        self.mock_logger.info.assert_called_with("Reference collections build complete: 5/5 successful")
    
    def test_build_reference_collections_actual_failure(self):
        """Test build_reference_collections when methods actually fail due to exceptions."""
        # Create data that will cause exceptions in some methods
        bad_data = {
            'reference_docs': None,  # This will cause exceptions in predicate/themrole methods
            'verbnet': {'classes': None}  # This will cause exceptions in other methods
        }
        builder = CorpusCollectionBuilder(bad_data, self.mock_logger)
        
        results = builder.build_reference_collections()
        
        # Most should fail due to exceptions
        self.assertFalse(results['predicate_definitions'])
        self.assertFalse(results['themrole_definitions'])
        self.assertFalse(results['verb_specific_features'])
        self.assertFalse(results['syntactic_restrictions'])
        self.assertFalse(results['selectional_restrictions'])
        
        # Logger should report 0/5 successful
        self.mock_logger.info.assert_called_with("Reference collections build complete: 0/5 successful")
    
    def test_empty_collections_handling(self):
        """Test handling of empty collections in data."""
        empty_data = {
            'reference_docs': {
                'predicates': {},
                'themroles': {},
                'verb_specific': {}
            },
            'verbnet': {
                'classes': {}
            }
        }
        builder = CorpusCollectionBuilder(empty_data, self.mock_logger)
        
        # All methods should succeed but build empty collections
        results = builder.build_reference_collections()
        
        for method_result in results.values():
            self.assertTrue(method_result)
        
        # Verify empty collections were built
        self.assertEqual(builder.reference_collections['predicates'], {})
        self.assertEqual(builder.reference_collections['themroles'], {})
        self.assertEqual(builder.reference_collections['verb_specific_features'], [])
        self.assertEqual(builder.reference_collections['syntactic_restrictions'], [])
        self.assertEqual(builder.reference_collections['selectional_restrictions'], [])
    
    def test_complex_verbnet_structure_handling(self):
        """Test handling of complex VerbNet data structures."""
        complex_data = {
            'verbnet': {
                'classes': {
                    'complex-class': {
                        'frames': [
                            {
                                'syntax': [
                                    [
                                        {'synrestrs': []},  # Empty synrestrs
                                        {'synrestrs': [
                                            {'Value': 'complex_syn1'},
                                            {'Other_Key': 'should_be_ignored'}  # Wrong key
                                        ]}
                                    ],
                                    [
                                        {'synrestrs': [
                                            {'Value': 'complex_syn2'}
                                        ]}
                                    ]
                                ],
                                'semantics': [
                                    [
                                        {'value': 'complex_sem1'},
                                        {'other_key': 'ignored'},  # Wrong key
                                        {'value': ''}  # Empty value
                                    ],
                                    [
                                        {'value': 'complex_sem2'}
                                    ]
                                ]
                            }
                        ],
                        'themroles': [
                            {
                                'selrestrs': [
                                    {'Value': 'complex_sel1'},
                                    {'Wrong_Key': 'ignored'}  # Wrong key
                                ]
                            },
                            {
                                'selrestrs': []  # Empty selrestrs
                            },
                            {
                                'selrestrs': [
                                    {'Value': 'complex_sel2'}
                                ]
                            }
                        ]
                    }
                }
            }
        }
        builder = CorpusCollectionBuilder(complex_data, self.mock_logger)
        
        # Test verb-specific features
        result = builder.build_verb_specific_features()
        self.assertTrue(result)
        features = builder.reference_collections['verb_specific_features']
        self.assertEqual(sorted(features), ['complex_sem1', 'complex_sem2'])
        
        # Test syntactic restrictions  
        result = builder.build_syntactic_restrictions()
        self.assertTrue(result)
        restrictions = builder.reference_collections['syntactic_restrictions']
        self.assertEqual(sorted(restrictions), ['complex_syn1', 'complex_syn2'])
        
        # Test selectional restrictions
        result = builder.build_selectional_restrictions()
        self.assertTrue(result)
        restrictions = builder.reference_collections['selectional_restrictions']
        self.assertEqual(sorted(restrictions), ['complex_sel1', 'complex_sel2'])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)