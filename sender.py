__author__ = 'Andrey Alekov'

from modem import Modem
from pdu import PDU

if __name__ == "__main__":
    m = Modem(r"\\.\COM1")
    print(m.getinfo())
    msg = PDU('+79856661111', 'Привет из Python скрипта')
    m.sendsms(msg)
    m.close()