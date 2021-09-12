import pandas as pd
df = pd.read_json (r'data/json/defis_ch_24h.geojson')
df.to_csv (r'data/csv/defis_ch_24h.csv', index = None)

df = pd.read_json (r'data/json/defis_ch_not_24h.geojson')
df.to_csv (r'data/csv/defis_ch_not_24h.csv', index = None)

df = pd.read_json (r'data/json/defis_dispo_knzsg.geojson')
df.to_csv (r'data/csv/defis_dispo_knzsg.csv', index = None)

df = pd.read_json (r'data/json/defis_dispo_srz.geojson')
df.to_csv (r'data/csv/defis_dispo_srz.csv', index = None)