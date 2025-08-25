output "test_bucket_id" {
  value = aws_s3_bucket.s3_bucket.id
}

output "test_bucket_domain_name" {
  value = aws_s3_bucket.s3_bucket.bucket_domain_name
}

output "test_bucket_arn" {
  value = aws_s3_bucket.s3_bucket.arn
}

output "test_queue_arn" {
  value = aws_sqs_queue.sqs_queue.arn
}

output "test_queue_id" {
  value = aws_sqs_queue.sqs_queue.id
}

output "deadletter_queue_id" {
  value = aws_sqs_queue.terraform_queue_deadletter.id
}

output "deadletter_queue_arn" {
  value = aws_sqs_queue.terraform_queue_deadletter.arn
}
