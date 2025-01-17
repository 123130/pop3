from scapy.packet import *
from scapy.fields import *
from scapy.ansmachine import *
from scapy.layers.inet import *
# import dissector


class POPField(StrField):
    """
    field class for handling pop requests or pop response
    @attention: it inherets StrField from Scapy library
    """
    holds_packets = 1
#     name = "POPField"

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
#         cstream = -1
#         if pkt.underlayer.name == "TCP":
#             cstream = dissector.check_stream(\
#             pkt.underlayer.underlayer.fields["src"],\
#              pkt.underlayer.underlayer.fields["dst"],\
#               pkt.underlayer.fields["sport"],\
#                pkt.underlayer.fields["dport"],\
#                 pkt.underlayer.fields["seq"], s)
#         if not cstream == -1:
#             s = cstream
        remain = ""
        value = ""
        ls = s.splitlines()
        length_ls = len(ls)
        ls01 = []
        for i in range(length_ls):
            str01 = str(ls[i], encoding="utf-8")
            if i == 0 and len(str01) > 3:
                str_list = str01.split('-')
                for j in range(len(str_list)):
                    if str_list[j] == '':
                        continue
                    else:
                        ls01.append(str_list[j])
            else:
                ls01.append(str01)
        myresult = ''
        lslen = len(ls01)
        i = 0
        k = 0
        for line in ls01:
            k = k + 1
            ls2 = line.split()
            length = len(ls2)
            if length > 1 and k == 1:
                value = ls2[0]
                c = 1
                remain = ""
                while c < length:
                    remain = remain + ls2[c] + " "
                    c = c + 1
                if self.name.startswith("request"):
                    myresult = myresult + "Request command: " + value +\
                    ", Request parameter: " + remain
                if self.name.startswith("response"):
                    myresult = myresult + "Response indicator: " + value +\
                    ", Response description: " + remain
            if k > 1:
                remain = str(ls2[0])
                c = 1
                while c < length:
                    remain = remain + " " + str(ls2[c])
                    c = c + 1
                myresult = myresult + remain
            if length == 1 and length_ls == 1:
                myresult = "Request command: " + str(ls2[0])
            i = i + 1
            if i == lslen:
                return "", myresult

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
        super().__init__(name, default, fmt)
        self.name = name
#         StrField.__init__(self, name, default, fmt, remain)


class POPRes(Packet):
    """
    class for handling pop responses
    @attention: it inherets Packet from Scapy library
    """
    name = "pop"
    fields_desc = [POPField("response", "", "H")]


class POPReq(Packet):
    """
    class for handling pop requests
    @attention: it inherets Packet from Scapy library
    """
    name = "pop"
    fields_desc = [POPField("request", "", "H")]


bind_layers(TCP, POPReq, dport=110)
bind_layers(TCP, POPRes, sport=110)
