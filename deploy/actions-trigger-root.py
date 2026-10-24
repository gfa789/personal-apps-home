#!/usr/bin/python3
"""Run a deployment in a restricted transient systemd service; never a shell."""
import re
import subprocess
import sys
import time

def main():
    if len(sys.argv)!=3 or sys.argv[1] not in {'fivek','rookcursion','personal-apps-home'} or not re.fullmatch('[a-f0-9]{40}',sys.argv[2]):
        sys.exit(2)
    app,sha=sys.argv[1:]
    command=['systemd-run','--quiet','--wait','--pipe','--collect',
      '--unit=personal-apps-action-'+app+'-'+str(time.time_ns()),
      '--property=Type=oneshot','--property=TimeoutStartSec=20min',
      '--property=UMask=0022','--property=NoNewPrivileges=true',
      '--property=PrivateTmp=true','--property=ProtectHome=true','--property=ProtectSystem=strict',
      '--property=ReadWritePaths=/opt/rookcursion /opt/fivek /opt/personal-apps-home /var/lib/rookcursion /var/lib/fivek /var/lib/personal-apps-deploy /var/backups/personal-apps',
      '--property=MemoryMax=2G','--property=CPUQuota=100%',
      '/usr/bin/python3','/usr/local/sbin/personal-apps-auto-deploy.py',app,'--sha',sha,'--wait']
    sys.exit(subprocess.run(command).returncode)

if __name__=='__main__':
    main()
