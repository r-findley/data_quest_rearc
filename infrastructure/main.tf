provider "aws" {
  alias   = "management"
  region  = var.region
  profile = "management"
}

provider "aws" {
  alias   = "sandbox"
  region  = var.region
  profile = "sandbox"
}

module "sandbox_role" {
  source                = "./modules/sandbox_role"
  providers             = { aws = aws.sandbox }
  management_account_id = "542403648992"
}

module "management_group" {
  source             = "./modules/management_role"
  providers          = { aws = aws.management }
  sandbox_account_id = "856558477169"
}

resource "aws_s3_bucket" "this" {
  provider = aws.sandbox
  bucket   = "rearc-test-bucket-${random_id.suffix.hex}"

  tags = {
    Name        = "rearc-data-quest"
    Environment = "Dev"
  }
}

resource "aws_sqs_queue" "this" {
  provider                  = aws.sandbox
  name                      = "rearc-sqs-queue-${random_id.suffix.hex}"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.terraform_queue_deadletter.arn
    maxReceiveCount     = 4
  })

  tags = {
    Environment = "Dev"
  }
}

resource "aws_sqs_queue" "terraform_queue_deadletter" {
  provider = aws.sandbox
  name     = "rearc-deadletter-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 4
}