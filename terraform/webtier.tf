resource "aws_iam_role" "webtier-role" {
    name = "webtier-role"
    assume_role_policy = "${file("assume-role-policy.json")}"
}

resource "aws_iam_policy" "webtier-policy" {
    name = "webtier-policy"
    description = "IAM Policy to allow web tier to write to SNS"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "${aws_sns_topic.bbr-notify.arn}"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "webtier-policy-attach" {
    name = "webtier-policy-attachment"
    roles = ["${aws_iam_role.webtier-role.name}"]
    policy_arn = "${aws_iam_policy.webtier-policy.arn}"
}

resource "aws_iam_instance_profile" "webtier-profile" {
    name = "webtier-profile"
    role = "${aws_iam_role.webtier-role.name}"
}

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

data "template_file" "backports-sources-apt" {
    template = "deb http://ftp.debian.org/debian stretch-backports main"
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
        dbPasswordBbr = "${var.db_password_bbr}"
        djangoSecretKey = "${var.django_secret_key}"
        googleMapsKey = "${var.google_maps_key}"
        notificationTopicArn = "${aws_sns_topic.bbr-notify.arn}"
        prefix = "${var.prefix}"
	    region = "${var.region}"
        stripePublicDataKey = "${var.stripe_public_data_key}"
        stripeSecretKey = "${var.stripe_secret_key}"
        bitlyLogin = "${var.bitly_login}"
        bitlyApiKey = "${var.bitly_api_key}"
    }
}

resource "aws_instance" "bbr-web" {
    ami = "${lookup(var.ec2ami, var.region)}"
    instance_type = "t2.micro"
    key_name = "${lookup(var.keypair, var.region)}"
    subnet_id = "${aws_subnet.public-subnet.id}"
    private_ip = "10.0.7.7"
    iam_instance_profile = "${aws_iam_instance_profile.webtier-profile.name}"
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
        content = "${data.template_file.backports-sources-apt}"
        destination = "/etc/apt/source.list.d/stretch-backports.list"

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
