"""
Comprehensive unit tests for the CorpusCollectionAnalyzer class.

This test suite covers all key methods of the CorpusCollectionAnalyzer class
with mock data and various error handling scenarios.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from uvi.corpus_loader import CorpusCollectionAnalyzer


class TestCorpusCollectionAnalyzer(unittest.TestCase):
    """Test suite for CorpusCollectionAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock loaded data with comprehensive test data
        self.mock_loaded_data = {
            'verbnet': {
                'statistics': {
                    'total_verbs': 3000,
                    'total_frames': 500,
                    'coverage': 0.95
                },
                'classes': {
                    'class-1': {'members': ['run', 'walk']},
                    'class-2': {'members': ['think', 'believe']},
                    'class-3': {'members': ['give', 'send']}
                },
                'members': {
                    'run': {'class': 'class-1'},
                    'walk': {'class': 'class-1'},
                    'think': {'class': 'class-2'},
                    'believe': {'class': 'class-2'},
                    'give': {'class': 'class-3'},
                    'send': {'class': 'class-3'}
                }
            },
            'framenet': {
                'statistics': {
                    'total_frames': 1200,
                    'total_lexical_units': 13000,
                    'coverage': 0.88
                },
                'frames': {
                    'Motion': {'description': 'Movement frame'},
                    'Cognition': {'description': 'Thinking frame'},
                    'Transfer': {'description': 'Giving frame'},
                    'Communication': {'description': 'Speaking frame'}
                },
                'lexical_units': {
                    'run.v': {'frame': 'Motion'},
                    'walk.v': {'frame': 'Motion'},
                    'think.v': {'frame': 'Cognition'},
                    'give.v': {'frame': 'Transfer'},
                    'speak.v': {'frame': 'Communication'}
                }
            },
            'propbank': {
                'statistics': {
                    'total_predicates': 8000,
                    'total_rolesets': 12000,
                    'coverage': 0.92
                },
                'predicates': {
                    'run.01': {'description': 'Run predicate'},
                    'think.01': {'description': 'Think predicate'},
                    'give.01': {'description': 'Give predicate'}
                },
                'rolesets': {
                    'run.01': {'roles': ['Agent', 'Direction']},
                    'think.01': {'roles': ['Thinker', 'Topic']},
                    'give.01': {'roles': ['Giver', 'Theme', 'Recipient']},
                    'speak.01': {'roles': ['Speaker', 'Message']}
                }
            },
            'wordnet': {
                'statistics': {
                    'total_synsets': 117000,
                    'nouns': 82115,
                    'verbs': 13767,
                    'adjectives': 18156,
                    'adverbs': 3621
                }
            },
            'ontonotes': {
                'statistics': {
                    'total_documents': 63000,
                    'total_sentences': 1400000,
                    'total_tokens': 35000000
                }
            }
        }
        
        # Mock load status
        self.mock_load_status = {
            'verbnet': {'loaded': True, 'timestamp': '2024-01-15T10:00:00'},
            'framenet': {'loaded': True, 'timestamp': '2024-01-15T10:05:00'},
            'propbank': {'loaded': True, 'timestamp': '2024-01-15T10:10:00'},
            'wordnet': {'loaded': True, 'timestamp': '2024-01-15T10:15:00'},
            'ontonotes': {'loaded': False, 'error': 'File not found'}
        }
        
        # Mock build metadata
        self.mock_build_metadata = {
            'last_build': '2024-01-15T09:30:00',
            'build_version': '1.2.3',
            'build_environment': 'test',
            'collections_built': ['predicates', 'themroles', 'syntactic_restrictions']
        }
        
        # Mock reference collections
        self.mock_reference_collections = {
            'predicates': {
                'motion': {'description': 'Motion predicate'},
                'cognition': {'description': 'Thinking predicate'},
                'transfer': {'description': 'Transfer predicate'}
            },
            'themroles': {
                'Agent': {'description': 'Doer of action'},
                'Theme': {'description': 'Thing being acted upon'},
                'Goal': {'description': 'End point of action'}
            },
            'syntactic_restrictions': ['np', 'pp', 'vp', 'adj'],
            'selectional_restrictions': ['animate', 'concrete', 'abstract'],
            'verb_specific_features': ['caused_motion', 'mental_state', 'transfer_event']
        }
        
        # Mock corpus paths
        self.mock_corpus_paths = {
            'verbnet': '/path/to/verbnet',
            'framenet': '/path/to/framenet',
            'propbank': '/path/to/propbank',
            'wordnet': '/path/to/wordnet',
            'ontonotes': '/path/to/ontonotes'
        }
        
        # Create analyzer instance
        self.analyzer = CorpusCollectionAnalyzer(
            self.mock_loaded_data,
            self.mock_load_status,
            self.mock_build_metadata,
            self.mock_reference_collections,
            self.mock_corpus_paths
        )
    
    def test_init(self):
        """Test CorpusCollectionAnalyzer initialization."""
        self.assertEqual(self.analyzer.loaded_data, self.mock_loaded_data)
        self.assertEqual(self.analyzer.load_status, self.mock_load_status)
        self.assertEqual(self.analyzer.build_metadata, self.mock_build_metadata)
        self.assertEqual(self.analyzer.reference_collections, self.mock_reference_collections)
        self.assertEqual(self.analyzer.corpus_paths, self.mock_corpus_paths)
    
    def test_get_collection_statistics_complete_data(self):
        """Test get_collection_statistics with complete data."""
        statistics = self.analyzer.get_collection_statistics()
        
        # Check VerbNet statistics
        self.assertIn('verbnet', statistics)
        vn_stats = statistics['verbnet']
        self.assertEqual(vn_stats['total_verbs'], 3000)
        self.assertEqual(vn_stats['total_frames'], 500)
        self.assertEqual(vn_stats['coverage'], 0.95)
        self.assertEqual(vn_stats['classes'], 3)
        self.assertEqual(vn_stats['members'], 6)
        
        # Check FrameNet statistics
        self.assertIn('framenet', statistics)
        fn_stats = statistics['framenet']
        self.assertEqual(fn_stats['total_frames'], 1200)
        self.assertEqual(fn_stats['total_lexical_units'], 13000)
        self.assertEqual(fn_stats['coverage'], 0.88)
        self.assertEqual(fn_stats['frames'], 4)
        self.assertEqual(fn_stats['lexical_units'], 5)
        
        # Check PropBank statistics
        self.assertIn('propbank', statistics)
        pb_stats = statistics['propbank']
        self.assertEqual(pb_stats['total_predicates'], 8000)
        self.assertEqual(pb_stats['total_rolesets'], 12000)
        self.assertEqual(pb_stats['coverage'], 0.92)
        self.assertEqual(pb_stats['predicates'], 3)
        self.assertEqual(pb_stats['rolesets'], 4)
        
        # Check other corpora statistics
        self.assertIn('wordnet', statistics)
        self.assertEqual(statistics['wordnet']['total_synsets'], 117000)
        
        self.assertIn('ontonotes', statistics)
        self.assertEqual(statistics['ontonotes']['total_documents'], 63000)
        
        # Check reference collections statistics
        self.assertIn('reference_collections', statistics)
        ref_stats = statistics['reference_collections']
        self.assertEqual(ref_stats['predicates'], 3)
        self.assertEqual(ref_stats['themroles'], 3)
        self.assertEqual(ref_stats['syntactic_restrictions'], 4)
        self.assertEqual(ref_stats['selectional_restrictions'], 3)
        self.assertEqual(ref_stats['verb_specific_features'], 3)
    
    def test_get_collection_statistics_missing_statistics(self):
        """Test get_collection_statistics when statistics are missing."""
        # Create data without statistics
        data_without_stats = {
            'verbnet': {
                'classes': {'class-1': {}, 'class-2': {}},
                'members': {'verb1': {}, 'verb2': {}, 'verb3': {}}
            },
            'framenet': {
                'frames': {'frame1': {}, 'frame2': {}},
                'lexical_units': {'lu1': {}}
            },
            'propbank': {
                'predicates': {'pred1': {}},
                'rolesets': {'role1': {}, 'role2': {}}
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            data_without_stats, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # Should still count classes/members even without explicit statistics
        self.assertEqual(statistics['verbnet']['classes'], 2)
        self.assertEqual(statistics['verbnet']['members'], 3)
        self.assertEqual(statistics['framenet']['frames'], 2)
        self.assertEqual(statistics['framenet']['lexical_units'], 1)
        self.assertEqual(statistics['propbank']['predicates'], 1)
        self.assertEqual(statistics['propbank']['rolesets'], 2)
    
    def test_get_collection_statistics_exception_handling(self):
        """Test get_collection_statistics with data that causes exceptions."""
        # Create problematic data
        problematic_data = {
            'verbnet': None,  # This will cause an exception
            'framenet': {
                'statistics': {'valid_stat': 100},
                'frames': 'not_a_dict'  # Strings are not counted as collections, returns 0
            },
            'propbank': {
                'predicates': {'pred1': {}},  # This should work fine
                'rolesets': {'role1': {}}
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            problematic_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # VerbNet should have an error
        self.assertIn('verbnet', statistics)
        self.assertIn('error', statistics['verbnet'])
        
        # FrameNet won't error - strings are treated as non-collections (returns 0)
        self.assertIn('framenet', statistics)
        self.assertEqual(statistics['framenet']['valid_stat'], 100)
        self.assertEqual(statistics['framenet']['frames'], 0)  # strings return 0, not string length
        self.assertEqual(statistics['framenet']['lexical_units'], 0)  # len({}) default
        
        # PropBank should work fine
        self.assertIn('propbank', statistics)
        self.assertEqual(statistics['propbank']['predicates'], 1)
        self.assertEqual(statistics['propbank']['rolesets'], 1)
    
    def test_get_collection_statistics_empty_data(self):
        """Test get_collection_statistics with empty data."""
        analyzer = CorpusCollectionAnalyzer({}, {}, {}, {}, {})
        
        statistics = analyzer.get_collection_statistics()
        
        # Should return empty reference collections
        self.assertIn('reference_collections', statistics)
        self.assertEqual(statistics['reference_collections'], {})
    
    def test_get_collection_statistics_unknown_corpus(self):
        """Test get_collection_statistics with unknown corpus types."""
        unknown_data = {
            'custom_corpus': {
                'statistics': {'custom_stat': 42}
            },
            'another_corpus': {
                'data': ['item1', 'item2', 'item3']
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            unknown_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # Unknown corpora should use the generic statistics extraction
        self.assertIn('custom_corpus', statistics)
        self.assertEqual(statistics['custom_corpus']['custom_stat'], 42)
        
        self.assertIn('another_corpus', statistics)
        # Should be empty dict since no 'statistics' key exists
        self.assertEqual(statistics['another_corpus'], {})
    
    @patch('uvi.corpus_loader.CorpusCollectionAnalyzer.datetime')
    def test_get_build_metadata(self, mock_datetime):
        """Test get_build_metadata method."""
        # Mock the datetime to return a known value
        mock_now = datetime(2024, 1, 15, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        metadata = self.analyzer.get_build_metadata()
        
        # Check structure
        self.assertIn('build_metadata', metadata)
        self.assertIn('load_status', metadata)
        self.assertIn('corpus_paths', metadata)
        self.assertIn('timestamp', metadata)
        
        # Check content
        self.assertEqual(metadata['build_metadata'], self.mock_build_metadata)
        self.assertEqual(metadata['load_status'], self.mock_load_status)
        self.assertEqual(metadata['corpus_paths'], self.mock_corpus_paths)
        self.assertEqual(metadata['timestamp'], '2024-01-15T12:30:45')
    
    def test_get_build_metadata_empty_data(self):
        """Test get_build_metadata with empty input data."""
        analyzer = CorpusCollectionAnalyzer({}, {}, {}, {}, {})
        
        metadata = analyzer.get_build_metadata()
        
        # Should still return the structure with empty data
        self.assertIn('build_metadata', metadata)
        self.assertIn('load_status', metadata)
        self.assertIn('corpus_paths', metadata)
        self.assertIn('timestamp', metadata)
        
        self.assertEqual(metadata['build_metadata'], {})
        self.assertEqual(metadata['load_status'], {})
        self.assertEqual(metadata['corpus_paths'], {})
        # Timestamp should still be present
        self.assertIsInstance(metadata['timestamp'], str)
    
    def test_reference_collections_with_different_types(self):
        """Test reference collections statistics with different data types."""
        mixed_collections = {
            'list_collection': ['item1', 'item2', 'item3'],
            'dict_collection': {'key1': 'value1', 'key2': 'value2'},
            'set_collection': {'set_item1', 'set_item2', 'set_item3', 'set_item4'},
            'string_collection': 'not_countable',
            'number_collection': 42,
            'none_collection': None,
            'empty_list': [],
            'empty_dict': {},
            'empty_set': set()
        }
        
        analyzer = CorpusCollectionAnalyzer(
            {}, {}, {}, mixed_collections, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        ref_stats = statistics['reference_collections']
        
        # Lists, dicts, and sets should be counted correctly
        self.assertEqual(ref_stats['list_collection'], 3)
        self.assertEqual(ref_stats['dict_collection'], 2)
        self.assertEqual(ref_stats['set_collection'], 4)
        
        # Non-countable types should return 0
        self.assertEqual(ref_stats['string_collection'], 0)
        self.assertEqual(ref_stats['number_collection'], 0)
        self.assertEqual(ref_stats['none_collection'], 0)
        
        # Empty collections should return 0
        self.assertEqual(ref_stats['empty_list'], 0)
        self.assertEqual(ref_stats['empty_dict'], 0)
        self.assertEqual(ref_stats['empty_set'], 0)
    
    def test_verbnet_statistics_edge_cases(self):
        """Test VerbNet statistics with edge cases."""
        edge_case_data = {
            'verbnet': {
                'statistics': {'existing_stat': 100},
                'classes': None,  # None is handled gracefully, returns 0
                'members': {'verb1': {}}
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            edge_case_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # None is handled gracefully, no exception thrown
        self.assertIn('verbnet', statistics)
        self.assertEqual(statistics['verbnet']['existing_stat'], 100)
        self.assertEqual(statistics['verbnet']['classes'], 0)  # None returns 0
        self.assertEqual(statistics['verbnet']['members'], 1)  # dict with 1 item
    
    def test_framenet_statistics_edge_cases(self):
        """Test FrameNet statistics with edge cases."""
        edge_case_data = {
            'framenet': {
                'statistics': {'valid_stat': 200},
                'frames': {'frame1': {}, 'frame2': {}},
                'lexical_units': 'not_a_dict'  # Strings are not counted as collections, returns 0
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            edge_case_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # Strings are treated as non-collections, return 0
        self.assertIn('framenet', statistics)
        self.assertEqual(statistics['framenet']['valid_stat'], 200)
        self.assertEqual(statistics['framenet']['frames'], 2)
        self.assertEqual(statistics['framenet']['lexical_units'], 0)  # strings return 0, not string length
    
    def test_framenet_actual_exception_case(self):
        """Test FrameNet statistics with data that actually causes an exception."""
        # Create a mock object that will raise an exception when .get() is called
        class BadData:
            def get(self, key, default=None):
                if key == 'statistics':
                    return {'valid_stat': 300}
                raise ValueError("Simulated exception")
        
        edge_case_data = {
            'framenet': BadData()
        }
        
        analyzer = CorpusCollectionAnalyzer(
            edge_case_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # Should handle the exception and return error
        self.assertIn('framenet', statistics)
        self.assertIn('error', statistics['framenet'])
    
    def test_actual_exception_with_bad_corpus_data(self):
        """Test exception handling with corpus data that causes actual exceptions."""
        # Create a mock object that will raise an exception during statistics processing
        class BadCorpusData:
            def get(self, key, default=None):
                if key == 'statistics':
                    return {'existing_stat': 100}
                elif key in ['classes', 'members', 'frames', 'lexical_units', 'predicates', 'rolesets']:
                    raise RuntimeError("Simulated processing error")
                return default
        
        problematic_data = {
            'verbnet': BadCorpusData(),  # This will cause an exception during processing
            'framenet': BadCorpusData(),  # This will also cause an exception
            'propbank': BadCorpusData()   # This will also cause an exception
        }
        
        analyzer = CorpusCollectionAnalyzer(
            problematic_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # All should have errors due to exceptions during processing
        for corpus in ['verbnet', 'framenet', 'propbank']:
            self.assertIn(corpus, statistics)
            self.assertIn('error', statistics[corpus])
            self.assertIn('Simulated processing error', statistics[corpus]['error'])
    
    def test_propbank_statistics_edge_cases(self):
        """Test PropBank statistics with edge cases."""
        edge_case_data = {
            'propbank': {
                'statistics': {'valid_stat': 300},
                'predicates': {'pred1': {}, 'pred2': {}},
                'rolesets': None  # None is handled gracefully, returns 0
            }
        }
        
        analyzer = CorpusCollectionAnalyzer(
            edge_case_data, {}, {}, {}, {}
        )
        
        statistics = analyzer.get_collection_statistics()
        
        # None is handled gracefully, no exception thrown
        self.assertIn('propbank', statistics)
        self.assertEqual(statistics['propbank']['valid_stat'], 300)
        self.assertEqual(statistics['propbank']['predicates'], 2)  # dict with 2 items
        self.assertEqual(statistics['propbank']['rolesets'], 0)  # None returns 0
    
    def test_comprehensive_integration(self):
        """Test comprehensive integration of all methods."""
        # Test both methods work together correctly
        statistics = self.analyzer.get_collection_statistics()
        metadata = self.analyzer.get_build_metadata()
        
        # Verify statistics has all expected corpora
        expected_corpora = ['verbnet', 'framenet', 'propbank', 'wordnet', 'ontonotes']
        for corpus in expected_corpora:
            self.assertIn(corpus, statistics)
        
        # Verify reference collections are included
        self.assertIn('reference_collections', statistics)
        
        # Verify metadata structure
        expected_metadata_keys = ['build_metadata', 'load_status', 'corpus_paths', 'timestamp']
        for key in expected_metadata_keys:
            self.assertIn(key, metadata)
        
        # Verify data consistency
        self.assertEqual(len(metadata['corpus_paths']), 5)
        self.assertEqual(len(metadata['load_status']), 5)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)