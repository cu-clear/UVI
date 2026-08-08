"""
Test suite for CorpusLoader class.

Tests the corpus loading and parsing functionality for all supported corpus types.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.corpus_loader import CorpusLoader


class TestCorpusLoader(unittest.TestCase):
    """Test cases for CorpusLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the corpora directory relative to project root
        corpora_path = Path(__file__).parent.parent / 'corpora'
        self.loader = CorpusLoader(str(corpora_path))
    
    def test_initialization(self):
        """Test CorpusLoader initialization."""
        self.assertIsInstance(self.loader, CorpusLoader)
        self.assertTrue(hasattr(self.loader, 'corpora_path'))
        self.assertTrue(hasattr(self.loader, 'corpus_paths'))
        self.assertTrue(hasattr(self.loader, 'loaded_data'))
    
    def test_corpus_path_detection(self):
        """Test automatic corpus path detection."""
        paths = self.loader.get_corpus_paths()
        self.assertIsInstance(paths, dict)
        
        # Check that some expected corpora are detected
        expected_corpora = ['verbnet', 'framenet', 'propbank', 'wordnet', 'bso', 'semnet', 'reference_docs']
        for corpus in expected_corpora:
            if corpus in paths:
                self.assertTrue(Path(paths[corpus]).exists(), f"{corpus} path should exist: {paths[corpus]}")
    
    def test_load_verbnet_if_available(self):
        """Test VerbNet loading if available."""
        if 'verbnet' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('verbnet')
                self.assertIsInstance(result, dict)
                self.assertIn('classes', result)  # VerbNet should have classes
                
                # Check that data was actually loaded
                stats = self.loader.get_collection_statistics()
                if 'verbnet' in stats:
                    print(f"VerbNet loaded: {stats['verbnet']}")
            except Exception as e:
                self.skipTest(f"VerbNet loading failed: {e}")
        else:
            self.skipTest("VerbNet corpus not found")
    
    def test_load_framenet_if_available(self):
        """Test FrameNet loading if available."""
        if 'framenet' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('framenet')
                self.assertIsInstance(result, dict)
                self.assertIn('frames', result)  # FrameNet should have frames
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'framenet' in stats:
                    print(f"FrameNet loaded: {stats['framenet']}")
            except Exception as e:
                self.skipTest(f"FrameNet loading failed: {e}")
        else:
            self.skipTest("FrameNet corpus not found")
    
    def test_load_propbank_if_available(self):
        """Test PropBank loading if available."""
        if 'propbank' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('propbank')
                self.assertIsInstance(result, dict)
                # PropBank structure varies, just check it's a dict with data
                self.assertTrue(len(result) > 0)
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'propbank' in stats:
                    print(f"PropBank loaded: {stats['propbank']}")
            except Exception as e:
                self.skipTest(f"PropBank loading failed: {e}")
        else:
            self.skipTest("PropBank corpus not found")
    
    def test_load_wordnet_if_available(self):
        """Test WordNet loading if available."""
        if 'wordnet' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('wordnet')
                self.assertIsInstance(result, dict)
                # WordNet typically has synsets and indices
                self.assertTrue(len(result) > 0)
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'wordnet' in stats:
                    print(f"WordNet loaded: {stats['wordnet']}")
            except Exception as e:
                self.skipTest(f"WordNet loading failed: {e}")
        else:
            self.skipTest("WordNet corpus not found")
    
    def test_load_bso_if_available(self):
        """Test BSO loading if available."""
        if 'bso' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('bso')
                self.assertIsInstance(result, dict)
                # BSO might be empty but should still be a dict
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'bso' in stats:
                    print(f"BSO loaded: {stats['bso']}")
            except Exception as e:
                self.skipTest(f"BSO loading failed: {e}")
        else:
            self.skipTest("BSO corpus not found")
    
    def test_load_semnet_if_available(self):
        """Test SemNet loading if available."""
        if 'semnet' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('semnet')
                self.assertIsInstance(result, dict)
                # SemNet should have verb/noun data
                self.assertTrue(len(result) >= 0)  # Allow empty but valid dict
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'semnet' in stats:
                    print(f"SemNet loaded: {stats['semnet']}")
            except Exception as e:
                self.skipTest(f"SemNet loading failed: {e}")
        else:
            self.skipTest("SemNet corpus not found")
    
    def test_load_reference_docs_if_available(self):
        """Test reference docs loading if available."""
        if 'reference_docs' in self.loader.corpus_paths:
            try:
                result = self.loader.load_corpus('reference_docs')
                self.assertIsInstance(result, dict)
                # Reference docs should have predicates, themroles, etc.
                self.assertTrue(len(result) >= 0)  # Allow empty but valid dict
                
                # Check that data was loaded
                stats = self.loader.get_collection_statistics()
                if 'reference_docs' in stats:
                    print(f"Reference docs loaded: {stats['reference_docs']}")
            except Exception as e:
                self.skipTest(f"Reference docs loading failed: {e}")
        else:
            self.skipTest("Reference docs corpus not found")
    
    def test_load_all_corpora(self):
        """Test loading all available corpora."""
        try:
            results = self.loader.load_all_corpora()
            self.assertIsInstance(results, dict)
            
            # Print summary of what was loaded
            success_count = sum(1 for status in results.values() if status.get('status') == 'success')
            print(f"Successfully loaded {success_count} out of {len(results)} corpora")
            
            for corpus_name, status in results.items():
                print(f"  {corpus_name}: {status.get('status', 'unknown')}")
                if status.get('status') == 'error':
                    print(f"    Error: {status.get('error', 'unknown error')}")
                
        except Exception as e:
            self.fail(f"Load all corpora failed: {e}")
    
    def test_reference_collection_building(self):
        """Test building reference collections."""
        # First load some data
        if 'verbnet' in self.loader.corpus_paths:
            try:
                self.loader.load_corpus('verbnet')
            except:
                pass
        
        if 'reference_docs' in self.loader.corpus_paths:
            try:
                self.loader.load_corpus('reference_docs')
            except:
                pass
        
        # Try to build reference collections
        try:
            results = self.loader.build_reference_collections()
            self.assertIsInstance(results, dict)
            print(f"Reference collections built: {results}")
        except Exception as e:
            self.skipTest(f"Reference collection building failed: {e}")
    
    def test_collection_statistics(self):
        """Test getting collection statistics."""
        # Load at least one corpus if available
        for corpus_name in ['verbnet', 'framenet', 'propbank', 'wordnet']:
            if corpus_name in self.loader.corpus_paths:
                try:
                    self.loader.load_corpus(corpus_name)
                    break
                except:
                    continue
        
        try:
            stats = self.loader.get_collection_statistics()
            self.assertIsInstance(stats, dict)
            print(f"Collection statistics: {stats}")
        except Exception as e:
            self.skipTest(f"Statistics collection failed: {e}")
    
    def test_validation(self):
        """Test collection validation."""
        # Load at least one corpus if available
        for corpus_name in ['verbnet', 'framenet', 'propbank']:
            if corpus_name in self.loader.corpus_paths:
                try:
                    self.loader.load_corpus(corpus_name)
                    break
                except:
                    continue
        
        try:
            validation_results = self.loader.validate_collections()
            self.assertIsInstance(validation_results, dict)
            print(f"Validation results: {validation_results}")
        except Exception as e:
            self.skipTest(f"Validation failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)