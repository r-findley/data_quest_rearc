output "test_bucket_id" {
    value = aws_s3_bucket.this.id
}

output "test_bucket_domain_name" {
    value = aws_s3_bucket.this.bucket_domain_name
}

output "test_bucket_arn" {
    value = aws_s3_bucket.this.arn
}

output "test_queue_arn" {
    value = aws_sqs_queue.this.arn
}

output "test_queue_id" {
    value = aws_sqs_queue.this.id
}

output "deadletter_queue_id" {
    value = aws_sqs_queue.terraform_queue_deadletter.id
}

output "deadletter_queue_arn" {
    value = aws_sqs_queue.terraform_queue_deadletter.arn
}
