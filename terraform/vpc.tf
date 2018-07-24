resource "aws_vpc" "bbr-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags {
    Name = "bbr-vpc"
  }
}

resource "aws_subnet" "public-subnet" {
  vpc_id = "${aws_vpc.bbr-vpc.id}"
  cidr_block = "10.0.7.0/24"
  availability_zone = "${lookup(var.zones, var.region)}"
  map_public_ip_on_launch = true

  tags {
    Name = "BBR Web Public Subnet"
  }
}

# Define the private subnet
resource "aws_subnet" "private-subnet" {
  vpc_id = "${aws_vpc.bbr-vpc.id}"
  cidr_block = "10.0.1.0/24"
  availability_zone = "${lookup(var.zones, var.region)}"

  tags {
    Name = "BBR DB Private Subnet"
  }
}

# Secondary subnet required for RDS database, not actually used?
resource "aws_subnet" "private-subnet-secondary" {
  vpc_id = "${aws_vpc.bbr-vpc.id}"
  cidr_block = "10.0.2.0/24"
  availability_zone = "${lookup(var.zones_secondary, var.region)}"

  tags {
    Name = "BBR DB Secondary Private Subnet"
  }
}

resource "aws_internet_gateway" "bbr-public-gateway" {
  vpc_id = "${aws_vpc.bbr-vpc.id}"

  tags {
    Name = "BBR VPC Internet Gateway"
  }
}

resource "aws_route_table" "web-public-routetable" {
  vpc_id = "${aws_vpc.bbr-vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.bbr-public-gateway.id}"
  }

  tags {
    Name = "Public Subnet Route Table"
  }
}

# Assign the route table to the public Subnet
resource "aws_route_table_association" "web-rta" {
  subnet_id = "${aws_subnet.public-subnet.id}"
  route_table_id = "${aws_route_table.web-public-routetable.id}"
}