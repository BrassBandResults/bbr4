resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

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

resource "aws_lambda_function" "bbr-thumbnail" {
  filename = "../lambda/thumbnails/build/bbr-thumbnails.zip" 
  function_name = "${var.prefix}-thumbnail"
  role = "${aws_iam_role.iam_for_lambda.arn}"
  handler = "lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda/thumbnails/build/bbr-thumbnails.zip"))}"
  runtime = "python3.6"
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
