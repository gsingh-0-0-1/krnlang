import re
import exrex
import json

# Let's define some basics
PRONOUNS = [
	'na', # 1st person sing., from Arabic 'ana'
	'to', # 2nd person sing., from Hindi/Punjabi/Persian/Spanish/... 'tu'/'to'
	'wo', # 3rd person sing., from Hindi 'vo'/'voh'/'vah'
	'ns', # 1st person plur., from Spanish 'nosotros'
	'vs', # 2nd person plur., from Spanish 'vosotros'
	'nh'  # 3rd person plur., from Persian 'anha'
]

PREPOSITIONS = [
	'b', # with, from Arabic 'بِ'
]

MODALS = {
	'past' : 'kn', # past particle, from Arabic 'كان'
	'perf' : 'pa',
	'cont' : 'kr', # continuous particle, from Hindi 'करना'
	'fut'  : 'ft', # future particle, from English 'future'
	'imp'  : 'i'
}

f = open('langdata/verb_template.json')
VERB_TEMPLATE = json.load(f)
f.close()

def verb_table(inf):
	table = '<tbody><th colspan=3>Conjugation of {inf}</th>'
	for mood in VERB_TEMPLATE.keys():
		ntenses = len(list(VERB_TEMPLATE[mood].keys()))
		table = table + "<tr><th rowspan=%d>%s</th>" % (ntenses, mood)
		for tense in VERB_TEMPLATE[mood].keys():
			table = table + "<td>%s</td>" % tense
			#for pron in PRONOUNS:
			table = table + "<td>%s</td>" % VERB_TEMPLATE[mood][tense]
			table = table + "</tr>"

	table = table + "</tbody>"

	table = table.format(past = MODALS['past'], 
		perf = MODALS['perf'],
		cont = MODALS['cont'],
		fut = MODALS['fut'],
		imp = MODALS['imp'],
		inf = inf)

	return table


ROOT_TYPES = {
	'a' : [
		'literal root', 
		'',
	],
	'e' : [
		'expansive root', 
		'',
	],
}

DERIV_TYPES = {
	'c' : [
		'noun',
		'',
	],
	'm' : [
		'modifier', 
		'',
	],
	'v' : [
		'infinitive',
		''
	],
}

DERIV_SUBTYPES = {
	'c' : [
		['g', 'agentive noun', 'eg: klma ~ word, klmacg ~ writer'],
		['p', 'perfective noun', 'eg: klma ~ word, klmacp ~ word (redundant w/ root)'],
		['k', 'gerund', 'eg: klma ~ word, klmack ~ talking'],
		['l', 'locative noun', 'eg: znda ~ live, zndacl ~ home']
	],
	'm' : [
		['p', 'passive participle', 'eg: klma ~ word, klmamp ~ spoken (adj)'],
		['k', 'active participle', 'eg: klma ~ word, klmamk ~ speaking (adj)'],
	],

}

RULES = []

class Rule:
	def __init__(self, name, rule, children, parent = None):
		self.name = name
		self.rule = rule
		self.children = children
		self.parent = parent

		if parent is not None:
			parent.add_child(self)
			self.rule = self.parent.rule + self.rule

	def add_child(self, child):
		self.children.append(child)
		child.parent = self

def create_rule(name, rule, parent = None):
	return Rule(name, rule, [], parent)

	if level not in RULES:
		RULES[level] = {}

	if parent is None:
		RULES[level][name] = rule
	else:
		if parent not in RULES[level - 1]:
			raise Exception("Nonexistent parent rule < %s >!" % parent)

		RULES[level][name] = RULES[level - 1][parent] + rule

HEAD = create_rule('root', '[a-z][a-z][a-z]')

for rt in ROOT_TYPES:
	label_rt = ROOT_TYPES[rt][0]
	this_root_rule = create_rule(label_rt, rt, HEAD)

	for dt in DERIV_TYPES:
		label_dt = DERIV_TYPES[dt][0]
		this_deriv_rule = create_rule(label_dt + " of " + label_rt, dt, this_root_rule)

		if dt not in DERIV_SUBTYPES:
			continue

		for st_list in DERIV_SUBTYPES[dt]:
			st = st_list[0]
			label_st = st_list[1]

			create_rule(label_st + " of " + label_rt, st, this_deriv_rule)

def check_match(word, rule):
	rule_regex = rule.rule
	pattern = re.compile(rule_regex + "$")
	match = bool(pattern.match(word))

	if match:
		return rule
	else:
		if rule.children == []:
			return None
		else:
			for child in rule.children:
				result = check_match(word, child)
				if result:
					return result

def parse(word):

	match = check_match(word, HEAD)

	return match

