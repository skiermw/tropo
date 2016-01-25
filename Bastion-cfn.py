from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.autoscaling import AutoScalingGroup
from troposphere.autoscaling import LaunchConfiguration
from troposphere.cloudwatch import Alarm


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Bastion""")
AmiId = t.add_parameter(Parameter(
    "AmiId",
    Default="",
    Type="String",
    Description="AMI ID for Launch Configuration",
))

InstanceSecurityGroups = t.add_parameter(Parameter(
    "InstanceSecurityGroups",
    Default="",
    Type="String",
    Description="Security Groups assigned to instances in ASG",
))

VpcZoneIdentifierAz1 = t.add_parameter(Parameter(
    "VpcZoneIdentifierAz1",
    Default="",
    Type="String",
    Description="VPC Zone Id used for ASG in AZ1",
))

VpcZoneIdentifierAz3 = t.add_parameter(Parameter(
    "VpcZoneIdentifierAz3",
    Default="",
    Type="String",
    Description="VPC Zone Id used for ASG in AZ3",
))

VpcZoneIdentifierAz2 = t.add_parameter(Parameter(
    "VpcZoneIdentifierAz2",
    Default="",
    Type="String",
    Description="VPC Zone Id used for ASG in AZ2",
))

SnsTopic = t.add_parameter(Parameter(
    "SnsTopic",
    Default="",
    Type="String",
    Description="SNS Topic to be used in bootstrap",
))

IamInstanceProfile = t.add_parameter(Parameter(
    "IamInstanceProfile",
    Default="",
    Type="String",
    Description="IAM Instance Profile ARN",
))

BastionAsg = t.add_resource(AutoScalingGroup(
    "BastionAsg",
    AvailabilityZones=[Select("0", GetAZs("")), Select("1", GetAZs("")), Select("2", GetAZs(""))],
    DesiredCapacity="1",
    Tags=Tags(
        Name=Join("", ["Test", "-Bastion-Asg"]),
        project="ShelterMutual",
    ),
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=[Ref(VpcZoneIdentifierAz1), Ref(VpcZoneIdentifierAz2), Ref(VpcZoneIdentifierAz3)],
    LaunchConfigurationName=Ref("BastionLaunchConfig"),
    HealthCheckGracePeriod="300",
    HealthCheckType="EC2",
))

BastionLaunchConfig = t.add_resource(LaunchConfiguration(
    "BastionLaunchConfig",
    UserData=Base64(Join("", ["#!/usr/bin/env bash\n", "yum -y install epel-release\n", "yum -y --enablerepo=epel install python-pip\n", "pip install --upgrade awscli\n", "export PROJECT=", "sheltermutual", "\n", "export ENV=", "test", "\n", "export SNS_TOPIC=", Ref(SnsTopic), "\n", "aws s3 cp s3://", "shelter-mutual-aws-tools-us-east-1/bootstrap", "/bastion.sh", " /usr/local/bin/bastion.sh", " --region ", Ref("AWS::Region"), " \n", "chmod 770 /usr/local/bin/bastion.sh", " \n", "/usr/local/bin/bastion.sh", " \n"])),
    ImageId=Ref(AmiId),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "DeleteOnTermination": "true", "VolumeType": "gp2", "VolumeSize": "10" } }],
    KeyName="bastion-us-east-1",
    SecurityGroups=[Ref(InstanceSecurityGroups)],
    IamInstanceProfile=Ref(IamInstanceProfile),
    InstanceType="t2.micro",
    AssociatePublicIpAddress="true",
))

BastionAlarm = t.add_resource(Alarm(
    "BastionAlarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(BastionAsg) }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="High CPU",
    Namespace="AWS/EC2",
    Period="60",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="90",
    MetricName="CPUUtilization",
))

print(t.to_json())
