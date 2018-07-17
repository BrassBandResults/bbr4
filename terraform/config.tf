provider "aws" {
    version = "~> 1.26"
    profile = "default"
    region = "${var.region}"
}