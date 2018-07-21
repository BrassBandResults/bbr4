resource "aws_security_group" "web_traffic" {
    name="web-traffic-security-group"
    description="Allow access from the internet to the application"

    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "admin_access" {
    name="admin-access-security-group"
    description="Allow access from the defined home ip address to ssh"

     ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["${var.local_ip}/32"]
    }
}