#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Stopping and removing MongoDB stack (including data volume)..."
docker compose down -v 2>/dev/null || true
docker rm -f country-mongodb 2>/dev/null || true

echo "Starting fresh MongoDB..."
docker compose up -d

echo -n "Waiting for MongoDB on localhost:27017"
for attempt in $(seq 1 45); do
  # Prefer a local port check — fast and cannot hang like mongosh exec.
  if timeout 1 bash -c 'echo >/dev/tcp/127.0.0.1/27017' 2>/dev/null; then
    echo
    echo "MongoDB is up on localhost:27017"
    docker compose ps
    exit 0
  fi

  # Show progress; if the container exited, fail early with logs.
  if ! docker compose ps --status running 2>/dev/null | grep -q mongodb; then
    state="$(docker compose ps mongodb 2>/dev/null | tail -n +2 || true)"
    if echo "$state" | grep -qiE 'exit|restart'; then
      echo
      echo "MongoDB container is not running. Recent logs:"
      docker compose logs mongodb --tail 40
      if docker compose logs mongodb 2>/dev/null | grep -q 'SERVER-121912\|kernel versions 6.19'; then
        echo
        echo "Hint: your Linux kernel is in the 6.19–7.0.13 range MongoDB blocks on."
        echo "This project uses mongo:8.0.34 with GLIBC_TUNABLES in docker-compose.yml."
        echo "Recreate the container: docker compose down && docker compose up -d"
        echo "Long-term: upgrade the host kernel to 7.0.14+ when available."
      fi
      exit 1
    fi
  fi

  echo -n "."
  sleep 2
done

echo
echo "Timed out waiting for MongoDB. Check logs:"
echo "  docker compose logs mongodb --tail 50"
exit 1
