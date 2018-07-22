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

    provisioner "file" {
        content = "${data.template_file.pgpass.rendered}"
        destination = ".pgpass"
    }
    
    provisioner "file" {
        source = "../web/puppet/bootstrap.pp"
        destination = "bootstrap.pp"
    }

    provisioner "remote-exec" {
        inline = [
            "sudo apt-get update",
            "sudo apt-get upgrade",

            "sudo addgroup ${var.prefix}",
            "sudo adduser ${var.prefix} --ingroup ${var.prefix} --disabled-password --gecos \"\"",
            "sudo bash -c echo ${var.prefix}:${var.web_ssh_password} | chpasswd",
            "sudo mkdir /home/${var.prefix}/.ssh",
            "sudo cp ~/.ssh/authorized_keys /home/${var.prefix}/.ssh",
            "sudo chown -R ${var.prefix}:${var.prefix} /home/${var.prefix}/.ssh",

            "chmod 600 .pgpass",
            "sudo cp ~/.pgpass /home/${var.prefix}",
            "sudo chown -R ${var.prefix}:${var.prefix} /home/${var.prefix}/.pgpass",

            "sudo apt-get install puppet git postgresql-client -y",
            "sudo puppet module install puppetlabs/vcsrepo",
            "sudo puppet apply ~/bootstrap.pp",
        ]
    }

   connection {
        type = "ssh"
        agent = false
        private_key = "${file("${var.ec2_private_key}")}"
        user = "admin"
    }  
}