resource "aws_s3_bucket" "bbr-uploads-bucket" {
    bucket = "${var.prefix}-media-upload"
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
      "Resource": "arn:aws:s3:::${var.prefix}-media-upload/*",
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
    bucket = "${var.prefix}-media-upload-thumbnail"
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
      "Resource": "arn:aws:s3:::${var.prefix}-media-upload-thumbnail/*",
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
    bucket = "${var.prefix}-site-media"
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
      "Resource": "arn:aws:s3:::${var.prefix}-site-media/*",
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