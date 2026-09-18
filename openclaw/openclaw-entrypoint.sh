#!/bin/sh
set -eu

state_dir="${OPENCLAW_STATE_DIR:-${HOME:-/home/node}/.openclaw}"
config_path="${OPENCLAW_CONFIG_PATH:-${state_dir}/openclaw.json}"
config_dir=$(dirname "$config_path")

mkdir -p "$config_dir"
if [ "${OPENCLAW_FORCE_TEMPLATE:-0}" = "1" ] || [ ! -s "$config_path" ]; then
  cp /opt/openclaw/openclaw.json "$config_path"
fi

exec openclaw "$@"
