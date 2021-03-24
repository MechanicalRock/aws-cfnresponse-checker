import boto3
from botocore.config import Config

from cfnresponsechecker.stacks import Stacks
from cfnresponsereporter.reporter import Reporter

def main(regions, clean_print=False):
    for region in regions:
        if not clean_print:
            print(f"Region {region}")
        config = Config(region_name=region)
        client = boto3.client("cloudformation", config=config)
        stack = Stacks(client)
        # TODO
        problem_report = stack.get_problem_report()
        if problem_report:
            print(Reporter().pretty_problem_report(problem_report))
        elif not clean_print:
            print("None Found")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--regions", action="store", type=str, required=False)
    parser.add_argument("--clean-print", action="store_true", required=False)

    args = parser.parse_args()
    clean_print = args.clean_print

    if args.regions:
        regions = args.regions.split(",")
    else:
        ec2_client = boto3.client("ec2")
        regions = [
            region["RegionName"] for region in ec2_client.describe_regions()["Regions"]
        ]

    main(regions, clean_print)
