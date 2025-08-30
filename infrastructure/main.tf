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

resource "aws_s3_bucket" "s3_bucket" {
  provider = aws.sandbox
  bucket   = "rearc-test-bucket-${random_id.suffix.hex}"

  tags = {
    Name        = "rearc-data-quest"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_policy" "allow_jupyter_user_read" {
  provider = aws.sandbox
  bucket   = aws_s3_bucket.s3_bucket.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::542403648992:user/jupyter_user"
        },
        Action   = ["s3:GetObject"],
        Resource = "${aws_s3_bucket.s3_bucket.arn}/*"
      }
    ]
  })
}


resource "aws_sqs_queue" "sqs_queue" {
  provider                  = aws.sandbox
  name                      = "rearc-sqs-queue-${random_id.suffix.hex}"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  visibility_timeout_seconds = 60
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

data "aws_iam_policy_document" "send_message" {
  provider = aws.sandbox
  statement {
    sid    = "First"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.sqs_queue.arn]

  }
}

resource "aws_sqs_queue_policy" "send_message_policy" {
  provider  = aws.sandbox
  queue_url = aws_sqs_queue.sqs_queue.id
  policy    = data.aws_iam_policy_document.send_message.json
}

resource "random_id" "suffix" {
  byte_length = 4
}

data "archive_file" "lambda_one_payload" {
  type       = "zip"
  source_dir = var.lambda_one_src_dir
  excludes = [
    "venv",
    "__pycache__"
  ]
  output_path = "${var.lambda_one_src_dir}/payload.zip"
}

data "archive_file" "lambda_two_payload" {
  type       = "zip"
  source_dir = var.lambda_two_src_dir
  excludes = [
    "venv",
    "__pycache__"
  ]
  output_path = "${var.lambda_two_src_dir}/payload.zip"
}

resource "aws_iam_role" "lambda_exec" {
  provider = aws.sandbox
  name     = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_basic" {
  provider   = aws.sandbox
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_layer_version" "shared_dependencies" {
  provider            = aws.sandbox
  filename            = "${path.module}/../layer.zip"
  layer_name          = "shared_dependencies"
  compatible_runtimes = ["python3.12"]
  description         = "Shared dependencies for both lambdas"
}

resource "aws_lambda_function" "lambda_one" {
  provider      = aws.sandbox
  function_name = "lambda_one"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_one_handler"
  runtime       = "python3.12"
  timeout       = 60

  filename         = data.archive_file.lambda_one_payload.output_path
  source_code_hash = data.archive_file.lambda_one_payload.output_base64sha256

  layers = [aws_lambda_layer_version.shared_dependencies.arn]

  environment {
    variables = {
      BUCKET_NAME   = aws_s3_bucket.s3_bucket.id
      SQS_QUEUE_URL = aws_sqs_queue.sqs_queue.id
    }
  }
}

resource "aws_lambda_function" "lambda_two" {
  provider      = aws.sandbox
  function_name = "lambda_two"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_two_handler"
  runtime       = "python3.12"
  timeout       = 60

  filename         = "${path.module}/../lambda_two/zip.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda_two/zip.zip")

  layers = [aws_lambda_layer_version.shared_dependencies.arn]

  environment {
    variables = {
      BUCKET_NAME   = aws_s3_bucket.s3_bucket.id
      SQS_QUEUE_URL = aws_sqs_queue.sqs_queue.id
    }
  }
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  provider            = aws.sandbox
  name                = "lambda_one_schedule"
  description         = "Run Lambda every day at 12 PM PST"
  schedule_expression = "cron(30 20 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  provider  = aws.sandbox
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "lambda_one_target"
  arn       = aws_lambda_function.lambda_one.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  provider      = aws.sandbox
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_one.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

resource "aws_iam_role_policy" "lambda_s3_access" {
  provider = aws.sandbox
  name     = "lambda_s3_access"
  role     = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:ListBucket",
          "s3:GetObject",
          "s3:HeadObject",
          "s3:DeleteObject"
        ],
        Resource = [
          "${aws_s3_bucket.s3_bucket.arn}",
          "${aws_s3_bucket.s3_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_event_source_mapping" "sqs_mapping" {
  provider         = aws.sandbox
  event_source_arn = aws_sqs_queue.sqs_queue.arn
  function_name    = aws_lambda_function.lambda_two.arn
  batch_size       = 10
  enabled          = true
}

resource "aws_iam_role_policy" "lambda_sqs_access" {
  provider = aws.sandbox
  name     = "lambda_sqs_access"
  role     = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.sqs_queue.arn
      }
    ]
  })
}