# Infrastructure

## Table of Contents

1. [Technolody](#technology)
2. [Resources](#resources)
    - [S3 Bucket](#s3-bucket)
    - [Roles](#roles)
    - [SQS](#sqs)
    - [Random IDs](#random-ids)
3. [Notes](#notes)

## Technology

All resources are being built using Terraform within AWS.

## Resources

### S3 Bucket

An S3 bucket is being created to house the data files that were gathered in parts 1 and 2 of the data quest. The bucket has a private access policy.

### Roles

A sandbox role and a management role are being created using modules to allow access to the various accounts.

### SQS

Two separate queues are set up within this project, one being the standard queue and another being a deadletter queue.

### Random IDs

Random IDs are being created to append to the end of resource names to ensure unique values are being used each time resources are created.

## Notes

The [Terraform documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) was used to review resources, attributes, and credential setting.

In addition, ChatGPT was used to assist in troubleshooting in the initial setup of my configuration. The suggestions from ChatGPT were verified within the Terraform documentation before being applied to my project.
