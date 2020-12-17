#!/bin/bash

set -e
set -o pipefail

function cleanup {
  exit $?
}
trap "cleanup" EXIT

DIR="$(cd "$(dirname "$0")" && pwd)"


# Defibrillatoren Dispogebiet SRZ
echo -ne "Query Defibrillatoren Dispogebiet SRZ...         "
cat $DIR/queries/defis_dispo_srz.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_dispo_srz.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren Stadt Zürich
echo -ne "Query Defibrillatoren Stadt Zürich...            "
cat $DIR/queries/defis_stadt_zh.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_stadt_zh.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren Kanton Zürich
echo -ne "Query Defibrillatoren Kanton Zürich...           "
cat $DIR/queries/defis_kt_zh.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_kt_zh.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren Kanton St. Gallen
echo -ne "Query Defibrillatoren Kanton St.Gallen...           "
cat $DIR/queries/defis_kt_sg.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_kt_sg.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren KNZ St.Gallen
echo -ne "Query Defibrillatoren KNZ St. Gallen...           "
cat $DIR/queries/defis_dispo_knzsg.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_dispo_knzsg.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren ganze Schweiz
echo -ne "Query Defibrillatoren ganze Schweiz...           "
cat $DIR/queries/defis_switzerland.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_switzerland.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren ganze Schweiz 24h
echo -ne "Query Defibrillatoren ganze Schweiz 24h...           "
cat $DIR/queries/defis_ch_24h.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_ch_24h.geojson
echo -ne "\t\t - Done.\r"
echo ""

# Defibrillatoren ganze Schweiz NICHT 24h
echo -ne "Query Defibrillatoren ganze Schweiz, nicht 24h...           "
cat $DIR/queries/defis_ch_not_24h.txt | python $DIR/overpass_query.py | osmtogeojson > $DIR/data/defis_ch_not_24h.geojson
echo -ne "\t\t - Done.\r"
echo ""