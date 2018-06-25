import json
import os
import subprocess
import sys
import time

from config import *
PROJECTS = PROJECTS.split(' ')

def debug(*args,**kwargs):
    if DEBUG:
        print(*args, **kwargs)

def fetch_render_change(change, commit, ref, log=subprocess.DEVNULL):
    if '/' in commit:
        print("%s isn't a valid commit hash"%commit)
        return False
    os.chdir(PATH)
    proc = subprocess.run(['sh', '../do.sh', change, commit, ref, WEBROOT_WEB_BASE + change, WEBROOT_PATH + '/' + change], stdout=log, stderr=log)
    if proc.returncode != 0:
        debug("render failed!")

    os.chdir('..')
    return True


def parse(line, postfn):
    obj = json.loads(line)
    ps = obj['patchSet']
    change = obj['change']
    if ps['kind'] != 'REWORK' or change['project'] not in PROJECTS:
        print('not matching project')
        return 1
    print(DEBUG)
    if DEBUG:
        log = open(change['id'] + '.log', 'w')
    else:
        log = subprocess.DEVNULL
    cid = str(change['number'])
    ret = fetch_render_change(cid, ps['revision'], ps['ref'], log=log)
    if DEBUG:
        log.close()
    if ret:
        link = WEBROOT_WEB_URL + WEBROOT_WEB_BASE + cid
        if ps['number'] == 1:
            print('post link')
            postfn(change['project'], change['number'], ps['revision'], link)
        print('rendered at', link)
        return 0
    else:
        print("failed")
        return 1

if __name__ == '__main__':
    try:
        fake = {
                'patchSet': {
                    'revision': 'ef8a7c486de273ced4bd50937949dd8791db846c',
                    'ref': 'refs/changes/29/203329/4',
                    'kind': 'REWORK'
                },
                'change': {
                    'id': '1',
                    'project': 'LineageOS/lineage_wiki'
                },
        }
        ret = parse(json.dumps(fake))
    except Exception:
        sys.exit(1)
