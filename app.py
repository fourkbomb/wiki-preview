import paramiko
import requests
import threading
from config import *
from queue import Queue
from render import parse
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

msgq = Queue()

def post_comment(project, change, commit, link, verified=0):
    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    message = ''
    if verified == 1:
        message = 'Passes validator. Preview: {}'.format(link)
    elif verified == -1:
        message = 'Fails validator. Error log: {}'.format(link)
    obj = {
            'message': message,
            'notify': 'NONE',
            'tag': 'preview',
            'labels': {
                'Verified': verified,
            },
    }
    changeid = quote(project, safe='') + '~' + str(change)
    url = 'https://' + HOST + '/a/changes/' + changeid + '/revisions/' + commit + '/review'
    res = requests.post(url, json=obj, auth=auth)

class Streamer(threading.Thread):
    def run(self):
        while True:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(HOST, port=PORT, username=USER, key_filename=KEY)
                client.get_transport().set_keepalive(60)
                _, stdout, _ = client.exec_command('gerrit stream-events -s patchset-created')
                print('Connected to gerrit.')
                for line in stdout:
                    msgq.put(line)
            except Exception as e:
                print(e)
            finally:
                client.close()

stream = Streamer()
stream.daemon = True
stream.start()

while True:
    line = msgq.get()
    parse(line, post_comment)
