# VerbNet Reference Documentation Overview

This directory contains reference documentation and data files for VerbNet (Verb Network), a hierarchical domain-independent, broad-coverage verb lexicon with mappings to other lexical resources. VerbNet is based on Levin verb classes and provides detailed syntactic and semantic information about English verbs.

## File Hierarchy

```
reference_docs/
├── OVERVIEW.md                          # This file
├── pred_calc_for_website_final.json     # Complete predicate calculations dataset
├── themrole_defs.json                   # Thematic role definitions
├── vn_constants.tsv                     # VerbNet semantic constants definitions
├── vn_semantic_predicates.tsv           # VerbNet semantic predicates definitions  
├── vn_verb_specific_predicates.tsv      # Verb-specific predicates definitions
└── vn_themrole_html/                    # HTML documentation for thematic roles
    ├── Agent.php.html                   # Agent thematic role documentation
    ├── Patient.php.html                 # Patient thematic role documentation
    ├── Theme.php.html                   # Theme thematic role documentation
    └── [35 other role HTML files]       # Complete set of thematic role docs
```

## File Contents and Purpose

### 1. pred_calc_for_website_final.json

**Purpose**: Complete dataset of predicate calculations for VerbNet entries, containing syntactic and semantic representations of verb usages.

**Format**: JSON object with numeric string keys mapping to arrays of linguistic data

**Structure**: Each entry contains 8 elements:
```json
"ID": [
    "example_sentence",           # Natural language example
    "verbnet_class",             # VerbNet class identifier  
    "syntactic_pattern",         # Abstract syntactic pattern
    "concrete_pattern",          # Concrete NP/PP pattern
    "semantic_category",         # High-level semantic classification
    "aspectual_class",          # Aspectual/temporal properties
    "semantic_representation"   # Formal semantic predicate logic
]
```

**Size**: ~7,022 lines, 277KB

**Example**:
```json
"1000": [
    "Herman spliced ropes",
    "shake-22.3-2-1", 
    "Sbj V Obj",
    "NP V NP",
    "Volitional Internal",
    "IncrementalAccomplishment",
    "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,ropes) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INTL(q2) & FRC(a,b)"
]
```

### 2. themrole_defs.json

**Purpose**: Definitions and examples for all VerbNet thematic roles

**Format**: JSON array of objects, each defining a thematic role

**Structure**: Each role object contains:
- `name`: Role name (e.g., "Agent", "Patient", "Theme")  
- `description`: Linguistic definition of the role
- `example`: Example sentence with role highlighted in caps

**Size**: 40+ thematic roles defined

**Key Roles Include**:
- **Agent**: Actor who initiates events intentionally
- **Patient**: Undergoer that is structurally changed  
- **Theme**: Central undergoer not structurally changed
- **Instrument**: Tool manipulated by agent
- **Location**: Concrete place
- **Source/Destination**: Start/end points of motion
- **Experiencer**: Conscious undergoer of psychological events

### 3. vn_constants.tsv

**Purpose**: Definitions of semantic constants used in VerbNet predicate representations

**Format**: Tab-separated values with headers

**Columns**:
- `Constant name`: Name of the semantic constant
- `Definition`: Explanation of meaning
- `Arguments`: Formal argument structure  
- `Comments`: Additional notes and usage context

**Key Constants**:
- `abstract`: Event is abstract/metaphorical
- `ch_of_loc`: Entity changes location
- `ch_of_state`: Undergoer changes state
- `forceful`: Action uses/applies force
- `toward`: Motion toward destination

### 4. vn_semantic_predicates.tsv  

**Purpose**: Comprehensive list of semantic predicates used in VerbNet representations

**Format**: Tab-separated values with headers

**Columns**:
- `Predicate name`: Name and usage count in parentheses
- `Definition`: Semantic meaning
- `Arguments`: Formal argument structure
- `Comments`: Usage notes and status

**Notable Predicates**:
- `path_rel`: Most common (618 uses) - path relationships
- `Pred`: Predicate adjectives (50 uses) 
- `about`: Communication/social events (34 uses)
- `alive`: Animate patient vitality states (14 uses)

### 5. vn_verb_specific_predicates.tsv

**Purpose**: Definitions of predicates that are specific to particular verb classes

**Format**: Tab-separated values with headers

**Columns**:
- `VerbSpecific name`: Predicate name
- `Definition`: Semantic definition
- `Arguments`: Formal argument structure
- `Comments`: Usage context and verb classes

**Key Predicates**:
- `Direction`: Motion direction in change events
- `Form`: Physical form resulting from events  
- `Material`: Material used to change patients
- `Sound/Light/Odor`: Emission predicates
- `Pos`: Positional configurations

### 6. vn_themrole_html/ Directory

**Purpose**: HTML documentation files for each thematic role, generated from VerbNet database

**Format**: HTML files with embedded PHP references  

**Content**: Each file contains:
- Role definition and examples
- Complete list of VerbNet classes using that role
- Links to verb class documentation
- Navigation and search functionality

**Files**: 38 HTML files, one for each thematic role (Agent.php.html, Patient.php.html, etc.)

## Data Format Details

### JSON Files
- **Encoding**: UTF-8
- **Structure**: Well-formed JSON with consistent typing
- **Keys**: String keys for object properties, numeric strings for pred_calc IDs

### TSV Files  
- **Encoding**: UTF-8
- **Delimiter**: Tab characters (\t)
- **Headers**: First row contains column names
- **Escaping**: No special escaping required for tab-separated format

### HTML Files
- **Standard**: HTML 4.01 Transitional  
- **Encoding**: UTF-8 with XML declaration
- **JavaScript**: Interactive features for navigation and search
- **CSS**: External stylesheet references

## Python Code Examples

### Loading the Predicate Calculations Dataset

```python
import json

def load_predicate_calculations(filepath):
    """Load the main VerbNet predicate calculations dataset."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Usage
pred_calc = load_predicate_calculations('pred_calc_for_website_final.json')

# Access specific entry
entry_1000 = pred_calc['1000']
sentence = entry_1000[0]  # "Herman spliced ropes"
vn_class = entry_1000[1]  # "shake-22.3-2-1"
semantic_rep = entry_1000[7]  # Full semantic representation

# Iterate through all entries
for entry_id, data in pred_calc.items():
    sentence, vn_class, syn_pattern, conc_pattern, sem_cat, aspect, semantics = data
    print(f"ID {entry_id}: {sentence} ({vn_class})")
```

### Loading Thematic Role Definitions

```python
import json

def load_thematic_roles(filepath):
    """Load thematic role definitions."""
    with open(filepath, 'r', encoding='utf-8') as f:
        roles = json.load(f)
    return {role['name']: role for role in roles}

# Usage  
roles = load_thematic_roles('themrole_defs.json')

# Get definition for specific role
agent_def = roles['Agent']['description']
agent_example = roles['Agent']['example']

# Find roles with examples
roles_with_examples = [role for role in roles.values() 
                      if role['example'] != "No examples found"]

print(f"Found {len(roles_with_examples)} roles with examples")
```

### Loading TSV Reference Data

```python
import csv
from typing import List, Dict

def load_tsv_data(filepath: str) -> List[Dict[str, str]]:
    """Load TSV data into list of dictionaries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return list(reader)

# Load constants
constants = load_tsv_data('vn_constants.tsv')

# Find constants related to motion
motion_constants = [const for const in constants 
                   if 'motion' in const['Definition'].lower()]

# Load semantic predicates  
predicates = load_tsv_data('vn_semantic_predicates.tsv')

# Get most frequently used predicates
frequent_preds = [pred for pred in predicates 
                 if pred['Predicate name'].endswith(')')]

# Sort by usage count (extracted from name field)
def extract_count(pred_name):
    if '(' in pred_name:
        return int(pred_name.split('(')[1].split()[0])
    return 0

frequent_preds.sort(key=lambda p: extract_count(p['Predicate name']), reverse=True)
```

### Searching and Filtering Data

```python
def search_semantic_representations(pred_calc_data, search_term):
    """Search semantic representations for specific terms."""
    matches = []
    for entry_id, data in pred_calc_data.items():
        semantic_rep = data[7]  # Semantic representation is last element
        if search_term.lower() in semantic_rep.lower():
            matches.append({
                'id': entry_id,
                'sentence': data[0],
                'vn_class': data[1], 
                'semantic_rep': semantic_rep
            })
    return matches

# Find entries with force relations
force_entries = search_semantic_representations(pred_calc, 'FRC')

# Find entries with specific VerbNet classes  
def filter_by_vn_class(pred_calc_data, class_pattern):
    """Filter entries by VerbNet class pattern."""
    matches = []
    for entry_id, data in pred_calc_data.items():
        vn_class = data[1]
        if class_pattern in vn_class:
            matches.append((entry_id, data))
    return matches

# Get all entries from 'hit' class family
hit_entries = filter_by_vn_class(pred_calc, 'hit-')
```

### Data Analysis Examples

```python
from collections import Counter
import re

def analyze_aspectual_classes(pred_calc_data):
    """Analyze distribution of aspectual classes."""
    aspects = [data[5] for data in pred_calc_data.values()]
    return Counter(aspects)

def analyze_syntactic_patterns(pred_calc_data):
    """Analyze syntactic pattern frequencies.""" 
    patterns = [data[2] for data in pred_calc_data.values()]
    return Counter(patterns)

def extract_predicates_from_semantics(pred_calc_data):
    """Extract all predicates used in semantic representations."""
    all_predicates = set()
    for data in pred_calc_data.values():
        semantic_rep = data[7]
        # Extract predicates using regex (simplified)
        predicates = re.findall(r'([A-Za-z_]+)\(', semantic_rep)
        all_predicates.update(predicates)
    return sorted(all_predicates)

# Usage
aspect_dist = analyze_aspectual_classes(pred_calc)
syn_patterns = analyze_syntactic_patterns(pred_calc)  
semantic_predicates = extract_predicates_from_semantics(pred_calc)

print("Top 5 aspectual classes:")
for aspect, count in aspect_dist.most_common(5):
    print(f"  {aspect}: {count}")
```

## Usage Notes

1. **File Paths**: All file paths in code examples are relative to the `reference_docs/` directory
2. **Encoding**: All files use UTF-8 encoding
3. **Data Consistency**: The JSON files use consistent structure but TSV files may have varying column counts
4. **HTML Files**: The HTML files are primarily for web display and contain references to external CSS/JS files
5. **Large Dataset**: The main predicate calculations file is large (277KB) - consider memory usage for full dataset operations

For more information about VerbNet, see: https://verbs.colorado.edu/verbnet/