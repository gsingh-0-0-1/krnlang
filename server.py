from flask import Flask, render_template
import krn_parser
import json
import sys

try:
	if sys.argv[1] == "logfile":
		sys.stdout = sys.stderr = open('log.txt','wt')
except IndexError:
	pass

app = Flask(__name__)

# get the root defs object
f = open('langdata/main.json') 
ROOT_DEFS = json.load(f)
f.close()

f = open('langdata/hardset.json')
HARDSET = json.load(f)
f.close()

# get the english definitions
ENGLISH_TO_ROOT = {}
for root in ROOT_DEFS:
	ENGLISH_TO_ROOT[ROOT_DEFS[root]['rel']] = root
for hardset in HARDSET:
	ENGLISH_TO_ROOT[HARDSET[hardset]['rel']] = hardset

def generate_results(head):
	# yield head
	for child in head.children:
		yield child
		for grandchild in generate_results(child):
			yield grandchild

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/search')
def search():
	return render_template('search.html')

@app.route('/dict')
def dict():
	return render_template('dict.html')

@app.route('/examples')
def examples():
	return render_template('examples.html')

@app.route('/phonology')
def phonology():
	return render_template('phonology.html')

@app.route('/grammar')
def grammar():
	return render_template('grammar.html')

@app.route('/pronouns')
def pronouns():
	return ",".join(krn_parser.PRONOUNS)

@app.route('/verb_table/<path:inf>')
def verb_table(inf):
	return krn_parser.verb_table(inf)

@app.route('/allroots')
def allroots():
	return json.dumps(ROOT_DEFS)

@app.route('/word/<path:word>')
def wordpage(word):
	rule_object = krn_parser.parse(word)

	if not rule_object:
		return render_template('404.html')
	else:
		return render_template('word.html')

@app.route('/rootdef/<path:root>')
def definition(root):
	# we treat hardsets like roots as well
	if root in HARDSET:
		item = HARDSET[root]
		return '{"definition" : "relating to %s", "derivation" : "%s"}' % (item['rel'], item['der'])
	elif root in ROOT_DEFS:
		item = ROOT_DEFS[root]
		return '{"definition" : "relating to (literal, expansive) %s", "derivation" : "%s"}' % (item['rel'], item['der'])
	else:
		return 'null'

@app.route('/desc/<path:word>')
def desc(word):
	rule_object = krn_parser.parse(word)
	return rule_object.name

@app.route('/query/<path:query_item>')
def query(query_item):
	print("QUERY <%s>" % query_item)
	rule_objects = [krn_parser.parse(query_item)]
	query_items = [query_item]

	non_krn = False

	if not rule_objects[0]:
		non_krn = True

	if rule_objects[0] and query_item[:3] not in ROOT_DEFS:
		non_krn = False

	if non_krn:
		rule_objects = []
		query_items = []

	#if non_krn: # treat this as an english word
	if query_item in ENGLISH_TO_ROOT.keys():
		rule_objects.append(krn_parser.parse(ENGLISH_TO_ROOT[query_item]))
		query_items.append(ENGLISH_TO_ROOT[query_item])
	else:
		for engword in ENGLISH_TO_ROOT:
			if query_item in engword:
				print(query_item, engword)
				rule_objects.append(krn_parser.parse(ENGLISH_TO_ROOT[engword]))
				query_items.append(ENGLISH_TO_ROOT[engword])

	response_template = '{"word" : "%s", "type" : "%s", "definition" : "%s"}'
	rows = []

	#if not non_krn:
	#	rows.append(response_template % (query_item, rule_objects[0].name, ""))
	#else:
	#	pass
		#if len(query_items) != 0:
		#	rows.append(response_template % (query_items[0], rule_objects[0].name, ""))

	for rule_object, query_item in zip(rule_objects, query_items):
		objects = [el for el in generate_results(rule_object)]

		#if not non_krn:
		#	objects = objects[1:]

		#if len(objects) == 0:
		rows.append(response_template % (query_item, rule_object.name, ""))

		for o in objects:
			new_word = query_item + o.rule.replace(rule_object.rule, '')
			rows.append(response_template % (new_word, o.name, ""))

	return "\n".join(rows)

@app.route('/<path:url>')
def error(url):
	return render_template('404.html')

app.run(host = '0.0.0.0', port = 80, debug = True)