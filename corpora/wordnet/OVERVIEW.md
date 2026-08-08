# WordNet 3.0 Corpus Overview

## About WordNet

WordNet is an online lexical reference system developed at Princeton University's Cognitive Science Laboratory under the direction of George Miller. Word forms in WordNet are represented in their familiar orthography, while word meanings are represented by synonym sets (synsets) - lists of synonymous word forms that are interchangeable in some context. The system recognizes both lexical relations (between word forms) and semantic relations (between word meanings).

## License and Citation

This corpus is provided under the Princeton University WordNet 3.0 license, which allows free use, modification, and distribution for any purpose. The copyright remains with Princeton University (2006).

**Citation:**
```bibtex
@book{_Fellbaum:1998,
  booktitle =	 "{WordNet}: An Electronic Lexical Database",
  address =	 "Cambridge, MA",
  editor =	 "Fellbaum, Christiane",
  publisher =	 "MIT Press",
  year =	 1998,
}
```

## File Hierarchy

```
wordnet/
├── LICENSE                    # License text
├── README                     # General information about WordNet
├── citation.bib              # BibTeX citation
├── lexnames                  # Lexicographer file names and numbers
├── cntlist.rev              # Frequency data for word senses
│
├── Main Index Files (used for lookups):
├── index.adj                # Adjective index
├── index.adv                # Adverb index
├── index.noun               # Noun index
├── index.verb               # Verb index
├── index.sense              # Sense key index
│
├── Main Data Files (synset definitions):
├── data.adj                 # Adjective synsets
├── data.adv                 # Adverb synsets
├── data.noun                # Noun synsets
├── data.verb                # Verb synsets
│
├── Exception Files (morphological):
├── adj.exc                  # Adjective exceptions
├── adv.exc                  # Adverb exceptions
├── noun.exc                 # Noun exceptions
├── verb.exc                 # Verb exceptions
│
└── dict/                    # Extended database files
    ├── (duplicate core files)
    ├── cntlist              # Word frequency counts
    ├── sentidx.vrb          # Verb sentence frame index
    ├── sents.vrb            # Verb sentence templates
    ├── verb.Framestext      # Verb frame descriptions
    │
    └── dbfiles/             # Semantic category files
        ├── adj.all          # All adjectives
        ├── adj.pert         # Pertaining adjectives
        ├── adj.ppl          # Participial adjectives
        ├── adv.all          # All adverbs
        ├── noun.Tops        # Top-level noun hierarchy
        ├── noun.{category}  # Noun semantic categories
        └── verb.{category}  # Verb semantic categories
```

## Core Data File Formats

### Index Files (index.{pos})

Index files map word forms to synsets. Each line contains:
```
word_form pos synset_count p_cnt [ptr_symbol...] sense_count synset_offset [synset_offset...]
```

Example from `index.noun`:
```
'hood n 1 2 @ ; 1 0 08641944
```
- `'hood`: word form
- `n`: part of speech (noun)
- `1`: number of synsets
- `2`: number of pointer symbols
- `@`, `;`: pointer symbols (hypernym, domain)
- `1`: sense count
- `0`: tag sense count
- `08641944`: synset offset

### Data Files (data.{pos})

Data files contain synset definitions. Each line represents a synset:
```
synset_offset lex_filenum ss_type w_cnt word lex_id [word lex_id...] p_cnt [ptr...] [frames...] | gloss
```

Example from `data.noun`:
```
00001740 03 n 01 entity 0 003 ~ 00001930 n 0000 ~ 00002137 n 0000 ~ 04424418 n 0000 | that which is perceived or known or inferred to have its own distinct existence (living or nonliving)
```
- `00001740`: synset offset
- `03`: lexicographer file number
- `n`: part of speech
- `01`: word count
- `entity 0`: word and lexical ID
- `003`: pointer count
- `~`: hyponym relation markers
- `|`: gloss separator
- Text after `|`: definition and examples

### Exception Files (*.exc)

Morphological exception lists mapping irregular forms to their base forms:
```
irregular_form base_form
```

Example from `noun.exc`:
```
aardwolves aardwolf
children child
```

### Sense Index (index.sense)

Maps sense keys to synset offsets:
```
sense_key synset_offset sense_number tag_cnt
```

Example:
```
'hood%1:15:00:: 08641944 1 0
```
- `'hood%1:15:00::`: sense key
- `08641944`: synset offset
- `1`: sense number
- `0`: tag count

## Specialized Files

### Lexnames File

Maps lexicographer file numbers to semantic categories:
```
00	adj.all	3
03	noun.Tops	1
29	verb.body	2
```

### Verb Frame Files

**verb.Framestext**: Generic sentence frames for verbs
```
1  Something ----s
2  Somebody ----s
8  Somebody ----s something
```

**sents.vrb**: Specific sentence templates with placeholders
```
1 The children %s to the playground
10 The cars %s down the avenue
```

### Frequency Data (cntlist.rev)

Word sense frequency information:
```
sense_key sense_number tag_cnt
```

## Semantic Relations

WordNet uses various pointer symbols to represent relationships:

- `@`: hypernym (is-a relation)
- `~`: hyponym (reverse is-a)
- `#m`: member meronym (part-whole)
- `#s`: substance meronym
- `#p`: part meronym
- `%m`: member holonym
- `%s`: substance holonym
- `%p`: part holonym
- `=`: attribute
- `+`: derivationally related form
- `!`: antonym
- `&`: similar to
- `<`: participle of verb
- `*`: entailment
- `>`: cause
- `^`: also
- `$`: verb group
- `;c`: domain of synset - topic
- `;r`: domain of synset - region
- `;u`: domain of synset - usage

## Python Interface Examples

### Basic WordNet Access

```python
import re
from collections import defaultdict

class SimpleWordNet:
    def __init__(self, wordnet_path):
        self.wordnet_path = wordnet_path
        self.synsets = {}
        self.index = defaultdict(list)
        self.load_data()
    
    def load_data(self):
        """Load WordNet data files"""
        for pos in ['noun', 'verb', 'adj', 'adv']:
            self._load_index(pos)
            self._load_data(pos)
    
    def _load_index(self, pos):
        """Load index file for given part of speech"""
        index_file = f"{self.wordnet_path}/index.{pos}"
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(' ') or not line.strip():
                        continue  # Skip header
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        word = parts[0]
                        synset_count = int(parts[2])
                        # Extract synset offsets from the end of the line
                        offsets = parts[-synset_count:]
                        self.index[word.lower()].extend([
                            (offset, pos) for offset in offsets
                        ])
        except FileNotFoundError:
            print(f"Index file not found: {index_file}")
    
    def _load_data(self, pos):
        """Load data file for given part of speech"""
        data_file = f"{self.wordnet_path}/data.{pos}"
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(' ') or not line.strip():
                        continue  # Skip header
                    if '|' in line:
                        data_part, gloss = line.split('|', 1)
                        parts = data_part.strip().split()
                        if len(parts) >= 6:
                            offset = parts[0]
                            lex_filenum = parts[1]
                            ss_type = parts[2]
                            w_cnt = int(parts[3], 16)  # hex format
                            
                            # Extract words (every 2nd item starting from index 4)
                            words = []
                            for i in range(4, 4 + w_cnt * 2, 2):
                                if i < len(parts):
                                    words.append(parts[i])
                            
                            self.synsets[offset] = {
                                'offset': offset,
                                'pos': ss_type,
                                'words': words,
                                'gloss': gloss.strip()
                            }
        except FileNotFoundError:
            print(f"Data file not found: {data_file}")

    def get_synsets(self, word):
        """Get all synsets for a word"""
        synsets = []
        for offset, pos in self.index.get(word.lower(), []):
            if offset in self.synsets:
                synsets.append(self.synsets[offset])
        return synsets
    
    def get_definition(self, word):
        """Get definitions for a word"""
        synsets = self.get_synsets(word)
        return [synset['gloss'] for synset in synsets]

# Usage example
wordnet_path = "C:/path-to-repo-here/UVI/corpora/wordnet"
wn = SimpleWordNet(wordnet_path)

# Get definitions
definitions = wn.get_definition("dog")
for i, definition in enumerate(definitions, 1):
    print(f"{i}. {definition}")
```

### Loading Exception Lists

```python
def load_exceptions(wordnet_path, pos):
    """Load morphological exceptions for a part of speech"""
    exceptions = {}
    exc_file = f"{wordnet_path}/{pos}.exc"
    try:
        with open(exc_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    irregular_form = parts[0]
                    base_form = parts[1]
                    exceptions[irregular_form] = base_form
    except FileNotFoundError:
        print(f"Exception file not found: {exc_file}")
    return exceptions

# Usage
noun_exceptions = load_exceptions(wordnet_path, "noun")
print(noun_exceptions.get("children", "children"))  # Output: child
```

### Working with Verb Frames

```python
def load_verb_frames(wordnet_path):
    """Load verb sentence frames"""
    frames = {}
    frames_file = f"{wordnet_path}/dict/verb.Framestext"
    try:
        with open(frames_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('('):
                    parts = line.strip().split(' ', 1)
                    if len(parts) >= 2:
                        frame_num = int(parts[0])
                        frame_text = parts[1]
                        frames[frame_num] = frame_text
    except FileNotFoundError:
        print(f"Frames file not found: {frames_file}")
    return frames

# Usage
verb_frames = load_verb_frames(wordnet_path)
print(verb_frames.get(8, "Unknown frame"))  # Output: Somebody ----s something
```

### Advanced: NLTK Integration

For more sophisticated WordNet processing, consider using NLTK:

```python
import nltk
from nltk.corpus import wordnet as wn

# Download WordNet data (if not already available)
# nltk.download('wordnet')

# Basic usage
synsets = wn.synsets('dog')
for synset in synsets:
    print(f"{synset.name()}: {synset.definition()}")
    
# Get hypernyms
dog_synset = wn.synset('dog.n.01')
hypernyms = dog_synset.hypernyms()
for hyp in hypernyms:
    print(f"Hypernym: {hyp.name()} - {hyp.definition()}")
```

## Tips for Working with WordNet Data

1. **File Encoding**: All files are in UTF-8 encoding
2. **Header Lines**: Data and index files start with license header (lines beginning with spaces)
3. **Hex Numbers**: Some counts in data files are in hexadecimal format
4. **Pointer Symbols**: Learn the relationship symbols for semantic navigation
5. **Sense Keys**: Use for precise sense identification across applications
6. **Case Sensitivity**: Word lookups are typically case-insensitive
7. **Performance**: Consider indexing frequently accessed data in memory