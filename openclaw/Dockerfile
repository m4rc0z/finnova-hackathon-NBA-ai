# syntax=docker/dockerfile:1

FROM node:26-bookworm-slim

ARG OPENCLAW_VERSION=latest

ENV HOME=/home/node \
    OPENCLAW_HOME=/home/node \
    OPENCLAW_STATE_DIR=/home/node/.openclaw \
    OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json \
    OPENCLAW_WORKSPACE_DIR=/home/node/.openclaw/workspace \
    OPENCLAW_GATEWAY_PORT=18789 \
    NODE_ENV=production

RUN set -eux; \
    npm_major="$(npm --version | cut -d. -f1)"; \
    npm_minor="$(npm --version | cut -d. -f2)"; \
    if [ "$npm_major" -ge 12 ] || { [ "$npm_major" -eq 11 ] && [ "$npm_minor" -ge 16 ]; }; then \
      npm install --global "openclaw@${OPENCLAW_VERSION}" --allow-scripts=openclaw; \
    else \
      npm install --global "openclaw@${OPENCLAW_VERSION}"; \
    fi; \
    npm cache clean --force; \
    mkdir -p /home/node/.openclaw/workspace; \
    chown -R node:node /home/node/.openclaw

COPY --chown=node:node openclaw.json /opt/openclaw/openclaw.json
COPY --chown=node:node --chmod=755 openclaw-entrypoint.sh /usr/local/bin/openclaw-entrypoint

WORKDIR /home/node
USER node

EXPOSE 18789
VOLUME ["/home/node/.openclaw"]

ENTRYPOINT ["/usr/local/bin/openclaw-entrypoint"]
CMD ["gateway", "run", "--bind", "lan", "--auth", "token"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+(process.env.OPENCLAW_GATEWAY_PORT||'18789')+'/healthz').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"]
