#! /bin/bash

set -e

export AWS_DEFAULT_REGION=il-central-1

aws cloudformation deploy \
  --stack-name "alexa-red-alert-core" \
  --template-file "./infrastructure/core.cf.yaml"

lambda_assets_bucket_name=$(
  aws cloudformation describe-stacks \
  --stack-name "alexa-red-alert-core" \
  --query "Stacks[0].Outputs[?OutputKey=='LambdaAssetsBucketName'].OutputValue" \
  --output text
)

echo "-- Packaging code for lambda"
rm -rf .dist
mkdir -p .dist
cp -R alexa_red_alert .dist

aws cloudformation package \
  --template-file "./infrastructure/resources.cf.yaml" \
  --s3-bucket "$lambda_assets_bucket_name" \
  --s3-prefix "lambda" \
  --output-template-file ".template.cf.yaml"

aws cloudformation deploy \
  --stack-name "alexa-red-alert-resources" \
  --template-file ".template.cf.yaml" \
  --capabilities "CAPABILITY_NAMED_IAM"

api_url=$(
  aws cloudformation describe-stacks \
  --stack-name "alexa-red-alert-resources" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" \
  --output text
)
echo "API URL: $api_url"
