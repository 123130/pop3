from scapy.layers.dot11 import *
from scapy.layers.ir import *
from scapy.layers.ppp import *
from scapy.layers.gprs import *
from scapy.layers.mobileip import *
from scapy.layers.smb import *
from scapy.layers.bluetooth import *
from scapy.layers.isakmp import *
from scapy.layers.radius import *
from scapy.layers.hsrp import *
from scapy.layers.netbios import *
from scapy.layers.snmp import *
from scapy.layers.dhcp6 import *
from scapy.layers.l2 import *
from scapy.layers.rip import *
from scapy.layers.inet6 import *
from scapy.layers.netflow import *
from scapy.layers.tftp import *
from scapy.layers.dhcp import *
from scapy.layers.l2tp import *
from scapy.layers.rtp import *
from scapy.layers.inet import *
from scapy.layers.ntp import *
from scapy.layers.x509 import *
from scapy.layers.dns import *
from scapy.layers.llmnr import *
from scapy.layers.sebek import *
from scapy.layers.pflog import *
from scapy.layers.dot11 import *
from scapy.layers.mgcp import *
from scapy.layers.skinny import *

import base64
import binascii
from scapy.all import *
from scapy.packet import *
from scapy.fields import *
from scapy.ansmachine import *
from scapy.layers.inet import *
import dissector

sessions = []


def is_created_session(Src, Dst, SPort, DPort):
    """
    method returns true if the ssh session is exist
    @param Src: source ip address
    @param Dst: destination ip address
    @param SPort: source port number
    @param DPort: destination port number
    """
    i = 0
    while i < len(sessions):
        if  Src and Dst and SPort and DPort in sessions[i]:
            return True
        i = i + 1
    return False

def create_session(Src, Dst, SPort, DPort, expected_seq):
    """
    method for creating encypted ssh sessions
    @param Src: source ip address
    @param Dst: destination ip address
    @param SPort: source port number
    @param DPort: destination port number
    """
    if not is_created_session(Src, Dst, SPort, DPort):
        sessions.append([Src, Dst, SPort, DPort, expected_seq])
        
def build_stream(Src, Dst, SPort, DPort, expected_seq):
    i = 0
    while i < len(sessions):
        if  Src and Dst and SPort and DPort in sessions[i]:
            sessions[i][4] = sessions[i][4].append_data(Src, Dst, SPort, DPort, expected_seq)
        i = i + 1

def get_session(Src, Dst, SPort, DPort, obj):
    i = 0
    while i < len(sessions):
        if  Src and Dst and SPort and DPort in sessions[i]:
            if sessions[i][4].seq == obj.seq and obj.push:
                sessions[i][4].append_packet(obj.pkt)
                sessions[i][4].change_seq(obj.seq + len(obj.pkt))
                sessions[i][4].push = obj.push
                s = sessions[i][4].pkt
                del(sessions[i])
                return s
        i = i + 1
    return None

class Stream:
    pkt = ""
    seq = -1
    push = None
    def __init__(self, pkt, push, seq):
        self.pkt = self.pkt + pkt
        self.push = push
        self.seq = seq
        if not push:
            self.pkt = self.pkt + pkt
            
    def append_data(self, Src, Dst, SPort, DPort, obj):
        if self.seq == obj.seq and obj.push:
            self.append_packet(obj.pkt)
            self.change_seq(obj.seq + len(obj.pkt))
            self.push = obj.push
            ###### here
            
            pk = IP(src=Src, dst=Dst)/TCP(sport=SPort, dport=DPort)/self.pkt
            AAAAAAAAAAAAAAAA = dissector.Dissector()
            
            None

        elif self.seq == obj.seq:
            self.append_packet(obj.pkt)
            self.change_seq(obj.seq + len(obj.pkt))
            self.push = obj.push
        return self

    def append_packet(self, pkt):
        self.pkt = self.pkt + pkt
    
    def change_seq(self, seq):
        self.seq = seq

    
def int2bin(n, count=16):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

class HTTPReqField(StrField):
    """
    field class for handling http requests
    @attention: it inherets StrField from Scapy library
    """
    holds_packets = 1
    name = "HTTPReqField"

    def getfield(self, pkt, s):
        """
        this method will get the packet, takes what does need to be
        taken and let the remaining go, so it returns two values.
        first value which belongs to this field and the second is
        the remaining which does need to be dissected with
        other "field classes".
        @param pkt: holds the whole packet
        @param s: holds only the remaining data which is not dissected yet.
        """
        flags = None
        seq = pkt.underlayer.fields["seq"]
        push = False
        flags_bits = list(int2bin(pkt.underlayer.fields["flags"]))
        if flags_bits[11] == '1':
            flags = 'A'
        if flags_bits[12] == '1':
            flags = flags + 'P'
        if 'P' in flags:
            push = True
        else:
            push = False
            
        if not is_created_session(pkt.underlayer.underlayer.fields["src"],
                                    pkt.underlayer.underlayer.fields["dst"],
                                    pkt.underlayer.fields["sport"],
                                    pkt.underlayer.fields["dport"]) and not push:
            seqn = pkt.underlayer.fields["seq"] + len(s)
            stream = Stream(s, push, seqn)
            create_session(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"], stream)
        
        elif  is_created_session(pkt.underlayer.underlayer.fields["src"],
                                    pkt.underlayer.underlayer.fields["dst"],
                                    pkt.underlayer.fields["sport"],
                                    pkt.underlayer.fields["dport"]):
            seqn = pkt.underlayer.fields["seq"] + len(s)
            stream = Stream(s, push, seqn)
            build_stream(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"], stream)

        remain = ""
        value = ""
        if self.name == "request-line: ":
            ls = s.splitlines(True)
            f = ls[0].split()
            length = len(f)
            if length == 3:
                value = "Method:" + f[0] + ", Request-URI:" +\
        				f[1] + ", HTTP-Version:" + f[2]
                ls.remove(ls[0])
                for element in ls:
                    remain = remain + element
                return remain, value
            return s, ""


class HTTPResField(StrField):
    """
    field class for handling http requests
    @attention: it inherets StrField from Scapy library
    """
    holds_packets = 1
    name = "HTTPResField"
    fin = False
    def get_code_msg(self, cn):
        """
        method returns the message for the http code number
        @param cn: code number
    """
        codes = {
  "100": "Continue",
  "101": "Switching Protocols",
  "102": "Processing",
  "199": "Informational - Others",
  "200": "OK",
  "201": "Created",
  "202": "Accepted",
  "203": "Non-Authoritative Information",
  "204": "No Content",
  "205": "Reset Content",
  "206": "Partial Content",
  "207": "Multi-Status",
  "299": "Success - Others",
  "300": "Multiple Choices",
  "301": "Moved Permanently",
  "302": "Moved Temporarily",
  "303": "See Other",
  "304": "Not Modified",
  "305": "Use Proxy",
  "306": "(Unused)",
  "307": "Temporary Redirect",
  "399": "Redirection - Others",
  "400": "Bad Request",
  "401": "Unauthorized",
  "402": "Payment Required",
  "403": "Forbidden",
  "404": "Not Found",
  "405": "Method Not Allowed",
  "406": "Not Acceptable",
  "407": "Proxy Authentication Required",
  "408": "Request Time-out",
  "409": "Conflict",
  "410": "Gone",
  "411": "Length Required",
  "412": "Precondition Failed",
  "413": "Request Entity Too Large",
  "414": "Request-URI Too Large",
  "415": "Unsupported Media Type",
  "416": "Requested Range Not Satisfiable",
  "417": "Expectation Failed",
  "422": "Unprocessable Entity",
  "423": "Locked",
  "424": "Failed Dependency",
  "499": "Client Error - Others",
  "500": "Internal Server Error",
  "501": "Not Implemented",
  "502": "Bad Gateway",
  "503": "Service Unavailable",
  "504": "Gateway Time-out",
  "505": "HTTP Version not supported",
  "599": "Server Error - Others"}

        if cn in codes:
            return codes[cn]
        return ""

    def getfield(self, pkt, s):
        """
        this method will get the packet, takes what does need to be
        taken and let the remaining go, so it returns two values.
        first value which belongs to this field and the second is
        the remaining which does need to be dissected with
        other "field classes".
        @param pkt: holds the whole packet
        @param s: holds only the remaining data which is not dissected yet.
        """
        flags = None
        seq = pkt.underlayer.fields["seq"]
        push = False
        
        flags_bits = list(int2bin(pkt.underlayer.fields["flags"]))
        if flags_bits[11] == '1':
            flags = 'A'
        if flags_bits[12] == '1':
            flags = flags + 'P'
        if 'P' in flags:
            push = True
        else:
            push = False
            
        if not is_created_session(pkt.underlayer.underlayer.fields["src"],
                                    pkt.underlayer.underlayer.fields["dst"],
                                    pkt.underlayer.fields["sport"],
                                    pkt.underlayer.fields["dport"]) and not push:
            seqn = pkt.underlayer.fields["seq"] + len(s)
            stream = Stream(s, push, seqn)
            create_session(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"], stream)
        
        elif  is_created_session(pkt.underlayer.underlayer.fields["src"],
                                    pkt.underlayer.underlayer.fields["dst"],
                                    pkt.underlayer.fields["sport"],
                                    pkt.underlayer.fields["dport"]) and not push:
            seqn = pkt.underlayer.fields["seq"]
            stream = Stream(s, push, seqn)
            build_stream(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"], stream)
        
        elif  is_created_session(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"]) and push:
            if not self.fin:
                seqn = pkt.underlayer.fields["seq"]
                stream = Stream(s, push, seqn)
                s = get_session(pkt.underlayer.underlayer.fields["src"], pkt.underlayer.underlayer.fields["dst"], pkt.underlayer.fields["sport"], pkt.underlayer.fields["dport"], stream)
                #print s
                self.fin = True
        remain = ""
        value = ""
        if self.name == "status-line: " and s.startswith("HTTP/"):
            ls = s.splitlines(True)
            f = ls[0].split()
            length = len(f)
            if length == 3:
                value = "HTTP-Version:" + f[0] + ", Status-Code:" +\
        				f[1] + ", Reason-Phrase:" + f[2]
                ls.remove(ls[0])
                for element in ls:
                    remain = remain + element
                return remain, value
        return s, ""


#class HTTPMsgField(XByteField):
class HTTPMsgField(XByteField):
    """
    field class for handling http body
    @attention: it inherets XByteField from Scapy library
    """
    holds_packets = 1
    name = "HTTPMsgField"
    myresult = ""

    def __init__(self, name, default):
        """
        class constructor, for initializing instance variables
        @param name: name of the field
        @param default: Scapy has many formats to represent the data
        internal, human and machine. anyways you may sit this param to None.
        """
        self.name = name
        self.fmt = "!B"
        Field.__init__(self, name, default, "!B")


    def getfield(self, pkt, s):
        """
        this method will get the packet, takes what does need to be
        taken and let the remaining go, so it returns two values.
        first value which belongs to this field and the second is
        the remaining which does need to be dissected with
        other "field classes".
        @param pkt: holds the whole packet
        @param s: holds only the remaining data which is not dissected yet.
        """
        if s.startswith("\r\n"):
            s = s.lstrip("\r\n")
            if s == "":
                return "", ""
        self.myresult = ""
        firstb = struct.unpack(self.fmt, s[0])[0]
        self.myresult = ""
        for c in s:
            ustruct = struct.unpack(self.fmt, c)
            # byte = base64.standard_b64encode(str(ustruct[0]))
            
            byte = str(hex(ustruct[0]))[2:]
            if len(byte) == 1:
                byte = "0" + byte
            
            self.myresult = self.myresult + c
        if self.myresult[-1:] == " ":
            self.myresult = self.myresult.rstrip()
        return "",  self.myresult


class HTTPField(StrField):
    """
    field class for handling http fields
    @attention: it inherets StrField from Scapy library
    """
    holds_packets = 1
    name = "HTTPField"

    def getfield(self, pkt, s):
        """
        this method will get the packet, takes what does need to be
        taken and let the remaining go, so it returns two values.
        first value which belongs to this field and the second is
        the remaining which does need to be dissected with
        other "field classes".
        @param pkt: holds the whole packet
        @param s: holds only the remaining data which is not dissected yet.
        """
        if self.name == "bridge":
            return s, ""
        if self.name == "unknown-header(s): ":
            remain = ""
            value = []
            ls = s.splitlines(True)
            i = -1
            for element in ls:
                i = i + 1
                if element == "\r\n":
                    return s, []
                elif element != "\r\n"\
                 and (": " in element[:10])\
                  and (element[-2:] == "\r\n"):
                    value.append(element)
                    ls.remove(ls[i])
                    remain = ""
                    unknown = True
                    for element in ls:
                        if element != "\r\n" and (": " in element[:15])\
                         and (element[-2:] == "\r\n") and unknown:
                            value.append(element)
                        else:
                            unknown = False
                            remain = remain + element
                    return remain, value
            return s, []

        remain = ""
        value = ""
        ls = s.splitlines(True)
        i = -1
        for element in ls:
            i = i + 1
            if element.upper().startswith(self.name.upper()):
                value = element
                value = value.strip(self.name)
                ls.remove(ls[i])
                remain = ""
                for element in ls:
                    remain = remain + element
                return remain, value
        return s, ""

    def __init__(self, name, default, fmt, remain=0):
        """
        class constructor for initializing the instance variables
        @param name: name of the field
        @param default: Scapy has many formats to represent the data
        internal, human and machine. anyways you may sit this param to None.
        @param fmt: specifying the format, this has been set to "H"
        @param remain: this parameter specifies the size of the remaining
        data so make it 0 to handle all of the data.
        """
        self.name = name
        StrField.__init__(self, name, default, fmt, remain)


class HTTPRequest(Packet):
    """
    class for handling http requests
    @attention: it inherets Packet from Scapy library
    """
    name = "http"
    fields_desc = [HTTPReqField("request-line: ", "", "H"),
                    HTTPField("cache-control: ", "", "H"),
                    HTTPField("connection: ", "", "H"),
                     HTTPField("date: ", "", "H"),
                    HTTPField("pragma: ", "", "H"),
                     HTTPField("trailer: ", "", "H"),
                    HTTPField("transfer-encoding: ", "", "H"),
                     HTTPField("upgrade: ", "", "H"),
                    HTTPField("via: ", "", "H"),
                     HTTPField("Warning: ", "", "H"),
                    HTTPField("accept: ", "", "H"),
                     HTTPField("accept-encoding: ", "", "H"),
                    HTTPField("accept-language: ", "", "H"),
                     HTTPField("accept-charset: ", "", "H"),
                    HTTPField("expect: ", "", "H"),
                     HTTPField("authorization: ", "", "H"),
                    HTTPField("accept-encoding: ", "", "H"),
                     HTTPField("from: ", "", "H"),
                    HTTPField("host: ", "", "H"),
                     HTTPField("if-match: ", "", "H"),
                    HTTPField("if-modified-since: ", "", "H"),
                     HTTPField("iIf-none-match: ", "", "H"),
                    HTTPField("if-range: ", "", "H"),
                     HTTPField("if-unmodified-since: ", "", "H"),
                    HTTPField("max-forwards: ", "", "H"),
                     HTTPField("proxy-authorization: ", "", "H"),
                    HTTPField("range: ", "", "H"),
                     HTTPField("referer: ", "", "H"),
                    HTTPField("te: ", "", "H"),
                     HTTPField("user-agent: ", "", "H"),
                    HTTPField("link: ", "", "H"),
                     HTTPField("mime-version: ", "", "H"),
                    HTTPField("title: ", "", "H"),
                     HTTPField("uri: ", "", "H"),
                    HTTPField("cookie: ", "", "H"),
                     HTTPField("set-cookie: ", "", "H"),
                    HTTPField("x-forwarded-for: ", "", "H"),
                     HTTPField("keep-alive: ", "", "H"),
                    HTTPField("unknown-header(s): ", "", "H"),
                     HTTPMsgField("message-body: ", "")]


class HTTPResponse(Packet):
    """
    class for handling http responses
    @attention: it inherets Packet from Scapy library
    """
    name = "http"
    fields_desc = [HTTPResField("status-line: ", "", "H"),
                    HTTPField("cache-control: ", "", "H"),
                    HTTPField("connection: ", "", "H"),
                     HTTPField("date: ", "", "H"),
                    HTTPField("pragma: ", "", "H"),
                     HTTPField("trailer: ", "", "H"),
                    HTTPField("transfer-encoding: ", "", "H"),
                     HTTPField("upgrade: ", "", "H"),
                    HTTPField("via: ", "", "H"),
                     HTTPField("warning: ", "", "H"),
                    HTTPField("accept-ranges: ", "", "H"),
                     HTTPField("age: ", "", "H"),
                    HTTPField("etag: ", "", "H"),
                     HTTPField("location: ", "", "H"),
                    HTTPField("proxy-authenticate: ", "", "H"),
                     HTTPField("retry-after: ", "", "H"),
                    HTTPField("server: ", "", "H"),
                     HTTPField("vary: ", "", "H"),
                    HTTPField("allow: ", "", "H"),
                     HTTPField("content-encoding: ", "", "H"),
                    HTTPField("content-language: ", "", "H"),
                     HTTPField("content-length: ", "", "H"),
                    HTTPField("content-location: ", "", "H"),
                     HTTPField("content-md5: ", "", "H"),
                    HTTPField("content-range: ", "", "H"),
                     HTTPField("content-type: ", "", "H"),
                    HTTPField("expires: ", "", "H"),
                     HTTPField("last-modified: ", "", "H"),
                    HTTPField("extension-header: ", "", "H"),
                     HTTPField("link: ", "", "H"),
                    HTTPField("mime-version: ", "", "H"),
                     HTTPField("retry-after: ", "", "H"),
                    HTTPField("title: ", "", "H"),
                     HTTPField("uri: ", "", "H"),
                    HTTPField("public: ", "", "H"),
                     HTTPField("accept-patch: ", "", "H"),
                    HTTPField("cookie: ", "", "H"),
                     HTTPField("set-cookie: ", "", "H"),
                    HTTPField("x-forwarded-for: ", "", "H"),
                     HTTPField("keep-alive: ", "", "H"),
                    HTTPField("unknown-header(s): ", "", "H"),
                     HTTPMsgField("message-body: ", "")]


bind_layers(TCP, HTTPResponse, sport=80)
bind_layers(TCP, HTTPRequest, dport=80)

"""
pkts = rdpcap("/root/Desktop/http.cap")
for pkt in pkts:
    pkt.show()
"""