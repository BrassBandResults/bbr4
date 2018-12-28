resource "aws_security_group" "web_traffic" {
    name="web-traffic-security-group"
    description="Allow access from the internet to the application"

    tags {
        "Name"="Web Traffic"
    }
}
 
resource "aws_security_group_rule" "http_inbound" {
    type = "ingress"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    security_group_id = "${aws_security_group.web_traffic.id}"
}
 
resource "aws_security_group_rule" "https_inbound" {
    type = "ingress"
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    security_group_id = "${aws_security_group.web_traffic.id}"
}
 
resource "aws_security_group_rule" "web_outbound" {
    type = "egress"
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    security_group_id = "${aws_security_group.web_traffic.id}"
}
 
resource "aws_security_group" "admin_access" {
    name="admin-access-security-group"
    description="Allow access from the defined home ip address to ssh"

    tags {
        "Name"="SSH Traffic"
    }
}
 
resource "aws_security_group_rule" "ssh_inbound_home" {
    type = "ingress"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["${var.home_ip}/32"]
    security_group_id = "${aws_security_group.admin_access.id}"
}
 
resource "aws_security_group_rule" "ssh_inbound_work" {
    type = "ingress"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["${var.work_ip}/32"]
    security_group_id = "${aws_security_group.admin_access.id}"
}
 
