# OpenClaw in Docker

Dieses Repository enthaelt ein eigenstaendiges Node-26-Image fuer den
OpenClaw-Gateway. OpenClaw wird beim Image-Build entsprechend der offiziellen
npm-Installation global installiert. Docker Compose uebernimmt den Lifecycle;
der OpenClaw-State liegt in einem persistenten Volume.

## Voraussetzungen

- Docker Desktop oder Docker Engine
- Docker Compose v2
- mindestens 6 GB RAM fuer einen lokalen Image-Build

OpenClaw benoetigt aktuell Node 24.16+ oder Node 26.1+. Das Dockerfile nutzt
Node 26.

## Lokaler Start

1. Konfiguration anlegen:

   ```bash
   cp .env.example .env
   ```

2. In `.env` einen sicheren `OPENCLAW_GATEWAY_TOKEN` setzen und mindestens
   einen Provider konfigurieren. Einen Token kann man zum Beispiel so erzeugen:

   ```bash
   openssl rand -hex 32
   ```

3. Image bauen:

   ```bash
   docker compose build --pull
   ```

4. Einmaliges interaktives Onboarding im persistenten Volume ausfuehren:

   ```bash
   docker compose run --rm --no-deps openclaw onboard --mode local --no-install-daemon
   ```

   Eine native Service-Installation wird im Container nicht benoetigt. Bei der
   Authentifizierungsabfrage Token-Authentifizierung verwenden.

5. Gateway starten:

   ```bash
   docker compose up -d
   docker compose ps
   ```

Die Control UI ist standardmaessig unter
`http://127.0.0.1:18789/` erreichbar. Den Gateway-Token aus `.env` in der UI
eintragen. Bei einer abweichenden `OPENCLAW_HOST_PORT` diese Portnummer in der
URL verwenden.

## Betrieb

```bash
# Logs
docker compose logs -f openclaw

# Gateway-Gesundheit und Diagnose
docker compose exec openclaw openclaw health
docker compose exec openclaw openclaw doctor
docker compose exec openclaw openclaw security audit

# Token aus dem laufenden Container anzeigen (nicht in Logs weiterleiten)
docker compose exec openclaw openclaw gateway auth-token --show
```

`docker compose down` stoppt den Stack und behaelt das Volume. Mit
`docker compose down -v` werden auch OpenClaw-Konfiguration, Credentials und
Sessions geloescht.

## Versionen und Updates

`OPENCLAW_VERSION` ist standardmaessig `latest`. Fuer reproduzierbare Builds
eine konkrete OpenClaw-Version in `.env` pinnen, dann neu bauen und starten:

```bash
docker compose build --pull
docker compose up -d
```

## GitHub Container Registry

Die Workflow-Datei
`.github/workflows/docker.yml` baut das Dockerfile bei Pull Requests und
veroeffentlicht Images fuer `main` sowie `v*`-Tags in der GitHub Container
Registry (`ghcr.io`). Das Image nutzt nur `GITHUB_TOKEN`; Provider-Keys und
Gateway-Tokens werden nicht in CI benoetigt.

Auf einem spaeteren Docker-Host:

1. `.env` aus `.env.example` erzeugen und ein eigenes
   `OPENCLAW_GATEWAY_TOKEN` setzen.
2. `OPENCLAW_IMAGE` auf das veroeffentlichte Image setzen, zum Beispiel
   `ghcr.io/OWNER/REPOSITORY:latest`. Bei einem privaten Package vorher bei
   `ghcr.io` anmelden.
3. Image laden und Stack starten:

   ```bash
   docker compose pull
   docker compose up -d
   ```

Bei oeffentlicher Erreichbarkeit `OPENCLAW_BIND_ADDRESS=0.0.0.0` nur zusammen
mit Firewall-Regeln oder einem TLS-Reverse-Proxy verwenden. Die Token-
Authentifizierung bleibt aktiviert.

## Provider und Channels

Provider- und Channel-Variablen koennen in `.env` ergaenzt werden. Die Datei
ist absichtlich von Git ausgeschlossen. Channel-spezifische Einrichtung erfolgt
nach dem Start mit OpenClaw, zum Beispiel:

```bash
docker compose run --rm --no-deps openclaw channels add \
  --channel telegram --token "TOKEN"
```

Weitere Konfiguration kann ueber die Control UI oder die OpenClaw-Dokumentation
erfolgen: <https://docs.openclaw.ai/install>.
