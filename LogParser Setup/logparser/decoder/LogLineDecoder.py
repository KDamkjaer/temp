from .BaseLogDecoder import BaseLogDecoder
from .Error import Error
import re
import datetime

class LogLineDecoder(BaseLogDecoder):

    def __init__(self, codes):
        super().__init__(codes)

    def decodeLine(self, line):

        if line[:8] == '********':
            return line

        parseMatch = None
        versionDecode = re.match('(?P<version>.*?) :: (?P<linee>.*)', line)
        if versionDecode:
            if versionDecode.group('version') == '3.5':
                parseMatch = self._decodeLine35(line)
            else:
                parseMatch = self._decodeLine(line)
        return self.__convertMatch(parseMatch)

    def _decodeLine35(self, line):
        return re.match('(?P<version>.*?) :: (?P<tectime>.*) :: (?P<usrtime>.*) :: (?P<source>-?[0-9]+) :: C(?P<code>[0-9]+)A(?P<arg>[0-9]+):(.*?) :: (.*?) :: (?P<lvl>[0-9]+) :: (?P<str1>.*?) :: (?P<str2>.*?) :: (?P<data>.*)', line)

    def _decodeLine(self, line):
        return re.match('(?P<tectime>.*) :: (?P<usrtime>.*) :: (?P<source>-?[0-9]+) :: C(?P<code>[0-9]+)A(?P<arg>[0-9]+):(.*?) :: (?P<lvl>[0-9]+) :: (?P<str1>.*?) :: (?P<str2>.*?) :: (?P<data>.*)', line)

    def __convertMatch(self, match):
        
        if not match:
            return None

        e = Error()
        # e.tectime = match.group('tectime')
        e.timestamp = datetime.datetime.strptime(match.group('usrtime'), '%Y-%m-%d %H:%M:%S.%f')
        e.source = int(match.group('source'))
        e.code = int(match.group('code'))
        e.arg = int(match.group('arg'))
        e.level = int(match.group('lvl'))

        if e.code == 0 and e.arg == 0:
            estr = match.group('str1')
            estr += match.group('str2')
            e.text = estr
            
        else:
            e.data = match.group('data')
            e.datatype = None
            e.text = self.generateMsgString(e)

        return e