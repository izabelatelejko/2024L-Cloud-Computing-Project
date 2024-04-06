from google.cloud import bigquery
import pandas as pd

df = pd.read_csv("ecom-user-churn-data.csv")
df = df.iloc[20000:49358, :]
bq_client = bigquery.Client(
    location="europe-west3", project="cloud-computing-project-418718"
)
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = bq_client.load_table_from_dataframe(
    df, "cloud-computing-project-418718.common_ds.main_table", job_config=job_config
)
job.result()
