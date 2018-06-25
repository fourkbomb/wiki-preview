import paramiko
import requests
import threading
from config import *
from queue import Queue
from render import parse
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

msgq = Queue()

def post_comment(project, change, commit, link):
    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    obj = {
            'message': 'Preview: ' + link + ' (will be updated with each new patch set).',
            'notify': 'NONE',
            'tag': 'preview',
    }
    changeid = quote(project, safe='') + '~' + str(change)
    print(changeid, obj)
    url = 'https://' + HOST + '/a/changes/' + changeid + '/revisions/' + commit + '/review'
    print(url)
    res = requests.post(url, json=obj, auth=auth)
    print(res.text)



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
    ret = parse(line, post_comment)
    if ret != 0:
        print('failed to render changeset')
