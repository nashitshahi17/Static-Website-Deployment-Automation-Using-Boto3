# Static Website Deployer using Boto3

## Overview

A production-style Python automation project that deploys a static website to **Amazon S3** and serves it through **Amazon CloudFront**, using **Boto3**.

The project is built progressively to learn AWS and Boto3 concepts:

```text
Phase 1 → S3 Static Website Hosting
Phase 2 → CloudFront CDN
Phase 3 → ACM + Custom Domain
Phase 4 → AWS Resource Cleanup
```

**Phase 1 and Phase 2 are completed.**

---

## Project Status

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Completed | S3 static website deployment |
| Phase 2 | ✅ Completed | CloudFront distribution, deployment waiting, verification and cache invalidation |
| Phase 3 | ⏳ Upcoming | ACM certificate + custom domain |
| Phase 4 | ⏳ Upcoming | Automated AWS resource cleanup |

---

# Phase 1 — S3 Static Website Hosting

Phase 1 automates static website hosting using Amazon S3 and Boto3.

### Implemented

- Create an S3 bucket
- Generate unique bucket names
- Validate bucket names
- Configure logging
- Configure S3 Block Public Access for static website hosting
- Enable S3 Static Website Hosting
- Recursively upload website files
- Automatically detect MIME types
- Apply a public-read bucket policy
- Generate and print the S3 website endpoint

Example:

```text
http://<bucket-name>.s3-website-<region>.amazonaws.com
```

---

# Phase 2 — CloudFront

Phase 2 adds **Amazon CloudFront** in front of the S3 static website.

## Architecture

```text
                         Internet
                            │
                            │ HTTPS
                            ▼
                    ┌───────────────┐
                    │  CloudFront   │
                    │      CDN      │
                    └───────┬───────┘
                            │
                            │ HTTP
                            ▼
                  ┌─────────────────────┐
                  │ S3 Website Endpoint │
                  └──────────┬──────────┘
                             │
                             ▼
                       ┌───────────┐
                       │ S3 Bucket │
                       │           │
                       │ index.html│
                       │ style.css │
                       │ script.js │
                       └───────────┘
```

The deployment provides two endpoints:

### S3 Website

```text
http://<bucket-name>.s3-website-<region>.amazonaws.com
```

### CloudFront

```text
https://<distribution-domain>.cloudfront.net
```

CloudFront provides HTTPS delivery, caching and global content distribution while S3 remains the origin.

---

## Phase 2 Features

### CloudFront Distribution

The application creates a CloudFront distribution using Boto3.

The S3 Static Website Endpoint is configured as a **custom origin**.

```text
CloudFront
     │
     ▼
CustomOriginConfig
     │
     ▼
S3 Website Endpoint
```

Because the S3 website endpoint is used, the origin protocol is:

```text
http-only
```

The viewer-facing CloudFront connection uses:

```text
redirect-to-https
```

### Default Root Object

CloudFront uses:

```text
index.html
```

as the default root object.

### Cache Behavior

The static website uses:

```text
GET
HEAD
```

methods, with compression enabled for supported content.

### Deployment Waiter

CloudFront distribution creation is asynchronous. The application waits until the distribution reaches:

```text
Deployed
```

```text
Create Distribution
        │
        ▼
   InProgress
        │
        ▼
Wait for Deployment
        │
        ▼
     Deployed
```

### Distribution Verification

The application retrieves the current CloudFront distribution information using Boto3 and tracks:

- Distribution ID
- Distribution ARN
- Distribution status
- CloudFront domain name

### Cache Invalidation

When website files are updated, CloudFront may continue serving cached objects.

The application can create an invalidation and wait for it to complete:

```text
Upload new website
        │
        ▼
Create Invalidation
        │
        ▼
    InProgress
        │
        ▼
Wait
        │
        ▼
    Completed
```

The current learning deployment supports invalidating:

```text
/*
```

---

# Origin Access Control Exploration

During Phase 2, the project also introduced **CloudFront Origin Access Control (OAC)** using Boto3.

The implementation demonstrates:

- Creating an Origin Access Control
- SigV4 request signing
- `SigningBehavior`
- `SigningProtocol`
- S3 origin type

Conceptually:

```text
CloudFront
     │
     ▼
Origin Access Control
     │
     │ SigV4
     ▼
Private S3 Bucket
```

### Current Architecture vs. Secure Architecture

The current learning deployment intentionally uses:

```text
CloudFront
    ↓
S3 Website Endpoint
```

The OAC implementation is retained as an advanced architecture concept.

A production-oriented private-S3 architecture would instead use:

```text
CloudFront
    ↓
OAC
    ↓
Private S3 REST Endpoint
```

This distinction is intentional: the project first teaches S3 Static Website Hosting, then CloudFront, before evolving toward a more secure private-origin architecture.

---

# Resource State Tracking

The project includes local deployment state tracking to avoid unnecessarily creating duplicate AWS resources.

Example state:

```json
{
    "bucket_name": "<existing-bucket>",
    "distribution_id": "<existing-distribution>",
    "cloudfront_domain": "<distribution-domain>"
}
```

The state file is:

```text
deployment_state.json
```

and is excluded from Git using `.gitignore`.

The state is used as a reference while AWS remains the source of truth.

---

# Idempotent Deployment

The project demonstrates the basic concept of **idempotent infrastructure automation**.

Instead of:

```text
Run 1 → Create Bucket + Distribution
Run 2 → Create another Bucket + Distribution
Run 3 → Create another Bucket + Distribution
```

the intended behavior is:

```text
Run 1
  ↓
Create resources
  ↓
Save resource identifiers

Run 2
  ↓
Read state
  ↓
Check AWS
  ↓
Reuse existing resources
```

This is a fundamental DevOps concept also used by Terraform, CloudFormation, Ansible and Kubernetes.

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
│   ├── uploader.py
│   ├── policy.py
│   ├── cloudfront_manager.py
│   ├── state_manager.py
│   └── deployer.py
│
├── website/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
│       └── logo.png
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Component Responsibilities

## `main.py`

Application entry point. Starts the deployment orchestrator and displays final deployment information.

## `deployer.py`

Coordinates the deployment workflow:

```text
State
 ↓
S3
 ↓
Website Upload
 ↓
CloudFront
 ↓
Deployment Wait
 ↓
Cache Invalidation
```

## `s3_manager.py`

Handles bucket creation, existence checks, static website configuration, public access configuration and bucket policy configuration.

## `uploader.py`

Handles recursive website uploads and MIME type detection.

## `policy.py`

Contains S3 bucket policy generation/application logic.

## `cloudfront_manager.py`

Handles:

- Origin Access Control creation
- Distribution creation
- Distribution existence checks
- Distribution retrieval
- Deployment waiting
- Cache invalidation
- Invalidation waiting

## `state_manager.py`

Handles loading, saving and clearing local deployment state.

## `config.py`

Contains configuration and utility functions such as bucket name generation and website endpoint generation.

## `logger.py`

Centralizes application logging.

## `validators.py`

Contains validation logic used by the application.

---

# Tech Stack

### Programming

- Python 3.10+
- Object-Oriented Programming
- Exception Handling
- JSON
- pathlib
- UUID
- logging
- mimetypes

### AWS

- Amazon S3
- Amazon CloudFront
- AWS IAM
- CloudFront Origin Access Control
- AWS CLI

### Python AWS SDK

- Boto3
- Botocore

---

# Prerequisites

- AWS Account
- IAM identity with required S3 and CloudFront permissions
- AWS CLI
- Python 3.10+
- Python virtual environment

Configure AWS credentials:

```bash
aws configure
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Project

Run:

```bash
python main.py
```

The deployment flow is:

```text
Load deployment state
        │
        ▼
Find/Create S3 bucket
        │
        ▼
Configure S3 static website
        │
        ▼
Upload website
        │
        ▼
Apply bucket policy
        │
        ▼
Find/Create CloudFront distribution
        │
        ▼
Wait for CloudFront deployment
        │
        ▼
Invalidate CloudFront cache
        │
        ▼
Wait for invalidation
        │
        ▼
Save deployment state
        │
        ▼
Display deployment URLs
```

---

# AWS Services Used

### Completed

- Amazon S3
- Amazon CloudFront
- AWS IAM
- AWS CLI

### Upcoming

- AWS Certificate Manager (ACM)
- Amazon Route 53

---

# AWS Concepts Learned

## S3

- Buckets
- Objects
- Static Website Hosting
- Bucket policies
- Public access configuration
- Resource-based permissions
- Website endpoints
- MIME types
- Object uploads

## CloudFront

- Distributions
- Origins
- Custom origins
- Cache behaviors
- Viewer protocol policies
- Default root objects
- CDN caching
- Cache invalidation
- Distribution deployment states
- CloudFront domain names
- Origin Access Control
- SigV4 request signing

## Boto3

- AWS service clients
- API calls
- AWS response parsing
- Waiters
- ClientError handling
- Resource state verification
- Resource creation
- Resource reuse
- JSON-based local state management

---

# Engineering Concepts Demonstrated

- Separation of concerns
- Service wrapper classes
- Deployment orchestration
- Idempotent automation
- Resource state tracking
- Exception handling
- Logging
- Git-based incremental development
- AWS resource lifecycle management
- Asynchronous AWS operations
- CDN cache management

---

# Security Notes

- Never hardcode AWS credentials.
- Use AWS CLI profiles, IAM roles or environment-based credentials.
- Follow the Principle of Least Privilege.
- Do not commit AWS credentials.
- Do not commit `.env` files.
- Do not commit `deployment_state.json`.
- Do not commit virtual environments.
- Review S3 public access configuration carefully.
- The current S3 Website + CloudFront architecture intentionally uses a public S3 website endpoint for learning.
- For a production-oriented secure architecture, use CloudFront Origin Access Control with a private S3 bucket.

---

# Cost Awareness

AWS resources created by this project can incur charges depending on usage and account configuration.

Be especially careful with:

- CloudFront distributions
- CloudFront invalidations
- S3 storage and requests
- Data transfer

Do not repeatedly execute deployment scripts that create new infrastructure.

Before creating resources, verify the current AWS resources and deployment state.

Phase 4 will introduce automated cleanup.

---

# Future Phases

## Phase 3 — ACM + Custom Domain

Planned architecture:

```text
Custom Domain
      │
      ▼
ACM Certificate
      │
      ▼
CloudFront
      │
      ▼
S3
```

Topics:

- AWS Certificate Manager
- DNS validation
- Route 53
- CloudFront viewer certificates
- Alternate domain names
- HTTPS
- DNS records
- ACM regional requirements for CloudFront

## Phase 4 — Automated Cleanup

The cleanup script will identify and delete resources created by the project.

Planned dependency-aware cleanup:

```text
CloudFront
     ↓
ACM / Route 53 configuration
     ↓
S3
```

The cleanup process will account for AWS resource dependencies so resources can be removed safely.

---

# Future Improvements

- CLI arguments using `argparse`
- Configuration files
- Environment-specific deployments
- Changed-file detection
- Selective CloudFront invalidation
- File versioning
- Unit tests
- Integration tests
- GitHub Actions CI
- Automated deployment workflows
- Better AWS error classification
- Retry and backoff handling
- Dry-run mode
- Deployment reports
- Production-style private S3 + CloudFront OAC architecture

---

# Learning Outcomes

After completing the project, you will understand how to:

- Automate AWS infrastructure using Boto3
- Create and configure S3 buckets programmatically
- Host static websites on S3
- Upload website files recursively
- Configure bucket policies
- Build CloudFront distributions
- Configure CloudFront origins
- Configure cache behavior
- Wait for asynchronous AWS operations
- Retrieve and verify AWS resource state
- Invalidate CloudFront caches
- Track infrastructure state
- Build idempotent deployment automation
- Use Origin Access Control
- Configure HTTPS with ACM
- Connect custom domains through Route 53
- Safely clean up AWS resources

---

# Development Philosophy

This project is intentionally built incrementally.

```text
Phase 1
S3 Fundamentals
      │
      ▼
Phase 2
CloudFront + CDN
      │
      ▼
Phase 3
HTTPS + Custom Domain
      │
      ▼
Phase 4
Resource Cleanup
```

The objective is not only to build the application, but to understand **why each AWS service, API, configuration and architectural decision is being used**.

---

# License

This project is intended for learning, experimentation and portfolio purposes.
