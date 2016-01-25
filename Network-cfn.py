from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.rds import DBSubnetGroup
from troposphere.ec2 import DHCPOptions
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import Route
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import SubnetNetworkAclAssociation
from troposphere.ec2 import SecurityGroup
from troposphere.ec2 import EIP
from troposphere.ec2 import Subnet
from troposphere.ec2 import NetworkAclEntry
from troposphere.ec2 import VPC
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.ec2 import VPCDHCPOptionsAssociation
from troposphere.ec2 import EIPAssociation
from troposphere.ec2 import RouteTable
from troposphere.ec2 import NetworkInterface
from troposphere.ec2 import NetworkAcl


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Network""")
t.add_mapping("SubnetMap",
{u'TEST-PRIVATE-AZ1': {u'CIDR': u'192.168.129.128/25'},
 u'TEST-PRIVATE-AZ2': {u'CIDR': u'192.168.130.0/25'},
 u'TEST-PRIVATE-AZ3': {u'CIDR': u'192.168.130.128/25'},
 u'TEST-PUBLIC-AZ1': {u'CIDR': u'192.168.128.0/25'},
 u'TEST-PUBLIC-AZ2': {u'CIDR': u'192.168.128.128/25'},
 u'TEST-PUBLIC-AZ3': {u'CIDR': u'192.168.129.0/25'},
 u'TEST-RDS-AZ1': {u'CIDR': u'192.168.131.0/25'},
 u'TEST-RDS-AZ2': {u'CIDR': u'192.168.131.128/25'},
 u'TEST-RDS-AZ3': {u'CIDR': u'192.168.132.0/25'},
 u'VPC': {u'CIDR': u'192.168.128.0/21'}}
)

RdsSubnetGroupTest = t.add_resource(DBSubnetGroup(
    "RdsSubnetGroupTest",
    SubnetIds=[Ref("SubnetTestRdsAz1"), Ref("SubnetTestRdsAz2"), Ref("SubnetTestRdsAz3")],
    DBSubnetGroupDescription="Subnets for RDS Test",
))

DhcpOptions = t.add_resource(DHCPOptions(
    "DhcpOptions",
    Tags=Tags(
        Name="VPC_DHCP",
        project="ShelterMutual",
    ),
    DomainNameServers=["AmazonProvidedDNS"],
    DomainName="sheltermutual-aws.internal",
))

PrivateSubnetRouteTableAssociationSubnetTestRdsAz1 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestRdsAz1",
    SubnetId=Ref("SubnetTestRdsAz1"),
    RouteTableId=Ref("PrivateRouteTableAz1"),
))

PublicRoute = t.add_resource(Route(
    "PublicRoute",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("PublicRouteTable"),
    DependsOn="AttachGateway",
))

PrivateSubnetRouteTableAssociationSubnetTestRdsAz3 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestRdsAz3",
    SubnetId=Ref("SubnetTestRdsAz3"),
    RouteTableId=Ref("PrivateRouteTableAz3"),
))

PrivateSubnetRouteTableAssociationSubnetTestRdsAz2 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestRdsAz2",
    SubnetId=Ref("SubnetTestRdsAz2"),
    RouteTableId=Ref("PrivateRouteTableAz2"),
))

InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        project="ShelterMutual",
    ),
))

RdsNaclAssociationTestAz2 = t.add_resource(SubnetNetworkAclAssociation(
    "RdsNaclAssociationTestAz2",
    SubnetId=Ref("SubnetTestRdsAz2"),
    NetworkAclId=Ref("RdsTestNacl"),
))

RdsNaclAssociationTestAz3 = t.add_resource(SubnetNetworkAclAssociation(
    "RdsNaclAssociationTestAz3",
    SubnetId=Ref("SubnetTestRdsAz3"),
    NetworkAclId=Ref("RdsTestNacl"),
))

RdsNaclAssociationTestAz1 = t.add_resource(SubnetNetworkAclAssociation(
    "RdsNaclAssociationTestAz1",
    SubnetId=Ref("SubnetTestRdsAz1"),
    NetworkAclId=Ref("RdsTestNacl"),
))

NatSecurityGroup = t.add_resource(SecurityGroup(
    "NatSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "-1", "FromPort": "-1", "IpProtocol": "icmp", "CidrIp": "192.168.128.0/21" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "udp", "CidrIp": "192.168.128.0/21" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "tcp", "CidrIp": "192.168.128.0/21" }],
    VpcId=Ref("VPC"),
    GroupDescription="Enable communication to NAT Gateway(s).",
    SecurityGroupEgress=[{ "ToPort": "-1", "FromPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "udp", "CidrIp": "0.0.0.0/0" }, { "ToPort": "65535", "FromPort": "0", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0" }],
))

EipNatAz3 = t.add_resource(EIP(
    "EipNatAz3",
    Domain="vpc",
))

SubnetTestPrivateAz3 = t.add_resource(Subnet(
    "SubnetTestPrivateAz3",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ3", "CIDR"),
    AvailabilityZone=Select("2", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPrivateAz3",
        project="ShelterMutual",
    ),
))

SubnetTestPrivateAz2 = t.add_resource(Subnet(
    "SubnetTestPrivateAz2",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ2", "CIDR"),
    AvailabilityZone=Select("1", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPrivateAz2",
        project="ShelterMutual",
    ),
))

SubnetTestPublicAz1 = t.add_resource(Subnet(
    "SubnetTestPublicAz1",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PUBLIC-AZ1", "CIDR"),
    AvailabilityZone=Select("0", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPublicAz1",
        project="ShelterMutual",
    ),
))

SubnetTestPublicAz2 = t.add_resource(Subnet(
    "SubnetTestPublicAz2",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PUBLIC-AZ2", "CIDR"),
    AvailabilityZone=Select("1", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPublicAz2",
        project="ShelterMutual",
    ),
))

SubnetTestPublicAz3 = t.add_resource(Subnet(
    "SubnetTestPublicAz3",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PUBLIC-AZ3", "CIDR"),
    AvailabilityZone=Select("2", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPublicAz3",
        project="ShelterMutual",
    ),
))

PrivateSubnetRouteTableAssociationSubnetTestPrivateAz1 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestPrivateAz1",
    SubnetId=Ref("SubnetTestPrivateAz1"),
    RouteTableId=Ref("PrivateRouteTableAz1"),
))

SubnetTestPrivateAz1 = t.add_resource(Subnet(
    "SubnetTestPrivateAz1",
    VpcId=Ref("VPC"),
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ1", "CIDR"),
    AvailabilityZone=Select("0", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestPrivateAz1",
        project="ShelterMutual",
    ),
))

PrivateSubnetRouteTableAssociationSubnetTestPrivateAz3 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestPrivateAz3",
    SubnetId=Ref(SubnetTestPrivateAz3),
    RouteTableId=Ref("PrivateRouteTableAz3"),
))

PrivateSubnetRouteTableAssociationSubnetTestPrivateAz2 = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnetRouteTableAssociationSubnetTestPrivateAz2",
    SubnetId=Ref(SubnetTestPrivateAz2),
    RouteTableId=Ref("PrivateRouteTableAz2"),
))

RdsTestNaclEngress100 = t.add_resource(NetworkAclEntry(
    "RdsTestNaclEngress100",
    NetworkAclId=Ref("RdsTestNacl"),
    RuleNumber="100",
    Protocol="-1",
    Egress="true",
    RuleAction="Allow",
    CidrBlock="0.0.0.0/0",
))

EipNatAz2 = t.add_resource(EIP(
    "EipNatAz2",
    Domain="vpc",
))

EipNatAz1 = t.add_resource(EIP(
    "EipNatAz1",
    Domain="vpc",
))

VPC = t.add_resource(VPC(
    "VPC",
    EnableDnsSupport="true",
    CidrBlock=FindInMap("SubnetMap", "VPC", "CIDR"),
    EnableDnsHostnames="true",
    Tags=Tags(
        Name="ShelterMutual",
        project="ShelterMutual",
    ),
))

SubnetTestRdsAz3 = t.add_resource(Subnet(
    "SubnetTestRdsAz3",
    VpcId=Ref(VPC),
    CidrBlock=FindInMap("SubnetMap", "TEST-RDS-AZ3", "CIDR"),
    AvailabilityZone=Select("2", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestRdsAz3",
        project="ShelterMutual",
    ),
))

SubnetTestRdsAz2 = t.add_resource(Subnet(
    "SubnetTestRdsAz2",
    VpcId=Ref(VPC),
    CidrBlock=FindInMap("SubnetMap", "TEST-RDS-AZ2", "CIDR"),
    AvailabilityZone=Select("1", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestRdsAz2",
        project="ShelterMutual",
    ),
))

SubnetTestRdsAz1 = t.add_resource(Subnet(
    "SubnetTestRdsAz1",
    VpcId=Ref(VPC),
    CidrBlock=FindInMap("SubnetMap", "TEST-RDS-AZ1", "CIDR"),
    AvailabilityZone=Select("0", GetAZs("")),
    Tags=Tags(
        Name="SubnetTestRdsAz1",
        project="ShelterMutual",
    ),
))

RdsTestNaclIngress200 = t.add_resource(NetworkAclEntry(
    "RdsTestNaclIngress200",
    NetworkAclId=Ref("RdsTestNacl"),
    RuleNumber="200",
    Protocol="6",
    PortRange=PortRange(To="3306", From="3306"),
    Egress="false",
    RuleAction="allow",
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ2", "CIDR"),
))

AttachGateway = t.add_resource(VPCGatewayAttachment(
    "AttachGateway",
    VpcId=Ref(VPC),
    InternetGatewayId=Ref(InternetGateway),
))

RdsTestNaclIngress300 = t.add_resource(NetworkAclEntry(
    "RdsTestNaclIngress300",
    NetworkAclId=Ref("RdsTestNacl"),
    RuleNumber="300",
    Protocol="6",
    PortRange=PortRange(To="3306", From="3306"),
    Egress="false",
    RuleAction="allow",
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ3", "CIDR"),
))

PrivateRouteAz1 = t.add_resource(Route(
    "PrivateRouteAz1",
    DestinationCidrBlock="0.0.0.0/0",
    NetworkInterfaceId=Ref("EniNatAz1"),
    RouteTableId=Ref("PrivateRouteTableAz1"),
))

PrivateRouteAz2 = t.add_resource(Route(
    "PrivateRouteAz2",
    DestinationCidrBlock="0.0.0.0/0",
    NetworkInterfaceId=Ref("EniNatAz2"),
    RouteTableId=Ref("PrivateRouteTableAz2"),
))

PrivateRouteAz3 = t.add_resource(Route(
    "PrivateRouteAz3",
    DestinationCidrBlock="0.0.0.0/0",
    NetworkInterfaceId=Ref("EniNatAz3"),
    RouteTableId=Ref("PrivateRouteTableAz3"),
))

DhcpOptionsAssociation = t.add_resource(VPCDHCPOptionsAssociation(
    "DhcpOptionsAssociation",
    VpcId=Ref(VPC),
    DhcpOptionsId=Ref(DhcpOptions),
))

PublicSubnetRouteTableAssociationSubnetTestPublicAz1 = t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnetRouteTableAssociationSubnetTestPublicAz1",
    SubnetId=Ref(SubnetTestPublicAz1),
    RouteTableId=Ref("PublicRouteTable"),
))

PublicSubnetRouteTableAssociationSubnetTestPublicAz3 = t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnetRouteTableAssociationSubnetTestPublicAz3",
    SubnetId=Ref(SubnetTestPublicAz3),
    RouteTableId=Ref("PublicRouteTable"),
))

PublicSubnetRouteTableAssociationSubnetTestPublicAz2 = t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnetRouteTableAssociationSubnetTestPublicAz2",
    SubnetId=Ref(SubnetTestPublicAz2),
    RouteTableId=Ref("PublicRouteTable"),
))

EipAssociationNatAz3 = t.add_resource(EIPAssociation(
    "EipAssociationNatAz3",
    NetworkInterfaceId=Ref("EniNatAz3"),
    AllocationId=GetAtt(EipNatAz3, "AllocationId"),
))

EipAssociationNatAz2 = t.add_resource(EIPAssociation(
    "EipAssociationNatAz2",
    NetworkInterfaceId=Ref("EniNatAz2"),
    AllocationId=GetAtt(EipNatAz2, "AllocationId"),
))

EipAssociationNatAz1 = t.add_resource(EIPAssociation(
    "EipAssociationNatAz1",
    NetworkInterfaceId=Ref("EniNatAz1"),
    AllocationId=GetAtt(EipNatAz1, "AllocationId"),
))

PublicRouteTable = t.add_resource(RouteTable(
    "PublicRouteTable",
    VpcId=Ref(VPC),
    Tags=Tags(
        Name="PublicRouteTable",
    ),
))

EniNatAz3 = t.add_resource(NetworkInterface(
    "EniNatAz3",
    SubnetId=Ref(SubnetTestPublicAz3),
    GroupSet=[Ref(NatSecurityGroup)],
    Description="Network Interface for Nat in AZ3",
    Tags=Tags(
        Name="NatAZ3",
        project="ShelterMutual",
    ),
))

EniNatAz2 = t.add_resource(NetworkInterface(
    "EniNatAz2",
    SubnetId=Ref(SubnetTestPublicAz2),
    GroupSet=[Ref(NatSecurityGroup)],
    Description="Network Interface for Nat in AZ2",
    Tags=Tags(
        Name="NatAZ2",
        project="ShelterMutual",
    ),
))

EniNatAz1 = t.add_resource(NetworkInterface(
    "EniNatAz1",
    SubnetId=Ref(SubnetTestPublicAz1),
    GroupSet=[Ref(NatSecurityGroup)],
    Description="Network Interface for Nat in AZ1",
    Tags=Tags(
        Name="NatAZ1",
        project="ShelterMutual",
    ),
))

PrivateRouteTableAz3 = t.add_resource(RouteTable(
    "PrivateRouteTableAz3",
    VpcId=Ref(VPC),
    Tags=Tags(
        Name="PrivateRouteTableAz3",
    ),
))

PrivateRouteTableAz2 = t.add_resource(RouteTable(
    "PrivateRouteTableAz2",
    VpcId=Ref(VPC),
    Tags=Tags(
        Name="PrivateRouteTableAz2",
    ),
))

PrivateRouteTableAz1 = t.add_resource(RouteTable(
    "PrivateRouteTableAz1",
    VpcId=Ref(VPC),
    Tags=Tags(
        Name="PrivateRouteTableAz1",
    ),
))

RdsTestNaclIngress100 = t.add_resource(NetworkAclEntry(
    "RdsTestNaclIngress100",
    NetworkAclId=Ref("RdsTestNacl"),
    RuleNumber="100",
    Protocol="6",
    PortRange=PortRange(To="3306", From="3306"),
    Egress="false",
    RuleAction="allow",
    CidrBlock=FindInMap("SubnetMap", "TEST-PRIVATE-AZ1", "CIDR"),
))

RdsTestNacl = t.add_resource(NetworkAcl(
    "RdsTestNacl",
    VpcId=Ref(VPC),
    Tags=Tags(
        Name="RdsTest",
        project="ShelterMutual",
    ),
))

SubnetTestPrivateAz2Id = t.add_output(Output(
    "SubnetTestPrivateAz2Id",
    Description="SubnetTestPrivateAz2 ID",
    Value=Ref(SubnetTestPrivateAz2),
))

SubnetTestRdsAz2Id = t.add_output(Output(
    "SubnetTestRdsAz2Id",
    Description="SubnetTestRdsAz2 ID",
    Value=Ref(SubnetTestRdsAz2),
))

SubnetTestPrivateAz1Id = t.add_output(Output(
    "SubnetTestPrivateAz1Id",
    Description="SubnetTestPrivateAz1 ID",
    Value=Ref(SubnetTestPrivateAz1),
))

SubnetTestPublicAz1Id = t.add_output(Output(
    "SubnetTestPublicAz1Id",
    Description="SubnetTestPublicAz1 ID",
    Value=Ref(SubnetTestPublicAz1),
))

SubnetTestRdsAz3Id = t.add_output(Output(
    "SubnetTestRdsAz3Id",
    Description="SubnetTestRdsAz3 ID",
    Value=Ref(SubnetTestRdsAz3),
))

SubnetTestPrivateAz3Id = t.add_output(Output(
    "SubnetTestPrivateAz3Id",
    Description="SubnetTestPrivateAz3 ID",
    Value=Ref(SubnetTestPrivateAz3),
))

VpcId = t.add_output(Output(
    "VpcId",
    Description="VPC ID",
    Value=Ref(VPC),
))

SubnetTestPublicAz3Id = t.add_output(Output(
    "SubnetTestPublicAz3Id",
    Description="SubnetTestPublicAz3 ID",
    Value=Ref(SubnetTestPublicAz3),
))

SubnetTestRdsAz1Id = t.add_output(Output(
    "SubnetTestRdsAz1Id",
    Description="SubnetTestRdsAz1 ID",
    Value=Ref(SubnetTestRdsAz1),
))

SubnetTestPublicAz2Id = t.add_output(Output(
    "SubnetTestPublicAz2Id",
    Description="SubnetTestPublicAz2 ID",
    Value=Ref(SubnetTestPublicAz2),
))

NatSecurityGroupId = t.add_output(Output(
    "NatSecurityGroupId",
    Description="NAT Security Group ID",
    Value=Ref(NatSecurityGroup),
))

print(t.to_json())
