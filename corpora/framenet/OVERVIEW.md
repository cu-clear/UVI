# FrameNet Release 1.7 - Data Overview

## Introduction

FrameNet is a lexical database based on the theory of Frame Semantics developed by Charles Fillmore. This corpus contains Release 1.7 of the FrameNet data, which includes over 1,200 semantic frames, 13,570+ lexical units, and extensive annotations of real-world text examples.

## Directory Structure

### Root Level Files

- **README.txt** - Official release notes and getting started guide
- **frameIndex.xml** - Main index of all semantic frames in the database
- **frameIndex.xsl** - XSL stylesheet for viewing frameIndex.xml in browsers
- **luIndex.xml** - Index of all lexical units (LUs) in the database  
- **luIndex.xsl** - XSL stylesheet for viewing luIndex.xml
- **fulltextIndex.xml** - Index of full-text annotated documents
- **fulltextIndex.xsl** - XSL stylesheet for viewing fulltextIndex.xml
- **frRelation.xml** - Frame-to-frame relations data
- **semTypes.xml** - Semantic types and their hierarchical relations

### Main Data Directories

```
framenet/
├── docs/                    # Documentation and manuals
├── frame/                   # Individual frame definitions (1,221 files)
├── lu/                      # Lexical unit definitions (13,572 files)  
├── fulltext/                # Full-text annotated documents (107 files)
└── schema/                  # XML Schema definitions (XSD files)
```

## Data Structure and File Formats

### 1. Semantic Frames (`frame/` directory)

Each semantic frame is defined in an individual XML file named after the frame (e.g., `Activity.xml`, `Motion.xml`).

**Frame File Structure:**
- **Frame definition** - Conceptual description of the semantic frame
- **Frame Elements (FEs)** - Core participants and peripheral elements
- **Semantic types** - Categorization information
- **Frame relations** - Inheritance, usage, and other inter-frame relationships

**Example Frame Elements:**
```xml
<FE bgColor="FF0000" fgColor="FFFFFF" coreType="Core" name="Agent" ID="1617">
    <definition>The Agent is engaged in the Activity.</definition>
    <semType name="Sentient" ID="5"/>
</FE>
```

### 2. Lexical Units (`lu/` directory)

Lexical units represent word senses that evoke specific frames. Each LU file contains:

- **Header** - Frame element definitions with color coding
- **Definition** - Dictionary-style definition
- **Lexeme** - The base word form and part of speech
- **Valences** - Grammatical patterns and frame element realizations
- **Annotation sets** - Links to example sentences

**Key Components:**
- **Valence patterns** - How frame elements are grammatically realized
- **Annotation statistics** - Total number of annotated examples
- **Cross-references** - Links to frames and related LUs

### 3. Full-Text Documents (`fulltext/` directory)

Contains complete documents with comprehensive frame-semantic annotations:

**Document Sources:**
- **ANC** (American National Corpus) - Various text types
- **PropBank** - Proposition Bank examples  
- **WikiTexts** - Wikipedia articles
- **NTI** - Nuclear Threat Initiative documents
- **KBEval** - Knowledge Base evaluation texts
- **LUCorpus** - Lexical unit corpus examples

**Annotation Layers:**
- **Target** - The word or phrase that evokes the frame
- **Frame Elements (FE)** - Semantic roles with color coding
- **Grammatical Function (GF)** - Syntactic roles (Ext, Obj, Dep, etc.)
- **Phrase Type (PT)** - Syntactic categories (NP, PP, etc.)
- **PENN** - Penn Treebank POS tags
- **NER** - Named Entity Recognition
- **WSL** - Word Sense Labels

### 4. XML Schema (`schema/` directory)

Defines the structure and validation rules for all XML data:

- **commonTypes.xsd** - Shared type definitions
- **header.xsd** - Common header structures
- **sentence.xsd** - Sentence annotation structures
- **frame.xsd** - Frame definition schema
- **lexUnit.xsd** - Lexical unit schema  
- **fullText.xsd** - Full-text annotation schema
- **frameRelations.xsd** - Frame relation schema
- **semTypes.xsd** - Semantic type schema
- **frameIndex.xsd**, **luIndex.xsd**, **fulltextIndex.xsd** - Index schemas

### 5. Semantic Types (`semTypes.xml`)

Hierarchical classification system with 200+ types organized into categories:

**Major Categories:**
- **Sentient** - Living beings capable of perception
- **Physical_object** - Concrete entities
- **Event** - Temporal occurrences
- **State** - Static situations
- **Artifact** - Human-made objects
- **Location** - Spatial entities

## Loading and Working with FrameNet Data

### Python Interface Examples

#### Basic XML Parsing
```python
import xml.etree.ElementTree as ET
from pathlib import Path

# Parse a frame file
def load_frame(frame_name):
    frame_path = Path("framenet/frame") / f"{frame_name}.xml"
    tree = ET.parse(frame_path)
    root = tree.getroot()
    
    # Extract frame information
    frame_info = {
        'name': root.get('name'),
        'id': root.get('ID'),
        'definition': root.find('.//{http://framenet.icsi.berkeley.edu}definition').text,
        'frame_elements': []
    }
    
    # Extract frame elements
    for fe in root.findall('.//{http://framenet.icsi.berkeley.edu}FE'):
        fe_info = {
            'name': fe.get('name'),
            'id': fe.get('ID'),
            'core_type': fe.get('coreType'),
            'definition': fe.find('.//{http://framenet.icsi.berkeley.edu}definition').text
        }
        frame_info['frame_elements'].append(fe_info)
    
    return frame_info

# Example usage
activity_frame = load_frame("Activity")
print(f"Frame: {activity_frame['name']}")
print(f"Definition: {activity_frame['definition']}")
```

#### Loading Frame Index
```python
def load_frame_index():
    """Load the complete frame index"""
    tree = ET.parse("framenet/frameIndex.xml")
    root = tree.getroot()
    
    frames = {}
    for frame in root.findall('.//{http://framenet.icsi.berkeley.edu}frame'):
        frames[frame.get('name')] = {
            'id': frame.get('ID'),
            'modified_date': frame.get('mDate')
        }
    
    return frames

# Get all available frames
all_frames = load_frame_index()
print(f"Total frames: {len(all_frames)}")
```

#### Loading Lexical Units
```python
def load_lexical_unit(lu_id):
    """Load a specific lexical unit"""
    lu_path = Path("framenet/lu") / f"lu{lu_id}.xml"
    tree = ET.parse(lu_path)
    root = tree.getroot()
    
    return {
        'name': root.get('name'),
        'pos': root.get('POS'),
        'frame': root.get('frame'),
        'frame_id': root.get('frameID'),
        'total_annotated': int(root.get('totalAnnotated', 0)),
        'definition': root.find('.//{http://framenet.icsi.berkeley.edu}definition').text if root.find('.//{http://framenet.icsi.berkeley.edu}definition') is not None else None
    }

# Example usage
lu = load_lexical_unit(10)  # copy.v
print(f"LU: {lu['name']} ({lu['pos']})")
print(f"Frame: {lu['frame']}")
```

#### Processing Full-Text Annotations
```python
def load_fulltext_document(doc_name):
    """Load a full-text annotated document"""
    doc_path = Path("framenet/fulltext") / f"{doc_name}.xml"
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    document = {
        'sentences': []
    }
    
    for sentence in root.findall('.//{http://framenet.icsi.berkeley.edu}sentence'):
        sent_info = {
            'id': sentence.get('ID'),
            'text': sentence.find('.//{http://framenet.icsi.berkeley.edu}text').text,
            'annotations': []
        }
        
        # Process frame annotations
        for annot_set in sentence.findall('.//{http://framenet.icsi.berkeley.edu}annotationSet'):
            if annot_set.get('luName'):  # Frame annotation
                annotation = {
                    'lu_name': annot_set.get('luName'),
                    'frame_name': annot_set.get('frameName'),
                    'target': None,
                    'frame_elements': {}
                }
                
                # Extract target
                target_layer = annot_set.find('.//{http://framenet.icsi.berkeley.edu}layer[@name="Target"]')
                if target_layer is not None:
                    target_label = target_layer.find('.//{http://framenet.icsi.berkeley.edu}label')
                    if target_label is not None:
                        annotation['target'] = {
                            'start': int(target_label.get('start')),
                            'end': int(target_label.get('end')),
                            'text': sent_info['text'][int(target_label.get('start')):int(target_label.get('end'))+1]
                        }
                
                # Extract frame elements
                fe_layer = annot_set.find('.//{http://framenet.icsi.berkeley.edu}layer[@name="FE"]')
                if fe_layer is not None:
                    for fe_label in fe_layer.findall('.//{http://framenet.icsi.berkeley.edu}label'):
                        fe_name = fe_label.get('name')
                        annotation['frame_elements'][fe_name] = {
                            'start': int(fe_label.get('start')),
                            'end': int(fe_label.get('end')),
                            'text': sent_info['text'][int(fe_label.get('start')):int(fe_label.get('end'))+1]
                        }
                
                sent_info['annotations'].append(annotation)
        
        document['sentences'].append(sent_info)
    
    return document

# Example usage
doc = load_fulltext_document("ANC__110CYL067")
for sentence in doc['sentences'][:2]:  # Show first 2 sentences
    print(f"Text: {sentence['text']}")
    for annotation in sentence['annotations']:
        print(f"  Frame: {annotation['frame_name']}")
        print(f"  LU: {annotation['lu_name']}")
        if annotation['target']:
            print(f"  Target: {annotation['target']['text']}")
```

#### Working with Semantic Types
```python
def load_semantic_types():
    """Load the semantic type hierarchy"""
    tree = ET.parse("framenet/semTypes.xml")
    root = tree.getroot()
    
    sem_types = {}
    for sem_type in root.findall('.//{http://framenet.icsi.berkeley.edu}semType'):
        type_info = {
            'name': sem_type.get('name'),
            'id': sem_type.get('ID'),
            'abbrev': sem_type.get('abbrev'),
            'definition': sem_type.find('.//{http://framenet.icsi.berkeley.edu}definition').text if sem_type.find('.//{http://framenet.icsi.berkeley.edu}definition') is not None else None,
            'super_types': []
        }
        
        # Extract super types
        for super_type in sem_type.findall('.//{http://framenet.icsi.berkeley.edu}superType'):
            type_info['super_types'].append({
                'id': super_type.get('supID'),
                'name': super_type.get('superTypeName')
            })
        
        sem_types[type_info['name']] = type_info
    
    return sem_types

# Example usage
sem_types = load_semantic_types()
sentient_type = sem_types.get('Sentient')
if sentient_type:
    print(f"Type: {sentient_type['name']}")
    print(f"Definition: {sentient_type['definition']}")
```

### Advanced Analysis Examples

#### Frame Relationship Analysis
```python
def analyze_frame_relations():
    """Analyze frame-to-frame relationships"""
    tree = ET.parse("framenet/frRelation.xml")
    root = tree.getroot()
    
    relations = {}
    for rel in root.findall('.//{http://framenet.icsi.berkeley.edu}frameRelation'):
        rel_type = rel.get('type')
        if rel_type not in relations:
            relations[rel_type] = []
        
        super_frame = rel.find('.//{http://framenet.icsi.berkeley.edu}frameRelation').get('superFrameName')
        sub_frame = rel.find('.//{http://framenet.icsi.berkeley.edu}frameRelation').get('subFrameName')
        
        relations[rel_type].append({
            'super': super_frame,
            'sub': sub_frame
        })
    
    return relations
```

#### Statistics and Corpus Analysis
```python
def get_corpus_statistics():
    """Generate basic statistics about the FrameNet corpus"""
    # Count frames
    frame_count = len(list(Path("framenet/frame").glob("*.xml")))
    
    # Count lexical units
    lu_count = len(list(Path("framenet/lu").glob("*.xml")))
    
    # Count full-text documents
    fulltext_count = len(list(Path("framenet/fulltext").glob("*.xml")))
    
    return {
        'total_frames': frame_count,
        'total_lexical_units': lu_count,
        'total_fulltext_docs': fulltext_count
    }

stats = get_corpus_statistics()
print(f"FrameNet Statistics:")
print(f"  Frames: {stats['total_frames']}")
print(f"  Lexical Units: {stats['total_lexical_units']}")
print(f"  Full-text Documents: {stats['total_fulltext_docs']}")
```

## Usage Notes

### Viewing Data in Browser
All XML files include XSL stylesheets for browser viewing:
1. Open any index file (frameIndex.xml, luIndex.xml, fulltextIndex.xml) in a modern web browser
2. Navigate through the dynamically generated reports
3. Compatible browsers: Firefox, Chrome, Safari (see docs/GeneralReleaseNotes1.7.pdf)

### XML Namespace
All XML files use the namespace: `http://framenet.icsi.berkeley.edu`

### Character Encoding
All files use UTF-8 encoding

### Data Validation
XML files are validated against XSD schemas in the `schema/` directory

## Key Resources

- **Main Documentation**: `docs/book.pdf` (FrameNet II: Extended Theory and Practice)
- **XML Format Details**: `docs/R1.5XMLDocumentation.txt`
- **Release Notes**: `docs/GeneralReleaseNotes1.7.pdf`
- **FrameNet Website**: http://framenet.icsi.berkeley.edu

## Data Statistics (Release 1.7)

- **Semantic Frames**: 1,221
- **Lexical Units**: 13,572  
- **Frame Elements**: Thousands across all frames
- **Annotated Sentences**: Tens of thousands
- **Full-text Documents**: 107
- **Semantic Types**: 200+