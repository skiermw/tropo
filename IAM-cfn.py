from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.iam import InstanceProfile
from troposphere.iam import Role
from troposphere.iam import Group


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
IAM""")
craftInstanceProfile = t.add_resource(InstanceProfile(
    "craftInstanceProfile",
    Path="/",
    Roles=[Ref("craftIamRole")],
))

BastionInstanceProfile = t.add_resource(InstanceProfile(
    "BastionInstanceProfile",
    Path="/",
    Roles=[Ref("BastionIamRole")],
))

BastionIamRole = t.add_resource(Role(
    "BastionIamRole",
    Path="/",
    Policies=[{ "PolicyName": "BastionPolicy", "PolicyDocument": { "Statement": [{ "Action": ["elasticloadbalancing:DescribeLoadBalancers"], "Resource": "*", "Effect": "Allow", "Sid": "AllowDescribeLoadBalancers" }, { "Action": ["s3:ListAllMyBuckets"], "Resource": "*", "Effect": "Allow", "Sid": "AllowS3ListAllMyBuckets" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "Effect": "Allow", "Sid": "AllowS3BootstrapBucket" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "/*"]), "Effect": "Allow", "Sid": "AllowS3BootstrapObjects" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/pkg", "Effect": "Allow", "Sid": "AllowS3Pkg" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/pkg", "/*"]), "Effect": "Allow", "Sid": "AllowS3PkgObjects" }, { "Action": ["sns:Publish"], "Resource": "*", "Effect": "Allow", "Sid": "AllowSNSPublish" }] } }],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["ec2.amazonaws.com"] } }] },
))

NatInstanceProfile = t.add_resource(InstanceProfile(
    "NatInstanceProfile",
    Path="/",
    Roles=[Ref("NatIamRole")],
))

NatIamRole = t.add_resource(Role(
    "NatIamRole",
    Path="/",
    Policies=[{ "PolicyName": "NatPolicy", "PolicyDocument": { "Statement": [{ "Action": ["ec2:AttachNetworkInterface", "ec2:DescribeNetworkInterfaceAttribute", "ec2:ModifyNetworkInterfaceAttribute", "ec2:DescribeNetworkInterfaces", "ec2:DetachNetworkInterface"], "Resource": "*", "Effect": "Allow", "Sid": "AllowENIManipulation" }, { "Action": ["ec2:ModifyInstanceAttribute"], "Resource": "*", "Effect": "Allow", "Sid": "AllowModifyInstanceAttribute" }, { "Action": ["ec2:DescribeTags"], "Resource": "*", "Effect": "Allow", "Sid": "AllowDescribeTags" }, { "Action": ["elasticloadbalancing:DescribeLoadBalancers"], "Resource": "*", "Effect": "Allow", "Sid": "AllowDescribeLoadBalancers" }, { "Action": ["s3:ListAllMyBuckets"], "Resource": "*", "Effect": "Allow", "Sid": "AllowS3ListAllMyBuckets" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "Effect": "Allow", "Sid": "AllowS3BootstrapBucket" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "/*"]), "Effect": "Allow", "Sid": "AllowS3BootstrapObjects" }, { "Action": ["sns:Publish"], "Resource": "*", "Effect": "Allow", "Sid": "AllowSNSPublish" }] } }],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["ec2.amazonaws.com"] } }] },
))

ClientGroup = t.add_resource(Group(
    "ClientGroup",
    Policies=[{ "PolicyName": "ClientGroupPolicy", "PolicyDocument": { "Statement": [{ "Action": "*", "Resource": "*", "Effect": "Allow", "Sid": "AllowAll" }, { "Action": ["aws-portal:ViewBilling", "aws-portal:ViewUsage"], "Resource": "*", "Effect": "Deny", "Sid": "DenyBilling" }, { "Action": ["ec2:PurchaseReservedInstancesOffering"], "Resource": "*", "Effect": "Deny", "Sid": "DenyPurchaseReservedInstancesOffering" }, { "Action": ["rds:PurchaseReservedDBInstancesOffering"], "Resource": "*", "Effect": "Deny", "Sid": "DenyPurchaseReservedDBInstancesOffering" }, { "Action": ["redshift:PurchaseReservedNodeOffering"], "Resource": "*", "Effect": "Deny", "Sid": "DenyPurchaseReservedNodeOffering" }, { "Action": "cloudtrail:*", "Resource": "*", "Effect": "Deny", "Sid": "DenyCloudtrail" }, { "Action": ["iam:AddRoleToInstanceProfile", "iam:AddUserToGroup", "iam:CreateAccessKey", "iam:CreateAccountAlias", "iam:CreateGroup", "iam:CreateInstanceProfile", "iam:CreateLoginProfile", "iam:CreateSAMLProvider", "iam:CreateUser", "iam:DeleteAccessKey", "iam:DeleteAccountAlias", "iam:DeleteAccountPasswordPolicy", "iam:DeleteGroup", "iam:DeleteGroupPolicy", "iam:DeleteInstanceProfile", "iam:DeleteLoginProfile", "iam:DeleteRole", "iam:DeleteRolePolicy", "iam:DeleteSAMLProvider", "iam:DeleteServerCertificate", "iam:DeleteSigningCertificate", "iam:DeleteUser", "iam:DeleteUserPolicy", "iam:DeleteVirtualMFADevice", "iam:GetAccountPasswordPolicy", "iam:GetAccountSummary", "iam:GetGroup", "iam:GetGroupPolicy", "iam:GetInstanceProfile", "iam:GetLoginProfile", "iam:GetSAMLProvider", "iam:GetServerCertificate", "iam:GetUser", "iam:GetUserPolicy", "iam:ListAccessKeys", "iam:ListAccountAliases", "iam:ListGroupPolicies", "iam:ListGroups", "iam:ListGroupsForUser", "iam:ListInstanceProfiles", "iam:ListInstanceProfilesForRole", "iam:ListSAMLProviders", "iam:ListServerCertificates", "iam:ListSigningCertificates", "iam:ListUserPolicies", "iam:PutGroupPolicy", "iam:PutRolePolicy", "iam:PutUserPolicy", "iam:RemoveRoleFromInstanceProfile", "iam:RemoveUserFromGroup", "iam:UpdateAccessKey", "iam:UpdateAccountPasswordPolicy", "iam:UpdateAssumeRolePolicy", "iam:UpdateGroup", "iam:UpdateLoginProfile", "iam:UpdateSAMLProvider", "iam:UpdateServerCertificate", "iam:UpdateSigningCertificate", "iam:UpdateUser", "iam:UploadServerCertificate", "iam:UploadSigningCertificate"], "Resource": ["*"], "Effect": "Deny", "Sid": "DenyIAM" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-cloudtrail-us-east-1", "Effect": "Deny", "Sid": "DenyS3CloudtrailBucket" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-cloudtrail-us-east-1", "/*"]), "Effect": "Deny", "Sid": "DenyS3CloudtrailObjects" }] } }],
))

craftIamRole = t.add_resource(Role(
    "craftIamRole",
    Path="/",
    Policies=[{ "PolicyName": "craftPolicy", "PolicyDocument": { "Statement": [{ "Action": ["elasticloadbalancing:DescribeLoadBalancers"], "Resource": "*", "Effect": "Allow", "Sid": "AllowDescribeLoadBalancers" }, { "Action": ["s3:ListAllMyBuckets"], "Resource": "*", "Effect": "Allow", "Sid": "AllowS3ListAllMyBuckets" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "Effect": "Allow", "Sid": "AllowS3BootstrapBucket" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/bootstrap", "/*"]), "Effect": "Allow", "Sid": "AllowS3BootstrapObjects" }, { "Action": "s3:*", "Resource": "arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/pkg", "Effect": "Allow", "Sid": "AllowS3Pkg" }, { "Action": "s3:*", "Resource": Join("", ["arn:aws:s3:::shelter-mutual-aws-tools-us-east-1/pkg", "/*"]), "Effect": "Allow", "Sid": "AllowS3PkgObjects" }, { "Action": "cloudwatch:*", "Resource": "*", "Effect": "Allow", "Sid": "AllowCloudWatch" }, { "Action": ["sns:Publish"], "Resource": "*", "Effect": "Allow", "Sid": "AllowSNSPublish" }, { "Action": ["s3:*"], "Resource": ["arn:aws:s3:::"], "Effect": "Allow", "Sid": "AllowS3Code" }, { "Action": ["s3:*"], "Resource": ["arn:aws:s3:::/*"], "Effect": "Allow", "Sid": "AllowS3CodeObjects" }] } }],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["ec2.amazonaws.com"] } }] },
))

NatInstanceProfile = t.add_output(Output(
    "NatInstanceProfile",
    Description="NAT IAM Instance Profile",
    Value=Ref(NatInstanceProfile),
))

craftInstanceProfile = t.add_output(Output(
    "craftInstanceProfile",
    Description="craft IAM Instance Profile",
    Value=Ref(craftInstanceProfile),
))

BastionInstanceProfile = t.add_output(Output(
    "BastionInstanceProfile",
    Description="Bastion IAM Instance Profile",
    Value=Ref(BastionInstanceProfile),
))

print(t.to_json())
