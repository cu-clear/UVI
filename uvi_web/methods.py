#uvi_web/methods.py

import random
# import json
from bson.json_util import dumps
from randomcolor import RandomColor
from operator import itemgetter
import re

from pymongo import MongoClient

mongo_client = MongoClient()
db = mongo_client['uvi_corpora']

def top_parent_id(class_id):
	return ('-').join(class_id.split('-')[:2])

def full_class_hierarchy_tree(class_id):
	top_parent_id = ('-').join(class_id.split('-')[:2])
	top_parent_class = db['verbnet'].find_one({'class_id': top_parent_id})
	def get_subclass_ids(parent_class_id):
		subclasses_list = db['verbnet'].find_one({'class_id': parent_class_id})['subclasses']
		if subclasses_list:
			return [subclass['class_id'] for subclass in subclasses_list]
		else:
			return None

	def subclass_hierarchy_tree(parent_id, depth_counter):
		subclasses = get_subclass_ids(parent_id)
		
		html_string = ''
		
		if subclasses == None:
			return html_string
		
		else:
			for subclass in subclasses:
				if subclass == class_id:
					html_string += '&nbsp' * 6 * depth_counter + '<span style=background-color:MistyRose>' + subclass + '</span><br />'
				else:
					html_string += '&nbsp' * 6 * depth_counter + subclass + '<br />'

				html_string += subclass_hierarchy_tree(subclass, depth_counter+1)
			return html_string
			
	return top_parent_id + '<br />' + subclass_hierarchy_tree(top_parent_id, 1)

def vn_sanitized_class(vn_class_id):
	def del_original(vn_class_json, original_class_id):
		subclasses = vn_class_json['subclasses']
		if subclasses != None:
			class_ids = [vn_subclass_json['class_id'] for vn_subclass_json in subclasses]
			if original_class_id in class_ids:
				vn_class_json['subclasses'] = [vn_subclass for vn_subclass in vn_class_json['subclasses'] if vn_subclass['class_id'] != original_class_id]
				return vn_class_json
			else:
				for subclass in vn_class_json['subclasses']:
					del_original(subclass, original_class_id)
	#if already top-level class, return None type
	if len(vn_class_id.split('-')) == 2:
		return None
	else:
		top_parent_id = ('-').join(vn_class_id.split('-')[:2])
		top_parent_json = db.verbnet.find_one({'class_id': top_parent_id})
		del_original(top_parent_json, vn_class_id)
		return [top_parent_json]


def remove_object_ids(matched_vn):
	for doc in matched_vn:
		doc.pop('_id')
		if doc['subclasses']:
			remove_object_ids(doc['subclasses'])
	return matched_vn

def find_matching_ids(lemmas, incl_vn, incl_fn, incl_pb, incl_wn, multiword_behavior, sort_behavior):
	def sort_matched_ids(matched_ids):
		if sort_behavior == 'alpha':
			for resource in matched_ids:
				matched_ids[resource].sort()
		elif sort_behavior == 'num':
			# vn_elements = matched_elements['VerbNet']
			vn_elements_numsort = sorted([(class_id, float('.'.join((class_id.split('-')[1]).split('.')[:2]))) for class_id in matched_ids['VerbNet']], key=itemgetter(1))
			matched_ids['VerbNet'] = [class_id for class_id, numerical_id in vn_elements_numsort]
		return matched_ids


	matched_ids = {}
	if multiword_behavior == 'and':
		if incl_vn:
			matched_ids['VerbNet'] = [vn_class['class_id'] for vn_class in db.verbnet.find({'members.name': {'$all': lemmas}}, {'class_id':1})]
		if incl_fn:
			matched_ids['FrameNet'] = [frame['name'] for frame in db.framenet.find({'lexical_units.lu_name': {'$all': [lemma+'.v' for lemma in lemmas]}}, {'name':1})]
		if incl_pb:
			matched_ids['PropBank'] = [pb_frame['frameset_id'] for pb_frame in db.propbank.find({'predicates.lemma': {'$all': [lemma for lemma in lemmas]}}, {'frameset_id':1})]
		# if incl_wn:
		#   pass
		return sort_matched_ids(matched_ids)

	elif multiword_behavior == 'or':
		if incl_vn:
			matched_ids['VerbNet'] = [vn_class['class_id'] for vn_class in db.verbnet.find({'members.name': {'$in': lemmas}}, {'class_id':1})]
		if incl_fn:
			matched_ids['FrameNet'] = [frame['name'] for frame in db.framenet.find({'lexical_units.lu_name': {'$in': [lemma+'.v' for lemma in lemmas]}}, {'name':1})]
		if incl_pb:
			matched_ids['PropBank'] = [pb_frame['frameset_id'] for pb_frame in db.propbank.find({'predicates.lemma': {'$in': [lemma for lemma in lemmas]}}, {'frameset_id':1})]
		# if incl_wn:
		#   pass
		return sort_matched_ids(matched_ids)


def find_matching_elements(mongo, lemmas, themrole, pred, const, verb_specific, incl_vn, incl_fn, incl_pb, incl_wn, multiword_behavior):
	matched_elements = {}
	if lemmas:
		if multiword_behavior == 'and':
			if incl_vn:
				matched_elements['VerbNet'] = list(mongo.db.verbnet.find({'members.name': {'$all': lemmas}}))
			if incl_fn:
				matched_elements['FrameNet'] = list(mongo.db.framenet.find({'lexical_units.lu_name': {'$all': [lemma+'.v' for lemma in lemmas]}}))
			if incl_pb:
				matched_elements['PropBank'] = list(mongo.db.propbank.find({'predicates.lemma': {'$all': [lemma for lemma in lemmas]}}))
			# if incl_wn:
			#   pass
			return matched_elements

		elif multiword_behavior == 'or':
			if incl_vn:
				matched_elements['VerbNet'] = list(mongo.db.verbnet.find({'members.name': {'$in': lemmas}}))
			if incl_fn:
				matched_elements['FrameNet'] = list(mongo.db.framenet.find({'lexical_units.lu_name': {'$in': [lemma+'.v' for lemma in lemmas]}}))
			if incl_pb:
				matched_elements['PropBank'] = list(mongo.db.propbank.find({'predicates.lemma': {'$in': [lemma for lemma in lemmas]}}))
			# if incl_wn:
			#   pass
			return matched_elements

	elif themrole:
		matched_elements['VerbNet'] = list(db.verbnet.find({'themroles.themrole':themrole}))
		return matched_elements

	elif pred:
		matched_elements['VerbNet'] = list(db.verbnet.find({'semantics.predicate':pred}))
		return matched_elements

	elif const:
		matched_elements['VerbNet'] = list(db.verbnet.find({'frames.semantics.args.arg_type':'Constant','frames.semantics.args.value':const}))
		return matched_elements

	elif verb_specific:
		matched_elements['VerbNet'] = list(db.verbnet.find({'frames.semantics.args.arg_type':'VerbSpecific','frames.semantics.args.value':verb_specific}))
		return matched_elements

def unique_id():
	return ''.join(random.choice('0123456789abcdef') for i in range(16))

def mongo_to_json(elements):
	return dumps(elements)

def colored_pb_example(example):
	arg_text_examples = [arg['arg_text'] for arg in example['args']]
	colors = RandomColor(seed = example['example_name']).generate(count=len(example['args']), luminosity='light')
	color_dict = {arg_text:color for arg_text,color in zip(arg_text_examples, colors)}
	colored_arg_dict = {arg_text:'<span style=background-color:'+color_dict[arg_text]+'>'+arg_text+'</span>' for arg_text in arg_text_examples }
	for arg in example['args']:
		arg['arg_text'] = colored_arg_dict[arg['arg_text']]
	
	for arg_text in arg_text_examples:
		example['example_text'] = example['example_text'].replace(arg_text, colored_arg_dict[arg_text])
		
	return example

#return HTML formatted definition for FrameNet frame
def formatted_def(frame, markup, popover=False):
	frame_elements = frame['elements']
	colors = RandomColor(seed = frame['name']).generate(count=len(frame_elements), luminosity='light')
	color_dict = {f['fe_name']:c for f,c in zip(frame_elements, colors)}
	color_dict_abbrev = {f['abbrev']:c for f,c in zip(frame_elements, colors)}
	
	if popover==True:
		element_dict = {element['fe_name']: formatted_def(frame, element['def_markup']) for element in frame['elements']}
	
	else:
		element_dict = None
		
	pattern_fen = re.compile('<fen[^>]*>[^<]+</fen>')
	for tagset in set(re.findall(pattern_fen, markup)):
		fen = tagset[5:-6]
		try:
			fen_color = color_dict[fen]
			if element_dict:
				fen_def = element_dict.get(fen,'No Entry Found')
				popover_id = 'fen_popover_'+fen
				popover_div_content = '<div id='+popover_id+' style="display:none;"><div class="popover-body">'+fen_def+'</div></div>'
				markup = markup.replace('<fen>'+fen,popover_div_content+'<fen data-trigger="hover focus" data-toggle="popover" data-popover-content="#'+popover_id+'" style="background-color:'+fen_color+';">'+fen)
			else:
				markup = markup.replace('<fen>'+fen,'<fen style="background-color:'+fen_color+';">'+fen)
		except KeyError:
			try:
				fen_color = color_dict_abbrev[fen]
				if element_dict:
					popover_id = 'fen_popover_'+fen
					popover_div_content = '<div id='+popover_id+' style="display:none;"><div class="popover-body">'+fen_def+'</div></div>'
					markup = markup.replace('<fen>'+fen,popover_div_content+'<fen data-trigger="hover focus" data-toggle="popover" data-popover-content="#'+popover_id+'" style="background-color:'+fen_color+';">'+fen)
				else:
					markup = markup.replace('<fen>'+fen,'<fen style="background-color:'+fen_color+';">'+fen)
			except KeyError:
				break

	pattern_t = re.compile('<t[^>]*>[^<]+</t>')
	for tagset in set(re.findall(pattern_t, markup)):
		markup = markup.replace('<t>','<t style="font-weight:bold; text-transform:uppercase;">')

	pattern_ex = re.compile('<fex[^>]*>[^<]+</fex>')
	ex_tags = re.findall(pattern_ex, markup)
	name_pattern = re.compile('<fex (name=".+")>.*</fex>')
	for ex_tag in ex_tags:
		try:
			fex_name_block = re.findall(name_pattern, ex_tag)[0]
			fex_name = fex_name_block.split('=')[1].strip('"')
			try:
				fex_color = color_dict[fex_name]
				markup = markup.replace(fex_name_block, 'style="background-color:'+ fex_color+';"')
			except KeyError:
				try:
					fex_color = color_dict_abbrev[fex_name]
					markup = markup.replace(fex_name_block, 'style="background-color:'+ fex_color+';"')
				except KeyError:
					break
		except IndexError:
			pass

	return markup
# def formatted_def(frame, markup):
# 	frame_elements = frame['elements']
# 	colors = RandomColor(seed = frame['name']).generate(count=len(frame_elements), luminosity='light')
# 	color_dict = {f['fe_name']:c for f,c in zip(frame_elements, colors)}
# 	color_dict_abbrev = {f['abbrev']:c for f,c in zip(frame_elements, colors)}
	
# 	pattern_fen = re.compile('<fen[^>]*>[^<]+</fen>')
# 	for tagset in set(re.findall(pattern_fen, markup)):
# 		fen = tagset[5:-6]
# 		try:
# 			fen_color = color_dict[fen]
# 			markup = markup.replace('<fen>'+fen,'<fen style="background-color:'+fen_color+';">'+fen)
# 		except KeyError:
# 			try:
# 				fen_color = color_dict_abbrev[fen]
# 				markup = markup.replace('<fen>'+fen,'<fen style="background-color:'+fen_color+';">'+fen)
# 			except KeyError:
# 				break

# 	pattern_t = re.compile('<t[^>]*>[^<]+</t>')
# 	for tagset in set(re.findall(pattern_t, markup)):
# 		markup = markup.replace('<t>','<t style="font-weight:bold; text-transform:uppercase;">')

# 	pattern_ex = re.compile('<fex[^>]*>[^<]+</fex>')
# 	ex_tags = re.findall(pattern_ex, markup)
# 	name_pattern = re.compile('<fex (name=".+")>.*</fex>')
# 	for ex_tag in ex_tags:
# 		fex_name_block = re.findall(name_pattern, ex_tag)[0]
# 		fex_name = fex_name_block.split('=')[1].strip('"')
# 		try:
# 			fex_color = color_dict[fex_name]
# 			markup = markup.replace(fex_name_block, 'style="background-color:'+ fex_color+';"')
# 		except KeyError:
# 			try:
# 				fex_color = color_dict_abbrev[fex_name]
# 				markup = markup.replace(fex_name_block, 'style="background-color:'+ fex_color+';"')
# 			except KeyError:
# 				break

# 	return markup

def get_pred_fields(pred_name):
	return db['vn_predicates'].find_one({'name':pred_name})

def get_constant_fields(constant_name):
	return db['vn_constants'].find_one({'name':constant_name})

def get_verb_specific_fields(feature_name):
	found_entry = db['vn_verb_specific'].find_one({'name':feature_name})
	if found_entry == None:
		found_entry = db['vn_verb_specific'].find_one({'name':feature_name.capitalize()})
	return found_entry

def get_themrole_fields_undefined(themrole_name):
	themrole_name_stripped = themrole_name.strip('?').strip('_i').strip('_j').strip('Co-')
	themrole_entry = db['vn_themroles'].find_one({'name':themrole_name_stripped})
	if themrole_entry:
		themrole_desc = themrole_entry['description']
		themrole_example = themrole_entry['example']
	else:
		themrole_desc = 'no entry found'
		themrole_example = 'no entry found'
	return {'themrole_desc': themrole_desc, 'themrole_example': themrole_example}

def get_themrole_fields(class_id, frame_desc_primary, frame_desc_secondary, themrole_name):
	themrole_name_stripped = themrole_name.strip('?').strip('_i').strip('_j').strip('Co-')
	return db.vn_themrole_fields.find_one({'class_id': class_id, 'frame_desc_primary': frame_desc_primary, 'frame_desc_secondary': frame_desc_secondary, 'themrole_name': themrole_name_stripped})

# def get_themrole_fields(class_id, themrole_name):
# 	#Get Class ID's for parent classes of current class (returned list includes the original class)
# 	themrole_name_stripped = themrole_name.strip('?').strip('_i').strip('_j')

# 	selrestr_list = None
# 	selrestr_logic = None
	
# 	#Get the list of parent class id's from which this class would inherit semantic restrictions (if any)
# 	parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
# 	for parent_class_id in parents:
# 		selrestr_fields = db['verbnet'].find_one({ 'class_id': parent_class_id, 'themroles.themrole':themrole_name_stripped}, {'themroles.themrole.$':1})
# 		if selrestr_fields:
# 			selrestr_list = selrestr_fields['themroles'][0]['selrestrs']['selrestrs_list']
# 			selrestr_logic = selrestr_fields['themroles'][0]['selrestrs']['selrestr_logic']

# 	synrestr_list = None
# 	synrestr_logic = None
# 	parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
# 	for parent_class_id in parents:
# 		synrestr_fields = db['verbnet'].find_one({ 'class_id': parent_class_id, 'themroles.themrole':themrole_name_stripped}, {'themroles.themrole.$':1})
# 		if synrestr_fields:
# 			synrestr_list = synrestr_fields['themroles'][0]['synrestrs']['synrestr_list']
# 			synrestr_logic = synrestr_fields['themroles'][0]['synrestrs']['synrestr_logic']

# 	themrole_entry = db['vn_themroles'].find_one({'name':themrole_name_stripped})

# 	if themrole_entry:
# 		themrole_desc = themrole_entry['description']
# 		themrole_example = themrole_entry['example']
# 	else:
# 		themrole_desc = 'no entry found'
# 		themrole_example = 'no entry found'

# 	return {'selrestr_list':selrestr_list, 'selrestr_logic':selrestr_logic, 'synrestr_list':synrestr_list, 
# 	'synrestr_logic':synrestr_logic, 'themrole_desc':themrole_desc, 'themrole_example':themrole_example}



# def vn_lemma_popover_template(member):
# 	wn_list = member['wn']
# 	gr_list = member['grouping']
# 	vs_features = member['vs_features']

# 	html_to_return = "<b>Features:</b><br>"
# 	if vs_features == None: 
# 		html_to_return += 'None<br>'
# 	else: 
# 		for vs_feature in vs_features: 
# 			html_to_return += vs_feature + '<br>'

# 	html_to_return += '<b>WordNet:</b><br>'
# 	if wn_list == None: 
# 		html_to_return += 'None<br>'
# 	else:
# 		for wn in wn_list: 
# 			html_to_return+= wn + '<br>'
	
# 	html_to_return += "<b>Grouping:</b><br>"
# 	if gr_list == None: 
# 		html_to_return += 'None<br>'
# 	else: 
# 		for gr in gr_list: 
# 			html_to_return += gr + '<br>'

# 	return html_to_return


 # def vn_semantic_content(passed_id, predicates, class_id):
#   def get_selrestrs(class_id, themrole_name_stripped):
#       #Get Class ID's for parent classes of current class (returned list includes the original class)
#       selrestr_list = None
#       selrestr_logic = None
#       parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
#       for parent_class_id in parents:
#           selrestr_fields = db['verbnet'].find_one({ 'class_id': parent_class_id, 'themroles.themrole':themrole_name_stripped}, {'themroles.themrole.$':1})
#           if selrestr_fields:
#               selrestr_list = selrestr_fields['themroles'][0]['selrestrs']['selrestrs_list']
#               selrestr_logic = selrestr_fields['themroles'][0]['selrestrs']['selrestr_logic']
#       return (selrestr_list, selrestr_logic)

#   output_html = ''
#   for pred_index, predicate in enumerate(predicates):
#       popover_id = str(passed_id) + str(pred_index)
#       pred_name = predicate['predicate']
#       pred_entry = db['vn_predicates'].find_one({'name':pred_name})
#       pred_def = pred_entry['def']
#       pred_args = pred_entry['args']
#       pred_def_html = '<strong>Definition:</strong><br />' + pred_def + '<br /><strong>Arguments:</strong><br />' + pred_args
#       args_html = ''
#       for arg_index, arg in enumerate(predicate['args']):
#           arg_popover_id = str(passed_id) + str(pred_index) + str(arg_index)
#           if arg['arg_type'] == 'Event':
#               arg_html = '<span style="color:black;">{}</span>'.format(arg['value'].upper())
#           elif arg['arg_type'] == 'ThemRole':
#               themrole_name = arg['value']
#               themrole_name_stripped = arg['value'].strip('?').strip('_i').strip('_j')
#               themrole_entry = db['vn_themroles'].find_one({'name':themrole_name_stripped})

#               if themrole_entry:
#                   themrole_desc = themrole_entry['description']
#                   themrole_example = themrole_entry['example']
#               else:
#                   themrole_desc = 'no entry found'
#                   themrole_example = 'no entry found'

#               # if class_id 
#               selrestr_fields = get_selrestrs(class_id, themrole_name_stripped)
#               selrestr_list = selrestr_fields[0]
#               selrestr_logic = selrestr_fields[1]
#               selrestrs_html = ''
#               if selrestr_list:
#                   selrestrs_html += '<br /><strong style="color:#bf616a;">Selectional Restrictions:</strong><br />'
#                   for selrestr_index, selrestr in enumerate(selrestr_list):
#                       if selrestr_index < len(selrestr_list) - 1:
#                           selrestrs_html += selrestr['value'] + selrestr['type'].upper() + ' ' + selrestr_logic + ' '
#                       else:
#                           selrestrs_html += selrestr['value'] + selrestr['type'].upper()


#               themrole_def_html = '<strong>Description:</strong><br />' + themrole_desc + '<br /><strong>Example:</strong><br />' + themrole_example + selrestrs_html
#               themrole_popover_body_html = '''<div id={} style='display:none;'><div class='popover-body'>{}</div></div>'''.format(arg_popover_id, themrole_def_html)
#               arg_html = themrole_popover_body_html + '''<span style="color:#5e81ac;" data-toggle="popover" data-popover-content="#{}" data-trigger='hover focus' data-placement='top'>{}</span>'''.format(arg_popover_id, themrole_name)

#           elif arg['arg_type'] == 'Constant':
#               arg_html = '<span style="color:#a3be8c;">{}</span>'.format(arg['value'].upper())
#           elif arg['arg_type'] == 'VerbSpecific':
#               arg_html = '<span style="color:black;">{}</span>'.format(arg['value'].upper())

#           if arg_index < len(predicate['args']) - 1:
#               args_html += arg_html + ' , '
#           else:
#               args_html += arg_html

#       popover_body_html = '''<div id={} style='display:none;'><div class='popover-body'>{}</div></div>'''.format(popover_id, pred_def_html)
#       pred_html = '''<span style="color:#bf616a;"><span data-toggle="popover" data-popover-content="#{}" data-trigger='hover focus' data-placement='top'>{}</span>(</span>{}<span style="color:#bf616a;">)</span>'''.format(popover_id, pred_name.upper(), args_html)
#       output_html += popover_body_html + pred_html + '<br />'
#   return output_html

# def vn_syntactic_content(passed_id, syntax, class_id):
#   def get_selrestrs(class_id, themrole_name_stripped):
#       #Get Class ID's for parent classes of current class (returned list includes the original class)
#       selrestr_list = None
#       selrestr_logic = None
#       parents = [('-').join(class_id.split('-')[:x]) for x in range(2, len(class_id.split('-'))+1)]
#       for parent_class_id in parents:
#           selrestr_fields = db['verbnet'].find_one({ 'class_id': parent_class_id, 'themroles.themrole':themrole_name_stripped}, {'themroles.themrole.$':1})
#           if not selrestr_fields:
#               print('hi')
#           else:

#               selrestr_list = selrestr_fields['themroles'][0]['selrestrs']['selrestrs_list']
#               selrestr_logic = selrestr_fields['themroles'][0]['selrestrs']['selrestr_logic']
#       return (selrestr_list, selrestr_logic)

#   output_html = ''
#   for arg_index, arg in enumerate(syntax):
#       arg_type = arg['arg_type']
#       value = arg['value']
#       selrestrs = arg['selrestrs']
#       synrestrs = arg['synrestrs']

#       if arg_type == 'NP':
#           arg_popover_id = str(passed_id) + str(arg_index) + 'syntax'

#           selrestrs_html = ''
#           synrestrs_html = ''

#           themrole_entry = db['vn_themroles'].find_one({'name':value})

#           if themrole_entry:
#               themrole_desc = themrole_entry['description']
#               themrole_example = themrole_entry['example']
#           else:
#               themrole_desc = 'no entry found'
#               themrole_example = 'no entry found'

			

#           synrestr_list = synrestrs['synrestr_list']
#           synrestr_logic = synrestrs['synrestr_logic'] 

#           if synrestr_list:
#               synrestrs_html += '<br /><strong style="color:#bf616a;">Syntactic Restrictions:</strong><br />'
#               for synrestr_index, synrestr in enumerate(synrestr_list):
#                   if synrestr_index < len(synrestr_list) - 1:
#                       synrestrs_html += synrestr['value'] + synrestr['type'].upper() + ' ' + synrestr_logic + ' '
#                   else:
#                       synrestrs_html += synrestr['value'] + synrestr['type'].upper()

#           selrestr_fields = get_selrestrs(class_id, value)
#           selrestr_list = selrestr_fields[0]
#           selrestr_logic = selrestr_fields[1]

#           if selrestr_list:
#               selrestrs_html += '<br /><strong style="color:#bf616a;">Selectional Restrictions:</strong><br />'
#               for selrestr_index, selrestr in enumerate(selrestr_list):
#                   if selrestr_index < len(selrestr_list) - 1:
#                       selrestrs_html += selrestr['value'] + selrestr['type'].upper() + ' ' + selrestr_logic + ' '
#                   else:
#                       selrestrs_html += selrestr['value'] + selrestr['type'].upper()

#           themrole_def_html = '<strong>Description:</strong><br />' + themrole_desc + '<br /><strong>Example:</strong><br />' + themrole_example + selrestrs_html + synrestrs_html
#           themrole_popover_body_html = '''<div id={} style='display:none;'><div class='popover-body'>{}</div></div>'''.format(arg_popover_id, themrole_def_html)
#           arg_html = themrole_popover_body_html + '''<span style="color:#5e81ac;" data-toggle="popover" data-popover-content="#{}" data-trigger='hover focus' data-placement='top'>{} </span>'''.format(arg_popover_id, value)


#           output_html += arg_html

#       elif arg_type == 'VERB':
#           output_html += value + ' '

#       elif arg_type == 'PREP':
#           if value:
#               output_html += '{ '
#               for val_index, arg_val in enumerate(value.split(' ')):
#                   if val_index < len(value.split(' ')) - 1:
#                       output_html += arg_val + ' | '
#                   else:
#                       output_html += arg_val + ' } '

#           elif selrestrs['selrestr_list']:

#               output_html += '{ '
#               selrestrs_parsed = [selrestr['value'] + selrestr['type']  for selrestr in selrestrs['selrestr_list']]
#               for selrestr_index, selrestr_val in enumerate(selrestrs_parsed):
#                   if selrestr_index < len(selrestrs_parsed) - 1:
#                       output_html += selrestr_val + ' ' + selrestrs['selrestr_logic'] + ' | '
#                   else:
#                       output_html += selrestr_val + ' } '

#       elif arg_type == 'LEX':
#           output_html += '(' + value.upper() + ') '
#       elif arg_type == 'ADV':
#           output_html += arg_type + ' '
#       elif arg_type == 'ADJ':
#           output_html += arg_type + ' '
#   return output_html