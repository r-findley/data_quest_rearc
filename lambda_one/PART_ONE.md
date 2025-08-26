# Challenge Part One

## Description

Part one of the challenge requires obtaining data from a bls.gov website and loading this to an S3 bucket. In addition, the data should be updated or removed if the data at the bls.gov website is found to be changed.

## Process

The process for Part One consists of multipe helper functions. These functions perform actions such as:

- Adding metadata to an S3 object
- Listing the objects in the S3 bucket
- Determining which objects should be removed/updated based on whether the metadata matches the information on the bls.gov website.

The lambda handler function utilizes the helper functions to determine what item(s) need to be updated, removed, or added.

## Next Steps

Additional development could be performed to check the hashes of the documents and include that information in the metadata. Then, if the file size and/or last modified date were different between the object(s) in the s3 bucket and the equivalently named object on the bls.gov website, the hash could be checked to determine if the document did in fact change.

Data validation could also be completed on the metadata, confirming that there is in fact a date modified, file size, link, etc. to ensure the files were not processed unless they contained these items.
