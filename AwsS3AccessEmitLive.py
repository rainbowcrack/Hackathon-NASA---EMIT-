# comments on this code were made by @rainbowcrack
# create a temporary access key on AWS S3 Access server to extract real-time data. Access an example: 
# s3://lp-prod-protected/EMITL2ARFL.001/EMIT_L2A_RFL_001_20231005T044255_2327803_027/EMIT_L2A_RFL_001_20231005T044255_2327803_027.nc
# import libraries like bitstreaming files, JSON notation and HTTP request in url into a CSV file
# someone have pip install 

import argparse
import base64
import boto3
import json
import requests

# a definition to receive your access key - token

def retrieve_credentials(event):

# code comment that says to replace the dummy values ​​with your 1 hour token

    """Makes the Oauth calls to authenticate with EDS and return a set of s3
    same-region, read-only credntials.
    """
    login_resp = requests.get(
        event['s3_endpoint'], allow_redirects=False
    )
    login_resp.raise_for_status()

    auth = f"{event['edl_username']}:{event['edl_password']}"
    encoded_auth  = base64.b64encode(auth.encode('ascii'))

    auth_redirect = requests.post(
        login_resp.headers['location'],
        data = {"credentials": encoded_auth},
        headers= { "Origin": event['s3_endpoint'] },
        allow_redirects=False
    )
    auth_redirect.raise_for_status()

# Here comes the HTTP request by requests library

    final = requests.get(auth_redirect.headers['location'], allow_redirects=False)

    results = requests.get(event['s3_endpoint'], cookies={'accessToken': final.cookies['accessToken']})
    results.raise_for_status()

    return json.loads(results.content)

# return the code in javascript - file JSON


def lambda_handler(event, context):

    creds = retrieve_credentials(event)
    bucket = event['bucket_name']

# create client with temporary credentials

    client = boto3.client(
        's3',
        aws_access_key_id=creds["accessKeyId"],
        aws_secret_access_key=creds["secretAccessKey"],
        aws_session_token=creds["sessionToken"]
    )

# use the client for readonly access.

    response = client.list_objects_v2(Bucket=bucket, Prefix="")

    return {
        'statusCode': 200,
        'body': json.dumps([r["Key"] for r in response['Contents']])
    }
