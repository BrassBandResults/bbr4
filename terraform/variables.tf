variable "home_ip" {
    type = "string"
}
 
variable "work_ip" {
    type = "string"
}

variable "mail_server_primary" {
    type = "string"
}

variable "mail_server_secondary" {
    type = "string"
}

variable "region" {
    type = "string"
    default = "eu-west-1"
}

variable "prefix" {
    type = "string"
    default = "bbrie"
}

variable "zones" {
    type = "map"
    default = {
      "eu-west-1" = "eu-west-1a"
    }
}

variable "zones_secondary" {
    type = "map"
    default = {
      "eu-west-1" = "eu-west-1b"
    }
}

variable "ec2ami" {
    type = "map"
    default = {
        "eu-west-1" = "ami-0636e459be80b841e"
    }
}

variable "keypair" {
    type = "map"
    default = {
        "eu-west-1" = "bbr-ireland"
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

variable "mapbox_access_token" {
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
