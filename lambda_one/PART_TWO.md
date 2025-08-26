# Challenge Part Two

## Description

Part two of the challenge gets data from the DataUSA datasets and writes this to an s3 bucket under the prefix datausa/.

The work to write an SQS message to a queue for triggering the 2nd lambda function has been included in this part as well.

## Process

This work is performed with a simple GET request to obtain the data. A function was written to write messages to the SQS queue that was created with the Terraform files.

## Next Steps

Additional research could assist in determining why this dataset returns a 443 error without using the verify=False parameter to the requests.get method. The function has been set to use this parameter at this time to obtain the data for the purposes of this sample project.
