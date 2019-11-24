# Copyright (C) 2009, Thomas Leonard

import logging
import trust_db
from xml.sax.saxutils import XMLGenerator
from google.appengine.api import urlfetch

import webapp2

def load(db):
	return set(x.strip() for x in file(db))

debian = load('debian.db')
debian_maint = load('debian-maintainers.db')

class KeyLookup(webapp2.RequestHandler):
	def get(self, keyID):
		self.response.headers['Content-Type'] = 'application/xml'
		url = 'https://keylookup.0install.net/key/' + keyID
		try:
			result = urlfetch.fetch(url)
			if result.status_code == 200:
				self.response.write(result.content)
				return
			logging.warning('Error from 0install.net (%d): %s' % (result.status_code, result.content))
		except urlfetch.Error:
			logging.exception('Caught exception fetching url')

		# Fall back to built-in database

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
