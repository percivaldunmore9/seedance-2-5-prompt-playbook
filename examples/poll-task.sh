#!/usr/bin/env bash
set -euo pipefail
: "${ARGOLINK_API_KEY:?Set ARGOLINK_API_KEY in the environment}"
: "${TASK_ID:?Set TASK_ID to the returned Argolink task id}"

curl -fsS "https://api.argolink.io/v1/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARGOLINK_API_KEY"
