from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.ec2 import SecurityGroup


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Security Groups""")
VpcId = t.add_parameter(Parameter(
    "VpcId",
    Default="",
    Type="String",
    Description="VPC ID",
))


craftElbSecurityGroup = t.add_resource(SecurityGroup(
    "craftElbSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": 80, "FromPort": 80, "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }, { "ToPort": 443, "FromPort": 443, "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
    VpcId=Ref(VpcId),
    GroupDescription="Enable communication to craftElb",
    SecurityGroupEgress=[{ "ToPort": -1, "FromPort": -1, "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0" }, { "ToPort": 65535, "FromPort": 0, "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": 65535, "FromPort": 0, "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
))

BastionSecurityGroup = t.add_resource(SecurityGroup(
    "BastionSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "22", "FromPort": "22", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
    VpcId=Ref(VpcId),
    GroupDescription="Enable communication to bastion host(s).",
    SecurityGroupEgress=[{ "ToPort": "-1", "FromPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
))

VpnSecurityGroup = t.add_resource(SecurityGroup(
    "VpnSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "22", "FromPort": "22", "IpProtocol": "tcp", "CidrIp": "192.168.128.0/21" }, { "ToPort": "51", "FromPort": "50", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "500", "FromPort": "500", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "4500", "FromPort": "4500", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }],
    VpcId=Ref(VpcId),
    GroupDescription="Enable communication to Vpn and VPC.",
    SecurityGroupEgress=[{ "ToPort": "-1", "FromPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
))

craftSecurityGroup = t.add_resource(SecurityGroup(
    "craftSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": 22, "FromPort": 22, "IpProtocol": "tcp", "CidrIp": "192.168.128.0/21" }, { "ToPort": 80, "FromPort": 80, "IpProtocol": "tcp", "CidrIp": "192.168.128.0/21" }, { "ToPort": 443, "FromPort": 443, "IpProtocol": "tcp", "CidrIp": "192.168.128.0/21" }],
    VpcId=Ref(VpcId),
    GroupDescription="Enable communication to craft",
    SecurityGroupEgress=[{ "ToPort": -1, "FromPort": -1, "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0" }, { "ToPort": 65535, "FromPort": 0, "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": 65535, "FromPort": 0, "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
))

craftSecurityGroupId = t.add_output(Output(
    "craftSecurityGroupId",
    Description="craftSecurityGroup ID",
    Value=Ref(craftSecurityGroup),
))

VpnSecurityGroupId = t.add_output(Output(
    "VpnSecurityGroupId",
    Description="Vpn Security Group ID",
    Value=Ref(VpnSecurityGroup),
))

craftElbSecurityGroupId = t.add_output(Output(
    "craftElbSecurityGroupId",
    Description="craftElbSecurityGroup ID",
    Value=Ref(craftElbSecurityGroup),
))


BastionSecurityGroupId = t.add_output(Output(
    "BastionSecurityGroupId",
    Description="Bastion Security Group ID",
    Value=Ref(BastionSecurityGroup),
))

print(t.to_json())
