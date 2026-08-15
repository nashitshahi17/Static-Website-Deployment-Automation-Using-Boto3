from src.acm_manager import ACMManager


def main():

    acm = ACMManager()

    certificates = acm.list_certificates()

    print("\nACM Certificates")
    print("================")

    if not certificates:

        print("No certificates found.")

        return

    for certificate in certificates:

        print(
            f"\nDomain: "
            f"{certificate.get('DomainName')}"
        )

        print(
            f"ARN: "
            f"{certificate.get('CertificateArn')}"
        )


if __name__ == "__main__":
    main()