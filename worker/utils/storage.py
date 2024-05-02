import os
import io
import sys

project_id = os.environ.get('GCLOUD_PROJECT')
bucket_name = os.environ.get('GCLOUD_BUCKET')

from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def upload_file(source_file_name, destination_blob_name):
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(
        source_file_name)
    print("\n-> Updaload storage object {} to bucket {} to {}".format(blob.name, bucket_name, destination_blob_name))

    public = True
    if public:
        blob.make_public()

    return blob.public_url



def download_blob(source_blob_name, destination_file_name):
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )
