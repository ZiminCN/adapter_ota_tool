import sys
import os
from typing import List
import threading as test_thread

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.abspath(current_dir))
sys.path.append(os.path.join(project_root, 'can_tool'))

from can_tool import CanTool

def test_can_receive(can_tool_handle):
        loop_flag = True
        while loop_flag:
                get_message = can_tool_handle.receive_can_data()
                if(get_message == None):
                        print("None message! Break")
                        loop_flag = False
                        break
                else:
                        print("Get Message: ID:[get_message.arbitration_id], Data:[get_message.data]")
                        loop_flag = False
                        break

def test_can_send(can_tool_handle):
        print("Init CanTool.")
        can_tool_handle.send_can_data(False, False, 0x404, [0x12, 0x34, 0x45, 0x56])
        print("Can send.")

if __name__ == "__main__":
        can_tool_handle = CanTool()
        send_thread = test_thread.Thread(target=test_can_send, name='send_thread', args=(can_tool_handle,))
        receive_thread = test_thread.Thread(target=test_can_receive, name='receive_thread', args=(can_tool_handle,))
        
        receive_thread.start()
        send_thread.start()
        