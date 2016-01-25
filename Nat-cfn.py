from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.cloudwatch import Alarm
from troposphere.autoscaling import LaunchConfiguration
from troposphere.autoscaling import AutoScalingGroup


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
NAT""")
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

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    Type="String",
    Description="Instance Type",
))

NatAz2Alarm = t.add_resource(Alarm(
    "NatAz2Alarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref("NatAz2") }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="High CPU",
    Namespace="AWS/EC2",
    Period="60",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="90",
    MetricName="CPUUtilization",
))

AsgLaunchConfiguration = t.add_resource(LaunchConfiguration(
    "AsgLaunchConfiguration",
    UserData=Base64(Join("", ["#!/usr/bin/env bash\n", "yum -y install epel-release\n", "yum -y --enablerepo=epel install python-pip\n", "pip install --upgrade awscli\n", "export PROJECT=", "sheltermutual", "\n", "export ENV=", "test", "\n", "export SNS_TOPIC=", Ref(SnsTopic), "\n", "aws s3 cp s3://", "shelter-mutual-aws-tools-us-east-1/bootstrap", "/nat.sh", " /usr/local/bin/nat.sh", " --region ", Ref("AWS::Region"), " \n", "chmod 770 /usr/local/bin/nat.sh", " \n", "/usr/local/bin/nat.sh", " \n"])),
    ImageId=Ref(AmiId),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "DeleteOnTermination": "true", "VolumeType": "gp2", "VolumeSize": "10" } }],
    KeyName="common-us-east-1",
    SecurityGroups=[Ref(InstanceSecurityGroups)],
    IamInstanceProfile=Ref(IamInstanceProfile),
    InstanceType=Ref(InstanceType),
    AssociatePublicIpAddress="true",
))

NatAz2 = t.add_resource(AutoScalingGroup(
    "NatAz2",
    AvailabilityZones=[Select("1", GetAZs(""))],
    DesiredCapacity="1",
    Tags=Tags(
        Name="Test-Nat-Asg-Az2",
        project="ShelterMutual",
        WhichAZ="AZ2",
    ),
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=[Ref(VpcZoneIdentifierAz2)],
    LaunchConfigurationName=Ref(AsgLaunchConfiguration),
    HealthCheckGracePeriod="300",
    HealthCheckType="EC2",
))

NatAz3 = t.add_resource(AutoScalingGroup(
    "NatAz3",
    AvailabilityZones=[Select("2", GetAZs(""))],
    DesiredCapacity="1",
    Tags=Tags(
        Name="Test-Nat-Asg-Az3",
        project="ShelterMutual",
        WhichAZ="AZ3",
    ),
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=[Ref(VpcZoneIdentifierAz3)],
    LaunchConfigurationName=Ref(AsgLaunchConfiguration),
    HealthCheckGracePeriod="300",
    HealthCheckType="EC2",
))

NatAz1 = t.add_resource(AutoScalingGroup(
    "NatAz1",
    AvailabilityZones=[Select("0", GetAZs(""))],
    DesiredCapacity="1",
    Tags=Tags(
        Name="Test-Nat-Asg-Az1",
        project="ShelterMutual",
        WhichAZ="AZ1",
    ),
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=[Ref(VpcZoneIdentifierAz1)],
    LaunchConfigurationName=Ref(AsgLaunchConfiguration),
    HealthCheckGracePeriod="300",
    HealthCheckType="EC2",
))

NatAz3Alarm = t.add_resource(Alarm(
    "NatAz3Alarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(NatAz3) }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="High CPU",
    Namespace="AWS/EC2",
    Period="60",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="90",
    MetricName="CPUUtilization",
))

NatAz1Alarm = t.add_resource(Alarm(
    "NatAz1Alarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(NatAz1) }],
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
