resource "aws_iam_role" "bbr-iam-lambda-thumbs" {
  name = "bbr-iam-lambda-thumbs"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-thumbs-logs" {
  role = "${aws_iam_role.bbr-iam-lambda-thumbs.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-log-policy.arn}"
}

resource "aws_lambda_function" "bbr-thumbnail" {
  filename = "../lambda/thumbnails/target/lambda-thumbnails-1.0.jar" 
  function_name = "${var.prefix}-thumbnail"
  role = "${aws_iam_role.bbr-iam-lambda-thumbs.arn}"
  handler = "uk.co.brassbandresults.lambda.CreateThumbnail"
  source_code_hash = "${base64sha256(file("../lambda/thumbnails/target/lambda-thumbnails-1.0.jar"))}"
  runtime = "java8"
  memory_size = "192"
  timeout = "60"
}

resource "aws_lambda_permission" "bbr-thumbnail-allow-bucket-access" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.bbr-thumbnail.arn}"
  principal = "s3.amazonaws.com"
  source_arn = "${aws_s3_bucket.bbr-uploads-bucket.arn}"  
}

resource "aws_s3_bucket_notification" "lambda-image-bucket-notification" {
  bucket = "${aws_s3_bucket.bbr-uploads-bucket.id}"

  lambda_function {
    lambda_function_arn = "${aws_lambda_function.bbr-thumbnail.arn}"
    events = ["s3:ObjectCreated:*"]
    filter_prefix = ""
    filter_suffix = ""
  }
}

resource "aws_iam_policy" "bbr-lambda-access-thumbnails-policy" {
  name = "bbr-lambda-access-thumbnails-policy"
  path = "/"
  description = "IAM policy for writing to thumbnails bucket"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [ 
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:DeleteObject"
      ],
      "Resource": "${aws_s3_bucket.bbr-uploads-thumbnail-bucket.arn}/*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-write-to-thumbnails" {
  role = "${aws_iam_role.bbr-iam-lambda-thumbs.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-access-thumbnails-policy.arn}"
}

