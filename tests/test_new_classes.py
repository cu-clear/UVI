"""
Test suite for the new Presentation and CorpusMonitor classes.
"""

import unittest
import time
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for importing
test_dir = Path(__file__).parent
src_dir = test_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

from uvi.Presentation import Presentation
from uvi.CorpusMonitor import CorpusMonitor


class TestPresentation(unittest.TestCase):
    """Test cases for the Presentation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.presenter = Presentation()
    
    def test_init(self):
        """Test Presentation initialization."""
        self.assertIsInstance(self.presenter, Presentation)
        self.assertIsInstance(self.presenter._color_cache, dict)
    
    def test_generate_unique_id(self):
        """Test unique ID generation."""
        id1 = self.presenter.generate_unique_id()
        id2 = self.presenter.generate_unique_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertEqual(len(id1), 16)
        self.assertEqual(len(id2), 16)
        self.assertNotEqual(id1, id2)
    
    def test_generate_element_colors(self):
        """Test element color generation."""
        elements = ['ARG0', 'ARG1', 'ARG2']
        colors = self.presenter.generate_element_colors(elements, seed=42)
        
        self.assertIsInstance(colors, dict)
        self.assertEqual(len(colors), 3)
        
        # Test consistency with same seed
        colors2 = self.presenter.generate_element_colors(elements, seed=42)
        self.assertEqual(colors, colors2)
        
        # All colors should be valid hex colors
        for color in colors.values():
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)
    
    def test_strip_object_ids(self):
        """Test stripping of internal object IDs."""
        data = {
            'class_id': 'run-51.3.2',
            '_internal_id': 123,
            'members': ['run', 'jog'],
            'object_id': 'mongo_456',
            'mongodb_id': 'obj_789'
        }
        
        clean_data = self.presenter.strip_object_ids(data)
        
        self.assertIn('class_id', clean_data)
        self.assertIn('members', clean_data)
        self.assertNotIn('_internal_id', clean_data)
        self.assertNotIn('object_id', clean_data)
        self.assertNotIn('mongodb_id', clean_data)
    
    def test_json_to_display(self):
        """Test JSON display conversion."""
        data = {'test': 'value', '_internal': 'hidden'}
        json_str = self.presenter.json_to_display(data)
        
        self.assertIsInstance(json_str, str)
        self.assertIn('test', json_str)
        self.assertNotIn('_internal', json_str)
    
    def test_format_themrole_display(self):
        """Test thematic role formatting."""
        themrole_data = {
            'name': 'Agent',
            'type': 'animate',
            'selectional_restrictions': ['+animate']
        }
        
        result = self.presenter.format_themrole_display(themrole_data)
        
        self.assertIsInstance(result, str)
        self.assertIn('Agent', result)
        self.assertIn('animate', result)
        self.assertIn('themrole-name', result)
    
    def test_format_predicate_display(self):
        """Test predicate formatting."""
        predicate_data = {
            'name': 'motion',
            'args': ['Theme', 'Goal'],
            'description': 'Motion predicate'
        }
        
        result = self.presenter.format_predicate_display(predicate_data)
        
        self.assertIsInstance(result, str)
        self.assertIn('motion', result)
        self.assertIn('Theme', result)
        self.assertIn('predicate-name', result)
    
    def test_format_restriction_display(self):
        """Test restriction formatting."""
        restriction_data = {
            'value': '+animate',
            'logic': 'and',
            'type': 'selectional'
        }
        
        result = self.presenter.format_restriction_display(restriction_data, 'selectional')
        
        self.assertIsInstance(result, str)
        self.assertIn('+animate', result)
        self.assertIn('selectional-restriction', result)
    
    def test_sanitize_html(self):
        """Test HTML sanitization."""
        dangerous_text = "<script>alert('xss')</script>"
        sanitized = self.presenter._sanitize_html(dangerous_text)
        
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)
        self.assertIn('&lt;script&gt;', sanitized)
    
    def test_format_propbank_example(self):
        """Test PropBank example formatting."""
        example = {
            'text': 'John ran quickly',
            'args': [
                {'text': 'John', 'type': 'ARG0'},
                {'text': 'quickly', 'type': 'ARGM-MNR'}
            ]
        }
        
        result = self.presenter.format_propbank_example(example)
        
        self.assertIsInstance(result, dict)
        self.assertIn('colored_text', result)
        self.assertIn('arg_colors', result)
        self.assertIn('propbank-arg', result['colored_text'])


class MockCorpusLoader:
    """Mock corpus loader for testing."""
    
    def __init__(self):
        self.rebuild_calls = []
    
    def load_corpus(self, corpus_type):
        return {'status': 'loaded', 'corpus': corpus_type}
    
    def rebuild_corpus(self, corpus_type):
        self.rebuild_calls.append(corpus_type)
        time.sleep(0.01)  # Simulate work
        return True


class TestCorpusMonitor(unittest.TestCase):
    """Test cases for the CorpusMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_loader = MockCorpusLoader()
        self.monitor = CorpusMonitor(self.mock_loader)
    
    def test_init(self):
        """Test CorpusMonitor initialization."""
        self.assertIsInstance(self.monitor, CorpusMonitor)
        self.assertEqual(self.monitor.corpus_loader, self.mock_loader)
        self.assertFalse(self.monitor.is_monitoring_active)
        self.assertEqual(self.monitor.rebuild_strategy, 'immediate')
    
    def test_set_watch_paths(self):
        """Test setting watch paths."""
        # Create temporary directories for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            vn_path = os.path.join(temp_dir, 'verbnet')
            fn_path = os.path.join(temp_dir, 'framenet')
            os.makedirs(vn_path)
            os.makedirs(fn_path)
            
            result = self.monitor.set_watch_paths(
                verbnet_path=vn_path,
                framenet_path=fn_path
            )
            
            self.assertIn('verbnet', result)
            self.assertIn('framenet', result)
            self.assertEqual(result['verbnet'], vn_path)
            self.assertEqual(result['framenet'], fn_path)
    
    def test_set_rebuild_strategy(self):
        """Test setting rebuild strategy."""
        result = self.monitor.set_rebuild_strategy('batch', 30)
        
        self.assertEqual(result['strategy'], 'batch')
        self.assertEqual(result['batch_timeout'], 30)
        self.assertEqual(self.monitor.rebuild_strategy, 'batch')
        self.assertEqual(self.monitor.batch_timeout, 30)
    
    def test_set_rebuild_strategy_invalid(self):
        """Test setting invalid rebuild strategy."""
        with self.assertRaises(ValueError):
            self.monitor.set_rebuild_strategy('invalid')
    
    def test_trigger_rebuild(self):
        """Test triggering a rebuild."""
        result = self.monitor.trigger_rebuild('verbnet', 'Test rebuild')
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result['success'])
        self.assertEqual(result['corpus_type'], 'verbnet')
        self.assertEqual(result['reason'], 'Test rebuild')
        self.assertGreater(result['duration'], 0)
        self.assertIn('verbnet', self.mock_loader.rebuild_calls)
    
    def test_batch_rebuild(self):
        """Test batch rebuild."""
        corpus_types = ['verbnet', 'framenet']
        result = self.monitor.batch_rebuild(corpus_types)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'batch_rebuild')
        self.assertEqual(result['corpus_types'], corpus_types)
        self.assertTrue(result['total_success'])
        self.assertIn('results', result)
        
        # Check that both corpora were rebuilt
        for corpus in corpus_types:
            self.assertIn(corpus, self.mock_loader.rebuild_calls)
    
    def test_is_monitoring(self):
        """Test monitoring status check."""
        self.assertFalse(self.monitor.is_monitoring())
        
        self.monitor.is_monitoring_active = True
        self.assertTrue(self.monitor.is_monitoring())
    
    def test_log_event(self):
        """Test event logging."""
        success = self.monitor.log_event('test_event', {'key': 'value'})
        
        self.assertTrue(success)
        self.assertEqual(len(self.monitor.change_log), 1)
        
        event = list(self.monitor.change_log)[0]
        self.assertEqual(event['event_type'], 'test_event')
        self.assertEqual(event['details']['key'], 'value')
        self.assertIn('timestamp', event)
    
    def test_get_change_log(self):
        """Test getting change log."""
        # Add some events
        for i in range(5):
            self.monitor.log_event(f'event_{i}', {'index': i})
        
        recent = self.monitor.get_change_log(limit=3)
        
        self.assertEqual(len(recent), 3)  # Limited to 3 as requested
        
        recent_all = self.monitor.get_change_log(limit=10)
        self.assertEqual(len(recent_all), 5)  # All events since limit is higher
    
    def test_get_rebuild_history(self):
        """Test getting rebuild history."""
        # Trigger some rebuilds
        self.monitor.trigger_rebuild('verbnet')
        self.monitor.trigger_rebuild('framenet')
        
        history = self.monitor.get_rebuild_history(limit=10)
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['corpus_type'], 'verbnet')
        self.assertEqual(history[1]['corpus_type'], 'framenet')
    
    def test_set_error_recovery_strategy(self):
        """Test setting error recovery strategy."""
        result = self.monitor.set_error_recovery_strategy(max_retries=5, retry_delay=10)
        
        self.assertEqual(result['max_retries'], 5)
        self.assertEqual(result['retry_delay'], 10)
        self.assertEqual(self.monitor.max_retries, 5)
        self.assertEqual(self.monitor.retry_delay, 10)
    
    def test_handle_file_change(self):
        """Test handling file changes."""
        # Set up a watch path first
        with tempfile.TemporaryDirectory() as temp_dir:
            vn_path = os.path.join(temp_dir, 'verbnet')
            os.makedirs(vn_path)
            self.monitor.set_watch_paths(verbnet_path=vn_path)
            
            # Test file change in watched directory
            test_file = os.path.join(vn_path, 'test.xml')
            result = self.monitor.handle_file_change(test_file, 'modify')
            
            self.assertIn('action', result)
            self.assertIn('corpus_type', result)


class TestIntegration(unittest.TestCase):
    """Integration tests for Presentation and CorpusMonitor."""
    
    def test_basic_integration(self):
        """Test that both classes can be used together."""
        presenter = Presentation()
        mock_loader = MockCorpusLoader()
        monitor = CorpusMonitor(mock_loader)
        
        # Test that they can work independently
        unique_id = presenter.generate_unique_id()
        self.assertIsInstance(unique_id, str)
        
        rebuild_result = monitor.trigger_rebuild('test')
        self.assertTrue(rebuild_result['success'])
        
        # Test that they don't interfere with each other
        colors = presenter.generate_element_colors(['ARG0', 'ARG1'])
        self.assertEqual(len(colors), 2)
        
        self.assertFalse(monitor.is_monitoring())


if __name__ == '__main__':
    unittest.main()