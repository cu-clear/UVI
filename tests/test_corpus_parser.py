"""
Unit tests for CorpusParser class.

Comprehensive test suite for the CorpusParser class including parsing methods
for VerbNet, FrameNet, PropBank, WordNet, BSO mappings, and other corpus formats.
"""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import xml.etree.ElementTree as ET
from io import StringIO
import sys
import os

# Add src directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from uvi.corpus_loader import CorpusParser


class TestCorpusParser:
    """Test cases for the CorpusParser class."""

    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.mock_logger = Mock()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test corpus paths
        self.corpus_paths = {
            'verbnet': self.temp_dir / 'verbnet',
            'framenet': self.temp_dir / 'framenet',
            'propbank': self.temp_dir / 'propbank',
            'wordnet': self.temp_dir / 'wordnet',
            'ontonotes': self.temp_dir / 'ontonotes',
            'bso': self.temp_dir / 'bso',
            'semnet': self.temp_dir / 'semnet',
            'reference_docs': self.temp_dir / 'reference_docs',
            'vn_api': self.temp_dir / 'vn_api'
        }
        
        # Create directories
        for path in self.corpus_paths.values():
            path.mkdir(parents=True, exist_ok=True)
        
        self.parser = CorpusParser(self.corpus_paths, self.mock_logger)

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # Helper methods for creating mock XML data
    
    def create_mock_verbnet_xml(self, class_id="test-1.1"):
        """Create mock VerbNet XML content."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="{class_id}">
            <MEMBERS>
                <MEMBER name="test_verb" wn="test.01" grouping="test.01"/>
            </MEMBERS>
            <THEMROLES>
                <THEMROLE type="Agent">
                    <SELRESTRS>
                        <SELRESTR Value="+" type="animate"/>
                    </SELRESTRS>
                </THEMROLE>
            </THEMROLES>
            <FRAMES>
                <FRAME primary="Basic Transitive">
                    <DESCRIPTION primary="Basic Transitive" secondary="" descriptionNumber="1" xtag=""/>
                    <EXAMPLES>
                        <EXAMPLE>John tested the system.</EXAMPLE>
                    </EXAMPLES>
                    <SYNTAX>
                        <NP value="Agent">
                            <SYNRESTRS>
                                <SYNRESTR Value="+" type="np"/>
                            </SYNRESTRS>
                        </NP>
                        <VERB/>
                        <NP value="Patient"/>
                    </SYNTAX>
                    <SEMANTICS>
                        <PRED value="test">
                            <ARG type="ThemRole" value="Agent"/>
                            <ARG type="ThemRole" value="Patient"/>
                        </PRED>
                    </SEMANTICS>
                </FRAME>
            </FRAMES>
            <SUBCLASSES>
                <VNSUBCLASS ID="{class_id}.1">
                    <MEMBERS>
                        <MEMBER name="subclass_verb" wn="subclass.01"/>
                    </MEMBERS>
                </VNSUBCLASS>
            </SUBCLASSES>
        </VNCLASS>"""

    def create_mock_framenet_xml(self, frame_name="Test_Frame"):
        """Create mock FrameNet XML content."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <frame name="{frame_name}" ID="1">
            <definition>Test frame definition</definition>
            <FE name="Agent" ID="1" coreType="Core">
                <definition>Agent definition</definition>
            </FE>
            <lexUnit name="test.v" ID="1" POS="V" lemmaID="1">
                <definition>Test lexical unit</definition>
            </lexUnit>
        </frame>"""

    def create_mock_propbank_xml(self, lemma="test"):
        """Create mock PropBank XML content."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <frameset lemma="{lemma}">
            <predicate lemma="{lemma}">
                <roleset id="{lemma}.01" name="to test" vncls="test-1.1">
                    <roles>
                        <role n="0" descr="tester" f="PAG" vnrole="Agent"/>
                        <role n="1" descr="thing tested" f="PPT" vnrole="Patient"/>
                    </roles>
                    <example name="basic usage">
                        <text>John tested the system.</text>
                        <arg n="0">John</arg>
                        <arg n="1">the system</arg>
                    </example>
                </roleset>
            </predicate>
        </frameset>"""

    # Test initialization

    def test_init(self):
        """Test CorpusParser initialization."""
        assert self.parser.corpus_paths == self.corpus_paths
        assert self.parser.logger == self.mock_logger
        assert self.parser.bso_mappings == {}

    # Test VerbNet parsing

    def test_parse_verbnet_files_missing_path(self):
        """Test parse_verbnet_files with missing VerbNet path."""
        parser_no_vn = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="verbnet corpus path not configured"):
            parser_no_vn.parse_verbnet_files()

    def test_parse_verbnet_files_no_xml_files(self):
        """Test parse_verbnet_files with no XML files."""
        result = self.parser.parse_verbnet_files()
        
        assert result['classes'] == {}
        assert result['hierarchy'] == {'by_name': {}, 'by_id': {}, 'parent_child': {}}
        assert result['members'] == {}
        assert result['statistics']['total_files'] == 0
        assert result['statistics']['parsed_files'] == 0

    def test_parse_verbnet_files_with_xml(self):
        """Test parse_verbnet_files with valid XML files."""
        # Create test XML file
        xml_content = self.create_mock_verbnet_xml("test-1.1")
        test_xml = self.corpus_paths['verbnet'] / 'test-1.1.xml'
        test_xml.write_text(xml_content, encoding='utf-8')
        
        result = self.parser.parse_verbnet_files()
        
        assert 'test-1.1' in result['classes']
        assert result['statistics']['parsed_files'] == 1
        assert result['statistics']['total_classes'] == 1
        assert 'test_verb' in result['members']
        assert result['members']['test_verb'] == ['test-1.1']

    def test_parse_verbnet_class_invalid_root(self):
        """Test _parse_verbnet_class with invalid root element."""
        # Create XML with wrong root
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><INVALID>test</INVALID>'
        test_xml = self.corpus_paths['verbnet'] / 'invalid.xml'
        test_xml.write_text(xml_content, encoding='utf-8')
        
        result = self.parser._parse_verbnet_class(test_xml)
        assert result == {}

    def test_parse_verbnet_class_malformed_xml(self):
        """Test _parse_verbnet_class with malformed XML."""
        xml_content = '<VNCLASS ID="test-1.1"><INVALID_XML'
        test_xml = self.corpus_paths['verbnet'] / 'malformed.xml'
        test_xml.write_text(xml_content, encoding='utf-8')
        
        result = self.parser._parse_verbnet_class(test_xml)
        assert result == {}

    def test_parse_verbnet_subclass(self):
        """Test _parse_verbnet_subclass method."""
        xml_content = """<VNSUBCLASS ID="test-1.1.1">
            <MEMBERS>
                <MEMBER name="subtest" wn="subtest.01" grouping="subtest.01"/>
            </MEMBERS>
            <FRAMES>
                <FRAME primary="Subclass Frame">
                    <EXAMPLES>
                        <EXAMPLE>Sub example</EXAMPLE>
                    </EXAMPLES>
                </FRAME>
            </FRAMES>
        </VNSUBCLASS>"""
        
        root = ET.fromstring(xml_content)
        result = self.parser._parse_verbnet_subclass(root)
        
        assert result['id'] == 'test-1.1.1'
        assert len(result['members']) == 1
        assert result['members'][0]['name'] == 'subtest'
        assert len(result['frames']) == 1

    def test_extract_frame_description(self):
        """Test _extract_frame_description method."""
        xml_content = '<FRAME primary="Test" secondary="Secondary" descriptionNumber="1" xtag="test"/>'
        root = ET.fromstring(xml_content)
        
        result = self.parser._extract_frame_description(root)
        
        assert result['primary'] == 'Test'
        assert result['secondary'] == 'Secondary'
        assert result['descriptionNumber'] == '1'
        assert result['xtag'] == 'test'

    def test_build_verbnet_hierarchy(self):
        """Test _build_verbnet_hierarchy method."""
        classes = {
            'test-1': {'id': 'test-1'},
            'test-1.1': {'id': 'test-1.1'},
            'another-2': {'id': 'another-2'}
        }
        
        hierarchy = self.parser._build_verbnet_hierarchy(classes)
        
        assert 'T' in hierarchy['by_name']
        assert 'A' in hierarchy['by_name']
        assert '1' in hierarchy['by_id']
        assert '2' in hierarchy['by_id']
        assert 'test-1' in hierarchy['parent_child']
        assert 'test-1.1' in hierarchy['parent_child']['test-1']

    # Test FrameNet parsing

    def test_parse_framenet_files_missing_path(self):
        """Test parse_framenet_files with missing FrameNet path."""
        parser_no_fn = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="framenet corpus path not configured"):
            parser_no_fn.parse_framenet_files()

    def test_parse_framenet_files_empty(self):
        """Test parse_framenet_files with empty directory."""
        result = self.parser.parse_framenet_files()
        
        assert result['frames'] == {}
        assert result['lexical_units'] == {}
        assert result['frame_relations'] == {}

    def test_parse_framenet_frame_index(self):
        """Test _parse_framenet_frame_index method."""
        index_content = """<?xml version="1.0" encoding="UTF-8"?>
        <frameIndex>
            <frame ID="1" name="Test_Frame" cDate="2023-01-01"/>
            <frame ID="2" name="Another_Frame" cDate="2023-01-02"/>
        </frameIndex>"""
        
        index_path = self.corpus_paths['framenet'] / 'frameIndex.xml'
        index_path.write_text(index_content, encoding='utf-8')
        
        result = self.parser._parse_framenet_frame_index(index_path)
        
        assert 'Test_Frame' in result
        assert result['Test_Frame']['id'] == '1'
        assert result['Test_Frame']['cdate'] == '2023-01-01'

    def test_parse_framenet_frame(self):
        """Test _parse_framenet_frame method."""
        frame_content = self.create_mock_framenet_xml("Test_Frame")
        frame_path = self.corpus_paths['framenet'] / 'frame' / 'Test_Frame.xml'
        frame_path.parent.mkdir(exist_ok=True)
        frame_path.write_text(frame_content, encoding='utf-8')
        
        result = self.parser._parse_framenet_frame(frame_path)
        
        assert result['name'] == 'Test_Frame'
        assert result['definition'] == 'Test frame definition'
        assert 'Agent' in result['frame_elements']
        assert 'test.v' in result['lexical_units']

    def test_parse_framenet_lu_index(self):
        """Test _parse_framenet_lu_index method."""
        lu_content = """<?xml version="1.0" encoding="UTF-8"?>
        <luIndex>
            <lu ID="1" name="test.v" POS="V" frame="Test_Frame"/>
        </luIndex>"""
        
        lu_path = self.corpus_paths['framenet'] / 'luIndex.xml'
        lu_path.write_text(lu_content, encoding='utf-8')
        
        result = self.parser._parse_framenet_lu_index(lu_path)
        
        assert 'test.v' in result
        assert result['test.v']['frame'] == 'Test_Frame'

    def test_parse_framenet_relations(self):
        """Test _parse_framenet_relations method."""
        relations_content = """<?xml version="1.0" encoding="UTF-8"?>
        <frameRelations>
            <frameRelation type="Inheritance" superFrame="Super_Frame" subFrame="Sub_Frame"/>
            <feRelation type="Subframe" superFE="Super_FE" subFE="Sub_FE" frameRelation="1"/>
        </frameRelations>"""
        
        rel_path = self.corpus_paths['framenet'] / 'frRelation.xml'
        rel_path.write_text(relations_content, encoding='utf-8')
        
        result = self.parser._parse_framenet_relations(rel_path)
        
        assert len(result['frame_relations']) == 1
        assert len(result['fe_relations']) == 1
        assert result['frame_relations'][0]['type'] == 'Inheritance'

    # Test PropBank parsing

    def test_parse_propbank_files_missing_path(self):
        """Test parse_propbank_files with missing PropBank path."""
        parser_no_pb = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="propbank corpus path not configured"):
            parser_no_pb.parse_propbank_files()

    def test_parse_propbank_files_with_frame(self):
        """Test parse_propbank_files with frame file."""
        # Create frames directory and file
        frames_dir = self.corpus_paths['propbank'] / 'frames'
        frames_dir.mkdir(exist_ok=True)
        
        pb_content = self.create_mock_propbank_xml("test")
        frame_file = frames_dir / 'test-v.xml'
        frame_file.write_text(pb_content, encoding='utf-8')
        
        result = self.parser.parse_propbank_files()
        
        assert 'test' in result['predicates']
        assert 'test.01' in result['rolesets']
        assert result['statistics']['predicates_parsed'] == 1

    def test_parse_propbank_frame(self):
        """Test _parse_propbank_frame method."""
        pb_content = self.create_mock_propbank_xml("test")
        pb_path = self.temp_dir / 'test.xml'
        pb_path.write_text(pb_content, encoding='utf-8')
        
        result = self.parser._parse_propbank_frame(pb_path)
        
        assert result['lemma'] == 'test'
        assert len(result['rolesets']) == 1
        assert result['rolesets'][0]['id'] == 'test.01'
        assert len(result['rolesets'][0]['roles']) == 2

    def test_parse_propbank_frame_malformed(self):
        """Test _parse_propbank_frame with malformed XML."""
        pb_content = '<frameset lemma="test"><invalid'
        pb_path = self.temp_dir / 'malformed.xml'
        pb_path.write_text(pb_content, encoding='utf-8')
        
        result = self.parser._parse_propbank_frame(pb_path)
        assert result == {}

    # Test OntoNotes parsing

    def test_parse_ontonotes_files_missing_path(self):
        """Test parse_ontonotes_files with missing OntoNotes path."""
        parser_no_on = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="ontonotes corpus path not configured"):
            parser_no_on.parse_ontonotes_files()

    def test_parse_ontonotes_data(self):
        """Test _parse_ontonotes_data method."""
        on_content = """<?xml version="1.0" encoding="UTF-8"?>
        <inventory lemma="test">
            <sense n="1" name="test_sense" group="1">
                <commentary>Test sense commentary</commentary>
                <examples>
                    <example>Test example sentence</example>
                </examples>
                <mappings>
                    <wn version="3.0">test.v.01</wn>
                    <vn>test-1.1</vn>
                    <pb>test.01</pb>
                </mappings>
            </sense>
        </inventory>"""
        
        on_path = self.temp_dir / 'test.xml'
        on_path.write_text(on_content, encoding='utf-8')
        
        result = self.parser._parse_ontonotes_data(on_path)
        
        assert result['lemma'] == 'test'
        assert len(result['senses']) == 1
        assert result['senses'][0]['n'] == '1'
        assert 'wn' in result['senses'][0]['mappings']

    # Test WordNet parsing

    def test_parse_wordnet_files_missing_path(self):
        """Test parse_wordnet_files with missing WordNet path."""
        parser_no_wn = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="wordnet corpus path not configured"):
            parser_no_wn.parse_wordnet_files()

    def test_parse_wordnet_data_file(self):
        """Test _parse_wordnet_data_file method."""
        wn_data_content = """  Licensed to you under the GNU GPL.
00001740 03 v 02 test 0 examine 0 002 ! 35000417 v 0000 @ 00002419 v 0000 | to test something
00002419 03 v 01 check 0 003 ~ 00001740 v 0000 ~ 00005678 v 0000 @ 00009876 v 0000 | to check or examine"""
        
        data_path = self.corpus_paths['wordnet'] / 'data.verb'
        data_path.write_text(wn_data_content, encoding='utf-8')
        
        result = self.parser._parse_wordnet_data_file(data_path)
        
        assert '00001740' in result
        assert result['00001740']['ss_type'] == 'v'
        assert len(result['00001740']['words']) == 2

    def test_parse_wordnet_index_file(self):
        """Test _parse_wordnet_index_file method."""
        index_content = """  Licensed to you under the GNU GPL.
test v 2 2 @ ~ 2 0 00001740 00002419
examine v 1 1 @ 1 0 00001740"""
        
        index_path = self.corpus_paths['wordnet'] / 'index.verb'
        index_path.write_text(index_content, encoding='utf-8')
        
        result = self.parser._parse_wordnet_index_file(index_path)
        
        assert 'test' in result
        assert result['test']['synset_cnt'] == 2
        assert len(result['test']['synset_offsets']) == 2

    def test_parse_wordnet_exception_file(self):
        """Test _parse_wordnet_exception_file method."""
        exc_content = """ran run
went go
better good well"""
        
        exc_path = self.corpus_paths['wordnet'] / 'verb.exc'
        exc_path.write_text(exc_content, encoding='utf-8')
        
        result = self.parser._parse_wordnet_exception_file(exc_path)
        
        assert 'ran' in result
        assert result['ran'] == ['run']
        assert result['better'] == ['good', 'well']

    # Test BSO mapping methods

    def test_parse_bso_mappings_missing_path(self):
        """Test parse_bso_mappings with missing BSO path."""
        parser_no_bso = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="bso corpus path not configured"):
            parser_no_bso.parse_bso_mappings()

    def test_load_bso_mappings(self):
        """Test load_bso_mappings method."""
        csv_content = """VN_Class,BSO_Category,Description
test-1.1,Motion,Test motion category
another-2.1,Contact,Test contact category"""
        
        csv_path = self.corpus_paths['bso'] / 'VNBSOMapping.csv'
        csv_path.write_text(csv_content, encoding='utf-8')
        
        result = self.parser.load_bso_mappings(csv_path)
        
        assert len(result) == 2
        assert result[0]['VN_Class'] == 'test-1.1'
        assert result[0]['BSO_Category'] == 'Motion'

    def test_parse_bso_mappings_with_data(self):
        """Test parse_bso_mappings with CSV data."""
        csv_content = """VN_Class,BSO_Category,Description
test-1.1,Motion,Test motion category"""
        
        csv_path = self.corpus_paths['bso'] / 'VNBSOMapping.csv'
        csv_path.write_text(csv_content, encoding='utf-8')
        
        result = self.parser.parse_bso_mappings()
        
        assert 'test-1.1' in result['vn_to_bso']
        assert result['vn_to_bso']['test-1.1'] == 'Motion'
        assert 'Motion' in result['bso_to_vn']

    def test_apply_bso_mappings(self):
        """Test apply_bso_mappings method."""
        # Set up BSO mappings
        self.parser.bso_mappings = {
            'vn_to_bso': {'test-1.1': 'Motion'},
            'bso_to_vn': {'Motion': ['test-1.1']}
        }
        
        verbnet_data = {
            'classes': {
                'test-1.1': {'id': 'test-1.1'},
                'other-2.1': {'id': 'other-2.1'}
            }
        }
        
        result = self.parser.apply_bso_mappings(verbnet_data)
        
        assert result['classes']['test-1.1']['bso_category'] == 'Motion'
        assert 'bso_category' not in result['classes']['other-2.1']

    def test_apply_bso_mappings_no_mappings(self):
        """Test apply_bso_mappings with no mappings loaded."""
        verbnet_data = {'classes': {'test-1.1': {'id': 'test-1.1'}}}
        
        result = self.parser.apply_bso_mappings(verbnet_data)
        
        assert result == verbnet_data

    # Test SemNet parsing

    def test_parse_semnet_data_missing_path(self):
        """Test parse_semnet_data with missing SemNet path."""
        parser_no_semnet = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="semnet corpus path not configured"):
            parser_no_semnet.parse_semnet_data()

    def test_parse_semnet_data_with_files(self):
        """Test parse_semnet_data with JSON files."""
        verb_data = {"test_verb": {"relations": ["cause", "motion"]}}
        noun_data = {"test_noun": {"categories": ["physical", "animate"]}}
        
        verb_path = self.corpus_paths['semnet'] / 'verb-semnet.json'
        noun_path = self.corpus_paths['semnet'] / 'noun-semnet.json'
        
        verb_path.write_text(json.dumps(verb_data), encoding='utf-8')
        noun_path.write_text(json.dumps(noun_data), encoding='utf-8')
        
        result = self.parser.parse_semnet_data()
        
        assert result['verb_network'] == verb_data
        assert result['noun_network'] == noun_data
        assert result['statistics']['verb_entries'] == 1
        assert result['statistics']['noun_entries'] == 1

    def test_parse_semnet_data_malformed_json(self):
        """Test parse_semnet_data with malformed JSON."""
        verb_path = self.corpus_paths['semnet'] / 'verb-semnet.json'
        verb_path.write_text('{"invalid": json}', encoding='utf-8')
        
        result = self.parser.parse_semnet_data()
        
        # Should handle error gracefully
        assert result['verb_network'] == {}
        assert result['statistics']['verb_entries'] == 0

    # Test Reference docs parsing

    def test_parse_reference_docs_missing_path(self):
        """Test parse_reference_docs with missing path."""
        parser_no_ref = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="reference_docs corpus path not configured"):
            parser_no_ref.parse_reference_docs()

    def test_parse_reference_docs_with_files(self):
        """Test parse_reference_docs with JSON and TSV files."""
        pred_data = {"cause": {"definition": "To bring about an event"}}
        themrole_data = {"Agent": {"definition": "The entity performing an action"}}
        
        pred_path = self.corpus_paths['reference_docs'] / 'pred_calc_for_website_final.json'
        themrole_path = self.corpus_paths['reference_docs'] / 'themrole_defs.json'
        constants_path = self.corpus_paths['reference_docs'] / 'vn_constants.tsv'
        
        pred_path.write_text(json.dumps(pred_data), encoding='utf-8')
        themrole_path.write_text(json.dumps(themrole_data), encoding='utf-8')
        constants_path.write_text("Constant\tValue\nTEST_CONST\ttest_value\n", encoding='utf-8')
        
        result = self.parser.parse_reference_docs()
        
        assert result['predicates'] == pred_data
        assert result['themroles'] == themrole_data
        assert 'TEST_CONST' in result['constants']

    def test_parse_tsv_file(self):
        """Test _parse_tsv_file method."""
        tsv_content = "Key\tValue\tDescription\ntest_key\ttest_value\tTest description\n"
        tsv_path = self.temp_dir / 'test.tsv'
        tsv_path.write_text(tsv_content, encoding='utf-8')
        
        result = self.parser._parse_tsv_file(tsv_path)
        
        assert 'test_key' in result
        assert result['test_key']['Value'] == 'test_value'

    # Test VN API parsing

    def test_parse_vn_api_files_missing_path(self):
        """Test parse_vn_api_files with missing VN API path but VerbNet available."""
        # Remove vn_api from paths but keep verbnet
        vn_paths = {k: v for k, v in self.corpus_paths.items() if k != 'vn_api'}
        parser = CorpusParser(vn_paths, self.mock_logger)
        
        # Should use VerbNet parser
        with patch.object(parser, 'parse_verbnet_files') as mock_parse:
            mock_parse.return_value = {'test': 'data'}
            result = parser.parse_vn_api_files()
            mock_parse.assert_called_once()

    def test_parse_vn_api_files_no_paths(self):
        """Test parse_vn_api_files with no paths available."""
        parser = CorpusParser({}, self.mock_logger)
        
        with pytest.raises(FileNotFoundError, match="VN API corpus path not configured"):
            parser.parse_vn_api_files()

    # Test error handling

    def test_xml_parsing_errors(self):
        """Test XML parsing error handling."""
        # Test with completely invalid XML
        invalid_xml = self.corpus_paths['verbnet'] / 'invalid.xml'
        invalid_xml.write_text('not xml at all', encoding='utf-8')
        
        result = self.parser._parse_verbnet_class(invalid_xml)
        assert result == {}
        self.mock_logger.error.assert_called()

    def test_file_not_found_errors(self):
        """Test file not found error handling."""
        non_existent = Path('/non/existent/file.xml')
        
        result = self.parser._parse_verbnet_class(non_existent)
        assert result == {}

    def test_permission_errors(self):
        """Test permission error handling."""
        with patch('xml.etree.ElementTree.parse', side_effect=PermissionError("Access denied")):
            xml_path = self.corpus_paths['verbnet'] / 'test.xml'
            xml_path.write_text('<VNCLASS ID="test"/>', encoding='utf-8')
            
            result = self.parser._parse_verbnet_class(xml_path)
            assert result == {}

    # Integration tests

    def test_full_verbnet_parsing_workflow(self):
        """Test complete VerbNet parsing workflow."""
        # Create multiple test files
        for i in range(3):
            xml_content = self.create_mock_verbnet_xml(f"test-{i}.1")
            xml_file = self.corpus_paths['verbnet'] / f'test-{i}.1.xml'
            xml_file.write_text(xml_content, encoding='utf-8')
        
        result = self.parser.parse_verbnet_files()
        
        assert len(result['classes']) == 3
        assert result['statistics']['parsed_files'] == 3
        assert len(result['hierarchy']['by_name']['T']) == 3  # All start with 'T'

    def test_full_framenet_parsing_workflow(self):
        """Test complete FrameNet parsing workflow."""
        # Create frame directory and index
        frame_dir = self.corpus_paths['framenet'] / 'frame'
        frame_dir.mkdir(exist_ok=True)
        
        # Create frame files
        for frame_name in ['Test_Frame', 'Another_Frame']:
            frame_content = self.create_mock_framenet_xml(frame_name)
            frame_file = frame_dir / f'{frame_name}.xml'
            frame_file.write_text(frame_content, encoding='utf-8')
        
        result = self.parser.parse_framenet_files()
        
        assert len(result['frames']) == 2
        assert 'Test_Frame' in result['frames']
        assert 'Another_Frame' in result['frames']

    def test_cross_corpus_integration(self):
        """Test integration across multiple corpus types."""
        # Setup VerbNet
        vn_content = self.create_mock_verbnet_xml("test-1.1")
        vn_file = self.corpus_paths['verbnet'] / 'test-1.1.xml'
        vn_file.write_text(vn_content, encoding='utf-8')
        
        # Setup BSO mappings
        bso_content = "VN_Class,BSO_Category\ntest-1.1,Motion\n"
        bso_file = self.corpus_paths['bso'] / 'VNBSOMapping.csv'
        bso_file.write_text(bso_content, encoding='utf-8')
        
        # Parse both
        vn_data = self.parser.parse_verbnet_files()
        bso_data = self.parser.parse_bso_mappings()
        
        # Apply BSO mappings
        enhanced_vn = self.parser.apply_bso_mappings(vn_data)
        
        assert enhanced_vn['classes']['test-1.1']['bso_category'] == 'Motion'

    # Edge cases and boundary conditions

    def test_empty_xml_elements(self):
        """Test handling of empty XML elements."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="">
            <MEMBERS></MEMBERS>
            <THEMROLES></THEMROLES>
            <FRAMES></FRAMES>
        </VNCLASS>"""
        
        xml_file = self.corpus_paths['verbnet'] / 'empty.xml'
        xml_file.write_text(xml_content, encoding='utf-8')
        
        result = self.parser._parse_verbnet_class(xml_file)
        
        assert result['id'] == ''
        assert result['members'] == []
        assert result['themroles'] == []
        assert result['frames'] == []

    def test_unicode_handling(self):
        """Test Unicode character handling in XML."""
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="test-unicode-1.1">
            <MEMBERS>
                <MEMBER name="café" wn="café.01"/>
                <MEMBER name="naïve" wn="naïve.01"/>
            </MEMBERS>
        </VNCLASS>"""
        
        xml_file = self.corpus_paths['verbnet'] / 'unicode.xml'
        xml_file.write_text(xml_content, encoding='utf-8')
        
        result = self.parser._parse_verbnet_class(xml_file)
        
        assert len(result['members']) == 2
        assert result['members'][0]['name'] == 'café'
        assert result['members'][1]['name'] == 'naïve'

    def test_large_hierarchy_building(self):
        """Test hierarchy building with large numbers of classes."""
        classes = {}
        # Create a large number of test classes
        for i in range(100):
            classes[f'test-{i}'] = {'id': f'test-{i}'}
            for j in range(3):
                classes[f'test-{i}.{j}'] = {'id': f'test-{i}.{j}'}
        
        hierarchy = self.parser._build_verbnet_hierarchy(classes)
        
        assert len(hierarchy['by_name']['T']) == 400  # All start with 'T'
        assert len(hierarchy['parent_child']) == 100  # 100 parent classes
        # Each parent should have 3 children
        for i in range(100):
            assert len(hierarchy['parent_child'][f'test-{i}']) == 3


class TestCorpusParserErrorRecovery:
    """Test error recovery and robustness of CorpusParser."""

    def setup_method(self):
        """Setup for error recovery tests."""
        self.mock_logger = Mock()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.corpus_paths = {'verbnet': self.temp_dir / 'verbnet'}
        self.corpus_paths['verbnet'].mkdir(parents=True, exist_ok=True)
        self.parser = CorpusParser(self.corpus_paths, self.mock_logger)

    def teardown_method(self):
        """Cleanup after error recovery tests."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_partial_file_parsing_failure(self):
        """Test handling when some files fail to parse."""
        # Create one valid file
        valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <VNCLASS ID="valid-1.1">
            <MEMBERS><MEMBER name="valid_verb"/></MEMBERS>
        </VNCLASS>"""
        
        # Create one invalid file
        invalid_xml = '<?xml version="1.0"?><VNCLASS ID="invalid-1.1"><INVALID'
        
        valid_file = self.corpus_paths['verbnet'] / 'valid.xml'
        invalid_file = self.corpus_paths['verbnet'] / 'invalid.xml'
        
        valid_file.write_text(valid_xml, encoding='utf-8')
        invalid_file.write_text(invalid_xml, encoding='utf-8')
        
        result = self.parser.parse_verbnet_files()
        
        # Should successfully parse the valid file
        assert len(result['classes']) == 1
        assert 'valid-1.1' in result['classes']
        assert result['statistics']['parsed_files'] == 1
        assert result['statistics']['error_files'] == 1

    def test_recovery_from_encoding_errors(self):
        """Test recovery from file encoding errors."""
        # Create a file with problematic encoding
        problematic_content = b'\xff\xfe<?xml version="1.0"?><VNCLASS ID="test"/>'
        
        problem_file = self.corpus_paths['verbnet'] / 'encoding_issue.xml'
        problem_file.write_bytes(problematic_content)
        
        result = self.parser.parse_verbnet_files()
        
        # Should handle encoding error gracefully
        assert result['statistics']['error_files'] > 0
        self.mock_logger.error.assert_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])