# Jellyfin Server Installation Guide

Complete guide to installing and configuring Jellyfin Media Server — the foundation jellyfin-mcp builds on.

## Table of Contents

1. [Quick Decision Matrix](#quick-decision-matrix)
2. [Windows](#windows)
3. [Docker](#docker)
4. [Linux](#linux)
5. [macOS](#macos)
6. [NAS (Synology / QNAP)](#nas)
7. [First-Time Setup Wizard](#first-time-setup-wizard)
8. [Media Folder Structure](#media-folder-structure)
9. [Hardware Acceleration](#hardware-acceleration)
10. [Remote Access](#remote-access)
11. [Post-Install Checklist](#post-install-checklist)

## Quick Decision Matrix

| Your Setup | Best Install | Notes |
|------------|-------------|-------|
| Windows desktop (daily driver) | Windows installer | Runs as service, auto-starts |
| Dedicated server / NAS | Docker | Easiest to manage, backup config |
| Linux home server | APT repo | Native packages, auto-updates |
| Synology / QNAP NAS | Docker or native package | Docker preferred for plugin support |
| Testing / dev | Docker | Throwaway container, easy reset |
| Tinkerer / builder | Build from source | .NET 10 SDK required |

---

## Windows

### Installer (Recommended)

1. Download from [jellyfin.org/downloads/windows](https://jellyfin.org/downloads/windows)
2. Run `jellyfin_10.11.x_windows-x64.exe`
3. Choose **Install as Service** (default) — Jellyfin starts automatically on boot
4. Complete installation
5. First-time setup at `http://localhost:8096`

### Windows Service Management

```powershell
# Check status
Get-Service jellyfin

# Start / Stop / Restart
Start-Service jellyfin
Stop-Service jellyfin
Restart-Service jellyfin

# Logs location
# C:\ProgramData\Jellyfin\Server\log\
```

### Windows Installer (Silent)

```powershell
jellyfin_10.11.9_windows-x64.exe /S
```

### Windows — Important Notes

- **Firewall**: First launch prompts for firewall access — allow both private and public
- **GPU transcoding**: Install Intel/NVIDIA drivers before Jellyfin for hardware detection
- **Port**: Default 8096 (HTTP) and 8920 (HTTPS). Change in Dashboard → Networking
- **Data path**: `C:\ProgramData\Jellyfin\Server\` (config, plugins, metadata cache)

---

## Docker

### Basic (docker run)

```bash
docker run -d \
  --name jellyfin \
  --restart unless-stopped \
  -p 8096:8096 \
  -p 8920:8920 \
  -v /opt/jellyfin/config:/config \
  -v /opt/jellyfin/cache:/cache \
  -v /mnt/media:/media:ro \
  jellyfin/jellyfin:latest
```

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: "3.8"
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096"
      - "8920:8920"
    volumes:
      - ./config:/config
      - ./cache:/cache
      - /mnt/media/movies:/media/movies:ro
      - /mnt/media/tv:/media/tv:ro
      - /mnt/media/music:/media/music:ro
    environment:
      - JELLYFIN_PublishedServerUrl=http://your-ip:8096
    devices:
      - /dev/dri:/dev/dri  # Intel GPU passthrough
```

```bash
docker compose up -d
```

### Docker with NVIDIA GPU

```yaml
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,video,utility
    # ... rest same as above
```

### Docker Upgrade

```bash
docker compose pull jellyfin
docker compose up -d
```

### Docker — Important Notes

- **Config persistence**: Mount `/config` volume — contains all users, libraries, metadata cache
- **Media read-only**: Mount media volumes with `:ro` to prevent accidental deletion
- **UID/GID**: Add `user: "1000:1000"` to match your filesystem permissions
- **Networking**: Use `network_mode: host` for DLNA/Chromecast discovery

---

## Linux

### Debian / Ubuntu (APT Repository)

```bash
# Add Jellyfin repo
curl -fsSL https://repo.jellyfin.org/install-debuntu.sh | sudo bash

# Or manual:
wget -O- https://repo.jellyfin.org/jellyfin_team.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/jellyfin.gpg
echo "deb [arch=amd64] https://repo.jellyfin.org/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/jellyfin.list
sudo apt update
sudo apt install jellyfin

# Start and enable
sudo systemctl enable jellyfin --now
```

### Fedora / RHEL

```bash
sudo dnf install https://repo.jellyfin.org/releases/server/fedora/versions/stable/server/10.11.9/jellyfin-server-10.11.9-1.fc41.x86_64.rpm
sudo systemctl enable jellyfin --now
```

### Arch (AUR)

```bash
yay -S jellyfin-bin  # pre-built
# or
yay -S jellyfin      # build from source

sudo systemctl enable jellyfin --now
```

### Linux — Post-Install

```bash
# Check status
sudo systemctl status jellyfin

# Logs
sudo journalctl -u jellyfin -f

# Config location
/etc/jellyfin/
/var/lib/jellyfin/

# Add user to video group for GPU access
sudo usermod -aG video jellyfin
sudo usermod -aG render jellyfin
```

---

## macOS

```bash
# Homebrew
brew install --cask jellyfin

# Or download .dmg from jellyfin.org/downloads

# Start
open /Applications/Jellyfin.app

# Runs as menu bar app, port 8096
```

---

## NAS

### Synology

**Docker (recommended):**
```bash
# In Synology Docker UI or SSH:
docker run -d --name jellyfin \
  -p 8096:8096 \
  -v /volume1/docker/jellyfin/config:/config \
  -v /volume1/media:/media:ro \
  --device /dev/dri:/dev/dri \
  jellyfin/jellyfin:latest
```

**Native package:** SynoCommunity provides a Jellyfin package, but Docker is preferred for plugin support and updates.

### QNAP

Use Container Station (Docker UI) or SSH with same docker run command above.

### TrueNAS

Use the Jellyfin app from the TrueCharts catalog, or deploy via Docker on a VM.

---

## First-Time Setup Wizard

When you first open `http://localhost:8096`:

### Step 1: Create Admin User
- Username and password for the admin account
- This account manages the server, creates libraries, manages users

### Step 2: Add Media Libraries
| Type | Recommended Name | Folder Path | Metadata Providers |
|------|-----------------|-------------|-------------------|
| Movies | Movies | `/media/movies` | TMDb, OMDb |
| Shows | TV Shows | `/media/tv` | TMDb, TVDb |
| Music | Music | `/media/music` | MusicBrainz, TheAudioDB |
| Photos | Photos | `/media/photos` | — |
| Home Videos | Home Videos | `/media/home-videos` | — |
| Books | Books | `/media/books` | — |

### Step 3: Metadata Language
- Primary language for metadata fetching
- Country for ratings

### Step 4: Remote Access
- Enable/disable remote connections
- Configure port forwarding if needed

### Step 5: Complete
- Jellyfin starts scanning your libraries
- Dashboard available immediately
- Media appears as scan progresses

---

## Media Folder Structure

Jellyfin uses the same naming conventions as Plex/Emby. Your existing folders likely work without changes.

### Movies

```
/mnt/media/movies/
├── Inception (2010)/
│   └── Inception (2010).mkv
├── The Matrix (1999)/
│   ├── The Matrix (1999) - 1080p.mkv
│   └── The Matrix (1999) - poster.jpg
├── Avatar (2009).mkv            # Single file also works
└── Dune (2021)/
    ├── Dune.2021.2160p.mkv
    └── Dune.2021.2160p.srt      # External subtitle
```

**Rules:**
- `MovieName (YYYY)/MovieName (YYYY).ext` — gold standard
- `MovieName (YYYY).ext` — works for single files
- Year in parentheses is critical for matching
- Subfolders per movie recommended for multi-file releases

### TV Shows

```
/mnt/media/tv/
├── Breaking Bad (2008)/
│   ├── Season 01/
│   │   ├── S01E01 - Pilot.mkv
│   │   ├── S01E02 - Cat's in the Bag.mkv
│   │   └── S01E03 - ...and the Bag's in the River.mkv
│   └── Season 02/
│       └── S02E01.mkv
├── The Office (US) (2005)/
│   └── Season 1/
│       └── The Office S01E01.mkv
└── Anime Series/
    └── Attack on Titan (2013)/
        └── Season 1/
            └── S01E01.mkv
```

**Rules:**
- `ShowName (YYYY)/Season XX/SXXEYY.ext`
- `S01E01`, `S01E02`, `1x01`, `Season 1 Episode 1` all work
- Absolute numbering (E01, E02 without season) works for anime

### Music

```
/mnt/media/music/
├── Artist Name/
│   └── Album Name (YYYY)/
│       ├── 01 - Track Name.flac
│       ├── 02 - Track Name.flac
│       └── cover.jpg
└── Various Artists/
    └── Compilation Name/
        └── 01 - Artist - Track.mp3
```

### Audiobooks / Books

```
/mnt/media/books/
├── Author Name/
│   └── Book Title/
│       ├── Book Title.m4b
│       └── cover.jpg
└── ...
```

### File Permissions (Linux/Docker)

```bash
# Make files readable by Jellyfin
sudo chown -R jellyfin:jellyfin /mnt/media
sudo chmod -R 755 /mnt/media

# Or for Docker with custom UID
sudo chown -R 1000:1000 /mnt/media
```

---

## Hardware Acceleration

Jellyfin supports hardware transcoding on all platforms — **completely free**, unlike Plex.

### Intel Quick Sync (QSV)

**Best for:** Integrated Intel GPUs (almost all Intel CPUs)
```bash
# Linux — enable in Dashboard → Playback → Hardware Acceleration: Intel QuickSync
# Add jellyfin user to render group
sudo usermod -aG render jellyfin

# Docker — add device
--device /dev/dri:/dev/dri
```

### NVIDIA NVENC/NVDEC

**Best for:** Dedicated NVIDIA GPUs (GTX 1050+, RTX series)

Linux:
```bash
# Install NVIDIA drivers + nvidia-container-toolkit
sudo apt install nvidia-driver nvidia-container-toolkit

# Docker — use nvidia runtime
--runtime nvidia
```

### AMD AMF / VAAPI

**Best for:** AMD GPUs on Linux

```bash
# Docker
--device /dev/dri:/dev/dri
# Dashboard → Hardware Acceleration: VAAPI
```

### Apple VideoToolbox

**Best for:** macOS (built-in, no config needed)
Dashboard → Hardware Acceleration → VideoToolbox

### Raspberry Pi

```bash
# Pi 4/5 supports H.264 hardware decoding
# Dashboard → Hardware Acceleration: V4L2
--device /dev/video10:/dev/video10
--device /dev/video11:/dev/video11
```

### Verify Hardware Acceleration

1. Dashboard → Playback → Hardware Acceleration → select your GPU
2. Play a media file that requires transcoding (different codec than client supports)
3. Dashboard → Dashboard → Active Devices → check for "(HW)" indicator
4. Or check ffmpeg logs: `C:\ProgramData\Jellyfin\Server\log\transcode*.log`

---

## Remote Access

### Option 1: Reverse Proxy (Recommended)

**Nginx:**
```nginx
server {
    listen 443 ssl;
    server_name jellyfin.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/jellyfin/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jellyfin/privkey.pem;

    location / {
        proxy_pass http://localhost:8096;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Option 2: Tailscale

```
Install Tailscale on server → access via tailscale IP:8096
No port forwarding needed. Works behind CGNAT.
```

### Option 3: Port Forwarding

```
Router: Forward port 8096 → Jellyfin server IP:8096
Jellyfin Dashboard → Networking → set external domain
Use HTTPS (port 8920) for production — never expose HTTP publicly
```

---

## Post-Install Checklist

- [ ] Admin account created
- [ ] Media libraries added and scanning
- [ ] Metadata downloading (check Dashboard for progress)
- [ ] Hardware acceleration configured and verified
- [ ] API key generated (Dashboard → Users → API Keys)
- [ ] Plugins installed (Intro Skipper, Open Subtitles, etc.)
- [ ] Client apps tested (Android, iOS, TV, web)
- [ ] Remote access configured (if needed)
- [ ] Backup strategy: copy `/config` directory regularly
- [ ] jellyfin-mcp `.env` configured with URL and API key

## Next

Once Jellyfin is running → [Install jellyfin-mcp](INSTALL.md)
