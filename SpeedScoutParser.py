#!/usr/local/bin/python

from __future__ import print_function
import httplib2
import os
import base64

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-speedscout.json
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets',
          'https://mail.google.com/']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SpeedScoutParser'
CONFIG_FILE = './config'
SCRIPT_ID = None
USER_ID = 'me'
CACHE_DIR = './cache'
NEW_DATA = os.path.join(CACHE_DIR,'matchData.csv')
HEADER = ["Team #","A. Color","Match #","Crossed BLine","Low Boiler",
          "High Boiler","Gear","Low Boiler","High Boiler","Gears","Climbed AShip","Comments"]


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'python-speedscout.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def combineMatchData(matchDataFiles,combinedDataFile):
    if not os.path.exists(combinedDataFile):
        with open(combinedDataFile,'w') as outFile:
            for header in HEADER:
                outFile.write(header+',')
    with open(combinedDataFile,'a') as outFile:
        for dataFile in matchDataFiles:
            outFile.write('\n')
            with open(os.path.join(CACHE_DIR,dataFile),'r') as f:
                for line in f:
                    kvPairs = line.split(',')
                    kvPairs = [x.strip() for x in kvPairs]
                    if kvPairs[0] in HEADER:
                        outFile.write(kvPairs[1]+',')


def main():
    global SCRIPT_ID

    with open(CONFIG_FILE,'r') as configFile:
        for line in configFile:
            kvPairs = line.split(':')
            kvPairs = [x.strip() for x in kvPairs]
            if kvPairs[0] == "ScriptID":
                SCRIPT_ID = kvPairs[1]

    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    gmailService = discovery.build('gmail', 'v1', http=http)
    scriptService = discovery.build('script', 'v1', http=http)

    response = gmailService.users().messages().list(userId=USER_ID,q='').execute()
    
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = gmailService.users().messages().list(userId=USER_ID, q='',
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
    for message in messages:
        msg_id=message['id']
        haveAttachments = False

        curMessage = gmailService.users().messages().get(userId=USER_ID, id=msg_id).execute()
        for part in curMessage['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data=part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=gmailService.users().messages().attachments().get(userId=USER_ID, messageId=msg_id,id=att_id).execute()
                    data=att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = CACHE_DIR+'/'+part['filename']

                with open(path, 'w') as f:
                    f.write(file_data)
                haveAttachments = True

        # Only delete messages with attachments
        if haveAttachments:
            gmailService.users().messages().trash(userId=USER_ID, id=msg_id).execute()

    matchData = [f for f in os.listdir(CACHE_DIR) if os.path.isfile(os.path.join(CACHE_DIR,f)) and (f not in NEW_DATA)]
    combineMatchData(matchData,NEW_DATA)
    for datum in matchData:
        os.remove(os.path.join(CACHE_DIR,datum))

    publishError = False
    with open(NEW_DATA,'r') as f:
        for line in f:
            request = {"function": "addDataRow"}
            request["parameters"] = [[]]
            rowData = line.split(',')
            rowData = [x.strip() for x in rowData]
            if rowData[0] not in HEADER:
                for datum in rowData:
                    if len(datum) > 0:
                        request["parameters"][0].append(datum)
            else:
                continue
            response = scriptService.scripts().run(body=request, scriptId=SCRIPT_ID).execute()
            if 'error' in response:
                publishError = True
                error = response['error']['details'][0]
                print("Script error message: {0}".format(error['errorMessage']))

                if 'scriptStackTraceElements' in error:
                    # There may not be a stacktrace if the script didn't start
                    # executing.
                    print("Script error stacktrace:")
                    for trace in error['scriptStackTraceElements']:
                        print("\t{0}: {1}".format(trace['function'],
                            trace['lineNumber']))

    if not publishError:
        os.remove(NEW_DATA)


if __name__ == '__main__':
    main()
