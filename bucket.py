import inspect
import os
import boto3


def print_error(e: Exception):
    # print(f"Error during `{inspect.stack()[1].function}`: {bucket_name}\n")
    print(f"Error during `{inspect.stack()[1].function}`.\n")
    print(f"{e.__class__}\n")
    print(f"{e}\n")
    print(f"End error clause -------- \n")


def create_s3_bucket(bucket_name: str, profile: str = "iam_root"):
    print(f"Attempting to create bucket {bucket_name}\n")

    # Create Bucket
    session = boto3.session.Session(
        profile_name=profile if profile else None
    )
    s3 = session.resource('s3')
    try:
        s3.create_bucket(
            Bucket=bucket_name.lower()
        )
    except Exception as e:
        print_error(e)

    print(f"Bucket `{bucket_name}` created.")

    # Query Bucket
    # try:
    #     bucket_region = s3.meta.client.head_bucket(Bucket=bucket_name)['BucketRegion']
    #     print(f"Bucket {bucket_name} exists @ {bucket_region=}")
    # except Exception as e:
    #     print_error(e)


def create_s3_folder(bucket_name: str, folder_name: str, profile: str = "iam_root"):
    print(f"Attempting to create folder in bucket: {bucket_name}")
    session = boto3.session.Session(
        profile_name=profile if profile else None
    )
    s3 = session.resource('s3')

    try:
        s3.Object(bucket_name, folder_name + '/').put()
    except Exception as e:
        print_error(e)

    print(f"Folder `{folder_name}` created.")

def upload_s3_object_to_bucket(bucket_name: str, file_path: str, folder: str = None, profile: str = "iam_root"):
    print(f"Attempting to upload file {file_path} to bucket: {bucket_name}")
    session = boto3.session.Session(
        profile_name=profile if profile else None
    )
    s3 = session.resource('s3')
    try:
        file_short_name = file_path.split('\\')[-1]
        # os.path.join(folder, file_short_name) # concatenating like Windows FS structure
        s3.Object(bucket_name, f"{folder}/{file_short_name}").upload_file(file_path)
    except Exception as e:
        print_error(e)

    print(f"File `{file_short_name}` was uploaded to `{bucket_name}/{folder}/{file_short_name}`.")
