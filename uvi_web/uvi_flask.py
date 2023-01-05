import os
from flask import Flask, Response
from flask import render_template, redirect, url_for, request, jsonify, g
from flask_pymongo import PyMongo

from methods import top_parent_id, find_matching_ids, find_matching_elements, unique_id, mongo_to_json, formatted_def, get_themrole_fields, full_class_hierarchy_tree, get_pred_fields, get_constant_fields, get_verb_specific_fields, remove_object_ids, colored_pb_example, vn_sanitized_class, get_themrole_fields_undefined
from methods import sort_by_char, sort_by_id

import json

from bson import json_util

from flask_mail import Mail, Message
import configparser

configs = configparser.ConfigParser()
configs.read('configs.ini')

mail_settings = {
	"MAIL_SERVER": "smtp.gmail.com",
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	# Set environment variables for more security
	"MAIL_USERNAME": configs['MAIL_SETUP']['MAIL_USERNAME'],
	"MAIL_PASSWORD": configs['MAIL_SETUP']['MAIL_PASSWORD']
}
app = Flask(__name__)

#generate SECRET_KEY randomly on startup
app.config['SECRET_KEY'] = os.urandom(16)
app.config['MONGO_DBNAME'] = 'new_corpora'
app.config["MONGO_URI"] = "mongodb://localhost:27017/" + app.config['MONGO_DBNAME']
app.config.update(mail_settings)
mongo = PyMongo(app)
mail = Mail(app)

def sort_key(predicate):
	## Key will be returned with the assumption that there's only oneword per entry in the list
	return str.lower(list(predicate.keys())[0])

@app.context_processor
def context_methods():
	return dict(top_parent_id=top_parent_id, unique_id=unique_id, mongo_to_json=mongo_to_json, formatted_def=formatted_def, \
		full_class_hierarchy_tree=full_class_hierarchy_tree, get_themrole_fields=get_themrole_fields, get_pred_fields=get_pred_fields, \
		get_constant_fields=get_constant_fields, get_verb_specific_fields=get_verb_specific_fields, remove_object_ids=remove_object_ids, \
		colored_pb_example=colored_pb_example, vn_sanitized_class=vn_sanitized_class, get_themrole_fields_undefined=get_themrole_fields_undefined)

@app.route('/uvi_search')
def uvi_search():
	process_query()
	
	gen_themroles = sorted(list(mongo.db.verbnet.references.gen_themroles.find({}, {'_id':0})), key=sort_key)
	predicates = sorted(list(mongo.db.verbnet.references.predicates.find({}, {'_id':0})), key=sort_key)
	vs_features = sorted(list(mongo.db.verbnet.references.vs_features.find({}, {'_id':0})), key=sort_key)
	syn_res = sorted(list(mongo.db.verbnet.references.syn_restrs.find({}, {'_id':0})), key=sort_key)
	sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)
	
	return render_template('uvi_search.html',
		gen_themroles=gen_themroles, predicates=predicates, vs_features=vs_features, syn_res=syn_res, sel_res=sel_res
	)

@app.route('/download_json', methods=['GET', 'POST'])
def download_json():
	form_keys = list(request.form.keys())
	if not form_keys:
		return render_template('applications.html')
	resources = {}
	if 'down_vn' in form_keys:
		resources['VerbNet'] = list(mongo.db.verbnet.find({}, {'_id':0}))
	if 'down_fn' in form_keys:
		resources['FrameNet'] = list(mongo.db.framenet.find({}, {'_id':0}))
	if 'down_pb' in form_keys:
		resources['PropBank'] = list(mongo.db.propbank.find({}, {'_id':0}))
	if 'down_on' in form_keys:
		resources['OntoNotes'] = list(mongo.db.ontonotes.find({}, {'_id':0}))
	returned_json = json_util.dumps(resources, indent=4)
	return Response(returned_json, mimetype='application/json', headers={'Content-Disposition':'attachment;filename=uvi_export.json'})

@app.route('/', methods=['GET','POST'])
def index():
	gen_themroles = sorted(list(mongo.db.verbnet.references.gen_themroles.find({}, {'_id':0})), key=sort_key)
	predicates = sorted(list(mongo.db.verbnet.references.predicates.find({}, {'_id':0})), key=sort_key)
	vs_features = sorted(list(mongo.db.verbnet.references.vs_features.find({}, {'_id':0})), key=sort_key)
	syn_res = sorted(list(mongo.db.verbnet.references.syn_restrs.find({}, {'_id':0})), key=sort_key)
	sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)
	
	return render_template('welcome_page.html',
		gen_themroles=gen_themroles, predicates=predicates, vs_features=vs_features, syn_res=syn_res, sel_res=sel_res
	)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
	## mail recipients 
	recipients = configs['MAIL_SETUP']['recipients'].split(',')
	if request.method=='POST':
		## unused variable "reply_to_name"
		#reply_to_name = request.form.get('name')
		reply_to=request.form.get('email')
		subject = request.form.get('subject')
		message = request.form.get('message')
		msg = Message(subject=subject, 
						sender=app.config.get("MAIL_USERNAME"), 
						recipients=recipients,
						body=message)
		msg.add_recipient(reply_to)
		mail.send(msg)

	return render_template('contact.html')

@app.route('/references_page', methods=['GET'])
def references_page():
	gen_themroles = sorted(list(mongo.db.verbnet.references.gen_themroles.find({}, {'_id':0})), key=sort_key)
	predicates = sorted(list(mongo.db.verbnet.references.predicates.find({}, {'_id':0})), key=sort_key)
	vs_features = sorted(list(mongo.db.verbnet.references.vs_features.find({}, {'_id':0})), key=sort_key)
	syn_res = sorted(list(mongo.db.verbnet.references.syn_restrs.find({}, {'_id':0})), key=sort_key)
	sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)
	
	## All Page details are returned by get_ref_page in a dictioanry format
	return render_template('references.html',
		gen_themroles=gen_themroles, predicates=predicates, vs_features=vs_features, syn_res=syn_res, sel_res=sel_res
	)

@app.route('/_process_query', methods=['GET','POST'])
def process_query(common_query_string = None):
	if request.form.get('lemma_query_string') or common_query_string:
		if(common_query_string):
			print('entered common if loop')
			query_string = common_query_string
			lemmas = [x.lower() for x in query_string.split(' ')]
			logic = "and"
			sort_behavior = "alpha"
			incl_vn = True
			incl_fn = True
			incl_pb = True
			incl_wn = True
			matched_ids = find_matching_ids(lemmas, incl_vn, incl_fn, incl_pb, incl_wn, logic, sort_behavior)
			print('done common if loop')
			return render_template('results.html', matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

		else:
			print('entered common if loop')
			query_string = request.form['lemma_query_string']
			# print(request.form.get('lemma_query_string')+' POOOOOPPP!!')
			lemmas = [x.lower() for x in query_string.split(' ')]
			logic = request.form['logic']
			sort_behavior = request.form['sort_behavior']
			form_keys = list(request.form.keys())
			incl_vn = True if 'incl_vn' in form_keys else False
			incl_fn = True if 'incl_fn' in form_keys else False
			incl_pb = True if 'incl_pb' in form_keys else False
			incl_wn = True if 'incl_wn' in form_keys else False
			matched_ids = find_matching_ids(lemmas, incl_vn, incl_fn, incl_pb, incl_wn, logic, sort_behavior)
			return render_template('results.html', matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

	elif request.form.get('vn_attribute'):
		query_string = request.form['attribute_query_string']
		#if query string is empty, return all possible instances of this attribute
		#e.g. all predicates, themroles, etc.
		if query_string == '':
			return ''

		attribute_type = request.form['vn_attribute']
		if attribute_type == 'themrole':
			themrole = query_string[0].upper() + query_string[1:].lower()
			sort_behavior = 'alpha'
			matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.args': {'arg_type':'ThemRole', 'value':themrole}})])}
			return render_template('themrole_search.html', themrole=themrole.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

		elif attribute_type == 'predicate':
			predicate = query_string.lower()
			sort_behavior = 'alpha'
			matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.predicate':predicate})])}
			return render_template('predicate_search.html', predicate=predicate.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

		elif attribute_type == 'vs_feature':
			vs_feature = query_string
			matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'members.vs_features': vs_feature})])}
			return render_template('vs_feature_search.html', vs_feature=vs_feature.upper(), matched_ids=matched_ids)

		elif attribute_type == 'selrestr':
			selrestr_type = query_string[1:]
			selrestr_val = query_string[0]
			sort_behavior = 'alpha'
			class_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.selrestr_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
			matched_ids = {'VerbNet':sorted(list(class_level_selrestr_ids))}
			frame_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.frame_level_selrestrs_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
			matched_ids['VerbNet'].extend(sorted(list(frame_level_selrestr_ids)))
			return render_template('selrestr_search.html', selrestr = selrestr_val.upper()+selrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior, level=None)

		elif attribute_type == 'synrestr':
			synrestr_type = query_string[1:]
			synrestr_val = query_string[0]
			sort_behavior = 'alpha'
			class_level_synrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.synrestr_list': {'$elemMatch': {'value':synrestr_val, 'type':synrestr_type}}})])
			frame_level_synrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.frame_level_synrestrs_list': {'$elemMatch': {'value':synrestr_val, 'type':synrestr_type}}})])
			matched_ids = {'VerbNet':sorted(list(class_level_synrestr_ids.union(frame_level_synrestr_ids)))}
			return render_template('synrestr_search.html', synrestr = synrestr_val.upper()+synrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior)

	elif request.args.get('themrole'):
		themrole = request.args.get('themrole')
		query_string = ''
		sort_behavior = 'alpha'
		matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.args': {'arg_type':'ThemRole', 'value':themrole}})])}
		return render_template('themrole_search.html', themrole=themrole.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

	elif request.args.get('pred'):
		predicate = request.args.get('pred')
		query_string = ''
		sort_behavior = 'alpha'
		matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.predicate':predicate})])}
		return render_template('predicate_search.html', predicate=predicate.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)


	elif request.args.get('const'):
		const = request.args.get('const')
		query_string = ''
		sort_behavior = 'alpha'
		matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.args': {'arg_type':'Constant', 'value':const}})])}
		return render_template('constant_search.html', const=const.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)


	elif request.args.get('verb_specific_arg'):
		vs_arg = request.args.get('verb_specific_arg')
		query_string = ''
		sort_behavior = 'alpha'
		matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.args': {'arg_type':'VerbSpecific', 'value':vs_arg}})])}
		return render_template('vs_arg_search.html', vs_arg=vs_arg.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

	elif request.args.get('verb_specific_feature'):
		vs_feature = request.args.get('verb_specific_feature')
		matched_ids = {'VerbNet':sorted([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'members.vs_features': vs_feature})])}
		return render_template('vs_feature_search.html', vs_feature=vs_feature.upper(), matched_ids=matched_ids)


	elif request.args.get('selrestr'):
		selrestr_type = request.args.get('selrestr')
		selrestr_val = request.args.get('selrestr_val')
		level = request.args.get('level')
		sort_behavior = 'alpha'
		if level == 'class':
			class_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.selrestr_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
			matched_ids = {'VerbNet':sorted(list(class_level_selrestr_ids))}
			return render_template('selrestr_search.html', selrestr = selrestr_val.upper()+selrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior, level=level)

		elif level == 'frame':
			frame_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.frame_level_selrestrs_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
			matched_ids = {'VerbNet':sorted(list(frame_level_selrestr_ids))}
			return render_template('selrestr_search.html', selrestr = selrestr_val.upper()+selrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior, level=level)


	elif request.args.get('synrestr'):
		synrestr_type = request.args.get('synrestr')
		synrestr_val = request.args.get('synrestr_val')
		sort_behavior = 'alpha'
		class_level_synrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.synrestr_list': {'$elemMatch': {'value':synrestr_val, 'type':synrestr_type}}})])
		frame_level_synrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.frame_level_synrestrs_list': {'$elemMatch': {'value':synrestr_val, 'type':synrestr_type}}})])
		matched_ids = {'VerbNet':sorted(list(class_level_synrestr_ids.union(frame_level_synrestr_ids)))}
		return render_template('synrestr_search.html', synrestr = synrestr_val.upper()+synrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior)
	return ''


#POST request: <form id='vn_filtered_elements'> in "results.html"
@app.route('/_display_element', methods=['GET','POST'])
def display_element():
	if request.form.get('resource_key') == 'VerbNet':
		vn_class_id = request.form['vn_class_id']
		matched_elements = mongo.db.verbnet.find({'class_id': vn_class_id})
		return render_template('render_verbnet_top.html', vn_elements = matched_elements, first_level = True)

	elif request.form.get('resource_key') == 'FrameNet':
		fn_name = request.form['fn_name']
		matched_element = mongo.db.framenet.find_one({'name': fn_name})
		return render_template('render_framenet.html', frame_json = matched_element)

	elif request.form.get('resource_key') == 'PropBank':
		pb_lemma = request.form['pb_lemma']
		matched_element = mongo.db.propbank.find_one({'predicates.lemma': pb_lemma})
		return render_template('render_propbank.html', frame_json = matched_element)

	elif request.form.get('resource_key') == 'OntoNotes':
		on_lemma = request.form['on_lemma']
		matched_element = mongo.db.ontonotes.find_one({'lemma': on_lemma})
		return render_template('render_ontonotes.html', frame_json = matched_element)

@app.route('/verbnet/<vn_class_id>')
def render_vn_class(vn_class_id):
	matched_elements = mongo.db.verbnet.find({'class_id':vn_class_id})
	return render_template('render_verbnet_top.html', vn_elements=matched_elements, first_level=True)

@app.route('/welcome_frame')
def welcome_frame():
	return render_template('welcome_frame.html')


@app.route('/class_hierarchy')
def class_hierarchy():
	return render_template('class_hierarchy.html', class_by_num=sort_by_id(), class_by_name=sort_by_char())

@app.route('/nlp_applications')
def applications():
	return render_template('applications.html')

@app.route('/uvi_search_anywhere', methods=['GET','POST'])
def uvi_search_anywhere():
	if request.form.get('common_query_string'):
		uvi_search()
		query_string = request.form.get('common_query_string')
		lemmas = [x.lower() for x in query_string.split(' ')]
		logic = "and"
		sort_behavior = "alpha"
		incl_vn = True
		incl_fn = True
		incl_pb = True
		incl_wn = True
		matched_ids = find_matching_ids(lemmas, incl_vn, incl_fn, incl_pb, incl_wn, logic, sort_behavior)

	return render_template('results.html', matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)
