# OntoNotes Sense Inventories Overview

## Description

This directory contains the OntoNotes sense inventories corpus, which provides detailed semantic annotations for English words. The OntoNotes project was a collaborative effort to create large-scale, multilingual annotation of shallow semantic structures in text, including sense annotation using an inventory of word senses.

## File Hierarchy

```
ontonotes/
├── sense-inventories/
│   ├── inventory.dtd                    # XML DTD schema definition
│   ├── grouping_template.xml           # Template for verb sense entries
│   ├── noun_grouping_template.xml      # Template for noun sense entries
│   ├── abandon-n.xml                   # Noun sense inventory for "abandon"
│   ├── abandon-v.xml                   # Verb sense inventory for "abandon"
│   ├── ability-n.xml                   # Noun sense inventory for "ability"
│   ├── ...                             # 4,896 total sense inventory files
│   └── zoom-v.xml                      # Verb sense inventory for "zoom"
└── OVERVIEW.md                         # This documentation file
```

## Data Contents and Structure

### File Naming Convention

All sense inventory files follow a consistent naming pattern:
- **Format**: `{lemma}-{pos}.xml`
- **lemma**: The root form of the word (e.g., "abandon", "ability", "computer")
- **pos**: Part of speech indicator
  - `n` for nouns
  - `v` for verbs
- **Examples**: `abandon-v.xml`, `computer-n.xml`, `ability-n.xml`

### XML Structure

Each sense inventory file is structured according to the `inventory.dtd` schema and contains:

#### 1. Root Element
```xml
<inventory lemma="word-pos">
```

#### 2. Optional Commentary
```xml
<commentary>
    <!-- Word-level annotations and guidance -->
</commentary>
```

#### 3. Sense Definitions
Each word contains multiple sense definitions with the following structure:

```xml
<sense group="1" n="1" name="descriptive sense name" type="optional_type">
    <commentary>
        <!-- Sense-specific guidance and definitions -->
    </commentary>
    <examples>
        <!-- Example sentences demonstrating usage -->
        <!-- Each example on a separate line -->
    </examples>
    <mappings>
        <gr_sense></gr_sense>                    <!-- Grammar sense mapping -->
        <wn version="3.0">1,2,3</wn>           <!-- WordNet sense numbers -->
        <wn lemma="" version=""></wn>           <!-- Alternative WordNet lemma -->
        <omega></omega>                         <!-- Omega ontology mapping -->
        <pb>abandon.01,abandon.02</pb>          <!-- PropBank predicate mapping -->
        <vn>leave-51.2</vn>                    <!-- VerbNet class mapping -->
        <fn>Departing</fn>                     <!-- FrameNet frame mapping -->
    </mappings>
    <SENSE_META clarity=""/>                   <!-- Automatically generated clarity score -->
</sense>
```

#### 4. Word Metadata
```xml
<WORD_META authors="author_names" sample_score="-"/>
```

### Key Components Explained

- **group**: Coarse clustering identifier for distinguishing homographs
- **n**: Unique sense number within the word
- **name**: Clear, concise description of the sense
- **type**: Optional semantic type (e.g., Entity, Event, State)
- **examples**: Real usage examples illustrating the sense
- **mappings**: Cross-references to external lexical resources:
  - **WordNet (wn)**: Mapping to WordNet synset numbers
  - **PropBank (pb)**: Predicate-argument structure mappings
  - **VerbNet (vn)**: Verb classification mappings
  - **FrameNet (fn)**: Semantic frame mappings

## Data Format Details

### File Statistics
- **Total Files**: 4,898 XML files + 3 support files
- **Word Coverage**: Approximately 4,896 unique lemmas
- **Part of Speech**: Both nouns and verbs
- **Format**: Well-formed XML following DTD specification

### Special Files
1. **inventory.dtd**: XML Document Type Definition specifying the schema
2. **grouping_template.xml**: Empty template for creating verb sense inventories
3. **noun_grouping_template.xml**: Empty template for creating noun sense inventories

### Sense Organization
- Most words have 2-6 distinct senses
- Each sense includes detailed usage examples
- Comprehensive mappings to major lexical databases
- Some entries include a "none of the above" (NOTA) sense for completeness

## Python Code Examples

### Basic XML Parsing

```python
import xml.etree.ElementTree as ET
import os
from pathlib import Path

def load_sense_inventory(file_path):
    """Load and parse an OntoNotes sense inventory file."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    lemma = root.get('lemma')
    senses = []
    
    for sense in root.findall('sense'):
        sense_data = {
            'group': sense.get('group'),
            'number': sense.get('n'),
            'name': sense.get('name'),
            'type': sense.get('type', ''),
            'examples': [],
            'mappings': {}
        }
        
        # Extract examples
        examples_elem = sense.find('examples')
        if examples_elem is not None and examples_elem.text:
            sense_data['examples'] = [ex.strip() for ex in examples_elem.text.strip().split('\n') if ex.strip()]
        
        # Extract mappings
        mappings_elem = sense.find('mappings')
        if mappings_elem is not None:
            for mapping_type in ['wn', 'pb', 'vn', 'fn']:
                elem = mappings_elem.find(mapping_type)
                if elem is not None and elem.text:
                    sense_data['mappings'][mapping_type] = elem.text.strip()
        
        senses.append(sense_data)
    
    return lemma, senses

# Example usage
sense_file = "C:/path-to-repo-here/UVI/corpora/ontonotes/sense-inventories/abandon-v.xml"
lemma, senses = load_sense_inventory(sense_file)

print(f"Lemma: {lemma}")
for i, sense in enumerate(senses):
    print(f"  Sense {sense['number']}: {sense['name']}")
    print(f"    Examples: {len(sense['examples'])}")
    print(f"    Mappings: {list(sense['mappings'].keys())}")
```

### Corpus-wide Analysis

```python
def analyze_corpus(sense_inventories_dir):
    """Analyze the entire OntoNotes sense inventories corpus."""
    corpus_stats = {
        'total_files': 0,
        'total_words': 0,
        'total_senses': 0,
        'pos_distribution': {'n': 0, 'v': 0},
        'sense_count_distribution': {},
        'mapping_coverage': {}
    }
    
    sense_dir = Path(sense_inventories_dir)
    
    for xml_file in sense_dir.glob("*-[nv].xml"):
        corpus_stats['total_files'] += 1
        
        try:
            lemma, senses = load_sense_inventory(xml_file)
            corpus_stats['total_words'] += 1
            corpus_stats['total_senses'] += len(senses)
            
            # Track part of speech
            pos = lemma.split('-')[-1]
            if pos in corpus_stats['pos_distribution']:
                corpus_stats['pos_distribution'][pos] += 1
            
            # Track sense count distribution
            sense_count = len(senses)
            corpus_stats['sense_count_distribution'][sense_count] = \
                corpus_stats['sense_count_distribution'].get(sense_count, 0) + 1
            
            # Track mapping coverage
            for sense in senses:
                for mapping_type in sense['mappings']:
                    if mapping_type not in corpus_stats['mapping_coverage']:
                        corpus_stats['mapping_coverage'][mapping_type] = 0
                    corpus_stats['mapping_coverage'][mapping_type] += 1
                    
        except ET.ParseError:
            print(f"Parse error in {xml_file}")
            continue
    
    return corpus_stats

# Example usage
corpus_dir = "C:/path-to-repo-here/UVI/corpora/ontonotes/sense-inventories"
stats = analyze_corpus(corpus_dir)

print("Corpus Statistics:")
print(f"  Total files: {stats['total_files']}")
print(f"  Total words: {stats['total_words']}")
print(f"  Total senses: {stats['total_senses']}")
print(f"  Average senses per word: {stats['total_senses'] / stats['total_words']:.2f}")
print(f"  Part of speech distribution: {stats['pos_distribution']}")
```

### Search and Query Functions

```python
def find_words_by_sense_name(sense_inventories_dir, search_term):
    """Find all words that have senses containing the search term."""
    results = []
    sense_dir = Path(sense_inventories_dir)
    
    for xml_file in sense_dir.glob("*-[nv].xml"):
        try:
            lemma, senses = load_sense_inventory(xml_file)
            
            for sense in senses:
                if search_term.lower() in sense['name'].lower():
                    results.append({
                        'lemma': lemma,
                        'sense_number': sense['number'],
                        'sense_name': sense['name'],
                        'examples': sense['examples'][:2]  # First 2 examples
                    })
        except ET.ParseError:
            continue
    
    return results

def get_wordnet_mappings(sense_inventories_dir, wordnet_sense):
    """Find OntoNotes senses that map to a specific WordNet sense."""
    results = []
    sense_dir = Path(sense_inventories_dir)
    
    for xml_file in sense_dir.glob("*-[nv].xml"):
        try:
            lemma, senses = load_sense_inventory(xml_file)
            
            for sense in senses:
                wn_mappings = sense['mappings'].get('wn', '')
                if wordnet_sense in wn_mappings.split(','):
                    results.append({
                        'lemma': lemma,
                        'sense_number': sense['number'],
                        'sense_name': sense['name'],
                        'wordnet_mapping': wn_mappings
                    })
        except ET.ParseError:
            continue
    
    return results

# Example usage
# Find words with senses related to "money"
money_senses = find_words_by_sense_name(corpus_dir, "money")
print(f"Found {len(money_senses)} senses related to 'money'")

# Find OntoNotes senses that map to WordNet sense 1
wn_mappings = get_wordnet_mappings(corpus_dir, "1")
print(f"Found {len(wn_mappings)} senses mapping to WordNet sense 1")
```

### Validation and Quality Control

```python
def validate_inventory_file(file_path):
    """Validate an OntoNotes sense inventory file for completeness."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        issues = []
        
        # Check root element
        if root.tag != 'inventory':
            issues.append("Root element is not 'inventory'")
        
        if not root.get('lemma'):
            issues.append("Missing lemma attribute")
        
        # Check senses
        senses = root.findall('sense')
        if not senses:
            issues.append("No senses defined")
        
        for i, sense in enumerate(senses):
            sense_id = f"sense {i+1}"
            
            if not sense.get('n'):
                issues.append(f"{sense_id}: Missing sense number")
            
            if not sense.get('name'):
                issues.append(f"{sense_id}: Missing sense name")
            
            examples = sense.find('examples')
            if examples is None or not examples.text or not examples.text.strip():
                issues.append(f"{sense_id}: No examples provided")
            
            mappings = sense.find('mappings')
            if mappings is None:
                issues.append(f"{sense_id}: Missing mappings element")
        
        # Check word metadata
        word_meta = root.find('WORD_META')
        if word_meta is None:
            issues.append("Missing WORD_META element")
        elif not word_meta.get('authors'):
            issues.append("Missing authors in WORD_META")
        
        return len(issues) == 0, issues
        
    except ET.ParseError as e:
        return False, [f"XML parsing error: {e}"]

# Example usage - validate a file
is_valid, validation_issues = validate_inventory_file(sense_file)
if is_valid:
    print("File is valid!")
else:
    print("Validation issues:")
    for issue in validation_issues:
        print(f"  - {issue}")
```

## Usage Notes

1. **XML Parsing**: All files are well-formed XML that can be parsed with standard XML libraries
2. **Encoding**: Files use UTF-8 encoding
3. **Cross-references**: The mapping elements provide valuable links to other lexical resources
4. **Completeness**: Some senses may have empty mapping fields, indicating no direct correspondence
5. **Templates**: Use the provided template files for creating new sense inventories