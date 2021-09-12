import pandas as pd
df = pd.read_json (r'data/json/defis_ch_24h.geojson')
df.to_csv (r'data/csv/defis_ch_24h.csv', index = None)