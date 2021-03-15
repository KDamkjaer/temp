import logging
import re
from PrimaryInterfaceClient import Types
DataType = Types.DataType
from enum import IntEnum

class RobotMode(IntEnum):
    DISCONNECTED   = 0
    CONFIRM_SAFETY = 1
    BOOTING        = 2
    POWER_OFF      = 3
    POWER_ON       = 4
    IDLE           = 5
    BACKDRIVE      = 6
    RUNNING        = 7
    UPDATING       = 8
    POWERING_OFF   = 9

def updateMsgStringFloat(m, reportText, datatype, data):
    formatString = '{0:5.2f}'
    if m.group('format'):
        formatString = '{0:' + m.group('format').replace('_', '.') + 'f}'

    return reportText.replace(m.group('all'), formatString.format(data))

def updateMsgStringInt(m, reportText, datatype, data):
    return reportText.replace(m.group('all'), '{0}'.format(data))

def updateMsgStringHex(m, reportText, datatype, data):
    return reportText.replace(m.group('all'), '0x{0:08X}'.format(data))

def updateMsgStringData(m, reportText, datatype, data):
    if datatype in (DataType.INT32, DataType.UINT32):
        return updateMsgStringInt(m, reportText, datatype, data)
    elif datatype == DataType.HEX:
        return updateMsgStringHex(m, reportText, datatype, data)
    elif datatype == DataType.FLOAT:
        return updateMsgStringFloat(m, reportText, datatype, data)
    elif datatype == DataType.STRING:
        return reportText.replace(m.group('all'), data)
    else:
        return reportText.replace(m.group('all'), 'No Data')

class BaseLogDecoder(object):
    def __init__(self, codes):
        self.codes = codes
        self.logger = logging.getLogger(self.__class__.__name__)

        self.converters = {
            'float'    : updateMsgStringFloat,
            'signed'   : updateMsgStringInt,
            'unsigned' : updateMsgStringInt,
            'hex'      : updateMsgStringHex,
            'string'   : updateMsgStringData,
            'data'     : updateMsgStringData,
        }

    def generateMsgString(self, e):
        '''
        Generates error text from code, arg and data
        '''
        code = str(e.code)
        arg = str(e.arg)

        reportText = ''

        try:
            codeText = self.codes[code]['text']
        except KeyError:
            codeText = None

        try:
            argText = self.codes[code]['args'][arg]['text']
        except KeyError:
            argText = None

        if argText and codeText:
            reportText = codeText + ' : ' + argText
        elif codeText:
            reportText = codeText
        elif argText:
            reportText = argText
        else:
            reportText = 'Undefined'

        # Handle polyscope logging weirdness (might be better to just define the value of the args)
        if e.code == 100:
            reportText += f': {RobotMode(e.arg).name}'

        m = re.match('.*(?P<all>{(?P<type>[a-zA-Z]*)(_(?P<format>.*))?}).*', reportText)
        if m:
            if e.datatype == None:
                self.updateMsgNoData(m, e)
                # print(f'{e.datatype}, {e.data}')
            return self.converters[m.group('type')](m, reportText, e.datatype, e.data)
        else:
            return reportText

    def updateMsgNoData(self, m, e):
        '''
        Tries to determine the datatype if no one was provided
        '''
        e.datatype = 0
        if m.group('type') == 'float':
            e.data = float(e.data)
            e.datatype = DataType.FLOAT
        elif m.group('type') == 'signed':
            e.data = int(e.data)
            e.datatype = DataType.INT32
        elif m.group('type') == 'unsigned':
            e.data = int(e.data)
            e.datatype = DataType.UINT32
        elif m.group('type') == 'hex':
            e.data = int(e.data, base=16)
            e.datatype = DataType.HEX
        elif m.group('type') == 'data':
            try:
                tmp = int(e.data)
                e.datatype = DataType.STRING
                # e.datatype = 1
            except ValueError:
                try:
                    tmp = int(e.data, 16)
                    # e.datatype = 4
                    e.datatype = DataType.STRING
                except ValueError:
                    try:
                        e.data = float(e.data)
                        e.datatype = DataType.FLOAT
                    except ValueError:
                        e.datatype = DataType.STRING