# Static Website Deployer using Boto3

A Python-based AWS automation project that deploys a static website to Amazon S3 and distributes it through Amazon CloudFront using **Boto3**.

The project was built in phases to learn AWS and Boto3 concepts through practical implementation.

> **Current implementation note:** The working deployment uses the CloudFront-provided `*.cloudfront.net` URL. No custom domain is required. ACM and Route 53 support is implemented as optional architecture/code for learning. **CloudFront Origin Access Control (OAC) is not implemented or used by the current deployment.**

---

## Project Goals

- Automate S3 static website deployment with Boto3
- Learn S3 bucket and object management
- Learn CloudFront distribution automation
- Understand ACM certificate and DNS validation concepts
- Understand Route 53 DNS concepts
- Track created AWS resources
- Build safe, idempotent AWS cleanup automation
- Practice modular Python/OOP design
- Maintain the project through incremental Git commits

---

# Architecture

## Current Working Architecture

```text
                    Python CLI
                        │
                        ▼
                     Boto3
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
        Amazon S3             CloudFront
             │                     │
             └─────── Origin ──────┘
                                   │
                                   ▼
                         CloudFront HTTPS URL
```

The deployed website is accessed through:

```text
https://dxxxxxxxxxxxx.cloudfront.net
```

## Optional Custom-Domain Architecture

When a real domain is available, the intended architecture is:

```text
                    User
                     │
                     ▼
                  Route 53
                     │
                 DNS Record
                     │
                     ▼
                CloudFront
                     │
              ACM Certificate
                     │
                     ▼
                    S3
```

This custom-domain path is not required for the current project.

---

# Project Phases

## Phase 1 — S3 Static Website Hosting

### Completed

- Generate unique S3 bucket names
- Validate bucket names
- Create S3 bucket
- Configure logging
- Disable bucket-level Block Public Access as required by the current architecture
- Enable S3 static website hosting
- Recursively upload website files
- Automatically detect MIME types
- Apply a public-read bucket policy
- Print the S3 website endpoint
- Track deployment resources in local state

Architecture:

```text
Python
  │
  ▼
Boto3
  │
  ▼
S3 Bucket
  │
  ├── index.html
  ├── style.css
  ├── script.js
  └── images/
```

---

# Phase 2 — CloudFront

### Completed

- CloudFront distribution creation
- S3 origin configuration
- Default root object
- Viewer protocol policy
- Cache behavior configuration
- CloudFront deployment monitoring
- Waiting for distribution deployment
- Cache invalidation
- Distribution inspection
- Custom-domain configuration methods

Architecture:

```text
             Browser
                │
                ▼
          CloudFront
                │
                ▼
          S3 Website
```

### Important OAC Note

Origin Access Control (OAC) was investigated during the learning process, but the current project **does not create, attach, or use OAC**.

The current S3 origin uses the static website architecture.

A future enhancement could migrate the project to:

```text
CloudFront
    │
    ▼
   OAC
    │
    ▼
Private S3 Bucket
```

---

# Phase 3 — ACM + Custom Domain Architecture

### ACM

Implemented:

- ACM client configuration
- Certificate listing
- Certificate inspection
- Certificate status handling
- Certificate lifecycle concepts
- DNS validation record extraction
- Certificate deletion
- CloudFront certificate configuration support

For CloudFront viewer certificates, ACM certificates must be managed in:

```text
us-east-1
```

### DNS Validation

ACM DNS validation uses a CNAME similar to:

```text
_acm-validation.example.com
        │
        ▼
_xyz.acm-validations.aws
```

The validation record proves domain ownership and can support certificate renewal.

### Route 53

Implemented:

- Hosted zone listing
- Hosted zone inspection
- Hosted zone lookup
- ACM validation record construction
- CloudFront Alias A record construction
- DNS record deletion support
- Hosted zone deletion support

### Current Limitation

No custom domain is configured.

Therefore the current deployment uses:

```text
https://<distribution-id>.cloudfront.net
```

No Route 53 hosted zone, DNS record, or ACM certificate is created by the current deployment.

---

# Phase 4 — AWS Resource Cleanup

### Completed

- Cleanup manager
- Dry-run mode
- S3 object deletion
- S3 bucket deletion
- CloudFront distribution disabling
- CloudFront deployment waiting
- CloudFront distribution deletion
- ACM certificate deletion
- Route 53 cleanup support
- Deployment state cleanup
- Idempotent deletion handling
- Explicit destructive confirmation
- Dependency-aware cleanup orchestration

## Cleanup Architecture

```text
cleanup.py
     │
     ├── Default mode
     │       │
     │       ▼
     │    Dry Run
     │
     └── --execute
             │
             ▼
        Confirmation
             │
             ▼
       CleanupManager
             │
       ┌─────┼─────────────┐
       ▼     ▼             ▼
 CloudFront ACM          Route 53
       │
       ▼
      S3
       │
       ▼
 Clear State
```

## Cleanup Order

```text
1. Load deployment state
2. Disable CloudFront
3. Wait for CloudFront deployment
4. Delete CloudFront distribution
5. Delete ACM certificate if present
6. Delete Route 53 resources if present
7. Delete S3 objects
8. Delete S3 bucket
9. Clear deployment state
```

Resources that were never created are skipped.

---

# Safe Cleanup Design

The cleanup system does not blindly delete AWS resources.

It uses deployment state to identify resources created by this project.

Example:

```json
{
    "bucket_name": "static-site-example",
    "distribution_id": "EXAMPLE123",
    "cloudfront_domain": "dexample.cloudfront.net"
}
```

The principle is:

```text
Project State
     │
     ▼
Resources created by this deployment
     │
     ▼
Cleanup only those resources
```

---

# Dry Run

Run:

```bash
python cleanup.py
```

This does not delete anything.

It displays the resources currently tracked by the deployment state.

Example:

```text
========== CLEANUP DRY RUN ==========

bucket_name: static-site-example
distribution_id: EXAMPLE123
cloudfront_domain: dexample.cloudfront.net
certificate_arn: None
hosted_zone_id: None

No AWS resources were deleted.
```

# Execute Cleanup

When intentionally ready to remove the project's AWS infrastructure:

```bash
python cleanup.py --execute
```

The script requires explicit confirmation before deletion.

```text
WARNING: This will delete AWS resources
created by this project.

Type 'DELETE' to continue:
```

> **Warning:** `--execute` is destructive. Always inspect the dry-run output first.

---

# Idempotency

Cleanup operations are designed to handle resources that are already absent.

```text
First cleanup
    │
    ▼
Resource exists
    │
    ▼
Delete
    │
    ▼
Success
```

Running cleanup again:

```text
Second cleanup
    │
    ▼
Resource doesn't exist
    │
    ▼
Treat as already deleted
    │
    ▼
Continue
```

This is an important infrastructure automation principle.

---

# Project Structure

```text
static-site-deployer/
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── validators.py
│   ├── s3_manager.py
│   ├── cloudfront_manager.py
│   ├── acm_manager.py
│   ├── route53_manager.py
│   ├── cleanup_manager.py
│   ├── state_manager.py
│   ├── uploader.py
│   └── policy.py
│
├── tests/
│   ├── test_acm.py
│   ├── test_route53.py
│   ├── test_route53_records.py
│   └── test_state_cleanup.py
│
├── website/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
│       └── logo.png
│
├── main.py
├── cleanup.py
├── requirements.txt
├── README.md
├── .gitignore
└── deployment_state.json
```

> `deployment_state.json` should be excluded from Git if it contains deployment-specific local state.

---

# Main Components

## `main.py`

Application entry point that starts the deployment process.

## `s3_manager.py`

Handles S3 bucket creation, configuration, inspection, and deletion.

## `uploader.py`

Handles recursive website discovery, MIME type detection, and object uploads.

## `policy.py`

Generates and applies the S3 bucket policy used by the current static website architecture.

## `cloudfront_manager.py`

Handles distribution creation, configuration, inspection, deployment waiting, cache invalidation, custom-domain configuration, disabling, and deletion.

## `acm_manager.py`

Handles ACM client operations, certificate requests/inspection, validation information, lifecycle operations, and certificate deletion.

## `route53_manager.py`

Handles hosted-zone inspection, DNS record construction, ACM validation record construction, CloudFront Alias record construction, DNS record deletion, and hosted-zone deletion.

## `cleanup_manager.py`

Orchestrates dependency-aware AWS resource cleanup.

## `state_manager.py`

Maintains local deployment state so cleanup can identify resources created by the project.

---

# Tech Stack

### Programming

- Python 3.10+
- Object-Oriented Programming
- Exception Handling
- Logging
- JSON
- pathlib
- uuid
- mimetypes
- argparse

### AWS

- Amazon S3
- Amazon CloudFront
- AWS Certificate Manager
- Amazon Route 53
- AWS IAM

### SDK / Tools

- Boto3
- Botocore
- AWS CLI
- Git
- GitHub

---

# Prerequisites

- Python 3.10+
- AWS account
- AWS CLI
- IAM identity with required permissions
- Git

Configure AWS credentials:

```bash
aws configure
```

Verify:

```bash
aws sts get-caller-identity
```

---

# Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd static-site-deployer
```

Create a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Deploy

Run:

```bash
python main.py
```

The application will:

1. Generate a unique bucket name.
2. Validate the name.
3. Create the S3 bucket.
4. Configure static website hosting.
5. Configure the required public-access settings for the current architecture.
6. Upload website assets recursively.
7. Detect MIME types.
8. Apply the bucket policy.
9. Create/configure CloudFront.
10. Wait for CloudFront deployment.
11. Perform cache invalidation where configured.
12. Save deployment state.
13. Display the CloudFront URL.

---

# Cleanup

Preview:

```bash
python cleanup.py
```

Execute:

```bash
python cleanup.py --execute
```

Review the dry run before executing the destructive command.

---

# AWS Permissions

Required permissions depend on which phase is being used.

### S3

```text
s3:CreateBucket
s3:DeleteBucket
s3:ListBucket
s3:PutObject
s3:DeleteObject
s3:DeleteObjects
s3:GetBucketPolicy
s3:PutBucketPolicy
s3:PutBucketWebsite
s3:PutPublicAccessBlock
```

### CloudFront

```text
cloudfront:CreateDistribution
cloudfront:GetDistribution
cloudfront:GetDistributionConfig
cloudfront:UpdateDistribution
cloudfront:CreateInvalidation
cloudfront:DeleteDistribution
```

### ACM

```text
acm:RequestCertificate
acm:ListCertificates
acm:DescribeCertificate
acm:DeleteCertificate
```

### Route 53

```text
route53:ListHostedZones
route53:ListResourceRecordSets
route53:ChangeResourceRecordSets
route53:DeleteHostedZone
```

For real deployments, apply the Principle of Least Privilege and restrict permissions to the resources and operations actually required.

---

# Security Considerations

## Never hardcode AWS credentials

Do not place AWS access keys or secrets in source code.

Use:

```bash
aws configure
```

or IAM roles/environment-specific credential mechanisms.

## Principle of Least Privilege

Use the minimum IAM permissions required.

## State Files

Do not commit sensitive or deployment-specific state to Git.

## Destructive Cleanup

Always inspect:

```bash
python cleanup.py
```

before executing:

```bash
python cleanup.py --execute
```

---

# Boto3 Concepts Learned

This project was designed as a hands-on Boto3 learning exercise.

### Clients

```python
boto3.client("s3")
boto3.client("cloudfront")
boto3.client("acm", region_name="us-east-1")
boto3.client("route53")
```

### AWS Regions

```text
S3          → Regional
ACM         → Regional
CloudFront  → Global
Route 53    → Global
```

CloudFront viewer certificates are managed through ACM in `us-east-1`.

### Exceptions

```python
from botocore.exceptions import ClientError
```

### Paginators

Used when AWS APIs can return results across multiple pages.

### Waiters / Polling

CloudFront deployments can take time, so the project waits for required AWS states.

### ETags

CloudFront update/delete operations use the current configuration ETag.

### Idempotency

Cleanup safely handles resources that are already absent.

---

# AWS Concepts Learned

## S3

- Buckets
- Objects
- Object keys
- Static website hosting
- Bucket policies
- Public access configuration
- MIME types
- Regional endpoints

## CloudFront

- Distribution
- Origin
- Cache behavior
- Viewer protocol policy
- Default root object
- Deployment states
- Cache invalidation
- Custom domains
- Viewer certificates

## ACM

- TLS/SSL certificates
- Certificate ARN
- DNS validation
- Certificate states
- Certificate lifecycle
- CloudFront certificate requirements

## Route 53

- Hosted zones
- DNS records
- CNAME
- A records
- Alias records
- ACM validation
- Domain → CloudFront routing

## IAM

- Permissions
- Least privilege
- AWS credential provider chain

---

# What Is Not Implemented

The following are intentionally not part of the current deployed architecture:

- Purchasing a domain
- Custom-domain deployment
- Actual ACM certificate issuance for a real domain
- Actual Route 53 DNS configuration
- CloudFront Origin Access Control
- Private S3 origin using OAC

These are future enhancements rather than claims about the current deployment.

---

# Future Improvements

- Private S3 bucket with CloudFront Origin Access Control
- Full custom-domain deployment
- Automatic ACM DNS validation through Route 53
- Route 53 Alias record creation
- HTTPS-only custom-domain deployment
- More robust resource state tracking
- Unit tests with mocked AWS APIs
- Integration tests
- Multi-environment configuration
- GitHub Actions CI
- Structured JSON logging
- Retry/backoff handling
- Improved rollback and recovery mechanisms

---

# Learning Outcomes

```text
Python
  │
  ├── OOP
  ├── Exceptions
  ├── Logging
  ├── JSON
  ├── pathlib
  ├── argparse
  └── Modular design
        │
        ▼
Boto3
  │
  ├── Clients
  ├── Paginators
  ├── AWS errors
  ├── Waiters / polling
  ├── ETags
  └── Resource lifecycle
        │
        ▼
AWS
  │
  ├── S3
  ├── CloudFront
  ├── ACM
  ├── Route 53
  └── IAM
```

---

# Git Development Strategy

The project was developed incrementally.

Every meaningful milestone followed:

```text
Implement
   ↓
Test
   ↓
Review
   ↓
git diff
   ↓
Commit
   ↓
Push
   ↓
Next milestone
```

This keeps the Git history understandable and provides working checkpoints throughout development.

---

# Final Project Status

```text
PHASE 1 — S3 Static Website Hosting
████████████████████ 100%

PHASE 2 — CloudFront
████████████████████ 100%

PHASE 3 — ACM + Custom Domain Architecture
████████████████████ 100%

PHASE 4 — Resource Cleanup
████████████████████ 100%
```

## Overall

```text
S3 Deployment              ✅
Static Website Hosting     ✅
CloudFront                 ✅
Cache Invalidation         ✅
ACM Management             ✅
Route 53 Support           ✅
Cleanup Automation         ✅
Dry Run                    ✅
Idempotent Cleanup         ✅
Deployment State           ✅
Custom Domain              ⏳ Requires real domain
OAC                        ⏳ Future enhancement
```

---

# License

This project is intended for educational, portfolio, and learning purposes.

---

# Author

**Nashit Shahi**

Built as a hands-on AWS and Boto3 learning project.
