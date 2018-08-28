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

variable "django_secret_key" {
    type = "string"
}

variable "google_maps_key" {
    type = "string"
}

variable "stripe_public_data_key" {
    type = "string"
}

variable "stripe_secret_key" {
    type = "string"
}

variable "bitly_login" {
    type = "string"
}

variable "bitly_api_key" {
    type = "string"
}

variable "tweepy_consumer_token" {
    type = "string"
}

variable "tweepy_consumer_secret" {
    type = "string"
}

variable "tweepy_access_token_key" {
    type = "string"
}

variable "tweepy_access_token_secret" {
    type = "string"
}
