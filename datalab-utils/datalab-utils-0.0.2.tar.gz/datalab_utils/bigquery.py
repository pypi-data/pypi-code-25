import pandas as pd
import io
import uuid

from tqdm import tqdm_notebook
from google.cloud import bigquery, storage
from google.cloud.storage.bucket import Bucket
from google.cloud.bigquery.dataset import Dataset


def read_bq_table(project_id, dataset_id, table_id, bucket_name, facturation_project_id=None, usecols=None, dtype=None, tqdm=False):
    work_directory = _extract_bq_table(project_id, dataset_id, table_id, bucket_name, facturation_project_id=facturation_project_id)
    df = _load_from_storage(project_id, bucket_name, work_directory, usecols, dtype, tqdm)
    _delete(project_id, bucket_name, work_directory)
    return df

def _extract_bq_table(project_id, dataset_id, table_id, bucket_name='temporary_work', work_directory=None, facturation_project_id=None):
    work_directory = work_directory or str(uuid.uuid4())
    facturation_project_id = facturation_project_id or project_id

    # Prepare extract job
    client = bigquery.Client(project=facturation_project_id)
    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref = dataset_ref.table(table_id)
    gs_uri = "gs://{}/{}/part_*.csv.gz".format(bucket_name, work_directory)
    extract_conf = bigquery.ExtractJobConfig()
    extract_conf.compression = 'GZIP'
    extract_conf.destination_format = 'CSV'

    # Ensure bucket exists
    location = client.get_dataset(dataset_ref).location
    _ensure_bucket(project_id, bucket_name, location)

    print('Extracting table %s to %s' % (table_ref, gs_uri))
    extract_job = client.extract_table(table_ref, gs_uri, job_config=extract_conf)
    extract_job.result()
    return work_directory

def _load_part(blob, usecols=None, dtype=None):
    content = blob.download_as_string()
    return pd.read_csv(io.BytesIO(content), usecols=usecols, dtype=dtype, compression='gzip')

def _load_from_storage(project_id, bucket_name, work_directory, usecols, dtype, tqdm):
    client = storage.client.Client(project=project_id)
    bucket = storage.bucket.Bucket(client, bucket_name)
    parts = list(bucket.list_blobs(prefix=work_directory + "/"))
    parts = tqdm_notebook(parts) if tqdm else parts
    raw_data = []
    print('Loading %s files from gs://%s/%s' % (len(parts), bucket_name, work_directory))
    for part in parts:
        df = _load_part(part, usecols, dtype)
        raw_data.append(df)
    frame = pd.concat(raw_data)
    return frame

def _ensure_bucket(project_id, bucket_name, location):
    client = storage.client.Client(project=project_id)
    bucket = storage.bucket.Bucket(client, bucket_name)
    bucket.location = location
    if not bucket.exists():
        print('Creating bucket gs://%s (location: %s)' % (bucket_name, location))
        bucket.create()

def _delete(project_id, bucket_name, work_directory):
    client = storage.client.Client(project=project_id)
    bucket = storage.bucket.Bucket(client, bucket_name)
    blobs = list(bucket.list_blobs(prefix=work_directory + "/"))

    print('Deleting %s files in gs://%s/%s' % (len(blobs), bucket_name, work_directory))
    bucket.delete_blobs(blobs)