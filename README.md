# Rearc Data Quest

## Table of Contents

1. [Description](#description)
2. [Technology](#technology)
3. [Components](#components)
    1. [Challenge Part One - Data from BLS Website](#challenge-part-one---data-from-bls-website)
    2. [Challenge Part Two - Data from DataUSA Website](#challenge-part-two---data-from-datausa-website)
    3. [Challenge Part Three - Data Analytics](#challenge-part-three---data-analytics)
    4. [Challenge Part Four - Infrastructure as Code](#challenge-part-four---infrastructure-as-code)
4. [Next Steps](#next-steps)
5. [Disclaimer](#disclaimer)

## Description

This project resembles my attempt to solve the Rearc Data Quest.
 There are four parts to the quest:

1. Access data from a BLS website and load this to an S3 bucket, mirroring the website.
2. Access data from an API and store it as a JSON file in an S3 bucket.
3. Perform data analytics on the data retrieved in steps 1 and 2.
4. Create Infrastructure as Code to automate this pipeline.

## Technology

The primary technologies for this project will by Python, Terraform, and AWS.

## Components

### Challenge Part One - Data from BLS Website

The first part of the challenge included obtaining data from a bls.gov website
 and loading this data to an s3 bucket. The data in the s3 bucket should mirror
 the data that is present on the bls.gov website. This includes deleting files
 from the s3 bucket that no longer exist on the bls.gov website as well as
 updating the files in the s3 bucket if they were updated on the bls.gov website.

This work was accomplished by building functionality to retrieve information about
the files that are on the website and attaching that to the s3 object for each file.
In addition, the files are downloaded and stored in the s3 bucket under a prefix
of bls_data/. This allows for syncing the files in that specific prefic without
impacting other files stored within the bucket. The sync function compares the
file size and date last modified on the bls.gov website with the information
about each file stored in the s3 bucket. If any files need to be updated, the
file name is added to a list of files that is used by the main lambda function
to begin uploading the data from the bls.gov website. If a file no longer exists
on the bls.gov website, the function will remove the file and not suggest it needs
to be uploaded again.

Upon reading of the objects in the s3 bucket, a set of pre-signed URLs is created.
These are used to allow access to each of the items from within the s3 bucket.
An index.html file is generated and written to the s3 bucket, with a signed URL
created for this to share with others.

The work to complete this part of the challenge is deployed as part of an AWS
Lambda function. This function is triggered daily by a CloudWatch Event.

### Challenge Part Two - Data from DataUSA Website

The second part of the challenge includes obtaining data from a datausa.io site
and loading this to a JSON file in the s3 bucket. This data is loaded using a
prefix of datausa/ to allow for separation from the bls.gov data that is synced
on a daily basis.

Once the data file is loaded, a message is then sent to an SQS queue indicating
that new data has been uploaded. This is used to trigger a second Lambda function
that performs the data analytics in
[Part Three](#challenge-part-three---data-analytics) of the challenge.

### Challenge Part Three - Data Analytics

#### Jupyter Notebook Analysis

The initial analysis was completed within a [Jupyter Notebook](/analytics.ipynb).
The data was obtained from the s3 bucket and converted into dataframes for use
in the analytics work. Tables were built as instructed to display the values
requested.

#### Lambda Function

A Lambda function was built that performs the analytics work that occurred
within the [Jupyter Notebook](/analytics.ipynb) file. This data is logged
to CloudWatch using the built-in Python logger. The function is started
by an SQS message sent by the lambda function from parts one and two.

Please note the following instructions to properly build the pandas and
numpy libraries:

Within the lambda_two directory, the ```pip install -t . pandas``` command
was run in order to install pandas directly into the directory for the
lambda function. Then, whl packages were downloaded from pypi for both
pandas and numpy for Python version 3.12 using the manylinux version of
the whl files. The pandas, numpy, and *.dist-info directories were removed,
and the whl files were unzipped. The whl files, __pycache__ and*.dist-info
items were removed, and a zip.zip was created of the lambda_two directory.
This zip is used in building the Lambda function.

### Challenge Part Four - Infrastructure as Code

The last part of the challenge includes writing infrastructure as code
to automate the deployment of the resources necessary for this pipeline to run.

This work was done with Terraform utilizing the AWS provider. Modules were created
to handle the roles for the management and sandbox roles within my AWS account.
Other resources utilized include:

- Lambda Functions, roles, and policies
- SQS queues, roles, and policies
- Random module to result in random integers to use in resource names
- CloudWatch event to trigger the first Lambda function

## Instructions To Deploy

In order to run this application/code, please follow the below.

1. Clone the repository and build a virtual environment using the requirements.txt
file from either the lambda_one or lambda_two directory.
2. Log into AWS. This project is set up to use a management account and a sandbox
account. The account IDs are set up in the [main.tf](./infrastructure/main.tf) file.
You can switch these to match your accounts.
3. From the root directory, run the following within a terminal:

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

Prior to running the ```terraform apply``` command be sure to review the output
of the ```terraform plan```.

If you want to remove the assets, run the ```terraform destroy``` command.

## Next Steps

Additional work, design, and structuring of this project is possible. Some ideas
to improve the project include:

- Adding data validation when loading data to the s3 bucket as well as
when downloading data for the data analytics work.
- Creating a dashboard-style website to display the analytics work utilizing
graphing libraries.
- Including hashing of the documents in the bls.gov website to confirm the
data has in fact changed if metadata (size, date modified, name) have changed.
- Additional utilization of Terraform modules to better organize the infrastructure.
- Improvement of the shell script to create layers to generate these dynamically
for each layer necessary.
- Automation of deployment when code is committed to the main branch in GitHub.

## Disclaimer

Please note that AI was used during this work. The use of AI was limited to
assistance with processing error messages, troubleshooting those errors, and
as a more powerful search. For example, the configuration of Terraform on my
computer needed to be completed in order to do this project. I utilized
ChatGPT to assist me in troubleshooting access errors I was receiving during
that setup. This included helping me solve the role requirements necessary
in AWS in order to perform the initial builds.
