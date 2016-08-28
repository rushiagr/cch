# -*- coding: utf-8 -*-

import boto3
import botocore
import click
import prettytable
import sys


@click.command()
@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
@click.argument('name', default='world', required=False)
def main(name, as_cowboy):
    """Cloud CLI for Humans"""
    greet = 'Howdy' if as_cowboy else 'Hello'
    click.echo('{0}, {1}.'.format(greet, name))

@click.command()
@click.option('-s', 'show_vol_info', flag_value=True,
        help='Show VM disk sizes (GBs), starting with root disk')
@click.option('-n', 'filter_name',
        help='Show only VMs which matches given string (case-insensitive)')
def lsvm(show_vol_info, filter_name):
    '''List all EC2 VMs. '''
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
        sys.exit()

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
