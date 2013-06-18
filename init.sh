#!/bin/bash -v
NAME=$(curl http://169.254.169.254/latest/meta-data/instance-id)
source /root/bash_profile
export HOME=/root
mkdir /root/.chef/
/opt/aws/bin/cfn-init
wget https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chef-11.4.0-1.el6.x86_64.rpm
rpm -ivh chef-11.4.0-1.el6.x86_64.rpm
ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
until [ -e /usr/bin/knife ] ; do sleep 1; done
/usr/bin/knife bootstrap -c /root/.chef/knife.rb -i /root/.ssh/id_rsa localhost -N $NAME &>/tmp/knife.log
/usr/bin/chef-client -c /etc/chef/client.rb -j /root/.chef/runlist.json &>/tmp/chef.log

