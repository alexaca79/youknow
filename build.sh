#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${ACR_LOGIN_SERVER:-}"
TAG="${IMAGE_TAG:-latest}"

BACKEND_IMAGE="youknow-backend:${TAG}"
FRONTEND_IMAGE="youknow-frontend:${TAG}"

echo "=== Building backend image ==="
docker build -t "${BACKEND_IMAGE}" "${SCRIPT_DIR}/backend"

echo ""
echo "=== Building frontend image ==="
docker build -t "${FRONTEND_IMAGE}" "${SCRIPT_DIR}/frontend"

echo ""
echo "✓ Built ${BACKEND_IMAGE}"
echo "✓ Built ${FRONTEND_IMAGE}"

if [[ -n "${REGISTRY}" ]]; then
  echo ""
  echo "=== Tagging and pushing to ${REGISTRY} ==="
  docker tag "${BACKEND_IMAGE}" "${REGISTRY}/${BACKEND_IMAGE}"
  docker tag "${FRONTEND_IMAGE}" "${REGISTRY}/${FRONTEND_IMAGE}"
  docker push "${REGISTRY}/${BACKEND_IMAGE}"
  docker push "${REGISTRY}/${FRONTEND_IMAGE}"
  echo "✓ Pushed ${REGISTRY}/${BACKEND_IMAGE}"
  echo "✓ Pushed ${REGISTRY}/${FRONTEND_IMAGE}"
fi
