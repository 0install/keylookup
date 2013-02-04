# Copyright (C) 2009, Thomas Leonard

import trust_db
from xml.sax.saxutils import XMLGenerator

import webapp2

def load(db):
	return set(x.strip() for x in file(db))

debian = load('debian.db')
debian_maint = load('debian-maintainers.db')

class KeyLookup(webapp2.RequestHandler):
	def get(self, keyID):
		self.response.headers['Content-Type'] = 'application/xml'
		gen = XMLGenerator(self.response.out, 'utf-8')
		gen.startDocument()
		gen.startElement('key-lookup', {})

		def report(vote, text):
			gen.startElement('item', {'vote': vote})
			gen.characters(text)
			gen.endElement('item')

		hint = trust_db.hints.get(keyID, None)
		if hint:
			report('good', hint)

		if keyID in debian:
			report('good', 'This key belongs to a Debian Developer.')

		if keyID in debian_maint:
			report('good', 'This key belongs to a Debian Maintainer.')

		gen.endElement('key-lookup')
		gen.endDocument()

app = webapp2.WSGIApplication([
	('/key/([0-9A-F]+)', KeyLookup),
	],
	debug=True)
