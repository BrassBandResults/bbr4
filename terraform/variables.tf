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