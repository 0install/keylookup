# Copyright (C) 2013, Thomas Leonard

import webapp2
import urllib

from google.appengine.api import urlfetch

with open('0mirror-update.cap', 'r') as stream:
	mirror_update_cap = stream.read().strip()

class Cron(webapp2.RequestHandler):
	def get(self):
		self.response.write("updating...")
		form_data = urllib.urlencode({})
		result = urlfetch.fetch(url=mirror_update_cap,
					payload=form_data,
					method=urlfetch.POST,
					headers={'Content-Type': 'application/x-www-form-urlencoded'})
		if result.status_code == 200:
			self.response.write("done")
		else:
			raise Exception("error updating 0mirror: %s" % result)

app = webapp2.WSGIApplication([
	('/cron/0mirror', Cron),
	],
	debug=True)
