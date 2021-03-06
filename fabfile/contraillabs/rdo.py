"""Private contrail task for setting up RDO in the openstack node."""

from fabfile.config import *

@task
@roles('openstack')
def fix_yum_repos():
    """ copy local repo locations """
    put('fabfile/contraillabs/repo/rhel70_rdo.repo', '/etc/yum.repos.d/cobbler-config.repo')
    run('yum clean all')

@task
@roles('openstack')
def setup_rdo(rdo_url='https://repos.fedorapeople.org/repos/openstack/openstack-icehouse/rdo-release-icehouse-4.noarch.rpm'):
    """Set up RDO in the openstack node"""
    with settings(warn_only=True):
         run('sudo yum -y install %s' % rdo_url)
    execute(fix_yum_repos)
    with settings(warn_only=True):
        run('sudo yum install -y openstack-packstack')
    run('yes %s | packstack --allinone --mysql-pw juniper123' % env.passwords[env.host_string])
    openstack_password = getattr(env, 'openstack_admin_password', 'contrail123')
    run('source keystonerc_admin && keystone user-password-update --pass %s admin' % openstack_password)
    run("sed -i -e 's/export OS_PASSWORD=.*/export OS_PASSWORD=%s/' keystonerc_admin " % openstack_password)
    with settings(warn_only=True):
        run("service openstack-nova-compute status")
    run("service openstack-nova-compute stop")
    with settings(warn_only=True):
        run("service openstack-nova-compute status")
    with settings(warn_only=True):
        run("service neutron-server status")
    run("service neutron-server stop")
    with settings(warn_only=True):
        run("service neutron-server status")
    with settings(warn_only=True):
        openstackrc_file = run("ls /etc/contrail/openstackrc")
        if openstackrc_file.return_code != 0:
            run('mkdir -p /etc/contrail/')
            run("ln -s /root/keystonerc_admin /etc/contrail/openstackrc")
    cfgm_0_ip = testbed.env['roledefs']['cfgm'][0].split('@')[1]
    run("openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class nova.network.neutronv2.api.API")
    run("openstack-config --set /etc/nova/nova.conf DEFAULT neutron_url http://%s:9696" % cfgm_0_ip)
    run("openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_auth_url http://%s:35357/v2.0" % cfgm_0_ip)
    run("openstack-config --set /etc/nova/nova.conf DEFAULT  compute_driver nova.virt.libvirt.LibvirtDriver")
    run("openstack-config --set /etc/nova/nova.conf DEFAULT  novncproxy_port 5999")
    run("iptables --flush")

    steps = "\n\n\n"
    steps += "="*160
    steps += "\nSteps to bring up contrail with the RDO:\n\
                1. Get the admin_token from /etc/keystone/keystone.conf of the openstack node and populate it as service_token in the testbed.py.\n\
                2. fab install_without_openstack (This step can be executed even before fab setup_rdo)\n\
                3. fab setup_without_openstack\n"
    steps += "="*160
    print steps
