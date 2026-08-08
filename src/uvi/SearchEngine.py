"""
SearchEngine Helper Class

Universal search operations with enhanced analytics via CorpusCollectionAnalyzer integration.
Provides comprehensive search capabilities across all corpora with enhanced statistics and 
reference collection searching.

This class replaces UVI's duplicate statistics methods and enhances search functionality
with CorpusCollectionAnalyzer and CorpusCollectionBuilder integration.
"""

from typing import Dict, List, Optional, Union, Any, Set
from .BaseHelper import BaseHelper
from .corpus_loader import CorpusCollectionAnalyzer


class SearchEngine(BaseHelper):
    """
    Universal search operations with enhanced analytics via CorpusCollectionAnalyzer integration.
    
    Provides cross-corpus lemma search, semantic pattern matching, and attribute-based search
    with comprehensive statistics and enhanced analytics. Integrates with CorpusCollectionAnalyzer
    to eliminate duplicate statistics code from UVI.
    
    Key Features:
    - Cross-corpus lemma searching with enhanced statistics
    - Semantic pattern matching with collection context
    - Attribute-based search with coverage analysis
    - Reference collection searching via CorpusCollectionBuilder
    - Enhanced search results with analytics metadata
    """
    
    def __init__(self, uvi_instance):
        """
        Initialize SearchEngine with CorpusCollectionAnalyzer integration.
        
        Args:
            uvi_instance: The main UVI instance containing corpus data and components
        """
        super().__init__(uvi_instance)
        
        # Initialize CorpusCollectionAnalyzer for enhanced analytics
        self.analytics = CorpusCollectionAnalyzer(
            loaded_data=uvi_instance.corpora_data,
            load_status=getattr(uvi_instance.corpus_loader, 'load_status', {}),
            build_metadata=getattr(uvi_instance.corpus_loader, 'build_metadata', {}),
            reference_collections=getattr(uvi_instance.corpus_loader, 'reference_collections', {}),
            corpus_paths=getattr(uvi_instance, 'corpus_paths', {})
        )
        
        # Access to CorpusCollectionBuilder for reference-based search enhancement
        self.collection_builder = getattr(uvi_instance, 'collection_builder', None)
        
    def search_lemmas(self, lemmas: Union[str, List[str]], include_resources: Optional[List[str]] = None, 
                     logic: str = 'OR', sort_behavior: str = 'alphabetical') -> Dict[str, Any]:
        """
        Cross-corpus lemma search with enhanced analytics via CorpusCollectionAnalyzer.
        
        Args:
            lemmas (Union[str, List[str]]): Lemma(s) to search for
            include_resources (Optional[List[str]]): Specific corpora to search in
            logic (str): Search logic ('AND' or 'OR')
            sort_behavior (str): How to sort results ('alphabetical', 'frequency', 'relevance')
            
        Returns:
            Dict[str, Any]: Search results with enhanced statistics and analytics
        """
        # Normalize lemmas input
        if isinstance(lemmas, str):
            lemmas = [lemmas]
        normalized_lemmas = [lemma.lower().strip() for lemma in lemmas]
        
        # Default to all loaded corpora if none specified
        if include_resources is None:
            include_resources = self._get_available_corpora()
            
        # Perform search across specified corpora
        matches = {}
        for corpus_name in include_resources:
            if self._validate_corpus_loaded(corpus_name):
                corpus_matches = self._search_lemmas_in_corpus(normalized_lemmas, corpus_name, logic)
                if corpus_matches:
                    matches[corpus_name] = corpus_matches
                    
        # Sort results according to specified behavior
        sorted_matches = self._sort_search_results(matches, sort_behavior)
        
        # Calculate enhanced search statistics using CorpusCollectionAnalyzer
        search_stats = self._calculate_enhanced_search_statistics(sorted_matches)
        
        return {
            'search_type': 'lemma_search',
            'query_lemmas': lemmas,
            'normalized_lemmas': normalized_lemmas,
            'search_logic': logic,
            'searched_corpora': include_resources,
            'sort_behavior': sort_behavior,
            'matches': sorted_matches,
            'statistics': search_stats,
            'timestamp': self._get_timestamp()
        }
        
    def search_by_semantic_pattern(self, pattern_type: str, pattern_value: str, 
                                 target_resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enhanced semantic pattern search using CorpusCollectionBuilder reference data.
        
        Args:
            pattern_type (str): Type of semantic pattern ('predicate', 'themrole', 'semantic')
            pattern_value (str): Value to search for
            target_resources (Optional[List[str]]): Specific corpora to search in
            
        Returns:
            Dict[str, Any]: Search results with collection context and reference matches
        """
        if target_resources is None:
            target_resources = self._get_available_corpora()
            
        # Standard corpus search
        corpus_matches = self._search_corpus_semantic_patterns(pattern_type, pattern_value, target_resources)
        
        # Enhanced search using reference collections
        reference_matches = []
        if self.collection_builder and hasattr(self.collection_builder, 'reference_collections'):
            collections = self.collection_builder.reference_collections
            
            # Search predicates for semantic patterns
            if pattern_type in ['predicate', 'semantic'] and 'predicates' in collections:
                pred_matches = self._search_reference_collection(
                    collections['predicates'], 
                    pattern_value, fuzzy_match=True, result_type='semantic_predicate'
                )
                reference_matches.extend(pred_matches)
                
            # Search themroles for semantic patterns  
            if pattern_type in ['themrole', 'role'] and 'themroles' in collections:
                role_matches = self._search_reference_collection(
                    collections['themroles'],
                    pattern_value, fuzzy_match=True, result_type='semantic_themrole'
                )
                reference_matches.extend(role_matches)
        
        # Calculate pattern statistics with collection context
        pattern_stats = self._calculate_pattern_statistics_with_analytics(corpus_matches, pattern_type)
        
        return {
            'search_type': 'semantic_pattern',
            'pattern_type': pattern_type,
            'pattern_value': pattern_value,
            'searched_corpora': target_resources,
            'corpus_matches': corpus_matches,
            'reference_matches': reference_matches,
            'total_matches': len(corpus_matches.get('matches', [])) + len(reference_matches),
            'enhanced_by_references': len(reference_matches) > 0,
            'statistics': pattern_stats,
            'timestamp': self._get_timestamp()
        }
        
    def search_by_attribute(self, attribute_type: str, query_string: str, 
                          target_resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Attribute-based search with coverage analysis and enhanced statistics.
        
        Args:
            attribute_type (str): Type of attribute to search ('syntactic', 'selectional', 'feature')
            query_string (str): Query string for attribute search
            target_resources (Optional[List[str]]): Specific corpora to search in
            
        Returns:
            Dict[str, Any]: Search results with coverage analysis and enhanced statistics
        """
        if target_resources is None:
            target_resources = self._get_available_corpora()
            
        matches = {}
        for corpus_name in target_resources:
            if self._validate_corpus_loaded(corpus_name):
                corpus_matches = self._search_attribute_in_corpus(attribute_type, query_string, corpus_name)
                if corpus_matches:
                    matches[corpus_name] = corpus_matches
                    
        # Calculate attribute statistics with coverage analysis
        attribute_stats = self._calculate_attribute_statistics_with_coverage(matches, attribute_type)
        
        return {
            'search_type': 'attribute_search',
            'attribute_type': attribute_type,
            'query_string': query_string,
            'searched_corpora': target_resources,
            'matches': matches,
            'statistics': attribute_stats,
            'timestamp': self._get_timestamp()
        }
        
    def search_by_reference_type(self, reference_type: str, query: str, 
                               fuzzy_match: bool = False) -> Dict[str, Any]:
        """
        Search within CorpusCollectionBuilder reference collections.
        
        Args:
            reference_type (str): Type of reference ('themroles', 'predicates', 'features', etc.)
            query (str): Search query
            fuzzy_match (bool): Enable fuzzy matching
            
        Returns:
            Dict[str, Any]: Search results from reference collections
        """
        if not self.collection_builder or not hasattr(self.collection_builder, 'reference_collections'):
            return {
                'error': 'Reference collections not available',
                'reference_type': reference_type,
                'query': query
            }
            
        collections = self.collection_builder.reference_collections
        results = []
        
        if reference_type == 'themroles' and 'themroles' in collections:
            results = self._search_reference_collection(
                collections['themroles'], query, fuzzy_match, 'themrole'
            )
        elif reference_type == 'predicates' and 'predicates' in collections:
            results = self._search_reference_collection(
                collections['predicates'], query, fuzzy_match, 'predicate'
            )
        elif reference_type == 'features' and 'verb_specific_features' in collections:
            results = self._search_feature_list(
                collections['verb_specific_features'], query, fuzzy_match
            )
        elif reference_type == 'syntactic_restrictions' and 'syntactic_restrictions' in collections:
            results = self._search_restriction_list(
                collections['syntactic_restrictions'], query, fuzzy_match, 'syntactic'
            )
        elif reference_type == 'selectional_restrictions' and 'selectional_restrictions' in collections:
            results = self._search_restriction_list(
                collections['selectional_restrictions'], query, fuzzy_match, 'selectional'
            )
            
        return {
            'search_type': 'reference_collection',
            'reference_type': reference_type,
            'query': query,
            'fuzzy_match': fuzzy_match,
            'total_matches': len(results),
            'matches': results,
            'timestamp': self._get_timestamp()
        }
    
    # Private helper methods
    
    def _search_lemmas_in_corpus(self, normalized_lemmas: List[str], corpus_name: str, logic: str) -> Dict[str, List]:
        """Per-corpus lemma search implementation."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return {}
            
        matches = {}
        
        if corpus_name == 'verbnet' and 'classes' in corpus_data:
            matches = self._search_verbnet_lemmas(corpus_data['classes'], normalized_lemmas, logic)
        elif corpus_name == 'framenet' and 'frames' in corpus_data:
            matches = self._search_framenet_lemmas(corpus_data['frames'], normalized_lemmas, logic)
        elif corpus_name == 'propbank' and 'predicates' in corpus_data:
            matches = self._search_propbank_lemmas(corpus_data['predicates'], normalized_lemmas, logic)
        # Add other corpus-specific search implementations as needed
            
        return matches
        
    def _search_corpus_semantic_patterns(self, pattern_type: str, pattern_value: str, 
                                       target_resources: List[str]) -> Dict[str, Any]:
        """Search semantic patterns across specified corpora."""
        matches = {}
        
        for corpus_name in target_resources:
            if self._validate_corpus_loaded(corpus_name):
                corpus_matches = self._search_semantic_pattern_in_corpus(pattern_type, pattern_value, corpus_name)
                if corpus_matches:
                    matches[corpus_name] = corpus_matches
                    
        return {'matches': matches, 'pattern_type': pattern_type, 'pattern_value': pattern_value}
        
    def _search_semantic_pattern_in_corpus(self, pattern_type: str, pattern_value: str, 
                                         corpus_name: str) -> List[Dict]:
        """Per-corpus semantic pattern search."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return []
            
        # Implement corpus-specific semantic pattern search
        # This would include searching for predicates, themroles, etc.
        return []  # Placeholder - implement specific logic
        
    def _search_attribute_in_corpus(self, attribute_type: str, query_string: str, 
                                  corpus_name: str) -> List[Dict]:
        """Per-corpus attribute search."""
        corpus_data = self._get_corpus_data(corpus_name)
        if not corpus_data:
            return []
            
        # Implement corpus-specific attribute search
        # This would include syntactic restrictions, selectional restrictions, features
        return []  # Placeholder - implement specific logic
        
    def _search_reference_collection(self, collection: Dict, query: str, fuzzy_match: bool, 
                                   result_type: str) -> List[Dict]:
        """Search within a CorpusCollectionBuilder reference collection."""
        results = []
        query_lower = query.lower()
        
        for item_name, item_data in collection.items():
            match_score = 0
            match_fields = []
            
            # Exact name match
            if query_lower == item_name.lower():
                match_score += 100
                match_fields.append('name_exact')
                
            # Fuzzy name match
            elif fuzzy_match and query_lower in item_name.lower():
                match_score += 75
                match_fields.append('name_fuzzy')
                
            # Description/definition match
            if isinstance(item_data, dict):
                for field in ['description', 'definition']:
                    if field in item_data and isinstance(item_data[field], str):
                        field_text = item_data[field].lower()
                        if query_lower == field_text:
                            match_score += 90
                            match_fields.append(f'{field}_exact')
                        elif fuzzy_match and query_lower in field_text:
                            match_score += 60
                            match_fields.append(f'{field}_fuzzy')
            
            if match_score > 0:
                results.append({
                    'name': item_name,
                    'data': item_data,
                    'match_score': match_score,
                    'match_fields': match_fields,
                    'result_type': result_type,
                    'source': 'corpus_collection_builder'
                })
        
        # Sort by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
        
    def _sort_search_results(self, matches: Dict[str, Any], sort_behavior: str) -> Dict[str, Any]:
        """Sort search results according to specified behavior."""
        if sort_behavior == 'alphabetical':
            # Sort matches within each corpus alphabetically
            for corpus_name, corpus_matches in matches.items():
                if isinstance(corpus_matches, dict):
                    matches[corpus_name] = dict(sorted(corpus_matches.items()))
        elif sort_behavior == 'frequency':
            # Sort by frequency/count of matches
            for corpus_name, corpus_matches in matches.items():
                if isinstance(corpus_matches, dict):
                    sorted_items = sorted(corpus_matches.items(), 
                                        key=lambda x: len(x[1]) if isinstance(x[1], list) else 0, 
                                        reverse=True)
                    matches[corpus_name] = dict(sorted_items)
        
        return matches
        
    def _calculate_enhanced_search_statistics(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced statistics.
        This replaces UVI lines 4247-4261 with enhanced analytics.
        """
        # Basic search statistics (keep UVI logic for search-specific metrics)
        basic_stats = {
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            if isinstance(corpus_matches, dict):
                corpus_total = sum(len(lemma_matches) if isinstance(lemma_matches, list) else 0 
                                 for lemma_matches in corpus_matches.values())
            else:
                corpus_total = len(corpus_matches) if isinstance(corpus_matches, list) else 0
            basic_stats['total_matches_by_corpus'][corpus_name] = corpus_total
            basic_stats['total_matches_overall'] += corpus_total
        
        # Enhance with CorpusCollectionAnalyzer collection statistics
        try:
            collection_stats = self.analytics.get_collection_statistics()
            enhanced_stats = {
                **basic_stats,
                'corpus_collection_sizes': {
                    corpus: collection_stats.get(corpus, {})
                    for corpus in matches.keys()
                },
                'search_coverage_percentage': self._calculate_coverage_percentage(matches, collection_stats)
            }
        except Exception as e:
            self.logger.warning(f"Could not enhance statistics with CorpusCollectionAnalyzer: {e}")
            enhanced_stats = basic_stats
            
        return enhanced_stats
        
    def _calculate_pattern_statistics_with_analytics(self, matches: Dict[str, Any], 
                                                   pattern_type: str) -> Dict[str, Any]:
        """
        Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced pattern statistics.
        This replaces UVI lines 4444-4459 with collection context.
        """
        corpus_matches = matches.get('matches', {})
        
        # Basic pattern statistics
        basic_stats = {
            'pattern_type': pattern_type,
            'total_corpora_with_matches': len(corpus_matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_match_list in corpus_matches.items():
            total_matches = len(corpus_match_list) if isinstance(corpus_match_list, list) else 0
            basic_stats['total_matches_by_corpus'][corpus_name] = total_matches
            basic_stats['total_matches_overall'] += total_matches
        
        # Enhance with collection context from CorpusCollectionAnalyzer
        try:
            collection_stats = self.analytics.get_collection_statistics()
            enhanced_stats = {
                **basic_stats,
                'collection_context': {
                    corpus: collection_stats.get(corpus, {})
                    for corpus in corpus_matches.keys()
                },
                'pattern_density': self._calculate_pattern_density(corpus_matches, collection_stats, pattern_type)
            }
        except Exception as e:
            self.logger.warning(f"Could not enhance pattern statistics: {e}")
            enhanced_stats = basic_stats
            
        return enhanced_stats
        
    def _calculate_attribute_statistics_with_coverage(self, matches: Dict[str, Any], 
                                                    attribute_type: str) -> Dict[str, Any]:
        """
        Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced attribute statistics.
        This replaces UVI lines 4575-4588 with coverage analysis.
        """
        # Basic attribute statistics
        basic_stats = {
            'attribute_type': attribute_type,
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            total_matches = len(corpus_matches) if isinstance(corpus_matches, list) else 0
            basic_stats['total_matches_by_corpus'][corpus_name] = total_matches
            basic_stats['total_matches_overall'] += total_matches
        
        # Enhance with CorpusCollectionAnalyzer metadata
        try:
            build_metadata = self.analytics.get_build_metadata()
            enhanced_stats = {
                **basic_stats,
                'corpus_metadata': build_metadata,
                'attribute_distribution': self._analyze_attribute_distribution(matches, attribute_type)
            }
        except Exception as e:
            self.logger.warning(f"Could not enhance attribute statistics: {e}")
            enhanced_stats = basic_stats
            
        return enhanced_stats
        
    def _calculate_coverage_percentage(self, matches: Dict[str, Any], 
                                     collection_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate search coverage as percentage of total corpus collections."""
        coverage = {}
        for corpus_name, corpus_matches in matches.items():
            corpus_stats = collection_stats.get(corpus_name, {})
            
            # Calculate coverage based on corpus type
            if corpus_name == 'verbnet' and 'classes' in corpus_stats:
                total_classes = corpus_stats['classes']
                matched_classes = len(set(match.get('class_id') for match_list in corpus_matches.values() 
                                        for match in (match_list if isinstance(match_list, list) else []) 
                                        if isinstance(match, dict) and match.get('class_id')))
                coverage[corpus_name] = (matched_classes / total_classes * 100) if total_classes > 0 else 0
                
            elif corpus_name == 'framenet' and 'frames' in corpus_stats:
                total_frames = corpus_stats['frames']
                matched_frames = len(set(match.get('frame_name') for match_list in corpus_matches.values() 
                                       for match in (match_list if isinstance(match_list, list) else [])
                                       if isinstance(match, dict) and match.get('frame_name')))
                coverage[corpus_name] = (matched_frames / total_frames * 100) if total_frames > 0 else 0
                
            elif corpus_name == 'propbank' and 'predicates' in corpus_stats:
                total_predicates = corpus_stats['predicates']
                matched_predicates = len(set(match.get('predicate') for match_list in corpus_matches.values() 
                                           for match in (match_list if isinstance(match_list, list) else [])
                                           if isinstance(match, dict) and match.get('predicate')))
                coverage[corpus_name] = (matched_predicates / total_predicates * 100) if total_predicates > 0 else 0
        
        return coverage
        
    def _calculate_pattern_density(self, matches: Dict[str, Any], collection_stats: Dict[str, Any], 
                                 pattern_type: str) -> Dict[str, float]:
        """Calculate pattern density across collections."""
        density = {}
        for corpus_name, corpus_matches in matches.items():
            match_count = len(corpus_matches) if isinstance(corpus_matches, list) else 0
            total_size = self._get_corpus_total_size(corpus_name, collection_stats)
            if total_size > 0:
                density[corpus_name] = (match_count / total_size) * 100
            else:
                density[corpus_name] = 0.0
        return density
        
    def _analyze_attribute_distribution(self, matches: Dict[str, Any], attribute_type: str) -> Dict[str, Any]:
        """Analyze distribution of attributes across corpora."""
        distribution = {
            'by_corpus': {},
            'overall_distribution': {},
            'attribute_type': attribute_type
        }
        
        # Calculate distribution metrics
        for corpus_name, corpus_matches in matches.items():
            if isinstance(corpus_matches, list):
                distribution['by_corpus'][corpus_name] = {
                    'total_matches': len(corpus_matches),
                    'unique_attributes': len(set(str(match) for match in corpus_matches))
                }
        
        return distribution
        
    def _get_corpus_total_size(self, corpus_name: str, collection_stats: Dict[str, Any]) -> int:
        """Get total size of a corpus from collection statistics."""
        corpus_stats = collection_stats.get(corpus_name, {})
        
        # Return appropriate size metric based on corpus type
        if corpus_name == 'verbnet':
            return corpus_stats.get('classes', 0)
        elif corpus_name == 'framenet':
            return corpus_stats.get('frames', 0)
        elif corpus_name == 'propbank':
            return corpus_stats.get('predicates', 0)
        else:
            # Try to get a general size metric
            for key in ['total', 'count', 'size']:
                if key in corpus_stats:
                    return corpus_stats[key]
            return 0
            
    # Corpus-specific search implementations (placeholders for full implementation)
    
    def _search_verbnet_lemmas(self, classes: Dict, lemmas: List[str], logic: str) -> Dict[str, List]:
        """Search for lemmas in VerbNet classes."""
        # Placeholder - implement actual VerbNet lemma search
        return {}
        
    def _search_framenet_lemmas(self, frames: Dict, lemmas: List[str], logic: str) -> Dict[str, List]:
        """Search for lemmas in FrameNet frames."""
        # Placeholder - implement actual FrameNet lemma search
        return {}
        
    def _search_propbank_lemmas(self, predicates: Dict, lemmas: List[str], logic: str) -> Dict[str, List]:
        """Search for lemmas in PropBank predicates."""
        # Placeholder - implement actual PropBank lemma search
        return {}
        
    def _search_feature_list(self, features: List, query: str, fuzzy_match: bool) -> List[Dict]:
        """Search within feature list."""
        results = []
        query_lower = query.lower()
        
        for feature in features:
            if isinstance(feature, str):
                if query_lower == feature.lower():
                    results.append({'feature': feature, 'match_type': 'exact'})
                elif fuzzy_match and query_lower in feature.lower():
                    results.append({'feature': feature, 'match_type': 'fuzzy'})
                    
        return results
        
    def _search_restriction_list(self, restrictions: List, query: str, fuzzy_match: bool, 
                               restriction_type: str) -> List[Dict]:
        """Search within restriction list."""
        results = []
        query_lower = query.lower()
        
        for restriction in restrictions:
            if isinstance(restriction, str):
                if query_lower == restriction.lower():
                    results.append({
                        'restriction': restriction, 
                        'type': restriction_type,
                        'match_type': 'exact'
                    })
                elif fuzzy_match and query_lower in restriction.lower():
                    results.append({
                        'restriction': restriction,
                        'type': restriction_type, 
                        'match_type': 'fuzzy'
                    })
                    
        return results
    
    def __str__(self) -> str:
        """String representation of SearchEngine."""
        return f"SearchEngine(corpora={len(self.loaded_corpora)}, analytics_enabled={self.analytics is not None})"