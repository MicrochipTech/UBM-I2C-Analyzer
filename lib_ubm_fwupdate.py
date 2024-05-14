# Copyright 2024 Microchip Technology Incorporated
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

PROGRAMMING_SUB_COMMAND_GET_NVM_GEOMETRY = 0x01
PROGRAMMING_SUB_COMMAND_ERASE = 0x02
PROGRAMMING_SUB_COMMAND_GET_ERASE_STATUS = 0x03
PROGRAMMING_SUB_COMMAND_PROGRAM = 0x04
PROGRAMMING_SUB_COMMAND_GET_PROGRAM_STATUS = 0x05
PROGRAMMING_SUB_COMMAND_VERIFY = 0x06
PROGRAMMING_SUB_COMMAND_GET_VERIFY_STATUS = 0x07
PROGRAMMING_SUB_COMMAND_VERIFY_IMAGE = 0x08
PROGRAMMING_SUB_COMMAND_GET_VERIFY_IMAGE_STATUS = 0x09
PROGRAMMING_SUB_COMMAND_SET_ACTIVE_IMAGE = 0x0A
PROGRAMMING_SUB_COMMAND_ACTIVE_IMAGE_STATUS = 0x0B


def PrintEnterProgrammingModeCommandWrite(data):
    print("2-Wire Programming Address: ", hex(data[0]))
    print("Unlock Sequence 0:", hex(data[1]))
    print("Unlock Sequence 1:", hex(data[2]))
    print("Unlock Sequence 2:", hex(data[3]))
    print("Transfer to Programming Update Mode Bit: ", data[4]&1)

def PrintExitProgrammingModeCommandWrite(data):
    print("Lock Sequence 0:", hex(data[0]))
    print("Lock Sequence 1:", hex(data[1]))
    print("Lock Sequence 2:", hex(data[2]))
    print("Transfer to Programming Update Mode Bit: ", data[3]&1)

def GetSubCommandString(subCommand):
    switcher = {
        PROGRAMMING_SUB_COMMAND_GET_NVM_GEOMETRY : "Get NV Geometry",
        PROGRAMMING_SUB_COMMAND_ERASE : "Erase Sector",
        PROGRAMMING_SUB_COMMAND_GET_ERASE_STATUS : "Get Erase Status",
        PROGRAMMING_SUB_COMMAND_PROGRAM : "Program Sector",
        PROGRAMMING_SUB_COMMAND_GET_PROGRAM_STATUS : "Get Program Status",
        PROGRAMMING_SUB_COMMAND_VERIFY : "Verify Programmed Sector",
        PROGRAMMING_SUB_COMMAND_GET_VERIFY_STATUS : "Get Programmed Sector Verify Status",
        PROGRAMMING_SUB_COMMAND_VERIFY_IMAGE : "Verify Image",
        PROGRAMMING_SUB_COMMAND_GET_VERIFY_IMAGE_STATUS : "Get Verify Image Status",
        PROGRAMMING_SUB_COMMAND_SET_ACTIVE_IMAGE : "Set Active Image",
        PROGRAMMING_SUB_COMMAND_ACTIVE_IMAGE_STATUS : "Get Active Image Status",
    }

    return switcher.get(subCommand, "Unknown")

def GetProgrammableModeStatusString(status):
    switcher = {
        0: "Invalid (0)",
        1: "Success (1)",
        2: "Image Verify Failed (2)",
        3: "Unsupported Device (3)",
        4: "Non-Volatile Location Invalid (4)",
        5: "Unknown Error (5)",
        6: "Busy (6)"
    }
    return switcher.get(status, "Reserved {0}".format(status))

def PrintWriteToNVGeometrySubCommand(data):
    print("Write to NV Geometry Sub-Command")
    print("Number of Bytes: ", data[1])

def PrintReadFromNVGeometrySubCommand(data):
    print("Read of NV Geometry Sub-Command")
    print("Programmable Mode Status: ", GetProgrammableModeStatusString(data[0]))
    print("Number of Data Bytes: ", data[1])
    print("Number of Sectors: ", data[2])
    numSectors = data[2]
    print("Sector Size: ", data[3])
    offset = 4
    for sectorIndex in range(0, numSectors):
        print("Sector {0} First Index {1}".format(sectorIndex, data[offset + sectorIndex*2]))
        print("Sector {0} Last Index {1}".format(sectorIndex, data[offset + sectorIndex*2 + 1]))

def PrintWriteToEraseSubCommand(data):
    print("Write to Erase Sub-Command")
    print("Number of Bytes: ", data[1])
    print("Sector Number: ", data[2])
    print("Sector Index: ", data[3])
    print("Checksum: ", hex(data[4]))

def PrintWriteToGetEraseStatusSubCommand(data):
    print("Write to Get Erase Status Sub-Command")
    print("Number of Bytes: ", data[1])

def PrintReadFromGetEraseStatusSubCommand(data):
    print("Read From Get Erase Status Sub-Command")
    print("Programmable Mode Status: ", GetProgrammableModeStatusString(data[0]))
    print("Number of Bytes: ", data[1])
    print("Sector Number: ", data[2])
    print("Sector Index: ", data[3])
    print("Checksum: ", hex(data[4]))

def PrintWriteToProgramSubCommand(data):
    print("Write to Program Sub-Command")
    print("Number of Bytes: ", data[1])
    print("Sector Number: ", data[2])
    print("Sector Index: ", data[3])
    print("Application Seuqence Number: ", data[4])

def PrintWriteToGetProgramStatusSubCommand(data):
    print("Write to Get Program Status Sub-Command")
    print("Number of Bytes: ", data[1])

def PrintReadFromGetProgramStatusSubCommand(data):
    print("Read from Get Program Status Sub-Command")
    print("Programmable Mode Status: ", GetProgrammableModeStatusString(data[0]))
    print("Number of Bytes: ", data[1])
    print("Application Seuqence Number: ", data[2])

def PrintWriteToVerifySubCommand(data):
    print("Write to Verify Sub-Command")
    print("Number of Bytes: ", data[1])
    print("Sector Number: ", data[2])
    print("Sector Index: ", data[3])

def PrintWriteToGetVerifyStatusSubCommand(data):
    print("Write to Get Verify Status Sub-Command")
    print("Number of Bytes: ", data[1])

def PrintReadFromGetVerifyStatusSubCommand(data):
    print("Read from Get Verify Status Sub-Command")
    print("Programmable Mode Status: ", GetProgrammableModeStatusString(data[0]))
    print("Number of Bytes: ", data[1])
    print("Sector Number: ", data[2])
    print("Sector Index: ", data[3])

def PrintWriteToVerifyImageSubCommand(data):
    print("Write to Verify Image Sub-Command")
    print("Number of Bytes: ", data[1])
    print("Image Number: ", data[2])

def PrintWriteToGetVerifyImageStatusSubCommand(data):
    print("Write to Get Verify Image Status Sub-Command")
    print("Number of Bytes: ", data[1])

def PrintReadFromGetImageVerifyStatusSubCommand(data):
    print("Read from Get Image Verify Status Sub-Command")
    print("Programmable Mode Status: ", GetProgrammableModeStatusString(data[0]))
    print("Number of Bytes: ", data[1])
    print("Image Number: ", data[2])


def PrintProgrammingModeSubCommandWrite(data):
    subCommand = data[0]
    if PROGRAMMING_SUB_COMMAND_GET_NVM_GEOMETRY == subCommand:
        PrintWriteToNVGeometrySubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_ERASE == subCommand:
        PrintWriteToEraseSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_ERASE_STATUS == subCommand:
        PrintWriteToGetEraseStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_PROGRAM == subCommand:
        PrintWriteToProgramSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_PROGRAM_STATUS == subCommand:
        PrintWriteToGetProgramStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_VERIFY == subCommand:
        PrintWriteToVerifySubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_VERIFY_STATUS == subCommand:
        PrintWriteToGetVerifyStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_VERIFY_IMAGE == subCommand:
        PrintWriteToVerifyImageSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_VERIFY_IMAGE_STATUS == subCommand:
        PrintWriteToGetVerifyImageStatusSubCommand(data)

def PrintProgrammingModeSubCommandRead(subCommand, data):
    
    if PROGRAMMING_SUB_COMMAND_GET_NVM_GEOMETRY == subCommand:
        PrintReadFromNVGeometrySubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_ERASE_STATUS == subCommand:
        PrintReadFromGetEraseStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_PROGRAM_STATUS == subCommand:
        PrintReadFromGetProgramStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_VERIFY_STATUS == subCommand:
        PrintReadFromGetVerifyStatusSubCommand(data)
    elif PROGRAMMING_SUB_COMMAND_GET_VERIFY_IMAGE_STATUS == subCommand:
        PrintReadFromGetImageVerifyStatusSubCommand(data)