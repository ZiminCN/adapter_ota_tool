import can
from typing import List

class CanTool:
        def __init__(self):
                ota_filters = [
                        {
                        "can_id": 0x387, 
                        "can_mask": 0x7FF,  # 11位标准帧掩码
                        "extended": False   # 标准帧
                        },
                ]
                self.can_bus = can.Bus(interface='socketcan', channel='can0', fd=True, can_filters=ota_filters)
                
        def __del__(self):
                self.can_bus.shutdown()
                return
                
        def send_can_data(self, is_fd: bool, bitrate_switch: bool, can_id: int, can_data: List[int]):
                can_message = can.Message(is_fd=is_fd, bitrate_switch=bitrate_switch, arbitration_id=can_id, data=can_data, is_extended_id=False)
                self.can_bus.send(can_message, timeout=0.2)
                
        def receive_can_data(self):
                rx_message = self.can_bus.recv(timeout=0)
                return rx_message
                