#!/bin/sh
# Запуск Klava: отдельное окно через Chromium-подобный браузер (--app),
# иначе — обычная вкладка браузера по умолчанию.
DIR=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
INDEX="$DIR/index.html"

for b in chromium chromium-browser google-chrome google-chrome-stable brave-browser microsoft-edge vivaldi; do
  if command -v "$b" >/dev/null 2>&1; then
    exec "$b" --app="file://$INDEX" "$@"
  fi
done
exec xdg-open "$INDEX"
