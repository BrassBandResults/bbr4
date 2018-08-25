variable "home_ip" {
    type = "string"
}
 
variable "work_ip" {
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

variable "zones_secondary" {
    type = "map"
    default = {
      "eu-west-2" = "eu-west-2b"
    }
}

variable "ec2ami" {
    type = "map"
    default = {
        "eu-west-2" = "ami-02d7859cef54f67bb"
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

variable "db_password_bbr" {
    type = "string"
}

variable "web_ssh_password" {
    type = "string"
}

variable "djangoSecretKey" {
    type = "string"
    default = "ABC123"
}

variable "googleMapsKey" {
    type = "string"
    default = "ABC123"
}