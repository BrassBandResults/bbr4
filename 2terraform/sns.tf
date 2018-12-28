resource "aws_sns_topic" "bbr-notify" {
  name="${var.prefix}-notify-topic"
}