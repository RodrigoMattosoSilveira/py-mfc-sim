# https://www.pythontutorial.net/python-basics/python-write-csv-file/

import csv


class CSV(object):
    def __init__(self, _file_name):
        self.__fileName = _file_name
        self.__file = None
        self.__writer = None

    @property
    def fileName(self):
        return self.__fileName

    @fileName.setter
    def fileName(self, value):
        self.__fileName = value

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

    def write(self, row):
        self.writer.writerow(row)

    def close(self):
        self.file.close()

