variable "region" {
  description = "Region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "lambda_one_src_dir" {
  default = "../lambda_one"
}