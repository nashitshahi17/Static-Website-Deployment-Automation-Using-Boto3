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
