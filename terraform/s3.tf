resource "aws_s3_bucket" "bbr-uploads-bucket" {
    bucket = "${var.prefix}-media-upload"
    acl = "private"
}

resource "aws_s3_bucket" "bbr-uploads-thumbnail-bucket" {
    bucket = "${var.prefix}-media-upload-thumbnail"
    acl = "private"
}