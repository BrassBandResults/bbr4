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

data "template_file" "bootstrap-web" {
    template = "${file("bootstrap-web.tpl")}" 
    vars {
        username = "${var.prefix}"
        password = "${var.web_ssh_password}"
    }
}

data "template_file" "bootstrap-bbr" {
    template = "${file("bootstrap-bbr.tpl")}" 
    vars {
        
    }
}

data "template_file" "django-settings-live" {
    template = "${file("settings-live.tpl.py")}" 
    vars {
        dbHost = "${aws_db_instance.bbr-db.address}"
        dbPassword = "${var.db_password}"
        djangoSecretKey = "${var.djangoSecretKey}"
        googleMapsKey = "${var.googleMapsKey}"
    }
}

resource "aws_instance" "bbr-web" {
    ami = "${lookup(var.ec2ami, var.region)}"
    instance_type = "t2.micro"
    key_name = "${lookup(var.keypair, var.region)}"
    subnet_id = "${aws_subnet.public-subnet.id}"
    private_ip = "10.0.7.7"

    vpc_security_group_ids = [
        "${aws_security_group.web_traffic.id}",
        "${aws_security_group.admin_access.id}"
    ]
    
    tags {
        Name = "bbr-web"    
    }

    provisioner "file" {
        source = "../web/scripts/"
        destination = "/home/admin"
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "admin"
        }  
    }

    provisioner "file" {
        content = "${data.template_file.bootstrap-web.rendered}"
        destination = "bootstrap-web.sh"
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "admin"
        }  
    }

    provisioner "remote-exec" {
        inline = [
            "chmod a+x bootstrap-web.sh",
            "./bootstrap-web.sh",
        ]
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "admin"
        }  
    }
    
    provisioner "file" {
        content = "${data.template_file.pgpass.rendered}"
        destination = ".pgpass"
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "bbr"
        }  
    }

    provisioner "file" {
        content = "${data.template_file.bootstrap-bbr.rendered}"
        destination = "bootstrap-bbr.sh"
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "bbr"
        }  
    }

    provisioner "remote-exec" {
        inline = [
            "chmod a+x bootstrap-bbr.sh",
            "./bootstrap-bbr.sh",
        ]
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "bbr"
        }  
    }

        provisioner "file" {
        content = "${data.template_file.django-settings-live.rendered}"
        destination = "~/bbr4/web/site/bbr/settingslive.py"
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "bbr"
        }  
    }

    provisioner "remote-exec" {
        inline = [
            "sudo /etc/init.d/gu-bbr stop",
            "sudo /etc/init.d/gu-bbr start",
        ]
        connection {
            type = "ssh"
            agent = false
            private_key = "${file("${var.ec2_private_key}")}"
            user = "admin"
        }  
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
