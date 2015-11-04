#!/usr/bin/env python3
# Please install pyVmomi and progressbar
#
# pip install pyvmomi
# pip install progress
#

try:
    from pyVim import connect
    from pyVmomi import vmodl
    from pyVmomi import vim
    from progress.bar import Bar

    from tools import pchelper

    import re
    import os
    import getpass
    import cmd
    import atexit
    import ssl
    import warnings
    from tools import tasks
    # Time for monkey patch!
    ssl._create_default_https_context = ssl._create_unverified_context
    warnings.filterwarnings("ignore")

except ImportError:
    print("Please check your python modules")


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
        args = host.split()

        if len(args) == 2:
            try:
                vm_list = self.connect(args[0])
                for vm in vm_list:
                    if vm["runtime.powerState"] == 'poweredOn':
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

            except vmodl.MethodFault as e:
                print("Caught error")
                return 0

        if len(args) == 1:
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

        if len(args) == 0:
            print("Please provide a hostname or IP address")

    def do_stop(self, host):
        """ 
        Shutdown a cluster based on a regex.
        First it will show which hosts are available and then will ask Host regex?.
        If no regex is entered IT WILL ASUMME EVERYTHING!!!

        (Cmd) stop host 
        Please enter your username: root
        Password: 
        You're connected to host
        ----------------------------------------------------------------------
        Hosts available here: 

        DC0_C0_H0
        DC0_C0_H1
        DC0_C0_H2
        DC0_C0_H3
        DC0_C0_H4
        DC0_C0_H5
        DC0_C0_H6
        DC0_C0_H7
        DC0_C1_H0
        DC0_C1_H1
        DC0_C1_H2
        DC0_C1_H3
        DC0_C1_H4
        DC0_C1_H5
        DC0_C1_H6
        DC0_C1_H7
        ----------------------------------------------------------------------
        Host regex?: DC0.*
        Powered off/total (vcenter) VirtualMachines:  |################################| 46/46

        """

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
            print("Hosts available here: ")
            print("")
            """
            TODO:

            > SAVE DC STATE!!!
            > Be nicer.
            > Parameters
            """
            
            """
            Save current state datacenter

            """

            with open('save-state.txt', 'w') as f:
                for vm in objview.view:
                    f.write("Name           :  {}\n".format(vm.name))
                    f.write("State          :  {}\n".format(vm.runtime.powerState))
                    f.write("Instance UUID  :  {}\n".format(vm.config.instanceUuid))
                    f.write('\n')

            """
            Save only poweredOn machines in order to powerOn afterwards

            """

            with open('uuidpoweredon.txt', 'w') as f:
                for vm in objview.view:
                    if vm.runtime.powerState == 'poweredOn':
                        f.write("{}".format(vm.config.instanceUuid).strip())
                        f.write('\n')

            """
            Print vmware hosts available to stop
            
            """


            for host in hosts.view:
                print(host.name)
            print("-" * 70)

            """
            Asks for vmware hosts regex

            """

            regex = input("Host regex?: ")
            barvm = Bar('Powered off/total (vcenter) VirtualMachines: ',
                      max=len(objview.view))
            for vm in objview.view:
                """ MIND THIS!! :D
                """
                if re.match(regex, vm.runtime.host.name):
                    vm.PowerOff()
                    barvm.next()
            barvm.finish()


            for host in hosts.view:
                if re.match(regex, host.name):
                    print("Shutting down host {0}".format(host.name))
                    vim.HostSystem.Shutdown(host, True)
                    

        else:
            print("Please provide a vmware host to connect")
            
    def do_start(self, host):
        """
        Start all VM's on vCenter or ESXi given a uuid file.
        It will ask you an username and valid password.
        Usage example and output:
                                                                               
        (Cmd) start esxi.domain.tld uuidon.txt
        Please enter your username: root


        You can check if it is powered on or not.

        (Cmd) ls esxi.domain.tld on
        Please enter your username: root
        Password: 
        ----------------------------------------------------------------------
        Name:                    DC0_C1_RP0_VM0
        Instance UUID:           503b382f-0ec4-b961-9461-883e0c759b31
        CPUs:                    1
        MemoryMB:                64
        Guest PowerState:        poweredOn
        Guest Full Name:         Microsoft Windows Server 2003 Standard (32-bit)
        Guest Container Type:    winNetStandardGuest
        Container Version:       vmx-07
                                                                               
        """
                                                                               
        self.host = host
        args = host.split()
                                                                               
        if len(args) == 2:
            try:

                user = input("Please enter your username: ")
                password = getpass.getpass("Password: ")

                SI = connect.SmartConnect(host=args[0],
                        user=user,
                        pwd=password)

                with open(args[1]) as uuid:
                    for line in uuid:
                        line = line.strip()
                        if uuid:
                            try:
                                VM = SI.content.searchIndex.FindByUuid(None, line, True, True)
                                TASK = VM.PowerOn()
                                tasks.wait_for_tasks(SI, [TASK])

                            except vim.fault.InvalidPowerState:
                                print("{0} Its already powered On!!".format(line))


            except vmodl.MethodFault as e:
                print("Caught vmodl fault : ", e)
                return 0


                                                                               
        if len(args) == 1:
            try:
                print("Please enter a file containing uuid to power on!!")

                                                                               
            except vmodl.MethodFault as e:
                print("Caught vmodl fault : ", e)
                return 0
                                                                               
        if len(args) == 0:
            print("Please provide a hostname or IP address")


    def do_shell(self, line):
        """
        Yes you can! shell is available thorough !

        (Cmd) !uname -a
        running shell command: uname -a
        Linux lsanmartin 3.13.0-49-generic #83-Ubuntu SMP Fri Apr 10 20:11:33 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

        """
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
