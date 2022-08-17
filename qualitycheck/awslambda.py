import json

import boto3

# TODO I would retool this module to send messages to an sqs queue, rather than invoking a lambda.
class AwsLambda:

    def __init__(self, region='us-west-2'):
        self.region = region
        self.client = boto3.client('lambda', region_name=self.region)

    def invoke(self, function_name, payload, invocation_type='RequestResponse'):
        resp = self.client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload).encode()
        )
        return resp
