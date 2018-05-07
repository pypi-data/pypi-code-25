import io
import math
import pandas as pd
import uuid

from google.cloud import bigquery, storage


def read_bq_table(
        project_id,
        dataset_id,
        table_id,
        temporary_bucket_name='temporary_work',
        facturation_project_id=None,
        usecols=None,
        dtype=None,
        tqdm=None):
    work_directory = _extract_bq_table(project_id, dataset_id, table_id, temporary_bucket_name, facturation_project_id)
    df = _load_from_storage(project_id, temporary_bucket_name, work_directory, usecols, dtype, tqdm)
    _delete_bucket_data(project_id, temporary_bucket_name, work_directory)
    return df


def read_bq_query(
        query,
        temporary_project_id,
        temporary_bucket_name='temporary_work',
        temporary_dataset_id='exports',
        temporary_table_id=None,
        use_legacy_sql=False,
        usecols=None,
        dtype=None,
        tqdm=False):

    temporary_table_id = temporary_table_id or 'tmp_%s' % int(math.fabs(hash(query)))
    _create_temporary_table(query, temporary_project_id, temporary_dataset_id, temporary_table_id, use_legacy_sql)
    df = read_bq_table(temporary_project_id, temporary_dataset_id, temporary_table_id, temporary_bucket_name, usecols=usecols, dtype=dtype, tqdm=tqdm, facturation_project_id=temporary_project_id)
    _delete_table(temporary_project_id, temporary_dataset_id, temporary_table_id)
    return df


def _create_temporary_table(query, project_id, dataset_id, table_id, use_legacy_sql):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.QueryJobConfig()
    job_config.allow_large_results = True
    job_config.create_disposition = 'CREATE_IF_NEEDED'
    job_config.write_disposition = 'WRITE_TRUNCATE'
    job_config.destination = table_ref
    job_config.flatten_results = True
    job_config.use_legacy_sql = use_legacy_sql

    print('Creating temporary table %s from %s' % (table_ref, query))
    job = client.query(query, job_config)
    return job.result()


def _extract_bq_table(project_id, dataset_id, table_id, bucket_name, facturation_project_id):
    work_directory = str(uuid.uuid4())
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
    parts = tqdm(parts) if tqdm else parts
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


def _delete_bucket_data(project_id, bucket_name, work_directory):
    client = storage.client.Client(project=project_id)
    bucket = storage.bucket.Bucket(client, bucket_name)
    blobs = list(bucket.list_blobs(prefix=work_directory + "/"))

    print('Deleting %s files in gs://%s/%s' % (len(blobs), bucket_name, work_directory))
    bucket.delete_blobs(blobs)


def _delete_table(project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref = dataset_ref.table(table_id)
    print('Deleting %s' % table_ref)
    client.delete_table(table_ref)
