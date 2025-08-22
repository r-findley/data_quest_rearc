resource "aws_iam_role" "sandbox_developer_role" {
  name = "SandboxDeveloperRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${var.management_account_id}:root"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sandbox_developer_poweruser" {
  role       = aws_iam_role.sandbox_developer_role.name
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

