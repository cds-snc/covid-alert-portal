provider "aws" {
  version = "~> 2.0"
  region  = var.region
}

provider "random" {
  version = "~> 2.3"
}

provider "template" {
  version = "~> 2.1"

}
terraform {
  required_version = "> 0.12.0"
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
