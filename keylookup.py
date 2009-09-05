# Copyright (C) 2009, Thomas Leonard

import trust_db
import os
from xml.sax.saxutils import XMLGenerator
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

def load(db):
	return set(x.strip() for x in file(db))

debian = load('debian.db')
debian_maint = load('debian-maintainers.db')

class MainPage(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class KeyLookup(webapp.RequestHandler):
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
			report('good', 'This key belongs to a Debian Developer')

		if keyID in debian_maint:
			report('good', 'This key belongs to a Debian Maintainer')

		gen.endElement('key-lookup')
		gen.endDocument()

application = webapp.WSGIApplication([
	('/', MainPage),
	('/key/([0-9A-F]+)', KeyLookup),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
