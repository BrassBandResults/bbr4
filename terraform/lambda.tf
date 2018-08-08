resource "aws_iam_role" "bbr-iam-lambda" {
  name = "bbr-iam-lambda"

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
  filename = "../lambda/thumbnails/target/lambda-thumbnails-1.0.jar" 
  function_name = "${var.prefix}-thumbnail"
  role = "${aws_iam_role.bbr-iam-lambda.arn}"
  handler = "uk.co.brassbandresults.lambda.CreateThumbnail"
  source_code_hash = "${base64sha256(file("../lambda/thumbnails/target/lambda-thumbnails-1.0.jar"))}"
  runtime = "java8"
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

resource "aws_iam_policy" "bbr-lambda-logging" {
  name = "bbr-lambda-logging"
  path = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-logs" {
  role = "${aws_iam_role.bbr-iam-lambda.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-logging.arn}"
}
