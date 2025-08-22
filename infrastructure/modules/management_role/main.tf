resource "aws_iam_group" "developers" {
  name = "Developers"
}

resource "aws_iam_policy" "assume_sandbox_role" {
  name        = "AssumeSandboxDeveloperRole"
  description = "Allow developers to assume SandboxDeveloperRole in Sandbox account"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sts:AssumeRole",
        Resource = "arn:aws:iam::${var.sandbox_account_id}:role/SandboxDeveloperRole"
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "developers_assume_sandbox" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.assume_sandbox_role.arn
}


