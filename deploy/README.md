# Deploying Taskman

Target: Ubuntu VPS on DigitalOcean, served over HTTPS via nginx + gunicorn + systemd.

## Prerequisites

- A DigitalOcean Ubuntu 22.04 droplet (1 GB RAM is sufficient)
- A domain pointed at the droplet's IP (A record)
- SSH access as `ubuntu` (or adjust `User=` in `taskman.service`)

---

## 1. Server setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx git
```

---

## 2. Clone and build

```bash
cd ~
git clone <your-repo-url> taskman
cd taskman

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cd client
npm install
npm run build
cd ..
```

---

## 3. Environment variables

Create `~/taskman/.env`:

```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
TASKMAN_BASE_URL=https://your-domain.com
```

`TASKMAN_BASE_URL` drives the OAuth redirect URI and post-login redirect. It must match the authorised redirect URI registered in Google Cloud Console.

Restrict access to the file:

```bash
chmod 600 ~/taskman/.env
```

---

## 4. Systemd service

```bash
sudo cp ~/taskman/deploy/taskman.service /etc/systemd/system/taskman.service
# Edit User= and WorkingDirectory= if your username is not "ubuntu"
sudo systemctl daemon-reload
sudo systemctl enable taskman
sudo systemctl start taskman
sudo systemctl status taskman
```

Gunicorn binds to `127.0.0.1:8000`. Logs: `journalctl -u taskman -f`.

---

## 5. Nginx

```bash
sudo cp ~/taskman/deploy/taskman.nginx /etc/nginx/sites-available/taskman
# Replace "your-domain.com" with your actual domain
sudo sed -i 's/your-domain.com/yourdomain.com/g' /etc/nginx/sites-available/taskman
sudo ln -s /etc/nginx/sites-available/taskman /etc/nginx/sites-enabled/taskman
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. HTTPS (Let's Encrypt)

Run certbot once to obtain a certificate and patch the nginx config automatically:

```bash
sudo certbot --nginx -d your-domain.com
```

Certbot installs a renewal cron job automatically. Test renewal with:

```bash
sudo certbot renew --dry-run
```

---

## 7. Google OAuth production setup

In [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials → your OAuth client:

- **Authorised JavaScript origins**: `https://your-domain.com`
- **Authorised redirect URIs**: `https://your-domain.com/api/oauth/callback`

If the domain ever changes, update both entries and set `TASKMAN_BASE_URL` in `.env` to match.

---

## 8. Data persistence

All user data lives in `~/.taskman/` on the VPS:

```
~/.taskman/
  config.json          shared server config (secretKey)
  sessions/            server-side session files
  users/
    you@gmail.com/
      db.json          your tasks, lists, groups, daysheet
      config.json      your calendar/timezone config
```

**Deploys do not touch `~/.taskman/`** — git pull and service restart are safe.

Before destructive operations (disk wipe, droplet rebuild), back up:

```bash
tar -czf taskman-data-$(date +%Y%m%d).tar.gz ~/.taskman/
```

---

## 9. Moving data to another machine

Because `TASKMAN_DIR` is overridable via environment variable, you can point any instance at a different directory:

```bash
TASKMAN_DIR=/path/to/backup/.taskman flask --app server run -p 5050
```

To move data from the VPS back to your local machine:

```bash
scp -r ubuntu@your-vps:~/.taskman/ ~/.taskman/
```

The JSON schema is identical across environments — no migration needed.

---

## Updating

```bash
sudo systemctl stop taskman
cd /home/ubuntu/taskman
git pull
.venv/bin/pip install -r requirements.txt
cd client
npm install
npm run build
cd ..
sudo systemctl start taskman
```
