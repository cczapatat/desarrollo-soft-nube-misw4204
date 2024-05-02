import os

project_id = os.environ.get('GCLOUD_PROJECT')
bucket_name = os.environ.get('GCLOUD_BUCKET')
#credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')

from google.cloud import storage
from google.cloud import secretmanager
from google.oauth2 import service_account
import json



# Initialize the Secret Manager client
client = secretmanager.SecretManagerServiceClient()

# Define the secret name
secret_name = "projects/616996447568/secrets/storage-credentials/versions/3"

# Access the secret
response = client.access_secret_version(request={"name": secret_name})

# Extract the secret payload
secret_payload = response.payload.data.decode("UTF-8")

# Write the secret to a temporary file
temp_file_path = "/backend/secret.json"
with open(temp_file_path, "w") as f:
    f.write(secret_payload)

print("storing crdentials from vault")
# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

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
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    # With credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    client_signed = storage.Client(credentials=credentials)

    # Obtiene el bucket y el objeto
    bucket_signed = client_signed.bucket(bucket_name)
    blob = bucket_signed.blob(object_name)

    # Genera la URL firmada con la expiración proporcionada en segundos
    signed_url = blob.generate_signed_url(expiration=expiration)

    return signed_url
