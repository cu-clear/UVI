"""
Command Line Interface for UVI Package

This module provides command-line tools for the UVI package, enabling
corpus validation, data export, and performance benchmarking from the
command line.

Available commands:
- uvi-validate: Validate corpus files and schemas
- uvi-export: Export corpus data in various formats
- uvi-benchmark: Run performance benchmarks
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from . import UVI, CorpusLoader, Presentation
except ImportError:
    # Handle case where running as script
    from uvi import UVI, CorpusLoader, Presentation


def validate_command():
    """Command-line tool for corpus validation."""
    parser = argparse.ArgumentParser(
        description='Validate UVI corpus files and schemas',
        prog='uvi-validate'
    )
    
    parser.add_argument(
        'corpora_path',
        help='Path to the corpora directory'
    )
    
    parser.add_argument(
        '--corpus', '-c',
        choices=['verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet', 
                'bso', 'semnet', 'reference_docs', 'vn_api'],
        help='Validate specific corpus only'
    )
    
    parser.add_argument(
        '--schema-validation', '-s',
        action='store_true',
        help='Enable XML/JSON schema validation (requires lxml)'
    )
    
    parser.add_argument(
        '--cross-references', '-x',
        action='store_true',
        help='Validate cross-corpus references'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format for validation results'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed information'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize UVI
        if args.verbose:
            print(f"Initializing UVI with corpus path: {args.corpora_path}")
        
        uvi = UVI(args.corpora_path, load_all=False)
        
        # Load specific corpus if specified
        if args.corpus:
            if args.verbose:
                print(f"Loading corpus: {args.corpus}")
            uvi._load_corpus(args.corpus)
            corpus_list = [args.corpus]
        else:
            if args.verbose:
                print("Loading all available corpora")
            uvi._load_all_corpora()
            corpus_list = list(uvi.get_loaded_corpora())
        
        # Validation results
        validation_results = {
            'corpora_path': args.corpora_path,
            'validated_corpora': corpus_list,
            'results': {}
        }
        
        # Basic corpus loading validation
        for corpus_name in corpus_list:
            corpus_result = {
                'loaded': corpus_name in uvi.loaded_corpora,
                'path_exists': Path(uvi.corpus_paths.get(corpus_name, '')).exists() if corpus_name in uvi.corpus_paths else False
            }
            
            if args.verbose and corpus_result['loaded']:
                print(f"✓ {corpus_name}: Loaded successfully")
            elif args.verbose:
                print(f"✗ {corpus_name}: Failed to load")
            
            validation_results['results'][corpus_name] = corpus_result
        
        # Schema validation if requested
        if args.schema_validation:
            if args.verbose:
                print("Performing schema validation...")
            
            try:
                if hasattr(uvi, 'validate_corpus_schemas'):
                    schema_results = uvi.validate_corpus_schemas(corpus_list)
                    for corpus_name in corpus_list:
                        if corpus_name in validation_results['results']:
                            validation_results['results'][corpus_name]['schema_valid'] = schema_results.get(corpus_name, False)
                else:
                    if args.verbose:
                        print("⚠ Schema validation method not available")
            except Exception as e:
                if args.verbose:
                    print(f"Schema validation error: {e}")
        
        # Cross-reference validation if requested
        if args.cross_references:
            if args.verbose:
                print("Validating cross-references...")
            
            try:
                if hasattr(uvi, 'check_data_integrity'):
                    integrity_results = uvi.check_data_integrity()
                    validation_results['cross_reference_integrity'] = integrity_results
                else:
                    if args.verbose:
                        print("⚠ Cross-reference validation method not available")
            except Exception as e:
                if args.verbose:
                    print(f"Cross-reference validation error: {e}")
        
        # Output results
        _output_validation_results(validation_results, args.output, args.verbose)
        
        # Exit code based on validation success
        failed_corpora = [name for name, result in validation_results['results'].items() 
                         if not result.get('loaded', False)]
        
        if failed_corpora:
            print(f"Validation failed for: {', '.join(failed_corpora)}", file=sys.stderr)
            sys.exit(1)
        else:
            if args.verbose:
                print("All validations passed!")
            sys.exit(0)
            
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)


def export_command():
    """Command-line tool for corpus data export."""
    parser = argparse.ArgumentParser(
        description='Export UVI corpus data in various formats',
        prog='uvi-export'
    )
    
    parser.add_argument(
        'corpora_path',
        help='Path to the corpora directory'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'xml', 'csv'],
        default='json',
        help='Export format (default: json)'
    )
    
    parser.add_argument(
        '--corpora', '-c',
        nargs='+',
        choices=['verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet',
                'bso', 'semnet', 'reference_docs', 'vn_api'],
        help='Specific corpora to export (default: all)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--include-mappings', '-m',
        action='store_true',
        help='Include cross-corpus mappings in export'
    )
    
    parser.add_argument(
        '--lemma',
        help='Export semantic profile for specific lemma'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print output (for JSON/XML)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize UVI
        if args.verbose:
            print(f"Initializing UVI with corpus path: {args.corpora_path}", file=sys.stderr)
        
        uvi = UVI(args.corpora_path, load_all=False)
        
        # Load specified corpora
        if args.corpora:
            for corpus in args.corpora:
                if args.verbose:
                    print(f"Loading corpus: {corpus}", file=sys.stderr)
                uvi._load_corpus(corpus)
        else:
            if args.verbose:
                print("Loading all available corpora", file=sys.stderr)
            uvi._load_all_corpora()
        
        # Perform export
        if args.lemma:
            # Export semantic profile for specific lemma
            if args.verbose:
                print(f"Exporting semantic profile for lemma: {args.lemma}", file=sys.stderr)
            
            if hasattr(uvi, 'export_semantic_profile'):
                export_data = uvi.export_semantic_profile(args.lemma, format=args.format)
            elif hasattr(uvi, 'get_complete_semantic_profile'):
                profile = uvi.get_complete_semantic_profile(args.lemma)
                if args.format == 'json':
                    export_data = json.dumps(profile, indent=2 if args.pretty else None, default=str)
                else:
                    export_data = str(profile)  # Fallback
            else:
                raise Exception("Semantic profile export not available")
        else:
            # Export corpus data
            if args.verbose:
                print(f"Exporting corpus data in {args.format} format", file=sys.stderr)
            
            if hasattr(uvi, 'export_resources'):
                export_data = uvi.export_resources(
                    include_resources=args.corpora,
                    format=args.format,
                    include_mappings=args.include_mappings
                )
            else:
                raise Exception("Export method not available")
        
        # Pretty formatting
        if args.pretty and args.format == 'json':
            try:
                parsed = json.loads(export_data)
                export_data = json.dumps(parsed, indent=2, default=str)
            except json.JSONDecodeError:
                pass  # Keep original format
        
        # Output
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(export_data)
            
            if args.verbose:
                file_size = output_path.stat().st_size
                print(f"Export saved to {output_path} ({file_size} bytes)", file=sys.stderr)
        else:
            print(export_data)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        sys.exit(1)


def benchmark_command():
    """Command-line tool for performance benchmarking."""
    parser = argparse.ArgumentParser(
        description='Run UVI performance benchmarks',
        prog='uvi-benchmark'
    )
    
    parser.add_argument(
        'corpora_path',
        help='Path to the corpora directory'
    )
    
    parser.add_argument(
        '--test', '-t',
        choices=['initialization', 'loading', 'search', 'export', 'all'],
        default='all',
        help='Specific benchmark test to run (default: all)'
    )
    
    parser.add_argument(
        '--trials', '-n',
        type=int,
        default=5,
        help='Number of trials for each test (default: 5)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for benchmark results (JSON format)'
    )
    
    parser.add_argument(
        '--memory-profiling',
        action='store_true',
        help='Include memory profiling (requires psutil)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed timing'
    )
    
    args = parser.parse_args()
    
    try:
        import time
        
        # Check for optional dependencies
        memory_available = False
        if args.memory_profiling:
            try:
                import psutil
                memory_available = True
            except ImportError:
                print("Warning: psutil not available, memory profiling disabled", file=sys.stderr)
        
        benchmark_results = {
            'corpora_path': args.corpora_path,
            'test_type': args.test,
            'trials': args.trials,
            'timestamp': time.time(),
            'results': {}
        }
        
        def get_memory_usage():
            if memory_available:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024  # MB
            return 0
        
        def run_benchmark_test(test_name, test_func, trials=None):
            if trials is None:
                trials = args.trials
                
            if args.verbose:
                print(f"Running {test_name} benchmark ({trials} trials)...", file=sys.stderr)
            
            times = []
            memory_before = get_memory_usage()
            
            for trial in range(trials):
                start_time = time.time()
                try:
                    test_func()
                    elapsed = time.time() - start_time
                    times.append(elapsed)
                    
                    if args.verbose:
                        print(f"  Trial {trial + 1}: {elapsed:.4f}s", file=sys.stderr)
                except Exception as e:
                    if args.verbose:
                        print(f"  Trial {trial + 1}: Failed - {e}", file=sys.stderr)
            
            memory_after = get_memory_usage()
            
            if times:
                result = {
                    'mean_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'successful_trials': len(times),
                    'total_trials': trials
                }
                
                if memory_available:
                    result['memory_delta_mb'] = memory_after - memory_before
                
                benchmark_results['results'][test_name] = result
                
                if args.verbose:
                    print(f"  {test_name}: {result['mean_time']:.4f}s avg", file=sys.stderr)
        
        # Define benchmark tests
        def test_initialization():
            uvi = UVI(args.corpora_path, load_all=False)
            return uvi
        
        def test_loading():
            uvi = UVI(args.corpora_path, load_all=False)
            uvi._load_corpus('verbnet')  # Load one corpus as test
        
        def test_search():
            uvi = UVI(args.corpora_path, load_all=False)
            try:
                results = uvi.search_lemmas(['run'])
            except Exception:
                pass  # Expected if not implemented
        
        def test_export():
            uvi = UVI(args.corpora_path, load_all=False)
            try:
                if hasattr(uvi, 'export_resources'):
                    export_data = uvi.export_resources(format='json')
            except Exception:
                pass  # Expected if not implemented
        
        # Run selected benchmarks
        if args.test in ['initialization', 'all']:
            run_benchmark_test('initialization', test_initialization)
        
        if args.test in ['loading', 'all']:
            run_benchmark_test('corpus_loading', test_loading)
        
        if args.test in ['search', 'all']:
            run_benchmark_test('search_operations', test_search)
        
        if args.test in ['export', 'all']:
            run_benchmark_test('export_operations', test_export)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(benchmark_results, f, indent=2)
            
            if args.verbose:
                print(f"Benchmark results saved to: {output_path}", file=sys.stderr)
        else:
            print(json.dumps(benchmark_results, indent=2))
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Benchmark error: {e}", file=sys.stderr)
        sys.exit(1)


def _output_validation_results(results: Dict[str, Any], format_type: str, verbose: bool):
    """Output validation results in specified format."""
    if format_type == 'json':
        print(json.dumps(results, indent=2))
    
    elif format_type == 'csv':
        import csv
        import sys
        
        writer = csv.writer(sys.stdout)
        writer.writerow(['Corpus', 'Loaded', 'Path Exists', 'Schema Valid'])
        
        for corpus, result in results['results'].items():
            writer.writerow([
                corpus,
                result.get('loaded', False),
                result.get('path_exists', False),
                result.get('schema_valid', 'N/A')
            ])
    
    else:  # text format
        print(f"Corpus Validation Results")
        print(f"Corpora Path: {results['corpora_path']}")
        print(f"Validated: {', '.join(results['validated_corpora'])}")
        print("-" * 50)
        
        for corpus, result in results['results'].items():
            status_symbols = []
            
            if result.get('loaded', False):
                status_symbols.append('✓ Loaded')
            else:
                status_symbols.append('✗ Not Loaded')
            
            if result.get('path_exists', False):
                status_symbols.append('✓ Path Exists')
            else:
                status_symbols.append('✗ Path Missing')
            
            if 'schema_valid' in result:
                if result['schema_valid']:
                    status_symbols.append('✓ Schema Valid')
                else:
                    status_symbols.append('✗ Schema Invalid')
            
            print(f"{corpus:<15}: {' | '.join(status_symbols)}")
        
        if 'cross_reference_integrity' in results:
            print(f"\nCross-Reference Integrity: {results['cross_reference_integrity']}")


def main():
    """Main entry point for CLI tools."""
    if len(sys.argv) < 1:
        print("Usage: Use uvi-validate, uvi-export, or uvi-benchmark commands")
        sys.exit(1)
    
    # This function can be used for testing or as a general entry point
    print("UVI CLI Tools Available:")
    print("  uvi-validate  - Validate corpus files and schemas")
    print("  uvi-export    - Export corpus data in various formats")  
    print("  uvi-benchmark - Run performance benchmarks")
    print("\nUse --help with each command for detailed options.")


if __name__ == '__main__':
    main()