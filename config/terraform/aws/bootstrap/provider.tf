provider "aws" {
  version = "~> 2.0"
  region  = "ca-central-1"
}

resource "aws_s3_bucket" "log_bucket" {
  bucket = join("",[var.storage_bucket,"-logs"])
  acl    = "log-delivery-write"
  #tfsec:ignore:AWS002
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket" "storage_bucket" {
  bucket = var.storage_bucket
  acl    = "private"
  logging {
    target_bucket = aws_s3_bucket.log_bucket.id
    target_prefix = "log/"
  }
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-lock"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    ("CostCentre") = "covidportal"
  }
}


resource "aws_route53_zone" "covidportal" {
  name = var.route53_zone_name

  tags = {
    ("CostCentre") = "CovidPortal"
  }
}
