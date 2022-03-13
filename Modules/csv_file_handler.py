# https://www.pythontutorial.net/python-basics/python-write-csv-file/

import csv
import threading


class CSV(object):
    def __init__(self, _file_name, _orderTallyLogLock):
        self.__fileName = _file_name
        self.__orderTallyLogLock = _orderTallyLogLock
        self.__file = None
        self.__writer = None

    @property
    def fileName(self):
        return self.__fileName

    @fileName.setter
    def fileName(self, value):
        self.__fileName = value

    @property
    def orderTallyLogLock(self):
        return self.__orderTallyLogLock

    @orderTallyLogLock.setter
    def orderTallyLogLock(self, value):
        self.__orderTallyLogLock = value

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, value):
        self.__file = value

    @property
    def writer(self):
        return self.__writer

    @writer.setter
    def writer(self, value):
        self.__writer = value

    def open(self):
        # open the file in the write mode
        file = open(self.fileName, 'w', encoding='UTF8')
        self.file = file

        # create the csv writer
        self.writer = csv.writer(file)

    #  see https://gist.github.com/rahulrajaram/5934d2b786ed2c29dc418fafaa2830ad for details on locking
    def write(self, row):
        while self.orderTallyLogLock.locked():
            continue

        self.orderTallyLogLock.acquire()
        self.writer.writerow(row)
        self.orderTallyLogLock.release()

    def close(self):
        self.file.close()

