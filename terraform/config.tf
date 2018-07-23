provider "aws" {
    version = "~> 1.27.0"
    profile = "default"
    region = "${var.region}"
}