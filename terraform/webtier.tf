resource "aws_instance" "bbr-web" {
    ami = "${lookup(var.ec2ami, var.region)}"
    instance_type = "t2.micro"
    tags {
        Name = "bbr-web"    
    }

}