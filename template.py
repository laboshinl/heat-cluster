import os, json
from netaddr import IPNetwork
from random import randint, choice

##############################
keypair="u-can-get-it-in-swft"
flavor="m1.small"
image="centos-heat-new"
ext_net_uuid="97e728ea-23a0-4d20-a7b7-1406a5815015"
nodes_count=3
##############################

cft = CloudFormationTemplate(description=str(nodes_count)+"-nodes "+ image+" cluster.")

#Randomly generate ip-address
ip=IPNetwork(choice(["10."+str(randint(0,255))+".","172.16.","192.168."])+str(randint(0,255))+".0/24")
ip_list = list(ip)

cft.parameters.add(Parameter('KeyName', 'String',
    {
        'Description': 'Name of an existing KeyPair',
	'Default': keypair
    })
)

cft.parameters.add(Parameter('ImageName', 'String',
    {
        'Description': 'Name of image to work with',
	'Default': image
    })
)

cft.parameters.add(Parameter('Flavor', 'String',
    {
        'Description': 'Instance size',
	'Default': flavor
    })
)

cft.parameters.add(Parameter('ExtNetUuid', 'String',
    {
        'Description': 'UUID of the external network to be used for external access',
	'Default': ext_net_uuid
    })
)

cft.resources.add(Resource("AllowAllSecurityGroup", 'AWS::EC2::SecurityGroup',
    {"GroupDescription" : "Open all ports, enable ping",
				"SecurityGroupIngress" : [
					{
						"IpProtocol" : "tcp", 
						"FromPort" : "1", 
						"ToPort" : "65535", 
						"CidrIp" : "0.0.0.0/0" 
					},
					{
						"IpProtocol" : "udp", 
						"FromPort" : "1", 
						"ToPort" : "65535", 
						"CidrIp" : "0.0.0.0/0" 
					},
					{
						"IpProtocol" : "icmp", 
						"FromPort" : "-1", 
						"ToPort" : "-1", 
						"CidrIp" : "0.0.0.0/0"
					}					
				]
    })
)
cft.resources.add(Resource("Network", 'OS::Quantum::Net',
    {
        "name" : "LocalNetwork"
    })
)
cft.resources.add(Resource("Subnet", 'OS::Quantum::Subnet',
    {
       "network_id" : { "Ref" : "Network" },
	"ip_version" : 4,
	"cidr" : str(ip),
	"value_specs": {
	"dns_nameservers": ["195.208.117.177"]
	}
    })
)

cft.resources.add(Resource("Router", 'OS::Quantum::Router'))

cft.resources.add(Resource("RouterExternalInterface", 'OS::Quantum::RouterGateway',
    {
	"router_id" : { "Ref" : "Router"},
	"network_id" : { "Ref" : "ExtNetUuid" }
    })
)
cft.resources.add(Resource("RouterInternalInterface", 'OS::Quantum::RouterInterface',
    {
	"router_id": { "Ref" : "Router" },
	"subnet_id": { "Ref" : "Subnet" }
    })
)
cft.resources["RouterInternalInterface"]["DependsOn"] = "RouterExternalInterface"

nodenames=""

for y in range(1,nodes_count+1):
	nodenames=nodenames+str(ip_list[y*3])+"  node"+str(y)+"\n"

for x in range(1,nodes_count+1):
	cft.resources.add(Resource("port"+str(x), 'OS::Quantum::Port', 
	{
		"network_id": { "Ref" : "Network" },
		"security_groups" : [{"Fn::GetAtt" : [ "AllowAllSecurityGroup", "ID" ]}],
		"fixed_ips": [{
			"subnet_id": { "Ref" : "Subnet" },
			"ip_address": str(ip_list[x*3])
		}]
	})
	)
	cft.resources["port"+str(x)]["DependsOn"] = "AllowAllSecurityGroup"
	if x==1:
		cft.resources.add(Resource("FloatingIp"+str(x), 'OS::Quantum::FloatingIP', 
		{
			"floating_network_id" : { "Ref" : "ExtNetUuid" }
		})
		)
		cft.resources.add(Resource("FloatingIpAssociate"+str(x), 'OS::Quantum::FloatingIPAssociation', 
		{
			"floatingip_id": { "Ref" : "FloatingIp"+str(x) },
			"port_id": { "Ref" : "port"+str(x) }
		})
		)
		cft.resources["FloatingIpAssociate"+str(x)]["DependsOn"] = "port"+str(x)
		cft.resources["FloatingIpAssociate"+str(x)]["DependsOn"] = "RouterInternalInterface"

	cft.resources.add(Resource("node"+str(x), 'AWS::EC2::Instance',
    	{
        	'ImageId': { 'Ref' : 'ImageName' },
        	'InstanceType': { 'Ref' : 'Flavor' },
		'KeyName' : { 'Ref' : 'KeyName' },
        	'UserData': base64(base64(open('init.sh').read())),
		'NetworkInterfaces': [{ "Ref" : "port"+str(x)}]
    	})
	)
	runlist = "node"+str(x)+'.json' if os.path.exists('node'+str(x)+'.json') else "default.json" 
	cft.resources["node"+str(x)]['Metadata'] = {"AWS::CloudFormation::Init" : {
        			"config" : {
					"commands" : {
					    "hosts" : {
						"command" : "echo $'" + nodenames + "' >> /etc/hosts"
					    },
					    "hostname" : {
						"command" : "hostname node" + str(x)
					    },
 					    "hostname2" : {
						"command" : "sed -ri 's#^HOSTNAME=.*#HOSTNAME=node" + str(x) + "#' /etc/sysconfig/network"
					    }
					},
		        		"files" : {
					      	"/etc/chef/client.rb" : {
							"content" : base64(open('client.rb').read()),
					        	"mode" : "000644",
					        	"owner" : "root",
					        	"group" : "root"
					      	},
					      	"/etc/chef/runlist.json": {
					      		"content" : json.loads(open(runlist).read()),
					        	"mode" : "000644",
					        	"owner" : "root",
					        	"group" : "root"
					      	},
					      	"/etc/chef/validation.pem" : {
				        		"content" : base64(open('validation.pem').read()),
				        		"mode" : "000644",
				        		"owner" : "root",
				        		"group" : "root"
				      		}
	              			}	
        			}
        		}
		}

