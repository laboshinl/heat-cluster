heat-cluster
----------------
Python script generates cloudformation template to bootstrap cluster using chef-server

![cluster](cluster.png)
 
1. Install pyplates:
`pip install cfn-pyplates netaddr`
2. Clone repo: 
`git clone https://github.com/laboshinl/heat-cluster.git`
3. Add your runlists to node(1..nodes_count).json if not
`cfn_py_generate template.py template.json`

`heat stack-create my_cluster -f template.json`
