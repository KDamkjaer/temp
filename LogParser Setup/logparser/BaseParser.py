from .DefinitionsManager import DefinitionsDownloader, DefinitionsFileLoader
from .decoder.LogLineDecoder import LogLineDecoder
import logging
from abc import ABC, abstractmethod

class BaseParser(ABC):

    def __init__(self, outPath):
        self.outPath = outPath
        self.logger = logging.getLogger(self.__class__.__name__)
        self.src = ''

    def downloadCodes(self, version = None):
        self.d = DefinitionsDownloader(version)

    def storeCodes(self, path):
        self.d.storeCodes(path)

    def readCodes(self, path):
        self.d = DefinitionsFileLoader(path)

    @abstractmethod
    def readData(self):
        raise NotImplementedError()

    def readFromBuffer(self, buffer):
        while True:
            try:
                line = buffer.readline()
                if not line:
                    break
                yield True, line
            except UnicodeDecodeError as e:
                code_err_str = '### Unable to decode line, UnicodeDecodeError : {0} ###\n'.format(e)
                self.logger.warning(code_err_str)
                yield False, code_err_str


    def parse(self):

        self.logger.info('Parsing "{0}" to "{1}"'.format(self.src, self.outPath))

        with open(self.outPath, 'w', encoding="utf8") as wf:
            for e in self.parseLine():
                wf.write(e.__str__() + '\n')

        self.logger.info('Done Parsing')

    def parseLine(self):
        if self.d.codes == None:
            raise RuntimeError("No errorcodes have been loaded")
        decoder = LogLineDecoder(self.d.codes)

        for (success, line) in self.readData():
            if success:
                e = decoder.decodeLine(line)
                yield e

    @staticmethod
    def setupLogging(debug):
        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s : %(levelname)-8s : %(name)-21s : %(message)s')
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
