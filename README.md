# GD-Thief
Red Team tool for exfiltrating files from a target's Google Drive that you have access to, via Google's API.
## Dependencies
Google API Libraries: `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
## Usage:
```
usage:

gd_thief.py [-h] -m [{dlAll,} (default = dlAll)


help:

This Module will connect to Google's API using an access token and exfiltrate files
from a target's Google Drive

arguments:
	-m [{dlAll}],
		--mode [{dlAll}]
		The mode of file download
		Can be "dlAll", or... (default: dlAll)

optional arguments:

	-h, --help
		show this help message and exit
```
