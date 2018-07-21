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
        "eu-west-2" = "ami-b8b45ddf"
    }
}

variable "db_password" {
    type = "string"
    default = "ThisIsTheDefaultDatabasePassword947362"
}