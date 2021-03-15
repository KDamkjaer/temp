from .BaseLogDecoder import BaseLogDecoder
from .Error import Error, DataType
from struct import unpack
from datetime import datetime

class LogDataDecoder(BaseLogDecoder):

    def __init__(self, codes):
        super().__init__(codes)

    def decodeRawError(self, timestamp, source, messageType, payload):
        e = Error()

        e.code, e.arg, e.level, e.datatype = unpack('!4I', payload[:16])
        if timestamp:
            e.timestamp = timestamp
        else:
            e.timestamp = datetime.now()
        e.source = source

        e.data = None
        if e.datatype:
            e.datatype = DataType(e.datatype)

        if e.datatype == DataType.UINT32 or e.datatype == DataType.HEX:
            e.data = unpack('!I', payload[16:20])[0]
        elif e.datatype == DataType.INT32:
            e.data = unpack('!i', payload[16:20])[0]
        elif e.datatype == DataType.FLOAT:
            e.data = unpack('!f', payload[16:20])[0]


        if e.code == 0 and e.arg == 0:
            e.text = payload[20:]
        else:
            e.text = self.generateMsgString(e)

        # print(f'code {e.code}, arg: {e.arg}, arg: {e.arg}, arg: {e.arg}')

        return e