#!/usr/bin/python3
"""One-time administrator installation; does not copy app data or credentials."""
import os, pathlib, pwd, shutil, subprocess
D=pathlib.Path('/root/actions-migration')
def run(*args): return subprocess.run(args,check=True,capture_output=True,text=True).stdout
for user,home in [('personal-apps-home','/var/lib/personal-apps-home'),('personal-apps-home-build','/var/lib/personal-apps-deploy/build/personal-apps-home'),('deploy-trigger','/var/lib/deploy-trigger')]:
    try: pwd.getpwnam(user)
    except KeyError: run('useradd','--system','--create-home','--home-dir',home,'--shell','/bin/sh' if user=='deploy-trigger' else '/usr/sbin/nologin',user)
    account=pwd.getpwnam(user)
    pathlib.Path(home).mkdir(parents=True,exist_ok=True)
    os.chown(home,account.pw_uid,account.pw_gid)
    pathlib.Path(home).chmod(0o700)
pathlib.Path('/opt/personal-apps-home/releases').mkdir(parents=True,exist_ok=True)
pathlib.Path('/etc/personal-apps-home').mkdir(exist_ok=True)
# Copy only the owner allowlist setting, never Garmin/calendar credentials.
owner=next(line for line in pathlib.Path('/etc/fivek/app.env').read_text().splitlines() if line.startswith('TAILSCALE_OWNER='))
env=pathlib.Path('/etc/personal-apps-home/app.env');env.write_text(owner+'\n');env.chmod(0o600)
for src,dst in [('auto-deploy.py','/usr/local/sbin/personal-apps-auto-deploy.py'),('actions-trigger.py','/usr/local/sbin/personal-apps-trigger'),('actions-trigger-root.py','/usr/local/sbin/personal-apps-trigger-root')]:
    shutil.copyfile(D/src,dst);pathlib.Path(dst).chmod(0o755)
shutil.copyfile(D/'personal-apps-home.service','/etc/systemd/system/personal-apps-home.service')
keys=pathlib.Path('/etc/ssh/authorized_keys');keys.mkdir(exist_ok=True,mode=0o755)
lines=[]
for app in ('fivek','rookcursion','personal-apps-home'):
    public=(D/(app+'-actions.pub')).read_text().strip()
    lines.append('restrict,command="/usr/local/sbin/personal-apps-trigger '+app+'" '+public)
(keys/'deploy-trigger').write_text('\n'.join(lines)+'\n');(keys/'deploy-trigger').chmod(0o600)
pathlib.Path('/etc/ssh/sshd_config.d/40-deploy-trigger.conf').write_text('''Match User deploy-trigger
    AuthorizedKeysFile /etc/ssh/authorized_keys/%u
    AuthenticationMethods publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    PermitTTY no
    DisableForwarding yes
    PermitUserEnvironment no
Match all
''')
# AuthorizedKeysFile must be readable by sshd after dropping to the account.
(keys/'deploy-trigger').chmod(0o644)
sudo=pathlib.Path('/etc/sudoers.d/personal-apps-deploy');sudo.write_text('deploy-trigger ALL=(root) NOPASSWD: /usr/local/sbin/personal-apps-trigger-root\n');sudo.chmod(0o440)
run('visudo','-cf',str(sudo));run('sshd','-t')
run('systemctl','daemon-reload');run('systemctl','reload','ssh')
print('Isolated homepage service and deployment-only SSH access installed.')
