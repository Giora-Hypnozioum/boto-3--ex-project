#!/usr/bin/env python3
import boto3
import configparser
import logging
import sys

# Setup logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Load AWS credentials from aws.cfg
config = configparser.ConfigParser()
config.read("aws.cfg")

try:
    aws_access_key_id = config["default"]["aws_access_key_id"]
    aws_secret_access_key = config["default"]["aws_secret_access_key"]
    region_name = config["default"]["region"]
except KeyError as e:
    logging.error(f"Missing key in aws.cfg: {e}")
    sys.exit(1)

# Create boto3 clients
ec2 = boto3.client(
    "ec2",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

def test_vpc_connection():
    logging.info("Testing VPC connection...")
    try:
        vpcs = ec2.describe_vpcs()
        if not vpcs["Vpcs"]:
            logging.warning("No VPCs found in this account.")
        else:
            logging.info(f"Found {len(vpcs['Vpcs'])} VPC(s).")
            for vpc in vpcs["Vpcs"]:
                logging.info(f"VPC ID: {vpc['VpcId']}, CIDR: {vpc['CidrBlock']}")
    except Exception as e:
        logging.error(f"Error fetching VPCs: {e}")

def test_subnet_connection():
    logging.info("Testing Subnet connection...")
    try:
        subnets = ec2.describe_subnets()
        if not subnets["Subnets"]:
            logging.warning("No subnets found in this account.")
        else:
            logging.info(f"Found {len(subnets['Subnets'])} subnet(s).")
            for subnet in subnets["Subnets"]:
                logging.info(
                    f"Subnet ID: {subnet['SubnetId']}, CIDR: {subnet['CidrBlock']}, AZ: {subnet['AvailabilityZone']}"
                )
    except Exception as e:
        logging.error(f"Error fetching subnets: {e}")

def test_instance_connection():
    logging.info("Testing EC2 instance connection...")
    try:
        instances = ec2.describe_instances()
        all_instances = sum(
            [reservation["Instances"] for reservation in instances["Reservations"]], []
        )
        if not all_instances:
            logging.warning("No EC2 instances found in this account.")
        else:
            logging.info(f"Found {len(all_instances)} EC2 instance(s).")
            for instance in all_instances:
                state = instance["State"]["Name"]
                instance_id = instance["InstanceId"]
                public_ip = instance.get("PublicIpAddress", "N/A")
                private_ip = instance.get("PrivateIpAddress", "N/A")
                logging.info(
                    f"Instance ID: {instance_id}, State: {state}, Public IP: {public_ip}, Private IP: {private_ip}"
                )
    except Exception as e:
        logging.error(f"Error fetching EC2 instances: {e}")

if __name__ == "__main__":
    logging.info("Starting AWS connection tests...")
    test_vpc_connection()
    test_subnet_connection()
    test_instance_connection()
    logging.info("AWS connection tests completed.")
