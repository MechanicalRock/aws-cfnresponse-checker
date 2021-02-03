import boto3
import botocore
from botocore.config import Config
import argparse

from stacks import Stacks

# https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html

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

sts_client = boto3.client("sts")
# Call the assume_role method of the STSConnection object and pass the role
# ARN and a role session name.
assumed_role_object = sts_client.assume_role(
    RoleArn=role,
    RoleSessionName="cfnresponseCheck",
)

credentials = assumed_role_object["Credentials"]

for region in regions:
    config = Config(region_name=region)
    client = boto3.client(
        "cloudformation",
        config=config,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    stack = Stacks(client)
    stack.get_stack_resources()