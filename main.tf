# Simple VPC for hospital system
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Locals for workspace-specific naming
locals {
  workspace_suffix = terraform.workspace == "ny-hospital" ? "ny" : terraform.workspace == "ca-hospital" ? "ca" : terraform.workspace
  region_name      = terraform.workspace == "ny-hospital" ? "NY" : terraform.workspace == "ca-hospital" ? "CA" : "UNKNOWN"
}

# Create VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "hospital-vpc-${local.workspace_suffix}"
  }
}

# App subnet
resource "aws_subnet" "app" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "app-subnet-${local.workspace_suffix}"
  }
}

# Database subnet
resource "aws_subnet" "database" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "database-subnet-${local.workspace_suffix}"
  }
}

# Public subnet for ALB (in different AZ)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = {
    Name = "public-subnet-1b-${local.workspace_suffix}"
  }
}

# Internet gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "hospital-igw-${local.workspace_suffix}"
  }
}

# Route table for app subnet
resource "aws_route_table" "app" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name = "app-route-table-${local.workspace_suffix}"
  }
}

resource "aws_route_table_association" "app" {
  subnet_id      = aws_subnet.app.id
  route_table_id = aws_route_table.app.id
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.app.id
}

# Security Groups
resource "aws_security_group" "app" {
  name        = "hospital-app-sg-${local.workspace_suffix}"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ip_ranges
  }

  ingress {
    from_port   = 80
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Grafana UI"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "app-security-group-${local.workspace_suffix}"
  }
}

resource "aws_security_group" "database" {
  name        = "hospital-db-sg-${local.workspace_suffix}"
  description = "Allow access only from app server"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.1.0/24"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "database-security-group-${local.workspace_suffix}"
  }
}

resource "aws_security_group" "alb" {
  name        = "hospital-alb-sg-${local.workspace_suffix}"
  description = "Allow HTTPS from anywhere"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "alb-sg-${local.workspace_suffix}"
  }
}

# EC2 Instances
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.app.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  key_name                    = "hospital-app-key"

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
  }

  tags = {
    Name = "hospital-app-server-${local.workspace_suffix}"
  }
}

resource "aws_instance" "database" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.database.id
  vpc_security_group_ids = [aws_security_group.database.id]
  key_name               = "hospital-app-key"

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y postgresql15-server
              postgresql-setup initdb
              systemctl start postgresql
              systemctl enable postgresql
              EOF

  tags = {
    Name     = "hospital-database-${local.workspace_suffix}"
    Type     = "Database"
    Hospital = var.hospital_name
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "hospital-alb-${local.workspace_suffix}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.app.id, aws_subnet.public.id]

  tags = {
    Name = "hospital-alb-${local.workspace_suffix}"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "hospital-app-tg-${local.workspace_suffix}"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 3
    interval            = 30
    path                = "/"
    port                = "8000"
    protocol            = "HTTP"
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_lb_target_group_attachment" "app" {
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app.id
  port             = 80
}

# WAF IP Set
resource "aws_wafv2_ip_set" "hospital_ips" {
  name               = "hospital-allowed-ips-${local.workspace_suffix}"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.allowed_ip_ranges
}

# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  name  = "hospital-waf-${local.workspace_suffix}"
  scope = "CLOUDFRONT"

  default_action {
    block {}
  }

  rule {
    name     = "AllowHospitalIPs"
    priority = 1

    action {
      allow {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.hospital_ips.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AllowHospitalIPs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "HospitalWAF"
    sampled_requests_enabled   = true
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  enabled         = true
  is_ipv6_enabled = false
  http_version    = "http2"
  price_class     = "PriceClass_All"
  web_acl_id      = aws_wafv2_web_acl.main.arn

  origin {
    domain_name = aws_lb.app.dns_name
    origin_id   = "hospital-alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "hospital-alb"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = true
      cookies {
        forward = "all"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

output "app_server_ip" {
  value = aws_instance.app.public_ip
}

output "database_private_ip" {
  value = aws_instance.database.private_ip
}

output "alb_dns" {
  value = aws_lb.app.dns_name
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.main.domain_name
}

output "app_sg_id" {
  value = aws_security_group.app.id
}

output "db_sg_id" {
  value = aws_security_group.database.id
}
