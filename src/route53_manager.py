import boto3
from botocore.exceptions import ClientError
from .logger import logger

class Route53Manager:
    def __init__(self):
        self.client = boto3.client('route53')

    def list_hosted_zones(self):
        try:
            response = self.client.list_hosted_zones()

            return response.get("HostedZones",[])
        except ClientError as e:
            logger.error(f"Failed to list Route53 hosted zones: {e}")
            raise

    def find_hosted_zone(self,domain_name):
        hosted_zones = self.list_hosted_zones()
        normalized_domain = domain_name.rstrip("/") + "."

        for zone in hosted_zones:
            zone_name = zone["Name"]
            if zone_name == normalized_domain:
                return zone

        return None

    def inspect_hosted_zones(self):
        hosted_zones = self.list_hosted_zones()

        if not hosted_zones:
            logger.info("No Route 53 hosted zones found")
            return

        for zone in hosted_zones:
            logger.info(f"Hosted Zone: {zone["Name"]}")
            logger.info(f"Zone ID: {zone["Id"]}")
            logger.info(f"Private: {zone['Config']['PrivateZone']}")

    def build_validation_record(self,validation_record):
        return{
            "Name": validation_record["name"],
            "Type": validation_record["type"],
            "TTL" : 300,
            "ResourceRecords":[
                {
                    "Value": validation_record["value"]
                }
            ]
        }

    def build_cloudfront_alias_record(self,domain_name,cloudfront_domain):
        return {
            "Name": domain_name,
            "Type": "A",
            "AliasTarget":{
                "DNSName": cloudfront_domain,
                "HostedZoneId" : "Z2FDTNDATAQYW2",
                "EvaluatedTargetHealth": False
            }
        }

    def delete_record(self,hosted_zone_id,record):
        if not hosted_zone_id:
            logger.info("No hosted zone ID provided.")
            return False
        
        if not record:
            logger.info("No DNS record provided.")
            return False

        try:
            self.client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    "Changes": [
                        {
                            "Action": "DELETE",
                            "ResourceRecordSet": record
                        }
                    ]
                }
            )

            logger.info(f"Deleted DNS record: {record['Name']}")

            return True

        except ClientError as e:

            error_code = e.response["Error"].get("Code")

            if error_code == "InvalidChangeBatch":

                logger.info(f"DNS record may already be deleted: {record.get('Name')}")

                return True

            logger.error(
                f"Failed to delete DNS record: {e}")
            raise

    def delete_hosted_zone(self,hosted_zone_id):

        if not hosted_zone_id:
            logger.info("No hosted zone ID provided.")
            return False

        try:

            self.client.delete_hosted_zone(Id=hosted_zone_id)

            logger.info(f"Hosted zone deleted: {hosted_zone_id}")

            return True

        except ClientError as e:

            error_code = e.response["Error"].get("Code")

            if error_code == "NoSuchHostedZone":

                logger.info(f"Hosted zone already deleted: {hosted_zone_id}")

                return True

            logger.error(f"Failed to delete hosted zone {hosted_zone_id}: {e}")
            raise