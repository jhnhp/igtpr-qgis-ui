#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pasang / perbarui symlink ke direktori plugin QGIS
bash "$DIR/install_to_qgis.sh"

echo "Memulai QGIS dengan plugin Geoportal IGT-PR..."
exec qgis "$@"
