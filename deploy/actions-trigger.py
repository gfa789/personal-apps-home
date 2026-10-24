#!/usr/bin/python3
"""An SSH key can only request its fixed app and an exact main-branch revision."""
import os
import re
import subprocess
import sys

APPS={'fivek','rookcursion','personal-apps-home'}
def request(app, command):
    match=re.fullmatch(r'deploy ([a-f0-9]{40})',command)
    if app not in APPS or not match:
        raise ValueError('Only an exact deployment request is allowed')
    return match.group(1)

def main():
    if len(sys.argv)!=2:
        sys.exit(2)
    app=sys.argv[1]
    try:
        sha=request(app,os.environ.get('SSH_ORIGINAL_COMMAND',''))
    except ValueError as error:
        print(error,file=sys.stderr)
        sys.exit(2)
    sys.exit(subprocess.run(['sudo','-n','/usr/local/sbin/personal-apps-trigger-root',app,sha]).returncode)

if __name__=='__main__':
    main()
