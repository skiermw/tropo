from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.cloudformation import Stack


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Top-Level""")
t.add_mapping("CentOS7",
{u'ap-northeast-1': {u'HVM': u'ami-d38dc6e9'},
 u'ap-southeast-1': {u'HVM': u'ami-2a7b6b78'},
 u'ap-southeast-2': {u'HVM': u'ami-b80b6db8'},
 u'eu-central-1': {u'HVM': u'ami-33734044'},
 u'eu-west-1': {u'HVM': u'ami-e68f82fb'},
 u'sa-east-1': {u'HVM': u'ami-fd0197e0'},
 u'us-east-1': {u'HVM': u'ami-61bbf104'},
 u'us-west-1': {u'HVM': u'ami-f77fbeb3'},
 u'us-west-2': {u'HVM': u'ami-d440a6e7'}}
)

t.add_mapping("AmznLinux",
{u'ap-northeast-1': {u'HVM': u'ami-a22fb8a2',
                     u'HVMwithEBS': u'ami-9a2fb89a',
                     u'PV': u'ami-a42fb8a4',
                     u'PVwithEBS': u'ami-9c2fb89c'},
 u'ap-southeast-1': {u'HVM': u'ami-ac9481fe',
                     u'HVMwithEBS': u'ami-52978200',
                     u'PV': u'ami-4c97821e',
                     u'PVwithEBS': u'ami-50978202'},
 u'ap-southeast-2': {u'HVM': u'ami-871856bd',
                     u'HVMwithEBS': u'ami-c11856fb',
                     u'PV': u'ami-851856bf',
                     u'PVwithEBS': u'ami-c71856fd'},
 u'eu-central-1': {u'HVM': u'ami-a2aeaebf',
                   u'HVMwithEBS': u'ami-daaeaec7',
                   u'PV': u'ami-a0aeaebd',
                   u'PVwithEBS': u'ami-a6aeaebb'},
 u'eu-west-1': {u'HVM': u'ami-7db9940a',
                u'HVMwithEBS': u'ami-69b9941e',
                u'PV': u'ami-8fbe93f8',
                u'PVwithEBS': u'ami-a3be93d4'},
 u'sa-east-1': {u'HVM': u'ami-030c991e',
                u'HVMwithEBS': u'ami-3b0c9926',
                u'PV': u'ami-010c991c',
                u'PVwithEBS': u'ami-370c992a'},
 u'us-east-1': {u'HVM': u'ami-65116700',
                u'HVMwithEBS': u'ami-e3106686',
                u'PV': u'ami-971066f2',
                u'PVwithEBS': u'ami-cf1066aa'},
 u'us-west-1': {u'HVM': u'ami-c33aff87',
                u'HVMwithEBS': u'ami-cd3aff89',
                u'PV': u'ami-c93aff8d',
                u'PVwithEBS': u'ami-d53aff91'},
 u'us-west-2': {u'HVM': u'ami-bbf7e88b',
                u'HVMwithEBS': u'ami-9ff7e8af',
                u'PV': u'ami-bdf7e88d',
                u'PVwithEBS': u'ami-81f7e8b1'}}
)

t.add_mapping("UbuntuTrusty",
{u'ap-northeast-1': {u'HVM': u'ami-ee294bee',
                     u'HVMwithEBS': u'ami-402e4c40',
                     u'PV': u'ami-32254732',
                     u'PVwithEBS': u'ami-362e4c36'},
 u'ap-southeast-1': {u'HVM': u'ami-a01003f2',
                     u'HVMwithEBS': u'ami-42170410',
                     u'PV': u'ami-2e11027c',
                     u'PVwithEBS': u'ami-54170406'},
 u'ap-southeast-2': {u'HVM': u'ami-016c263b',
                     u'HVMwithEBS': u'ami-6d6c2657',
                     u'PV': u'ami-c96e24f3',
                     u'PVwithEBS': u'ami-776c264d'},
 u'eu-central-1': {u'HVM': u'ami-90262a8d',
                   u'HVMwithEBS': u'ami-46272b5b',
                   u'PV': u'ami-84252999',
                   u'PVwithEBS': u'ami-48272b55'},
 u'eu-west-1': {u'HVM': u'ami-fb38048c',
                u'HVMwithEBS': u'ami-37360a40',
                u'PV': u'ami-91437fe6',
                u'PVwithEBS': u'ami-5b360a2c'},
 u'sa-east-1': {u'HVM': u'ami-8348d99e',
                u'HVMwithEBS': u'ami-1f4bda02',
                u'PV': u'ami-cf49d8d2',
                u'PVwithEBS': u'ami-e148d9fc'},
 u'us-east-1': {u'HVM': u'ami-b91042dc',
                u'HVMwithEBS': u'ami-ff02509a',
                u'PV': u'ami-11f9aa74',
                u'PVwithEBS': u'ami-e902508c'},
 u'us-west-1': {u'HVM': u'ami-2f8b486b',
                u'HVMwithEBS': u'ami-198a495d',
                u'PV': u'ami-c7864583',
                u'PVwithEBS': u'ami-138a4957'},
 u'us-west-2': {u'HVM': u'ami-e8e102db',
                u'HVMwithEBS': u'ami-8ee605bd',
                u'PV': u'ami-aa9a7999',
                u'PVwithEBS': u'ami-82e605b1'}}
)

IAM = t.add_resource(Stack(
    "IAM",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/iam.json",
))

TestCraft = t.add_resource(Stack(
    "TestCraft",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/craft.json",
    Parameters={ "AmiId": "ami-b18c62da", "VpcZoneIdentifierAz2": GetAtt("Network", "Outputs.SubnetTestPrivateAz2Id"), "ElbSecurityGroups": GetAtt("SecurityGroups", "Outputs.craftElbSecurityGroupId"), "InstanceSecurityGroups": GetAtt("SecurityGroups", "Outputs.craftSecurityGroupId"), "VpcZoneIdentifierAz1": GetAtt("Network", "Outputs.SubnetTestPrivateAz1Id"), "CraftElbSubnetAz1": GetAtt("Network", "Outputs.SubnetTestPublicAz1Id"), "CraftElbSubnetAz2": GetAtt("Network", "Outputs.SubnetTestPublicAz2Id"), "CraftElbSubnetAz3": GetAtt("Network", "Outputs.SubnetTestPublicAz3Id"), "SnsTopic": GetAtt("SNS", "Outputs.PrimaryArn"), "Environment": "Test", "ElbName": "Test-Craft-Elb", "IamInstanceProfile": GetAtt(IAM, "Outputs.craftInstanceProfile"), "InstanceType": "t2.micro", "VpcZoneIdentifierAz3": GetAtt("Network", "Outputs.SubnetTestPrivateAz3Id") },
))

Network = t.add_resource(Stack(
    "Network",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/network.json",
))

Bastion = t.add_resource(Stack(
    "Bastion",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/bastion.json",
    Parameters={ "AmiId": FindInMap("AmznLinux", Ref("AWS::Region"), "HVMwithEBS"), "InstanceSecurityGroups": GetAtt("SecurityGroups", "Outputs.BastionSecurityGroupId"), "VpcZoneIdentifierAz1": GetAtt(Network, "Outputs.SubnetTestPublicAz1Id"), "VpcZoneIdentifierAz3": GetAtt(Network, "Outputs.SubnetTestPublicAz3Id"), "VpcZoneIdentifierAz2": GetAtt(Network, "Outputs.SubnetTestPublicAz2Id"), "SnsTopic": GetAtt("SNS", "Outputs.PrimaryArn"), "IamInstanceProfile": GetAtt(IAM, "Outputs.BastionInstanceProfile") },
))

SecurityGroups = t.add_resource(Stack(
    "SecurityGroups",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/security_groups.json",
    Parameters={ "VpcId": GetAtt(Network, "Outputs.VpcId") },
))

SNS = t.add_resource(Stack(
    "SNS",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/sns.json",
))

Nat = t.add_resource(Stack(
    "Nat",
    TemplateURL="https://s3.amazonaws.com/shelter-mutual-aws-tools-us-east-1/cloudformation/nat.json",
    Parameters={ "AmiId": FindInMap("AmznLinux", Ref("AWS::Region"), "HVMwithEBS"), "InstanceSecurityGroups": GetAtt(Network, "Outputs.NatSecurityGroupId"), "VpcZoneIdentifierAz1": GetAtt(Network, "Outputs.SubnetTestPublicAz1Id"), "VpcZoneIdentifierAz3": GetAtt(Network, "Outputs.SubnetTestPublicAz3Id"), "VpcZoneIdentifierAz2": GetAtt(Network, "Outputs.SubnetTestPublicAz2Id"), "SnsTopic": GetAtt(SNS, "Outputs.PrimaryArn"), "IamInstanceProfile": GetAtt(IAM, "Outputs.NatInstanceProfile"), "InstanceType": "m3.medium" },
))

print(t.to_json())
