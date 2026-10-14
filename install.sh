#!/bin/sh
# Установка Klava в меню приложений (Linux, только для текущего пользователя).
#   ./install.sh              — установить или обновить
#   ./install.sh --uninstall  — удалить
set -eu

SRC=$(cd "$(dirname "$0")" && pwd)
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
DEST="$DATA/klava"
APPS="$DATA/applications"
ICONS="$DATA/icons/hicolor/scalable/apps"
# Имя ярлыка совпадает с ID приложения: так GNOME связывает окно с иконкой в доке
DESKTOP_ID="io.github.alexander_lun.Klava"

refresh() {
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" || true
  command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -f -t "$DATA/icons/hicolor" 2>/dev/null || true
}

if [ "${1:-}" = "--uninstall" ]; then
  rm -f "$APPS/$DESKTOP_ID.desktop" "$APPS/klava.desktop" "$ICONS/klava.svg"
  # Каталог с исходниками (например, git-клон) не трогаем
  if [ "$SRC" != "$DEST" ] && [ -d "$DEST" ]; then rm -rf "$DEST"; fi
  refresh
  echo "Klava удалена из меню приложений."
  echo "Статистика оставлена в ${DATA}/klava-data (удалите вручную, если не нужна)."
  exit 0
fi

if [ "$SRC" != "$DEST" ]; then
  mkdir -p "$DEST/packaging"
  cp "$SRC/index.html" "$SRC/texts-ru.js" "$SRC/texts-en.js" "$DEST/"
  cp "$SRC/packaging/klava.sh" "$SRC/packaging/klava-window.py" "$SRC/packaging/icon.svg" "$DEST/packaging/"
fi
chmod +x "$DEST/packaging/klava.sh"

mkdir -p "$APPS" "$ICONS"
cp "$SRC/packaging/icon.svg" "$ICONS/.klava.svg.tmp" && mv -f "$ICONS/.klava.svg.tmp" "$ICONS/klava.svg"
# Ярлык пишется во временный файл и подменяется атомарно: GNOME Shell следит за
# каталогом и падает, если успевает прочитать недописанный .desktop
TMP="$APPS/.$DESKTOP_ID.desktop.tmp"
cat > "$TMP" <<EOF
[Desktop Entry]
Type=Application
Version=1.5
Name=Klava
GenericName=Тренажёр слепой печати
GenericName[en]=Touch Typing Trainer
Comment=Офлайн-тренажёр слепой печати (русский и английский)
Comment[en]=Offline touch typing trainer (Russian and English)
Exec="$DEST/packaging/klava.sh"
Icon=klava
Terminal=false
Categories=Education;
Keywords=typing;keyboard;touch;слепая;печать;клавиатура;тренажёр;klava;
EOF
mv -f "$TMP" "$APPS/$DESKTOP_ID.desktop"
rm -f "$APPS/klava.desktop"  # ярлык старых версий
refresh
echo "Klava установлена: $DEST"
echo "Ищите её в меню приложений по слову «Klava»."
