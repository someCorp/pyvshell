#!/usr/bin/env python3
# Please install pyVmomi and progressbar
#
# pip install pyvmomi
# pip install progressbar
#
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from progress.bar import Bar

from tools import tasks
from tools import pchelper


import re
import os
import getpass
import cmd
import atexit
import ssl

# Time for monkey patch!
ssl._create_default_https_context = ssl._create_unverified_context


class someshell(cmd.Cmd):

    def connect(self, host):
        """ Basic connector to ESXi. It uses pchelper in order to get vm
        properties.
        """

        self.vcenter = host
        user = input("Please enter your username: ")
        password = getpass.getpass("Password: ")
        SI = connect.SmartConnect(host=host, user=user,
                                  pwd=password,
                                  port=443)
        atexit.register(connect.Disconnect, SI)
        view = pchelper.get_container_view(SI, obj_type=[vim.VirtualMachine])
        vm_properties = ["name", "config.instanceUuid",
                         "config.hardware.numCPU",
                         "config.hardware.memoryMB", "runtime.powerState",
                         "config.guestFullName", "config.guestId",
                         "config.version"]
        vm_data = pchelper.collect_properties(SI, view_ref=view,
                                              obj_type=vim.VirtualMachine,
                                              path_set=vm_properties,
                                              include_mors=True)
        return vm_data

    def do_ls(self, host):
        """
        Get all VM's on vCenter or ESXi.
        It will ask you an username and valid password.
        Usage example and output:

        (Cmd) ls esxi.domain.tld
        Please enter your username: root
        Password:
        ----------------------------------------------------------------------
        Name:                    syslog02.domain.tld
        Instance UUID:           523589d3-60fd-b49a-0dc1-c66b0b42b394
        CPUs:                    2
        MemoryMB:                4096
        Guest PowerState:        running
        Guest Full Name:         Ubuntu Linux (64-bit)
        Guest Container Type:    ubuntu64Guest
        Container Version:       vmx-07
        **********************************************************************
        You have a total of 1 VM in esxi.domain.tld

        """

        self.host = host

        if host:
            try:
                vm_list = self.connect(host)
                for vm in vm_list:
                    print("-" * 70)
                    print(
                        "Name:                    {0}".format(vm["name"]))
                    print("Instance UUID:           {0}".format(
                        vm["config.instanceUuid"]))
                    print("CPUs:                    {0}".format(
                        vm["config.hardware.numCPU"]))
                    print("MemoryMB:                {0}".format(
                        vm["config.hardware.memoryMB"]))
                    print("Guest PowerState:        {0}".format(
                        vm["runtime.powerState"]))
                    print("Guest Full Name:         {0}".format(
                        vm["config.guestFullName"]))
                    print("Guest Container Type:    {0}".format(
                        vm["config.guestId"]))
                    print("Container Version:       {0}".format(
                        vm["config.version"]))

                print("*" * 70)
                print("You have a total of {0} VM in {1}".format(len(vm_list),
                                                                 host))

            except vmodl.MethodFault as e:
                print("Caught vmodl fault : ", e)
                return 0

        else:
            print("Please provide a hostname or IP address")

    def do_stop(self, host):
        """ Shutdown a cluster
        """
        line = host.split()
        user = input("Please enter your username: ")
        password = getpass.getpass("Password: ")
        SI = connect.SmartConnect(host=host, user=user,
                                  pwd=password,
                                  port=443)

        content = SI.RetrieveContent()
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine],
                                                          True)

        hosts = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)

        if host:
            print("You're connected to {0}".format(host))
            print("-" * 70)

            """
            SAVE DC STATE!!!

            Debug only.
            for host in hosts.view:
                print(host.name)
            print("-" * 70)
            """

            cluster = input("r710 or BL?: ")
            bar = Bar('Powered off/total (vcenter): ', max=len(objview.view))
            for vm in objview.view:
                """ MIND THIS!! :D
                """
                if cluster == 'r710':
                    if re.match(r'^DC0_C1.*', vm.runtime.host.name):
                        vm.PowerOff()
                        bar.next()
                if cluster == 'BL':
                    if re.match(r'^DC0_C0.*', vm.runtime.host.name):
                        vm.PowerOff()
                        bar.next()
            bar.finish()

        else:
            print("Please provide a vmware host to connect")

    def do_start(self, host):
        """ Start a cluster
        """
        line = host.split()
        user = input("Please enter your username: ")
        password = getpass.getpass("Password: ")
        SI = connect.SmartConnect(host=host, user=user,
                                  pwd=password,
                                  port=443)
        if host:
            with open('uuid-to-power-on.txt') as uuid:
                for line in uuid:
                    line = line.strip()
                    if uuid:
                        try:
                            VM = SI.content.searchIndex.FindByUuid(
                                None, line, True, True)
                            TASK = VM.PowerOn()
                            tasks.wait_for_tasks(SI, [TASK])

                        except vim.fault.InvalidPowerState:
                            pass

    def do_shell(self, line):
        "Run a shell command"
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def do_EOF(self, line):
        return True

    def postloop(self):
        print

    def emptyline(self):
        print("Do not type empty lines! type 'help' to get commands")

if __name__ == '__main__':
    someshell().cmdloop()
