# -*- coding: utf-8 -*-

import boto3
import botocore
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
