resource "aws_dynamodb_table" "bbr-event-log-table" {
  name = "EventLog"
  read_capacity = 1
  write_capacity = 2
  hash_key = "Username"
  range_key = "DateTimestamp"  

  attribute { name = "Username" type = "S" }
  attribute { name = "DateTimestamp" type = "N" }

  ttl {
    attribute_name = "TimeToLive"
    enabled = true
  }
}
