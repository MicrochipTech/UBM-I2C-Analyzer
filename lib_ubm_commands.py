#*******************************************************************************
#  Copyright (C) 2024 Microchip Technology Inc. and its subsidiaries.

#  Subject to your compliance with these terms, you may use Microchip software
#  and any derivatives exclusively with Microchip products. It is your
#  responsibility to comply with third party license terms applicable to your
#  use of third party software (including open source software) that may
#  accompany Microchip software.

#  THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
#  EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
#  WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
#  PARTICULAR PURPOSE.

#  IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
#  INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
#  WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
#  BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
#  FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
#  ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
#  THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
#*******************************************************************************/

GET_OPERATION_STATE = 0x00
GET_LAST_COMMAND_STATUS = 0x01
GET_SILICON_IDENTITY = 0x02
GET_UPDATE_CAPABILITIES = 0x03
ENTER_PROGRAMMING_MODE = 0x20
PROGRAM_MODE_DATA_TRANSFER = 0x21
EXIT_PROGRAMING_MODE = 0x22
GET_HFC_INFO = 0x30
GET_BACKPLANE_INFO = 0x31
GET_STARTING_SLOT = 0x32
GET_CAPABILITIES = 0x33
GET_FEATURES = 0x34
GET_CHANGE_COUNT = 0x35
GET_DFC_INDEX = 0x36
GET_DFC_STATUS_CONTROL = 0x40

OPERATIONAL_STATE_INVALID = 0
OPERATIONAL_STATE_INITIALIZING = 1
OPERATIONAL_STATE_BUSY = 2
OPERATIONAL_STATE_READY = 3
OPERATIONAL_STATE_REDUCED_FUNCTIONALITY = 4


SILICON_ID_SPEC_VERSION = 0
SILICON_ID_PCI_VENDOR_LSB = 1
SILICON_ID_PCI_VENDOR_MSB = 2
SILICON_ID_UBM_CONTROLLER_DEVICE_CODE_BYTE0 = 4
SILICON_ID_UBM_CONTROLLER_DEVICE_CODE_BYTE1 = 5
SILICON_ID_UBM_CONTROLLER_DEVICE_CODE_BYTE2 = 6
SILICON_ID_UBM_CONTROLLER_DEVICE_CODE_BYTE3 = 7
SILICON_ID_UBM_CONTROLLER_IMAGE_VER_MINOR = 10
SILICON_ID_UBM_CONTROLLER_IMAGE_VER_MAJOR = 11

NO_CHANGE_SOURCE = 0
CPRSNT_LEGACY_MODE_CHANGE_SOURCE = (1<<0)
PCIE_RESET_CHANGE_SOURCE = (1<<3)
DRIVE_TYPE_INSTALL_CHANGE_SOURCE = (1<<4)
OP_STATE_CHANGE_COURCE = (1<<5)
UBM_CONTROLLER_RESET_CHANGE_SOURCE = (1<<7)

DRIVE_INSTALL_TYPE_EDSFF = 0
DRIVE_INSTALL_TYPE_1001_PCIE = 1
DRIVE_INSTALL_TYPE_RSVD0 = 2
DRIVE_INSTALL_TYPE_GEN_Z = 3
DRIVE_INSTALL_TYPE_SAS_SATA = 4
DRIVE_INSTALL_TYPE_NVME = 5
DRIVE_INSTALL_TYPE_RSVD1 = 6
DRIVE_INSTALL_TYPE_BAY_EMPTY = 7

def CalculateFRUChecksum(data, startByte, endByte):
        checksumOut = 0
        for x in range(startByte, endByte):
            checksumOut += data[x]
            checksumOut &= 0xFF
        checksumOut = 255 - checksumOut + 1
        return checksumOut

def CalulateReadChecksum(data):
        checksum = 0xFF & (sum(data) + 0xA5)
        return 0xFF & ((255 - checksum) + 1)

def GetOperationalStateString(state):
    switcher = {
        0: "Invalid Operational State",
        1: "Operational State Initializing",
        2: "Operational State Busy",
        3: "Operational State Ready",
        4: "Operational State Reduced Functionality",
        }
    return switcher.get(state, "Operational State Reserved")

def GetProgrammingUpdateModeCapabilitiesString( byte):
    switcher = {
        0: "Programming Update is not supported",
        1: "Programming Update supported while Devices remain online",
        2: "Programming Update supported while Devices are offline",
        3: "Programming Update support is Vendor Specific"
    }
    return switcher.get((byte & 3))

def GetChangeCountSourceString(source):
    stringOut = ""
    if (CPRSNT_LEGACY_MODE_CHANGE_SOURCE == (CPRSNT_LEGACY_MODE_CHANGE_SOURCE&source)):
        stringOut += "CPRSNT Legacy Mode Change /"
    if (PCIE_RESET_CHANGE_SOURCE == (PCIE_RESET_CHANGE_SOURCE&source)):
        stringOut += "PCIe Reset Change /"
    if (DRIVE_TYPE_INSTALL_CHANGE_SOURCE == (DRIVE_TYPE_INSTALL_CHANGE_SOURCE&source)):
        stringOut += "Drive Type Install Change /"
    if (OP_STATE_CHANGE_COURCE == (OP_STATE_CHANGE_COURCE&source)):
        stringOut += "Op State Change"
    if (UBM_CONTROLLER_RESET_CHANGE_SOURCE == (UBM_CONTROLLER_RESET_CHANGE_SOURCE&source)):
        stringOut += "UBM Controller Reset Change"

    return stringOut

LAST_COMMAND_STATUS_STRING_DICT = {0: "Failed",
                                1: "Success",
                                2: "Invalid Checksum",
                                3: "Too Many Bytes Written",
                                4: "No Access Allowed",
                                5: "Change Count Does Not Match",
                                6: "Busy",
                                7: "Command Not Implemented",
                                8: "Invalid Descriptor Index",}

def PrintOperationState(opState):
    print("Operational State: ", GetOperationalStateString(opState))

def PrintLastCommandStatus(status):
    try:
        print("Last Command Status: ", LAST_COMMAND_STATUS_STRING_DICT[status])
    except:
        print("Last Command Status: Unkown")

def PrintSiliconIdentity(siliconIdentiy):
    print("Silicon Identity:")
    printString = "UBM Spec Version Version "
    printString += "{:x}.".format(siliconIdentiy[0]>>4)
    printString += "{:x}".format(siliconIdentiy[0]&0x0F)
    print(printString)
    print("PCIe Vendor ID: ", hex(((siliconIdentiy[2]<<8) | siliconIdentiy[1])))
    print("UBM Controller Device Code: ", hex(((siliconIdentiy[7]<<24) | (siliconIdentiy[6]<<16) | (siliconIdentiy[5]<<8) | siliconIdentiy[4])))
    printString = "UBM Controller Image Version "
    printString += "{0}.".format(siliconIdentiy[11])
    printString += "{0}".format(siliconIdentiy[10])
    print(printString)
    print("Vendor Specific Byte 12: ", hex(siliconIdentiy[12]))
    print("Vendor Specific Byte 12: ", hex(siliconIdentiy[13]))

def PrintProgrammingCapabilities(capabilities):
    print("Update mode: ", GetProgrammingUpdateModeCapabilitiesString(capabilities))

def PrintHFCInfo( hfcInfo):
    print("Host Facing Connector ID: ", hfcInfo & 0x0F)
    if 1 == (hfcInfo>>7):
        print("Port Type: Segregated")
    else:
        print("Port Type: Converged")

def PrintBackplaneInfo( bpInfo):
    print("Backplane Number :", bpInfo&0x0F)
    print("Backplane Type :", bpInfo>>5)

def PrintStartingSlot(startingSlot):
    print("Starting Slot Offset: ", startingSlot)

TwoWireResetCapabilityString_Dict = {0: "2 Wire Reset is not supported",
                                    1: "2 Wire Slave Reset and 2Wire Mux is supported",
                                    2: "UBM FRU and UBM Controller is supported",
                                    3: "2Wire Slave Reset and UBM FRU and UBM Controller and 2Wire Mux are supported"}

def PrintCapabilities(capabilities):
    print("Capabilities Byte 0: ", hex(capabilities[0]))
    print("Clock Routing Present: ", capabilities[0]&1)
    print("Slot Power Control: ", (capabilities[0]>>1)&1)
    print("PCIe Reset Control: ", (capabilities[0]>>2)&1)
    print("Dual Port: ", (capabilities[0]>>3)&1)
    print("2-Wire Reset Support: ", TwoWireResetCapabilityString_Dict[(capabilities[0]>>4)&3])
    print("Change Detect Interrupt Operation: ", (capabilities[0]>>6)&1)
    print("DFC Change Count: ", (capabilities[0]>>7)&1)

    print("Capabilities Byte 1: ", hex(capabilities[1]))
    print("PRSNT Reported: ", (capabilities[1]>>0)&1)
    print("IFDET 1 Reported: ", (capabilities[1]>>1)&1)
    print("IFDET 2 Reported: ", (capabilities[1]>>2)&1)
    print("DFC PERST Management Override supported: ", (capabilities[1]>>3)&1)
    print("DFC SMBus Reset Control Supported: ", (capabilities[1]>>4)&1)

DFCPerstManagementOverride_Dict = { 0: "No Override",
                                    1: "DFC PERST Managed upon install",
                                    2: "DFC PERST Automatically released upon install",
                                    3: "Reserved"}

def PrintFeatures(features):
    print("Features Byte 0: ", hex(features[0]))
    print("Read Checksum Creation: ", features[0]&1)
    print("Write Checksum Checking: ", (features[0]>>1)&1)
    print("CPRSNT Legacy Mode: ", (features[0]>>2)&1)
    print("PCIe Reset Change Count Mask: ", (features[0]>>3)&1)
    print("Drive Type Install Change Count Mask: ", (features[0]>>4)&1)
    print("Operational State Change Count Mask: ", (features[0]>>5)&1)
    print("DFC PERST Management Override: ", DFCPerstManagementOverride_Dict[(features[0]>>6)&3])

    print("Features Byte 1: ", hex(features[1]))
    print("DFC SMBus Reset Control: ", (features[1]>>0)&1)

def PrintFeaturesWrite(features):
    print("Features Write Byte 0: ", hex(features[0]))
    print("Read Checksum Creation: ", features[0]&1)
    print("Write Checksum Checking: ", (features[0]>>1)&1)
    print("CPRSNT Legacy Mode: ", (features[0]>>2)&1)
    print("PCIe Reset Change Count Mask: ", (features[0]>>3)&1)
    print("Drive Type Install Change Count Mask: ", (features[0]>>4)&1)
    print("Operational State Change Count Mask: ", (features[0]>>5)&1)
    print("DFC PERST Management Override: ", DFCPerstManagementOverride_Dict[(features[0]>>6)&3])

    print("Features Write Byte 1: ", hex(features[1]))
    print("DFC SMBus Reset Control: ", (features[1]>>0)&1)

def PrintChangeCount(changeCount):
    print("Change Count Reported:", changeCount[0])
    print("Change Source:", GetChangeCountSourceString(changeCount[1]))

def PrintChangeCountWrite(changeCount):
    print("Change Count Written: ", changeCount[0])

def GetDriveInstallBitsString(bits):
    switcher = {
        DRIVE_INSTALL_TYPE_RSVD0: "Reserved 0 Drive Installed",
        DRIVE_INSTALL_TYPE_1001_PCIE: "1001 PCIe Drive Installed",
        DRIVE_INSTALL_TYPE_RSVD1: "Reserved 1 Drive Installed",
        DRIVE_INSTALL_TYPE_GEN_Z: "Gen Z Drive Installed",
        DRIVE_INSTALL_TYPE_SAS_SATA: "SAS/ SATA Drive Installed",
        DRIVE_INSTALL_TYPE_NVME: "NVMe Drive Installed",
        DRIVE_INSTALL_TYPE_EDSFF: "EDSFF Drive Installed",
        DRIVE_INSTALL_TYPE_BAY_EMPTY: "No Drive Installed",
        }
    return switcher.get(bits)

STATUS_CODE_UNSUPPORTED = 0
STATUS_CODE_OK = 1
STATUS_CODE_CRITICAL = 2
STATUS_CODE_NON_CRITICAL = 3
STATUS_CODE_UNRECOVERABLE = 4
STATUS_CODE_NOT_INSTALLED = 5
STATUS_CODE_UNKNOWN = 6
STATUS_CODE_NOT_AVAILABLE = 7
STATUS_CODE_NO_ACCESS = 8

def GetDriveStatusCodeString(bits):
    switcher = {
        STATUS_CODE_UNSUPPORTED: "Unsupported",
        STATUS_CODE_OK: "OK",
        STATUS_CODE_CRITICAL: "Critical",
        STATUS_CODE_NON_CRITICAL: "Non-Critical",
        STATUS_CODE_UNRECOVERABLE: "Unrecoverable",
        STATUS_CODE_NOT_INSTALLED: "Not Installed",
        STATUS_CODE_UNKNOWN: "Unknown",
        STATUS_CODE_NOT_AVAILABLE: "Not Available",
        STATUS_CODE_NO_ACCESS: "No Access",
    }
    return switcher.get(bits, "RSVD")

def GetDrivePWRDISString(dfcDescByte4):
    switcher = {
        0: "PWRDIS OFF",
        16: "PWDRIS ON"}
    return switcher.get(dfcDescByte4&0x10)

def GetDrivePCIeResetString(dfcDescByte0):
    switcher = {
        0: "PCIe Reset NOP",
        1: "PCIe Reset Initiate",
        2: "PCIe Reset Held Low",
        3: "PCIe Reset Reserved"}
    return switcher.get(dfcDescByte0>>6)

def GetDrivePCIeResetCommandString(dfcDescByte0):
    switcher = {
        0: "PCIe Reset NOP",
        1: "PCIe Reset Hold High",
        2: "PCIe Reset Hold Low",
        3: "PCIe Reset Reserved"}
    return switcher.get(dfcDescByte0>>6)

def PrintDFCDescriptor( descriptor):
    print("Drive Descriptor Byte 0: ", hex(descriptor[0]))
    print("Drive Type Installed: ", GetDriveInstallBitsString(descriptor[0]&7))
    print("Bifurcate Port: ", (descriptor[0]>>5)&1)
    print("PCIe Reset: ", GetDrivePCIeResetString(descriptor[0]))

    print("Drive Descriptor Byte 1: ", hex(descriptor[1]))
    print("Status Code: ", GetDriveStatusCodeString(descriptor[1]&0x0F))
    print("Swap Bit: ", (descriptor[1]>>4) & 1)
    print("Disable Bit: ", (descriptor[1]>>5) & 1)
    print("Predict Failure Bit: ", (descriptor[1]>>6) & 1)

    print("Drive Descriptor Byte 2: ", hex(descriptor[2]))
    print("R/R Abort Bit: ",        (descriptor[2]>>0) & 1)
    print("Rebuild/Remap  Bit: ",   (descriptor[2]>>1) & 1)
    print("in Failed Array Bit: ",  (descriptor[2]>>2) & 1)
    print("in Critical Array Bit: ",(descriptor[2]>>3) & 1)
    print("Cons Check Bit: ",       (descriptor[2]>>4) & 1)
    print("Hot Spare Bit: ",        (descriptor[2]>>5) & 1)
    print("Rsvd Device Bit: ",      (descriptor[2]>>6) & 1)
    print("OK Bit: ",               (descriptor[2]>>7) & 1)

    print("Drive Descriptor Byte 3: ", hex(descriptor[3]))
    print("Report Bit: ",                   (descriptor[3]>>0) & 1)
    print("Identify Bit: ",                 (descriptor[3]>>1) & 1)
    print("Remove Bit: ",                   (descriptor[3]>>2) & 1)
    print("Ready to Insert Bit: ",          (descriptor[3]>>3) & 1)
    print("Enclosure Bypassed A Bit: ",     (descriptor[3]>>4) & 1)
    print("Enclosure Bypassed B Bit: ",     (descriptor[3]>>5) & 1)
    print("Do Not Remove Bit: ",            (descriptor[3]>>6) & 1)
    print("Active Bit: ",                   (descriptor[3]>>7) & 1)

    print("Drive Descriptor Byte 4: ", hex(descriptor[4]))
    print("Device Bypassed B: ",        (descriptor[4]>>0) & 1)
    print("Device Bypassed A: ",        (descriptor[4]>>1) & 1)
    print("Bypassed B: ",               (descriptor[4]>>2) & 1)
    print("Bypassed A: ",               (descriptor[4]>>3) & 1)
    print("Device Off: ",               (descriptor[4]>>4) & 1)
    print("Fault Requested: ",          (descriptor[4]>>5) & 1)
    print("Fault Sensed: ",             (descriptor[4]>>6) & 1)
    print("App Client Bypassed B: ",    (descriptor[4]>>7) & 1)

    print("DFC Change Count: ", descriptor[5])
    print("Vendor Specific Byte 6: ", hex(descriptor[6]))
    print("Vendor Specific Byte 7: ", hex(descriptor[7]))

def PrintDFCDescriptorWrite(descriptor):
    print("Drive Descriptor Write Byte 0: ", hex(descriptor[0]))
    print("PCIe Reset: ", GetDrivePCIeResetCommandString(descriptor[0]))

    print("Drive Descriptor Write Byte 1: ", hex(descriptor[1]))
    print("Swap Bit: ", (descriptor[1]>>4) & 1)
    print("Disable Bit: ", (descriptor[1]>>5) & 1)
    print("Predict Failure Bit: ", (descriptor[1]>>6) & 1)
    print("Select Bit: ", (descriptor[1]>>7) & 1)

    print("Drive Descriptor Write Byte 2: ", hex(descriptor[2]))
    print("Request R/R Abort Bit: ",        (descriptor[2]>>0) & 1)
    print("Request Rebuild/Remap  Bit: ",   (descriptor[2]>>1) & 1)
    print("Request in Failed Array Bit: ",  (descriptor[2]>>2) & 1)
    print("Request in Critical Array Bit: ",(descriptor[2]>>3) & 1)
    print("Request Cons Check Bit: ",       (descriptor[2]>>4) & 1)
    print("Request Hot Spare Bit: ",        (descriptor[2]>>5) & 1)
    print("Request Rsvd Device Bit: ",      (descriptor[2]>>6) & 1)
    print("Request OK Bit: ",               (descriptor[2]>>7) & 1)

    print("Drive Descriptor Write Byte 3: ", hex(descriptor[3]))
    print("Request Identify Bit: ",                 (descriptor[3]>>1) & 1)
    print("Request Remove Bit: ",                   (descriptor[3]>>2) & 1)
    print("Request Insert Bit: ",          (descriptor[3]>>3) & 1)
    print("Do Not Remove Bit: ",            (descriptor[3]>>6) & 1)
    print("Active Bit: ",                   (descriptor[3]>>7) & 1)

    print("Drive Descriptor Write Byte 4: ", hex(descriptor[4]))
    print("Enable Bypassed B: ",               (descriptor[4]>>2) & 1)
    print("Enable Bypassed A: ",               (descriptor[4]>>3) & 1)
    print("Device Off: ",               (descriptor[4]>>4) & 1)
    print("Request Fault: ",          (descriptor[4]>>5) & 1)