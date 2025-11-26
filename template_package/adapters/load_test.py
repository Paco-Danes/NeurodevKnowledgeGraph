import pandas as pd
human_path = "template_package/data/liana_humanconsensus_db.parquet"
df_human = pd.read_parquet(human_path)

print(df_human.columns)