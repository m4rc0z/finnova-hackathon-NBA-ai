# OpenClaw in Docker

Dieses Repository enthaelt ein eigenstaendiges Node-26-Image fuer den
OpenClaw-Gateway. Als Modell ist der OpenAI-kompatible Swisscom-Endpoint fuer
Apertus 1.5 70B vorkonfiguriert. Docker Compose uebernimmt den Lifecycle; der
OpenClaw-State liegt in einem persistenten Volume.

## Voraussetzungen

- Docker Desktop oder Docker Engine
- Docker Compose v2
- mindestens 6 GB RAM fuer einen lokalen Image-Build
- ein freigeschalteter Swisscom API-Key fuer Apertus

OpenClaw benoetigt aktuell Node 24.16+ oder Node 26.1+. Das Dockerfile nutzt
Node 26.

Die Docker-Dateien liegen im Unterordner `openclaw/`. Vor allen folgenden
Docker-Compose-Befehlen in ein Terminal wechseln:

```bash
cd openclaw
```

Die Befehle unten gehen davon aus, dass dieses Arbeitsverzeichnis aktiv bleibt.
`COMPOSE_PROJECT_NAME` bestimmt den Namen des persistenten Docker-Volumes; bei
einer bestehenden Installation den bisherigen Projektnamen beibehalten.

## Swisscom-Konfiguration

Das mitgelieferte `openclaw.json`-Template registriert:

- Provider: `swisscom`
- Base URL: `https://api.swisscom.com/products/swiss-ai-weeks/apertus-1.5-70b/v1`
- API: `openai-completions`
- Modell-ID: `swiss-ai/Apertus-v1.5-70B`
- Authentifizierung: `Authorization: Bearer <SWISSCOM_API_KEY>`

Die API-Key-Datei `.env` bleibt lokal und ist von Git ausgeschlossen. Der
`OPENCLAW_GATEWAY_TOKEN` ist davon getrennt: Er schuetzt die lokale Control UI
und ist nicht der Swisscom API-Key.

## Lokaler Start

1. Lokale Konfiguration anlegen:

   ```bash
   cp .env.example .env
   ```

2. In `.env` mindestens diese Werte ersetzen:

   ```dotenv
   OPENCLAW_GATEWAY_TOKEN=<zufaelliger-langer-gateway-token>
   SWISSCOM_API_KEY=<dein-swisscom-api-key>
   ```

   Einen Gateway-Token kann man zum Beispiel so erzeugen:

   ```bash
   openssl rand -hex 32
   ```

   `SWISSCOM_BASE_URL` und `SWISSCOM_MODEL` sind bereits passend vorbelegt.
   Falls Swisscom dir einen anderen Model-Identifier nennt, nur
   `SWISSCOM_MODEL` aendern.

3. Image bauen und Gateway starten:

   ```bash
   docker compose up -d --build
   docker compose ps
   ```

   Beim ersten Start kopiert der Container das versionierte `openclaw.json`-
   Template in das persistente Volume. Eine native Service-Installation oder
   separates Onboarding ist fuer diesen Docker-Stack nicht notwendig.

4. Control UI oeffnen:

   <http://127.0.0.1:18789/>

   In der UI den Wert von `OPENCLAW_GATEWAY_TOKEN` aus `.env` eintragen. Bei
   einem anderen `OPENCLAW_HOST_PORT` diese Portnummer in der URL verwenden.

5. Konfiguration und Gateway pruefen:

   ```bash
   docker compose exec openclaw openclaw config validate
   docker compose exec openclaw openclaw models list
   docker compose exec openclaw openclaw health
   ```

   `models list` sollte `swisscom/swiss-ai/Apertus-v1.5-70B` enthalten. Eine echte
   Provider-Anfrage pruefst du am einfachsten mit einer Nachricht in der
   Control UI.

## Bestehenden State aktualisieren

Wenn der Stack bereits mit dem vorherigen Template gestartet wurde, existiert
im Volume schon eine `openclaw.json`; sie wird absichtlich nicht automatisch
ueberschrieben. Vorhandene Chats und Konfigurationen bleiben dadurch erhalten.

Wenn dort noch keine wichtigen Daten liegen, kannst du die neue Swisscom-
Konfiguration so uebernehmen:

```bash
docker compose down
docker compose run --rm --no-deps -e OPENCLAW_FORCE_TEMPLATE=1 openclaw config validate
docker compose up -d
```

Der erste Befehl mit `OPENCLAW_FORCE_TEMPLATE=1` ersetzt nur die OpenClaw-
Konfigurationsdatei im Volume, nicht das Volume selbst. Bei wichtigen
bestehenden Anpassungen vorher eine Sicherung erstellen.

## Betrieb und Diagnose

```bash
# Logs

docker compose logs -f openclaw

# Gateway-Gesundheit und Diagnose

docker compose exec openclaw openclaw health
docker compose exec openclaw openclaw doctor
docker compose exec openclaw openclaw security audit

# Aktive Model-Auswahl anzeigen

docker compose exec openclaw openclaw config get agents.defaults.model.primary
```

`docker compose down` stoppt den Stack und behaelt das Volume. Mit
`docker compose down -v` werden auch OpenClaw-Konfiguration, Credentials und
Sessions geloescht.

## Troubleshooting

- **401 `INVALID_ACCESS_TOKEN`:** Swisscom API-Key, Freischaltung und
  `SWISSCOM_BASE_URL` pruefen. Der Stack verwendet den API-Key als Bearer-Token.
- **UI meldet unauthorized:** Nicht den Swisscom-Key, sondern
  `OPENCLAW_GATEWAY_TOKEN` aus `.env` verwenden.
- **Modell antwortet, aber Tools schlagen fehl:** Pruefen, ob der Swisscom-
  Endpoint Tool-/Function-Calling fuer Apertus freischaltet. Das Modell ist
  als text-only konfiguriert; Bild-Input ist nicht aktiviert.
- **Container startet nicht:** `docker compose logs openclaw` und danach
  `docker compose exec openclaw openclaw doctor` ausfuehren.

## Versionen und Updates

`OPENCLAW_VERSION` ist in `openclaw/.env.example` auf `2026.9.4` gepinnt. Fuer ein
kontrolliertes Update die Version aendern, anschliessend neu bauen und starten:

```bash
docker compose build --pull
docker compose up -d
```

## GitHub Container Registry

Die Workflow-Datei `.github/workflows/docker.yml` baut das Dockerfile bei Pull
Requests und veroeffentlicht Images fuer `main` sowie `v*`-Tags in der GitHub
Container Registry (`ghcr.io`). Das Image enthaelt keine Provider-Keys oder
Gateway-Tokens; diese werden erst auf dem jeweiligen Docker-Host ueber `.env`
eingesetzt.

Auf einem spaeteren Docker-Host:

1. `.env` aus `.env.example` erzeugen.
2. `OPENCLAW_GATEWAY_TOKEN` und `SWISSCOM_API_KEY` setzen.
3. `OPENCLAW_IMAGE` auf das veroeffentlichte Image setzen, zum Beispiel
   `ghcr.io/OWNER/REPOSITORY:latest`. Bei einem privaten Package vorher bei
   `ghcr.io` anmelden.
4. Image laden und Stack starten:

   ```bash
   docker compose pull
   docker compose up -d
   ```

Bei oeffentlicher Erreichbarkeit `OPENCLAW_BIND_ADDRESS=0.0.0.0` nur zusammen
mit Firewall-Regeln oder einem TLS-Reverse-Proxy verwenden. Die Token-
Authentifizierung bleibt aktiviert.

## Channels

Channel-Tokens koennen ebenfalls in `.env` oder ueber OpenClaw eingerichtet
werden. Beispiel fuer Telegram:

```bash
docker compose run --rm --no-deps openclaw channels add \
  --channel telegram --token "TOKEN"
```

Weitere Konfiguration: <https://docs.openclaw.ai/install>.
