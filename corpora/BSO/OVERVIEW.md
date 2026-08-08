# BSO (Broad Semantic Organization) Corpus Overview

## Introduction

The BSO (Broad Semantic Organization) corpus contained in this folder provides mappings between VerbNet classes and broad semantic categories. This corpus facilitates the organization of verbs into higher-level semantic groupings, enabling researchers to study verb semantics at different levels of granularity.

## File Hierarchy

```
BSO/
├── BSOVNMapping_withMembers.csv    # BSO semantic classes mapped to VerbNet classes with member verbs
└── VNBSOMapping_withMembers.csv    # VerbNet classes mapped to BSO semantic classes with member verbs
```

## File Contents and Purpose

### 1. BSOVNMapping_withMembers.csv

**Purpose**: This file maps Broad Semantic Organization categories to VerbNet classes, providing the verb members for each mapping.

**Structure**: Each row contains a mapping from a BSO semantic class to a VerbNet class with the following columns:
- **Column 1**: BSO semantic class name (e.g., "Cause Negative Feeling")
- **Column 2**: VerbNet class ID (e.g., "amuse-31.1")
- **Column 3**: Number of verb members in this mapping (e.g., "92")
- **Column 4**: List of verb members as a Python list string (e.g., "['unsettle', 'dispirit', 'displease', ...]")

**Example entries**:
```csv
Cause Negative Feeling,amuse-31.1,92,"['unsettle', 'dispirit', 'displease', 'agonize', ...]"
Manner of Motion,run-51.3.2,48,"['shuffle', 'gallop', 'skip', 'limp', 'bound', ...]"
Cause Positive Feeling,amuse-31.1,40,"['reassure', 'soothe', 'hearten', 'revitalize', ...]"
```

### 2. VNBSOMapping_withMembers.csv

**Purpose**: This file provides the reverse mapping from VerbNet classes to BSO semantic categories, with verb members for each mapping.

**Structure**: Each row contains a mapping from a VerbNet class to a BSO semantic class:
- **Column 1**: VerbNet class ID (e.g., "fit-54.3")
- **Column 2**: BSO semantic class name (e.g., "Sleep State")
- **Column 3**: Number of verb members in this mapping (e.g., "2")
- **Column 4**: List of verb members as a Python list string (e.g., "['hibernate', 'sleep']")

**Example entries**:
```csv
fit-54.3,Sleep State,2,"['hibernate', 'sleep']"
fit-54.3,Winning Activity,1,"['take']"
invest-13.5.4,Give Activity,2,"['invest', 'allocate']"
```

## Data Format and Structure

Both files follow a consistent CSV format:

1. **No header row**: Data starts immediately
2. **Comma-separated values**: Fields are separated by commas
3. **Quoted member lists**: The fourth column containing verb lists is enclosed in double quotes
4. **Python list format**: Verb members are stored as string representations of Python lists

### Member List Format
The verb member lists in column 4 are formatted as Python list literals:
```python
"['verb1', 'verb2', 'verb3', ...]"
```

## Semantic Categories

The BSO corpus organizes verbs into broad semantic categories such as:

- **Emotional states and causation**: "Cause Negative Feeling", "Cause Positive Feeling"
- **Physical activities**: "Hit Activity", "Manner of Motion", "Dance Activity"
- **Cognitive processes**: "Mental Process", "Know Activity", "Believe Activity"
- **Communication**: "Say Activity", "Talk Activity", "Communicate With Instrument"
- **Change of state**: "Come Into Existence", "Go Out of Existence", "Change of Physical State"
- **And many more...**

## Python Code Examples

### Loading and Basic Processing

```python
import csv
import ast

def load_bso_vn_mapping(file_path):
    """Load BSO to VerbNet mapping from CSV file."""
    mappings = {}
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            bso_class = row[0]
            vn_class = row[1]
            member_count = int(row[2])
            # Convert string representation of list to actual list
            members = ast.literal_eval(row[3])
            
            if bso_class not in mappings:
                mappings[bso_class] = []
            mappings[bso_class].append({
                'vn_class': vn_class,
                'member_count': member_count,
                'members': members
            })
    
    return mappings

def load_vn_bso_mapping(file_path):
    """Load VerbNet to BSO mapping from CSV file."""
    mappings = {}
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            vn_class = row[0]
            bso_class = row[1]
            member_count = int(row[2])
            members = ast.literal_eval(row[3])
            
            if vn_class not in mappings:
                mappings[vn_class] = []
            mappings[vn_class].append({
                'bso_class': bso_class,
                'member_count': member_count,
                'members': members
            })
    
    return mappings

# Usage example
bso_to_vn = load_bso_vn_mapping('BSOVNMapping_withMembers.csv')
vn_to_bso = load_vn_bso_mapping('VNBSOMapping_withMembers.csv')
```

### Finding Verbs by Semantic Category

```python
def get_verbs_for_bso_category(mappings, category):
    """Get all verbs for a specific BSO semantic category."""
    if category not in mappings:
        return []
    
    all_verbs = []
    for mapping in mappings[category]:
        all_verbs.extend(mapping['members'])
    
    return list(set(all_verbs))  # Remove duplicates

# Example: Get all verbs related to causing negative feelings
negative_feeling_verbs = get_verbs_for_bso_category(bso_to_vn, 'Cause Negative Feeling')
print(f"Verbs that cause negative feelings: {negative_feeling_verbs[:10]}...")
```

### Finding Semantic Categories for a VerbNet Class

```python
def get_bso_categories_for_vn_class(mappings, vn_class):
    """Get BSO categories for a specific VerbNet class."""
    if vn_class not in mappings:
        return []
    
    return [mapping['bso_class'] for mapping in mappings[vn_class]]

# Example: Get semantic categories for the 'amuse-31.1' VerbNet class
categories = get_bso_categories_for_vn_class(vn_to_bso, 'amuse-31.1')
print(f"BSO categories for amuse-31.1: {categories}")
```

### Statistical Analysis

```python
def analyze_bso_coverage(bso_mappings):
    """Analyze the distribution of BSO categories."""
    stats = {}
    total_mappings = 0
    total_verbs = 0
    
    for category, mappings in bso_mappings.items():
        verb_count = sum(mapping['member_count'] for mapping in mappings)
        vn_class_count = len(mappings)
        
        stats[category] = {
            'vn_classes': vn_class_count,
            'total_verbs': verb_count,
            'avg_verbs_per_class': verb_count / vn_class_count if vn_class_count > 0 else 0
        }
        
        total_mappings += vn_class_count
        total_verbs += verb_count
    
    return stats, total_mappings, total_verbs

# Analyze the corpus
stats, total_mappings, total_verbs = analyze_bso_coverage(bso_to_vn)
print(f"Total BSO categories: {len(stats)}")
print(f"Total VerbNet class mappings: {total_mappings}")
print(f"Total verb instances: {total_verbs}")
```

### Integration with MongoDB (as used in the project)

Based on the project's usage in `build_mongo_collections.py`:

```python
def build_bso_mongo_dict(csv_path):
    """Build BSO dictionary as used in the project's MongoDB integration."""
    bso_mongo = {}
    
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            vn_class = row[0]
            bso_class = row[1]
            member_count = row[2]
            members_str = row[3]
            
            if vn_class not in bso_mongo:
                bso_mongo[vn_class] = [[bso_class, member_count, members_str]]
            else:
                bso_mongo[vn_class].append([bso_class, member_count, members_str])
    
    return bso_mongo

# Usage
bso_dict = build_bso_mongo_dict('VNBSOMapping_withMembers.csv')
```

## Research Applications

The BSO corpus enables various research applications:

1. **Semantic verb clustering**: Group verbs by broad semantic categories
2. **Cross-linguistic studies**: Compare verb organization across languages
3. **Computational semantics**: Enhance NLP systems with semantic knowledge
4. **Lexical resource development**: Build semantic dictionaries and thesauri
5. **Cognitive studies**: Investigate human conceptualization of verb meanings

## Data Quality and Coverage

- Contains mappings for hundreds of VerbNet classes
- Covers thousands of individual verb tokens
- Provides hierarchical semantic organization
- Includes frequency information through member counts
- Bidirectional mappings ensure comprehensive access

## Notes for Researchers

1. **List parsing**: Remember to use `ast.literal_eval()` to safely parse the verb member lists
2. **Encoding**: Files use UTF-8 encoding
3. **Duplicates**: Some verbs may appear in multiple semantic categories
4. **Integration**: This data integrates with the broader UVI (Unified Verb Index) project
5. **Version**: Check project documentation for version information and updates