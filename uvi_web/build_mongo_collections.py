import json
import os
from pprint import pprint
import nltk
import csv
from lxml import etree
import re
from bs4 import BeautifulSoup
from nltk import word_tokenize as tokenizer
import urllib3


path_framenet = '../corpora/framenet/'
path_propbank = '../corpora/propbank/frames/'
path_verbnet = '../corpora/vn/verbnet3.4/'
path_wordnet = '../corpora/wordnet/'
path_ontonotes = 'http://verbs.colorado.edu/html_groupings/'
path_bso='../corpora/BSO/VNBSOMapping_withMembers.csv'
path_dep = 'static/images/Dep_Parses/'

path_fd = '../corpora/reference_docs/pred_calc_for_website_final.json'


from pymongo import MongoClient

mongo_client = MongoClient()
db = mongo_client['new_corpora']
def parse_vs_features(features_string):
	'''Parse a member's "features" attribute into a list of atomic feature tokens.
	VN 3.4 uses a structured syntax: semicolon-separated groups, where a group is
	either a bare feature ("+manner_of_motion") or a key with comma-separated
	values ("property_changed: intensity, price"). Values may be multi-word
	("covering_entity_type: Drugs and Medicines") and a +/- prefixed item inside
	a value list is a standalone feature ("activity: Acquire, +force_involved").'''
	if features_string is None:
		return None
	features_string = features_string.strip()
	if features_string in ('', 'None'):
		return None
	features = []
	for group in features_string.split(';'):
		group = group.strip()
		if not group:
			continue
		if ':' in group:
			key, _, values = group.partition(':')
			key = key.strip()
			for value in values.split(','):
				value = value.strip()
				if not value:
					continue
				if value[0] in '+-':
					features.append(value)
				else:
					features.append(key + ': ' + value)
		else:
			for item in group.split(','):
				item = item.strip()
				if not item:
					continue
				subtokens = item.split()
				## legacy format: space-separated +/- features ("+act_laughing +loud");
				## multi-word phrase names ("Cause Negative Behavior") stay as one token
				if len(subtokens) > 1 and all(s[0] in '+-' for s in subtokens):
					features.extend(subtokens)
				else:
					features.append(item)
	return features if features else None

bso_mongo={}
#BSO
with open(path_bso) as csv_file:
	csv_reader=csv.reader(csv_file,delimiter=',')
	for row in csv_reader:
		if row[0] not in bso_mongo:
			bso_mongo[row[0]]=[[row[1],row[2],row[3]]]		
		else:
			bso_mongo[row[0]].append([row[1],row[2],row[3]])

################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
#VERBNET REFERENCES ONLY
def parse_sense(sense):
	def parse_examples(examples):
		if examples is not None:
			ex_list = examples.text
			if ex_list:
				split_list = ex_list.split('\n')
				leading_space_stripped = [my_str.strip() for my_str in split_list]
				single_str = ''
				for line in leading_space_stripped:
					if line:
						if line[-1] in [r'.', r'?', r'!', r')']: single_str += line+'\n'
						else: single_str += line
				lines_out = single_str.split('\n')
				return lines_out
			return ''
		return ''
	
	def parse_mappings(mappings):
		vn = []
		pb = []
		fn = []
		wn = []
		vn_map = mappings.find('vn')
		if vn_map is not None:
			if vn_map.text:
				vn = vn_map.text.split(',')
		pb_map = mappings.find('pb')
		if pb_map is not None:
			if pb_map.text:
				pb = pb_map.text.split(',')
		fn_map = mappings.find('fn')
		if fn_map is not None:
			if fn_map.text:
				fn = fn_map.text.split(',')
		wn_list = mappings.findall('wn')
		for wn_el in wn_list:
			senses = []
			lemma = wn_el.get('lemma')
			version = wn_el.get("version")
			senses_list = wn_el.text
			if senses_list:
				senses = senses_list.split(',')
			if lemma or version or senses_list:
				wn.append({"Lemma":lemma, "Version": version, "Senses":senses})
		return {'vn': vn, 'pb': pb, 'fn': fn, 'wn': wn}
	
	def parse_comments(comments):
		lines_final = []
		syn = ['Syntax', 'SYNTAX']
		others = ['NOTE', 'Note', 'Comments']
		if comments is not None:
			comm_list = comments.text
			if comm_list:
				split_list = comm_list.split('\n')
				leading_space_stripped = [my_str.strip() for my_str in split_list]
				for line in leading_space_stripped:
					if line:
						is_syn_struct = False
						is_split = False
						tokens = tokenizer(line)
						if tokens[0] in syn:
							is_syn_struct = True
							is_split = True
						elif tokens[0] in others:
							is_syn_struct = False
							is_split = True
						elif is_syn_struct:
							is_split = True
						if is_split: lines_final.append(line)
						elif not lines_final: lines_final.append(line)
						else: lines_final[-1]+= ' ' + line
				return lines_final
			return ''
		return ''
	
	group = sense.get('group')
	sense_num = sense.get('n')
	name = sense.get('name')
	examples_list = parse_examples(sense.find('examples'))
	mappings = parse_mappings(sense.find('mappings'))
	line_sep_comments = parse_comments(sense.find('commentary')) #Comments are split to list by line
	return {'num': sense_num, 'group': group, 'name': name, 
			'examples': examples_list, 'mappings': mappings,
			'comments': line_sep_comments}

def parse_on_frame(on_frame, file_name):
	lemma = on_frame.get('lemma')
	senses = [parse_sense(s) for s in on_frame.findall('sense')]
	return {'lemma':lemma, 'predicate': lemma[:-2] ,'senses': senses, 'resource_type': 'on'}

def on_to_mongo(file, path_ontonotes):
	with open(path_ontonotes+file,'r') as xml_file:
		root = etree.parse(xml_file).getroot()
		on_frame = parse_on_frame(root, file)
		return on_frame
	
def add_onto_to_db():
	print('Building ON collection... ')

	def gen_onto_resource(collection, data):
		soup = BeautifulSoup(data, 'lxml')

		for item in soup.select('a'):
			text = item.text.strip()
			if re.match(r".*\-.\.html", text) is not None:
				key = re.search(r"((.*)\-.)\.html", text, re.IGNORECASE)
				if key:
					predicate = key.group(2).lower()
					lemma = key.group(1).lower()

					collection.insert_one({'predicate': predicate, 'lemma': lemma})

	manager = urllib3.PoolManager()

	request = manager.request("GET", path_ontonotes)
	content = request.data.decode("utf8")

	db.drop_collection('ontonotes')
	on_collection = db['ontonotes']

	gen_onto_resource(on_collection, content)
	print("ON Done")

def add_predicate_defs(predicate_definition_file, mongo_collection):
    '''Get definitions and args for vn elements'''
    with open(predicate_definition_file, 'r') as definition_tsv:
        #skip first line (tsv heading)
        next(definition_tsv)
        for line in definition_tsv:
            pred_fields = line.split('\t')
            pred_name = pred_fields[0].split('(')[0].strip()
            pred_def = pred_fields[1]
            pred_args = pred_fields[2]
            pred_dict = {'name':pred_name, 'def':pred_def, 'args':pred_args}
            mongo_collection.insert_one(pred_dict)

def ref_to_db():
	print("References added")
	''' Adds all the reference info into the existing verbnet collection by creating a doc 'reference' 
	and then adding further fields.'''

	# Put all additional info about themroles, predicates, etc into db.
	db.drop_collection('vn_predicates')
	vn_pred_collection = db['vn_predicates']
	add_predicate_defs('../corpora/reference_docs/vn_semantic_predicates.tsv', vn_pred_collection)

	db.drop_collection('vn_constants')
	vn_constant_collection = db['vn_constants']
	add_predicate_defs('../corpora/reference_docs/vn_constants.tsv', vn_constant_collection)

	db.drop_collection('vn_verb_specific')
	vn_verb_specific_collection = db['vn_verb_specific']
	add_predicate_defs('../corpora/reference_docs/vn_verb_specific_predicates.tsv', vn_verb_specific_collection)

	### Get general themroles
	themroles_dict = {}
	with open('../corpora/reference_docs/themrole_defs.json') as td:
		themrole_defs = json.load(td)

	for themrole_list in db.verbnet.find({}, {'themroles.themrole':1, 'class_id':1, '_id':0}):
		for tr in themrole_list['themroles']:
			if tr['themrole'] not in themroles_dict:
				themroles_dict[tr['themrole']] = {'count':1, 'vn_class_members':set([themrole_list['class_id']])}
				role_index = next((index for (index, d) in enumerate(themrole_defs) if d["name"] == tr['themrole']), None)
				if not role_index:
					themroles_dict[tr['themrole']]['description'] = 'No description found'
					themroles_dict[tr['themrole']]['example'] = 'No examples found'
				else:
					themroles_dict[tr['themrole']]['description'] = themrole_defs[role_index]['description']
					themroles_dict[tr['themrole']]['example'] = themrole_defs[role_index]['example']            
			else:
				themroles_dict[tr['themrole']]['count']+=1
				themroles_dict[tr['themrole']]['vn_class_members'].add(themrole_list['class_id'])
				
	## Insert to db element-wise. Convert set of vn class members to list because mongo 
	## does not accept sets as data members

	db.drop_collection('verbnet.references.gen_themroles')
	gen_themroles = db['verbnet']['references']['gen_themroles']
	for key, val in themroles_dict.items():
		val['vn_class_members'] = list(val['vn_class_members'])
		gen_themroles.insert_one({key: val})

	
	### Get Predicates

	predicates_dict = {}
	for doc in list(db.verbnet.find({}, {'frames.semantics.predicate':1, 'class_id':1, '_id':0})):
		for frame in doc['frames']:
			for pr in frame['semantics']:
				if pr['predicate'] not in predicates_dict:
					predicates_dict[pr['predicate']] = {'count':1, 'vn_class_members':set([doc['class_id']])}
					predicates_dict[pr['predicate']]['description'] = 'No description found'
					description = vn_pred_collection.find_one({'name': pr['predicate']}, {'def': 1, '_id': 0})
					if description is not None:
						predicates_dict[pr['predicate']]['description'] = description['def']
				else:
					predicates_dict[pr['predicate']]['count']+=1
					predicates_dict[pr['predicate']]['vn_class_members'].add(doc['class_id'])
					
	db.drop_collection('verbnet.references.predicates')
	predicates = db['verbnet']['references']['predicates']
	for key, val in predicates_dict.items():
		val['vn_class_members'] = list(val['vn_class_members'])
		predicates.insert_one({key: val})

	### Get Verb-Specific Features
	#Can't simply match on cases where vs_features is not None, so instead we match cases where the datatype is a list (mongodb array) 
	vs_features_count_dict = {}
	for doc in list(db.verbnet.find({'members.vs_features': {'$exists': 'true'}}, {'members.vs_features':1, 'class_id':1, '_id':0})):
		for vs_features_dict in doc['members']:
			if vs_features_dict['vs_features'] is not None:
				for vs in vs_features_dict['vs_features']:
					if vs not in vs_features_count_dict:
						vs_features_count_dict[vs]={'count':1, 'vn_class_mem':set([doc['class_id']])}
					else:
						vs_features_count_dict[vs]['count'] += 1
						vs_features_count_dict[vs]['vn_class_mem'].add(doc['class_id'])

	db.drop_collection('verbnet.references.vs_features')
	vs_features = db['verbnet']['references']['vs_features']
	for key, val in vs_features_count_dict.items():
		val['vn_class_mem'] = list(val['vn_class_mem'])
		vs_features.insert_one({key: val})

	### Get syntactic restrictions
	sr_dict = {}
	for vn_class in list(db.verbnet.find({'frames.syntax.synrestrs.synrestr_list.type': {'$exists':1}}, {'frames.syntax.synrestrs.synrestr_list':1, 'class_id':1, '_id':0})):
		for syn in vn_class['frames']:
			for el in syn['syntax']:
				if el['synrestrs']['synrestr_list']:
					for sr_el in el['synrestrs']['synrestr_list']:
						if sr_el['type'] not in sr_dict:
							sr_dict[sr_el['type']] = {sr_el['value']:{'count':1,
																	'vn_mem':set([vn_class['class_id']])}}
						else:
							if sr_el['value'] not in sr_dict[sr_el['type']]:
								sr_dict[sr_el['type']][sr_el['value']] = {'count':1,
																					 'vn_mem': set([vn_class['class_id']])}                          
							else:
								sr_dict[sr_el['type']][sr_el['value']]['count'] +=1
								sr_dict[sr_el['type']][sr_el['value']]['vn_mem'].add(vn_class['class_id'])

	## Add syntactic restrictions to db
	db.drop_collection('verbnet.references.syn_restrs')
	syn_restrs = db['verbnet']['references']['syn_restrs']
	for key, val in sr_dict.items():
		for _, inner_dict in val.items():
			inner_dict['vn_mem'] = list(inner_dict['vn_mem'])
		syn_restrs.insert_one({key: val})


	### Get selectional restrictions
	### This script finds selectional restrictions on themroles
	# TODO: FInd selectional restrictions at class level


	sel_res_dict = {}
	for vn_class in list(db.verbnet.find({}, {'themroles.selrestrs.selrestrs_list':1, 'class_id':1, '_id':0})):
		for selres in vn_class['themroles']:
			if isinstance(selres['selrestrs']['selrestrs_list'], list):
				for sel_elem in selres['selrestrs']['selrestrs_list']:
					if sel_elem['type']:
						if sel_elem['type'] not in sel_res_dict:
							sel_res_dict[sel_elem['type']] = {'Themroles': {sel_elem['value']:{'count':1, 
																	'vn_mem': set([vn_class['class_id']])}}}
						else:
							if sel_elem['value'] not in sel_res_dict[sel_elem['type']]['Themroles']:
								sel_res_dict[sel_elem['type']]['Themroles'][sel_elem['value']] = {'count':1,'vn_mem': set([vn_class['class_id']])}
							else:
								sel_res_dict[sel_elem['type']]['Themroles'][sel_elem['value']]['count'] +=1
								sel_res_dict[sel_elem['type']]['Themroles'][sel_elem['value']]['vn_mem'].add(vn_class['class_id'])

	## Add selectional restrictions to db
	db.drop_collection('verbnet.references.sel_restrs')
	sel_restrs = db['verbnet']['references']['sel_restrs']
	for key, val in sel_res_dict.items():
		for _, inner_dict in val['Themroles'].items():
			inner_dict['vn_mem'] = list(inner_dict['vn_mem'])
		sel_restrs.insert_one({key: val})

################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################


def normalize_fd_example_text(example_text):
	'''Normalize an example sentence for matching VN examples against the Force
	Dynamics annotations. Only letters and digits are kept, so differences in
	trailing punctuation, stray quotes and the optional parentheses used in the
	FD file ("from (the) milk") do not block an otherwise exact match.'''
	return re.sub(r'[^a-z0-9]', '', example_text.lower())


#VERBNET
def build_verbnet_collection():
	print('Building VN Collection...')
	#VERBNET
	import spacy
	from spacy import displacy
	spacy_nlp = spacy.load('en_core_web_sm')

	with open(path_fd) as rf:
		fd_list =  json.load(rf)

	fd_by_example = {normalize_fd_example_text(feats[0]): (key, feats) for key, feats in fd_list.items()}

	def parse_member(member,class_id):
		bso=[]
		fn = []
		name = member.get('name')
		wn = member.get('wn').split(' ')
		if member.get('fnframe'):
			fn = [el for el in member.get('fnframe').split(' ') if el]
		elif member.get('fn_mapping'):
			fn = [el for el in member.get('fn_mapping').split(' ') if el]
		grouping = member.get('grouping').split(' ')
		vs_features = parse_vs_features(member.get('features'))
		if wn[0] == '':
			wn = None
		if grouping[0] == '':
			grouping = None
		if class_id in bso_mongo.keys():
			for val in bso_mongo[class_id]:
				if name in val[2] and val[0] not in bso:	
					bso.append(val[0])
		if not bso:
			bso=None
		return {'name': name, 'wn': wn, 'grouping': grouping, 'vs_features': vs_features,'bso':bso, 'fn': fn}
			
	def parse_themrole(themrole):
		def parse_selrestr(selrestr):
			selrestr_type = selrestr.get('type')
			value = selrestr.get('Value')
			return {'value': value, 'type': selrestr_type}
		
		def parse_synrestr(synrestr):
			synrestr_type = synrestr.get('type')
			value = synrestr.get('Value')
			return {'value': value, 'type': synrestr_type}
			
		themrole_type = themrole.get('type')
		
	#     selrestr_logic = themrole.find('SELRESTRS').get('logic')
		
	#     if selrestr_logic == None: selrestr_logic = 'and'
	#     if selrestr_logic.strip() == 'and': selrestr_logic = '&'
	#     elif selrestr_logic.strip() == 'or': selrestr_logic = '|'
			
	#     selrestrs = [parse_selrestr(selrestr) for selrestr in themrole.find('SELRESTRS')]
		found_selrestrs = themrole.find('SELRESTRS')
		if found_selrestrs is not None: 
			if found_selrestrs.get('logic'):
				selrestr_logic = found_selrestrs.get('logic')
			else:
				selrestr_logic = 'and'

			if selrestr_logic.strip() == 'and': selrestr_logic = '&'
			elif selrestr_logic.strip() == 'or': selrestr_logic = '|'

			if len(found_selrestrs) > 0: 
				selrestrs = [parse_selrestr(selrestr) for selrestr in found_selrestrs]
			else:
				selrestrs = None
		else:
			selrestrs = None
			selrestr_logic = None

		found_synrestrs = themrole.find('SYNRESTRS')
		if found_synrestrs is not None:
			if found_synrestrs.get('logic'):
				synrestr_logic = found_synrestrs.get('logic')
			else:
				synrestr_logic = 'and'

			if synrestr_logic.strip() == 'and': synrestr_logic = '&'
			elif synrestr_logic.strip() == 'or': synrestr_logic = '|'

			synrestrs = [parse_synrestr(synrestr) for synrestr in found_synrestrs]
			
		else:
			synrestrs = None
			synrestr_logic = None
		
		return {'themrole': themrole_type, 'selrestrs': {'selrestrs_list':selrestrs, 'selrestr_logic':selrestr_logic}, 'synrestrs': {'synrestr_list': synrestrs, 'synrestr_logic':synrestr_logic}}

	def parse_frame(frame, class_id, frame_num):
		def parse_description(frame_description):
			primary = frame_description.get('primary')
			secondary = frame_description.get('secondary')
			number = frame_description.get('descriptionNumber')
			xtag = frame_description.get('xtag')
			return {'primary': primary, 'secondary': secondary, 'number': number, 'xtag': xtag}
		
		def parse_syntax_arg(syntax_arg):
			def parse_selrestr(selrestr):
				if selrestr.tag == 'SELRESTRS':
					return [parse_selrestr(selrestr) for selrestr in found_selrestrs]
				selrestr_type = selrestr.get('type')
				value = selrestr.get('Value')
				return {'value': value, 'type': selrestr_type}
			
			def parse_synrestr(synrestr):
				synrestr_type = synrestr.get('type')
				value = synrestr.get('Value')
				return {'value': value, 'type': synrestr_type}
			
			arg_type = syntax_arg.tag
			if arg_type == 'VERB': value = 'VERB'
			elif arg_type == 'PREP':
				value = syntax_arg.get('value')
				#if no values specified (e.g. attend-107.4-1), return generic placeholder string 'PREP'
				if value == None: value = 'PREP'
				#resolves inconsistencies in how the prep values are saved in the XML
				else: value = value.replace('| ', '')

			else: value = syntax_arg.get('value')
				
			found_selrestrs = syntax_arg.find('SELRESTRS')
			if found_selrestrs is not None: 
				if found_selrestrs.get('logic'):
					selrestr_logic = found_selrestrs.get('logic')
				else:
					selrestr_logic = 'and'
				
				if selrestr_logic.strip() == 'and': selrestr_logic = '&'
				elif selrestr_logic.strip() == 'or': selrestr_logic = '|'
					
				if len(found_selrestrs) > 0: 
					selrestrs = [parse_selrestr(selrestr) for selrestr in found_selrestrs]
				else:
					selrestrs = None
			else:
				selrestrs = None
				selrestr_logic = None
			
			found_synrestrs = syntax_arg.find('SYNRESTRS')
			if found_synrestrs is not None:
				if found_synrestrs.get('logic'):
					synrestr_logic = found_synrestrs.get('logic')
				else:
					synrestr_logic = 'and'
				
				if synrestr_logic.strip() == 'and': synrestr_logic = '&'
				elif synrestr_logic.strip() == 'or': synrestr_logic = '|'
					
				if len(found_synrestrs) > 0: 
					synrestrs = [parse_synrestr(synrestr) for synrestr in found_synrestrs]
				else:
					synrestrs = None
			else:
				synrestrs = None
				synrestr_logic = None
				
			return {'arg_type': arg_type, 'value': value, 'selrestrs': {'selrestr_list': selrestrs, 'selrestr_logic': selrestr_logic }, 'synrestrs': {'synrestr_list': synrestrs, 'synrestr_logic':synrestr_logic}}
		
		def parse_pred(predicate):
			def parse_arg(arg):
				arg_type = arg.get('type')
				value = arg.get('value')
				return {'arg_type': arg_type, 'value': value}
				
			pred_value = predicate.get('value')
			boolean = predicate.get('bool')
			args = [parse_arg(arg) for arg in predicate.find('ARGS')]
			return {'predicate': pred_value, 'args': args, 'bool': boolean}
		
		def parse_fd(example_text):
			"Parse Force Dynamics representations"
			match = fd_by_example.get(normalize_fd_example_text(example_text))
			if match is None:
				return None
			key, list_of_feats = match
			return {'num':key, 'fd_val':list_of_feats[4]}


		def dependency_tree_svg(example_text, ex_num):
			spacy_doc = spacy_nlp(example_text)
			svg_xml = displacy.render(spacy_doc,style='dep', options={'compact':True, 'color': 'black'})
			filename = str(class_id)+'_'+str(frame_num)+'_'+str(ex_num)+'.svg'
			with open(path_dep+filename, 'w', encoding='utf-8') as wf:
				wf.write(svg_xml)
			return '/'+path_dep+filename

		
		description = parse_description(frame.find('DESCRIPTION'))
		examples = [{'example_text':example.text.replace('\n','').strip(), 'fd': parse_fd(example.text), 'svg': dependency_tree_svg(example.text.strip(), ex_n)} for ex_n, example in enumerate(frame.find('EXAMPLES'))]
		syntax = [parse_syntax_arg(arg) for arg in frame.find('SYNTAX')]
		semantics = [parse_pred(pred) for pred in frame.find('SEMANTICS')]
		return {'description': description, 'examples': examples, 'syntax': syntax, 'semantics': semantics}

	def parse_numerical_comparison_id(class_id):
		num_format_list = ''.join(class_id.split('-')[1:]).split('.')
		return float(num_format_list[0]+'.'+''.join(num_format_list[1:]))

	def parse_vn_class(vn_class):
		class_id = vn_class.get('ID')
		num_comparison_id = parse_numerical_comparison_id(class_id)
		members = [parse_member(member,class_id) for member in vn_class.find('MEMBERS') if member.tag == 'MEMBER']
		themroles = [parse_themrole(themrole) for themrole in vn_class.find('THEMROLES') if themrole.tag == 'THEMROLE']
		frames = [parse_frame(frame, class_id, frame_num) for frame_num, frame in enumerate(vn_class.find('FRAMES')) if frame.tag == 'FRAME']
		try:
			subclasses = [parse_vn_class(subclass) for subclass in vn_class.find('SUBCLASSES') if subclass.tag=='VNSUBCLASS']
			if not subclasses:
				subclasses = None
		except:
			print("Problem with subclass structure in "+str(class_id))
			print(vn_class.find('SUBCLASSES'))
			subclasses = None
		return {'class_id': class_id, 'num_comparison_id': num_comparison_id, 'members': members, 'themroles': themroles, 'frames': frames, 'subclasses': subclasses, 'resource_type': 'vn'}


	def include_subclasses(vn_classes):
		for vn_class in vn_classes:
			subclasses = vn_class['subclasses']
			if subclasses:
				vn_classes.extend(subclasses)
		return vn_classes



	#Populate the database
	def vn_to_mongo(file):
		with open(path_verbnet+file,'r') as xml_file:
			root = etree.parse(xml_file).getroot()
			vn_class = parse_vn_class(root)
			return vn_class

	verbnet_xml = [f for f in os.listdir(path_verbnet) if f.endswith('.xml')]
	verbnet_mongo = include_subclasses([vn_to_mongo(f) for f in verbnet_xml])
	#print(verbnet_mongo)	
	db.drop_collection('verbnet')
	vn_collection = db['verbnet']
	vn_collection.insert_many(verbnet_mongo)



	#VN Reference Information (themrole defs, predicate defs, etc.)
	predicate_definition_files = ['../corpora/reference_docs/'+f for f in ['vn_verb_specific_predicates.tsv',
	 'vn_semantic_predicates.tsv',
	 'vn_constants.tsv']]

	def add_predicate_defs(predicate_definition_file, mongo_collection):
		with open(predicate_definition_file, 'r') as definition_tsv:
			#skip first line (tsv heading)
			next(definition_tsv)
			for line in definition_tsv:
				pred_fields = line.split('\t')
				pred_name = pred_fields[0].split('(')[0].strip()
				pred_def = pred_fields[1]
				pred_args = pred_fields[2]
				pred_dict = {'name':pred_name, 'def':pred_def, 'args':pred_args}
				mongo_collection.insert_one(pred_dict)

	db.drop_collection('vn_predicates')
	vn_pred_collection = db['vn_predicates']
	add_predicate_defs('../corpora/reference_docs/vn_semantic_predicates.tsv', vn_pred_collection)

	db.drop_collection('vn_constants')
	vn_constant_collection = db['vn_constants']
	add_predicate_defs('../corpora/reference_docs/vn_constants.tsv', vn_constant_collection)

	db.drop_collection('vn_verb_specific')
	vn_verb_specific_collection = db['vn_verb_specific']
	add_predicate_defs('../corpora/reference_docs/vn_verb_specific_predicates.tsv', vn_verb_specific_collection)

	html_dir = '../corpora/reference_docs/vn_themrole_html/'
	html_files = [html_dir + f for f in os.listdir(html_dir)]

	themrole_defs = []

	for html_file in html_files:
		html_doc = open(html_file,'r')
		soup = BeautifulSoup(html_doc, 'html.parser')
		h3_tags = [t.get_text() for t in soup.find_all('h3')]
		
		themrole = str(soup.h2).split(':')[1].split('<')[0].strip()
		description = 'No description found'
		example = 'No examples found'
		
		for tag in h3_tags:
			tag_fields = tag.split(':')
			if tag_fields[0].strip() == 'Description':
				description = tag_fields[1].strip()
			elif tag_fields[0].strip() == 'Example':
				example = tag_fields[1].strip()
		
		themrole_dict = {'name':themrole, 'description':description, 'example':example}
		themrole_defs.append(themrole_dict)

	db.drop_collection('vn_themroles')
	vn_themroles_db = db['vn_themroles']
	vn_themroles_db.insert_many(themrole_defs)


	def get_themrole_fields(class_id, frame_json, themrole_name):
		#Get Class ID's for parent classes of current class (returned list includes the original class)
		themrole_name_stripped = themrole_name.strip('?').strip('_i').strip('_j').strip('Co-')
		
		#Edge case: Co-Patient not defined; use attributes for Patient
	#     if themrole_name_stripped == 'Co-Patient': 
	#         themrole_name_stripped = 'Patient'

		selrestr_list = None
		selrestr_logic = None
		
		#Get the list of parent class id's (up to & including current class_id) from which this class would inherit semantic restrictions (if any)
		parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
		for parent_class_id in parents:
			selrestr_fields = db['verbnet'].find_one({ 'class_id': parent_class_id, 'themroles.themrole':themrole_name_stripped}, {'themroles.$':1})
			if selrestr_fields:
				selrestr_list = selrestr_fields['themroles'][0]['selrestrs']['selrestrs_list']
				selrestr_logic = selrestr_fields['themroles'][0]['selrestrs']['selrestr_logic']
		
		themrole_entry = db['vn_themroles'].find_one({'name':themrole_name_stripped})

		if themrole_entry:
			themrole_desc = themrole_entry['description']
			themrole_example = themrole_entry['example']
		else:
			themrole_desc = 'no entry found'
			themrole_example = 'no entry found'
			
		frame_syntax = frame_json['syntax']
		synrestrs = [arg['synrestrs'] for arg in frame_syntax if arg['value'] == themrole_name_stripped]
		if synrestrs == []:
			synrestr_list = None
			synrestr_logic = None
		else:
			synrestr_list = synrestrs[0]['synrestr_list']
			synrestr_logic = synrestrs[0]['synrestr_logic']
		
		frame_level_selrestrs = [arg['selrestrs'] for arg in frame_syntax if arg['value'] == themrole_name_stripped]
		if frame_level_selrestrs == []:
			frame_level_selrestr_list = None
			frame_level_selrestr_logic = None
		else:
			frame_level_selrestr_list = frame_level_selrestrs[0]['selrestr_list']
			frame_level_selrestr_logic = frame_level_selrestrs[0]['selrestr_logic']

		return {'selrestr_list':selrestr_list, 'selrestr_logic':selrestr_logic, 'synrestr_list':synrestr_list, 
		'synrestr_logic':synrestr_logic, 'themrole_desc':themrole_desc, 'themrole_example':themrole_example,
		'frame_level_selrestrs_list':frame_level_selrestr_list, 'frame_level_selrestrs_logic': frame_level_selrestr_logic}

	def aggregate_themrole_list(class_id):
		parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
		themroles = []
		for parent_class_id in parents:
			tr_list = db['verbnet'].find_one({'class_id': parent_class_id}, {'themroles.themrole':1})
			if tr_list:
				parent_themroles = [themrole['themrole'] for themrole in tr_list['themroles']]
				themroles.extend(parent_themroles)
		return list(set(themroles))

	db.drop_collection('vn_themrole_fields')
	vn_themrole_fields = db['vn_themrole_fields']

	vn_class_ids = [class_id['class_id'] for class_id in list(db.verbnet.find({},{'class_id':1, '_id':0}))]
	for class_id in vn_class_ids:
		class_frames = []
		cf = db.verbnet.find_one({'class_id':class_id}, {'frames.examples.svg':0})
		if cf:
			class_frames = cf['frames']

		class_themrole_names = aggregate_themrole_list(class_id)
		for frame_json in class_frames:
			frame_desc = frame_json['description']['primary']
			for themrole_name in class_themrole_names:
				themrole_fields = get_themrole_fields(class_id, frame_json, themrole_name)
				vn_themrole_fields.insert_one({'class_id': class_id, 'frame_desc': frame_desc, 'themrole_name': themrole_name, 'themrole_fields': themrole_fields})
	
	ref_to_db()

	print("Finished building VN Collections.")

################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
#FRAMENET
def build_framenet_collection():
	print("Building FrameNet Collections...")

	def parse_fn_def(definition_markup):
		def_split = definition_markup.split('<ex>')
		def_text_markup = def_split[0].strip()
		examples_markup = [ex.replace('<ex>','').replace('</ex>','').strip() for ex in def_split[1:]]
		return {'def_text_markup': def_text_markup, 'examples_markup': examples_markup}
		
	def parse_frame_element(frame_element):
		def_markup = frame_element['definitionMarkup'].replace('<def-root>','').replace('</def-root>','').strip()
		return {'fe_name': frame_element['name'], 'core_type': frame_element['coreType'], 'abbrev': frame_element['abbrev'], 'def_markup': def_markup}

	def parse_lexical_unit(lexical_unit):
		lu_name = ('_').join(lexical_unit['name'].split(' '))
		return {'lu_name': lu_name, 'lu_def': lexical_unit['definition'], 'url': lexical_unit['URL']}

	from nltk.corpus.reader.framenet import FramenetCorpusReader

	def fn_to_mongo(frame):
		frame_definition = parse_fn_def(frame['definitionMarkup'])
		frame_elements = [parse_frame_element(frame['FE'][fe]) for fe in frame['FE'].keys()]
		lexical_units = [parse_lexical_unit(frame['lexUnit'][lu]) for lu in frame['lexUnit'].keys()]
		fn_frame = {'name': frame['name'], 'definition': frame_definition, 'elements': frame_elements, 'lexical_units': lexical_units, 'url': frame['URL'], 'resource_type': 'fn'}
		return fn_frame

	fn = FramenetCorpusReader(path_framenet, [f for f in path_framenet if f.endswith('.xml')])
	frames = fn.frames()
	framenet_mongo = [fn_to_mongo(f) for f in frames]

	db.drop_collection('framenet')
	fn_collection = db['framenet']
	fn_collection.insert_many(framenet_mongo)

	print("Finished building FrameNet Collections.")
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################



################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
#PROPBANK
def build_propbank_collection():
	print("Building PropBank Collections...")
	def parse_predicate(predicate):
		def parse_roleset(roleset):
			def parse_aliases(aliases):
				alias_list = []
				for alias in aliases:
					alias_name = alias.text
					pos = alias.get('pos')
					fn = alias.get('framenet').split(' ') if alias.get('framenet') else ''
					vn = alias.get('verbnet').split(' ') if alias.get('verbnet') else ''
					alias_list.append({'alias_name': alias_name, 'pos': pos, 'fn': fn, 'vn': vn})
				return alias_list
			
			def parse_roles(roles):
				role_list = []
				for role in roles:
					descr = role.get('descr')
					f = role.get('f')
					n = role.get('n')
					
					vnroles_found = role.findall('vnrole')
					if vnroles_found:
						vnroles = [vnrole.get('vncls')+'-'+vnrole.get('vntheta').lower() for vnrole in vnroles_found]
						
					else:
						vnroles = None
					role_list.append({'descr':descr, 'f': f, 'n': n, 'vnroles': vnroles})
				return role_list
			
			def parse_examples(examples):
				def parse_ex_args(args):
					args_list = []
					for arg in args:
						arg_text = arg.text
						f = arg.get('f')
						n = arg.get('n')
						args_list.append({'arg_text': arg_text, 'f':f, 'n':n})
					return args_list
				
				def parse_ex_rel(rel):
					if rel != None:
						rel_text = rel.text
						f = rel.get('f')
					else:
						rel_text = ''
						f = ''
					return {'rel_text': rel_text, 'f': f}

				example_list = []
				for example in examples:
					example_name = example.get('name')
					example_text = example.find('text').text
					args = parse_ex_args(example.findall('arg'))
					rel = parse_ex_rel(example.find('rel'))
					example_list.append({'example_name': example_name, 'example_text': example_text, 'args': args, 'rel': rel})
				
				return example_list
						
			roleset_id = roleset.get('id')
			roleset_name = roleset.get('name')
			aliases = parse_aliases(roleset.find('aliases'))
			roles = parse_roles(roleset.find('roles'))
			examples = parse_examples(roleset.findall('example'))
			return {'roleset_id': roleset_id, 'roleset_name': roleset_name, 'aliases': aliases, 'roles': roles, 'examples': examples}

		lemma = predicate.get('lemma')
		rolesets = [parse_roleset(r) for r in predicate.findall('roleset')]
		
		return {'lemma': lemma, 'rolesets': rolesets}

	def parse_pb_frame(pb_frame):
		predicates = [parse_predicate(p) for p in pb_frame.findall('predicate')]
		return {'predicates':predicates, 'resource_type': 'pb'}

	def pb_to_mongo(file):
		with open(path_propbank+file,'r') as xml_file:
			root = etree.parse(xml_file).getroot()
			pb_frame = parse_pb_frame(root)
			pb_frame['frameset_id'] = file[:-4]
			return pb_frame
		
	propbank_xml = [f for f in os.listdir(path_propbank) if f.endswith('.xml')]
	propbank_mongo = [pb_to_mongo(f) for f in propbank_xml]

	db.drop_collection('propbank')
	pb_collection = db['propbank']
	pb_collection.insert_many(propbank_mongo)

	print("Finished building PropBank Collections.")
################################################################################################################################################################
################################################################################################################################################################

def build_publications_collection():
	'''Seed of the `publications` collection, grouped into 5 sections: Understanding the
	Current VerbNet, Foundational Books and Papers, Evaluation and Evolution of VerbNet and
	Related Resources (Semlink, VerbNet Parser), Uses of VerbNet, and Linguistically Diverse
	VerbNets. Safe to re-run on any environment: each seed entry is upserted by (section,
	title), so it restores/updates just those canonical entries without touching unrelated
	publications added later through the admin UI. Also retires any leftover documents from
	the older 'Recent Work' / 'Background Publications' section names (see below).'''

	def authors_list(raw):
		return [a.strip().rstrip('.') for a in raw.split(';') if a.strip()]

	def citation_of(authors, title, venue):
		return '{}. {}. {}'.format('; '.join(authors), title, venue)

	SEC_UNDERSTANDING = 'Understanding the Current VerbNet'
	SEC_FOUNDATIONAL = 'Foundational Books and Papers'
	SEC_EVALUATION = 'Evaluation and Evolution of VerbNet and Related Resources (Semlink, VerbNet Parser)'
	SEC_USES = 'Uses of VerbNet'
	SEC_DIVERSE = 'Linguistically Diverse VerbNets'

	seed_publications = [
		# Understanding the Current VerbNet
		{
			'section': SEC_UNDERSTANDING, 'year': 2022,
			'authors': authors_list('Brown, Susan Windisch; Bonn, Julia; Kazeminejad, Ghazaleh; Zaenen, Annie; Pustejovsky, James; Palmer, Martha.'),
			'title': 'Semantic representations for nlp using verbnet and the generative lexicon',
			'hyperlink': '',
			'venue': 'Frontiers in artificial intelligence 5: 821697.',
		},
		{
			'section': SEC_UNDERSTANDING, 'year': 2017,
			'authors': authors_list('Palmer, Martha; Bonial, Claire; Hwang, Jena D.'),
			'title': 'VerbNet: Capturing English verb behavior, meaning and usage',
			'hyperlink': 'https://academic.oup.com/edited-volume/34641/chapter/295177378',
			'venue': 'The Oxford Handbook of Cognitive Science, ed. Susan Chipman. Oxford University Press.',
		},
		{
			'section': SEC_UNDERSTANDING, 'year': None,
			'authors': [],
			'title': 'VerbNet Guidelines',
			'hyperlink': 'http://verbs.colorado.edu/verb-index/VerbNet_Guidelines.pdf',
			'venue': '',
		},
		# Foundational Books and Papers
		{
			'section': SEC_FOUNDATIONAL, 'year': 2008,
			'authors': authors_list('Kipper, Karin; Korhonen, Anna; Ryant, Neville; Palmer, Martha.'),
			'title': 'A Large-scale Classification of English Verbs',
			'hyperlink': 'https://link.springer.com/article/10.1007/s10579-007-9048-2',
			'venue': 'Language Resources and Evaluation Journal 42(1). Springer Netherland. pp. 21–40.',
		},
		{
			'section': SEC_FOUNDATIONAL, 'year': 2005,
			'authors': authors_list('Schuler, Karin Kipper.'),
			'title': 'VerbNet: A Broad-Coverage, Comprehensive Verb Lexicon',
			'hyperlink': 'https://www.proquest.com/openview/7ca4b1b9093522a7d8089ff2e987e74e/1?pq-origsite=gscholar&cbl=18750&diss=y',
			'venue': 'PhD Dissertation. University of Pennsylvania.',
		},
		{
			'section': SEC_FOUNDATIONAL, 'year': 1993,
			'authors': authors_list('Levin, Beth.'),
			'title': 'English Verb Classes and Alternations: A Preliminary Investigation',
			'hyperlink': 'https://press.uchicago.edu/ucp/books/book/chicago/E/bo3684144.html',
			'venue': 'University of Chicago Press.',
		},
		# Evaluation and Evolution of VerbNet and Related Resources (Semlink, VerbNet Parser)
		{
			'section': SEC_EVALUATION, 'year': 2024,
			'authors': authors_list('Brown, Susan W.'),
			'title': "Extending VerbNet's verb-specific features to enhance selectional preferences of semantic roles",
			'hyperlink': '',
			'venue': 'In Proceedings of the Fifth International Workshop on Designing Meaning Representations @ LREC-COLING 2024, pp. 124–130.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2024,
			'authors': authors_list('Tu, Jingxuan; Obiso, Tim; Ye, Bingyang; Rim, Kyeongmin; Xu, Keer; Yue, Liulu; Brown, Susan W.; Palmer, Martha; Pustejovsky, James.'),
			'title': 'GLAMR: augmenting AMR with GL-VerbNet event structure',
			'hyperlink': '',
			'venue': 'In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024), pp. 7746–7759.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2023,
			'authors': authors_list('Kazeminejad, Ghazaleh; Palmer, Martha.'),
			'title': 'Event semantic knowledge in procedural text understanding',
			'hyperlink': '',
			'venue': 'In Proceedings of the 12th Joint Conference on Lexical and Computational Semantics (*SEM 2023), pp. 388–398.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2022,
			'authors': authors_list('Kazeminejad, Ghazaleh; Palmer, Martha; Brown, Susan W.; Pustejovsky, James.'),
			'title': 'Componential analysis of English verbs',
			'hyperlink': '',
			'venue': 'Frontiers in artificial intelligence, 5, 780385.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2021,
			'authors': authors_list('Majewska, Olga; Collins, Charlotte; Baker, Simon; Björne, Jari; Brown, Susan W.; Korhonen, Anna; Palmer, Martha.'),
			'title': 'BioVerbNet: A large semantic-syntactic classification of verbs in biomedicine',
			'hyperlink': '',
			'venue': 'Journal of Biomedical Semantics, 12(1), p.12.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2021,
			'authors': authors_list('Gung, James; Palmer, Martha.'),
			'title': 'Predicate representations and polysemy in VerbNet semantic parsing',
			'hyperlink': '',
			'venue': 'In Proceedings of the 14th International Conference on Computational Semantics (IWCS), pp. 51–62.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2020,
			'authors': authors_list('Peterson, Daniel; Brown, Susan W.; Palmer, Martha.'),
			'title': 'Verb class induction with partial supervision',
			'hyperlink': '',
			'venue': 'In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 34, No. 05, pp. 8616–8623).',
		},
		{
			'section': SEC_EVALUATION, 'year': 2020,
			'authors': authors_list('Croft, William; Vigus, Meagan.'),
			'title': 'Event causation and force dynamics in argument structure constructions',
			'hyperlink': '',
			'venue': 'In Perspectives on Causation: Selected Papers from the Jerusalem 2017 Workshop, pp. 151–183. Cham: Springer International Publishing.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2019,
			'authors': authors_list('Huminski, Aleksandra; Liausvia, Fiona; Goel, Amitash.'),
			'title': 'Semantic roles in Verbnet and Framenet: Statistical analysis and evaluation',
			'hyperlink': '',
			'venue': 'In International Conference on Computational Linguistics and Intelligent Text Processing, pp. 135–147. Cham: Springer Nature Switzerland.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2019,
			'authors': authors_list('Brown, Susan W.; Bonn, Julia; Gung, James; Zaenen, Annie; Pustejovsky, James; Palmer, Martha.'),
			'title': 'VerbNet representations: Subevent semantics for transfer verbs',
			'hyperlink': '',
			'venue': 'In Proceedings of the First International Workshop on Designing Meaning Representations, pp. 154–163.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2018,
			'authors': authors_list('Brown, Susan W.; Pustejovsky, James; Zaenen, Annie; Palmer, Martha.'),
			'title': 'Integrating Generative Lexicon Event Structures into VerbNet',
			'hyperlink': 'http://www.lrec-conf.org/proceedings/lrec2018/pdf/1056.pdf',
			'venue': 'In Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC 2018). Miyazaki, Japan.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2018,
			'authors': authors_list('Peterson, Daniel; Palmer, Martha.'),
			'title': 'Bayesian verb sense clustering',
			'hyperlink': '',
			'venue': 'In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 32, No. 1).',
		},
		{
			'section': SEC_EVALUATION, 'year': 2017,
			'authors': authors_list('Palmer, Martha; Bonial, Claire; Choi, Jinho; Hargraves, Orin; Palmer, Derek; Stowe, Kevin.'),
			'title': 'The Pitfalls of Shortcuts: Tales from the word sense tagging trenches',
			'hyperlink': 'https://scholar.google.com/scholar?q=%22The+Pitfalls+of+Shortcuts%3A+Tales+from+the+word+sense+tagging+trenches%22',
			'venue': 'Essays in Lexical Semantics and Computational Lexicography - In Honor of Adam Kilgarriff. M. Diab, A. Villavicencio, M. Apidianaki, V. Kordoni, A. Korhonen, P. Nakov, M. Stevenson (editors). Springer series Text, Speech and Language Technology. Springer.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2017,
			'authors': authors_list('Green, Meredith; Hargraves, Orin; Bonial, Claire; Chen, Jinying; Clark, Lyndsie; Palmer, Martha.'),
			'title': 'VerbNet/OntoNotes-based sense annotation',
			'hyperlink': 'https://link.springer.com/chapter/10.1007/978-94-024-0881-2_26',
			'venue': 'In The Handbook of Linguistic Annotations, ed. James Pustejovsky and Nancy Ide. Springer.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2016,
			'authors': authors_list('Pustejovsky, James; Palmer, Martha; Zaenen, Annie; Brown, Susan W.'),
			'title': 'Integrating VerbNet and GL Predicative Structures',
			'hyperlink': 'https://scholarworks.brandeis.edu/esploro/outputs/conferencePaper/Verb-Meaning-in-Context-Integrating-VerbNet/9924147742001921',
			'venue': 'Interoperability for Semantic Annotation (ISA-12) with LREC-2016. Portorož, Slovenia.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2013,
			'authors': authors_list('Bonial, Claire; Hargraves, Orin; Palmer, Martha.'),
			'title': 'Expanding VerbNet with Sketch Engine',
			'hyperlink': 'https://aclanthology.org/W13-5407/',
			'venue': 'In Proceedings of the Generative Lexicon Conference (GenLex-13). Pisa, Italy.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2012,
			'authors': authors_list('Feeley, Weston; Bonial, Claire; Palmer, Martha.'),
			'title': 'Evaluating the coverage of VerbNet',
			'hyperlink': 'https://sigsem.uvt.nl/isa8/isa8_submission_6-1.pdf',
			'venue': 'In Proceedings of ISA-8: Eighth Joint ACL-ISO Workshop on Interoperable Semantic Annotation. Pisa, Italy.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2011,
			'authors': authors_list('Bonial, Claire; Brown, Susan W.; Corvey, William; Palmer, Martha; Petukhova, Volha; Bunt, Harry.'),
			'title': 'An Exploratory Comparison of Thematic Roles in VerbNet and LIRICS',
			'hyperlink': 'https://let.uvt.nl/general/people/bunt/docs/bonial-final.pdf',
			'venue': 'In Proceedings of the Sixth Joint ISO-ACL SIGSEM Workshop on Interoperable Semantic Annotation (ISA-6), pp. 39–44.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2006,
			'authors': authors_list('Kipper, Karin; Korhonen, Anna; Ryant, Neville; Palmer, Martha.'),
			'title': 'Extending VerbNet with Novel Verb Classes',
			'hyperlink': 'http://www.lrec-conf.org/proceedings/lrec2006/pdf/468_pdf.pdf',
			'venue': 'Proceedings of the Fifth International Conference on Language Resources and Evaluation (LREC). Genoa, Italy.',
		},
		{
			'section': SEC_EVALUATION, 'year': 2004,
			'authors': authors_list('Korhonen, Anna; Briscoe, Ted.'),
			'title': 'Extended Lexical-Semantic Classification of English Verbs',
			'hyperlink': 'https://aclanthology.org/W04-2606/',
			'venue': 'In Proceedings of the HLT/NAACL Workshop on Computational Lexical Semantics. Boston, MA.',
		},
		# Uses of VerbNet
		{
			'section': SEC_USES, 'year': 2026,
			'authors': authors_list('Rim, Kyeongmin; Pustejovsky, James.'),
			'title': 'Subevent structure as a predictor of entity identity change in procedural text',
			'hyperlink': '',
			'venue': 'In Proceedings of the Workshop on Structured Linguistic Data and Evaluation (SLiDE).',
		},
		{
			'section': SEC_USES, 'year': 2026,
			'authors': authors_list('Ahmed, Wafaa; Ivy, Bassey P. U.; Mapari, Suraj; Mahmoud, Ahmed; El-Batrawy, Hend.'),
			'title': 'Exploring machine learning approaches to predicting semantic roles from syntactic frames',
			'hyperlink': '',
			'venue': 'In 2026 International Conference on Electronics and Renewable Systems (ICEARS), pp. 1807–1813. IEEE.',
		},
		{
			'section': SEC_USES, 'year': 2026,
			'authors': authors_list('Singh, Diksha P.; Gusain, Divyansh; Bulgarelli, Federica; Hendricks, Anna E.; Beavers, John; Beers, Nathan M.; Nwogu, Ifeoma.'),
			'title': 'A scalable tool for measuring manner and result verbs in developmental language research',
			'hyperlink': '',
			'venue': 'In Proceedings of the 1st Workshop on Computational Developmental Linguistics (CDL), pp. 117–128.',
		},
		{
			'section': SEC_USES, 'year': 2026,
			'authors': authors_list('Farina, Alessia; Passarotti, Marco; Mambrini, Francesco; Pellegrini, Matteo; Moretti, Giovanni; Litta, Eleonora.'),
			'title': 'PREMOVE In LiLa: Integrating Latin preverbed motion verbs with WordNet and VerbNet',
			'hyperlink': '',
			'venue': 'In The Fifteenth Language Resources and Evaluation Conference (LREC 2026), pp. 3672–3683. European Language Resources Association (ELRA).',
		},
		{
			'section': SEC_USES, 'year': 2023,
			'authors': authors_list('Li, Tao; Kazeminejad, Ghazaleh; Brown, Susan W.; Srikumar, Vivek; Palmer, Martha.'),
			'title': 'Learning semantic role labeling from compatible label sequences',
			'hyperlink': '',
			'venue': 'In Findings of the Association for Computational Linguistics: EMNLP 2023, pp. 15561–15572.',
		},
		{
			'section': SEC_USES, 'year': 2023,
			'authors': authors_list('Grasso, Francesco; Rulfi, Valentina L.; Caro, Luigi Di.'),
			'title': 'Verbalignet: Unlocking multilingual exploration of verbal arguments',
			'hyperlink': '',
			'venue': 'In Research Conference on Metadata and Semantics Research, pp. 3–17. Cham: Springer Nature Switzerland.',
		},
		{
			'section': SEC_USES, 'year': 2023,
			'authors': authors_list('Sowański, Maciej; Janicki, Artur.'),
			'title': 'Optimizing machine translation for virtual assistants: Multi-variant generation with VerbNet and conditional beam search',
			'hyperlink': '',
			'venue': 'In 2023 18th Conference on Computer Science and Intelligence Systems (FedCSIS), pp. 1149–1154. IEEE.',
		},
		{
			'section': SEC_USES, 'year': 2022,
			'authors': authors_list('Strelnikoff, Sonya; Jammalamadaka, Aditya; Lu, Tsai-Ching.'),
			'title': 'Semantic causal abstraction for event prediction',
			'hyperlink': '',
			'venue': 'In International Cross-Domain Conference for Machine Learning and Knowledge Extraction, pp. 188–200. Cham: Springer International Publishing.',
		},
		{
			'section': SEC_USES, 'year': 2021,
			'authors': authors_list('Kazeminejad, Ghazaleh; Palmer, Martha; Li, Tao; Srikumar, Vivek.'),
			'title': 'Automatic entity state annotation using the VerbNet semantic parser',
			'hyperlink': '',
			'venue': 'In Proceedings of the Joint 15th Linguistic Annotation Workshop (LAW) and 3rd Designing Meaning Representations (DMR) Workshop, pp. 123–132.',
		},
		{
			'section': SEC_USES, 'year': 2021,
			'authors': authors_list('Basu, Kinjal; Varanasi, Sarat Chandra; Shakerin, Farhad; Arias, Joaquín; Gupta, Gopal.'),
			'title': 'Knowledge-driven natural language understanding of English text and its applications',
			'hyperlink': '',
			'venue': 'In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 35, No. 14, pp. 12554–12563).',
		},
		{
			'section': SEC_USES, 'year': 2020,
			'authors': authors_list('Diwanji, Prakhar; Guo, Hongkai; Singh, Munindar P.; Kalia, Anup.'),
			'title': 'Lin: Unsupervised extraction of tasks from textual communication',
			'hyperlink': '',
			'venue': 'In Proceedings of the 28th International Conference on Computational Linguistics, pp. 1815–1819.',
		},
		{
			'section': SEC_USES, 'year': 2020,
			'authors': authors_list('Amjad, Zainab; Ihsan, Iqra.'),
			'title': 'VerbNet-based citation sentiment class assignment using machine learning',
			'hyperlink': '',
			'venue': 'International Journal of Advanced Computer Science and Applications, 11(9).',
		},
		{
			'section': SEC_USES, 'year': 2019,
			'authors': authors_list('Scicluna, Simon; Strapparava, Carlo.'),
			'title': 'The visual representation of abstract verbs: merging verb classification with iconicity in sign language',
			'hyperlink': '',
			'venue': 'In 2019 IEEE International Conference on Cognitive Computing (ICCC), pp. 73–80. IEEE.',
		},
		{
			'section': SEC_USES, 'year': 2017,
			'authors': authors_list('Wali, Wafa; Gargouri, Bilel; Hamadou, Abdelmajid Ben.'),
			'title': 'Sentence similarity computation based on WordNet and VerbNet',
			'hyperlink': '',
			'venue': 'Computación y Sistemas, 21(4), pp. 627–635.',
		},
		{
			'section': SEC_USES, 'year': 2016,
			'authors': authors_list('Gerz, Daniela; Vulić, Ivan; Hill, Felix; Reichart, Roi; Korhonen, Anna.'),
			'title': 'Simverb-3500: A large-scale evaluation set of verb similarity',
			'hyperlink': '',
			'venue': 'In Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pp. 2173–2182.',
		},
		# Linguistically Diverse VerbNets
		{
			'section': SEC_DIVERSE, 'year': 2024,
			'authors': authors_list('Chungnoi, Kanthika; Kongkachandra, Rattapoom; Gulyanon, Signal.'),
			'title': 'The computational method for supporting Thai VerbNet construction',
			'hyperlink': '',
			'venue': 'ACM Transactions on Asian and Low-Resource Language Information Processing, 23(2), pp. 1–15.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2024,
			'authors': authors_list('Akram, Sana; Tahir, Muhammad Sarmad.'),
			'title': 'Mapping of English and Punjabi verb classes; a corpus based study',
			'hyperlink': '',
			'venue': 'Journal of Arts and Linguistics Studies, 2(2), pp. 727–751.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2023,
			'authors': authors_list('Vetulani, Zygmunt; Vetulani, Grażyna.'),
			'title': 'Towards lexicon-grammar VerbNets through lexical ontologies',
			'hyperlink': '',
			'venue': 'Neophilologica, 35, pp. 1–32.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2023,
			'authors': authors_list('Liu, Mei-chun.'),
			'title': 'Semantic Annotation and Mandarin VerbNet',
			'hyperlink': '',
			'venue': 'In Chinese Language Resources: Data Collection, Linguistic Analysis, Annotation and Language Processing, pp. 187–210. Cham: Springer International Publishing.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2020,
			'authors': authors_list('Liu, Mei-chun.'),
			'title': 'The construction and annotation of a semantically enriched database: the Mandarin VerbNet and its NLP applications',
			'hyperlink': '',
			'venue': 'From minimal contrast to meaning construct: Corpus-based, near synonym driven approaches to Chinese lexical semantics, pp. 257–272.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2020,
			'authors': authors_list('Estarrona, Aitziber; Aldezabal, Izaskun; Díaz de Ilarraza, Arantza.'),
			'title': 'How the corpus-based Basque Verb Index lexicon was built',
			'hyperlink': '',
			'venue': 'Language Resources and Evaluation, 54(1), pp. 73–95.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2020,
			'authors': authors_list('Linh, Ha Manh; Huyen, Nguyen Thi Minh.'),
			'title': 'Construction of a VerbNet style lexicon for Vietnamese',
			'hyperlink': '',
			'venue': 'In Proceedings of the 34th Pacific Asia Conference on Language, Information and Computation, pp. 84–91.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2017,
			'authors': authors_list('Bick, Eckhard.'),
			'title': 'From treebank to Propbank: A semantic-role and VerbNet corpus for Danish',
			'hyperlink': '',
			'venue': 'In Proceedings of the 21st Nordic Conference on Computational Linguistics, pp. 202–210.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2016,
			'authors': authors_list('Danlos, Laurence; Pradet, Quentin; Barque, Lucie; Nakamura, Takuya; Constant, Matthieu.'),
			'title': 'Un Verbenet du français [A Verbnet for French]',
			'hyperlink': '',
			'venue': 'Traitement automatique des langues, 57(1), pp. 33–58.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2016,
			'authors': authors_list('Busso, Lucia; Lenci, Alessandro.'),
			'title': 'Italian VerbNet: a construction-based approach to Italian verb classification',
			'hyperlink': '',
			'venue': 'In Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), pp. 2633–2642. ELRA.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2016,
			'authors': authors_list('Hautli-Janisz, Annette.'),
			'title': 'See the forest and the trees: visual verb class identification in Urdu/Hindi VerbNet',
			'hyperlink': '',
			'venue': 'VisLR II: Visualization as Added Value in the Development, Use and Evaluation of Language Resources, p. 16.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2015,
			'authors': authors_list('Hautli, Annette; King, Tracy Holloway; Ramchand, Gillian.'),
			'title': 'Encoding event structure in urdu/hindi verbnet',
			'hyperlink': '',
			'venue': 'In Proceedings of the 3rd Workshop on EVENTS: Definition, Detection, Coreference, and Representation, pp. 25–33.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2014,
			'authors': authors_list('Pradet, Quentin; Danlos, Laurence; De Chalendar, Gaël.'),
			'title': 'Adapting VerbNet to French using existing resources',
			'hyperlink': '',
			'venue': "In LREC'14 - Ninth International Conference on Language Resources and Evaluation.",
		},
		{
			'section': SEC_DIVERSE, 'year': 2014,
			'authors': authors_list('Scarton, Carolina; Duran, Magali Sanches; Aluísio, Sandra M.'),
			'title': 'Using cross-linguistic knowledge to build VerbNet-style lexicons: Results for a (Brazilian) Portuguese VerbNet',
			'hyperlink': '',
			'venue': 'In Computational Processing of the Portuguese Language: 11th International Conference, PROPOR 2014, pp. 149–160. Springer International Publishing.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2012,
			'authors': authors_list('Scarton, Carolina; Aluísio, Sandra.'),
			'title': 'Towards a cross-linguistic VerbNet-style lexicon for Brazilian Portuguese',
			'hyperlink': '',
			'venue': 'In Workshop on Creating Cross-language Resources for Disconnected Languages and Styles Workshop Programme, p. 11.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2011,
			'authors': authors_list('Mousser, Jaouad.'),
			'title': 'Classifying arabic verbs using sibling classes',
			'hyperlink': '',
			'venue': 'In the Proceedings of the International Workshop on Computational Semantics, Oxford, UK.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2010,
			'authors': authors_list('Sun, Lin; Korhonen, Anna; Poibeau, Thierry; Messiant, Cédric.'),
			'title': 'Investigating the cross-linguistic potential of VerbNet-style classification',
			'hyperlink': '',
			'venue': 'In CoLing 2010, p. 94.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2010,
			'authors': authors_list('Mousser, Jaouad.'),
			'title': 'A Large Coverage Verb Taxonomy for Arabic',
			'hyperlink': '',
			'venue': 'In LREC.',
		},
		{
			'section': SEC_DIVERSE, 'year': 2008,
			'authors': authors_list('Liu, Mei-chun; Chiang, Ting-yi.'),
			'title': 'The construction of Mandarin VerbNet: A frame-based study of statement verbs',
			'hyperlink': '',
			'venue': 'Language and Linguistics 9, no. 2: 239–270.',
		},
	]

	for order, pub in enumerate(seed_publications):
		pub['order'] = order
		pub['subject'] = ''
		pub['description'] = ''
		pub['citation'] = citation_of(pub['authors'], pub['title'], pub['venue'])

	publications_collection = db['publications']
	# The old 'Recent Work' / 'Background Publications' sections were retired in favor of
	# the 5 sections above; every title that lived there has been re-seeded under its new
	# section name, so the old-named documents are now orphaned duplicates. Remove them.
	retired = publications_collection.delete_many({'section': {'$in': ['Recent Work', 'Background Publications']}})
	if retired.deleted_count:
		print("Removed {} publication(s) under retired section names.".format(retired.deleted_count))

	upserted, matched = 0, 0
	for pub in seed_publications:
		result = publications_collection.update_one(
			{'section': pub['section'], 'title': pub['title']},
			{'$set': pub},
			upsert=True,
		)
		if result.upserted_id is not None:
			upserted += 1
		else:
			matched += 1
	print("Seeded publications: {} inserted, {} updated.".format(upserted, matched))

	print("Finished building Publications Collection.")
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
