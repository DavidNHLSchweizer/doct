from __future__ import annotations
from dataclasses import dataclass
import datetime
from pathlib import Path
import re
import time
import pandas as pd
from date_parser import DateParser


def is_valid_email(email: str)->bool:
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.compile(email_regex).match(email) is not None

@dataclass
class AanvraagDocumentInfo:
    datum: str = ''
    student: str = ''
    studnr: str = ''
    telno: str = ''
    email: str = ''
    bedrijf: str = ''
    titel: str = ''
    def __str__(self):
        return f'{self.student}({self.studnr}) - {self.datum}: {self.bedrijf} - "{self.titel}"'
    def __eq__(self, value: AanvraagDocumentInfo):
        if  self.datum != value.datum:
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

COLMAP = {'timestamp':0, 'student':1, 'studentnr':2, 'telefoonnummer':3, 'email':4, 'datum':5, 'versie':6, 'bedrijf':7, 'titel':8, 'beoordeling':9}
class AanvraagData:   
    def __init__(self, xls_filename, new_file = False):
        self.xls_filename = xls_filename
        self._aanvragen:list[AanvraagInfo] = []
        self.__init_xls(xls_filename, new_file)
        print(len(self.aanvragen))
    @property
    def aanvragen(self):
        return self._aanvragen
    def __init_xls(self, xls_filename, new_file):
        if new_file:
            pd.DataFrame(columns=COLMAP.keys()).to_excel(xls_filename, index=False)
        else:
            self.read_aanvragen()
    def add_aanvraag(self, aanvraag: AanvraagInfo, allow_duplicates = False):
        if allow_duplicates or not self.is_duplicate(aanvraag):
            self.aanvragen.append(aanvraag)
    def __read_aanvraag(self, row)->AanvraagInfo:
        def get_col(heading):
            return row[COLMAP[heading]].value
        return AanvraagInfo(AanvraagDocumentInfo(datum=get_col('datum'), student=get_col('student'), studnr=get_col('studentnr'), 
                                telno=get_col('telefoonnummer'), email=get_col('email'), bedrijf=get_col('bedrijf'), titel=get_col('titel')), 
                                get_col('timestamp'))
                                # datetime.datetime.strptime(get_col('timestamp'),  '%a %b %d %H:%M:%S %Y'))
    def is_duplicate(self, new_aanvraag: AanvraagInfo):
        for aanvraag in self.aanvragen:
            if aanvraag == new_aanvraag:
                print('duplo')
                return True
        return False
    def read_aanvragen(self, skip=True):
        with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
            sheet = writer.sheets['Sheet1']
            for i, row in enumerate(sheet): 
                if i == 0: # skip headings
                    continue
                self.add_aanvraag(self.__read_aanvraag(row))
    def __write_aanvraag(self, sheet, aanvraag: AanvraagInfo):
        info = aanvraag.docInfo
        tem_date,tem_versie = DateParser().parse_date(info.datum)
        if tem_date:
            datum = datetime.date.strftime(tem_date, '%d-%m-%Y')
            if tem_versie.find('/') >= 0:
                versie = tem_versie.split('/')[1].strip()
            else:
                versie = tem_versie
        else:           
            datum = info.datum
            versie = ''
        row = [aanvraag.timestamp, info.student, info.studnr, info.telno, info.email, datum, versie, info.bedrijf, info.titel, '']
        sheet.append(row)
    def sort(self, reverse = False):
        self.aanvragen.sort(key=lambda aanvraag: (aanvraag.timestamp, aanvraag.docInfo.student), reverse=reverse)        
    def save(self):
        self.sort()
        with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
            sheet = writer.sheets['Sheet1']
            for aanvraag in self.aanvragen:
                self.__write_aanvraag(sheet, aanvraag)

