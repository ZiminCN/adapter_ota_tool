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
                        epilog='Usage: python3 adapter_ota.py -b adapter_board -f firmware.hex'
                )
                
                parser.add_argument(
                        '-f', '--file',           # 短参数和长参数
                        required=True,            # 必须提供
                        help='Hex file path'      # 帮助信息
                )
                
                parser.add_argument(
                        '-b', '--board',          # 板子类型
                        choices=['adapter_board', 'box_board'],
                        required=True,           # 默认
                        help='target board type: 1) adapter_board 2) box_board'  # 帮助信息
                )
                
                input_arg = parser.parse_args()
                
                if not os.path.exists(input_arg.file):
                        print(f"Error: file not exists.")
                        return
                
                print(f"hex file path: {input_arg.file}")
                        
                self.adapter_dev_handle = AdapterDevInfo(input_arg.file, input_arg.board)
                
                send_thread = thread.Thread(target=self.ota_send_thread, name='send_thread')
                receive_thread = thread.Thread(target=self.ota_receive_thread, name='receive_thread')
                timeout_thread = thread.Thread(target=self.ota_timeout_thread, name='timeout_thread')

                receive_thread.start()
                send_thread.start()
                timeout_thread.start()
        
        def ota_send_thread(self):
                self.adapter_dev_handle.ota_send_process()
        
        def ota_receive_thread(self):
                self.adapter_dev_handle.ota_receive_process()
                
        def ota_timeout_thread(self):
                self.adapter_dev_handle.timeout_process()

if __name__ == "__main__":
        main()