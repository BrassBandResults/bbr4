provider "aws" {
    version = "~> 1.27.0"
    profile = "default"
    region = "${var.region}"
}

provider "aws" {
    alias = "london"
    region = "eu-west-2"
}

terraform {
    backend "s3" {
        bucket = "bbrie-terraform-state"
        key = "tfstate"
        region = "eu-west-1" 
    }
}