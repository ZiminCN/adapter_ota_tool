from typing import List
import sys
import os
from dataclasses import dataclass, field
from typing import Optional, List
from enum import IntEnum
import struct
import time
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.abspath(current_dir))
sys.path.append(os.path.join(project_root, 'can_tool'))
sys.path.append(os.path.join(project_root, 'hex_decoder'))


from hex_parser import HexParser
from can_tool import CanTool

class OTA_CAN_ID_E(IntEnum):
        CANFD_ID_R2A_OTA_BOARDCAST_ID=0x386
        CANFD_ID_R2A_OTA_ACK_ID=0x387

class OTA_ORDER_E(IntEnum):
	OTA_ORDER_TRY_CONNECT = 0x00,
	OTA_ORDER_DEVICE_INFO = 0x01,
	OTA_ORDER_FIRMWARE_INFO = 0x02,
	OTA_ORDER_UPGRADE = 0x03,
 
class OTA_ACK_E(IntEnum):
	OTA_ACK_OKAY = 0x00,
	OTA_ACK_FAIL = 0x01, 

@dataclass
class OTA_INFO_T:
        ota_order: OTA_ORDER_E = OTA_ORDER_E.OTA_ORDER_TRY_CONNECT # u8
        current_package_index: int = 1 #u16, start from 1
        total_package_index: int = 1 #u16
        data_len: int = 1 #u16
        data: List[int] = field(default_factory=list)
        
        # 序列化为字节串
        def to_list(self, include_data: bool = True) -> List[int]:
                header = struct.pack(
                        '<BHHH', # little endian
                        self.ota_order.value,
                        self.current_package_index,
                        self.total_package_index,
                        self.data_len
                )
                
                can_data = list(header)
                
                if include_data and self.data:
                        can_data.extend(self.data)

                return can_data
                
        # 反序列化为结构体
        @classmethod
        def from_list(cls, data_list: List[int]) -> 'OTA_INFO_T':
                if len(data_list) < 7:
                        raise ValueError("数据长度不足，疑似错误帧")
                
                data_bytes = bytes(data_list)
                
                header = data_bytes[:7]
                ota_order, current_package_index, total_package_index, data_len = struct.unpack('<BHHH', header)
                
                if data_len > 0:
                        data_bytes = data_bytes[7:(7 + data_len)]
                else:
                        data_bytes = b''
                
                return cls(
                        ota_order=OTA_ORDER_E(ota_order),
                        current_package_index=current_package_index,
                        total_package_index=total_package_index,
                        data_len=data_len,
                        data=data_bytes
                )

class AdapterDevInfo:
        def __init__(self, hex_file_path: str):
                self.can_tool_handle = CanTool()
                self.hex_parser_handle = HexParser(hex_file_path)
                self.ota_info = OTA_INFO_T()
                self.is_wait_for_try_connect_ack = False
                self.is_wait_for_get_dev_info_ack = False
                self.is_wait_for_notic_firmware_ack = False
                self.is_wait_for_upgrade_ack = False
                self.is_wait_for_end_upgrade_ack = False
                self.is_wait_for_check_upgrade_success_ack = False
                
                self.firmware_total_package = 0
                return
        
        def __del__(self):
                return
        
        def ota_try_connect_adapter(self):
                self.ota_info.ota_order = OTA_ORDER_E.OTA_ORDER_TRY_CONNECT 
                self.ota_info.current_package_index = 1
                self.ota_info.total_package_index = 1
                self.ota_info.data_len = 1
                self.ota_info.data = [0xFF]
                
                can_data: List[int] = self.ota_info.to_list(True)
                
                # self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                
                #! for test can2.0.
                while (self.is_wait_for_try_connect_ack == False):
                        self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                        time.sleep(0.2)
                
                print("Send ota_try_connect_adapter...")
                return
        
        def ota_get_adapter_dev_info(self):
                self.ota_info.ota_order = OTA_ORDER_E.OTA_ORDER_DEVICE_INFO
                self.ota_info.current_package_index = 1
                self.ota_info.total_package_index = 1
                self.ota_info.data_len = 1
                self.ota_info.data = [0x02]
                
                can_data: List[int] = self.ota_info.to_list(True)
                
                # self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                
                #! for test can2.0.
                while (self.is_wait_for_get_dev_info_ack == False):
                        self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                        time.sleep(1.5)
                
                print("Send ota_get_adapter_dev_info...")
                return
        
        def ota_notic_firmware_info(self):
                self.ota_info.ota_order = OTA_ORDER_E.OTA_ORDER_FIRMWARE_INFO
                self.ota_info.current_package_index = 1
                self.ota_info.total_package_index = 1
                self.ota_info.data_len = 1
                self.ota_info.data = [0x03]
                
                can_data: List[int] = self.ota_info.to_list(True)
                
                # self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                
                #! for test can2.0.
                while (self.is_wait_for_notic_firmware_ack == False):
                        self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                        time.sleep(1.5)
                        
                print("Send ota_notic_firmware_info...")
                return
        
        def ota_upgrade(self):
                # get the count of all package cnt
                canfd_frame_size = 64
                canfd_frame_header_size = 7
                canfd_frame_data_size = canfd_frame_size - canfd_frame_header_size
                hex_file_total_size = self.hex_parser_handle.get_hex_file_total_bytes_size()
                
                judge_ret:int = (self.hex_parser_handle.get_hex_file_total_bytes_size()) % (canfd_frame_data_size)
                if judge_ret != 0:
                        temp_total_package_cnt = (self.hex_parser_handle.get_hex_file_total_bytes_size())//(canfd_frame_data_size) + 1
                else:
                        temp_total_package_cnt = (self.hex_parser_handle.get_hex_file_total_bytes_size())//(canfd_frame_data_size)
                
                self.ota_info.ota_order = OTA_ORDER_E.OTA_ORDER_UPGRADE
                self.ota_info.total_package_index = temp_total_package_cnt
                # print(f"hex_file_total_size is {hex_file_total_size}")
                # print(f"self.ota_info.total_package_index is {self.ota_info.total_package_index}")
                
                for i in range(self.ota_info.total_package_index):
                        i: int = i
                        self.ota_info.current_package_index = (i + 1)
                        
                        # check last bytes size
                        if (self.ota_info.current_package_index * (canfd_frame_data_size) > hex_file_total_size):
                                self.ota_info.data_len = hex_file_total_size - (self.ota_info.current_package_index * (canfd_frame_data_size - 1))
                        else:
                                self.ota_info.data_len = canfd_frame_data_size
                        
                        # send data
                        hex_file_data = self.hex_parser_handle.ger_hex_file_data((self.ota_info.current_package_index - 1) * (canfd_frame_data_size), self.ota_info.data_len)
                        self.ota_info.data = hex_file_data
                        can_data: List[int] = self.ota_info.to_list(True)
                                                
                        # self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                        
                        # wait for ack
                        while((self.is_wait_for_upgrade_ack == False) and (self.is_wait_for_end_upgrade_ack == False)):
                                time.sleep(0.001)
                                self.can_tool_handle.send_can_data(True, True, OTA_CAN_ID_E.CANFD_ID_R2A_OTA_BOARDCAST_ID, can_data)
                        
                        if (self.ota_info.current_package_index) == (self.ota_info.total_package_index):
                                break
                        else:
                                self.is_wait_for_upgrade_ack = False 
                        
                        if self.is_wait_for_end_upgrade_ack == True:
                                return
                                
                return
        
        def ota_receive_process(self):
                
                # init
                
                dev_info_data = [0x00]
                
                while(self.is_wait_for_check_upgrade_success_ack == False):
                        get_message = self.can_tool_handle.receive_can_data()
                        if(get_message == None):
                                continue
                        else:
                                match get_message.arbitration_id:
                                        case OTA_CAN_ID_E.CANFD_ID_R2A_OTA_ACK_ID:
                                                if get_message.data[0] == OTA_ORDER_E.OTA_ORDER_TRY_CONNECT:
                                                        return_data_status = (get_message.data[6])
                                                        if return_data_status == 0x01:
                                                                print("Error! Unexpected Error Occurred")
                                                        else:
                                                                print("get OTA_ORDER_TRY_CONNECT Ack")
                                                                self.is_wait_for_try_connect_ack = True
                                                elif get_message.data[0] == OTA_ORDER_E.OTA_ORDER_DEVICE_INFO:      
                                                        return_current_package_cnt = (get_message.data[2] << 8) | (get_message.data[1])
                                                        return_total_package_cnt = (get_message.data[4] << 8) | (get_message.data[3])                                 
                                                                                                                
                                                        if return_current_package_cnt == return_total_package_cnt:                                                
                                                                self.is_wait_for_get_dev_info_ack = True
                                                elif get_message.data[0] == OTA_ORDER_E.OTA_ORDER_FIRMWARE_INFO:
                                                        return_data_status = (get_message.data[6])
                                                        if return_data_status == 0x01:
                                                                print("Error! Unexpected Error Occurred")
                                                        else:
                                                                print("get OTA_ORDER_FIRMWARE_INFO Ack")
                                                                self.is_wait_for_notic_firmware_ack = True
                                                elif get_message.data[0] == OTA_ORDER_E.OTA_ORDER_UPGRADE:
                                                        return_current_package_cnt = (get_message.data[2] << 8) | (get_message.data[1])
                                                        return_total_package_cnt = (get_message.data[4] << 8) | (get_message.data[3])
                                                        return_data_len = (get_message.data[6] << 8) | (get_message.data[5])
                                                        return_data_status = (get_message.data[6])
                                                        if (return_total_package_cnt == self.ota_info.total_package_index) and (return_current_package_cnt == self.ota_info.current_package_index) and (return_total_package_cnt == return_current_package_cnt):
                                                                print(f"\r Adapter OTA progree: {return_current_package_cnt}/{return_total_package_cnt}", end='', flush=True)
                                                                self.is_wait_for_end_upgrade_ack = True
                                                        if (return_total_package_cnt == self.ota_info.total_package_index) and (return_current_package_cnt == self.ota_info.current_package_index):
                                                                print(f"\r Adapter OTA progree: {return_current_package_cnt}/{return_total_package_cnt}", end='', flush=True)
                                                                self.is_wait_for_upgrade_ack = True
                                                        elif (return_total_package_cnt == 0x0001) and (return_current_package_cnt == 0x0001) and (return_data_len == 0x0001) and (return_data_status == 0x00):
                                                                print("\r\n Upgrade Success!")
                                                                self.is_wait_for_check_upgrade_success_ack = True                         
                
                return
