provider "aws" {
  region = var.region
}

provider "random" {
}

provider "template" {
}

terraform {
  backend "s3" {
    bucket = "covid-portal-terraform"
    key    = "aws/backend/default.tfstate"
    region = "ca-central-1"

    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
