# Configuration file for AWS VPC automation

AWS_REGION = "il-central-1"        # Israel region
VPC_CIDR = "10.0.0.0/16"
PUBLIC_SUBNET_CIDR = "10.0.1.0/24"
PRIVATE_SUBNET_CIDR = "10.0.2.0/24"
INSTANCE_TYPE = "t2.micro"         
KEY_NAME = "key01"
SECURITY_GROUP_BASTION = "sg-bastion"
SECURITY_GROUP_NAT = "sg-nat"
SECURITY_GROUP_PRIVATE = "sg-private"
VPC_NAME = "lab-vpc"
AMI_ID = "ami-0c02fb55956c7d316"  
