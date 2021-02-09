import boto3
from cfnresponsechecker.assume_role import Roles
from cfnresponsechecker.utils import get_accounts


def main(regions, role_name, accounts, clean_print=False):
    for id in accounts:
        if not clean_print:
            print(f"Account {id}")
        role = Roles(f"arn:aws:iam::{id}:role/{role_name}")
        for region in regions:
            if not clean_print:
                print(f"Region {region}")
            problem_stacks = role.get_problem_stacks(region)
            if problem_stacks:
                for stack in problem_stacks:
                    print(stack)
            elif not clean_print:
                print("None Found")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--role-name", action="store", type=str, required=True)
    parser.add_argument("--regions", action="store", type=str, required=False)
    parser.add_argument("--accounts", action="store", type=str, required=False)
    parser.add_argument("--clean-print", action="store_true", required=False)

    args = parser.parse_args()
    role_name = args.role_name
    clean_print = args.clean_print

    if args.regions:
        regions = args.regions.split(",")
    else:
        ec2_client = boto3.client("ec2")
        regions = [
            region["RegionName"] for region in ec2_client.describe_regions()["Regions"]
        ]

    if args.accounts:
        accounts = args.accounts.split(",")
    else:
        accounts = get_accounts()

    main(regions, role_name, accounts, clean_print)
