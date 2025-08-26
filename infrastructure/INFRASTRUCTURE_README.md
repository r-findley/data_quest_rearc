# Infrastructure

## Table of Contents

1. [Technolody](#technology)
2. [Resources](#resources)
    - [Cloudwatch Event](#cloudwatch-event)
    - [Lambda Functions](#lambda-functions)
    - [Permissions/Policies](#permissionspolicies)
    - [Random IDs](#random-ids)
    - [Roles](#roles)
    - [S3 Bucket](#s3-bucket)
    - [SQS](#sqs)
3. [Notes](#notes)

## Technology

All resources are being built using Terraform within AWS.

## Resources

### Cloudwatch Event

A cloudwatch event was set up to run the Lamba One function at 130p Pacific time each day.

### Lambda Functions

Lambda functions are being used to handle the gathering of data as well as processing that data to perform analytics.

### Permissions/Policies

Permissions and policies were added to handle access to the functions and buckets.

### Random IDs

Random IDs are being created to append to the end of resource names to ensure unique values are being used each time resources are created.

### Roles

A sandbox role and a management role are being created using modules to allow access to the various accounts.

### S3 Bucket

An S3 bucket is being created to house the data files that were gathered in parts 1 and 2 of the data quest. The bucket has a private access policy.

### SQS

Two separate queues are set up within this project, one being the standard queue and another being a deadletter queue.

## Notes

The [Terraform documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) was used to review resources, attributes, and credential setting.

In addition, ChatGPT was used to assist in troubleshooting in the initial setup of my configuration. The suggestions from ChatGPT were verified within the Terraform documentation before being applied to my project.
