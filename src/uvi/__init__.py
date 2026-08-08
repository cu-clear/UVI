"""
UVI (Unified Verb Index) Package

A comprehensive standalone package providing integrated access to all nine linguistic 
corpora (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, SemNet, Reference Docs, 
VN API) with cross-resource navigation, semantic validation, and hierarchical analysis 
capabilities.

This package implements the universal interface patterns and shared semantic frameworks 
documented in corpora/OVERVIEW.md, enabling seamless cross-corpus integration and validation.
"""

from .UVI import UVI
from .corpus_loader import CorpusLoader
from .Presentation import Presentation
from .CorpusMonitor import CorpusMonitor

__version__ = "1.0.0"
__author__ = "UVI Development Team"
__description__ = "Unified Verb Index - Comprehensive linguistic corpora access"

# Export main classes and subpackages
__all__ = ['UVI', 'CorpusLoader', 'Presentation', 'CorpusMonitor', 'corpus_loader', 'parsers', 'utils']

# Make subpackages accessible
from . import corpus_loader
from . import parsers
from . import utils

# Import parsers for backward compatibility
from .parsers import (
    VerbNetParser, FrameNetParser, PropBankParser, OntoNotesParser,
    WordNetParser, BSOParser, SemNetParser, ReferenceParser, VNAPIParser
)

# Import corpus loader classes
from .corpus_loader import (
    CorpusCollectionAnalyzer, CorpusCollectionBuilder, CorpusCollectionValidator,
    CorpusLoader as CorpusLoaderClass, CorpusParser
)

# Import utils classes
from .utils import (
    SchemaValidator, CrossReferenceManager, CorpusFileManager
)

# Package metadata
SUPPORTED_CORPORA = [
    'verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet',
    'bso', 'semnet', 'reference_docs', 'vn_api'
]

def get_version():
    """Get the current version of the UVI package."""
    return __version__

def get_supported_corpora():
    """Get list of supported corpora."""
    return SUPPORTED_CORPORA.copy()