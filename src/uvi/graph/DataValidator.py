"""
Data Validator for safe data access utilities.

This module provides utilities for safe dictionary access, data validation,
and error handling across all graph builders.
"""

from typing import Dict, Any, List, Optional, Union, Type


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class DataValidator:
    """Utility class for safe data access and validation."""

    @staticmethod
    def safe_get(data: Dict[str, Any], path: str, default: Any = None, expected_type: Optional[Type] = None) -> Any:
        """
        Safely get value from nested dictionary using dot-separated path.

        Args:
            data: Dictionary to access
            path: Dot-separated path (e.g., 'frames.Motion.lexical_units')
            default: Default value if path not found
            expected_type: Optional type to validate result

        Returns:
            Value at path or default

        Raises:
            DataValidationError: If expected_type validation fails
        """
        if not data or not isinstance(data, dict):
            return default

        try:
            keys = path.split('.')
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key)
                else:
                    return default

                if result is None:
                    return default

            # Type validation if requested
            if expected_type and result is not None:
                if not isinstance(result, expected_type):
                    raise DataValidationError(
                        f"Expected {expected_type.__name__} at path '{path}', got {type(result).__name__}"
                    )

            return result

        except (AttributeError, KeyError, TypeError):
            return default

    @staticmethod
    def safe_slice(data: Union[List, Dict], max_limit: int, start_index: int = 0) -> Union[List, Dict]:
        """
        Safely slice data with validation and error handling.

        Args:
            data: Data to slice (list or dict)
            max_limit: Maximum number of items to return
            start_index: Starting index for slicing

        Returns:
            Sliced data
        """
        if not data:
            return data

        try:
            if isinstance(data, list):
                return data[start_index:start_index + max_limit]
            elif isinstance(data, dict):
                items = list(data.items())[start_index:start_index + max_limit]
                return dict(items)
            else:
                # For other types, return as-is
                return data
        except (TypeError, IndexError) as e:
            print(f"Warning: Failed to slice data: {e}")
            return data if isinstance(data, (list, dict)) else []

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str], context: str = "") -> bool:
        """
        Validate that dictionary contains required fields.

        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            context: Context for error messages

        Returns:
            True if all required fields present

        Raises:
            DataValidationError: If validation fails
        """
        if not data or not isinstance(data, dict):
            raise DataValidationError(f"Invalid data structure{' for ' + context if context else ''}")

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise DataValidationError(
                f"Missing required fields {missing_fields}{' in ' + context if context else ''}"
            )

        return True

    @staticmethod
    def validate_data_structure(
        data: Dict[str, Any],
        structure_template: Dict[str, Type],
        context: str = ""
    ) -> bool:
        """
        Validate data structure against template.

        Args:
            data: Dictionary to validate
            structure_template: Template with field names and expected types
            context: Context for error messages

        Returns:
            True if structure matches

        Raises:
            DataValidationError: If validation fails
        """
        for field_name, expected_type in structure_template.items():
            if field_name in data:
                field_value = data[field_name]
                if field_value is not None and not isinstance(field_value, expected_type):
                    raise DataValidationError(
                        f"Field '{field_name}' expected {expected_type.__name__}, "
                        f"got {type(field_value).__name__}{' in ' + context if context else ''}"
                    )

        return True

    @staticmethod
    def get_with_fallback(data: Dict[str, Any], primary_key: str, fallback_keys: List[str], default: Any = None) -> Any:
        """
        Get value with multiple fallback keys.

        Args:
            data: Dictionary to search
            primary_key: Primary key to try first
            fallback_keys: List of fallback keys to try in order
            default: Default value if none found

        Returns:
            First found value or default
        """
        if not data or not isinstance(data, dict):
            return default

        # Try primary key first
        if primary_key in data:
            return data[primary_key]

        # Try fallback keys
        for key in fallback_keys:
            if key in data:
                return data[key]

        return default

    @staticmethod
    def clean_node_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean node data by removing empty/null values and standardizing format.

        Args:
            data: Raw node data

        Returns:
            Cleaned node data
        """
        cleaned = {}
        for key, value in data.items():
            if value is not None and value != "":
                # Convert empty collections to None for consistency
                if isinstance(value, (list, dict)) and len(value) == 0:
                    cleaned[key] = None
                else:
                    cleaned[key] = value

        return cleaned

    @staticmethod
    def count_nested_items(data: Union[Dict, List], path: str = "") -> int:
        """
        Count items in nested data structure.

        Args:
            data: Data structure to count
            path: Optional path to nested structure

        Returns:
            Count of items
        """
        if path:
            data = DataValidator.safe_get(data, path, default={})

        if isinstance(data, dict):
            return len(data)
        elif isinstance(data, list):
            return len(data)
        else:
            return 0 if data is None else 1