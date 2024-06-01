from google.cloud import bigquery
import pandas as pd

df = pd.read_csv("pokemon_data/pokemon.csv")
df = df.loc[:50000, :]
bq_client = bigquery.Client(
    location="europe-west3", project="cloud-computing-project-418718"
)
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = bq_client.load_table_from_dataframe(
    df, "cloud-computing-project-418718.common_ds.main_table", job_config=job_config
)
job.result()
