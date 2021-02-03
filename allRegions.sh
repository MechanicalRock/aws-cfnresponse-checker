#!/bin/bash

for region in $(aws ec2 describe-regions --query 'Regions[].{Name:RegionName}' --output text); do
  echo ""
  echo "==========="
  echo "Region $region"
  python stacks.py --region $region
done
