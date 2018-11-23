resource "aws_dynamodb_table" "bbr-event-log-table" {
  name = "EventLog"
  read_capacity = 5
  write_capacity = 5
  hash_key = "Username"
  range_key = "DateTimestamp"  

  attribute { name = "Username" type = "S" }
  attribute { name = "DateTimestamp" type = "N" }

  ttl {
    attribute_name = "TimeToLive"
    enabled = true
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
    vpc_id = "${aws_vpc.bbr-vpc.id}"
    service_name = "com.amazonaws.eu-west-2.dynamodb"
    vpc_endpoint_type = "Gateway"
    route_table_ids = ["${aws_vpc.bbr-vpc.main_route_table_id}",]
}
