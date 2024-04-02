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
#*******************************************************************************
# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions
from enum import Enum, auto
from dataclasses import dataclass
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from saleae.data import GraphTime
import lib_ubm_commands as ubm
import lib_ubm_fru as fru
import lib_ubm_fwupdate as fwupdate

FRU_ADDRESS = 0x57

class I2CState(Enum):
    IDLE  = auto()
    START = auto()
    DATA  = auto()

@dataclass
class SaleaeFrame:
    start_time: GraphTime
    end_time: GraphTime
    data: bytearray
    read: bool
    address: int

# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer.
    ubmAddress = StringSetting(label = '7-bit UBM Controller Address in hex format (0x55)')

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''
        self.accessCountList = [[ubm.GET_OPERATION_STATE, 0], [ubm.GET_LAST_COMMAND_STATUS, 0], [ubm.GET_SILICON_IDENTITY, 0], [ubm.GET_UPDATE_CAPABILITIES, 0],
                                [ubm.GET_HFC_INFO, 0], [ubm.GET_BACKPLANE_INFO, 0], [ubm.GET_STARTING_SLOT, 0], [ubm.GET_CAPABILITIES, 0],
                                [ubm.GET_FEATURES, 0], [ubm.GET_CHANGE_COUNT, 0], [ubm.GET_DFC_INDEX, 0], [ubm.GET_DFC_STATUS_CONTROL, 0],
                                [ubm.ENTER_PROGRAMMING_MODE, 0], [ubm.PROGRAM_MODE_DATA_TRANSFER, 0], [ubm.EXIT_PROGRAMING_MODE, 0]]
        self.fruAccessCount = 0
        self.lastCommand = 0
        self.lastSubCommand = 0
        self.ubmAddress = int(self.ubmAddress, 16)
        self.reset()

    def reset(self):
        self.state      = I2CState.IDLE
        self.address    = None
        self.data       = bytearray()
        self.start_time = None
        self.read       = False
    
    def GetAccessCountIndex(self, cmd):
        for i, sublist in enumerate(self.accessCountList):
            if cmd == sublist[0]:
                return i

    def I2CFrameStateMachine(self, frame):
        out = None
        if self.state == I2CState.IDLE:
            if frame.type == "start":
                self.state = I2CState.START
                self.start_time = frame.start_time
                return out
        elif self.state == I2CState.START:
            if frame.type == "address" and frame.data["ack"]:
                self.read |= frame.data["read"]
                self.address = frame.data["address"][0]
                if (self.ubmAddress == self.address) | (FRU_ADDRESS == self.address):
                    self.state = I2CState.DATA
                    return out
        elif self.state == I2CState.DATA:
            if frame.type == "data":
                self.data.extend(frame.data["data"])
                return out
            elif frame.type == "start":
                self.state = I2CState.START
                return out
            elif frame.type == "stop":
                self.state = I2CState.IDLE
                out = SaleaeFrame(
                    start_time=self.start_time,
                    end_time=frame.end_time,
                    read=self.read,
                    data=self.data,
                    address=self.address
                )
        self.reset()
        return out
    
    def PrintParsedData(self, address, data, isRead):
        
        
        if self.ubmAddress == address:
            cmd = data[0]
            if ubm.ENTER_PROGRAMMING_MODE == cmd:
                print("Enter Programming Mode Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                if not isRead:
                    fwupdate.PrintEnterProgrammingModeCommandWrite(data[1:])
            elif ubm.PROGRAM_MODE_DATA_TRANSFER == cmd:
                if not isRead:
                    fwupdate.PrintProgrammingModeSubCommandWrite(data[1:])
            elif ubm.PROGRAM_MODE_DATA_TRANSFER == self.lastCommand:
                if isRead:
                    fwupdate.PrintProgrammingModeSubCommandRead(self.lastSubCommand, data)
            elif ubm.EXIT_PROGRAMING_MODE == cmd:
                if not isRead:
                    fwupdate.PrintExitProgrammingModeCommandWrite(data[1:])
            elif ubm.GET_OPERATION_STATE == cmd:
                print("Get Operational State Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintOperationState(data[2])
            elif ubm.GET_LAST_COMMAND_STATUS == cmd:
                print("Get Last Command Status Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintLastCommandStatus(data[2])
            elif ubm.GET_SILICON_IDENTITY == cmd:
                print("Get Silicon Identity Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintSiliconIdentity(data[2:])   
            elif ubm.GET_UPDATE_CAPABILITIES == cmd:
                print("Get Update Capabilities Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintProgrammingCapabilities(data[2])   
            elif ubm.GET_HFC_INFO == cmd:
                print("Get HFC Info Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintHFCInfo(data[2])   
            elif ubm.GET_BACKPLANE_INFO == cmd:
                print("Get HFC Info Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintBackplaneInfo(data[2])  
            elif ubm.GET_STARTING_SLOT == cmd:
                print("Get Starting Slot Offset Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintStartingSlot(data[2])  
            elif ubm.GET_CAPABILITIES == cmd:
                print("Get Capabilities Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                ubm.PrintCapabilities(data[2:])  
            elif ubm.GET_FEATURES == cmd:
                print("Features Command Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                if isRead:
                    ubm.PrintFeatures(data[2:])  
                else:
                    ubm.PrintFeaturesWrite(data[1:])
            elif ubm.GET_CHANGE_COUNT == cmd:
                print("Change Count Command Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                if isRead:
                    ubm.PrintChangeCount(data[2:])  
                else:
                    ubm.PrintChangeCountWrite(data[1:])
            elif ubm.GET_DFC_INDEX == cmd:
                print("DFC Index Command Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                if isRead:
                    print("DFC Index Read:", data[2])
                else:
                    print("DFC Index Written:", data[1])
            elif ubm.GET_DFC_STATUS_CONTROL == cmd:
                print("DFC Descriptor Command Access Count:", self.accessCountList[self.GetAccessCountIndex(cmd)][1])
                if isRead:
                    ubm.PrintDFCDescriptor(data[2:])
                else:
                    ubm.PrintDFCDescriptorWrite(data[1:])
            

        if FRU_ADDRESS == address:
            fru.PrintUBMFru(data[2:])

        print("")

    def GetUBMOperation(self, address, data, isRead):
        if self.ubmAddress == address:
            cmd = data[0]
            if ubm.ENTER_PROGRAMMING_MODE == cmd:
                if isRead:
                    return "Read Enter Programming Mode Command"
                else:
                    return "Write to Enter Programming Mode Command"
            elif ubm.PROGRAM_MODE_DATA_TRANSFER == cmd:
                if isRead:
                    return "Read from " + fwupdate.GetSubCommandString(self.lastSubCommand)
                else:
                    return "Write to " + fwupdate.GetSubCommandString(data[1])
            elif ubm.EXIT_PROGRAMING_MODE == cmd:
                if isRead:
                    return "Read from Exit Programming Mode Command"
                else: 
                    return "Write to Exit Programming Mode Command"
            elif ubm.PROGRAM_MODE_DATA_TRANSFER == self.lastCommand:
                if isRead:
                    return "Read from " + fwupdate.GetSubCommandString(self.lastSubCommand)
            elif ubm.GET_OPERATION_STATE == cmd:
                return "Read Operational State"
            elif ubm.GET_LAST_COMMAND_STATUS == cmd:
                return "Read Last Command Status"
            elif ubm.GET_SILICON_IDENTITY == cmd:
                return "Read Silicon Identity"
            elif ubm.GET_UPDATE_CAPABILITIES == cmd:
                return "Read Update Capabilities"
            elif ubm.GET_HFC_INFO == cmd:
                return "Read HFC Info"
            elif ubm.GET_BACKPLANE_INFO == cmd:
                return "Read Backplane Info"
            elif ubm.GET_STARTING_SLOT == cmd:
                return "Read Starting Slot Offset"
            elif ubm.GET_CAPABILITIES == cmd:
                return "Read Capabilities"
            elif ubm.GET_FEATURES == cmd:
                if isRead:
                    return "Read Features"
                else:
                    return "Write Features Byte"
            elif ubm.GET_CHANGE_COUNT == cmd:
                if isRead:
                    return "Read Change Count"
                else:
                    return "Write Change Count"
            elif ubm.GET_DFC_INDEX == cmd:
                if isRead:
                    return "Read DFC Index"
                else:
                    return "Write DFC Index"
            elif ubm.GET_DFC_STATUS_CONTROL == cmd:
                if isRead:
                    return "Read DFC Descriptor"
                else:
                    return "Write DFC Descriptor"
            
        if FRU_ADDRESS == address:
            return "Read of UBM FRU"
        
        return "Unknown operation"
    
    def GetUBMOperationAccessCount(self, address, data, isRead):
        returnVal = 0
        if self.ubmAddress == address:
            cmd = data[0]
            try:
                if (ubm.PROGRAM_MODE_DATA_TRANSFER == self.lastCommand) and isRead:
                    returnVal = self.accessCountList[self.GetAccessCountIndex(self.lastCommand)][1]-1
                else:
                    returnVal = self.accessCountList[self.GetAccessCountIndex(cmd)][1]
                    self.accessCountList[self.GetAccessCountIndex(cmd)][1] += 1
            except:
                print("Unable to increment access count for command: ", hex(cmd))

        if FRU_ADDRESS == address:
            return self.fruAccessCount
        
        return returnVal

    
    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        if i2c_frame := self.I2CFrameStateMachine(frame):
            if len(i2c_frame.data) > 3:
                self.PrintParsedData(i2c_frame.address, i2c_frame.data, i2c_frame.read)
                operation = self.GetUBMOperation(i2c_frame.address, i2c_frame.data, i2c_frame.read)
                accessCount = str(self.GetUBMOperationAccessCount(i2c_frame.address, i2c_frame.data, i2c_frame.read))
                self.lastCommand = i2c_frame.data[0]
                if ubm.PROGRAM_MODE_DATA_TRANSFER == self.lastCommand:
                    self.lastSubCommand = i2c_frame.data[1]
                return AnalyzerFrame(
                    "UBM Transaction",
                    i2c_frame.start_time,
                    i2c_frame.end_time,
                    {
                        "Operation": operation,
                        "Operation Access Count: ": accessCount
                    }
                    )
