resource "aws_db_instance" "bbr-db" {
    allocated_storage = 20
    allow_major_version_upgrade = false
    apply_immediately = true
    auto_minor_version_upgrade = true
    backup_retention_period = 7
    backup_window = "05:37-06:37"
    storage_type = "gp2"
    engine = "postgres"
    engine_version = "10.4"
    final_snapshot_identifier = "${var.prefix}-snapshot-final"
    identifier = "bbr-db"
    instance_class = "db.t2.micro"
    name = "bbr"
    username = "bbradmin"
    password = "${var.db_password}"
    publicly_accessible = false
    db_subnet_group_name = "${aws_db_subnet_group.db-subnet-group.name}"
    multi_az = false
    skip_final_snapshot = false
    vpc_security_group_ids = ["${aws_security_group.db_traffic.id}"]
}

resource "aws_db_subnet_group" "db-subnet-group"{
    name = "db-subnet-group"
    subnet_ids = ["${aws_subnet.private-subnet.id}", "${aws_subnet.private-subnet-secondary.id}"]
}
