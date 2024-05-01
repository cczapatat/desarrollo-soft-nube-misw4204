# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.oauth2 import service_account


project_id = os.environ.get('GCLOUD_PROJECT')
bucket_name = os.environ.get('GCLOUD_BUCKET')
credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')


from google.cloud import storage

storage_client = storage.Client()


bucket = storage_client.bucket(bucket_name)


def upload_file(source_file_name, destination_blob_name):

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(
        source_file_name)
    print("\n-> Upload storage object {} to bucket {} to {}".format(blob.name, bucket_name, destination_blob_name))

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


def generate_signed_url(object_name, expiration=3600):

    # With credentials
    # credentials = service_account.Credentials.from_service_account_file(credentials_path)
    # client = storage.Client(credentials=credentials)
    # With service Account
    client = storage.Client()

    # Obtiene el bucket y el objeto
    blob = bucket.blob(object_name)

    # Genera la URL firmada con la expiración proporcionada en segundos
    signed_url = blob.generate_signed_url(expiration=expiration)

    return signed_url
