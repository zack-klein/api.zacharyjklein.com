terraform {

  backend "s3" {
    bucket = "zacharyjklein-state"
    key    = "state/api.zacharyjklein.com.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region  = "us-east-1"
  version = "~> 2.60"
}

# Instance module

module "instance" {
  source            = "github.com/zack-klein/ec2-instance"
  instance_name     = "api.zacharyjklein.com"
  user_data_path    = "./user-data.sh"
  vpc_id            = "vpc-792b4b03"
  subnets           = ["subnet-bc9fcee0", "subnet-21237746", "subnet-7b91c255"]
  ssh_public_key    = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCBIu48ryZCZZlufVF9AgjBrEmjau3Hmb20Aah75SYQTAhA5+9E5MuXJ1UwlDBXUPDIv/VFgu+/AmyT1kk1+8N9OE8I2kVcr8nAsFV7c7PNG60zxMXtCiCA8KgzQw/JeUceCmSZnGTCY5pgkXFvTAVaPtNywaEuKU9sICi+J+jm6WBk+IbX+GQYCJCTjGugbH0SOqivyBj/xiVgXQAdDKybvSQkWZqlERnfpbI0vSGEVqzlia+D54TlxaL5tnI76KoR6toWBmp81Y4JVHNAMW7LMerbQuor9gEUWWY1pdY/NikY9Sy1YMPOiYtAqbi/x3rm03tsr1mEAsu7o29g+oID"
  instance_profile  = aws_iam_instance_profile.profile.name
  public            = true
  target_group_arns = [aws_lb_target_group.tg.arn]
}

# IAM

resource "aws_iam_instance_profile" "profile" {
  name = "api.zacharyjklein.com"
  role = aws_iam_role.role.name
}

resource "aws_iam_role" "role" {
  name = "api.zacharyjklein.com"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "secretsmanager" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role_policy_attachment" "s3" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "billing" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSBillingReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "rds" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_role_policy_attachment" "dynamo" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "ecr" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

# Load balancer
resource "aws_lb" "lb" {
  internal           = false
  load_balancer_type = "application"
  subnets            = ["subnet-bc9fcee0", "subnet-21237746", "subnet-7b91c255"]
}


resource "aws_lb_target_group" "tg" {
  port     = 443
  protocol = "HTTP"
  vpc_id   = "vpc-792b4b03"
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.lb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = data.aws_acm_certificate.cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

# Route 53

data "aws_route53_zone" "zone" {
  name         = "zacharyjklein.com."
  private_zone = false
}

data "aws_acm_certificate" "cert" {
  domain      = "zacharyjklein.com"
  most_recent = true
}


resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = "api.zacharyjklein.com"
  type    = "A"

  alias {
    name                   = aws_lb.lb.dns_name
    zone_id                = aws_lb.lb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_ecr_repository" "repository" {
  name = "api.zacharyjklein.com"
}
