from src.route53_manager import Route53Manager


def main():

    route53 = Route53Manager()

    validation_record = {
        "domain_name": "www.example.com",
        "name": "_abc123.www.example.com",
        "type": "CNAME",
        "value": "_xyz456.acm-validations.aws"
    }

    print("\nACM Validation Record")
    print("====================")

    print(
        route53.build_validation_record(
            validation_record
        )
    )

    print("\nCloudFront Alias Record")
    print("======================")

    print(
        route53.build_cloudfront_alias_record(
            "www.example.com",
            "d123456789.cloudfront.net"
        )
    )


if __name__ == "__main__":
    main()