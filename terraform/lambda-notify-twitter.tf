resource "aws_iam_role" "bbr-iam-lambda-notify-twitter" {
  name = "bbr-iam-lambda-notify-twitter"

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

resource "aws_iam_role_policy_attachment" "bbr-lambda-notify-twitter-logs" {
  role = "${aws_iam_role.bbr-iam-lambda-notify-twitter.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-log-policy.arn}"
}

resource "aws_lambda_function" "bbr-notify-twitter" {
  filename = "../lambda/notify-twitter/target/bbr_notify_twitter.zip" 
  function_name = "${var.prefix}-notify-twitter"
  role = "${aws_iam_role.bbr-iam-lambda-notify-twitter.arn}"
  handler = "bbr_notify_twitter.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda/notify-twitter/target/bbr_notify_twitter.zip"))}"
  runtime = "python3.6"
}

resource "aws_sns_topic_subscription" "bbr-notify-twitter-subs" {
  topic_arn = "${aws_sns_topic.bbr-notify.arn}"
  protocol  = "lambda"
  endpoint  = "${aws_lambda_function.bbr-notify-twitter.arn}"
}

resource "aws_lambda_permission" "bbr-sns-notify-twitter-perms" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.bbr-notify-twitter.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${aws_sns_topic.bbr-notify.arn}"
}