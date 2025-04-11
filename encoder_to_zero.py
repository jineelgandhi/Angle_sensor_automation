import pandas as pd


FILEPATH = "measurement_log_20250408_125915.csv"
df = pd.read_csv(FILEPATH)
df.loc[df['step'] == 0, 'encoder'] = 0
df.to_csv(FILEPATH, index=False)
