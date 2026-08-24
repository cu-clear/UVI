import os
from functools import wraps
from datetime import datetime, timezone
from flask import Flask, Response
from flask import render_template,request,flash,redirect,url_for,session
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from methods import top_parent_id, find_matching_ids, find_matching_elements, unique_id, mongo_to_json, formatted_def, get_themrole_fields, full_class_hierarchy_tree, get_pred_fields, get_constant_fields, get_verb_specific_fields, remove_object_ids, colored_pb_example, vn_sanitized_class, get_themrole_fields_undefined, oewn_url
from methods import sort_by_char, sort_by_id

import json
import re
import secrets

from bson import json_util
from bson.objectid import ObjectId, InvalidId
import configparser

configs = configparser.ConfigParser()
configs.read('configs.ini')

ADMIN_USERNAME = configs['ADMIN_SETUP']['ADMIN_USERNAME']
ADMIN_PASSWORD_HASH = configs['ADMIN_SETUP']['ADMIN_PASSWORD_HASH']

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
app.config.update(
	SESSION_COOKIE_SECURE=True,
	SESSION_COOKIE_HTTPONLY=True,
	SESSION_COOKIE_SAMESITE='Lax',
)
mongo = PyMongo(app)
mail = Mail(app)

def login_required(view):
	@wraps(view)
	def wrapped(*args, **kwargs):
		if not session.get('admin_logged_in'):
			return redirect(url_for('admin_login', next=request.path))
		return view(*args, **kwargs)
	return wrapped

def get_csrf_token():
	if 'csrf_token' not in session:
		session['csrf_token'] = secrets.token_hex(32)
	return session['csrf_token']

def csrf_valid():
	token = session.get('csrf_token')
	return bool(token) and secrets.compare_digest(token, request.form.get('csrf_token', ''))

app.jinja_env.globals['get_csrf_token'] = get_csrf_token

def vs_feature_regex(query):
	'''Case-insensitive matcher for verb-specific feature tokens. Matches a stored
	token ("+fast", "Aperture", "property_changed: intensity") when the query equals
	the whole token, the key, or one of the values; an explicit +/- prefix in the
	query is respected, otherwise any polarity matches.'''
	query = query.strip()
	sign = ''
	if query and query[0] in '+-':
		sign, query = query[0], query[1:].strip()
	q = re.escape(query)
	sign_pat = re.escape(sign) if sign else r'[+-]?'
	return re.compile(r'(^' + sign_pat + q + r'$)|(^' + q + r'\s*:)|(:\s*' + sign_pat + q + r'$)', re.IGNORECASE)

def sort_key(predicate):
	## Key will be returned with the assumption that there's only oneword per entry in the list
	return str.lower(list(predicate.keys())[0])

@app.context_processor
def context_methods():
	return dict(top_parent_id=top_parent_id, unique_id=unique_id, mongo_to_json=mongo_to_json, formatted_def=formatted_def, \
		full_class_hierarchy_tree=full_class_hierarchy_tree, get_themrole_fields=get_themrole_fields, get_pred_fields=get_pred_fields, \
		get_constant_fields=get_constant_fields, get_verb_specific_fields=get_verb_specific_fields, remove_object_ids=remove_object_ids, \
		colored_pb_example=colored_pb_example, vn_sanitized_class=vn_sanitized_class, get_themrole_fields_undefined=get_themrole_fields_undefined, \
		oewn_url=oewn_url)

@app.route('/uvi_search')
def uvi_search(common_query_string=None):
	
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
	vs_features_freq = sorted(vs_features,key=lambda x: list(x.values())[0]["count"], reverse=True)
	syn_res = sorted(list(mongo.db.verbnet.references.syn_restrs.find({}, {'_id':0})), key=sort_key)
	sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)
	return render_template('welcome_page.html',
		gen_themroles=gen_themroles, predicates=predicates, vs_features=vs_features, vs_features_freq =  vs_features_freq, syn_res=syn_res, sel_res=sel_res
	)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
	## mail recipients 
	recipients = configs['MAIL_SETUP']['recipients'].split(',')
	if request.method=='POST':
		reply_to = request.form.get('email', '')
		## strip newlines to prevent mail header injection via the subject field
		subject = request.form.get('subject', '').replace('\r', ' ').replace('\n', ' ')
		message = request.form.get('message', '')
		msg = Message(subject=subject,
						sender=app.config.get("MAIL_USERNAME"),
						recipients=recipients,
						reply_to=reply_to,
						body=message)
		try:
			mail.send(msg)
			flash('Your message has been sent. Thank you! 🎉', 'success')
		except Exception:
			app.logger.exception('Contact form mail send failed')
			flash('Sorry, your message could not be sent. Please email us directly instead.', 'danger')
		return redirect(url_for('contact_us'))

	return render_template('contact.html')

SECTION_ORDER = ['Recent Work', 'Background Publications']

def grouped_publications():
	'''Fetch all publications from Mongo, grouped by section (newest year first within
	each section). Known sections come first in SECTION_ORDER; any section an admin
	creates later is appended in the order it's first seen, so new tabs "just work".'''
	pubs = list(mongo.db.publications.find())
	sections = {}
	for pub in pubs:
		sections.setdefault(pub.get('section', 'Publications'), []).append(pub)
	for pub_list in sections.values():
		pub_list.sort(key=lambda p: (-(p.get('year') or 0), p.get('order', 0)))
	ordered_sections = [s for s in SECTION_ORDER if s in sections]
	ordered_sections += [s for s in sections if s not in ordered_sections]
	return [{'name': s, 'slug': re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-'), 'pubs': sections[s]} for s in ordered_sections]

@app.route('/publications', methods=['GET'])
def publications_page():
	return render_template('publications.html', sections=grouped_publications())

def publication_from_form(form):
	authors = [a.strip() for a in form.get('authors', '').splitlines() if a.strip()]
	title = form.get('title', '').strip()
	venue = form.get('venue', '').strip()
	citation = form.get('citation', '').strip() or '{}. {}. {}'.format('; '.join(authors), title, venue)
	year_raw = form.get('year', '').strip()
	return {
		'section': form.get('section', '').strip() or 'Publications',
		'year': int(year_raw) if year_raw.isdigit() else None,
		'authors': authors,
		'title': title,
		'hyperlink': form.get('hyperlink', '').strip(),
		'venue': venue,
		'subject': form.get('subject', '').strip(),
		'description': form.get('description', '').strip(),
		'citation': citation,
	}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
	if request.method == 'POST':
		username = request.form.get('username', '')
		password = request.form.get('password', '')
		if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
			session.clear()
			session['admin_logged_in'] = True
			return redirect(request.args.get('next') or url_for('admin_publications'))
		flash('Invalid username or password.', 'danger')
	return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
	session.clear()
	return redirect(url_for('admin_login'))

@app.route('/admin/publications', methods=['GET'])
@login_required
def admin_publications():
	return render_template('admin_publications.html', sections=grouped_publications())

@app.route('/admin/publications/new', methods=['GET', 'POST'])
@login_required
def admin_publications_new():
	existing_sections = sorted({sec['name'] for sec in grouped_publications()})
	if request.method == 'POST':
		if not csrf_valid():
			flash('Your session expired, please try again.', 'danger')
			return redirect(url_for('admin_publications_new'))
		pub = publication_from_form(request.form)
		pub['order'] = mongo.db.publications.count_documents({'section': pub['section']})
		pub['created_at'] = datetime.now(timezone.utc)
		pub['updated_at'] = pub['created_at']
		mongo.db.publications.insert_one(pub)
		flash('Publication added.', 'success')
		return redirect(url_for('admin_publications'))
	return render_template('admin_publication_form.html', pub=None, existing_sections=existing_sections)

@app.route('/admin/publications/<pub_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_publications_edit(pub_id):
	try:
		object_id = ObjectId(pub_id)
	except InvalidId:
		flash('Publication not found.', 'danger')
		return redirect(url_for('admin_publications'))
	pub = mongo.db.publications.find_one({'_id': object_id})
	if not pub:
		flash('Publication not found.', 'danger')
		return redirect(url_for('admin_publications'))
	existing_sections = sorted({sec['name'] for sec in grouped_publications()})
	if request.method == 'POST':
		if not csrf_valid():
			flash('Your session expired, please try again.', 'danger')
			return redirect(url_for('admin_publications_edit', pub_id=pub_id))
		updated = publication_from_form(request.form)
		updated['order'] = pub.get('order', 0)
		updated['updated_at'] = datetime.now(timezone.utc)
		mongo.db.publications.update_one({'_id': object_id}, {'$set': updated})
		flash('Publication updated.', 'success')
		return redirect(url_for('admin_publications'))
	return render_template('admin_publication_form.html', pub=pub, existing_sections=existing_sections)

@app.route('/admin/publications/<pub_id>/delete', methods=['POST'])
@login_required
def admin_publications_delete(pub_id):
	if not csrf_valid():
		flash('Your session expired, please try again.', 'danger')
		return redirect(url_for('admin_publications'))
	try:
		object_id = ObjectId(pub_id)
	except InvalidId:
		return redirect(url_for('admin_publications'))
	mongo.db.publications.delete_one({'_id': object_id})
	flash('Publication deleted.', 'success')
	return redirect(url_for('admin_publications'))

@app.route('/references_page', methods=['GET'])
def references_page():
	gen_themroles = sorted(list(mongo.db.verbnet.references.gen_themroles.find({}, {'_id':0})), key=sort_key)
	gen_themroles_freq = sorted(gen_themroles,key=lambda x: list(x.values())[0]["count"], reverse=True)
	predicates = sorted(list(mongo.db.verbnet.references.predicates.find({}, {'_id':0})), key=sort_key)
	predicates_freq = sorted(predicates,key=lambda x: list(x.values())[0]["count"], reverse=True)
	vs_features = sorted(list(mongo.db.verbnet.references.vs_features.find({}, {'_id':0})), key=sort_key)
	vs_features_freq = sorted(vs_features,key=lambda x: list(x.values())[0]["count"], reverse=True)
	sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)

	## All Page details are returned by get_ref_page in a dictioanry format
	return render_template('references.html',
		gen_themroles=gen_themroles, gen_themroles_freq = gen_themroles_freq, predicates=predicates, vs_features=vs_features, vs_features_freq = vs_features_freq, predicates_freq = predicates_freq, sel_res=sel_res
	)

@app.route('/_process_query', methods=['GET','POST'])
def process_query(common_query_string = None):
	if request.form.get('lemma_query_string') or common_query_string:
		if(common_query_string):
			print('entered common if loop')
			query_string = common_query_string
			lemmas = [x.lower() for x in query_string.split()]
			logic = "or"
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
			lemmas = [x.lower() for x in query_string.split()]
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
		if query_string.strip() == '':
			return ''

		attribute_type = request.form['vn_attribute']
		if attribute_type == 'themrole':
			themrole = query_string.strip()
			themrole_pattern = re.compile(r'^' + re.escape(themrole) + r'$', re.IGNORECASE)
			sort_behavior = 'alpha'
			matched_ids = {'VerbNet':sorted(set([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.args': {'$elemMatch': {'arg_type':'ThemRole', 'value':themrole_pattern}}})]))}
			return render_template('themrole_search.html', themrole=themrole.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

		elif attribute_type == 'predicate':
			predicate = query_string.strip().lower()
			predicate_pattern = re.compile(r'^' + re.escape(predicate) + r'$', re.IGNORECASE)
			sort_behavior = 'alpha'
			matched_ids = {'VerbNet':sorted(set([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'frames.semantics.predicate':predicate_pattern})]))}
			return render_template('predicate_search.html', predicate=predicate.upper(), matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)

		elif attribute_type == 'vs_feature':
			feature_pattern = vs_feature_regex(query_string)
			matched_ids = {'VerbNet': []}
			matched_features = set()
			for vn_class in mongo.db.verbnet.find({'members.vs_features': feature_pattern}):
				matched_ids['VerbNet'].append(vn_class['class_id'])
				for member in vn_class['members']:
					for feat in member.get('vs_features') or []:
						if feature_pattern.search(feat):
							matched_features.add(feat)
			matched_ids['VerbNet'] = sorted(set(matched_ids['VerbNet']))
			vs_f = ' , '.join(sorted(matched_features, key=str.lower))
			return render_template('vs_feature_search.html', vs_feature=vs_f.upper(), matched_ids=matched_ids, vs_query=query_string)

		elif attribute_type == 'selrestr':
			query_string = query_string.strip().lower()
			if query_string[0] == '+' or query_string[0] == '-' :
				selrestr_type = query_string[1:]
				selrestr_vals = [query_string[0]]
			else:
				selrestr_type = query_string
				selrestr_vals = ['+', '-']
			sort_behavior = 'alpha'
			matched_ids={}
			matched_ids['VerbNet'] = []
			matched_selrestr_vals = []
			for selrestr_val in selrestr_vals:
				c=len(matched_ids['VerbNet'])
				class_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.selrestr_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
				matched_ids['VerbNet'].extend(list(class_level_selrestr_ids))
				frame_level_selrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.frame_level_selrestrs_list': {'$elemMatch': {'value':selrestr_val, 'type':selrestr_type}}})])
				matched_ids['VerbNet'].extend(list(frame_level_selrestr_ids))
				if c!=len(matched_ids['VerbNet']):
					matched_selrestr_vals.append(selrestr_val)
			selrestr_vals = matched_selrestr_vals
			matched_ids['VerbNet'] = list(set(matched_ids['VerbNet']))
			matched_ids['VerbNet'].sort()
			#print('synrestr_vals', selrestr_vals)
			selrestr=''
			for selrestr_val in selrestr_vals:
				selrestr += selrestr_val.upper()+selrestr_type.upper()+' , ' 
			return render_template('selrestr_search.html', selrestr = selrestr[:-3], matched_ids=matched_ids, sort_behavior=sort_behavior, level=None)

		elif attribute_type == 'synrestr':
			query_string = query_string.strip().lower()
			if query_string[0] == '+' or query_string[0] == '-' :
				synrestr_type = query_string[1:]
				synrestr_vals = [query_string[0]]
			else:
				synrestr_type = query_string
				synrestr_vals = ['+', '-']
			matched_ids={}
			matched_ids['VerbNet'] = []
			sort_behavior = 'alpha'
			matched_synrestr_vals = []
			for synrestr_val in synrestr_vals:
				c=len(matched_ids['VerbNet'])
				class_level_synrestr_ids = set([doc['class_id'] for doc in mongo.db.vn_themrole_fields.find({'themrole_fields.synrestr_list': {'$elemMatch': {'value':synrestr_val, 'type':synrestr_type}}})])
				matched_ids['VerbNet'].extend(list(class_level_synrestr_ids))
				if c!=len(matched_ids['VerbNet']):
					matched_synrestr_vals.append(synrestr_val)
			synrestr_vals = matched_synrestr_vals
			matched_ids['VerbNet'] = list(set(matched_ids['VerbNet']))
			matched_ids['VerbNet'].sort()
			#print('synrestr_vals', synrestr_vals)
			synrestr=''
			for synrestr_val in synrestr_vals:
				synrestr += synrestr_val.upper()+synrestr_type.upper()+' , ' 
			return render_template('synrestr_search.html', synrestr = synrestr[:-3], matched_ids=matched_ids, sort_behavior=sort_behavior)

	elif request.args.get('lemma_query_string'):
		print('entered get if loop')
		query_string = request.args.get('lemma_query_string')
		lemmas = [x.lower() for x in query_string.split()]
		logic = "or"
		sort_behavior = "alpha"
		incl_vn = True
		incl_fn = True
		incl_pb = True
		incl_wn = True
		matched_ids = find_matching_ids(lemmas, incl_vn, incl_fn, incl_pb, incl_wn, logic, sort_behavior)
		print('done get if loop')
		return render_template('results.html', matched_ids=matched_ids, query_string=query_string, sort_behavior=sort_behavior)
	
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
		feature_pattern = vs_feature_regex(vs_feature)
		matched_ids = {'VerbNet':sorted(set([vn_class['class_id'] for vn_class in mongo.db.verbnet.find({'members.vs_features': feature_pattern})]))}
		return render_template('vs_feature_search.html', vs_feature=vs_feature.upper(), matched_ids=matched_ids, vs_query=vs_feature)


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
		matched_ids = {'VerbNet':sorted(list(class_level_synrestr_ids))}
		return render_template('synrestr_search.html', synrestr = synrestr_val.upper()+synrestr_type.upper(), matched_ids=matched_ids, sort_behavior=sort_behavior)
	
	return ''


#POST request: <form id='vn_filtered_elements'> in "results.html"
@app.route('/_display_element', methods=['GET','POST'])
def display_element():
	if request.form.get('resource_key') == 'VerbNet' or request.args.get('class_id'):
		vn_class_id =  request.args.get('class_id') if request.args.get('class_id') else request.form['vn_class_id']
		matched_elements1 = list(mongo.db.verbnet.find({'class_id': vn_class_id}))
		all_classes={}
		vs_feature_filter = vs_feature_regex(request.form['vs_feature']) if request.form.get('vs_feature') else None
		for element in matched_elements1:
			filtered_members = []
			for member in element['members']:
				if vs_feature_filter and any(vs_feature_filter.search(feat) for feat in member.get('vs_features') or []):
					filtered_members.append(member)
				member_name = member['name']
				class_ids = mongo.db.verbnet.find(
						{'members.name': member_name},
						{'class_id': 1, '_id': 0}
					)
				all_classes[member_name] = sorted([doc['class_id'] for doc in class_ids])
			if request.form.get('vs_feature'):
				element['members'] = filtered_members
		return render_template('render_verbnet_top.html', vn_elements = matched_elements1, first_level = True,member_classes=all_classes)

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
	matched_elements = list(mongo.db.verbnet.find({'class_id':vn_class_id}))
	all_classes={}
	for element in matched_elements:
		for member in element['members']:
			member_name = member['name']
			class_ids = mongo.db.verbnet.find(
                {'members.name': member_name},
                {'class_id': 1, '_id': 0}
            )
			all_classes[member_name] = sorted([doc['class_id'] for doc in class_ids])
	return render_template('render_verbnet_top.html', vn_elements=matched_elements, first_level=True,member_classes=all_classes)

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
		query_string = request.form.get('common_query_string')
		gen_themroles = sorted(list(mongo.db.verbnet.references.gen_themroles.find({}, {'_id':0})), key=sort_key)
		predicates = sorted(list(mongo.db.verbnet.references.predicates.find({}, {'_id':0})), key=sort_key)
		vs_features = sorted(list(mongo.db.verbnet.references.vs_features.find({}, {'_id':0})), key=sort_key)
		syn_res = sorted(list(mongo.db.verbnet.references.syn_restrs.find({}, {'_id':0})), key=sort_key)
		sel_res = sorted(list(mongo.db.verbnet.references.sel_restrs.find({}, {'_id':0})), key=sort_key)
		return render_template('uvi_search.html',
			gen_themroles=gen_themroles, predicates=predicates, vs_features=vs_features, syn_res=syn_res, sel_res=sel_res,query_string = query_string
		)
	else:
		return uvi_search()