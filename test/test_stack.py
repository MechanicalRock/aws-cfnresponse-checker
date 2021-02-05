from os import environ, path

import pytest
from cfnresponsechecker.assume_role import Roles

ROLE_NAME = environ.get("AWS_ROLE_NAME")


def parse_arn(arn):
    elements = arn.split(":")
    return {"arn": elements[0], "region": elements[3], "account": elements[4]}


directory = path.dirname(path.abspath(__file__))
file = path.join(directory, "stacks.txt")
with open(file, "r") as reader:
    stack_ids = [x.strip() for x in reader.readlines() if x[0] != "#"]


@pytest.mark.parametrize("stack_id", stack_ids)
def test_stack_is_safe(stack_id):

    arn = parse_arn(stack_id)
    role = Roles(f"arn:aws:iam::{arn['account']}:role/{ROLE_NAME}")
    assert not role.test_stack(
        arn["region"],
        stack_id,
    )
