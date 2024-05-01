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
import io
import sys

project_id = os.environ.get('GCLOUD_PROJECT')

# TODO: Get the Bucket name from the GCLOUD_BUCKET environment variable

bucket_name = os.environ.get('GCLOUD_BUCKET')

# END TODO

# TODO: Import the storage module

from google.cloud import storage

# END TODO

# TODO: Create a client for Cloud Storage

storage_client = storage.Client()

# END TODO


# TODO: Use the client to get the Cloud Storage bucket

bucket = storage_client.bucket(bucket_name)

# END TODO

"""
Uploads a file to a given Cloud Storage bucket and returns the public url
to the new object.
"""


def upload_file(source_file_name, destination_blob_name):
    # TODO: Use the bucket to get a blob object

    blob = bucket.blob(destination_blob_name)
    generation_match_precondition = 0

    # END TODO

    # TODO: Use the blob to upload the file
    generation_match_precondition = 0
    # blob.upload_from_file(file)
    blob.upload_from_filename(
        source_file_name)
    print("\n-> Updaload storage object {} to bucket {} to {}".format(blob.name, bucket_name, destination_blob_name))

    # END TODO

    # TODO: Make the object public
    public = True
    if public:
        blob.make_public()

    # END TODO

    # TODO: Modify to return the blob's Public URL

    return blob.public_url

    # END TODO


def download_blob(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )
