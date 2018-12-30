resource "aws_default_vpc" "default" {
}

resource "aws_default_security_group" "default" {
  vpc_id = "${aws_default_vpc.default.id}"

  ingress {
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_default_subnet" "default_az1" {
  availability_zone = "eu-west-1c"

  tags = {
    Name = "Default subnet for eu-west-1c"
  }
}

resource "aws_default_subnet" "default_az2" {
  availability_zone = "eu-west-1b"

  tags = {
    Name = "Default subnet for eu-west-1b"
  }
}