"""
Unified Data Processor for consolidating data selection and validation.

This module provides unified data processing logic that eliminates
duplication across all graph builders.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from .DataValidator import DataValidator, DataValidationError


class UnifiedDataProcessor:
    """
    Unified processor for data selection, validation, and transformation
    across all corpus types.
    """

    def __init__(self):
        """Initialize the UnifiedDataProcessor."""
        self.validator = DataValidator()

    def select_items_with_content(
        self,
        data_dict: Dict[str, Any],
        max_items: int,
        content_path: str = "",
        min_content_count: int = 1,
        fallback_to_any: bool = True
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Select items that have content, with fallback to any items.

        Args:
            data_dict: Dictionary of items to select from
            max_items: Maximum number of items to select
            content_path: Path to content to check (e.g., 'lexical_units')
            min_content_count: Minimum content items required
            fallback_to_any: Whether to fallback to any items if none have content

        Returns:
            List of (item_name, item_data) tuples
        """
        if not data_dict or not isinstance(data_dict, dict):
            return []

        items_with_content = []
        items_checked = 0
        max_checks = min(100, len(data_dict))  # Limit checks for performance

        # First pass: find items with required content
        for item_name, item_data in data_dict.items():
            if items_checked >= max_checks:
                break

            items_checked += 1

            if content_path:
                content = self.validator.safe_get(item_data, content_path, default={})
                content_count = self.validator.count_nested_items(content)

                if content_count >= min_content_count:
                    items_with_content.append((item_name, item_data))
                    if len(items_with_content) >= max_items:
                        break
            else:
                # No content path specified, just add items
                items_with_content.append((item_name, item_data))
                if len(items_with_content) >= max_items:
                    break

        print(f"Checked {items_checked} items, found {len(items_with_content)} with required content")

        # If we don't have enough items and fallback is enabled, add any remaining items
        if len(items_with_content) < max_items and fallback_to_any:
            remaining_needed = max_items - len(items_with_content)
            existing_names = {name for name, _ in items_with_content}

            for item_name, item_data in data_dict.items():
                if item_name not in existing_names:
                    items_with_content.append((item_name, item_data))
                    if len(items_with_content) >= max_items:
                        break

        return items_with_content[:max_items]

    def extract_child_items(
        self,
        parent_data: Dict[str, Any],
        child_path: str,
        max_children: int,
        required_fields: Optional[List[str]] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Extract child items from parent data with validation.

        Args:
            parent_data: Parent item data
            child_path: Path to child items (e.g., 'lexical_units')
            max_children: Maximum number of children to extract
            required_fields: Optional list of required fields in child items

        Returns:
            List of (child_name, child_data) tuples
        """
        child_data = self.validator.safe_get(parent_data, child_path, default={})

        if not child_data:
            return []

        child_items = []

        if isinstance(child_data, dict):
            # Dictionary of child items
            for child_name, child_info in child_data.items():
                if not isinstance(child_info, dict):
                    continue

                # Validate required fields if specified
                if required_fields:
                    try:
                        self.validator.validate_required_fields(
                            child_info, required_fields, f"child {child_name}"
                        )
                    except DataValidationError:
                        continue

                child_items.append((child_name, child_info))

                if len(child_items) >= max_children:
                    break

        elif isinstance(child_data, list):
            # List of child items
            for i, child_info in enumerate(child_data):
                if not isinstance(child_info, dict):
                    continue

                child_name = child_info.get('name', f"child_{i}")

                # Validate required fields if specified
                if required_fields:
                    try:
                        self.validator.validate_required_fields(
                            child_info, required_fields, f"child {child_name}"
                        )
                    except DataValidationError:
                        continue

                child_items.append((child_name, child_info))

                if len(child_items) >= max_children:
                    break

        return child_items

    def process_batch_data(
        self,
        raw_data_items: List[Tuple[str, Dict[str, Any]]],
        processor_func: callable,
        config: Dict[str, Any],
        error_context: str = "batch processing"
    ) -> List[Dict[str, Any]]:
        """
        Process multiple data items with error handling.

        Args:
            raw_data_items: List of (name, raw_data) tuples
            processor_func: Function to process each item
            config: Configuration dictionary
            error_context: Context for error messages

        Returns:
            List of processed data dictionaries
        """
        processed_items = []

        for item_name, raw_data in raw_data_items:
            try:
                # Add item name to config for processing
                item_config = config.copy()
                item_config['item_name'] = item_name

                # Process the item
                processed_data = processor_func(raw_data, item_config)

                if processed_data:
                    processed_items.append(processed_data)

            except Exception as e:
                print(f"Warning: Failed to process {item_name} in {error_context}: {e}")
                continue

        return processed_items

    def safe_slice_data(
        self,
        data: Union[List, Dict, str],
        max_limit: int,
        start_index: int = 0
    ) -> Union[List, Dict, str]:
        """
        Safely slice data with comprehensive error handling.

        Args:
            data: Data to slice
            max_limit: Maximum number of items
            start_index: Starting index

        Returns:
            Sliced data
        """
        if data is None:
            return None

        try:
            if isinstance(data, slice):
                # Handle slice objects (common issue in current code)
                return data
            elif isinstance(data, (list, tuple)):
                return data[start_index:start_index + max_limit]
            elif isinstance(data, dict):
                items = list(data.items())[start_index:start_index + max_limit]
                return dict(items)
            elif isinstance(data, str):
                return data  # Don't slice strings
            else:
                print(f"Warning: Unexpected data type for slicing: {type(data)}")
                return data

        except Exception as e:
            print(f"Warning: Failed to slice data: {e}")
            return data

    def validate_corpus_structure(
        self,
        data: Dict[str, Any],
        corpus_type: str
    ) -> bool:
        """
        Validate corpus data structure based on type.

        Args:
            data: Corpus data to validate
            corpus_type: Type of corpus ('framenet', 'propbank', etc.)

        Returns:
            True if structure is valid

        Raises:
            DataValidationError: If structure is invalid
        """
        corpus_structures = {
            'framenet': {
                'required_root': 'frames',
                'item_required_fields': ['name'],
                'optional_child_paths': ['lexical_units', 'frame_elements']
            },
            'propbank': {
                'required_root': 'rolesets',
                'item_required_fields': ['id'],
                'optional_child_paths': ['roles', 'examples']
            },
            'verbnet': {
                'required_root': 'classes',
                'item_required_fields': ['id', 'name'],
                'optional_child_paths': ['members', 'frames']
            },
            'wordnet': {
                'required_root': 'synsets',
                'item_required_fields': ['name'],
                'optional_child_paths': ['lemmas', 'hypernyms']
            }
        }

        if corpus_type not in corpus_structures:
            raise DataValidationError(f"Unknown corpus type: {corpus_type}")

        structure = corpus_structures[corpus_type]
        required_root = structure['required_root']

        # Check that required root exists
        if required_root not in data:
            raise DataValidationError(f"Missing required root '{required_root}' in {corpus_type} data")

        root_data = data[required_root]
        if not isinstance(root_data, dict):
            raise DataValidationError(f"Root '{required_root}' must be a dictionary in {corpus_type} data")

        # Validate a sample of items (don't check all for performance)
        sample_items = dict(list(root_data.items())[:5])  # Check first 5 items
        required_fields = structure['item_required_fields']

        for item_name, item_data in sample_items.items():
            if not isinstance(item_data, dict):
                continue

            try:
                self.validator.validate_required_fields(
                    item_data, required_fields, f"{corpus_type} item {item_name}"
                )
            except DataValidationError as e:
                print(f"Warning: Structure validation failed for {item_name}: {e}")
                # Continue validation, don't fail on single items

        return True

    def get_corpus_statistics(self, data: Dict[str, Any], corpus_type: str) -> Dict[str, int]:
        """
        Get statistics about corpus data.

        Args:
            data: Corpus data
            corpus_type: Type of corpus

        Returns:
            Dictionary with statistics
        """
        stats = {}

        try:
            self.validate_corpus_structure(data, corpus_type)
        except DataValidationError:
            return {'error': 1}

        corpus_structures = {
            'framenet': {'root': 'frames', 'children': ['lexical_units', 'frame_elements']},
            'propbank': {'root': 'rolesets', 'children': ['roles', 'examples']},
            'verbnet': {'root': 'classes', 'children': ['members', 'frames']},
            'wordnet': {'root': 'synsets', 'children': ['lemmas', 'hypernyms']}
        }

        if corpus_type not in corpus_structures:
            return {'error': 1}

        structure = corpus_structures[corpus_type]
        root_data = data.get(structure['root'], {})

        stats['total_items'] = len(root_data)

        # Count child items
        for child_path in structure['children']:
            total_children = 0
            for item_data in root_data.values():
                if isinstance(item_data, dict):
                    children = self.validator.safe_get(item_data, child_path, {})
                    total_children += self.validator.count_nested_items(children)
            stats[f'total_{child_path}'] = total_children

        return stats