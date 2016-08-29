# -*- coding: utf-8 -*-

from __future__ import print_function
import boto3
import botocore
from builtins import input
import click
import prettytable
import sys

images = {
    'ap-southeast-1': {'ubuntu14': 'ami-21d30f42'},     # Singapore
    'ap-south-1': {'ubuntu14': 'ami-4a90fa25'},         # Mumbai
    'us-east-1': {'ubuntu14': 'ami-2d39803a'},          # nvirginia
    'us-west-1': {'ubuntu14': 'ami-48db9d28'},          # northcalif
    'us-west-2': {'ubuntu14': 'ami-d732f0b7'},          # oregon
    'eu-west-1': {'ubuntu14': 'ami-ed82e39e'},          # ireland
    'eu-central-1': {'ubuntu14': 'ami-26c43149'},       # frankfurt
    'ap-northeast-1': {'ubuntu14': 'ami-a21529cc'},     # tokyo
    'ap-northeast-2': {'ubuntu14': 'ami-09dc1267'},     # seoul
    'ap-southeast-2': {'ubuntu14': 'ami-ba3e14d9'},     # sydney
    'sa-east-1': {'ubuntu14': 'ami-dc48dcb0'},          # saopaolo
}

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

def get_region_specific_ami_id(distro):
    region = boto3.session.Session().region_name
    return images.get(region).get(distro)

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

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
    print('Available flavors:', ' '.join(flavor_names))

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
    print('Available key pairs:', ' '.join(keypair_names))
    sys.stdout.write("Select keypair: ")
    selected_keypair=input()

    secgroups = list(ec2.security_groups.all())
    secgroup_name_id_dict = {}
    for sg in secgroups:
        secgroup_name_id_dict[sg.group_name] = sg.id
    secgroup_names = [sg.group_name for sg in secgroups]

    print('Available security groups:\n    ', '\t'.join(secgroup_names))
    sys.stdout.write("Select security group [empty for no security group]: ")
    selected_security_group_name=input()

    sys.stdout.write("Enter root volume size in GBs: ")
    selected_vol_size=input()

    ami_id = get_region_specific_ami_id('ubuntu14')

    if ami_id is None:
        print('We do not have Ubuntu image for this region')
        return

    if not selected_security_group_name:
        ec2.create_instances(DryRun=False, ImageId=ami_id, MinCount=1,
                MaxCount=1, KeyName=selected_keypair, InstanceType=flavor,
                BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                    'Ebs': {"VolumeSize": int(selected_vol_size)}}])
    else:
        ec2.create_instances(DryRun=False, ImageId=ami_id, MinCount=1,
                MaxCount=1, KeyName=selected_keypair, InstanceType=flavor,
                BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                    'Ebs': {"VolumeSize": int(selected_vol_size)}}],
                SecurityGroupIds=[
                    secgroup_name_id_dict[selected_security_group_name]])

@click.command()
def lskp():
    ec2 = get_connection()
    if not ec2:
        return

    keypairs = ec2.key_pairs.all()
    keypair_names = [kp.name for kp in keypairs]
    print('Available keypairs:\n   ', '\n    '.join(keypair_names))


@click.command()
@click.option('-a', 'is_detail', flag_value=True,
        help='Show security group rules.')
def lssg(is_detail):
    ec2 = get_connection()
    if not ec2:
        return

    secgroups = list(ec2.security_groups.all())
    if not is_detail:
        secgroup_names = [sg.group_name for sg in secgroups]
        print('Available security groups:\n   ', '\n    '.join(secgroup_names))
        print('\nExecute "lssg -a" for viewing security group rules')
    else:
        for sg in secgroups:
            print('\nSecurity group:', sg.group_name)

            ip_permissions = sg.ip_permissions
            print('   Protocol\t  IP\t\tfrom\tto')
            for perm in ip_permissions:
                if perm['IpRanges']:
                    print('     tcp\t' + perm['IpRanges'][0]['CidrIp'] + '\t' +
                        str(perm['FromPort']) + '\t' + str(perm['ToPort']))

@click.command()
@click.argument('vm_ids', nargs=-1, required=True)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to stop and terminate the VM/VMs?'
                ' You can stop the VM by using "stpvm" command.')
def rmvm(vm_ids):

    if len(vm_ids) == 0:
        print('No VM IDs provided. Aborting')
        return

    print('Stopping and terminating VMs with IDs: ', vm_ids)

    # TODO(rushiagr): use re.match('i-[0-9a-f]+', 'i-abcd1334') to confirm
    # it's an ID

    ec2 = get_connection()
    if not ec2:
        return

    ec2.instances.filter(InstanceIds=vm_ids).stop()
    ec2.instances.filter(InstanceIds=vm_ids).terminate()

@click.command()
@click.argument('vm_ids', nargs=-1)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to stop the VM?')
def stpvm(vm_ids):
    print('Stopping (but not terminating) VMs with IDs: ', vm_ids)

    # TODO(rushiagr): use re.match('i-[0-9a-f]+', 'i-abcd1334') to confirm
    # it's an ID

    ec2 = get_connection()
    if not ec2:
        return

    ec2.instances.filter(InstanceIds=vm_ids).stop()

@click.command()
def mkkp():
    ec2 = get_connection()
    if not ec2:
        return
    sys.stdout.write("Keypair name (required): ")
    keypair_name=input()
    kp = ec2.create_key_pair(KeyName=keypair_name)
    print('Keypair', keypair_name, 'created. Private key:')
    print(kp.key_material)

@click.command()
@click.argument('keypair_name', required=False)
def rmkp(keypair_name):
    ec2 = get_connection()
    if not ec2:
        return

    if keypair_name is None:
        sys.stdout.write("Keypair name (required): ")
        keypair_name=input()

    kp = ec2.KeyPair(keypair_name)
    kp.delete()
    print('Keypair', keypair_name, 'deleted.')

@click.command()
def mksg():
    ec2 = get_connection()
    if not ec2:
        return

    sys.stdout.write("Note that only TCP rules are supported as of now.\n")

    sys.stdout.write("Security group name (required): ")
    sg_name=input()
    sys.stdout.write("Security group description (required): ")
    sg_description=input()

    ip_portrange_tuples = []

    while True:
        sys.stdout.write("Add security group rule? [y/n]: ")
        bool_inp = input()
        if bool_inp.lower().startswith('y'):
            sys.stdout.write("IP (e.g. 0.0.0.0/0): ")
            ip = input()
            sys.stdout.write("Port or port range (e.g. '8080' or '8000-8999': ")
            port_range = input()
            if port_range.find('-') > -1:
                start_port, end_port = port_range.split('-')
            else:
                start_port = end_port = port_range
            start_port, end_port = int(start_port), int(end_port)
            if start_port > end_port:
                start_port, end_port = end_port, start_port
            ip_portrange_tuples.append((ip, start_port, end_port))
        else:
            break

    mysg = ec2.create_security_group(GroupName=sg_name,
            Description=sg_description)
    for ip, start_port, end_port in ip_portrange_tuples:
        mysg.authorize_ingress(IpProtocol="tcp", CidrIp=ip,
                FromPort=start_port, ToPort=end_port)

    print('Security group', sg_name, 'created')

@click.command()
@click.argument('secgroup_name', required=False)
def rmsg(secgroup_name):
    ec2 = get_connection()
    if not ec2:
        return

    if secgroup_name is None:
        sys.stdout.write("Security group name (required): ")
        secgroup_name=input()

    sg = [sg for sg in ec2.security_groups.filter(GroupNames=[secgroup_name])][0]
    sg.delete()
    print('Security group', secgroup_name, 'deleted.')
