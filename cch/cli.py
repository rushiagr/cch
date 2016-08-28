# -*- coding: utf-8 -*-

import boto3
import botocore
from builtins import input
import click
import prettytable
import sys

def get_connection():
    """Ensures that the AWS is configured properly.

    If not, tell how to configure it.

    Returns connection object if configured properly, else None.
    """
    try:
        ec2 = boto3.resource('ec2')
    except (botocore.exceptions.NoRegionError,
            botocore.exceptions.NoCredentialsError) as e:
        # TODO(rushiagr): instead of telling people to run credentials, ask
        # credentials here itself
        print('Credentials and region not configured? Run "aws configure" to configure it.')
        # TODO(rushiagr): let people provide singapore, and guess region name from
        # that.
        print('Provide region as "ap-southeast-1" for Singapore.')
        return None
    return ec2

@click.command()
@click.option('-s', 'show_vol_info', flag_value=True,
        help='Show VM disk sizes (GBs), starting with root disk')
@click.option('-n', 'filter_name',
        help='Show only VMs which matches given string (case-insensitive)')
def lsvm(show_vol_info, filter_name):
    '''List all EC2 VMs. '''
    ec2 = get_connection()
    if not ec2:
        return

    filter_name = filter_name.lower() if filter_name else None

    if show_vol_info:
        table = prettytable.PrettyTable(
                ['ID', 'Name', 'Status', 'Flavor', 'IP', 'Vols(GB)'])
    else:
        table = prettytable.PrettyTable(
                ['ID', 'Name', 'Status', 'Flavor', 'IP', 'Vols'])

    table.left_padding_width=0
    table.right_padding_width=1
    table.border=False

    instances = ec2.instances.all()

    instances_to_print = []

    if not filter_name:
        instances_to_print = instances
    else:
        for i in instances:
            if i.tags is not None and len(i.tags) > 0:
                for tag in i.tags:
                    if(tag['Key'] == 'Name' and
                            tag['Value'].lower().find(filter_name) > -1):
                        instances_to_print.append(i)
                        break

    for i in instances_to_print:
        row = [
                i.id,
                i.tags[0]['Value'] if i.tags is not None else '',
                i.state['Name'],
                i.instance_type,
                i.public_ip_address]
        if show_vol_info:
            row.append([vol.size for vol in i.volumes.all()])
        else:
            row.append(len(i.block_device_mappings))
        table.add_row(row)

    print(table.get_string(sortby='Status'))

@click.command()
def mkvm():
    ec2 = get_connection()
    if not ec2:
        return

    flavor_names = ['t1.micro', 'm1.small', 'm1.medium', 'm1.large',
            'm1.xlarge', 'm3.medium', 'm3.large', 'm3.xlarge', 'm3.2xlarge',
            'm4.large', 'm4.xlarge', 'm4.2xlarge', 'm4.4xlarge', 'm4.10xlarge',
            't2.micro', 't2.small', 't2.medium', 't2.large', 'm2.xlarge',
            'm2.2xlarge', 'm2.4xlarge', 'cr1.8xlarge', 'i2.xlarge',
            'i2.2xlarge', 'i2.4xlarge', 'i2.8xlarge', 'hi1.4xlarge',
            'hs1.8xlarge', 'c1.medium', 'c1.xlarge', 'c3.large', 'c3.xlarge',
            'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge', 'c4.large', 'c4.xlarge',
            'c4.2xlarge', 'c4.4xlarge', 'c4.8xlarge', 'cc1.4xlarge',
            'cc2.8xlarge', 'g2.2xlarge', 'cg1.4xlarge', 'r3.large',
            'r3.xlarge', 'r3.2xlarge', 'r3.4xlarge', 'r3.8xlarge', 'd2.xlarge',
            'd2.2xlarge', 'd2.4xlarge', 'd2.8xlarge']

    print('Only Ubuntu image and Singapore region supported as of now')
    print('Available flavors:', flavor_names)

    selected_flavor=''
    while True:
        sys.stdout.write("Select flavor ['l' to list]: ")
        flavor=input()
        if flavor.lower() == 'l':
            print(flavor_names)
            continue
        elif flavor in flavor_names:
            selected_flavor=flavor
            break
        else:
            print('Invalid flavor name.')

    keypairs = ec2.key_pairs.all()
    keypair_names = [kp.name for kp in keypairs]
    print( 'Available key pairs:', keypair_names)
    sys.stdout.write("Select keypair: ")
    selected_keypair=input()

    secgroups = ec2.security_groups.all()
    secgroups = [sg for sg in secgroups]
    secgroup_name_id_dict = {}
    for sg in secgroups:
        if sg.tags is not None:
            secgroup_name_id_dict[sg.tags[0]['Value']] = sg.id
    secgroup_names = [sg.tags[0]['Value']
            for sg in secgroups if sg.tags is not None]
    print('Available security groups:', secgroup_names)
    sys.stdout.write("Select security group [empty for no security group]: ")
    selected_security_group_name=input()

    sys.stdout.write("Enter root volume size in GBs: ")
    selected_vol_size=input()

    if not selected_security_group_name:
        ec2.create_instances(DryRun=False, ImageId='ami-96f1c1c4', MinCount=1,
                MaxCount=1, KeyName=selected_keypair, InstanceType=flavor,
                BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                    'Ebs': {"VolumeSize": int(selected_vol_size)}}])
    else:
        ec2.create_instances(DryRun=False, ImageId='ami-96f1c1c4', MinCount=1,
                MaxCount=1, KeyName=selected_keypair, InstanceType=flavor,
                BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                    'Ebs': {"VolumeSize": int(selected_vol_size)}}],
                SecurityGroupIds=[
                    secgroup_name_id_dict[selected_security_group_name]])
