import boto3
import time
from botocore.exceptions import ClientError
from config import *

# Initialize boto3 clients with the specific region
ec2 = boto3.resource('ec2', region_name=AWS_REGION)
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
iam_client = boto3.client('iam', region_name=AWS_REGION)

def create_vpc():
    print("[INFO] Creating VPC...")
    vpc = ec2.create_vpc(CidrBlock=VPC_CIDR)
    vpc.create_tags(Tags=[{"Key": "Name", "Value": VPC_NAME}])
    vpc.wait_until_available()
    print(f"[SUCCESS] VPC created with ID: {vpc.id}")
    return vpc

def create_subnet(vpc, cidr, name, public=True):
    print(f"[INFO] Creating {'Public' if public else 'Private'} Subnet {name}...")
    subnet = ec2.create_subnet(
        VpcId=vpc.id,
        CidrBlock=cidr,
        AvailabilityZone=f"{AWS_REGION}a"
    )
    subnet.create_tags(Tags=[{"Key": "Name", "Value": name}])
    print(f"[SUCCESS] Subnet {name} created: {subnet.id}")
    return subnet

def create_internet_gateway(vpc):
    print("[INFO] Creating Internet Gateway...")
    igw = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    print(f"[SUCCESS] Internet Gateway attached: {igw.id}")
    return igw

def create_route_table(subnet, vpc, igw=None, nat_instance=None):
    print(f"[INFO] Creating route table for subnet {subnet.id}...")
    route_table = vpc.create_route_table()
    if igw:
        route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
    elif nat_instance:
        route_table.create_route(DestinationCidrBlock='0.0.0.0/0', InstanceId=nat_instance.id)
    route_table.associate_with_subnet(SubnetId=subnet.id)
    print(f"[SUCCESS] Route table associated with subnet {subnet.id}")
    return route_table

def create_security_group(vpc, name, description, ingress_rules):
    print(f"[INFO] Creating security group {name}...")
    sg = ec2.create_security_group(GroupName=name, Description=description, VpcId=vpc.id)
    for rule in ingress_rules:
        sg.authorize_ingress(**rule)
    print(f"[SUCCESS] Security group {name} created: {sg.id}")
    return sg

def launch_instance(subnet, sg, name, ami=AMI_ID, key_name=KEY_NAME, public_ip=False):
    print(f"[INFO] Launching instance {name}...")
    instances = ec2.create_instances(
        ImageId=ami,
        InstanceType=INSTANCE_TYPE,
        KeyName=key_name,
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[{
            'SubnetId': subnet.id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': public_ip,
            'Groups': [sg.id]
        }],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    instance = instances[0]
    instance.wait_until_running()
    instance.reload()
    print(f"[SUCCESS] Instance {name} running: {instance.id}, IP: {instance.public_ip_address}")
    return instance

def main():
    vpc = create_vpc()
    public_subnet = create_subnet(vpc, PUBLIC_SUBNET_CIDR, "public-subnet", public=True)
    private_subnet = create_subnet(vpc, PRIVATE_SUBNET_CIDR, "private-subnet", public=False)
    igw = create_internet_gateway(vpc)

    # Security groups
    sg_bastion = create_security_group(
        vpc, SECURITY_GROUP_BASTION, "Bastion SSH access", 
        [{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'}]
    )
    sg_nat = create_security_group(
        vpc, SECURITY_GROUP_NAT, "NAT traffic",
        [{'IpProtocol': '-1', 'FromPort': -1, 'ToPort': -1, 'CidrIp': VPC_CIDR}]
    )
    sg_private = create_security_group(
        vpc, SECURITY_GROUP_PRIVATE, "Private instance SSH access",
        [{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'UserIdGroupPairs': [{'GroupId': sg_bastion.id}]}]
    )

    # Launch instances
    bastion = launch_instance(public_subnet, sg_bastion, "bastion", public_ip=True)
    nat = launch_instance(public_subnet, sg_nat, "nat", public_ip=True)
    private = launch_instance(private_subnet, sg_private, "private", public_ip=False)

    # Route tables
    create_route_table(public_subnet, vpc, igw=igw)
    create_route_table(private_subnet, vpc, nat_instance=nat)

if __name__ == "__main__":
    main()
