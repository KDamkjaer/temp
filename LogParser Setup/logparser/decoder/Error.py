from PrimaryInterfaceClient.Messages import Types 
class Error:
    def __init__(self):
        self.timestamp = None
        self.source = ''
        self.code = 0
        self.arg = 0
        self.level = 0
        self.datatype = 0
        self.data = None
        self.text = ''
    
    def __str__(self):
        return '{0} : {2} : C{3:03d}A{4:03d} : {1:6s} : {5}'.format(self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], Types.SOURCES(self.source).name, Types.LEVELS(self.level).name, self.code, self.arg, self.text)