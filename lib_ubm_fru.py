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

IPMI_OFFSET_MULTIPLIER = 8
IPMI_MULTIRECORD_OFFSET_BYTE = 5
RECORD_HEADER_SIZE = 5
RECORD_HEADER_TYPE_BYTE = 0
RECORD_HEADER_FORMAT_AND_EOL_BYTE = 1
RECORD_HEADER_SIZE_BYTE = 2
RECORD_HEADER_RECORD_CHECKSUM_BYTE = 3
RECORD_HEADER_CHECKSUM_BTYE = 4

RECORD_TYPE_UBM_OVERVIEW = 0xA0
RECORD_TYPE_PORT_ROUTE_INFO = 0xA1

def PrintIPMICommonHeader(data):
    print("IPMI Common Header")
    print("Format Version: ", data[0] & 0x0F)
    print("Internal Use Area Starting Offset:", data[1]*IPMI_OFFSET_MULTIPLIER)
    print("Chassis Info Area Starting Offset:", data[2]*IPMI_OFFSET_MULTIPLIER)
    print("Board Info Area Starting Offset:", data[3]*IPMI_OFFSET_MULTIPLIER)
    print("Product Info Area Starting Offset:", data[4]*IPMI_OFFSET_MULTIPLIER)
    print("Multirecord Area Starting Offset:", data[IPMI_MULTIRECORD_OFFSET_BYTE]*IPMI_OFFSET_MULTIPLIER)
    print("IPMI Header Checksum:", hex(data[7]))
    print("")

def IsRecordEOL(header):
    return (header[RECORD_HEADER_FORMAT_AND_EOL_BYTE]>>7) & 1

def GetRecordLength(header):
    return header[RECORD_HEADER_SIZE_BYTE]

def GetRecord(data, recordIndex):
    multiRecordStartOffset = data[IPMI_MULTIRECORD_OFFSET_BYTE]*IPMI_OFFSET_MULTIPLIER
    recordStart = multiRecordStartOffset
    for i in range(0, recordIndex):
        recordStart += data[recordStart + RECORD_HEADER_SIZE_BYTE] + RECORD_HEADER_SIZE
    
    return data[recordStart:]

def GetRecordTypeString(type):
    switcher = {
        RECORD_TYPE_UBM_OVERVIEW: "UBM Overview (0xA0)",
        RECORD_TYPE_PORT_ROUTE_INFO: "Port Route Info Area (0xA1)",
    }
    return switcher.get(type, "Unknown Record Type")

def PrintRecordHeader(header):
    print("Record Header")
    print("Record Type: ", GetRecordTypeString(header[RECORD_HEADER_TYPE_BYTE]))
    print("Record Format:", header[RECORD_HEADER_FORMAT_AND_EOL_BYTE]&0x0F)
    print("EOL bit:", IsRecordEOL(header))
    print("Record Length: ", header[RECORD_HEADER_SIZE_BYTE])
    print("Record Checksum:", hex(header[RECORD_HEADER_RECORD_CHECKSUM_BYTE]))
    print("Header Checksum:", hex(header[RECORD_HEADER_CHECKSUM_BTYE]))
    print("")

def Print2WireInfo(byte):
    switcher_1 = {
        0: "No Mux routed on HFC 2-Wire Interface (0)",
        1: "DFC 2-Wire interface behind MUX (1)",
        2: "reserved (2)",
        3: "UBM Controller and DFC 2-Wire interface located behind MUX (3)",
    }

    print("2-Wire Device Arrangement: ", switcher_1.get(byte&0x03))
    print("2-Wire MUX Address: ", (byte>>2) & 0x07)
    switcher_2 = {
        0: "No Limit (0)",
        1: "16 Bytes (1)",
        2: "32 Bytes (2)",
        3: "64 Bytes (3)",
        4: "128 Bytes (4)",
        5: "256 Bytes (5)",
    }
    print("UBM Controller 2-Wire Max Byte Count: ", switcher_2.get((byte>>5) & 0x07))

def Print2WireMuxInfoByte(byte):
    if 1 == (byte>>7) & 1:
        print("2-Wire Mux Description is Valid")
        if 1 == ((byte>>6) & 1):
            print("2-Wire Mux Enable Channel Method: Channels are selected using enable bit and channel byte (E.g., PCA9540, PCA9542, PCA9544, PCA9547) (bit = 1)")
        else:
            print("2-Wire Mux Enable Channel Method: Channels are selected using bit location (E.g., PCA9543,PCA9546, PCA9548) (bit = 0)")

        switcher_1 = {
            0: "Mux Enable is not applicable (0)",
            1: "Reserved (1)",
            2: "Mux Enable located at bit 2 of channel select byte (E.g., PCA9540, PCA9542, PCA9544)) (2)",
            3: "Mux Enable located at Bit 3 of Channel Select Byte (E.g., PCA9547) (3)"
        }
        print("2-Wire Mux Enable bit location: ", switcher_1.get((byte>>2) & 3))

        switcher_2 = {
            0: "No Mux implemented (0)",
            1: "2 Channel Mux implemented (1)",
            2: "4 Channel Mux implemented (2)",
            3: "8 Channel Mux implemented (3)",
        }
        print("2-Wire Mux Channel Count: ", switcher_2.get(byte & 3))
    else:
        print("2-Wire Mux Descriptor is not Valid")

def PrintUBMOverviewRecord(record):
    print("UBM Overview:")
    print("UBM Spec Version: {0}.{1}".format((record[5]>>4), record[5]&0x0F))

    Print2WireInfo(record[6])

    print("UBM FRU Invalid: ", record[7]&1)
    print("UBM Controller Max Time Limit: ", (record[7]>>1) & 0x7F, 'seconds')

    print("RCC: ", record[8]&1)
    print("WCC: ", (record[8]>>1) & 1)
    print("CLM: ", (record[8]>>2) & 1)
    print("PRCCM: ", (record[8]>>3) & 1)
    print("DTICCM: ", (record[8]>>4) & 1)
    print("OSCCM: ", (record[8]>>5) & 1)

    print("Number of DFC Status and Control Descriptors: ", record[10])
    print("Number of UBM Port Route Descriptors: ", record[11])
    print("Number of Backplane DFCs: ", record[12])
    print("Max Power per DFC: ", record[13])
    Print2WireMuxInfoByte(record[14])

def PrintUBMType(typeBit):
    if 1 == typeBit:
        print("UBM Controller Type: UBM Controller is Vendor specific (1)")
    else:
        print("UBM Controller Type: UBM Controller is defined by this specification (0)")

def PrintPortRouteByte3Byte(byte):
    switcher = {
        0: "1 lane (0)",
        1: "2 lanes (1)",
        2: "4 lanes (2)",
        3: "8 lanes (3)",
        4: "16 lanes (4)",
    }
    print("Link Width: ", switcher.get(byte&0x0F))

    if 1 == ((byte>>6) & 1):
        print("Port Type: Segregated (1)")
    else:
        print("Port Type: Converged  (0)")

    if 1 == ((byte>>7) & 1):
        print("Domain: Secondary Port")
    else:
        print("Domain: Primary Port")

def PrintMaxLinkRatesByte(byte):
    switcher_1 = {
        0: "Not Supported (0)",
        1: "3 Gb/s (1)",
        2: "6 Gb/s (2)",
        3: "No Limit (3)",
    }
    switcher_2 = {
        0: "Not Supported (0)",
        1: "PCIe-1 (2.5 GT/s) (1)",
        2: "PCIe-2 (5 GT/s) (2)",
        3: "PCIe-3 (3)",
        4: "PCIe-4 (16 GT/s) (4)",
        5: "PCIe-5 (32 GT/s) (5)",
        6: "PCIe-6 (TBD) (6)",
        7: "7h = No Limit (7)"
    }
    switcher_3 = {
        0: "Not Supported (0)",
        1: "SAS-1 (3 Gb/s) (1)",
        2: "SAS-2 (6 Gb/s) (2)",
        3: "SAS-3 (12 Gb/s) (3)",
        4: "SAS-4 (22.5 Gb/s) (4)",
        5: "SAS-5 (TBD) (5)",
        6: "SAS-6 (TBD) (6)",
        7: "7h = No Limit (7)"
    }
    print("Max SATA Link Rate: ", switcher_1.get(byte&0x03))
    print("Max PCIe Link Rate: ", switcher_2.get((byte>>2) & 7))
    print("Max SAS Link Rate: ", switcher_3.get((byte>>5) & 7))

def PrintPortRouteInfoRecord(record):
    numberOfDescriptors = int(record[RECORD_HEADER_SIZE_BYTE]/7)
    print("Port Route Info:")
    for descriptorIndex in range(0, numberOfDescriptors):
        offset = 7*descriptorIndex
        PrintUBMType(record[5 + offset]&1)
        print("UBM Controller Address: ", hex(record[5 + offset]>>1))

        print("DFC Status and Control Descriptor Index: ", record[6 + offset])

        print("Drive Type Supported Bits:")
        print("Other bit: ", record[7 + offset]&1)
        print("SFF TA 1001 PCIe Support: ", (record[7 + offset]>>1) & 1)
        print("Gen-Z Support: ", (record[7 + offset]>>3) & 1)
        print("SAS/SATA Support: ", (record[7 + offset]>>4) & 1)
        print("Quad PCIe Support: ", (record[7 + offset]>>5) & 1)
        print("DFC Empty Support: ", (record[7 + offset]>>7) & 1)

        PrintPortRouteByte3Byte(record[8 + offset])

        PrintMaxLinkRatesByte(record[9])

        print("HFC Starting Lane: ", record[10 + offset]&0x0F)
        print("HFC Identity: ", (record[10 + offset]>>4) & 0x0F)

        print("Slot Offset: ", record[11 + offset])

        print("")

def PrintRecord(record):
    recordType = record[RECORD_HEADER_TYPE_BYTE]

    if RECORD_TYPE_UBM_OVERVIEW == recordType:
        PrintUBMOverviewRecord(record)
    elif RECORD_TYPE_PORT_ROUTE_INFO == recordType:
        PrintPortRouteInfoRecord(record)

def PrintUBMFru(data):
    PrintIPMICommonHeader(data)

    recordIndex = 0
    while 1:
        record = GetRecord(data, recordIndex)
        PrintRecordHeader(record)
        PrintRecord(record)
        print("")
        if IsRecordEOL(record):
            return
        recordIndex += 1
        