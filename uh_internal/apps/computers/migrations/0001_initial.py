# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-28 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uh_internal.apps.computers.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '__first__'),
        ('network', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('networkdevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='network.NetworkDevice')),
                ('model', models.CharField(max_length=25, verbose_name='Model')),
                ('serial_number', models.CharField(blank=True, default=None, max_length=20, null=True, unique=True, verbose_name='Serial Number')),
                ('property_id', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name='Cal Poly Property ID')),
                ('location', models.CharField(blank=True, max_length=100, null=True, verbose_name='Location')),
                ('date_purchased', models.DateField(verbose_name='Date Purchased')),
                ('dn', models.CharField(max_length=250, verbose_name='Distinguished Name')),
                ('description', models.CharField(max_length=100, verbose_name='Description')),
                ('dhcp', models.BooleanField(default=False)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Department', verbose_name='Department')),
                ('sub_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.SubDepartment', verbose_name='Sub Department')),
            ],
            bases=('network.networkdevice',),
        ),
        migrations.CreateModel(
            name='DomainName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')),
                ('domain_name', models.CharField(max_length=100, verbose_name='Domain Name')),
                ('sr_number', models.IntegerField(db_column='ticket_id', null=True, verbose_name='SR Number')),
            ],
            options={
                'verbose_name': 'Domain Name',
            },
        ),
        migrations.CreateModel(
            name='Pinhole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')),
                ('service_name', models.CharField(max_length=50, verbose_name='Service Name')),
                ('inner_fw', models.BooleanField(default=None, verbose_name='Inner Firewall')),
                ('border_fw', models.BooleanField(default=None, verbose_name='Border Firewall')),
                ('tcp_ports', uh_internal.apps.computers.fields.ListField(verbose_name='TCP Ports')),
                ('udp_ports', uh_internal.apps.computers.fields.ListField(verbose_name='UDP Ports')),
                ('sr_number', models.IntegerField(db_column='ticket_id', null=True, verbose_name='SR Number')),
            ],
        ),
    ]
