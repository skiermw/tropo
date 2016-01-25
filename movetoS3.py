import boto3
import json

# gets the template from a stack and writes it to a json file

# Let's use Amazon S3
s3 = boto3.resource('s3')

'''
# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
'''

# Upload a new file
data = open('tropoSecurityGroup.json', 'rb')
s3.Bucket('saytemplates').put_object(Key='tropoSecurityGroup.json', Body=data)