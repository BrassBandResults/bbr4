resource "aws_iam_role" "bbr-iam-lambda-award-points" {
  name = "bbr-iam-lambda-award-points"

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

resource "aws_iam_role_policy_attachment" "bbr-lambda-award-points-logs" {
  role = "${aws_iam_role.bbr-iam-lambda-award-points.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-log-policy.arn}"
}

resource "aws_lambda_function" "bbr-award-points" {
  filename = "../lambda/award-points/target/bbr_award_points.zip" 
  function_name = "${var.prefix}-award-points"
  role = "${aws_iam_role.bbr-iam-lambda-award-points.arn}"
  handler = "bbr_award_points.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda/award-points/target/bbr_award_points.zip"))}"
  runtime = "python3.6"
}

resource "aws_sns_topic_subscription" "bbr-award-points-subs" {
  topic_arn = "${aws_sns_topic.bbr-notify.arn}"
  protocol  = "lambda"
  endpoint  = "${aws_lambda_function.bbr-award-points.arn}"
}

resource "aws_lambda_permission" "bbr-sns-award-points-perms" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.bbr-award-points.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${aws_sns_topic.bbr-notify.arn}"
}

resource "aws_iam_policy" "bbr-lambda-points-dynamodb-policy" {
  name = "bbr-lambda-points-dynamodb-policy"
  path = "/"
  description = "IAM policy for writing to DynamoDB event log"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [ 
        "dynamodb:PutItem"
      ],
      "Resource": "${aws_dynamodb_table.bbr-event-log-table.arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-points-log" {
  role = "${aws_iam_role.bbr-iam-lambda-award-points.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-points-dynamodb-policy.arn}"
}
