#! /bin/bash
aws cloudformation deploy --stack-name cfnresponsechecker-out-of-date-stack --template-file out-of-date-stack/template.yaml --capabilities CAPABILITY_IAM

aws cloudformation deploy --stack-name cfnresponsechecker-CustomResource-type-stack --template-file CustomResource-type-stack/template.yaml --capabilities CAPABILITY_IAM