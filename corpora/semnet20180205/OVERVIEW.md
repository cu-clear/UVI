# SemNet 2018-02-05 Corpus Overview

## Description

This directory contains the **SemNet corpus** from February 5, 2018, which provides semantic network data for English nouns and verbs. The corpus consists of two main JSON files containing structured semantic information including ontological hierarchies, definitions, syntactic frames, and thematic roles for lexical items.

## File Hierarchy

```
semnet20180205/
├── noun-semnet.json    (786 KB)  - Semantic data for 3,530 nouns
├── verb-semnet.json    (3.2 MB)  - Semantic data for 4,569 verbs
└── OVERVIEW.md         (this file)
```

## File Contents and Purpose

### noun-semnet.json
Contains semantic information for **3,530 noun entries**. Each noun is mapped to semantic data including:
- **SUMO ontology parents**: Hierarchical categorization in the Suggested Upper Merged Ontology
- **Wiktionary definitions**: Human-readable definitions extracted from Wiktionary

### verb-semnet.json  
Contains semantic information for **4,569 verb entries**. Each verb contains multiple sense entries (verb classes) with detailed linguistic annotations including:
- **Thematic roles**: Semantic roles like Agent, Theme, Goal, etc.
- **Syntactic frames**: Subcategorization patterns (e.g., "NP V NP", "NP V PP.destination")
- **WordNet synsets**: Groups of synonymous words
- **FrameNet frames**: Semantic frame annotations
- **Common objects**: Frequently occurring direct objects
- **Ontological definitions**: Semantic descriptions

## Data Format and Structure

### Noun Entries Structure

```json
{
  "noun_lemma": {
    "sumo_parent": ["parent_category1", "parent_category2"],
    "wiktionary_def": ["definition1", "definition2", "..."]
  }
}
```

**Fields:**
- `sumo_parent`: List of parent categories in SUMO ontology hierarchy
- `wiktionary_def`: List of definition strings from Wiktionary (may be empty)

### Verb Entries Structure

```json
{
  "verb_lemma": {
    "verb_class_id": {
      "wn": ["wordnet_sense_key"],
      "themroles": ["Agent", "Theme", "Goal"],
      "restrictions": ["selectional_restrictions"],
      "fn_frame": "FrameNet_frame_name",
      "predicates": ["semantic_predicate"],
      "syn_frames": ["NP V NP", "NP V PP.destination"],
      "vs_features": ["verbnet_features"],
      "wn_synset": ["synonym1", "synonym2"],
      "wn_supertype": ["hypernym1"],
      "common_objects": ["object1", "object2"],
      "on_definition": ["human_readable_definition"]
    }
  }
}
```

**Fields:**
- `wn`: WordNet sense keys identifying specific word senses
- `themroles`: Thematic/semantic roles (Agent, Patient, Theme, Source, Goal, etc.)
- `restrictions`: Selectional restrictions on arguments (e.g., "+animate")
- `fn_frame`: FrameNet frame name for semantic frame annotation
- `predicates`: Semantic predicates representing the verb's meaning
- `syn_frames`: Syntactic subcategorization frames showing argument structure
- `vs_features`: VerbNet-style semantic features
- `wn_synset`: WordNet synset members (synonymous verbs)
- `wn_supertype`: WordNet hypernyms (more general verbs)
- `common_objects`: Frequently occurring direct objects from corpus data
- `on_definition`: Human-readable semantic definitions

## Example Python Code for Data Access

### Loading and Exploring Noun Data

```python
import json
from collections import Counter

# Load noun semantic network
with open('noun-semnet.json', 'r', encoding='utf-8') as f:
    noun_data = json.load(f)

print(f"Total nouns: {len(noun_data)}")

# Explore a specific noun
noun = "computer"
if noun in noun_data:
    print(f"\n{noun}:")
    print(f"  SUMO parents: {noun_data[noun]['sumo_parent']}")
    print(f"  Definitions: {len(noun_data[noun]['wiktionary_def'])}")
    for i, defn in enumerate(noun_data[noun]['wiktionary_def'][:3]):
        print(f"    {i+1}. {defn}")

# Find most common SUMO categories
all_parents = []
for entry in noun_data.values():
    all_parents.extend(entry['sumo_parent'])

print(f"\nTop 10 SUMO categories:")
for category, count in Counter(all_parents).most_common(10):
    print(f"  {category}: {count}")

# Find nouns with specific SUMO parent
devices = [noun for noun, data in noun_data.items() 
           if 'device' in data['sumo_parent']]
print(f"\nNouns categorized as 'device': {devices[:10]}")
```

### Loading and Exploring Verb Data

```python
import json
from collections import defaultdict

# Load verb semantic network
with open('verb-semnet.json', 'r', encoding='utf-8') as f:
    verb_data = json.load(f)

print(f"Total verbs: {len(verb_data)}")

# Explore a specific verb
verb = "understand"
if verb in verb_data:
    print(f"\n{verb} has {len(verb_data[verb])} verb classes:")
    for class_id, class_data in verb_data[verb].items():
        print(f"  {class_id}:")
        print(f"    Thematic roles: {class_data['themroles']}")
        print(f"    Syntactic frames: {class_data['syn_frames']}")
        print(f"    Common objects: {class_data['common_objects'][:5]}")
        if class_data['on_definition']:
            print(f"    Definition: {class_data['on_definition'][0]}")

# Find verbs with specific thematic role patterns
motion_verbs = []
for verb, classes in verb_data.items():
    for class_id, class_data in classes.items():
        if 'Source' in class_data['themroles'] and 'Destination' in class_data['themroles']:
            motion_verbs.append(verb)
            break

print(f"\nMotion verbs (Source + Destination): {motion_verbs[:10]}")

# Analyze syntactic frame patterns
frame_counts = defaultdict(int)
for verb, classes in verb_data.items():
    for class_data in classes.values():
        for frame in class_data['syn_frames']:
            frame_counts[frame] += 1

print(f"\nTop 10 syntactic frames:")
for frame, count in sorted(frame_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {frame}: {count}")
```

### Advanced Analysis Examples

```python
# Find verbs that can take animate agents
def has_animate_restriction(class_data):
    return any('+animate' in str(r) for r in class_data['restrictions'])

animate_agent_verbs = []
for verb, classes in verb_data.items():
    if any(has_animate_restriction(class_data) for class_data in classes.values()):
        animate_agent_verbs.append(verb)

print(f"Verbs requiring animate agents: {animate_agent_verbs[:10]}")

# Extract semantic predicates
all_predicates = set()
for verb, classes in verb_data.items():
    for class_data in classes.values():
        all_predicates.update(class_data['predicates'])

print(f"\nUnique semantic predicates ({len(all_predicates)}): {sorted(list(all_predicates))[:15]}")

# Find verbs associated with specific FrameNet frames
framenet_verbs = defaultdict(list)
for verb, classes in verb_data.items():
    for class_data in classes.values():
        frame = class_data.get('fn_frame', '')
        if frame:
            framenet_verbs[frame].append(verb)

print(f"\nFrameNet frames with most verbs:")
for frame, verbs in sorted(framenet_verbs.items(), 
                          key=lambda x: len(x[1]), reverse=True)[:5]:
    print(f"  {frame}: {len(verbs)} verbs - {verbs[:5]}")
```

### Utility Functions for Data Exploration

```python
def find_nouns_by_sumo_category(noun_data, category):
    """Find all nouns belonging to a specific SUMO category."""
    return [noun for noun, data in noun_data.items() 
            if category in data['sumo_parent']]

def find_verbs_by_frame_pattern(verb_data, pattern):
    """Find verbs that use a specific syntactic frame pattern."""
    matching_verbs = []
    for verb, classes in verb_data.items():
        for class_data in classes.values():
            if any(pattern in frame for frame in class_data['syn_frames']):
                matching_verbs.append(verb)
                break
    return matching_verbs

def get_verb_object_associations(verb_data, min_frequency=5):
    """Extract verb-object associations above a frequency threshold."""
    verb_objects = defaultdict(lambda: defaultdict(int))
    for verb, classes in verb_data.items():
        all_objects = []
        for class_data in classes.values():
            all_objects.extend(class_data['common_objects'])
        
        for obj in all_objects:
            verb_objects[verb][obj] += 1
    
    # Filter by minimum frequency
    filtered_associations = {}
    for verb, objects in verb_objects.items():
        frequent_objects = {obj: freq for obj, freq in objects.items() 
                          if freq >= min_frequency}
        if frequent_objects:
            filtered_associations[verb] = frequent_objects
    
    return filtered_associations

# Usage examples
devices = find_nouns_by_sumo_category(noun_data, 'device')
transitive_verbs = find_verbs_by_frame_pattern(verb_data, 'NP V NP')
verb_objects = get_verb_object_associations(verb_data)
```

## Data Sources and Annotation

The SemNet corpus integrates multiple lexical resources:

- **SUMO (Suggested Upper Merged Ontology)**: Provides hierarchical semantic categories
- **WordNet**: Contributes synsets, hypernyms, and sense distinctions
- **FrameNet**: Supplies semantic frame annotations
- **VerbNet**: Provides verb classes, thematic roles, and syntactic frames
- **Wiktionary**: Contributes human-readable definitions
- **Corpus statistics**: Common object patterns derived from corpus analysis

## Use Cases

This semantic network data supports various NLP applications:

1. **Semantic Role Labeling**: Use thematic role information for SRL systems
2. **Word Sense Disambiguation**: Leverage multiple senses and synset information
3. **Semantic Similarity**: Compute similarity using SUMO hierarchies and WordNet relations
4. **Syntactic Parsing**: Utilize subcategorization frames for parsing
5. **Question Answering**: Use semantic predicates and frame information
6. **Information Extraction**: Employ verb-object associations and selectional restrictions
7. **Ontology Construction**: Build domain-specific ontologies using SUMO categories
8. **Language Generation**: Use syntactic frames and common objects for natural generation

## Technical Notes

- **Encoding**: Files are in UTF-8 encoding
- **JSON Format**: Standard JSON with nested dictionaries and lists
- **Memory Usage**: Loading verb-semnet.json requires ~50MB RAM for the full dataset
- **Processing**: Consider streaming or chunked processing for memory-constrained environments
- **Completeness**: Not all fields are populated for every entry (empty lists/strings are common)