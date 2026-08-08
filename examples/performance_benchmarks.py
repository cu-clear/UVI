"""
UVI Performance Benchmarking Suite

This script provides comprehensive performance testing for the UVI package,
measuring:
- Corpus loading performance with different sizes
- Search performance across different corpus types
- Memory usage patterns during operations
- Cross-corpus integration performance
- Export functionality performance
- Concurrent operation handling

Results are displayed with timing information and memory usage metrics.
"""

import sys
from pathlib import Path
import time
import psutil
import os
import gc
import json
from typing import List, Dict, Any, Callable
from contextlib import contextmanager

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI, CorpusLoader, Presentation, CorpusMonitor


class PerformanceBenchmark:
    """Performance benchmarking utilities for UVI package."""
    
    def __init__(self):
        self.results = {}
        self.start_memory = self._get_memory_usage()
        
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    @contextmanager
    def benchmark(self, test_name: str):
        """Context manager for benchmarking operations."""
        print(f"\n{'='*60}")
        print(f"BENCHMARKING: {test_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            elapsed_time = end_time - start_time
            memory_delta = {
                'rss_mb': end_memory['rss_mb'] - start_memory['rss_mb'],
                'vms_mb': end_memory['vms_mb'] - start_memory['vms_mb'],
                'percent': end_memory['percent'] - start_memory['percent']
            }
            
            result = {
                'test_name': test_name,
                'elapsed_time': elapsed_time,
                'start_memory': start_memory,
                'end_memory': end_memory,
                'memory_delta': memory_delta,
                'timestamp': time.time()
            }
            
            self.results[test_name] = result
            
            print(f"\n--- PERFORMANCE RESULTS ---")
            print(f"Elapsed Time: {elapsed_time:.3f} seconds")
            print(f"Memory Change: {memory_delta['rss_mb']:.2f} MB RSS, {memory_delta['vms_mb']:.2f} MB VMS")
            print(f"Memory Usage: {end_memory['percent']:.1f}% of system memory")
    
    def run_multiple_trials(self, func: Callable, trials: int = 5, *args, **kwargs) -> Dict[str, Any]:
        """Run a function multiple times and collect performance statistics."""
        times = []
        memory_deltas = []
        
        for trial in range(trials):
            gc.collect()  # Clean up before each trial
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f"Trial {trial + 1} failed: {e}")
                continue
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            elapsed = end_time - start_time
            memory_delta = end_memory['rss_mb'] - start_memory['rss_mb']
            
            times.append(elapsed)
            memory_deltas.append(memory_delta)
            
            print(f"Trial {trial + 1}: {elapsed:.3f}s, {memory_delta:.2f}MB")
        
        if times:
            return {
                'mean_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'mean_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'successful_trials': len(times),
                'total_trials': trials
            }
        else:
            return {'error': 'All trials failed'}
    
    def print_summary(self):
        """Print a summary of all benchmark results."""
        print(f"\n{'='*80}")
        print("PERFORMANCE BENCHMARK SUMMARY")
        print(f"{'='*80}")
        
        if not self.results:
            print("No benchmark results available.")
            return
        
        # Sort results by execution time
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['elapsed_time'])
        
        print(f"{'Test Name':<40} {'Time (s)':<12} {'Memory (MB)':<12} {'Status':<10}")
        print("-" * 80)
        
        for test_name, result in sorted_results:
            time_str = f"{result['elapsed_time']:.3f}"
            memory_str = f"{result['memory_delta']['rss_mb']:+.2f}"
            status = "✓ PASS" if result['elapsed_time'] < 30 else "⚠ SLOW"
            
            print(f"{test_name:<40} {time_str:<12} {memory_str:<12} {status:<10}")
        
        # Overall statistics
        total_time = sum(r['elapsed_time'] for r in self.results.values())
        total_memory = sum(r['memory_delta']['rss_mb'] for r in self.results.values())
        
        print("-" * 80)
        print(f"{'TOTAL':<40} {total_time:.3f}s     {total_memory:+.2f}MB")
        print(f"\nSlowest test: {max(sorted_results, key=lambda x: x[1]['elapsed_time'])[0]}")
        print(f"Fastest test: {min(sorted_results, key=lambda x: x[1]['elapsed_time'])[0]}")


def benchmark_initialization_performance():
    """Benchmark UVI initialization performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    # Test quick initialization
    with benchmark.benchmark("UVI Quick Initialization (load_all=False)"):
        for i in range(5):
            uvi = UVI(str(corpora_path), load_all=False)
            print(f"   Initialization {i+1}: ✓")
    
    # Test full initialization if corpora exist
    if corpora_path.exists():
        with benchmark.benchmark("UVI Full Initialization (load_all=True)"):
            try:
                uvi = UVI(str(corpora_path), load_all=True)
                print(f"   Full initialization: ✓ ({len(uvi.get_loaded_corpora())} corpora loaded)")
            except Exception as e:
                print(f"   Full initialization failed: {e}")
    
    # Test multiple rapid initializations
    with benchmark.benchmark("Rapid Multiple Initializations (10x)"):
        for i in range(10):
            uvi = UVI(str(corpora_path), load_all=False)
        print(f"   Created 10 UVI instances successfully")
    
    return benchmark


def benchmark_corpus_loading_performance():
    """Benchmark corpus loading and parsing performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    # Test CorpusLoader initialization
    with benchmark.benchmark("CorpusLoader Initialization"):
        loader = CorpusLoader(str(corpora_path))
        corpus_paths = loader.get_corpus_paths()
        print(f"   Detected {len(corpus_paths)} corpus paths")
    
    # Test individual corpus loading
    test_corpora = ['verbnet', 'framenet', 'wordnet', 'propbank']
    
    for corpus_name in test_corpora:
        with benchmark.benchmark(f"Load {corpus_name.title()} Corpus"):
            try:
                uvi = UVI(str(corpora_path), load_all=False)
                uvi._load_corpus(corpus_name)
                
                if corpus_name in uvi.loaded_corpora:
                    print(f"   ✓ {corpus_name} loaded successfully")
                else:
                    print(f"   ⚠ {corpus_name} not loaded (files may not exist)")
                    
            except Exception as e:
                print(f"   ✗ {corpus_name} loading failed: {e}")
    
    # Test corpus path detection performance
    def detect_paths():
        loader = CorpusLoader(str(corpora_path))
        return loader.get_corpus_paths()
    
    with benchmark.benchmark("Corpus Path Detection (Multiple Trials)"):
        stats = benchmark.run_multiple_trials(detect_paths, trials=10)
        if 'mean_time' in stats:
            print(f"   Mean detection time: {stats['mean_time']:.4f}s")
            print(f"   Range: {stats['min_time']:.4f}s - {stats['max_time']:.4f}s")
        else:
            print(f"   Detection failed: {stats}")
    
    return benchmark


def benchmark_search_performance():
    """Benchmark search and query performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    uvi = UVI(str(corpora_path), load_all=False)
    
    # Test basic search operations
    search_terms = ['run', 'walk', 'eat', 'think', 'break', 'give', 'take', 'move', 'see', 'hear']
    
    with benchmark.benchmark("Lemma Search Performance (10 terms)"):
        successful_searches = 0
        for term in search_terms:
            try:
                results = uvi.search_lemmas([term])
                successful_searches += 1
            except Exception as e:
                pass  # Expected for unimplemented methods
        
        print(f"   Successful searches: {successful_searches}/{len(search_terms)}")
    
    # Test single search with multiple trials
    def search_single_term(term='run'):
        try:
            return uvi.search_lemmas([term])
        except Exception:
            return None
    
    with benchmark.benchmark("Single Lemma Search (Multiple Trials)"):
        stats = benchmark.run_multiple_trials(search_single_term, trials=20, term='run')
        if 'mean_time' in stats:
            print(f"   Mean search time: {stats['mean_time']:.4f}s")
            print(f"   Successful trials: {stats['successful_trials']}/{stats['total_trials']}")
    
    # Test different search logic types
    search_logics = ['or', 'and']
    
    for logic in search_logics:
        with benchmark.benchmark(f"Multi-term Search ({logic.upper()} logic)"):
            try:
                results = uvi.search_lemmas(['run', 'walk', 'move'], logic=logic)
                print(f"   ✓ {logic.upper()} search completed")
            except Exception as e:
                print(f"   {logic.upper()} search: {e}")
    
    return benchmark


def benchmark_corpus_specific_retrieval():
    """Benchmark corpus-specific data retrieval performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    uvi = UVI(str(corpora_path), load_all=False)
    
    # Test VerbNet retrieval
    with benchmark.benchmark("VerbNet Class Retrieval"):
        test_classes = ['run-51.3.2', 'walk-51.3.2', 'eat-39.1', 'think-29.9']
        successful = 0
        for class_id in test_classes:
            try:
                result = uvi.get_verbnet_class(class_id)
                successful += 1
            except Exception:
                pass
        print(f"   Successful retrievals: {successful}/{len(test_classes)}")
    
    # Test FrameNet retrieval
    with benchmark.benchmark("FrameNet Frame Retrieval"):
        test_frames = ['Motion', 'Ingestion', 'Cogitation', 'Perception_active']
        successful = 0
        for frame in test_frames:
            try:
                result = uvi.get_framenet_frame(frame)
                successful += 1
            except Exception:
                pass
        print(f"   Successful retrievals: {successful}/{len(test_frames)}")
    
    # Test PropBank retrieval
    with benchmark.benchmark("PropBank Frame Retrieval"):
        test_lemmas = ['run', 'walk', 'eat', 'think']
        successful = 0
        for lemma in test_lemmas:
            try:
                result = uvi.get_propbank_frame(lemma)
                successful += 1
            except Exception:
                pass
        print(f"   Successful retrievals: {successful}/{len(test_lemmas)}")
    
    # Test WordNet retrieval
    with benchmark.benchmark("WordNet Synsets Retrieval"):
        test_words = ['run', 'walk', 'eat', 'think']
        successful = 0
        for word in test_words:
            try:
                result = uvi.get_wordnet_synsets(word, pos='v')
                successful += 1
            except Exception:
                pass
        print(f"   Successful retrievals: {successful}/{len(test_words)}")
    
    return benchmark


def benchmark_reference_data_access():
    """Benchmark reference data access performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    uvi = UVI(str(corpora_path), load_all=False)
    
    reference_methods = [
        'get_references',
        'get_themrole_references', 
        'get_predicate_references',
        'get_verb_specific_features',
        'get_syntactic_restrictions',
        'get_selectional_restrictions'
    ]
    
    for method_name in reference_methods:
        with benchmark.benchmark(f"Reference Data: {method_name}"):
            try:
                if hasattr(uvi, method_name):
                    method = getattr(uvi, method_name)
                    result = method()
                    
                    result_info = f"type: {type(result)}"
                    if isinstance(result, (list, dict)):
                        result_info += f", length: {len(result)}"
                    
                    print(f"   ✓ {method_name}: {result_info}")
                else:
                    print(f"   ⚠ {method_name}: Method not available")
                    
            except Exception as e:
                print(f"   ✗ {method_name}: {e}")
    
    return benchmark


def benchmark_class_hierarchy_performance():
    """Benchmark class hierarchy operations."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    uvi = UVI(str(corpora_path), load_all=False)
    
    hierarchy_methods = [
        ('get_class_hierarchy_by_name', None),
        ('get_class_hierarchy_by_id', None),
        ('get_full_class_hierarchy', 'run-51.3.2'),
        ('get_subclass_ids', 'run-51.3.2'),
        ('get_member_classes', 'run')
    ]
    
    for method_name, param in hierarchy_methods:
        with benchmark.benchmark(f"Class Hierarchy: {method_name}"):
            try:
                if hasattr(uvi, method_name):
                    method = getattr(uvi, method_name)
                    
                    if param is not None:
                        result = method(param)
                    else:
                        result = method()
                    
                    result_info = f"type: {type(result)}"
                    if isinstance(result, (list, dict)):
                        result_info += f", length: {len(result)}"
                    
                    print(f"   ✓ {method_name}: {result_info}")
                else:
                    print(f"   ⚠ {method_name}: Method not available")
                    
            except Exception as e:
                print(f"   ✗ {method_name}: {e}")
    
    return benchmark


def benchmark_presentation_performance():
    """Benchmark Presentation class performance."""
    benchmark = PerformanceBenchmark()
    
    presentation = Presentation()
    
    # Test unique ID generation performance
    with benchmark.benchmark("Unique ID Generation (1000 IDs)"):
        ids = []
        for i in range(1000):
            uid = presentation.generate_unique_id()
            ids.append(uid)
        
        # Check uniqueness
        unique_ids = set(ids)
        print(f"   Generated 1000 IDs, {len(unique_ids)} unique")
    
    # Test color generation performance
    with benchmark.benchmark("Element Color Generation"):
        large_element_list = [f"element_{i}" for i in range(100)]
        colors = presentation.generate_element_colors(large_element_list)
        print(f"   Generated colors for {len(colors)} elements")
    
    # Test data formatting performance
    with benchmark.benchmark("JSON Display Formatting"):
        test_data = {
            f"key_{i}": f"value_{i}" for i in range(1000)
        }
        test_data.update({f"_internal_{i}": f"hidden_{i}" for i in range(100)})
        
        # Test strip_object_ids
        cleaned_data = presentation.strip_object_ids(test_data)
        
        # Test json_to_display
        display_json = presentation.json_to_display(cleaned_data)
        
        print(f"   Processed {len(test_data)} keys -> {len(cleaned_data)} cleaned")
        print(f"   JSON output: {len(display_json)} characters")
    
    return benchmark


def benchmark_export_performance():
    """Benchmark data export performance."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    uvi = UVI(str(corpora_path), load_all=False)
    
    export_formats = ['json', 'xml', 'csv']
    
    for format_type in export_formats:
        with benchmark.benchmark(f"Export Performance ({format_type.upper()})"):
            try:
                if hasattr(uvi, 'export_resources'):
                    export_result = uvi.export_resources(format=format_type)
                    print(f"   ✓ Export {format_type}: {len(export_result)} characters")
                else:
                    print(f"   ⚠ Export method not available")
                    
            except Exception as e:
                print(f"   ✗ Export {format_type}: {e}")
    
    # Test semantic profile export
    with benchmark.benchmark("Semantic Profile Export"):
        try:
            if hasattr(uvi, 'export_semantic_profile'):
                profile = uvi.export_semantic_profile('run', format='json')
                print(f"   ✓ Profile export: {len(profile)} characters")
            else:
                print(f"   ⚠ Profile export method not available")
                
        except Exception as e:
            print(f"   ✗ Profile export: {e}")
    
    return benchmark


def benchmark_memory_usage_patterns():
    """Benchmark memory usage patterns during various operations."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    # Test memory usage with multiple UVI instances
    with benchmark.benchmark("Memory Usage: Multiple UVI Instances"):
        instances = []
        for i in range(10):
            uvi = UVI(str(corpora_path), load_all=False)
            instances.append(uvi)
        
        print(f"   Created {len(instances)} UVI instances")
        
        # Force garbage collection
        del instances
        gc.collect()
        print("   Cleaned up instances")
    
    # Test memory usage during searches
    with benchmark.benchmark("Memory Usage: Repeated Searches"):
        uvi = UVI(str(corpora_path), load_all=False)
        
        for i in range(100):
            try:
                results = uvi.search_lemmas([f'term_{i % 10}'])
            except Exception:
                pass  # Expected for unimplemented methods
        
        print("   Performed 100 search operations")
    
    # Test memory usage with presentation operations
    with benchmark.benchmark("Memory Usage: Presentation Operations"):
        presentation = Presentation()
        
        # Generate many colors and IDs
        for i in range(100):
            elements = [f"elem_{j}" for j in range(i, i+50)]
            colors = presentation.generate_element_colors(elements)
            ids = [presentation.generate_unique_id() for _ in range(50)]
        
        print("   Performed 100 presentation operations")
    
    return benchmark


def benchmark_concurrent_operations():
    """Benchmark concurrent-like operations (simulate with rapid sequential calls)."""
    benchmark = PerformanceBenchmark()
    corpora_path = Path(__file__).parent.parent / 'corpora'
    
    # Test rapid sequential operations
    with benchmark.benchmark("Concurrent-like Operations: Rapid Sequential"):
        uvi = UVI(str(corpora_path), load_all=False)
        presentation = Presentation()
        
        operations_completed = 0
        
        for i in range(50):
            try:
                # Mix different operation types
                if i % 4 == 0:
                    result = uvi.get_loaded_corpora()
                elif i % 4 == 1:
                    result = presentation.generate_unique_id()
                elif i % 4 == 2:
                    result = uvi.get_corpus_paths()
                else:
                    result = presentation.generate_element_colors([f'elem_{i}'])
                
                operations_completed += 1
                
            except Exception as e:
                pass  # Some operations may fail
        
        print(f"   Completed {operations_completed}/50 operations")
    
    # Test stability under load
    with benchmark.benchmark("Stability Under Load"):
        instances = []
        operations = 0
        
        try:
            for i in range(20):
                uvi = UVI(str(corpora_path), load_all=False)
                instances.append(uvi)
                
                # Perform operations on each instance
                for j in range(5):
                    try:
                        corpus_paths = uvi.get_corpus_paths()
                        loaded = uvi.get_loaded_corpora()
                        operations += 2
                    except Exception:
                        pass
            
            print(f"   Created {len(instances)} instances, {operations} operations")
            
        finally:
            del instances
            gc.collect()
    
    return benchmark


def main():
    """Run comprehensive performance benchmarks."""
    print("UVI Package Performance Benchmarking Suite")
    print("This suite measures performance across all major UVI components.")
    print("\nWARNING: This may take several minutes to complete.")
    
    input("\nPress Enter to start benchmarking...")
    
    all_benchmarks = []
    
    try:
        print("\n🚀 Starting Performance Benchmarks...")
        
        # Run all benchmark suites
        all_benchmarks.append(benchmark_initialization_performance())
        all_benchmarks.append(benchmark_corpus_loading_performance())
        all_benchmarks.append(benchmark_search_performance())
        all_benchmarks.append(benchmark_corpus_specific_retrieval())
        all_benchmarks.append(benchmark_reference_data_access())
        all_benchmarks.append(benchmark_class_hierarchy_performance())
        all_benchmarks.append(benchmark_presentation_performance())
        all_benchmarks.append(benchmark_export_performance())
        all_benchmarks.append(benchmark_memory_usage_patterns())
        all_benchmarks.append(benchmark_concurrent_operations())
        
        # Print comprehensive summary
        print(f"\n{'='*80}")
        print("COMPREHENSIVE PERFORMANCE SUMMARY")
        print(f"{'='*80}")
        
        total_tests = 0
        total_time = 0
        total_memory = 0
        
        for i, benchmark in enumerate(all_benchmarks, 1):
            print(f"\n--- Benchmark Suite {i} ---")
            benchmark.print_summary()
            
            suite_tests = len(benchmark.results)
            suite_time = sum(r['elapsed_time'] for r in benchmark.results.values())
            suite_memory = sum(r['memory_delta']['rss_mb'] for r in benchmark.results.values())
            
            total_tests += suite_tests
            total_time += suite_time
            total_memory += suite_memory
        
        print(f"\n{'='*80}")
        print("OVERALL SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"Total Time: {total_time:.3f} seconds ({total_time/60:.1f} minutes)")
        print(f"Total Memory Change: {total_memory:+.2f} MB")
        print(f"Average Time per Test: {total_time/total_tests:.3f} seconds")
        
        # Performance grade
        avg_time = total_time / total_tests if total_tests > 0 else 0
        if avg_time < 0.1:
            grade = "A+ (Excellent)"
        elif avg_time < 0.5:
            grade = "A (Very Good)"
        elif avg_time < 1.0:
            grade = "B (Good)"
        elif avg_time < 2.0:
            grade = "C (Fair)"
        else:
            grade = "D (Needs Optimization)"
        
        print(f"Performance Grade: {grade}")
        
        # Save results to file
        results_file = Path(__file__).parent / 'benchmark_results.json'
        all_results = {}
        for benchmark in all_benchmarks:
            all_results.update(benchmark.results)
        
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'total_time': total_time,
                    'total_memory_change': total_memory,
                    'average_time_per_test': avg_time,
                    'performance_grade': grade,
                    'timestamp': time.time()
                },
                'detailed_results': all_results
            }, f, indent=2)
        
        print(f"\n📊 Detailed results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print("\n⚠ Benchmarking interrupted by user.")
    except Exception as e:
        print(f"\n❌ Benchmarking failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Benchmarking completed.")


if __name__ == '__main__':
    main()