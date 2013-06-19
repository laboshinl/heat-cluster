#!/bin/bash -v
# Installing Chef from RPM
rpm -ivh https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chef-11.4.0-1.el6.x86_64.rpm
# Starting cloudformation
/opt/aws/bin/cfn-init
# Retrieving chef-client name from metadata 
echo "node_name \"$(curl http://169.254.169.254/latest/meta-data/instance-id)\"" >> /etc/chef/client.rb
# Runing chef-client 
/usr/bin/chef-client -j /etc/chef/runlist.json &>/tmp/chef.log

