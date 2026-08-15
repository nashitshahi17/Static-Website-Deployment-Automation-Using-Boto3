import boto3
import time
from botocore.exceptions import ClientError
from .logger import logger


class ACMManager:
    def __init__(self):
        self.client = boto3.client('acm', region_name='us-east-1')

    def request_certificate(self,domain_name,subject_alternative_names=None):
        params = {
            "DomainName":domain_name,
            "ValidationMethod":"DNS"
        }
        if subject_alternative_names:
            params["SubjectAlternativeNames"] = subject_alternative_names
        try:
            response = self.client.request_certificate(**params)

            certificate_arn = response["CertificateArn"]

            logger.info(
                f"ACM certificate requested: "
                f"{certificate_arn}"
            )

            return certificate_arn

        except ClientError as e:

            logger.error(
                f"Failed to request ACM certificate: {e}"
            )

            raise

    def get_certificate(self,certificate_arn):
        try:
            response = self.client.describe_certificate(
                CertificateArn=certificate_arn
            )
            return response["Certificate"]
        except ClientError as e:
            logger.error(
                f"Failed to retrieve ACM certificate: {e}"
            )
            raise

    def get_certificate_status(self,certificate_arn):
        certificate = self.get_certificate(certificate_arn)
        return certificate["Status"]

    def get_dns_validation_records(self,certificate_arn):
        certificate = self.get_certificate(certificate_arn)

        records = []

        for option in certificate["DomainValidationOptions"]:

            resource_record = option.get("ResourceRecord")

            if not resource_record:
                continue

            records.append({
                "domain_name": option["DomainName"],
                "name": resource_record["Name"],
                "type": resource_record["Type"],
                "value": resource_record["Value"]
            })

        return records

    def list_certificates(self):
        try:
            response = self.client.list_certificates()
            return response.get(
                "CertificateSummaryList",
                []
            )
        except ClientError as e:
            logger.error(f"Failed to list ACM certificates: {e}")
            raise


    def inspect_certificates(self):
        certificates = self.list_certificates()

        for certificate in certificates:

            logger.info(
                f"Certificate: "
                f"{certificate.get('CertificateArn')}"
            )

            logger.info(
                f"Domain: "
                f"{certificate.get('DomainName')}"
            )

    def get_certificate_state(self,certificate_arn):
        status = self.get_certificate_status(certificate_arn)
        if status == "ISUED":
            return "READY"

        if status == "PENDING_VALIDATION":
            return "WAITING"

        if status in {
            "FAILED",
            "VALIDATION_TIMED_OUT",
            "EXPIRED",
            "REVOKED",
            "INACTIVE"
        }:
            return "FAILED"

        return "UNKNOWN"

    def wait_for_certificate(self,certificate_arn,timeout=900,interval=15):
        start_time = time.time()
        while True:
            status = self.get_certificate_status(certificate_arn)
            logger.info(f"ACM certificate status: {status}")

            if status == "ISSUED":
                logger.info("ACM certificate has been issued.")
                return True

            if status in {
                "FAILED",
                "VALIDATION_TIMED_OUT",
                "EXPIRED",
                "REVOKED",
                "INACTIVE",
            }:
                reason = self.get_certificate_failure_reason(certificate_arn)

                logger.error(
                    f"ACM certificate failed "
                    f"Status: {status}"
                    f"Reason: {reason}"
                )

                return False

            elapsed = time.time() - start_time

            if elapsed >= timeout:

                logger.error(
                    "Timed out waiting for ACM "
                    "certificate."
                )

                return False

            time.sleep(interval)

    def get_certificate_failure_reason(self,certificate_arn):
        certificate = self.get_certificate(certificate_arn)
        return certificate.get("FailureReason")