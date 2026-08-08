"""
Unit Tests for UVI Parser Modules

Comprehensive test suite for all parser modules in the UVI package covering:
- VerbNet XML parsing
- FrameNet XML parsing  
- PropBank XML parsing
- OntoNotes parsing
- WordNet text file parsing
- BSO CSV parsing
- SemNet JSON parsing
- Reference documentation parsing
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import shutil
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any

import sys
import os
# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.parsers.verbnet_parser import VerbNetParser
from uvi.parsers.framenet_parser import FrameNetParser
from uvi.parsers.propbank_parser import PropBankParser
from uvi.parsers.ontonotes_parser import OntoNotesParser
from uvi.parsers.wordnet_parser import WordNetParser
from uvi.parsers.bso_parser import BSOParser
from uvi.parsers.semnet_parser import SemNetParser
from uvi.parsers.reference_parser import ReferenceParser


class TestVerbNetParser(unittest.TestCase):
    """Test VerbNet XML parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'verbnet'
        self.test_corpus_path.mkdir()
        
        # Create sample VerbNet XML file
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="run-51.3.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <MEMBERS>
                <MEMBER name="run" wn="run%2:38:00" grouping="run.01"/>
                <MEMBER name="jog" wn="jog%2:38:00" grouping="jog.01"/>
            </MEMBERS>
            <THEMROLES>
                <THEMROLE type="Agent">
                    <SELRESTRS>
                        <SELRESTR Value="+" type="animate"/>
                    </SELRESTRS>
                </THEMROLE>
                <THEMROLE type="Theme">
                    <SELRESTRS>
                        <SELRESTR Value="-" type="animate"/>
                    </SELRESTRS>
                </THEMROLE>
            </THEMROLES>
            <FRAMES>
                <FRAME>
                    <DESCRIPTION primary="Intransitive" secondary="basic" descriptionNumber="0.1" xtag=""/>
                    <EXAMPLES>
                        <EXAMPLE>Carmen ran.</EXAMPLE>
                        <EXAMPLE>The horse jogged.</EXAMPLE>
                    </EXAMPLES>
                    <SYNTAX>
                        <NP value="Agent">
                            <SYNRESTRS>
                                <SYNRESTR Value="+" type="plural"/>
                            </SYNRESTRS>
                        </NP>
                        <VERB/>
                    </SYNTAX>
                    <SEMANTICS>
                        <PRED value="motion">
                            <ARG type="ThemRole" value="Agent"/>
                        </PRED>
                        <PRED value="manner">
                            <ARG type="Constant" value="running"/>
                        </PRED>
                    </SEMANTICS>
                </FRAME>
            </FRAMES>
            <SUBCLASSES>
                <VNSUBCLASS ID="run-51.3.2-1">
                    <MEMBERS>
                        <MEMBER name="sprint" wn="sprint%2:38:00" grouping="sprint.01"/>
                    </MEMBERS>
                </VNSUBCLASS>
            </SUBCLASSES>
        </VNCLASS>"""
        
        with open(self.test_corpus_path / 'run-51.3.2.xml', 'w') as f:
            f.write(self.sample_xml)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test VerbNet parser initialization."""
        parser = VerbNetParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
        self.assertEqual(parser.schema_path, self.test_corpus_path / "vn_schema-3.xsd")
    
    def test_parse_all_classes_with_files(self):
        """Test parsing all VerbNet classes."""
        parser = VerbNetParser(self.test_corpus_path)
        result = parser.parse_all_classes()
        
        self.assertIsInstance(result, dict)
        self.assertIn('classes', result)
        self.assertIn('hierarchy', result)
        self.assertIn('members_index', result)
        
        # Should have parsed our sample file
        self.assertIn('run-51.3.2', result['classes'])
        
        class_data = result['classes']['run-51.3.2']
        self.assertEqual(class_data['id'], 'run-51.3.2')
        self.assertIsInstance(class_data['members'], list)
        self.assertIsInstance(class_data['themroles'], list)
        self.assertIsInstance(class_data['frames'], list)
    
    def test_parse_all_classes_empty_directory(self):
        """Test parsing with empty directory."""
        empty_dir = Path(self.test_dir) / 'empty'
        empty_dir.mkdir()
        
        parser = VerbNetParser(empty_dir)
        result = parser.parse_all_classes()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['classes']), 0)
    
    def test_parse_all_classes_nonexistent_path(self):
        """Test parsing with nonexistent path."""
        nonexistent = Path(self.test_dir) / 'nonexistent'
        
        parser = VerbNetParser(nonexistent)
        result = parser.parse_all_classes()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['classes']), 0)


class TestFrameNetParser(unittest.TestCase):
    """Test FrameNet XML parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'framenet'
        self.test_corpus_path.mkdir()
        
        # Create FrameNet directory structure
        frame_dir = self.test_corpus_path / 'frame'
        frame_dir.mkdir()
        
        # Sample FrameNet frame XML
        self.sample_frame_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <frame xmlns="http://framenet.icsi.berkeley.edu" name="Self_motion" ID="56" cDate="02/08/2001 01:28:09 PST">
            <definition>&lt;def-root&gt;A Mover moves under their own direction along a path.&lt;/def-root&gt;</definition>
            <FE name="Mover" ID="90" coreType="Core">
                <definition>&lt;def-root&gt;The entity that moves.&lt;/def-root&gt;</definition>
            </FE>
            <FE name="Path" ID="91" coreType="Peripheral">
                <definition>&lt;def-root&gt;The path along which motion takes place.&lt;/def-root&gt;</definition>
            </FE>
            <lexUnit name="run" ID="456" POS="V" lemmaID="789">
                <definition>&lt;def-root&gt;Move at speed using legs.&lt;/def-root&gt;</definition>
            </lexUnit>
            <lexUnit name="walk" ID="457" POS="V" lemmaID="790">
                <definition>&lt;def-root&gt;Move at regular pace using legs.&lt;/def-root&gt;</definition>
            </lexUnit>
        </frame>"""
        
        with open(frame_dir / 'Self_motion.xml', 'w') as f:
            f.write(self.sample_frame_xml)
        
        # Sample frame index
        self.sample_frame_index = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <frameIndex xmlns="http://framenet.icsi.berkeley.edu">
            <frame ID="56" name="Self_motion" cDate="02/08/2001 01:28:09 PST"/>
        </frameIndex>"""
        
        with open(self.test_corpus_path / 'frameIndex.xml', 'w') as f:
            f.write(self.sample_frame_index)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test FrameNet parser initialization."""
        parser = FrameNetParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_frames(self):
        """Test parsing all FrameNet frames."""
        parser = FrameNetParser(self.test_corpus_path)
        result = parser.parse_all_frames()
        
        self.assertIsInstance(result, dict)
        self.assertIn('frames', result)
        
        # Should have parsed our sample frame
        self.assertIn('Self_motion', result['frames'])
        
        frame_data = result['frames']['Self_motion']
        self.assertEqual(frame_data['name'], 'Self_motion')
        self.assertIn('definition', frame_data)
        self.assertIn('frame_elements', frame_data)
        self.assertIn('lexical_units', frame_data)


class TestPropBankParser(unittest.TestCase):
    """Test PropBank XML parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'propbank'
        self.test_corpus_path.mkdir()
        
        # Create PropBank frames directory
        frames_dir = self.test_corpus_path / 'frames'
        frames_dir.mkdir()
        
        # Sample PropBank frame XML
        self.sample_frame_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <frameset lemma="run">
            <predicate lemma="run">
                <roleset id="run.01" name="move quickly on foot" vncls="51.3.2">
                    <roles>
                        <role n="0" descr="runner" f="PPT" vnrole="Agent"/>
                        <role n="1" descr="path, race" f="LOC" vnrole="Location"/>
                        <role n="2" descr="distance" f="EXT" vnrole=""/>
                    </roles>
                    <example name="intransitive">
                        <text>John ran.</text>
                        <arg n="0">John</arg>
                        <rel>ran</rel>
                    </example>
                    <example name="with path">
                        <text>John ran to the store.</text>
                        <arg n="0">John</arg>
                        <rel>ran</rel>
                        <arg n="1">to the store</arg>
                    </example>
                </roleset>
                <roleset id="run.02" name="operate, manage" vncls="">
                    <roles>
                        <role n="0" descr="operator" f="PPT" vnrole=""/>
                        <role n="1" descr="thing operated" f="PPT" vnrole=""/>
                    </roles>
                </roleset>
            </predicate>
        </frameset>"""
        
        with open(frames_dir / 'run-v.xml', 'w') as f:
            f.write(self.sample_frame_xml)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test PropBank parser initialization."""
        parser = PropBankParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_frames(self):
        """Test parsing all PropBank frames."""
        parser = PropBankParser(self.test_corpus_path)
        result = parser.parse_all_frames()
        
        self.assertIsInstance(result, dict)
        self.assertIn('predicates', result)
        
        # Should have parsed our sample frame
        self.assertIn('run', result['predicates'])
        
        predicate_data = result['predicates']['run']
        self.assertEqual(predicate_data['lemma'], 'run')
        self.assertIn('rolesets', predicate_data)
        self.assertEqual(len(predicate_data['rolesets']), 2)


class TestOntoNotesParser(unittest.TestCase):
    """Test OntoNotes parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'ontonotes'
        self.test_corpus_path.mkdir()
        
        # Sample OntoNotes sense file
        self.sample_sense_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <inventory lemma="run">
            <commentary>No commentary.</commentary>
            <sense n="1" name="run-v.1" group="1">
                <commentary>Move quickly on foot</commentary>
                <examples>
                    <example>John ran to the store.</example>
                    <example>The horse ran across the field.</example>
                </examples>
                <mappings>
                    <wn version="3.0">run%2:38:00,run%2:38:01</wn>
                    <vn>run-51.3.2</vn>
                    <pb>run.01</pb>
                </mappings>
            </sense>
            <sense n="2" name="run-v.2" group="2">
                <commentary>Operate or manage</commentary>
                <examples>
                    <example>She runs the company.</example>
                </examples>
                <mappings>
                    <wn version="3.0">run%2:41:00</wn>
                    <pb>run.02</pb>
                </mappings>
            </sense>
        </inventory>"""
        
        with open(self.test_corpus_path / 'run-v.xml', 'w') as f:
            f.write(self.sample_sense_xml)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test OntoNotes parser initialization."""
        parser = OntoNotesParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_senses(self):
        """Test parsing all OntoNotes senses."""
        parser = OntoNotesParser(self.test_corpus_path)
        result = parser.parse_all_senses()
        
        self.assertIsInstance(result, dict)
        self.assertIn('sense_inventories', result)
        
        # Should have parsed our sample sense file
        self.assertIn('run', result['sense_inventories'])
        
        sense_data = result['sense_inventories']['run']
        self.assertEqual(sense_data['lemma'], 'run')
        self.assertIn('senses', sense_data)
        self.assertEqual(len(sense_data['senses']), 2)


class TestWordNetParser(unittest.TestCase):
    """Test WordNet text file parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'wordnet'
        self.test_corpus_path.mkdir()
        
        # Sample WordNet data.verb file content
        self.sample_data_verb = """  Princeton WordNet 3.1 Copyright 2011 by Princeton University.  All rights reserved.
00123456 15 v 02 run 0 jog 0 002 @ 00111111 v 0000 + 02000000 n 0101 | move at speed by using one's feet
00234567 15 v 01 operate 0 001 @ 00333333 v 0000 | control or direct the functioning of"""
        
        with open(self.test_corpus_path / 'data.verb', 'w') as f:
            f.write(self.sample_data_verb)
        
        # Sample WordNet index.verb file content
        self.sample_index_verb = """  Princeton WordNet 3.1 Copyright 2011 by Princeton University.  All rights reserved.
run v 2 0 @ + 2 2 00123456 00345678
operate v 1 0 @ 1 1 00234567"""
        
        with open(self.test_corpus_path / 'index.verb', 'w') as f:
            f.write(self.sample_index_verb)
        
        # Sample exception file
        self.sample_verb_exc = """ran run
running run
operated operate"""
        
        with open(self.test_corpus_path / 'verb.exc', 'w') as f:
            f.write(self.sample_verb_exc)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test WordNet parser initialization."""
        parser = WordNetParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_data(self):
        """Test parsing all WordNet data."""
        parser = WordNetParser(self.test_corpus_path)
        result = parser.parse_all_data()
        
        self.assertIsInstance(result, dict)
        self.assertIn('synsets', result)
        self.assertIn('index', result)
        self.assertIn('exceptions', result)
        
        # Should have parsed synset data
        self.assertIn('verb', result['synsets'])
        
        # Should have parsed index data
        self.assertIn('verb', result['index'])
        self.assertIn('run', result['index']['verb'])
        
        # Should have parsed exceptions
        self.assertIn('verb', result['exceptions'])
        self.assertIn('ran', result['exceptions']['verb'])


class TestBSOParser(unittest.TestCase):
    """Test BSO CSV parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'bso'
        self.test_corpus_path.mkdir()
        
        # Sample VN-BSO mapping CSV
        vn_bso_data = [
            ['VN_Class', 'BSO_Category', 'Description'],
            ['run-51.3.2', 'MOTION', 'Motion verbs'],
            ['walk-51.3.1', 'MOTION', 'Motion verbs'],
            ['eat-39.1', 'CONSUMPTION', 'Eating verbs']
        ]
        
        with open(self.test_corpus_path / 'VNBSOMapping_withMembers.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(vn_bso_data)
        
        # Sample BSO-VN mapping CSV
        bso_vn_data = [
            ['BSO_Category', 'VN_Class', 'Members'],
            ['MOTION', 'run-51.3.2', 'run, jog, sprint'],
            ['MOTION', 'walk-51.3.1', 'walk, stroll, amble'],
            ['CONSUMPTION', 'eat-39.1', 'eat, consume, devour']
        ]
        
        with open(self.test_corpus_path / 'BSOVNMapping_withMembers.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(bso_vn_data)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test BSO parser initialization."""
        parser = BSOParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_mappings(self):
        """Test parsing all BSO mappings."""
        parser = BSOParser(self.test_corpus_path)
        result = parser.parse_all_mappings()
        
        self.assertIsInstance(result, dict)
        self.assertIn('vn_to_bso', result)
        self.assertIn('bso_to_vn', result)
        
        # Should have VN to BSO mappings
        self.assertIn('run-51.3.2', result['vn_to_bso'])
        self.assertEqual(result['vn_to_bso']['run-51.3.2'], 'MOTION')
        
        # Should have BSO to VN mappings
        self.assertIn('MOTION', result['bso_to_vn'])
        self.assertIsInstance(result['bso_to_vn']['MOTION'], list)


class TestSemNetParser(unittest.TestCase):
    """Test SemNet JSON parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'semnet'
        self.test_corpus_path.mkdir()
        
        # Sample verb semantic network
        verb_semnet_data = {
            "run": {
                "synsets": ["run%2:38:00", "run%2:38:01"],
                "relations": {
                    "hypernyms": ["move%2:38:00"],
                    "hyponyms": ["jog%2:38:00", "sprint%2:38:00"],
                    "similar": ["walk%2:38:00"]
                }
            },
            "walk": {
                "synsets": ["walk%2:38:00", "walk%2:38:01"],
                "relations": {
                    "hypernyms": ["move%2:38:00"],
                    "hyponyms": ["stroll%2:38:00"],
                    "similar": ["run%2:38:00"]
                }
            }
        }
        
        with open(self.test_corpus_path / 'verb-semnet.json', 'w') as f:
            json.dump(verb_semnet_data, f)
        
        # Sample noun semantic network
        noun_semnet_data = {
            "runner": {
                "synsets": ["runner%1:18:00"],
                "relations": {
                    "hypernyms": ["person%1:03:00"],
                    "hyponyms": ["jogger%1:18:00"]
                }
            }
        }
        
        with open(self.test_corpus_path / 'noun-semnet.json', 'w') as f:
            json.dump(noun_semnet_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test SemNet parser initialization."""
        parser = SemNetParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_networks(self):
        """Test parsing all semantic networks."""
        parser = SemNetParser(self.test_corpus_path)
        result = parser.parse_all_networks()
        
        self.assertIsInstance(result, dict)
        self.assertIn('verb_network', result)
        self.assertIn('noun_network', result)
        
        # Should have verb network data
        self.assertIn('run', result['verb_network'])
        self.assertIn('synsets', result['verb_network']['run'])
        self.assertIn('relations', result['verb_network']['run'])
        
        # Should have noun network data
        self.assertIn('runner', result['noun_network'])


class TestReferenceParser(unittest.TestCase):
    """Test reference documentation parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir) / 'reference_docs'
        self.test_corpus_path.mkdir()
        
        # Sample predicate calculation data
        pred_calc_data = {
            "motion": {
                "definition": "Indicates motion event",
                "usage": "motion(e, Agent)",
                "examples": ["John ran", "The car moved"]
            },
            "manner": {
                "definition": "Indicates manner of action", 
                "usage": "manner(e, Manner)",
                "examples": ["quickly", "slowly"]
            }
        }
        
        with open(self.test_corpus_path / 'pred_calc_for_website_final.json', 'w') as f:
            json.dump(pred_calc_data, f)
        
        # Sample thematic role definitions
        themrole_data = {
            "Agent": {
                "definition": "Entity that performs action",
                "selectional_restrictions": ["+animate", "+volitional"]
            },
            "Theme": {
                "definition": "Entity that undergoes action",
                "selectional_restrictions": ["+concrete"]
            }
        }
        
        with open(self.test_corpus_path / 'themrole_defs.json', 'w') as f:
            json.dump(themrole_data, f)
        
        # Sample constants TSV
        constants_tsv = """Constant\tDefinition\tUsage
E_TIME\tTime of event\tUsed in temporal predicates
E_LOCATION\tLocation of event\tUsed in spatial predicates"""
        
        with open(self.test_corpus_path / 'vn_constants.tsv', 'w') as f:
            f.write(constants_tsv)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test reference parser initialization."""
        parser = ReferenceParser(self.test_corpus_path)
        
        self.assertEqual(parser.corpus_path, self.test_corpus_path)
    
    def test_parse_all_references(self):
        """Test parsing all reference documentation."""
        parser = ReferenceParser(self.test_corpus_path)
        result = parser.parse_all_references()
        
        self.assertIsInstance(result, dict)
        self.assertIn('predicates', result)
        self.assertIn('themroles', result)
        self.assertIn('constants', result)
        
        # Should have predicate data
        self.assertIn('motion', result['predicates'])
        self.assertIn('definition', result['predicates']['motion'])
        
        # Should have thematic role data
        self.assertIn('Agent', result['themroles'])
        self.assertIn('definition', result['themroles']['Agent'])
        
        # Should have constants data
        self.assertIsInstance(result['constants'], dict)


class TestParserErrorHandling(unittest.TestCase):
    """Test parser error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_corpus_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_parser_with_nonexistent_path(self):
        """Test parsers with nonexistent corpus path."""
        nonexistent = Path(self.test_dir) / 'nonexistent'
        
        # Test each parser
        vn_parser = VerbNetParser(nonexistent)
        result = vn_parser.parse_all_classes()
        self.assertIsInstance(result, dict)
        
        fn_parser = FrameNetParser(nonexistent)
        result = fn_parser.parse_all_frames()
        self.assertIsInstance(result, dict)
        
        pb_parser = PropBankParser(nonexistent)
        result = pb_parser.parse_all_frames()
        self.assertIsInstance(result, dict)
    
    def test_parser_with_empty_files(self):
        """Test parsers with empty or malformed files."""
        empty_dir = self.test_corpus_path / 'empty'
        empty_dir.mkdir()
        
        # Create empty XML file
        with open(empty_dir / 'empty.xml', 'w') as f:
            f.write('')
        
        # Should handle empty files gracefully
        vn_parser = VerbNetParser(empty_dir)
        result = vn_parser.parse_all_classes()
        self.assertIsInstance(result, dict)
    
    def test_parser_with_malformed_xml(self):
        """Test parsers with malformed XML files."""
        malformed_dir = self.test_corpus_path / 'malformed'
        malformed_dir.mkdir()
        
        # Create malformed XML file
        with open(malformed_dir / 'malformed.xml', 'w') as f:
            f.write('<unclosed><tag>malformed xml')
        
        # Should handle malformed XML gracefully
        vn_parser = VerbNetParser(malformed_dir)
        result = vn_parser.parse_all_classes()
        self.assertIsInstance(result, dict)
    
    def test_parser_with_malformed_json(self):
        """Test JSON parsers with malformed JSON files."""
        json_dir = self.test_corpus_path / 'json_test'
        json_dir.mkdir()
        
        # Create malformed JSON file
        with open(json_dir / 'malformed.json', 'w') as f:
            f.write('{"unclosed": "json"')
        
        # Should handle malformed JSON gracefully
        semnet_parser = SemNetParser(json_dir)
        result = semnet_parser.parse_all_networks()
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()