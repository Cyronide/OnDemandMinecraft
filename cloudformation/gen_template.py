from troposphere import (Base64, FindInMap, GetAtt, Join, Parameter, Ref, Sub,
                         Tags, Template, constants)

from troposphere.ec2 import (SecurityGroup, SecurityGroupEgress,
                             SecurityGroupIngress, Instance)

###########################################
#                 Constants
###########################################

ref_stack_id = Ref('AWS::StackId')
ref_region = Ref('AWS::Region')
ref_stack_name = Ref('AWS::StackName')

GIT_URL = 'https://github.com/Cyronide/OnDemandMinecraft.git'

t = Template()
c = constants
t.set_version()
t.add_description(
    "A template for deploying an OnDemandMinecraft instance: {}".format(
        GIT_URL
    )
)

###########################################
#                 Mappings
###########################################

t.add_mapping('InstanceAmiMap', {
    c.AP_EAST_1: {'AMI': 'ami-52760d23'},
    c.AP_NORTHEAST_1: {'AMI': 'ami-09b68f5653871885f'},
    c.AP_NORTHEAST_2: {'AMI': 'ami-0794a2d1e6d99117a'},
    c.AP_NORTHEAST_3: {'AMI': 'ami-0d797f6385021e49c'},
    c.AP_SOUTH_1: {'AMI': 'ami-04125d804acca5692'},
    c.AP_SOUTHEAST_1: {'AMI': 'ami-0bb35a5dad5658286'},
    c.AP_SOUTHEAST_2: {'AMI': 'ami-06705195ce845509c'},
    c.CA_CENTRAL_1: {'AMI': 'ami-0c2a0ac8b164db9e6'},
    c.CN_NORTH_1: {'AMI': 'ami-04060e657afb51a27'},
    c.CN_NORTHWEST_1: {'AMI': 'ami-0b92d6766d8e7fac0'},
    c.EU_CENTRAL_1: {'AMI': 'ami-009c174642dba28e4	'},
    c.EU_NORTH_1: {'AMI': 'ami-88de55f6'},
    c.EU_WEST_1: {'AMI': 'ami-01e6a0b85de033c99'},
    c.EU_WEST_2: {'AMI': 'ami-0c30afcb7ab02233d'},
    c.EU_WEST_3: {'AMI': 'ami-0119667e27598718e'},
    c.SA_EAST_1: {'AMI': 'ami-0dcf15c37a41c965f'},
    c.US_EAST_1: {'AMI': 'ami-026c8acd92718196b'},
    c.US_EAST_2: {'AMI': 'ami-0986c2ac728528ac2'},
    c.US_WEST_1: {'AMI': 'ami-068670db424b01e9a'},
    c.US_WEST_2: {'AMI': 'ami-07b4f3c02c7f83d59'},
    c.US_GOV_WEST_1: {'AMI': 'ami-f73c4696'},
    c.US_GOV_EAST_1: {'AMI': 'ami-bdd233cc'},
})

###########################################
#                Parameters
###########################################

vpc = t.add_parameter(Parameter(
    'VPC',
    Description='VPC in which the server will be deployed.',
    Type=constants.VPC_ID,
))

ssh_keypair = t.add_parameter(Parameter(
    'SshKeypair',
    Description='SSH keypair that the instance will be deployed with.',
    Type=constants.KEY_PAIR_NAME,
))

instance_type = t.add_parameter(Parameter(
    'InstanceType',
    Description='The EC2 instance type.',
    Default='t3.small',
    Type='String',
    AllowedValues=[
        't3.micro', 't3.small',
        't3.small', 't3.medium',
        't3.large', 't3.xlarge',
    ],
))
t.set_parameter_label(instance_type, 'Instance Type')

###########################################
#             Security Group
###########################################

ec2_security_group = t.add_resource(SecurityGroup(
    'Ec2SecurityGroup',
    VpcId=Ref(vpc),
    GroupDescription='Security group for Minecraft EC2 instance.',
    Tags=Tags(
        Name=Sub('$minecraft-sg'),
    )
))

ec2_minecraft_tcp_ingress = t.add_resource(SecurityGroupIngress(
    'Ec2MinecraftTcpIngress',
    DependsOn='Ec2SecurityGroup',
    ToPort='25565',
    FromPort='25565',
    IpProtocol='tcp',
    GroupId=Ref(ec2_security_group),
    CidrIp=c.QUAD_ZERO,
))

ec2_minecraft_udp_ingress = t.add_resource(SecurityGroupIngress(
    'Ec2MinecraftUdpIngress',
    DependsOn='Ec2SecurityGroup',
    ToPort='25565',
    FromPort='25565',
    IpProtocol='udp',
    GroupId=Ref(ec2_security_group),
    CidrIp=c.QUAD_ZERO,
))

ec2_ssh_ingress = t.add_resource(SecurityGroupIngress(
    'Ec2SshIngress',
    DependsOn='Ec2SecurityGroup',
    ToPort='22',
    FromPort='22',
    IpProtocol='tcp',
    GroupId=Ref(ec2_security_group),
    CidrIp=c.QUAD_ZERO,
))

ec2_egress = t.add_resource(SecurityGroupEgress(
    'Ec2Egress',
    DependsOn='Ec2SecurityGroup',
    ToPort='-1',
    IpProtocol='-1',
    GroupId=Ref(ec2_security_group),
    CidrIp=c.QUAD_ZERO,
))

###########################################
#             EC2 Instance
###########################################

server_instance = t.add_resource(Instance(
    'ServerInstance',
    DependsOn=['Ec2SecurityGroup'],
    SourceDestCheck='false',
    SecurityGroupIds=[Ref(ec2_security_group)],
    ImageId=FindInMap(
        'InstanceAmiMap',
        Ref('AWS::Region'),
        'AMI'
    ),
    InstanceType=Ref(instance_type),
    KeyName=Ref(ssh_keypair),
    UserData=Base64(
        Join('',
            [
                '#!/bin/bash -xe\n',
                'cd /home/ubuntu && git clone {git_url} && '
                '/home/ubuntu/OnDemandMinecraft/instancesetup/bootstrap.sh\n'.format(
                    git_url=GIT_URL,
                )
            ]
        )
    ),
    Tags=Tags(
        Name=Sub('minecraft-instance'),
    )
))

print(t.to_json())
