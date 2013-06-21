#!/bin/bash -v
echo -e "\nInstalling chef..." > /dev/kmsg
rpm -ivh http://xenlet.stu.neva.ru/chef-11.4.0-1.el6.x86_64.rpm &> /dev/kmsg
/opt/aws/bin/cfn-init
# Retrieving chef-client name from metadata 
echo "node_name \"$(curl http://169.254.169.254/latest/meta-data/instance-id)\"" >> /etc/chef/client.rb
# Runing chef-client
echo "Running chef-recipes..." > /dev/kmsg 
/usr/bin/chef-client -j /etc/chef/runlist.json &> /dev/kmsg

