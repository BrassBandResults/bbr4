resource "aws_route53_zone" "bbr-com" {
  name = "brassbandresults.com"
}

resource "aws_route53_record" "bbr-com-mx" {
  zone_id = "${aws_route53_zone.bbr-com.zone_id}"
  name    = ""
  type    = "MX"
  
  records = [
    "10 ${var.mail_server_primary}",
    "20 ${var.mail_server_secondary}",
  ]
  
  ttl = "86400"
}

resource "aws_route53_record" "bbr-com-a" {
  zone_id = "${aws_route53_zone.bbr-com.zone_id}"
  name    = ""
  type    = "A"
  
  records = [
    "63.34.49.245",
  ]
  
  ttl = "86400"
}