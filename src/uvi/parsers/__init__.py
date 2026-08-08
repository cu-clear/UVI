"""
UVI Parsers Package

This package contains specialized parsers for each of the nine linguistic corpora
supported by the UVI package. Each parser handles the specific file formats and
data structures of its respective corpus.

Parsers included:
- VerbNet XML parser
- FrameNet XML parser  
- PropBank XML parser
- OntoNotes XML/HTML parser
- WordNet text file parser
- BSO CSV parser
- SemNet JSON parser
- Reference documentation parser
- VN API enhanced XML parser
"""

from .verbnet_parser import VerbNetParser
from .framenet_parser import FrameNetParser
from .propbank_parser import PropBankParser
from .ontonotes_parser import OntoNotesParser
from .wordnet_parser import WordNetParser
from .bso_parser import BSOParser
from .semnet_parser import SemNetParser
from .reference_parser import ReferenceParser
from .vn_api_parser import VNAPIParser

__all__ = [
    'VerbNetParser',
    'FrameNetParser', 
    'PropBankParser',
    'OntoNotesParser',
    'WordNetParser',
    'BSOParser',
    'SemNetParser',
    'ReferenceParser',
    'VNAPIParser'
]