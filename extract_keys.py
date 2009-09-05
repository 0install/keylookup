#!/usr/bin/env python
from __future__ import with_statement
import subprocess

def scan_keyring(path, out):
	child = subprocess.Popen(['gpg', '--fixed-list-mode', '--with-colons', '--list-keys', '--fingerprint',
				  '--no-default-keyring', '--keyring', path], stdout = subprocess.PIPE)
	for line in child.stdout:
		if line.startswith('fpr:'):
			print >>out, line.split(':')[9]
	if child.wait():
		print "Failed to read keyring %s" % path

with file('debian.db', 'w') as out:
	scan_keyring('/usr/share/keyrings/debian-keyring.gpg', out)
with file('debian-maintainers.db', 'w') as out:
	scan_keyring('/usr/share/keyrings/debian-maintainers.gpg', out)
