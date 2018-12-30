resource "aws_s3_bucket" "bbr-uploads-bucket" {
    bucket = "bbr-media-upload"
    provider = "aws.london"
    region = "eu-west-2"
    acl = "private"
    policy = <<EOF
{
  "Id": "bucket_policy_uploads",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "bucket_policy_uploads_main",
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::bbr-media-upload/*",
      "Principal": "*"
    }
  ]
}
EOF
    website {
        index_document = "index.html"
        error_document = "404.html"
    }
}

resource "aws_s3_bucket" "bbr-uploads-thumbnail-bucket" {
    bucket = "bbr-media-upload-thumbnail"
    provider = "aws.london"
    region = "eu-west-2"
    acl = "private"
    policy = <<EOF
{
  "Id": "bucket_policy_uploads_thumbs",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "bucket_policy_uploads_thumbs_main",
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::bbr-media-upload-thumbnail/*",
      "Principal": "*"
    }
  ]
}
EOF
    website {
        index_document = "index.html"
        error_document = "404.html"
    }
}

resource "aws_s3_bucket" "bbr-media" {
    bucket = "bbr-site-media"
    provider = "aws.london"
    region = "eu-west-2"
    acl = "private"
    policy = <<EOF
{
  "Id": "bucket_policy_media",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "bucket_policy_media_main",
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::bbr-site-media/*",
      "Principal": "*"
    }
  ]
}
EOF
    website {
        index_document = "index.html"
        error_document = "404.html"
    }
}

