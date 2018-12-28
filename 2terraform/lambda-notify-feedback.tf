resource "aws_iam_role" "bbrie-iam-lambda-notify-feedback" {
  name = "bbrie-iam-lambda-notify-feedback"

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

resource "aws_iam_role_policy_attachment" "bbr-lambda-notify-feedback-logs" {
  role = "${aws_iam_role.bbrie-iam-lambda-notify-feedback.name}"
  policy_arn = "${aws_iam_policy.bbrie-lambda-log-policy.arn}"
}

resource "aws_lambda_function" "bbr-notify-feedback" {
  filename = "../lambda/notify-feedback/target/bbr_notify_feedback.zip" 
  function_name = "${var.prefix}-notify-feedback"
  role = "${aws_iam_role.bbrie-iam-lambda-notify-feedback.arn}"
  handler = "bbr_notify_feedback.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda/notify-feedback/target/bbr_notify_feedback.zip"))}"
  runtime = "python3.6"
  timeout = 30
}

resource "aws_sns_topic_subscription" "bbr-notify-feedback-subs" {
  topic_arn = "${aws_sns_topic.bbr-notify.arn}"
  protocol  = "lambda"
  endpoint  = "${aws_lambda_function.bbr-notify-feedback.arn}"
}

resource "aws_lambda_permission" "bbr-sns-notify-feedback-perms" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.bbr-notify-feedback.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${aws_sns_topic.bbr-notify.arn}"
}

resource "aws_iam_policy" "bbrie-lambda-feedback-ses-policy" {
  name = "bbrie-lambda-feedback-ses-policy"
  path = "/"
  description = "Allow access to SES"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
          "ses:SendEmail"
        ],
        "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-feedback-ses-access" {
  role = "${aws_iam_role.bbrie-iam-lambda-notify-feedback.name}"
  policy_arn = "${aws_iam_policy.bbrie-lambda-feedback-ses-policy.arn}"
}
 
