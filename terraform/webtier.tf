data "template_file" "pgpass" {
    template = "$${pg_host}:$${pg_port}:$${pg_dbname}:$${pg_username}:$${pg_password}"

    vars {
        pg_host = "${aws_db_instance.bbr-db.address}"
        pg_port = "${aws_db_instance.bbr-db.port}"
        pg_dbname = "${aws_db_instance.bbr-db.name}"
        pg_username = "bbradmin"
        pg_password = "${var.db_password}"
    }
}

data "template_file" "bootstrap" {
    template = "${file("bootstrap-web.sh")}"
    vars {
        username = "${var.prefix}"
        password = "${var.web_ssh_password}"
    }
}

resource "aws_instance" "bbr-web" {
    ami = "${lookup(var.ec2ami, var.region)}"
    instance_type = "t2.micro"
    key_name = "${lookup(var.keypair, var.region)}"
    subnet_id = "${aws_subnet.public-subnet.id}"
    private_ip = "10.0.7.7"
    user_data = "${data.template_file.bootstrap.rendered}"

    security_groups = [
        "${aws_security_group.web_traffic.id}",
        "${aws_security_group.admin_access.id}"
    ]
    
    tags {
        Name = "bbr-web"    
    }

    provisioner "file" {
        content = "${data.template_file.pgpass.rendered}"
        destination = ".pgpass"
    }

   connection {
        type = "ssh"
        agent = false
        private_key = "${file("${var.ec2_private_key}")}"
        user = "admin"
    }  
}

resource "aws_eip" "web-tier-ip-address" {
    vpc = true
    associate_with_private_ip = "10.0.7.7"
    depends_on = ["aws_internet_gateway.bbr-public-gateway"]
}

resource "aws_eip_association" "eip-web-association" {
    instance_id = "${aws_instance.bbr-web.id}"
    allocation_id = "${aws_eip.web-tier-ip-address.id}"
} 