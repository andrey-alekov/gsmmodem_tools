__author__ = 'Andrey Alekov'


class PDU(object):
    """
    Simple PDU format with hardcoded params.
    """
    def __init__(self, destination, text, smsc=None):
        if smsc is not None:
            self.sca = PDU.encode_sca(smsc)
        else:
            self.sca = "00"                     # use SIM card SMSC
        self.pdu_type = "01"                    # pdu type / outgoing message
        self.tp_mr = "00"                       # tp_message_reference
        self.da = PDU.encode_dest(destination)
        self.pid = "00"                         # protocol identifier
        self.dcs = "08"                         # data coding schema UCS2
        self.vp = "0"                           # validity period on SMSC
        self.ud = PDU.encode_text(text)        # user data
        self.udl = ('%0.2X' % (len(self.ud)/2))  # user data length in bytes
        self.pdu = self.pdu_type + self.tp_mr + self.da + self.pid + self.dcs + self.udl + self.ud
        self.pdu_len = int(len(self.pdu) / 2)
        self.pdu = self.sca + self.pdu

    def encode_number(number):
        number = number.replace('+', '')
        number += 'F'
        res = ""
        for i in range(0, len(number), 2):
            if (i+1) < len(number):
                res = res + number[i+1]
            res = res + number[i]
        return res

    def encode_sca(number):
        res = PDU.encode_number(number)
        size = int(len(res)/2 + 1)
        return ('%0.2X' % size) + '91' + res

    def encode_dest(number):
        res = PDU.encode_number(number)
        size = len(res) - 1
        return ('%0.2X' % size) + '91' + res

    def encode_text(text):
        res = ""
        for s in text:
            res += (str(hex(ord(s))[2:].zfill(4)).upper())
        return res

    def tostring(self):
        return self.pdu

    def len(self):
        return self.pdu_len