from scapy.all import *
from pop import POPReq
from pop import POPRes

def parse(data):
    hex_data = hex_bytes(data)
#   测试响应报文
    result = POPRes(hex_data)
#   测试请求报文
#   result = POPReq(hex_data)
    result.show(dump = False)

def test_parse_pop():
    parse("2b4f4b20556e697175652d4944206c697374696e6720666f6c6c6f77730d0a3120343537656463313030303030306236340d0a2e0d0a")

test_parse_pop()
