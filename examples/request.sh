#!/usr/bin/env bash
set -euo pipefail
: "${ARGOLINK_API_KEY:?Set ARGOLINK_API_KEY in the environment}"

curl -fsS https://api.argolink.io/v1/videos/generations \
  -H "Authorization: Bearer $ARGOLINK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"seedance-2.5","prompt":"a concise cinematic establishing shot","duration":5}'

# Save the returned task id and poll it with GET /v1/tasks/{id}; do not resubmit on a timeout.
