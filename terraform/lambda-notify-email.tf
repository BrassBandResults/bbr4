resource "aws_iam_role" "bbr-iam-lambda-notify-email" {
  name = "bbr-iam-lambda-notify-email"

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

resource "aws_iam_role_policy_attachment" "bbr-lambda-notify-email-logs" {
  role = "${aws_iam_role.bbr-iam-lambda-notify-email.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-log-policy.arn}"
}

resource "aws_lambda_function" "bbr-notify-email" {
  filename = "../lambda/notify-email/target/bbr_notify_email.zip" 
  function_name = "${var.prefix}-notify-email"
  role = "${aws_iam_role.bbr-iam-lambda-notify-email.arn}"
  handler = "bbr_notify_email.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda/notify-email/target/bbr_notify_email.zip"))}"
  runtime = "python3.6"

  vpc_config {
    subnet_ids=["${aws_subnet.lambda-subnet.id}","${aws_subnet.public-subnet.id}"]
    security_group_ids=["${aws_security_group.lambda.id}"]
  }

  environment {
    variables = {
      BBR_DB_CONNECT_STRING = "host='${aws_db_instance.bbr-db.address}' user='bbradmin' password='${var.db_password}' dbname='${aws_db_instance.bbr-db.name}'"
    }
  }

}

resource "aws_sns_topic_subscription" "bbr-notify-email-subs" {
  topic_arn = "${aws_sns_topic.bbr-notify.arn}"
  protocol  = "lambda"
  endpoint  = "${aws_lambda_function.bbr-notify-email.arn}"
}

resource "aws_lambda_permission" "bbr-sns-notify-email-perms" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.bbr-notify-email.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${aws_sns_topic.bbr-notify.arn}"
}

resource "aws_iam_policy" "bbr-lambda-email-rds-policy" {
  name = "bbr-lambda-email-rds-policy"
  path = "/"
  description = "Allow access to RDS in VPC"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
	"Effect": "Allow",
        "Action": [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ses:SendEmail"
        ],
        "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "bbr-lambda-email-db-access" {
  role = "${aws_iam_role.bbr-iam-lambda-notify-email.name}"
  policy_arn = "${aws_iam_policy.bbr-lambda-email-rds-policy.arn}"
}
