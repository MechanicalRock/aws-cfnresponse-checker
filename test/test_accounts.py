from os import environ, path
import json

import pytest
from cfnresponsechecker.assume_role import Roles


def parse_arn(arn):
    elements = arn.split(":")
    return {"arn": elements[0], "region": elements[3], "account": elements[4]}


directory = path.dirname(path.abspath(__file__))
file = path.join(directory, "accounts.json")
with open(file, "r") as reader:
    accounts = json.load(reader)

accounts_by_region = []
for account in accounts:
    for region in account["regions"]:
        accounts_by_region.append(
            {
                "account_id": account["account_id"],
                "region": region,
                "role_name": account["role_name"],
            }
        )


@pytest.mark.parametrize("account", accounts_by_region)
def test_account_stacks_are_safe(account):

    role = Roles(f"arn:aws:iam::{account['account_id']}:role/{account['role_name']}")
    assert not role.get_problem_stacks(
        account["region"],
    )
