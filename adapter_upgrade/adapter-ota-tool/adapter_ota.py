import sys
import os
import argparse
import threading as thread

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'adapter_dev'))
sys.path.append(os.path.join(project_root, 'hex_decoder'))

from adapter_dev_info import AdapterDevInfo

class main:
        def __init__(self):
                parser = argparse.ArgumentParser(
                        description='No Hex File Path',
                        epilog='Usage: python3 adapter_ota.py -f firmware.hex'
                )
                
                parser.add_argument(
                        '-f', '--file',           # 短参数和长参数
                        required=True,            # 必须提供
                        help='Hex file path'      # 帮助信息
                )
                
                hex_file_path = parser.parse_args()
                
                if not os.path.exists(hex_file_path.file):
                        print(f"Error: file not exists.")
                        return
                
                print(f"hex file path: {hex_file_path.file}")
                        
                self.adapter_dev_handle = AdapterDevInfo(hex_file_path.file)
                
                send_thread = thread.Thread(target=self.ota_send_thread, name='send_thread')
                receive_thread = thread.Thread(target=self.ota_receive_thread, name='receive_thread')

                receive_thread.start()
                send_thread.start()
        
        def ota_send_thread(self):
                self.adapter_dev_handle.ota_try_connect_adapter()
                self.adapter_dev_handle.ota_get_adapter_dev_info()
                self.adapter_dev_handle.ota_notic_firmware_info()
                self.adapter_dev_handle.ota_upgrade()
        
        def ota_receive_thread(self):
                self.adapter_dev_handle.ota_receive_process()

if __name__ == "__main__":
        main()