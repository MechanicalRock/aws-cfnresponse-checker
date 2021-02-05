import boto3
from botocore.config import Config

from cfnresponsechecker.stacks import Stacks


class Roles:
    def __init__(self, role):
        sts_client = boto3.client("sts")
        assumed_role_object = sts_client.assume_role(
            RoleArn=role,
            RoleSessionName="cfnresponseCheck",
        )
        self.credentials = assumed_role_object["Credentials"]

    def get_problem_stacks(self, region):
        config = Config(region_name=region)
        client = boto3.client(
            "cloudformation",
            config=config,
            aws_access_key_id=self.credentials["AccessKeyId"],
            aws_secret_access_key=self.credentials["SecretAccessKey"],
            aws_session_token=self.credentials["SessionToken"],
        )
        stack = Stacks(client)
        return stack.get_problem_stacks()

    def test_stack(self, region, stack_id):
        config = Config(region_name=region)
        client = boto3.client(
            "cloudformation",
            config=config,
            aws_access_key_id=self.credentials["AccessKeyId"],
            aws_secret_access_key=self.credentials["SecretAccessKey"],
            aws_session_token=self.credentials["SessionToken"],
        )
        stack = Stacks(client)
        return stack.test_stack(stack_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--role", action="store", type=str, required=True)
    parser.add_argument("--regions", action="store", type=str, required=False)

    args = parser.parse_args()
    role = args.role

    if args.regions:
        regions = args.regions.split(",")
    else:
        ec2_client = boto3.client("ec2")
        regions = [
            region["RegionName"] for region in ec2_client.describe_regions()["Regions"]
        ]

    roles = Roles(role)
    for region in regions:
        print(f"Region {region}")
        problem_stacks = role.get_problem_stacks(region)
        if problem_stacks:
            for stack in problem_stacks:
                print(stack)
        else:
            print("None Found")