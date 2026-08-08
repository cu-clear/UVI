# UVI Corpora Collection Overview

## Introduction

The UVI (Unified Verb Index) corpora collection brings together nine major lexical and semantic resources that provide comprehensive coverage of English verb semantics, syntax, and cross-linguistic mappings. This collection represents one of the most extensive integrated sets of computational linguistic resources available, offering researchers and developers access to multiple perspectives on verb meaning and usage.

## Collection Architecture

### Unified Design Principles

All corpora in this collection share several fundamental design principles that enable seamless integration and cross-resource navigation:

1. **Cross-Resource Integration**: Every corpus provides systematic mappings to other resources in the collection
2. **Hierarchical Organization**: Data is organized in semantic or syntactic hierarchies for efficient navigation
3. **Schema-Driven Validation**: Formal schemas ensure data consistency and enable automatic validation
4. **Example-Driven Documentation**: Real usage examples accompany semantic distinctions
5. **Python-First Interfaces**: Comprehensive Python APIs enable programmatic access and analysis

### Core Semantic Framework

The collection centers around a shared semantic framework with these key components:

- **Thematic Roles**: Agent, Patient, Theme, Goal, Source, Instrument, etc.
- **Syntactic Patterns**: Abstract syntactic frames (NP V NP, NP V PP, etc.)
- **Semantic Predicates**: Formal logical representations of verb meanings
- **Selectional Restrictions**: Constraints on argument types (+animate, +concrete, etc.)
- **Cross-Resource Mappings**: Systematic links between equivalent concepts

## Corpus Collection Summary

### Primary Lexical Resources

| Corpus | Format | Size | Primary Focus | Key Features |
|--------|--------|------|---------------|--------------|
| **VerbNet** | XML | 331 classes | Syntactic-semantic verb classes | Hierarchical organization, rich frame semantics |
| **PropBank** | XML | 7,311 frames | Predicate-argument structures | Semantic role labeling, annotated examples |
| **FrameNet** | XML | 1,221 frames | Frame-semantic analysis | Comprehensive FE annotations, full-text examples |
| **WordNet** | Custom text | 155K+ synsets | Lexical semantic network | Synsets, semantic relations, morphology |
| **OntoNotes** | XML | 4,896 senses | Multi-resource sense inventories | Cross-resource integration, human definitions |

### Specialized Resources

| Corpus | Format | Focus | Integration Role |
|--------|--------|-------|------------------|
| **BSO** | CSV | Broad semantic categorization | Higher-level semantic organization |
| **SemNet** | JSON | Integrated semantic networks | Multi-resource semantic integration |
| **Reference Docs** | JSON/TSV | Formal definitions and constants | Foundational semantic primitives |
| **VN (API)** | XML + Python | VerbNet with production API | Full-featured programmatic interface |

## Common Data Structures and Formats

### Hierarchical Organization Pattern

All corpora follow a consistent hierarchical organization:

```
Corpus Level
├── Major Categories (verb classes, semantic frames, etc.)
│   ├── Subcategories (subclasses, lexical units, etc.)
│   │   ├── Individual Entries (verbs, senses, etc.)
│   │   │   ├── Core Properties (definitions, roles, etc.)
│   │   │   ├── Usage Examples
│   │   │   ├── Syntactic Information
│   │   │   ├── Semantic Annotations
│   │   │   └── Cross-Resource Mappings
│   │   └── ...
│   └── ...
└── ...
```

### Standard XML Structure (6/9 corpora)

XML-based corpora share structural patterns:

```xml
<ROOT_ELEMENT ID="unique_identifier">
    <MEMBERS>
        <!-- Individual lexical items with cross-references -->
        <MEMBER name="lemma" wn="wordnet_key" grouping="propbank_id" 
                fn_mapping="framenet_frame" features="additional_features"/>
    </MEMBERS>
    
    <ROLES_OR_ELEMENTS>
        <!-- Semantic roles or frame elements with restrictions -->
        <ROLE type="Agent">
            <RESTRICTIONS logic="or">
                <RESTRICTION Value="+" type="animate"/>
            </RESTRICTIONS>
        </ROLE>
    </ROLES_OR_ELEMENTS>
    
    <PATTERNS_OR_FRAMES>
        <!-- Syntactic patterns with semantic interpretations -->
        <PATTERN>
            <SYNTAX><!-- Syntactic structure --></SYNTAX>
            <SEMANTICS><!-- Semantic predicates --></SEMANTICS>
            <EXAMPLES><!-- Natural language examples --></EXAMPLES>
        </PATTERN>
    </PATTERNS_OR_FRAMES>
</ROOT_ELEMENT>
```

### Cross-Resource Mapping System

Every corpus implements systematic cross-resource mappings:

```python
# Standard cross-reference structure found across all corpora
cross_references = {
    'wordnet_senses': ['sense_key1', 'sense_key2'],
    'propbank_frames': ['predicate.01', 'predicate.02'], 
    'framenet_frames': ['Frame_Name'],
    'verbnet_classes': ['class-number.subclass'],
    'additional_mappings': {...}
}
```

## Universal Interface Patterns

### Python API Framework

All corpora provide consistent Python interfaces following these patterns:

#### 1. Data Loading Pattern
```python
# Consistent loading pattern across all corpora
class CorpusLoader:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.data = {}
        self.index = {}
        self.load_data()
    
    def load_data(self):
        """Load and index corpus data"""
        # Implementation varies by format (XML, JSON, CSV, custom)
        pass
```

#### 2. Search and Query Interface
```python
# Universal search capabilities
def search_by_lemma(self, lemma):
    """Find all entries containing the specified lemma"""
    
def search_by_pattern(self, pattern):
    """Find entries matching syntactic or semantic pattern"""
    
def search_by_feature(self, feature_type, feature_value):
    """Find entries with specific semantic or syntactic features"""
    
def get_cross_references(self, entry_id, target_resource):
    """Get mappings to other resources"""
```

#### 3. Analysis and Statistics
```python
# Common analytical functions
def get_corpus_statistics(self):
    """Generate comprehensive corpus statistics"""
    
def analyze_feature_distribution(self, feature_type):
    """Analyze distribution of linguistic features"""
    
def validate_data_integrity(self):
    """Verify internal consistency and completeness"""
```

### Validation and Quality Assurance

All corpora implement data validation:

```python
# Universal validation patterns
def validate_schema(self, entry):
    """Validate against formal schema (DTD/XSD/custom)"""
    
def check_cross_references(self, entry):
    """Verify cross-resource mappings are valid"""
    
def verify_completeness(self, entry):
    """Check for required fields and information"""
```

## Shared Semantic Annotation Framework

### Thematic Role System

All corpora use a shared set of thematic roles with consistent definitions:

- **Core Roles**: Agent, Patient, Theme, Experiencer
- **Locational Roles**: Location, Source, Destination, Goal, Path
- **Temporal Roles**: Time, Duration, Frequency
- **Instrumental Roles**: Instrument, Manner, Means
- **Optional Roles**: Beneficiary, Purpose, Cause, Condition

### Selectional Restrictions

Standardized semantic features for argument selection:

- **Animacy**: animate, human, organization
- **Concreteness**: concrete, abstract, substance
- **Functionality**: machine, vehicle, tool, comestible
- **Spatial**: location, region, direction
- **Communicative**: communication, language, sound

### Syntactic Pattern Encoding

Uniform syntactic pattern representation:

```
# Standard syntactic patterns across corpora
NP V NP              # Basic transitive
NP V NP PP.dest      # Ditransitive with destination
NP V S               # Sentential complement
NP V NP.theme PP     # Theme + prepositional phrase
```

## Integration and Cross-Navigation


### Universal Cross-Navigation API

```python
class UnifiedCorpusNavigator:
    """Navigate between resources using cross-references"""
    
    def find_related_entries(self, entry_id, source_corpus, target_corpus):
        """Find related entries in target corpus"""
        
    def trace_semantic_path(self, start_entry, end_entry):
        """Find semantic relationship path between entries"""
        
    def get_complete_semantic_profile(self, lemma):
        """Get comprehensive semantic information from all resources"""
```

## Usage Examples and Best Practices

### Multi-Resource Query Example

```python
def analyze_verb_semantics(verb_lemma):
    """Complete semantic analysis using multiple corpora"""
    
    # Get VerbNet classes
    vn_classes = verbnet_corpus.find_verb_classes(verb_lemma)
    
    # Get PropBank frames
    pb_frames = propbank_corpus.get_frames_for_verb(verb_lemma)
    
    # Get FrameNet information
    fn_frames = framenet_corpus.get_frames_for_lemma(verb_lemma)
    
    # Get WordNet synsets
    wn_synsets = wordnet_corpus.get_synsets(verb_lemma)
    
    # Integrate semantic information
    semantic_profile = integrate_semantic_data(
        vn_classes, pb_frames, fn_frames, wn_synsets
    )
    
    return semantic_profile
```

### Cross-Corpus Validation

```python
def validate_cross_references(entry_id, source_corpus):
    """Validate cross-references across all corpora"""
    
    entry = source_corpus.get_entry(entry_id)
    validation_results = {}
    
    for ref_type, ref_values in entry.cross_references.items():
        target_corpus = get_corpus_by_type(ref_type)
        for ref_value in ref_values:
            exists = target_corpus.entry_exists(ref_value)
            validation_results[f"{ref_type}:{ref_value}"] = exists
    
    return validation_results
```