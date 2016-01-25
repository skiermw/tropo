from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.sns import Topic, Subscription


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
SNS""")
Primary = t.add_resource(Topic(
    "Primary",
    DisplayName="ShelterMutual-Primary",
    TopicName="ShelterMutual-Primary",
    Subscription=[
    Subscription(
        Endpoint="jduggan@rightbrainnetworks.com",
        Protocol="email",
    ),
    ],
))

PrimaryArn = t.add_output(Output(
    "PrimaryArn",
    Description="Primary SNS ARN.",
    Value=Ref(Primary),
))

print(t.to_json())
