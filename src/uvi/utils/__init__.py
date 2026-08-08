"""
UVI Utils Package

This package contains utility functions and classes for the UVI package including
schema validation, cross-corpus reference management, and file system utilities.

Utilities included:
- Schema validation for XML and JSON corpus files
- Cross-corpus reference resolution and validation
- File system utilities for corpus management
"""

from .validation import SchemaValidator, validate_xml_against_dtd, validate_xml_against_xsd
from .cross_refs import CrossReferenceManager, build_cross_reference_index, validate_cross_references
from .file_utils import CorpusFileManager, detect_corpus_structure, safe_file_read

__all__ = [
    'SchemaValidator',
    'validate_xml_against_dtd',
    'validate_xml_against_xsd',
    'CrossReferenceManager',
    'build_cross_reference_index',
    'validate_cross_references',
    'CorpusFileManager',
    'detect_corpus_structure',
    'safe_file_read'
]