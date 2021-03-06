import platform

from fabfile.config import *

def copy_pkg(tgt_host, pkg_file):
    with settings(host_string = tgt_host):
        put(pkg_file)
#end _copy_pkg

def install_pkg(tgt_host, pkg_file):
    with settings(host_string = tgt_host):
        run("rpm -iv --force %s" %(pkg_file.split('/')[-1]))
#end _install_pkg

def detect_ostype():
    output = run('uname -a')
    dist = 'centos'
    if 'el6' in output:
        release = run('cat /etc/redhat-release')
        if 'Red Hat' in release:
            dist = 'redhat'
        else:
            dist = 'centos'
    elif 'el7' in output:
        dist = 'redhat'
    elif 'fc17' in output:
        dist = 'fedora'
    elif 'xen' in output:
        dist = 'xen'
    elif 'Ubuntu' in output:
        dist = 'Ubuntu'
    return dist
#end detect_ostype

def get_release(pkg='contrail-install-packages'):
    pkg_ver = None
    dist = detect_ostype() 
    if dist in ['centos', 'fedora', 'redhat']:
        cmd = "rpm -q --queryformat '%%{VERSION}' %s" %pkg
    elif dist in ['Ubuntu']:
        cmd = "dpkg -p %s | grep Version: | cut -d' ' -f2 | cut -d'-' -f1" %pkg
    pkg_ver = run(cmd)
    if 'is not installed' in pkg_ver or 'is not available' in pkg_ver:
        print "Package %s not installed." % pkg
        return None
    return pkg_ver

def get_build(pkg='contrail-install-packages'):
    pkg_rel = None
    dist = detect_ostype()
    if dist in ['centos', 'fedora', 'redhat']:
        cmd = "rpm -q --queryformat '%%{RELEASE}' %s" %pkg
    elif dist in ['Ubuntu']:
        cmd = "dpkg -p %s | grep Version: | cut -d' ' -f2 | cut -d'-' -f2" %pkg
    pkg_rel = run(cmd)
    if 'is not installed' in pkg_rel or 'is not available' in pkg_rel:
        print "Package %s not installed." % pkg
        return None
    return pkg_rel

def is_package_installed(pkg_name):
    ostype = detect_ostype()
    if ostype in ['Ubuntu']:
        cmd = 'dpkg-query -l "%s" | grep -q ^.i'
    elif ostype in ['centos','fedora']:
        cmd = 'rpm -qi %s '
    cmd = cmd % (pkg_name)
    with settings(warn_only=True):
        result = run(cmd)
    return result.succeeded 
#end is_package_installed
