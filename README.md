# Static Website Deployer using Boto3

## Overview

A production-style Python automation project that deploys a static
website to Amazon S3 using **Boto3**. This project is built in phases to
progressively introduce AWS concepts and best practices.

### Phase 1 (Completed)

-   Create an S3 bucket
-   Generate unique bucket names
-   Validate bucket names
-   Configure logging
-   Disable bucket-level Block Public Access
-   Enable Static Website Hosting
-   Recursively upload website files
-   Automatically detect and set MIME types
-   Apply a public-read bucket policy
-   Print the S3 website endpoint

### Upcoming Phases

-   **Phase 2:** Create an Amazon CloudFront distribution
-   **Phase 3:** Add ACM certificate and custom domain
-   **Phase 4:** Cleanup script to delete all created AWS resources

------------------------------------------------------------------------

# Architecture

``` text
Python CLI
     │
     ▼
   Boto3
     │
     ▼
 Amazon S3
     │
     ▼
Static Website
```

------------------------------------------------------------------------

# Tech Stack

-   Python 3.10+
-   Boto3
-   Botocore
-   AWS CLI
-   Amazon S3
-   pathlib
-   logging
-   mimetypes
-   uuid

------------------------------------------------------------------------

# Project Structure

``` text
static-site-deployer/
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── validators.py
│   ├── s3_manager.py
│   ├── uploader.py
│   └── policy.py
│
├── website/
│   ├── index.html
│   ├── style.css
│   ├── script.js
|   |images/
|    ├── logo.png
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

# Prerequisites

-   AWS Account
-   IAM User with S3 permissions
-   AWS CLI installed and configured
-   Python virtual environment

Configure AWS credentials:

``` bash
aws configure
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# Running the Project

``` bash
python main.py
```

The application will:

1.  Generate a unique bucket name.
2.  Create an S3 bucket.
3.  Disable bucket-level Block Public Access.
4.  Enable static website hosting.
5.  Upload website assets recursively.
6.  Apply a public-read bucket policy.
7.  Print the website endpoint.

------------------------------------------------------------------------

# AWS Services Used

-   Amazon S3
-   AWS IAM
-   AWS CLI

------------------------------------------------------------------------

# Python Concepts Demonstrated

-   Object-Oriented Programming
-   Exception Handling
-   Logging
-   pathlib
-   UUID generation
-   MIME type detection
-   JSON serialization

------------------------------------------------------------------------

# Security Notes

-   Never hardcode AWS credentials.
-   Use AWS CLI profiles or IAM roles.
-   Follow the Principle of Least Privilege.
-   Do not commit `.env`, credentials, or virtual environments.

------------------------------------------------------------------------

# Future Improvements

-   CloudFront distribution
-   HTTPS with ACM
-   Custom domain
-   Route 53 integration
-   Automatic cleanup
-   CLI arguments with `argparse`
-   Unit tests
-   GitHub Actions CI

------------------------------------------------------------------------

# Learning Outcomes

After completing all phases, you'll understand:

-   Amazon S3 internals
-   Static website hosting
-   Bucket policies
-   Resource-based permissions
-   Boto3 automation
-   CloudFront
-   ACM
-   Route 53
-   Infrastructure automation with Python

------------------------------------------------------------------------

# License

This project is intended for learning and portfolio purposes.
