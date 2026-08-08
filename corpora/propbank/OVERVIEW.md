# PropBank Corpus Overview

## Introduction

The PropBank (Proposition Bank) corpus is a comprehensive collection of semantic role annotations for English verbs, adjectives, and nouns. This corpus provides detailed information about predicate-argument structures, enabling natural language processing applications to understand the semantic relationships between predicates and their arguments.

## File Hierarchy

```
propbank/
├── LICENSE                    # Creative Commons Attribution-ShareAlike 4.0 International License
├── README.md                  # Brief repository description and contact information
├── OVERVIEW.md               # This comprehensive documentation file
└── frames/                   # Directory containing all predicate frame definitions
    ├── frameset.dtd          # XML Document Type Definition for frame structure
    └── [7,311 XML files]     # Individual predicate frame files
        ├── abandon.xml       # Frame for "abandon" predicate
        ├── accept.xml        # Frame for "accept" predicate
        ├── be.xml            # Frame for "be" predicate
        ├── 1500.xml          # Frame for numeric predicate "1500"
        └── ...               # Additional frame files (alphabetically organized)
```

## Data Format and Structure

### XML Frame Files

Each predicate has its own XML file containing comprehensive semantic information:

#### Document Structure
- **DOCTYPE Declaration**: References `frameset.dtd` for XML validation
- **Root Element**: `<frameset>` containing one or more predicates
- **Predicate Elements**: Define different senses and argument structures

#### Key Components

##### 1. Predicate Definition
```xml
<predicate lemma="abandon">
    <!-- Contains one or more rolesets -->
</predicate>
```

##### 2. Rolesets
Each roleset represents a distinct sense of the predicate:
```xml
<roleset id="abandon.01" name="leave behind">
    <aliases>...</aliases>
    <note>...</note>
    <roles>...</roles>
    <example>...</example>
</roleset>
```

##### 3. Semantic Roles
Numbered arguments (0-6) and modifier arguments (M):
```xml
<role descr="abandoner" f="ppt" n="0">
    <vnrole vncls="51.2" vntheta="theme"/>
</role>
```

**Function Tags (f attribute):**
- `PAG`: Prototypical agent
- `PPT`: Prototypical patient  
- `GOL`: Goal
- `DIR`: Direction
- `LOC`: Location
- `TMP`: Temporal
- `MNR`: Manner
- `CAU`: Cause
- `PRP`: Purpose
- `COM`: Comitative
- `EXT`: Extent
- And others (see DTD for complete list)

##### 4. Cross-Reference Mappings
- **VerbNet Classes**: Links to VerbNet semantic classes
- **FrameNet**: Connections to FrameNet semantic frames
- **Aliases**: Alternative forms (verb, noun, adjective variants)

##### 5. Annotated Examples
Real sentences with argument structure markup:
```xml
<example name="typical transitive" src="" type="">
    <text>And they believe the Big Board, under Mr. Phelan, has abandoned their interest.</text>
    <arg f="" n="0">the Big Board</arg>
    <arg f="adv" n="m">under Mr. Phelan</arg>
    <rel f="">abandoned</rel>
    <arg f="" n="1">their interest</arg>
</example>
```

### DTD Schema (frameset.dtd)

The Document Type Definition defines the XML structure and constraints:

**Main Elements:**
- `frameset`: Root element
- `predicate`: Individual predicate definition
- `roleset`: Specific sense/usage of predicate
- `role`: Semantic role definition
- `example`: Annotated sentence example
- `arg`: Argument span in example
- `rel`: Predicate span in example

**Key Attributes:**
- Role numbers: 0-6 for core arguments, M for modifiers
- Function tags: Semantic role types
- VerbNet/FrameNet references: Cross-corpus mappings

## Data Content and Coverage

### Corpus Statistics
- **Total Frame Files**: 7,311 XML files
- **Predicate Types**: Verbs, nouns, adjectives, and numeric expressions
- **Coverage**: Major English predicates with multiple senses

### Predicate Categories

1. **Verbal Predicates**: Most common (e.g., abandon, accept, be)
2. **Nominal Predicates**: Nominalizations and event nouns
3. **Adjectival Predicates**: Adjectives with argument structure
4. **Numeric Predicates**: Quantity expressions (e.g., 1500.xml)

### Linguistic Information

Each frame provides:
- **Semantic Roles**: Core arguments and adjuncts
- **Selectional Restrictions**: Constraints on argument types  
- **Syntactic Patterns**: Common phrase structures
- **Cross-Linguistic Mappings**: VerbNet and FrameNet connections
- **Usage Examples**: Real-world sentence contexts

## Python Interface Examples

### Basic Frame Loading

```python
import xml.etree.ElementTree as ET
import os
from pathlib import Path

class PropBankFrame:
    def __init__(self, xml_file_path):
        """Load a PropBank frame from XML file."""
        self.tree = ET.parse(xml_file_path)
        self.root = self.tree.getroot()
        self.lemma = self.root.find('predicate').get('lemma')
        
    def get_rolesets(self):
        """Extract all rolesets for this predicate."""
        rolesets = []
        for predicate in self.root.findall('predicate'):
            for roleset in predicate.findall('roleset'):
                rolesets.append({
                    'id': roleset.get('id'),
                    'name': roleset.get('name'),
                    'roles': self._extract_roles(roleset),
                    'examples': self._extract_examples(roleset)
                })
        return rolesets
    
    def _extract_roles(self, roleset):
        """Extract semantic roles from a roleset."""
        roles = []
        roles_elem = roleset.find('roles')
        if roles_elem is not None:
            for role in roles_elem.findall('role'):
                roles.append({
                    'number': role.get('n'),
                    'function': role.get('f'),
                    'description': role.get('descr'),
                    'vnroles': [vn.get('vncls') for vn in role.findall('vnrole')]
                })
        return roles
    
    def _extract_examples(self, roleset):
        """Extract annotated examples from a roleset."""
        examples = []
        for example in roleset.findall('example'):
            text_elem = example.find('text')
            if text_elem is not None:
                examples.append({
                    'name': example.get('name'),
                    'text': text_elem.text,
                    'arguments': [
                        {'n': arg.get('n'), 'f': arg.get('f'), 'text': arg.text}
                        for arg in example.findall('arg')
                    ],
                    'predicate': example.find('rel').text if example.find('rel') is not None else None
                })
        return examples

# Usage example
frames_dir = Path("C:/path-to-repo-here/UVI/corpora/propbank/frames")
frame = PropBankFrame(frames_dir / "abandon.xml")
print(f"Predicate: {frame.lemma}")
for roleset in frame.get_rolesets():
    print(f"  Roleset {roleset['id']}: {roleset['name']}")
    print(f"    Roles: {len(roleset['roles'])}")
    print(f"    Examples: {len(roleset['examples'])}")
```

### Corpus-Wide Analysis

```python
class PropBankCorpus:
    def __init__(self, frames_directory):
        """Initialize corpus with frames directory path."""
        self.frames_dir = Path(frames_directory)
        
    def get_all_predicates(self):
        """Get list of all predicates in the corpus."""
        predicates = []
        for xml_file in self.frames_dir.glob("*.xml"):
            if xml_file.name != "frameset.dtd":  # Skip DTD file
                predicates.append(xml_file.stem)
        return sorted(predicates)
    
    def search_by_role_pattern(self, min_roles=3):
        """Find predicates with at least min_roles semantic roles."""
        matching_predicates = []
        for xml_file in self.frames_dir.glob("*.xml"):
            if xml_file.name == "frameset.dtd":
                continue
            try:
                frame = PropBankFrame(xml_file)
                for roleset in frame.get_rolesets():
                    if len(roleset['roles']) >= min_roles:
                        matching_predicates.append({
                            'lemma': frame.lemma,
                            'roleset_id': roleset['id'],
                            'role_count': len(roleset['roles'])
                        })
            except ET.ParseError:
                continue
        return matching_predicates
    
    def get_statistics(self):
        """Generate corpus statistics."""
        total_predicates = 0
        total_rolesets = 0
        total_examples = 0
        
        for xml_file in self.frames_dir.glob("*.xml"):
            if xml_file.name == "frameset.dtd":
                continue
            try:
                frame = PropBankFrame(xml_file)
                total_predicates += 1
                rolesets = frame.get_rolesets()
                total_rolesets += len(rolesets)
                total_examples += sum(len(rs['examples']) for rs in rolesets)
            except ET.ParseError:
                continue
                
        return {
            'total_predicates': total_predicates,
            'total_rolesets': total_rolesets,
            'total_examples': total_examples,
            'avg_rolesets_per_predicate': total_rolesets / total_predicates if total_predicates > 0 else 0
        }

# Usage example
corpus = PropBankCorpus("C:/path-to-repo-here/UVI/corpora/propbank/frames")
stats = corpus.get_statistics()
print("PropBank Corpus Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")
```

### Role-Based Search

```python
def find_predicates_with_role_type(frames_dir, function_tag):
    """Find all predicates that have arguments with specified function tag."""
    results = []
    frames_path = Path(frames_dir)
    
    for xml_file in frames_path.glob("*.xml"):
        if xml_file.name == "frameset.dtd":
            continue
        try:
            frame = PropBankFrame(xml_file)
            for roleset in frame.get_rolesets():
                for role in roleset['roles']:
                    if role['function'] and function_tag.lower() in role['function'].lower():
                        results.append({
                            'lemma': frame.lemma,
                            'roleset_id': roleset['id'],
                            'role_desc': role['description'],
                            'role_number': role['number']
                        })
                        break
        except ET.ParseError:
            continue
    return results

# Find predicates with goal arguments
goal_predicates = find_predicates_with_role_type(
    "C:/path-to-repo-here/UVI/corpora/propbank/frames", 
    "GOL"
)
print(f"Found {len(goal_predicates)} predicates with goal arguments")
```

## Applications and Use Cases

### Natural Language Processing
- **Semantic Role Labeling**: Training and evaluation datasets
- **Information Extraction**: Template-based extraction systems
- **Question Answering**: Understanding predicate-argument relationships
- **Machine Translation**: Cross-lingual argument structure transfer

### Computational Linguistics Research
- **Verb Classification**: Semantic class induction
- **Argument Structure Analysis**: Syntactic-semantic interface studies
- **Cross-Linguistic Comparison**: Typological investigations
- **Corpus Linguistics**: Large-scale semantic pattern analysis

### Educational Resources
- **ESL Instruction**: Verb usage patterns and examples
- **Lexicography**: Dictionary and thesaurus enhancement
- **Linguistic Annotation**: Training materials for annotators

## Related Resources

- **PropBank Documentation**: [https://github.com/propbank/propbank-documentation](https://github.com/propbank/propbank-documentation)
- **VerbNet**: Complementary verb classification resource
- **FrameNet**: Frame-based semantic analysis resource
- **OntoNotes**: Multilingual corpus with PropBank annotations

## License and Usage

This corpus is distributed under the **Creative Commons Attribution-ShareAlike 4.0 International License**. Users are free to:
- Share and redistribute the material
- Adapt, remix, and transform the material
- Use for commercial purposes

**Requirements:**
- Provide appropriate attribution
- Indicate if changes were made
- Distribute contributions under the same license

## Contact Information

For additional releases or questions about the PropBank corpus, contact: **timjogorman@gmail.com**