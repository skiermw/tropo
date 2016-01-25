from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.cloudwatch import Alarm
from troposphere.autoscaling import AutoScalingGroup
from troposphere.autoscaling import ScalingPolicy
from troposphere.elasticloadbalancing import LoadBalancer, HealthCheck, ConnectionDrainingPolicy, AccessLoggingPolicy
from troposphere.autoscaling import LaunchConfiguration


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Craft""")
AmiId = t.add_parameter(Parameter(
    "AmiId",
    Default="",
    Type="String",
    Description="AMI ID for Launch Configuration",
))

VpcZoneIdentifierAz2 = t.add_parameter(Parameter(
    "VpcZoneIdentifierAz2",
    Default="",
    Type="String",
    Description="VPC Zone Id used for ASG in AZ2",
))

ElbSecurityGroups = t.add_parameter(Parameter(
    "ElbSecurityGroups",
    Default="",
    Type="String",
    Description="Security Groups assigned to ELB",
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

CraftElbSubnetAz1 = t.add_parameter(Parameter(
    "CraftElbSubnetAz1",
    Default="",
    Type="String",
    Description="Subnet for Craft ELB in AZ1",
))

CraftElbSubnetAz2 = t.add_parameter(Parameter(
    "CraftElbSubnetAz2",
    Default="",
    Type="String",
    Description="Subnet for Craft ELB in AZ2",
))

CraftElbSubnetAz3 = t.add_parameter(Parameter(
    "CraftElbSubnetAz3",
    Default="",
    Type="String",
    Description="Subnet for Craft ELB in AZ3",
))

SnsTopic = t.add_parameter(Parameter(
    "SnsTopic",
    Default="",
    Type="String",
    Description="SNS Topic to be used in bootstrap",
))

Environment = t.add_parameter(Parameter(
    "Environment",
    Default="",
    Type="String",
    Description="Environment of the stack",
))

ElbName = t.add_parameter(Parameter(
    "ElbName",
    Default="",
    Type="String",
    Description="Name, including environment, of ELB",
))

IamInstanceProfile = t.add_parameter(Parameter(
    "IamInstanceProfile",
    Default="",
    Type="String",
    Description="IAM Instance Profile ARN",
))

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="",
    Type="String",
    Description="Instance Type",
))

VpcZoneIdentifierAz3 = t.add_parameter(Parameter(
    "VpcZoneIdentifierAz3",
    Default="",
    Type="String",
    Description="VPC Zone Id used for ASG in AZ3",
))
'''
CraftHighElbLatencyAlarm = t.add_resource(Alarm(
    "CraftHighElbLatencyAlarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "LoadBalancerName", "Value": Ref("CraftElb") }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="Signal alarm if ELB Latency is above threshold",
    Namespace="AWS/ELB",
    Period="60",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="60",
    MetricName="Latency"
))
'''

CraftAsg = t.add_resource(AutoScalingGroup(
    "CraftAsg",
    AvailabilityZones=[Select("0", GetAZs("")), Select("1", GetAZs("")), Select("2", GetAZs(""))],
    DesiredCapacity=2,
    NotificationConfigurations=[{ "NotificationTypes": ["autoscaling:EC2_INSTANCE_LAUNCH", "autoscaling:EC2_INSTANCE_TERMINATE"], "TopicARN": Ref(SnsTopic) }],
    Tags=Tags(
        Name=Join("", [Ref(Environment), "-Craft-Asg"]),
        Environment=Ref(Environment),
        project="ShelterMutual",
    ),
    LaunchConfigurationName=Ref("CraftLaunchConfig"),
    MinSize=2,
    MaxSize=3,
    VPCZoneIdentifier=[Ref(VpcZoneIdentifierAz1), Ref(VpcZoneIdentifierAz2), Ref(VpcZoneIdentifierAz3)],
    LoadBalancerNames=[Ref("CraftElb")],
    HealthCheckGracePeriod=300,
    HealthCheckType="EC2",
))

CraftLowCpuAlarm = t.add_resource(Alarm(
    "CraftLowCpuAlarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(CraftAsg) }],
    AlarmActions=[Ref(SnsTopic), Ref("CraftScaleDownPolicy")],
    AlarmDescription="Signal alarm if CPU utilization is below threshold",
    Namespace="AWS/EC2",
    Period="120",
    ComparisonOperator="LessThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="40",
    MetricName="CPUUtilization",
))

CraftScaleUpPolicy = t.add_resource(ScalingPolicy(
    "CraftScaleUpPolicy",
    ScalingAdjustment="1",
    AutoScalingGroupName=Ref(CraftAsg),
    Cooldown=300,
    AdjustmentType="ChangeInCapacity",
))

CraftRootDiskWriteOps = t.add_resource(Alarm(
    "CraftRootDiskWriteOps",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(CraftAsg) }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="Send alert if DiskWriteOps is greater than ~90%",
    Namespace="AWS/EC2",
    Period="300",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="27",
    MetricName="DiskWriteOps",
))

CraftScaleDownPolicy = t.add_resource(ScalingPolicy(
    "CraftScaleDownPolicy",
    ScalingAdjustment="-1",
    AutoScalingGroupName=Ref(CraftAsg),
    Cooldown=120,
    AdjustmentType="ChangeInCapacity",
))

CraftRootDiskReadOps = t.add_resource(Alarm(
    "CraftRootDiskReadOps",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(CraftAsg) }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="Send alert if DiskReadOps is greater than ~90%",
    Namespace="AWS/EC2",
    Period="300",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="27",
    MetricName="DiskReadOps",
))

CraftElb = t.add_resource(LoadBalancer(
    "CraftElb",
    ConnectionDrainingPolicy=ConnectionDrainingPolicy(
        Enabled=True,
        Timeout="120",
    ),
    Subnets=[Ref(CraftElbSubnetAz1), Ref(CraftElbSubnetAz2), Ref(CraftElbSubnetAz3)],
    HealthCheck=HealthCheck(
        HealthyThreshold="2",
        Interval="10",
        Target="TCP:80",
        Timeout="5",
        UnhealthyThreshold="5",
    ),
    Listeners=[{ "InstancePort": "80", "LoadBalancerPort": "80", "Protocol": "HTTP", "InstanceProtocol": "HTTP" }],
    CrossZone="true",
    SecurityGroups=[Ref(ElbSecurityGroups)],
    LoadBalancerName=Ref(ElbName),
    Scheme="internet-facing",
))

CraftElbHealthyHosts = t.add_resource(Alarm(
    "CraftElbHealthyHosts",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "LoadBalancerName", "Value": Ref(CraftElb) }],
    AlarmActions=[Ref(SnsTopic)],
    AlarmDescription="Send alert if number of healthy host is below minimum # of instances",
    Namespace="AWS/ELB",
    Period="60",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold="2",
    MetricName="HealthyHostCount",
))

CraftHighCpuAlarm = t.add_resource(Alarm(
    "CraftHighCpuAlarm",
    EvaluationPeriods="1",
    Dimensions=[{ "Name": "AutoScalingGroupName", "Value": Ref(CraftAsg) }],
    AlarmActions=[Ref(SnsTopic), Ref(CraftScaleUpPolicy)],
    AlarmDescription="Signal alarm if CPU utilization is above threshold",
    Namespace="AWS/EC2",
    Period="300",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Statistic="Average",
    Threshold="85",
    MetricName="CPUUtilization",
))

CraftLaunchConfig = t.add_resource(LaunchConfiguration(
    "CraftLaunchConfig",
    UserData=Base64(Join("", ["#!/usr/bin/env bash\n", "export PROJECT=", "sheltermutual", "\n", "export ROLE=", "craft", "\nexport ENV=", Ref(Environment), "\n", "export SNS_TOPIC=", Ref(SnsTopic), "\n", "if [ $(which apt-get) ] ; then", "\n", "export DEBIAN_FRONTEND=noninteractive", "\n", "apt-get update", "\n", "apt-get -y install python-pip", "\n", "elif [ $(which yum) ] ; then", "\n", "if [ -e /etc/redhat-release ]; then", "\n", "yum -y install wget", "\n", "RELEASE=$(cut -d ' ' -f 7 /etc/redhat-release | cut -d '.' -f 1)", "\n", "wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-${RELEASE}.noarch.rpm", "\n", "rpm -Uvh epel-release*.rpm", "\n", "else", "\n", "yum -y install epel-release", "\n", "fi", "\n", "yum makecache fast", "\n", "yum -y install python-pip", "\n", "fi", "\n", "pip install --upgrade awscli", "\n", "aws s3 cp s3://", "shelter-mutual-aws-tools-us-east-1/bootstrap", "/", "craft", ".sh", " /usr/local/bin/", "craft", ".sh", " --region ", Ref("AWS::Region"), " \n", "chmod 770 /usr/local/bin/", "craft", ".sh", " \n", "/usr/local/bin/", "craft", ".sh", "\n"])),
    ImageId=Ref(AmiId),
    BlockDeviceMappings=[{ "DeviceName": "/dev/sda1", "Ebs": { "DeleteOnTermination": "true", "VolumeType": "gp2", "VolumeSize": 10 } }],
    KeyName="common-us-east-1",
    SecurityGroups=[Ref(InstanceSecurityGroups)],
    IamInstanceProfile=Ref(IamInstanceProfile),
    InstanceType=Ref(InstanceType),
    AssociatePublicIpAddress="false",
))

print(t.to_json())
