import boto3
import json

# gets the template from a stack and writes it to a json file

client = boto3.client('cloudformation')
response = client.get_template(
    StackName='ShelterMutual-Test-Nat-1OTADARJVZOTC'
)
json_string = json.dumps(response)
print json_string
template_json = json.loads(json_string)
f = open('Nat.json', 'w')
f.write(json.dumps(template_json['TemplateBody']))

