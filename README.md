# GD-Thief
Red Team tool for exfiltrating files from a target's Google Drive that you(the attacker) has access to, via the Google Drive API.
This includes includes all shared files, all files from shared drives, and all files from domain drives that the target
has access to.
## HOW TO
### Create a new Google Cloud Platform (GCP) project
Steps to get the Google API Access Token needed for connecting to the API
1.  Create a burner Gmail/google account
2.  Login to said account
3.  Navigate to the Google [Cloud Console](https://console.cloud.google.com/)
4.  Next to "Google Cloud Platform," click the `Down arrow`. A dialog listing current projects appears.
5.  Click `New Project`. The New Project screen appears.
6.  In the `Project Name field`, enter a descriptive name for your project.
7.  (Optional) To edit the `Project ID`, click `Edit`. The project ID can't be
  changed after the project is created, so choose an ID that meets your needs for
  the lifetime of the project.
8.  Click `Create`. The console navigates to the Dashboard page and your project is created within a few minutes.
### Enable a Google Workspace API
1.  Next to "Google Cloud Platform," click the `Down arrow` and select the project
  you just created from the dropdown list.
2.  In the top-left corner, click `Menu` > `APIs & Services`.
3.  Click `Enable APIs and Services`. The "Welcome to API Library" page appears.
4.  In the `search field`, enter "Google Drive".
5.  Click the API to enable. The API page appears.
6.  Click `Enable`. The Overview page appears.
###  Configure OAuth Consent screen
1.  On the left side of the Overview page click `Credentials`. The credential
page for your project appears.
2.  Click `Configure Consent Screen`. The "OAuth consent screen" screen appears.
3.  Click the `External` user type for your app.
4.  Click `Create`. A second "OAuth consent screen" screen appears.
5.  Fill out the form:
    - Enter an Application Name in the `App name` field
    - Enter your burner email address in the `User support email` field.
    - Enter your burner email address in the `Developer contact information` field.
6.  Click `Save and Continue`. The "Scopes" page appears.
7.  Click `Add or Remove Scopes`. The "Update selected scopes" page appears.
8.  Check all of the `Google Drive` the scopes to use in the app.
9.  Click `Update`. A list of scopes for your app appears.
10. Click `Save and Continue`. The "Edit app registration" page appears.
11. Click `Save and Continue`. The "OAuth consent screen" appears.
### Create a credential
1.  Click `Create Credentials` and select `OAuth client ID`. The "Create OAuth
  client ID" page appears.
2.  Click the Application type drop-down list and select `Desktop Application`.
3.  In the `name` field, type a name for the credential. This name is only shown
  in the Cloud Console.
4.  Click `Create`. The OAuth client created screen appears. This screen shows
  the `Client ID` and `Client secret`.
5.  Click `OK`. The newly created credential appears under "OAuth 2.0 Client IDs."
6.  Click the `download` button to the right of the newly-created OAuth 2.0
  Client ID. This copies a client secret JSON file to your desktop. Note the
  location of this file.
7.  Rename the client secret JSON file to "credentials.json" and move it to the
  `gd_thief/credentials` directory.
### Add the victim's Google account to the Application's Test Users
In order to be able to run this script against the victim, you will need to add
their Google account to the Test Users list for the App you just created
1.  On the Left side of the screen click `OAuth consent screen`.  You "OAuth
  Consent Screen" page appears.
2.  Under `Test Users` click the `Add Users` button.
3.  Enter the victim's Gmail address in the `email address` field.
4.  Click the `save` button.
### First Time running gd_thief
Upon gaining access to a Target's Google account, you can run gd_thief
1.  The first time running gd_thief, the script opens a new window prompting you
to authorize access to your data:
    1.  If you are not already signed in to your Google account, you are
      prompted to sign in. If you are signed in to multiple Google accounts, you
      are asked to select one account to use for the authorization.  Make sure
      you select the victim's Google account


## Dependencies
Google API Libraries: `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
## Usage:
```
usage:
gd_thief.py [-h] -m [{dlAll, dlDict[-d <DICTIONARY FILE PATH>]}
	[-t <THREAD COUNT>]

help:

This Module will connect to Google's API using an access token and exfiltrate files
from a target's Google Drive

arguments:
        -m [{dlAll, dlDict}],
                --mode [{dlAll, dlDict}]
                The mode of file download
                Can be "dlAll", "dlDict [-d <DICTIONARY FILE PATH>]", or... (More options to come)

optional arguments:
        -d <DICTIONARY FILE PATH>, --dict <DICTIONARY FILE PATH>
                        Path to the dictionary file. Mandatory with download mode"-m, --mode dlDict"
                        You can use the provided dictionary, per example: "-d ./dictionaries/secrets-keywords.txt"
        -t <THREAD COUNT>, --threads <THREAD COUNT>
                        Number of threads. (Too many could exceeed Google's rate limit threshold)

        -h, --help
                show this help message and exit
```
## NOTES:
-  Setting the thread count too high will cause an HTTP 403 "Rate limit exceeded," indicating that the 
user has reached Google Drive API's maximum request rate.
	-  The thread count limit vaires from machine to machine.  I've set it to 250 on a Macbook Pro, while 
	250 was too high for my Windows 10 Desktop
## REFERENCES:
-  The secrets-keywords dictionary file was taken from SecLists' [secrets-keywords.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Variables/secret-keywords.txt)
## TODO:
1.  ~Threading~
2.  ~Error Checking~
3.  ~Wordlist file content search and download~
4.  File type download
5.  Snort Sensitive Data regex file content search and download
6.  ~Optical Character Recognition (OCR)~
## Special Thanks:
Thank you to my good friend [Cedric Owens](https://github.com/cedowens) for helping me with the threading piece!
