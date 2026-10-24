# Personal apps home

The private app directory at https://personal-apps.tailce5ae8.ts.net/.

Edit `index.html` for the links and design. The owner-only Python server listens on loopback port 8880 behind Tailscale Serve. There are no external assets, browser scripts, databases, or account credentials in this repository.

## Development

Run `python -m unittest discover -q`. For a local server, set TAILSCALE_OWNER and run `python server.py`; Tailscale Serve supplies the authenticated identity header in production.

## Deployment

Every push to `main` runs `.github/workflows/deploy.yml`: GitHub-hosted tests, temporary Tailscale OIDC identity, then a deployment-only SSH request for the exact commit. Pull requests run tests only. Actions can also be run manually on main.

Repository variables: `TS_CLIENT_ID`, `TS_AUDIENCE`, `DEPLOY_KNOWN_HOSTS`. Repository secret: `DEPLOY_SSH_KEY` (a different forced-command key per repo, never the administrator key). Each Tailscale identity trusts only the exact repository's main-branch OIDC subject. The shared tag `tag:github-deploy` can reach only 100.69.243.15 TCP port 22, not other devices or app HTTPS.

The root-owned server manager fetches main from a fixed public repository, verifies the requested SHA is its head, builds as a separate unprivileged user without production credentials, reruns tests, then switches the release symlink. It retains the previous version if build/startup fails. Active jobs delay deployment. Persistent data is outside releases; schema/data changes are not rolled back automatically.

The root-owned SSH wrapper accepts only `deploy <40-character SHA>`. Each key fixes its app; interactive shells, forwarding, arbitrary commands and administrator access are disabled. GitHub never receives app credentials or databases. A trusted main-branch change still runs as the app's service user after deployment, so protect repository write access.

`deploy/automation/auto-deploy.py` is the canonical server manager source. Installing privileged deployment infrastructure is an administrator operation: app pushes cannot replace the root-owned manager or SSH wrappers. The old polling timer is disabled.

Routing:
- `/` -> homepage port 8880
- `/running` -> FiveK owner proxy port 8876 -> app 8765 (Serve strips /running; dashboard generates /running/ URLs)
- `/chess` -> Rookcursion owner bridge 8891 -> app 8890

Services start on boot; public application ports remain blocked. The entire setup runs on the existing Hetzner host.
