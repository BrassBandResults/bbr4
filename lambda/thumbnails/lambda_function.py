# (c) 2018 Tim Sawyer
# https://github.com/c-bata/lambda-thumbnail-generator

import boto3
import os
import sys
import uuid
from PIL import Image

s3_client = boto3.client('s3')

RESIZED_BUCKET_NAME = "output-bucket"
RESIZED_IMAGE_SIZE = (200,100)

def resize_image(image_path, resized_path):
  with Image.open(image_path) as image:
    image.thumbnail(RESIZED_IMAGE_SIZE)
    image.save(resized_path)

def lambda_handler(event, context):
  for record in event['Records']:
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    upload_path = '/tmp/resized-{}'.format(key)

    s3_client.download_file(bucket, key, download_path)
    resize_image(download_path, upload_path)
    s3_client.upload_file(upload_path, RESIZED_BUCKET_NAME, key)
