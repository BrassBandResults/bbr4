variable "local_ip" {
    type = "string"
}

variable "region" {
    type = "string"
    default = "eu-west-2"
}

variable "prefix" {
    type = "string"
    default = "bbr"
}

variable "zones" {
    type = "map"
    default = {
      "eu-west-2" = "eu-west-2a"
    }
}

variable "ec2ami" {
    type = "map"
    default = {
        "eu-west-2" = "ami-ba0ae1dd"
    }
}

variable "keypair" {
    type = "map"
    default = {
        "eu-west-2" = "bbr-london"
    }
}

variable "ec2_private_key" {
    type = "string"
}

variable "db_password" {
    type = "string"
}

variable "web_ssh_password" {
    type = "string"
}