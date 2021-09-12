#!/bin/bash

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"

echo -ne "Konvertiere Daten           "
python $DIR/converter.py
echo -ne "\t\t - Done.\r"
echo ""