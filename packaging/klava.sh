#!/bin/sh
# Запуск Klava на Linux, по убыванию предпочтения:
#   1) собственное окно на системном WebKitGTK (python3-gobject + webkitgtk6.0);
#   2) отдельное окно Chromium-подобного браузера (--app);
#   3) вкладка браузера по умолчанию.
DIR=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
INDEX="$DIR/index.html"

if command -v python3 >/dev/null 2>&1 &&
   python3 -c 'import gi; gi.require_version("Gtk", "4.0"); gi.require_version("WebKit", "6.0")' 2>/dev/null; then
  exec python3 "$DIR/packaging/klava-window.py" "$@"
fi

for b in chromium chromium-browser google-chrome google-chrome-stable brave-browser microsoft-edge vivaldi; do
  if command -v "$b" >/dev/null 2>&1; then
    exec "$b" --app="file://$INDEX" "$@"
  fi
done
exec xdg-open "$INDEX"
