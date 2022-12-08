from __future__ import annotations
import datetime
import re
from date_parser import DateParser


def is_valid_email(email: str)->bool:
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.compile(email_regex).match(email) is not None

class AanvraagDocumentInfo:
    def __init__(self, datum_str='', student='', studnr='', telno='', email='', bedrijf='', titel=''):        
        self._dateparser = DateParser()
        self.datum_str = datum_str
        self.student = student
        self.studnr = studnr
        self.telno = telno
        self.email = email
        self.bedrijf = bedrijf
        self.titel = titel
    def __str__(self):
        return f'{self.student}({self.studnr}) - {self.datum_str}: {self.bedrijf} - "{self.titel}"'
    def __eq__(self, value: AanvraagDocumentInfo):
        self_date,_ = self._dateparser.parse_date(self.datum_str)
        value_date,_= self._dateparser.parse_date(self.datum_str)
        if self_date  != value_date:
            return False
        if  self.datum != value.datum:
            return False
        if  self.versie != value.versie:
            return False
        if  self.student != value.student:
            return False
        if  self.studnr != value.studnr:
            return False
        if  self.telno != value.telno:
            return False
        if  self.email != value.email:
            return False
        if  self.bedrijf != value.bedrijf:
            return False
        if  self.titel != value.titel:
            return False
        return True
    def valid(self):
        return self.student != '' and self.studnr != '' and is_valid_email(self.email) and self.bedrijf != ''
    @property
    def datum(self): 
        return self.__datum
    @property
    def versie(self):
        return self.__versie
    @property 
    def datum_str(self):
        return self.__datum_str
    @datum_str.setter
    def datum_str(self, value):
        self.__datum_str = value
        self.__parse_datum()
    def __parse_datum(self):
        self.__datum,self.__versie = self._dateparser.parse_date(self.datum_str)
        if self.__versie and self.__versie.find('/') >= 0:
            self.__versie = self.__versie.replace('/','').strip()

class AanvraagInfo:
    def __init__(self, docInfo: AanvraagDocumentInfo, timestamp = datetime.datetime.now()):
        self.docInfo = docInfo
        self.timestamp = timestamp
    def __str__(self):
        return f'{str(self.docInfo)} [{self.timestamp}]'
    def __eq__(self, value: AanvraagInfo)->bool:
        if self.timestamp != value.timestamp:
            return False
        if not (self.docInfo == value.docInfo):
            return False
        return True      
    def valid(self):
        return self.docInfo.valid() and isinstance(self.timestamp, datetime.datetime)

