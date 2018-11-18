import os

from flask import Flask, Response
from flask import render_template, redirect, url_for, request, jsonify, g
from flask_pymongo import PyMongo

from methods import top_parent_id, find_matching_ids, find_matching_elements, unique_id, mongo_to_json, formatted_def, get_themrole_fields, full_class_hierarchy_tree, get_pred_fields, get_constant_fields, get_verb_specific_fields, remove_object_ids, colored_pb_example, vn_sanitized_class, get_themrole_fields_undefined

import json

from flask_mail import Mail, Message

mail_settings = {
	"MAIL_SERVER": "smtp.gmail.com",
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	# Set environment variables for more security
	"MAIL_USERNAME": 'testing.uvi@gmail.com', #os.environ.get('MAIL_USERNAME')
	"MAIL_PASSWORD": 'asdf#3456' #os.environ.get('MAIL_PASSWORD')
}

app = Flask(__name__)

#generate SECRET_KEY randomly on startup
app.config['SECRET_KEY'] = os.urandom(16)
app.config['MONGO_DBNAME'] = 'uvi_corpora'

mongo = PyMongo(app)


@app.context_processor
def context_methods():
	return dict(top_parent_id=top_parent_id, unique_id=unique_id, mongo_to_json=mongo_to_json, formatted_def=formatted_def, full_class_hierarchy_tree=full_class_hierarchy_tree, get_themrole_fields=get_themrole_fields, get_pred_fields=get_pred_fields, get_constant_fields=get_constant_fields, get_verb_specific_fields=get_verb_specific_fields, remove_object_ids=remove_object_ids, colored_pb_example=colored_pb_example, vn_sanitized_class=vn_sanitized_class, get_themrole_fields_undefined=get_themrole_fields_undefined)

@app.route('/download_json')
def download_json():
    returned_json = json.dumps(request.args.get('elements'))
    generator = (cell for row in returned_json for cell in row)
    return Response(generator, mimetype='application/json', headers={'Content-Disposition':'attachment;filename=uvi_export.json'})

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('search.html')

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
	if request.method=='POST':
		print("goes in")
		reply_to_name = request.form.get('name')
		reply_to=request.form.get('email')
		subject = request.form.get('subject')
		message = request.form.get('message')
		msg = Message(subject=subject, 
						sender=app.config.get("MAIL_USERNAME"), 
						recipients=["testing.uvi@gmail.com"],
						body=message)
		msg.add_recipient(reply_to)
		mail.send(msg)

	return render_template('contact.html')

@app.route('/references_page', methods=['GET'])
def references_page():
	return render_template('references.html')

@app.route('/_process_query', methods=['GET','POST'])
def process_query():
	if request.form.get('lemma_query_string'):
		print(request.form.get('lemma_query_string')+'POOOOOPPP!!')
		query_string = request.form['lemma_query_string']

		lemmas = query_string.split(' ')

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
			return 'Poopity Scoop'

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

@app.route('/verbnet/<vn_class_id>')
def render_vn_class(vn_class_id):
	matched_elements = mongo.db.verbnet.find({'class_id':vn_class_id})
	return render_template('render_verbnet_top.html', vn_elements=matched_elements, first_level=True)

@app.route('/welcome_frame')
def welcome_frame():
	return render_template('welcome_frame.html')