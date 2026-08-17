from src.route53_manager import Route53Manager


def main():

    route53 = Route53Manager()

    zones = route53.list_hosted_zones()

    print("\nRoute 53 Hosted Zones")
    print("====================")

    if not zones:

        print("No hosted zones found.")

        return

    for zone in zones:

        print(
            f"\nName: {zone['Name']}"
        )

        print(
            f"ID: {zone['Id']}"
        )

        print(
            f"Private: "
            f"{zone['Config']['PrivateZone']}"
        )


if __name__ == "__main__":
    main()