__author__ = 'Andrey Alekov'
import logging
import serial

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
LF = serial.to_bytes([10])
CR = serial.to_bytes([13])
CRTLZ = serial.to_bytes([26])
CRLF = serial.to_bytes([13, 10])


class Modem(object):
    """
    Modem class.
    """
    __port = None

    def __init__(self, port=r"\\.\COM0"):
        """
        Initialize modem
        :param port: Int number of serial port
        :return: None
        """
        self.__port = serial.Serial(port, 115200, timeout=10)
        logger.debug("Port {desc}".format(desc=self.__port))
        self.execute('ATZ')     # reset modem state
        # Modem is active?
        if self.execute('AT+CPAS')[1] != b'+CPAS: 0':
            raise Exception("Modem is not active!")
        if not self.execute('AT+CIMI'):
            raise Exception("Modem without SIM card!")
        if self.execute('AT+CREG?')[1] not in [b'+CREG: 0,1', b'+CREG: 0,5']:
            raise Exception("No registration in home or non-home network!")

    def close(self):
        """
        Close Serial Port
        :return:
        """
        self.__port.close()

    def execute(self, command):
        """
        Execute AT command
        :return: list of output or False when error.
        """
        self.__port.write(command.encode('latin1'))
        self.__port.write(CRLF)
        self.__port.flush()
        result = []
        while True:
            line = self.__port.readline()
            if line != b'\r\n':
                result.append(line[:-2])    # remove \r\n symbols
            if line in [b'OK\r\n', b'ERROR\r\n']:
                break
        logger.info("{cmd} \t>>\t {ret}".format(cmd=command, ret=result[-1].decode('ascii')))
        if result[-1] == b'ERROR':
            return False
        else:
            return result

    def getinfo(self):
        """
        Get information about modem
        :return: dictionary {company, model, firmware, imei}
        """
        info = dict()
        info.update({'company': self.execute('AT+CGMI')[1].decode('ascii')})
        info.update({'model': self.execute('AT+CGMM')[1].decode('ascii')})
        info.update({'firmware': self.execute('AT+CGMR')[1].decode('ascii')})
        info.update({'imei': self.execute('AT+CGSN')[1].decode('ascii')})
        return info

    def sendsms(self, pdu):
        """
        Send SMS using PDU format
        """
        self.execute('AT+CMGF=0')
        self.__port.write(('AT+CMGS=%s' % pdu.len()).encode('latin1'))
        self.__port.write(CR)
        self.__port.write(pdu.tostring().encode('latin1'))
        self.__port.write(CRTLZ)
        while True:
            line = self.__port.readline()
            if line != b'\r\n':
                logger.debug(line[:-2])    # remove \r\n symbols
            if line in [b'OK\r\n', b'ERROR\r\n']:
                break
        if line == b'OK\r\n':
            return True
        else:
            False