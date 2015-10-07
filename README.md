# pyvshell

First attempt to manage ESXi/vCenter through cmd python module and pyVmomi

## stop command:

  (Cmd) stop someesxi.domain.tld
  Please enter your username: root
  Password:
  You're connected to someesxi.domain.tld
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
  Host regex?: DC0_C1.*
  Powered off/total (vcenter) VirtualMachines:  |################                | 24/48


## ls command:

  (Cmd) ls someesxi.domain.tld
  Please enter your username: root
  Password:
  Instance UUID:           503b64ab-3fc2-e59a-36d4-3505079a08ff
  CPUs:                    1
  MemoryMB:                64
  Guest PowerState:        poweredOff
  Guest Full Name:         Microsoft Windows Server 2003 Standard (32-bit)
  Guest Container Type:    winNetStandardGuest
  Container Version:       vmx-07
  ----------------------------------------------------------------------
  Name:                    DC0_C1_RP2_VM2
  Instance UUID:           503b486c-f789-2b43-dbbf-ac2b62364329
  CPUs:                    1
  MemoryMB:                64
  Guest PowerState:        poweredOff
  Guest Full Name:         Microsoft Windows Server 2003 Standard (32-bit)
  Guest Container Type:    winNetStandardGuest
  Container Version:       vmx-07
  ----------------------------------------------------------------------
  Name:                    DC0_C1_RP0_VM0
  Instance UUID:           503b382f-0ec4-b961-9461-883e0c759b31
  CPUs:                    1
  MemoryMB:                64
  Guest PowerState:        poweredOff
  Guest Full Name:         Microsoft Windows Server 2003 Standard (32-bit)
  Guest Container Type:    winNetStandardGuest
  Container Version:       vmx-07
  **********************************************************************
  You have a total of 48 VM in someesxi.domain.tld
