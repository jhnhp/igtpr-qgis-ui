#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_SRC="$DIR/igtpr_login_example"
QGIS_PLUGINS_DIR="$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins"

mkdir -p "$QGIS_PLUGINS_DIR"
rm -rf "$QGIS_PLUGINS_DIR/igtpr_login_example"
ln -sfn "$PLUGIN_SRC" "$QGIS_PLUGINS_DIR/igtpr_login_example"

echo "✓ Plugin Geoportal IGT-PR (Mockup V2) berhasil dihubungkan (symlink) ke:"
echo "  $QGIS_PLUGINS_DIR/igtpr_login_example"
echo ""
echo "Perubahan kode pada repositori akan langsung aktif secara otomatis di QGIS."
