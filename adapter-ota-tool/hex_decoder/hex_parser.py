import os
import argparse
from typing import List
from intelhex import IntelHex

class HexParser:
        def __init__(self, hex_file_path: str):
                self.raw_data = bytearray()
                self.ih = IntelHex()
                self.ih.loadhex(hex_file_path)
                self.bin_data = self.ih.tobinarray()
                self.bin_bytes = bytes(self.bin_data)
                self.hex_file_total_size = len(self.bin_bytes)
        
        def get_hex_file_total_bytes_size(self) -> int:
                return self.hex_file_total_size
        
        def ger_hex_file_data(self, start_bytes: int, data_size: int) -> list:
                if (start_bytes < 0) or (start_bytes > self.hex_file_total_size):
                        print("Error: invaild hex file size")
                        return False
                        
                return list(self.bin_bytes[start_bytes:(start_bytes + data_size)])
        
        def test(self):
                bin_data = self.ih.tobinarray()
                
                bin_bytes = bytes(bin_data)
                
                print(f"提取到 {len(bin_bytes)} 字节数据")
                print("前16字节:", bin_bytes[:16].hex())
                    