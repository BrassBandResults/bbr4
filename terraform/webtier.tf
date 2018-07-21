resource "aws_instance" "bbr-web" {
    ami = "${lookup(var.ec2ami, var.region)}"
    instance_type = "t2.micro"
    key_name = "${lookup(var.keypair, var.region)}"
    security_groups = [
        "${aws_security_group.web_traffic.name}",
        "${aws_security_group.admin_access.name}"
    ]
    tags {
        Name = "bbr-web"    
    }

}