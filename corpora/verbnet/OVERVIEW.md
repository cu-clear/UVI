# VerbNet Corpus Overview

## Introduction

This directory contains the VerbNet corpus, a comprehensive computational lexicon that provides detailed syntactic and semantic information about English verbs. VerbNet classifies English verbs into hierarchical classes based on their syntactic behavior and semantic similarities, making it a valuable resource for natural language processing, computational linguistics, and semantic analysis.

## File Hierarchy and Structure

### Main Content Files
- **331 XML files** (e.g., `absorb-39.8.xml`, `give-13.1.xml`, `break-45.1.xml`)
  - Each XML file represents a distinct verb class
  - Named using the format: `{primary-verb}-{class-number}.xml`
  - Contains complete syntactic and semantic information for the verb class

### Schema and Validation Files
- **`vn_schema-3.xsd`** - XML Schema Definition for VerbNet version 3
  - Defines the structure, data types, and constraints for VerbNet XML files
  - Specifies valid thematic roles, selectional restrictions, syntactic patterns
  - Includes comprehensive enumerations of features, predicates, and argument types

- **`vn_class-3.dtd`** - Document Type Definition for VerbNet classes
  - Provides the formal grammar for VerbNet XML structure
  - Defines element hierarchy and attribute requirements
  - Alternative validation schema to the XSD file

- **`vn_class-3.dtd~`** - Backup copy of the DTD file

## XML File Structure and Format

Each VerbNet class XML file follows a consistent hierarchical structure:

### Root Element: `<VNCLASS>`
- **Attributes:**
  - `ID`: Unique identifier for the verb class (e.g., "give-13.1")
  - `xmlns:xsi` and `xsi:noNamespaceSchemaLocation`: XML schema references

### Main Sections

#### 1. `<MEMBERS>` Section
Contains individual verbs belonging to this class:
```xml
<MEMBER 
    name="give" 
    wn="give%2:40:03 give%2:40:00" 
    grouping="give.01 give.08" 
    fn_mapping="Giving" 
    verbnet_key="give#3" 
    features="None"/>
```

**Attributes:**
- `name`: The verb lemma
- `wn`: WordNet sense keys (space-separated)
- `grouping`: PropBank predicate mappings
- `fn_mapping`: FrameNet frame mappings
- `verbnet_key`: Unique VerbNet identifier
- `features`: Special semantic or syntactic features

#### 2. `<THEMROLES>` Section
Defines thematic roles (semantic participants) for the class:
```xml
<THEMROLE type="Agent">
    <SELRESTRS logic="or">
        <SELRESTR Value="+" type="animate"/>
        <SELRESTR Value="+" type="organization"/>
    </SELRESTRS>
</THEMROLE>
```

**Common Thematic Roles:**
- Agent, Patient, Theme, Experiencer
- Goal, Source, Destination, Location
- Instrument, Beneficiary, Recipient
- And many more specific roles

**Selectional Restrictions:**
- Define semantic constraints on arguments
- Use `+` (positive) or `-` (negative) values
- Include features like `animate`, `concrete`, `human`, etc.

#### 3. `<FRAMES>` Section
Contains syntactic patterns and their semantic interpretations:

```xml
<FRAME>
    <DESCRIPTION 
        descriptionNumber="0.2" 
        primary="NP V NP PP.recipient" 
        secondary="NP-PP; Recipient-PP" 
        xtag=""/>
    <EXAMPLES>
        <EXAMPLE>They lent a bicycle to me.</EXAMPLE>
    </EXAMPLES>
    <SYNTAX>
        <NP value="Agent"><SYNRESTRS/></NP>
        <VERB/>
        <NP value="Theme"><SYNRESTRS/></NP>
        <PREP value="to"><SELRESTRS/></PREP>
        <NP value="Recipient"><SYNRESTRS/></NP>
    </SYNTAX>
    <SEMANTICS>
        <PRED value="has_possession">
            <ARGS>
                <ARG type="Event" value="e1"/>
                <ARG type="ThemRole" value="Agent"/>
                <ARG type="ThemRole" value="Theme"/>
            </ARGS>
        </PRED>
        <!-- Additional predicates... -->
    </SEMANTICS>
</FRAME>
```

**Frame Components:**
- **DESCRIPTION**: Syntactic pattern classification
- **EXAMPLES**: Natural language examples
- **SYNTAX**: Detailed syntactic structure with argument positions
- **SEMANTICS**: Event-based semantic representation using predicates

#### 4. `<SUBCLASSES>` Section
Contains nested subclasses with additional specificity:
```xml
<SUBCLASSES>
    <VNSUBCLASS ID="give-13.1-1">
        <MEMBERS>...</MEMBERS>
        <THEMROLES>...</THEMROLES>
        <FRAMES>...</FRAMES>
        <SUBCLASSES/>
    </VNSUBCLASS>
</SUBCLASSES>
```

## Key Data Types and Enumerations

### Thematic Roles
The schema defines 70+ thematic role types including:
- Core roles: Agent, Patient, Theme, Experiencer
- Locational: Location, Source, Destination, Goal
- Temporal: Time, Duration, Init_Time, Final_Time
- Optional variants (prefixed with `?`): ?Agent, ?Theme, etc.

### Selectional Restrictions
27 main semantic features for argument selection:
- `abstract`, `animate`, `concrete`, `human`
- `location`, `organization`, `machine`
- `comestible`, `vehicle`, `communication`

### Syntactic Restrictions  
42 syntactic constraint types:
- Complementation: `ac_ing`, `ac_to_inf`, `that_comp`
- Case marking: `genitive`, `definite`
- Construction types: `small_clause`, `quotation`

### Semantic Predicates
200+ semantic predicate types including:
- State predicates: `be`, `has_possession`, `location`
- Change predicates: `becomes`, `cause`, `motion`
- Mental predicates: `believe`, `intend`, `perceive`

## Example Python Interface Code

### Basic XML Parsing

```python
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import glob
import os

class VerbNetClass:
    """Represents a single VerbNet class with its members, roles, and frames."""
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.class_id = self.root.get('ID')
    
    def get_members(self) -> List[Dict[str, str]]:
        """Extract all verb members of this class."""
        members = []
        for member in self.root.find('MEMBERS').findall('MEMBER'):
            members.append({
                'name': member.get('name'),
                'wordnet_keys': member.get('wn', '').split(),
                'grouping': member.get('grouping', ''),
                'framenet_mapping': member.get('fn_mapping', ''),
                'verbnet_key': member.get('verbnet_key', ''),
                'features': member.get('features', '')
            })
        return members
    
    def get_thematic_roles(self) -> List[Dict[str, Any]]:
        """Extract thematic roles and their selectional restrictions."""
        roles = []
        for role in self.root.find('THEMROLES').findall('THEMROLE'):
            role_info = {'type': role.get('type'), 'restrictions': []}
            
            selrestrs = role.find('SELRESTRS')
            if selrestrs is not None:
                for restr in selrestrs.findall('.//SELRESTR'):
                    role_info['restrictions'].append({
                        'type': restr.get('type'),
                        'value': restr.get('Value')
                    })
            
            roles.append(role_info)
        return roles
    
    def get_frames(self) -> List[Dict[str, Any]]:
        """Extract syntactic frames with examples and semantics."""
        frames = []
        for frame in self.root.find('FRAMES').findall('FRAME'):
            frame_info = {
                'description': self._get_frame_description(frame),
                'examples': [ex.text.strip() for ex in frame.find('EXAMPLES').findall('EXAMPLE')],
                'syntax': self._get_frame_syntax(frame),
                'semantics': self._get_frame_semantics(frame)
            }
            frames.append(frame_info)
        return frames
    
    def _get_frame_description(self, frame) -> Dict[str, str]:
        """Extract frame description information."""
        desc = frame.find('DESCRIPTION')
        return {
            'number': desc.get('descriptionNumber', ''),
            'primary': desc.get('primary', ''),
            'secondary': desc.get('secondary', ''),
            'xtag': desc.get('xtag', '')
        }
    
    def _get_frame_syntax(self, frame) -> List[Dict[str, str]]:
        """Extract syntactic structure of the frame."""
        syntax_elements = []
        for element in frame.find('SYNTAX'):
            elem_info = {
                'tag': element.tag,
                'value': element.get('value', ''),
                'restrictions': []
            }
            
            # Get syntactic restrictions
            synrestrs = element.find('SYNRESTRS')
            if synrestrs is not None:
                for restr in synrestrs.findall('SYNRESTR'):
                    elem_info['restrictions'].append({
                        'type': restr.get('type'),
                        'value': restr.get('Value')
                    })
            
            syntax_elements.append(elem_info)
        return syntax_elements
    
    def _get_frame_semantics(self, frame) -> List[Dict[str, Any]]:
        """Extract semantic predicates and their arguments."""
        predicates = []
        semantics = frame.find('SEMANTICS')
        if semantics is not None:
            for pred in semantics.findall('PRED'):
                pred_info = {
                    'value': pred.get('value'),
                    'bool': pred.get('bool', ''),
                    'args': []
                }
                
                args_elem = pred.find('ARGS')
                if args_elem is not None:
                    for arg in args_elem.findall('ARG'):
                        pred_info['args'].append({
                            'type': arg.get('type'),
                            'value': arg.get('value')
                        })
                
                predicates.append(pred_info)
        return predicates

class VerbNetCorpus:
    """Main interface for the VerbNet corpus."""
    
    def __init__(self, verbnet_dir: str):
        self.verbnet_dir = verbnet_dir
        self.class_files = glob.glob(os.path.join(verbnet_dir, "*.xml"))
        # Remove schema files
        self.class_files = [f for f in self.class_files 
                           if not f.endswith(('vn_schema-3.xsd', 'vn_class-3.dtd'))]
    
    def load_class(self, class_id: str) -> VerbNetClass:
        """Load a specific VerbNet class by ID."""
        for file_path in self.class_files:
            if class_id in os.path.basename(file_path):
                return VerbNetClass(file_path)
        raise ValueError(f"Class {class_id} not found")
    
    def find_verb_classes(self, verb: str) -> List[str]:
        """Find all classes containing the specified verb."""
        classes = []
        for file_path in self.class_files:
            vn_class = VerbNetClass(file_path)
            members = vn_class.get_members()
            if any(member['name'] == verb for member in members):
                classes.append(vn_class.class_id)
        return classes
    
    def get_all_classes(self) -> List[str]:
        """Get IDs of all available classes."""
        classes = []
        for file_path in self.class_files:
            class_name = os.path.basename(file_path).replace('.xml', '')
            classes.append(class_name)
        return sorted(classes)
    
    def search_by_predicate(self, predicate: str) -> List[str]:
        """Find classes that use a specific semantic predicate."""
        matching_classes = []
        for file_path in self.class_files:
            vn_class = VerbNetClass(file_path)
            frames = vn_class.get_frames()
            for frame in frames:
                if any(pred['value'] == predicate for pred in frame['semantics']):
                    matching_classes.append(vn_class.class_id)
                    break
        return matching_classes
```

### Usage Examples

```python
# Initialize the corpus
verbnet_dir = "C:/path-to-repo-here/UVI/corpora/verbnet"
corpus = VerbNetCorpus(verbnet_dir)

# Load a specific class
give_class = corpus.load_class("give-13.1")
print(f"Class: {give_class.class_id}")

# Get verb members
members = give_class.get_members()
for member in members:
    print(f"Verb: {member['name']}, FrameNet: {member['framenet_mapping']}")

# Get thematic roles
roles = give_class.get_thematic_roles()
for role in roles:
    print(f"Role: {role['type']}")
    for restriction in role['restrictions']:
        print(f"  {restriction['value']}{restriction['type']}")

# Get syntactic frames
frames = give_class.get_frames()
for i, frame in enumerate(frames):
    print(f"Frame {i+1}: {frame['description']['primary']}")
    print(f"Example: {frame['examples'][0] if frame['examples'] else 'No examples'}")

# Find all classes for a specific verb
give_classes = corpus.find_verb_classes("give")
print(f"Classes containing 'give': {give_classes}")

# Search for classes using specific semantic predicates
transfer_classes = corpus.search_by_predicate("transfer")
print(f"Classes with 'transfer' predicate: {transfer_classes[:5]}")  # Show first 5

# Get corpus statistics
all_classes = corpus.get_all_classes()
print(f"Total classes in corpus: {len(all_classes)}")
```

### Advanced Analysis Example

```python
def analyze_class_hierarchy(corpus: VerbNetCorpus, class_id: str):
    """Analyze a class and its subclass structure."""
    vn_class = corpus.load_class(class_id)
    
    print(f"Analysis of {class_id}")
    print("=" * 50)
    
    # Member analysis
    members = vn_class.get_members()
    print(f"Members ({len(members)}):")
    for member in members:
        features = member['features'] if member['features'] != 'None' else 'No special features'
        print(f"  - {member['name']} ({features})")
    
    # Thematic role analysis
    roles = vn_class.get_thematic_roles()
    print(f"\nThematic Roles ({len(roles)}):")
    for role in roles:
        restrictions = ", ".join([f"{r['value']}{r['type']}" for r in role['restrictions']])
        restrictions_str = f" [{restrictions}]" if restrictions else ""
        print(f"  - {role['type']}{restrictions_str}")
    
    # Frame pattern analysis
    frames = vn_class.get_frames()
    print(f"\nSyntactic Patterns ({len(frames)}):")
    for i, frame in enumerate(frames, 1):
        print(f"  {i}. {frame['description']['primary']}")
        if frame['examples']:
            print(f"     Example: \"{frame['examples'][0]}\"")
        
        # Semantic analysis
        predicates = [pred['value'] for pred in frame['semantics']]
        print(f"     Semantics: {', '.join(predicates)}")

# Example usage
analyze_class_hierarchy(corpus, "give-13.1")
```

## Data Characteristics and Coverage

### Corpus Statistics
- **Total Classes**: 331 verb classes
- **Hierarchical Structure**: Classes can contain subclasses for finer-grained distinctions
- **Cross-linguistic Links**: WordNet, FrameNet, and PropBank mappings provided
- **Rich Semantic Annotation**: Event-based semantic representations with detailed predicate structures

### Key Features
1. **Syntactic Diversity**: Covers major English verb alternation patterns
2. **Semantic Precision**: Detailed event structures with thematic role mappings
3. **Linguistic Integration**: Links to major lexical resources
4. **Computational Accessibility**: Well-structured XML format with comprehensive schemas
5. **Extensibility**: Clear hierarchical organization allows for easy extension

## Applications

This VerbNet corpus can be used for:
- Semantic role labeling systems
- Syntactic parsing and grammar development
- Machine translation systems
- Information extraction applications
- Computational semantics research
- Natural language generation
- Lexical resource development

## Version Information

This appears to be VerbNet version 3, as indicated by the schema files (`vn_schema-3.xsd`, `vn_class-3.dtd`). The format includes modern XML Schema definitions with comprehensive validation rules and extensive semantic annotations.