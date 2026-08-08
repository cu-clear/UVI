"""
AnalyticsManager Helper Class

Centralized analytics and corpus collection information management using 
CorpusCollectionAnalyzer integration. Provides comprehensive analytics capabilities
not available in base UVI while eliminating duplicate statistics calculations.

This class centralizes analytics operations through CorpusCollectionAnalyzer
and provides enhanced corpus information management.
"""

from typing import Dict, List, Optional, Union, Any
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionAnalyzer


class AnalyticsManager(BaseHelper):
    """
    Centralized analytics and corpus collection information management.
    
    Provides comprehensive analytics capabilities through direct CorpusCollectionAnalyzer
    integration, eliminating duplicate statistics calculations scattered across UVI methods.
    This class centralizes analytics operations and provides enhanced corpus analysis.
    
    Key Features:
    - Enhanced corpus info with CorpusCollectionAnalyzer statistics integration
    - Collection-wide statistics and metrics
    - Build and load metadata information with analytics context
    - Lemma coverage analysis across corpora
    - Comprehensive analytics reports
    - Collection size comparisons and growth tracking
    - Corpus health analysis and recommendations
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize AnalyticsManager with CorpusCollectionAnalyzer integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Direct integration with CorpusCollectionAnalyzer for all analytics operations
        self.analyzer = CorpusCollectionAnalyzer(
            uvi_instance.corpora_data,
            getattr(uvi_instance.corpus_loader, 'load_status', {}),
            getattr(uvi_instance.corpus_loader, 'build_metadata', {}),
            getattr(uvi_instance.corpus_loader, 'reference_collections', {}),
            getattr(uvi_instance, 'corpus_paths', {})
        )
        
        # Analytics cache for performance
        self._analytics_cache = {}
        self._cache_expiry = {}
        
    def get_corpus_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced corpus info with CorpusCollectionAnalyzer statistics integration.
        
        Replaces UVI method (lines 178-192) with CorpusCollectionAnalyzer-enhanced analytics.
        Eliminates duplicate statistics calculation and provides comprehensive corpus analysis.
        
        Returns:
            Dict[str, Dict[str, Any]]: Enhanced corpus information with analytics
        """
        # Get base corpus information
        corpus_info = {}
        supported_corpora = getattr(self.uvi, 'supported_corpora', list(self.loaded_corpora))
        
        for corpus_name in supported_corpora:
            corpus_info[corpus_name] = {
                'path': str(self.uvi.corpus_paths.get(corpus_name, 'Not found')),
                'loaded': corpus_name in self.loaded_corpora,
                'data_available': corpus_name in self.corpora_data and bool(self.corpora_data[corpus_name])
            }
        
        # Enhance with CorpusCollectionAnalyzer statistics
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            build_metadata = self.analyzer.get_build_metadata()
            
            for corpus_name in corpus_info.keys():
                if corpus_name in collection_stats:
                    corpus_info[corpus_name].update({
                        'collection_statistics': collection_stats[corpus_name],
                        'load_status': build_metadata.get('load_status', {}).get(corpus_name, 'unknown'),
                        'last_build_time': build_metadata.get('build_metadata', {}).get(f'{corpus_name}_last_build', 'unknown'),
                        'analytics_available': True
                    })
                    
                    # Add corpus-specific metrics
                    corpus_info[corpus_name]['metrics'] = self._calculate_corpus_metrics(corpus_name, collection_stats[corpus_name])
                else:
                    corpus_info[corpus_name]['analytics_available'] = False
                    
        except Exception as e:
            self.logger.warning(f"Could not enhance corpus info with analytics: {e}")
            
        # Add overall collection summary
        corpus_info['_collection_summary'] = self._build_collection_summary(corpus_info, supported_corpora)
        
        return corpus_info
        
    def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Delegate to CorpusCollectionAnalyzer with additional context.
        
        Returns:
            Dict[str, Any]: Collection statistics with contextual information
        """
        try:
            base_stats = self.analyzer.get_collection_statistics()
            
            # Add contextual information
            enhanced_stats = {
                **base_stats,
                'statistics_metadata': {
                    'generated_at': self.analyzer.get_build_metadata().get('timestamp', self._get_timestamp()),
                    'analysis_version': '1.0',
                    'total_collections_analyzed': len([k for k in base_stats.keys() if k != 'reference_collections']),
                    'analytics_capabilities': self._get_analytics_capabilities()
                }
            }
            
            return enhanced_stats
            
        except Exception as e:
            self.logger.error(f"Failed to get collection statistics: {e}")
            return {
                'error': str(e),
                'statistics_metadata': {
                    'generated_at': self._get_timestamp(),
                    'status': 'error'
                }
            }
            
    def get_build_metadata(self) -> Dict[str, Any]:
        """
        Enhanced build metadata with additional analytics context.
        
        Returns:
            Dict[str, Any]: Build metadata with analytics context
        """
        try:
            base_metadata = self.analyzer.get_build_metadata()
            
            # Add analytics-specific metadata
            enhanced_metadata = {
                **base_metadata,
                'analytics_context': {
                    'available_analytics_methods': [
                        'get_corpus_info', 'get_collection_statistics', 'analyze_corpus_coverage',
                        'generate_analytics_report', 'compare_collection_sizes', 'track_collection_growth'
                    ],
                    'supported_corpus_types': list(self.analyzer._CORPUS_COLLECTION_FIELDS.keys()) if hasattr(self.analyzer, '_CORPUS_COLLECTION_FIELDS') else [],
                    'analysis_capabilities': {
                        'collection_size_calculation': True,
                        'corpus_statistics_extraction': True,
                        'build_metadata_tracking': True,
                        'reference_collection_analysis': True,
                        'error_handling': True,
                        'cross_corpus_analysis': True
                    }
                }
            }
            
            return enhanced_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get build metadata: {e}")
            return {
                'error': str(e),
                'analytics_context': {
                    'status': 'error',
                    'generated_at': self._get_timestamp()
                }
            }
            
    def analyze_corpus_coverage(self, lemma: str) -> Dict[str, Any]:
        """
        Analyze lemma coverage across all corpora using CorpusCollectionAnalyzer context.
        
        Args:
            lemma (str): Lemma to analyze coverage for
            
        Returns:
            Dict[str, Any]: Comprehensive coverage analysis
        """
        coverage_analysis = {
            'target_lemma': lemma,
            'analysis_timestamp': self._get_timestamp(),
            'analysis_method': 'CorpusCollectionAnalyzer_enhanced',
            'corpus_coverage': {},
            'coverage_summary': {}
        }
        
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            
            for corpus_name in self.loaded_corpora:
                if corpus_name in self.corpora_data:
                    # Check lemma presence in corpus
                    lemma_found, match_details = self._check_lemma_in_corpus_detailed(lemma, corpus_name)
                    corpus_stats = collection_stats.get(corpus_name, {})
                    
                    coverage_analysis['corpus_coverage'][corpus_name] = {
                        'lemma_present': lemma_found,
                        'match_details': match_details,
                        'corpus_size': self._get_collection_size(corpus_stats),
                        'corpus_statistics': corpus_stats,
                        'coverage_percentage': self._calculate_lemma_corpus_coverage(match_details, corpus_stats)
                    }
                    
        except Exception as e:
            coverage_analysis['error'] = str(e)
            self.logger.error(f"Coverage analysis failed: {e}")
            
        # Calculate overall coverage summary
        coverage_analysis['coverage_summary'] = self._build_coverage_summary(coverage_analysis['corpus_coverage'])
        
        return coverage_analysis
        
    def generate_analytics_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report using CorpusCollectionAnalyzer.
        
        Returns:
            Dict[str, Any]: Comprehensive analytics report
        """
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            build_metadata = self.analyzer.get_build_metadata()
            
            report = {
                'report_metadata': {
                    'generated_at': self._get_timestamp(),
                    'report_type': 'comprehensive_analytics',
                    'analyzer_version': 'CorpusCollectionAnalyzer_1.0',
                    'report_sections': [
                        'collection_statistics', 'build_metadata', 'corpus_health',
                        'size_comparisons', 'reference_analysis', 'recommendations'
                    ]
                },
                'collection_statistics': collection_stats,
                'build_and_load_metadata': build_metadata,
                'corpus_health_analysis': self._analyze_corpus_health(collection_stats),
                'collection_size_comparisons': self._compare_collection_sizes(collection_stats),
                'reference_collection_analysis': self._analyze_reference_collections(collection_stats),
                'performance_metrics': self._calculate_performance_metrics(collection_stats, build_metadata),
                'recommendations': self._generate_analytics_recommendations(collection_stats, build_metadata)
            }
            
            # Add overall assessment
            report['overall_assessment'] = self._generate_overall_assessment(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Analytics report generation failed: {e}")
            return {
                'report_error': True,
                'error_message': str(e),
                'generated_at': self._get_timestamp(),
                'partial_data_available': False
            }
            
    def compare_collection_sizes(self) -> Dict[str, Any]:
        """
        Compare sizes across different collections with detailed analysis.
        
        Returns:
            Dict[str, Any]: Collection size comparison analysis
        """
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            
            size_comparison = {
                'comparison_timestamp': self._get_timestamp(),
                'comparison_method': 'CorpusCollectionAnalyzer',
                'size_analysis': {},
                'ranking': [],
                'size_distribution': {}
            }
            
            # Calculate sizes for each corpus
            corpus_sizes = {}
            for corpus_name, stats in collection_stats.items():
                if corpus_name != 'reference_collections':
                    size = self._get_collection_size(stats)
                    corpus_sizes[corpus_name] = size
                    
                    size_comparison['size_analysis'][corpus_name] = {
                        'total_items': size,
                        'size_category': self._categorize_collection_size(size),
                        'statistics': stats
                    }
                    
            # Create ranking
            size_comparison['ranking'] = sorted(
                corpus_sizes.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Analyze size distribution
            sizes = list(corpus_sizes.values())
            if sizes:
                size_comparison['size_distribution'] = {
                    'total_items': sum(sizes),
                    'largest_collection': max(sizes),
                    'smallest_collection': min(sizes),
                    'average_size': sum(sizes) / len(sizes),
                    'size_variance': self._calculate_variance(sizes),
                    'size_balance_score': self._calculate_balance_score(sizes)
                }
                
            return size_comparison
            
        except Exception as e:
            self.logger.error(f"Collection size comparison failed: {e}")
            return {
                'comparison_error': True,
                'error_message': str(e),
                'comparison_timestamp': self._get_timestamp()
            }
            
    def track_collection_growth(self, historical_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Track collection growth over time (requires historical data).
        
        Args:
            historical_data (Optional[Dict]): Historical collection statistics
            
        Returns:
            Dict[str, Any]: Collection growth analysis
        """
        growth_tracking = {
            'tracking_timestamp': self._get_timestamp(),
            'tracking_method': 'comparative_analysis',
            'historical_data_available': historical_data is not None,
            'growth_analysis': {}
        }
        
        if not historical_data:
            growth_tracking.update({
                'message': 'Historical data required for growth tracking',
                'current_snapshot': self._create_growth_snapshot(),
                'recommendation': 'Save current data as baseline for future growth tracking'
            })
            return growth_tracking
            
        try:
            current_stats = self.analyzer.get_collection_statistics()
            
            # Compare current stats with historical data
            for corpus_name in current_stats.keys():
                if corpus_name == 'reference_collections':
                    continue
                    
                current_size = self._get_collection_size(current_stats[corpus_name])
                historical_size = historical_data.get(corpus_name, {}).get('size', 0)
                
                if historical_size > 0:
                    growth_rate = ((current_size - historical_size) / historical_size) * 100
                    growth_analysis = {
                        'current_size': current_size,
                        'historical_size': historical_size,
                        'absolute_growth': current_size - historical_size,
                        'growth_rate_percentage': growth_rate,
                        'growth_category': self._categorize_growth_rate(growth_rate)
                    }
                else:
                    growth_analysis = {
                        'current_size': current_size,
                        'historical_size': historical_size,
                        'status': 'new_collection' if current_size > 0 else 'no_change'
                    }
                    
                growth_tracking['growth_analysis'][corpus_name] = growth_analysis
                
            # Overall growth summary
            growth_tracking['growth_summary'] = self._summarize_growth(growth_tracking['growth_analysis'])
            
        except Exception as e:
            growth_tracking['error'] = str(e)
            self.logger.error(f"Growth tracking failed: {e}")
            
        return growth_tracking
    
    # Private helper methods
    
    def _calculate_corpus_metrics(self, corpus_name: str, corpus_stats: Dict) -> Dict[str, Any]:
        """Calculate corpus-specific metrics based on corpus type."""
        metrics = {
            'corpus_type': corpus_name,
            'data_available': bool(corpus_stats)
        }
        
        if corpus_name == 'verbnet' and 'classes' in corpus_stats:
            metrics.update({
                'total_classes': corpus_stats['classes'],
                'total_members': corpus_stats.get('members', 0),
                'average_members_per_class': self._calculate_average_members_per_class(corpus_name)
            })
        elif corpus_name == 'framenet' and 'frames' in corpus_stats:
            metrics.update({
                'total_frames': corpus_stats['frames'],
                'total_lexical_units': corpus_stats.get('lexical_units', 0),
                'average_units_per_frame': self._calculate_average_units_per_frame(corpus_name)
            })
        elif corpus_name == 'propbank' and 'predicates' in corpus_stats:
            metrics.update({
                'total_predicates': corpus_stats['predicates'],
                'total_rolesets': corpus_stats.get('rolesets', 0),
                'average_rolesets_per_predicate': self._calculate_average_rolesets_per_predicate(corpus_name)
            })
        else:
            # Generic metrics
            metrics.update({
                'total_items': self._get_collection_size(corpus_stats),
                'data_structure': list(corpus_stats.keys()) if isinstance(corpus_stats, dict) else []
            })
            
        return metrics
        
    def _build_collection_summary(self, corpus_info: Dict, supported_corpora: List[str]) -> Dict[str, Any]:
        """Build overall collection summary."""
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            
            summary = {
                'total_supported_corpora': len(supported_corpora),
                'total_loaded_corpora': len(self.loaded_corpora),
                'load_completion_percentage': (len(self.loaded_corpora) / len(supported_corpora) * 100) if supported_corpora else 0,
                'reference_collections': collection_stats.get('reference_collections', {}),
                'total_collection_items': sum(
                    self._get_collection_size(stats) 
                    for stats in collection_stats.values() 
                    if isinstance(stats, dict) and stats != collection_stats.get('reference_collections', {})
                ),
                'analytics_summary': {
                    'analytics_enabled': True,
                    'analyzer_version': 'CorpusCollectionAnalyzer_1.0',
                    'last_analysis': self._get_timestamp()
                }
            }
            
        except Exception as e:
            summary = {
                'total_supported_corpora': len(supported_corpora),
                'total_loaded_corpora': len(self.loaded_corpora),
                'analytics_error': str(e)
            }
            
        return summary
        
    def _get_analytics_capabilities(self) -> List[str]:
        """Get list of analytics capabilities."""
        return [
            'collection_size_calculation',
            'corpus_statistics_extraction', 
            'build_metadata_tracking',
            'reference_collection_analysis',
            'cross_corpus_analysis',
            'lemma_coverage_analysis',
            'corpus_health_assessment',
            'growth_tracking',
            'performance_metrics'
        ]
        
    def _check_lemma_in_corpus_detailed(self, lemma: str, corpus_name: str) -> tuple:
        """Check lemma presence in corpus with detailed match information."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return False, {}
            
        lemma_lower = lemma.lower()
        match_details = {
            'corpus': corpus_name,
            'lemma': lemma,
            'matches': [],
            'match_types': set(),
            'total_matches': 0
        }
        
        # Corpus-specific lemma search
        if corpus_name == 'verbnet':
            matches = self._find_verbnet_lemma_matches(lemma_lower, corpus_data)
        elif corpus_name == 'framenet':
            matches = self._find_framenet_lemma_matches(lemma_lower, corpus_data)
        elif corpus_name == 'propbank':
            matches = self._find_propbank_lemma_matches(lemma_lower, corpus_data)
        else:
            matches = self._find_generic_lemma_matches(lemma_lower, corpus_data, corpus_name)
            
        match_details['matches'] = matches
        match_details['total_matches'] = len(matches)
        match_details['match_types'] = set(match.get('match_type', 'unknown') for match in matches)
        
        return len(matches) > 0, match_details
        
    def _find_verbnet_lemma_matches(self, lemma: str, verbnet_data: Dict) -> List[Dict]:
        """Find lemma matches in VerbNet data."""
        matches = []
        classes = verbnet_data.get('classes', {})
        
        for class_id, class_data in classes.items():
            members = class_data.get('members', [])
            for member in members:
                if isinstance(member, str) and lemma in member.lower():
                    matches.append({
                        'class_id': class_id,
                        'member': member,
                        'match_type': 'member',
                        'exact_match': lemma == member.lower()
                    })
                    
        return matches
        
    def _find_framenet_lemma_matches(self, lemma: str, framenet_data: Dict) -> List[Dict]:
        """Find lemma matches in FrameNet data."""
        matches = []
        frames = framenet_data.get('frames', {})
        
        for frame_name, frame_data in frames.items():
            lexical_units = frame_data.get('lexical_units', [])
            for lu in lexical_units:
                lu_name = lu.get('name', '') if isinstance(lu, dict) else str(lu)
                if lemma in lu_name.lower():
                    matches.append({
                        'frame_name': frame_name,
                        'lexical_unit': lu_name,
                        'match_type': 'lexical_unit',
                        'exact_match': lemma == lu_name.lower()
                    })
                    
        return matches
        
    def _find_propbank_lemma_matches(self, lemma: str, propbank_data: Dict) -> List[Dict]:
        """Find lemma matches in PropBank data."""
        matches = []
        predicates = propbank_data.get('predicates', {})
        
        if lemma in predicates:
            matches.append({
                'predicate': lemma,
                'match_type': 'direct',
                'exact_match': True
            })
            
        # Also search in roleset examples or other fields
        for pred_lemma, pred_data in predicates.items():
            if lemma in pred_lemma.lower() and lemma != pred_lemma.lower():
                matches.append({
                    'predicate': pred_lemma,
                    'match_type': 'partial',
                    'exact_match': False
                })
                
        return matches
        
    def _find_generic_lemma_matches(self, lemma: str, corpus_data: Dict, corpus_name: str) -> List[Dict]:
        """Find lemma matches in generic corpus data."""
        matches = []
        
        # Simple text search through corpus data
        self._search_text_recursive(lemma, corpus_data, matches, corpus_name, max_depth=3)
        
        return matches[:10]  # Limit to prevent excessive matches
        
    def _search_text_recursive(self, lemma: str, data: Any, matches: List, context: str, depth: int = 0, max_depth: int = 3):
        """Recursively search for lemma in data structure."""
        if depth > max_depth:
            return
            
        if isinstance(data, str) and lemma in data.lower():
            matches.append({
                'context': context,
                'match_text': data[:100],  # Truncate long matches
                'match_type': 'text',
                'exact_match': lemma == data.lower()
            })
        elif isinstance(data, dict):
            for key, value in data.items():
                self._search_text_recursive(lemma, value, matches, f"{context}.{key}", depth + 1, max_depth)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if len(matches) > 20:  # Prevent excessive matches
                    break
                self._search_text_recursive(lemma, item, matches, f"{context}[{i}]", depth + 1, max_depth)
                
    def _get_collection_size(self, corpus_stats: Dict) -> int:
        """Get collection size using CorpusCollectionAnalyzer logic."""
        if not corpus_stats or not isinstance(corpus_stats, dict):
            return 0
            
        # Try common size indicators
        size_fields = ['classes', 'frames', 'predicates', 'entries', 'synsets', 'total', 'size', 'count']
        
        for field in size_fields:
            if field in corpus_stats and isinstance(corpus_stats[field], int):
                return corpus_stats[field]
                
        # Count dictionary items if available
        for field, value in corpus_stats.items():
            if isinstance(value, dict):
                return len(value)
            elif isinstance(value, list):
                return len(value)
                
        return 0
        
    def _calculate_lemma_corpus_coverage(self, match_details: Dict, corpus_stats: Dict) -> float:
        """Calculate what percentage of the corpus the lemma appears in."""
        total_matches = match_details.get('total_matches', 0)
        corpus_size = self._get_collection_size(corpus_stats)
        
        if corpus_size > 0:
            return (total_matches / corpus_size) * 100
        return 0.0
        
    def _build_coverage_summary(self, corpus_coverage: Dict) -> Dict[str, Any]:
        """Build coverage summary from individual corpus coverage analyses."""
        summary = {
            'total_corpora_checked': len(corpus_coverage),
            'corpora_containing_lemma': 0,
            'total_matches_across_corpora': 0,
            'coverage_by_corpus': {},
            'best_coverage_corpus': None,
            'match_type_distribution': {}
        }
        
        best_coverage = 0.0
        match_types = {}
        
        for corpus_name, coverage_info in corpus_coverage.items():
            if coverage_info.get('lemma_present', False):
                summary['corpora_containing_lemma'] += 1
                
            total_matches = coverage_info.get('match_details', {}).get('total_matches', 0)
            summary['total_matches_across_corpora'] += total_matches
            
            coverage_pct = coverage_info.get('coverage_percentage', 0)
            summary['coverage_by_corpus'][corpus_name] = coverage_pct
            
            if coverage_pct > best_coverage:
                best_coverage = coverage_pct
                summary['best_coverage_corpus'] = corpus_name
                
            # Aggregate match types
            match_types_set = coverage_info.get('match_details', {}).get('match_types', set())
            for match_type in match_types_set:
                match_types[match_type] = match_types.get(match_type, 0) + 1
                
        summary['coverage_percentage'] = (
            summary['corpora_containing_lemma'] / summary['total_corpora_checked'] * 100
            if summary['total_corpora_checked'] > 0 else 0
        )
        summary['match_type_distribution'] = match_types
        
        return summary
        
    def _analyze_corpus_health(self, collection_stats: Dict) -> Dict[str, Any]:
        """Analyze overall corpus health from collection statistics."""
        health_analysis = {
            'overall_health_score': 0.0,
            'health_by_corpus': {},
            'health_factors': {},
            'recommendations': []
        }
        
        corpus_scores = []
        
        for corpus_name, stats in collection_stats.items():
            if corpus_name == 'reference_collections':
                continue
                
            corpus_health = self._assess_corpus_health(corpus_name, stats)
            health_analysis['health_by_corpus'][corpus_name] = corpus_health
            corpus_scores.append(corpus_health['health_score'])
            
        if corpus_scores:
            health_analysis['overall_health_score'] = sum(corpus_scores) / len(corpus_scores)
            
        # Analyze health factors
        health_analysis['health_factors'] = {
            'data_completeness': self._assess_data_completeness(collection_stats),
            'collection_balance': self._assess_collection_balance(collection_stats),
            'reference_health': self._assess_reference_health(collection_stats)
        }
        
        # Generate recommendations
        health_analysis['recommendations'] = self._generate_health_recommendations(health_analysis)
        
        return health_analysis
        
    def _assess_corpus_health(self, corpus_name: str, stats: Dict) -> Dict[str, Any]:
        """Assess health of individual corpus."""
        health = {
            'corpus_name': corpus_name,
            'health_score': 0.0,
            'status': 'unknown',
            'factors': {}
        }
        
        if not stats:
            health['status'] = 'no_data'
            return health
            
        # Calculate health score based on various factors
        score = 0.0
        
        # Data presence (40 points)
        if stats:
            score += 40
            
        # Data size (30 points)
        size = self._get_collection_size(stats)
        if size > 0:
            # Scale size score (up to 30 points)
            size_score = min(30, (size / 100) * 10)  # Adjust scaling as needed
            score += size_score
            
        # Data structure completeness (30 points)
        expected_fields = self._get_expected_fields(corpus_name)
        if expected_fields:
            present_fields = sum(1 for field in expected_fields if field in stats)
            structure_score = (present_fields / len(expected_fields)) * 30
            score += structure_score
            health['factors']['structure_completeness'] = present_fields / len(expected_fields)
        else:
            score += 30  # Give full points if no expected fields defined
            
        health['health_score'] = min(score, 100.0)
        
        # Determine status
        if health['health_score'] >= 90:
            health['status'] = 'excellent'
        elif health['health_score'] >= 75:
            health['status'] = 'good'
        elif health['health_score'] >= 50:
            health['status'] = 'fair'
        else:
            health['status'] = 'poor'
            
        health['factors'].update({
            'data_present': bool(stats),
            'data_size': size,
            'size_category': self._categorize_collection_size(size)
        })
        
        return health
        
    def _get_expected_fields(self, corpus_name: str) -> List[str]:
        """Get expected fields for corpus type."""
        expected_fields_map = {
            'verbnet': ['classes'],
            'framenet': ['frames'],
            'propbank': ['predicates'],
            'ontonotes': ['entries', 'senses'],
            'wordnet': ['synsets']
        }
        return expected_fields_map.get(corpus_name, [])
        
    def _categorize_collection_size(self, size: int) -> str:
        """Categorize collection size."""
        if size == 0:
            return 'empty'
        elif size < 10:
            return 'very_small'
        elif size < 100:
            return 'small'
        elif size < 1000:
            return 'medium'
        elif size < 10000:
            return 'large'
        else:
            return 'very_large'
            
    def _compare_collection_sizes(self, collection_stats: Dict) -> Dict[str, Any]:
        """Compare collection sizes with detailed analysis."""
        size_comparison = {
            'comparison_method': 'statistical_analysis',
            'size_rankings': [],
            'size_statistics': {},
            'balance_analysis': {}
        }
        
        # Calculate sizes and create rankings
        sizes = {}
        for corpus_name, stats in collection_stats.items():
            if corpus_name != 'reference_collections':
                size = self._get_collection_size(stats)
                sizes[corpus_name] = size
                
        if sizes:
            # Create rankings
            size_comparison['size_rankings'] = sorted(sizes.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate statistics
            size_values = list(sizes.values())
            size_comparison['size_statistics'] = {
                'total_items': sum(size_values),
                'largest': max(size_values),
                'smallest': min(size_values),
                'average': sum(size_values) / len(size_values),
                'median': self._calculate_median(size_values),
                'variance': self._calculate_variance(size_values),
                'standard_deviation': self._calculate_variance(size_values) ** 0.5
            }
            
            # Balance analysis
            size_comparison['balance_analysis'] = {
                'balance_score': self._calculate_balance_score(size_values),
                'size_distribution': self._analyze_size_distribution(sizes),
                'outliers': self._identify_size_outliers(sizes)
            }
            
        return size_comparison
        
    def _analyze_reference_collections(self, collection_stats: Dict) -> Dict[str, Any]:
        """Analyze reference collections from collection statistics."""
        ref_collections = collection_stats.get('reference_collections', {})
        
        analysis = {
            'reference_collections_available': bool(ref_collections),
            'total_reference_collections': len(ref_collections),
            'collection_analysis': {}
        }
        
        if ref_collections:
            for collection_name, collection_data in ref_collections.items():
                collection_analysis = {
                    'collection_name': collection_name,
                    'data_type': type(collection_data).__name__,
                    'size': len(collection_data) if hasattr(collection_data, '__len__') else 0,
                    'quality_score': self._assess_reference_collection_quality(collection_data)
                }
                analysis['collection_analysis'][collection_name] = collection_analysis
                
            # Overall reference health
            quality_scores = [ca['quality_score'] for ca in analysis['collection_analysis'].values()]
            analysis['overall_reference_health'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
        return analysis
        
    def _assess_reference_collection_quality(self, collection_data: Any) -> float:
        """Assess quality of reference collection data."""
        if not collection_data:
            return 0.0
            
        score = 0.0
        
        # Data presence (50 points)
        if collection_data:
            score += 50
            
        # Data size (25 points)
        if hasattr(collection_data, '__len__'):
            size = len(collection_data)
            if size > 0:
                score += min(25, size / 10)  # Scale appropriately
                
        # Data structure (25 points)
        if isinstance(collection_data, dict):
            # Check if dictionary values have expected structure
            sample_values = list(collection_data.values())[:5]
            if sample_values and all(isinstance(v, dict) for v in sample_values):
                score += 25
        elif isinstance(collection_data, list):
            # Check if list has non-empty items
            if collection_data and all(item for item in collection_data):
                score += 25
                
        return min(score, 100.0)
        
    def _calculate_performance_metrics(self, collection_stats: Dict, build_metadata: Dict) -> Dict[str, Any]:
        """Calculate performance metrics for the corpus collection system."""
        metrics = {
            'load_performance': {},
            'collection_efficiency': {},
            'system_performance': {}
        }
        
        # Load performance metrics
        load_status = build_metadata.get('load_status', {})
        if load_status:
            total_corpora = len(load_status)
            successful_loads = sum(1 for status in load_status.values() if status == 'success')
            
            metrics['load_performance'] = {
                'total_corpora': total_corpora,
                'successful_loads': successful_loads,
                'success_rate': (successful_loads / total_corpora * 100) if total_corpora > 0 else 0,
                'failed_corpora': [corpus for corpus, status in load_status.items() if status != 'success']
            }
            
        # Collection efficiency metrics
        total_items = sum(
            self._get_collection_size(stats)
            for stats in collection_stats.values()
            if isinstance(stats, dict) and stats != collection_stats.get('reference_collections', {})
        )
        
        metrics['collection_efficiency'] = {
            'total_items_loaded': total_items,
            'items_per_corpus': total_items / len(collection_stats) if collection_stats else 0,
            'collection_density_score': self._calculate_collection_density(collection_stats)
        }
        
        # System performance indicators
        metrics['system_performance'] = {
            'analytics_enabled': True,
            'cache_available': bool(self._analytics_cache),
            'memory_efficiency_score': self._estimate_memory_efficiency(collection_stats)
        }
        
        return metrics
        
    def _generate_analytics_recommendations(self, collection_stats: Dict, build_metadata: Dict) -> List[str]:
        """Generate analytics-based recommendations."""
        recommendations = []
        
        # Check load status
        load_status = build_metadata.get('load_status', {})
        failed_loads = [corpus for corpus, status in load_status.items() if status != 'success']
        
        if failed_loads:
            recommendations.append(f"Address failed corpus loads: {', '.join(failed_loads)}")
            
        # Check collection sizes
        sizes = {
            corpus: self._get_collection_size(stats)
            for corpus, stats in collection_stats.items()
            if corpus != 'reference_collections'
        }
        
        empty_collections = [corpus for corpus, size in sizes.items() if size == 0]
        if empty_collections:
            recommendations.append(f"Investigate empty collections: {', '.join(empty_collections)}")
            
        # Check reference collections
        ref_collections = collection_stats.get('reference_collections', {})
        if not ref_collections:
            recommendations.append("Consider building reference collections for enhanced functionality")
            
        # Performance recommendations
        total_size = sum(sizes.values())
        if total_size > 50000:
            recommendations.append("Large dataset detected - consider implementing data caching for performance")
            
        if not recommendations:
            recommendations.append("Corpus collection system appears to be functioning well")
            
        return recommendations
        
    def _generate_overall_assessment(self, report: Dict) -> Dict[str, Any]:
        """Generate overall assessment from analytics report."""
        assessment = {
            'overall_score': 0.0,
            'status': 'unknown',
            'key_strengths': [],
            'areas_for_improvement': [],
            'critical_issues': []
        }
        
        # Calculate overall score from various components
        scores = []
        
        # Corpus health score
        health_analysis = report.get('corpus_health_analysis', {})
        if 'overall_health_score' in health_analysis:
            scores.append(health_analysis['overall_health_score'])
            
        # Load success rate
        performance_metrics = report.get('performance_metrics', {})
        load_perf = performance_metrics.get('load_performance', {})
        if 'success_rate' in load_perf:
            scores.append(load_perf['success_rate'])
            
        if scores:
            assessment['overall_score'] = sum(scores) / len(scores)
            
            # Determine status
            if assessment['overall_score'] >= 90:
                assessment['status'] = 'excellent'
                assessment['key_strengths'].append('High overall system health')
            elif assessment['overall_score'] >= 75:
                assessment['status'] = 'good'
                assessment['key_strengths'].append('Good system performance')
            elif assessment['overall_score'] >= 50:
                assessment['status'] = 'fair'
                assessment['areas_for_improvement'].append('System performance could be improved')
            else:
                assessment['status'] = 'needs_attention'
                assessment['critical_issues'].append('System performance requires attention')
                
        # Identify specific strengths and issues
        recommendations = report.get('recommendations', [])
        for recommendation in recommendations:
            if 'functioning well' in recommendation:
                assessment['key_strengths'].append('System functioning normally')
            elif any(word in recommendation.lower() for word in ['failed', 'empty', 'missing']):
                assessment['critical_issues'].append(recommendation)
            else:
                assessment['areas_for_improvement'].append(recommendation)
                
        return assessment
    
    # Statistical calculation methods
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of values."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
            
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        
    def _calculate_balance_score(self, values: List[float]) -> float:
        """Calculate balance score (0-100) where 100 is perfectly balanced."""
        if not values or len(values) < 2:
            return 100.0
            
        mean = sum(values) / len(values)
        if mean == 0:
            return 100.0
            
        # Calculate coefficient of variation (inverse of balance)
        std_dev = self._calculate_variance(values) ** 0.5
        cv = std_dev / mean
        
        # Convert to balance score (lower CV = higher balance)
        balance_score = max(0, 100 - (cv * 100))
        return min(balance_score, 100.0)
        
    def _analyze_size_distribution(self, sizes: Dict[str, int]) -> Dict[str, Any]:
        """Analyze distribution of collection sizes."""
        size_values = list(sizes.values())
        
        return {
            'size_categories': {
                category: sum(1 for size in size_values if self._categorize_collection_size(size) == category)
                for category in ['empty', 'very_small', 'small', 'medium', 'large', 'very_large']
            },
            'distribution_type': self._classify_distribution(size_values)
        }
        
    def _classify_distribution(self, values: List[float]) -> str:
        """Classify the type of distribution."""
        if len(values) < 3:
            return 'insufficient_data'
            
        mean = sum(values) / len(values)
        median = self._calculate_median(values)
        
        if abs(mean - median) < mean * 0.1:
            return 'normal'
        elif mean > median:
            return 'right_skewed'
        else:
            return 'left_skewed'
            
    def _identify_size_outliers(self, sizes: Dict[str, int]) -> List[str]:
        """Identify outliers in collection sizes."""
        size_values = list(sizes.values())
        
        if len(size_values) < 4:
            return []
            
        # Use IQR method for outlier detection
        sorted_sizes = sorted(size_values)
        q1 = sorted_sizes[len(sorted_sizes) // 4]
        q3 = sorted_sizes[3 * len(sorted_sizes) // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = []
        for corpus, size in sizes.items():
            if size < lower_bound or size > upper_bound:
                outliers.append(corpus)
                
        return outliers
        
    def _assess_data_completeness(self, collection_stats: Dict) -> float:
        """Assess overall data completeness."""
        total_corpora = len([k for k in collection_stats.keys() if k != 'reference_collections'])
        if total_corpora == 0:
            return 0.0
            
        complete_corpora = sum(
            1 for corpus, stats in collection_stats.items()
            if corpus != 'reference_collections' and self._get_collection_size(stats) > 0
        )
        
        return (complete_corpora / total_corpora) * 100
        
    def _assess_collection_balance(self, collection_stats: Dict) -> float:
        """Assess balance across collections."""
        sizes = [
            self._get_collection_size(stats)
            for corpus, stats in collection_stats.items()
            if corpus != 'reference_collections'
        ]
        
        return self._calculate_balance_score(sizes)
        
    def _assess_reference_health(self, collection_stats: Dict) -> float:
        """Assess health of reference collections."""
        ref_collections = collection_stats.get('reference_collections', {})
        if not ref_collections:
            return 0.0
            
        quality_scores = [
            self._assess_reference_collection_quality(collection_data)
            for collection_data in ref_collections.values()
        ]
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
    def _generate_health_recommendations(self, health_analysis: Dict) -> List[str]:
        """Generate health-based recommendations."""
        recommendations = []
        overall_score = health_analysis.get('overall_health_score', 0)
        
        if overall_score < 50:
            recommendations.append('System health is poor - consider comprehensive data validation')
        elif overall_score < 75:
            recommendations.append('System health is fair - some improvements recommended')
            
        # Specific recommendations based on health factors
        factors = health_analysis.get('health_factors', {})
        
        data_completeness = factors.get('data_completeness', 0)
        if data_completeness < 80:
            recommendations.append('Improve data completeness by loading missing corpora')
            
        collection_balance = factors.get('collection_balance', 0)
        if collection_balance < 60:
            recommendations.append('Collections are imbalanced - review data loading procedures')
            
        reference_health = factors.get('reference_health', 0)
        if reference_health < 70:
            recommendations.append('Reference collections need attention - consider rebuilding')
            
        return recommendations
        
    def _calculate_collection_density(self, collection_stats: Dict) -> float:
        """Calculate collection density score."""
        total_corpora = len([k for k in collection_stats.keys() if k != 'reference_collections'])
        if total_corpora == 0:
            return 0.0
            
        total_items = sum(
            self._get_collection_size(stats)
            for corpus, stats in collection_stats.items()
            if corpus != 'reference_collections'
        )
        
        # Density as average items per corpus
        density = total_items / total_corpora if total_corpora > 0 else 0
        
        # Convert to 0-100 scale (adjust scaling as needed)
        return min(density / 100 * 100, 100.0)
        
    def _estimate_memory_efficiency(self, collection_stats: Dict) -> float:
        """Estimate memory efficiency score."""
        # This is a placeholder implementation
        # In a real system, you would measure actual memory usage
        
        total_items = sum(
            self._get_collection_size(stats)
            for stats in collection_stats.values()
            if isinstance(stats, dict)
        )
        
        # Simple heuristic: assume good efficiency for reasonable data sizes
        if total_items < 10000:
            return 95.0
        elif total_items < 50000:
            return 85.0
        elif total_items < 100000:
            return 75.0
        else:
            return 60.0
            
    def _create_growth_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot for growth tracking."""
        try:
            collection_stats = self.analyzer.get_collection_statistics()
            snapshot = {
                'timestamp': self._get_timestamp(),
                'corpus_sizes': {}
            }
            
            for corpus_name, stats in collection_stats.items():
                if corpus_name != 'reference_collections':
                    snapshot['corpus_sizes'][corpus_name] = {
                        'size': self._get_collection_size(stats),
                        'statistics': stats
                    }
                    
            return snapshot
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
            
    def _categorize_growth_rate(self, growth_rate: float) -> str:
        """Categorize growth rate."""
        if growth_rate == 0:
            return 'no_growth'
        elif growth_rate > 50:
            return 'high_growth'
        elif growth_rate > 20:
            return 'moderate_growth'
        elif growth_rate > 5:
            return 'slow_growth'
        elif growth_rate > 0:
            return 'minimal_growth'
        else:
            return 'decline'
            
    def _summarize_growth(self, growth_analysis: Dict) -> Dict[str, Any]:
        """Summarize growth analysis."""
        summary = {
            'total_corpora_analyzed': len(growth_analysis),
            'growth_categories': {},
            'total_absolute_growth': 0,
            'average_growth_rate': 0.0
        }
        
        growth_rates = []
        categories = {}
        
        for corpus_name, analysis in growth_analysis.items():
            if 'growth_rate_percentage' in analysis:
                growth_rate = analysis['growth_rate_percentage']
                growth_rates.append(growth_rate)
                
                category = self._categorize_growth_rate(growth_rate)
                categories[category] = categories.get(category, 0) + 1
                
            if 'absolute_growth' in analysis:
                summary['total_absolute_growth'] += analysis['absolute_growth']
                
        summary['growth_categories'] = categories
        
        if growth_rates:
            summary['average_growth_rate'] = sum(growth_rates) / len(growth_rates)
            
        return summary
    
    # Corpus-specific helper methods
    
    def _calculate_average_members_per_class(self, corpus_name: str) -> float:
        """Calculate average members per VerbNet class."""
        if corpus_name != 'verbnet':
            return 0.0
            
        verbnet_data = self._get_corpus_data('verbnet')
        if not verbnet_data or 'classes' not in verbnet_data:
            return 0.0
            
        classes = verbnet_data['classes']
        total_members = 0
        class_count = 0
        
        for class_data in classes.values():
            members = class_data.get('members', [])
            total_members += len(members)
            class_count += 1
            
        return total_members / class_count if class_count > 0 else 0.0
        
    def _calculate_average_units_per_frame(self, corpus_name: str) -> float:
        """Calculate average lexical units per FrameNet frame."""
        if corpus_name != 'framenet':
            return 0.0
            
        framenet_data = self._get_corpus_data('framenet')
        if not framenet_data or 'frames' not in framenet_data:
            return 0.0
            
        frames = framenet_data['frames']
        total_units = 0
        frame_count = 0
        
        for frame_data in frames.values():
            lexical_units = frame_data.get('lexical_units', [])
            total_units += len(lexical_units)
            frame_count += 1
            
        return total_units / frame_count if frame_count > 0 else 0.0
        
    def _calculate_average_rolesets_per_predicate(self, corpus_name: str) -> float:
        """Calculate average rolesets per PropBank predicate."""
        if corpus_name != 'propbank':
            return 0.0
            
        propbank_data = self._get_corpus_data('propbank')
        if not propbank_data or 'predicates' not in propbank_data:
            return 0.0
            
        predicates = propbank_data['predicates']
        total_rolesets = 0
        predicate_count = 0
        
        for pred_data in predicates.values():
            rolesets = pred_data.get('rolesets', [])
            total_rolesets += len(rolesets)
            predicate_count += 1
            
        return total_rolesets / predicate_count if predicate_count > 0 else 0.0
    
    def __str__(self) -> str:
        """String representation of AnalyticsManager."""
        return f"AnalyticsManager(corpora={len(self.loaded_corpora)}, analyzer_enabled={self.analyzer is not None})"