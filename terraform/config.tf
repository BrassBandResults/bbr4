provider "aws" {
    version = "~> 1.27.0"
    profile = "default"
    region = "${var.region}"
}

terraform {
    backend "s3" {
        bucket = "bbr-terraform-state"
        key = "tfstate"
        region = "eu-west-2" 
    }
}