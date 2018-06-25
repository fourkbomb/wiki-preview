import json
import os
import subprocess
import sys
import time

from config import *
PROJECTS = PROJECTS.split(' ')

FAIL = 0
OK = 1
VALIDATOR_FAIL = 2
try:
    os.mkdir('logs')
except FileExistsError:
    pass

def debug(*args,**kwargs):
    if DEBUG:
        print(*args, **kwargs)

def fetch_render_change(change, commit, ref, log=subprocess.DEVNULL):
    if '/' in commit:
        print("%s isn't a valid commit hash"%commit)
        return FAIL
    os.chdir(PATH)
    ret = OK
    proc = subprocess.run(['sh', '../do.sh', change, commit, ref, WEBROOT_WEB_BASE + change, WEBROOT_PATH + '/' + change], stdout=log, stderr=log)
    if proc.returncode == 4:
        debug("validator failed!")
        ret = VALIDATOR_FAIL
    elif proc.returncode != 0:
        debug("render failed!")
        ret = FAIL

    os.chdir('..')
    return ret


def parse(line, postfn):
    obj = json.loads(line)
    ps = obj['patchSet']
    change = obj['change']
    if ps['kind'] == 'NO_CHANGE' or ps['kind'] == 'NO_CODE_CHANGE' or change['project'] not in PROJECTS:
        print('not matching project')
        return 1
    if DEBUG:
        log = open('logs/' + change['id'] + '.log', 'w')
    else:
        log = subprocess.DEVNULL
    cid = str(change['number'])
    ret = fetch_render_change(cid, ps['revision'], ps['ref'], log=log)
    if DEBUG:
        log.close()
    if ret == OK:
        link = WEBROOT_WEB_URL + WEBROOT_WEB_BASE + cid
        postfn(change['project'], change['number'], ps['revision'], link, 1)
        print('rendered at', link)
        return 0
    elif ret == VALIDATOR_FAIL:
        link = WEBROOT_WEB_URL + WEBROOT_WEB_BASE + cid + '.log'
        postfn(change['project'], change['number'], ps['revision'], link, -1)
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
