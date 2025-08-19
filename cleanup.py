import boto3
from config import *

ec2 = boto3.resource('ec2', region_name=AWS_REGION)

def cleanup():
    print("[INFO] Terminating all lab instances...")
    for instance in ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': ['bastion', 'nat', 'private']}]):
        instance.terminate()
        instance.wait_until_terminated()
        print(f"[SUCCESS] Terminated {instance.id}")

    print("[INFO] Deleting security groups...")
    for sg_name in [SECURITY_GROUP_BASTION, SECURITY_GROUP_NAT, SECURITY_GROUP_PRIVATE]:
        try:
            sg = list(ec2.security_groups.filter(Filters=[{'Name': 'group-name', 'Values':[sg_name]}]))[0]
            sg.delete()
            print(f"[SUCCESS] Deleted {sg_name}")
        except IndexError:
            print(f"[WARNING] Security group {sg_name} not found")

    print("[INFO] Deleting subnets and VPC...")
    for vpc in ec2.vpcs.filter(Filters=[{'Name': 'tag:Name', 'Values':[VPC_NAME]}]):
        for subnet in vpc.subnets.all():
            subnet.delete()
        for igw in vpc.internet_gateways.all():
            vpc.detach_internet_gateway(InternetGatewayId=igw.id)
            igw.delete()
        vpc.delete()
        print(f"[SUCCESS] Deleted VPC {vpc.id}")

if __name__ == "__main__":
    cleanup()
