import datetime

import pandas as pd
from aanvraag_directory import AanvraagDirectory
from aanvraag_info import AanvraagDocumentInfo, AanvraagInfo
from date_parser import DateParser

COLMAP = {'timestamp':0, 'student':1, 'studentnr':2, 'telefoonnummer':3, 'email':4, 'datum':5, 'versie':6, 'bedrijf':7, 'titel':8, 'beoordeling':9}
class AanvraagDataXLS:   
    def __init__(self, xls_filename, new_file = False):
        self.xls_filename = xls_filename
        self.writer:pd.ExcelWriter = self.open_xls(new_file)
    def open_xls(self, new_file = False):
        writer:pd.ExcelWriter = self.__init_xls(self.xls_filename, new_file)
        if writer:
            self.sheet = writer.sheets['Sheet1']
        else:
            self.sheet = None
        return writer
    def __init_xls(self, xls_filename, new_file):
        if new_file:
            pd.DataFrame(columns=COLMAP.keys()).to_excel(xls_filename, index=False)
        return pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a')   
    def __as_sheet_row(self, aanvraag: AanvraagInfo):
        info = aanvraag.docInfo
        return [aanvraag.timestamp, info.student, info.studnr, info.telno, info.email, info.datum, info.versie, info.bedrijf, info.titel, '']
    def number_rows(self):
        return self.sheet.max_row
    def create_aanvraag(self, aanvraag: AanvraagInfo):
        self.sheet.append(self.__as_sheet_row(aanvraag))
    def read_aanvraag(self, row_nr: int)->AanvraagInfo:
        def get_col(heading):
            return row[COLMAP[heading]].value
        def get_datum_str():
            return f'{get_col("datum")} / {get_col("versie")}'
        row = self.sheet[row_nr]
        return AanvraagInfo(AanvraagDocumentInfo(datum_str=get_datum_str(), student=get_col('student'), studnr=get_col('studentnr'), 
                                telno=get_col('telefoonnummer'), email=get_col('email'), bedrijf=get_col('bedrijf'), titel=get_col('titel')), 
                                get_col('timestamp'))
                                # datetime.datetime.strptime(get_col('timestamp'),  '%a %b %d %H:%M:%S %Y'))
    def update_aanvraag(self, aanvraag: AanvraagInfo, row_nr: int):
        new_row = self.__as_sheet_row(aanvraag)
        for col_nr,value in enumerate(new_row):
            self.sheet.cells[row_nr][col_nr] = value
    def save(self):
        self.writer.close()
        self.writer = self.open_xls(False)

class AanvraagData:   
    def __init__(self):
        self._aanvragen:list[AanvraagInfo] = []
    @property
    def aanvragen(self):
        return self._aanvragen
    def add_aanvraag(self, aanvraag: AanvraagInfo):
        if not self.is_duplicate(aanvraag):
            self.aanvragen.append(aanvraag)
    def is_duplicate(self, new_aanvraag: AanvraagInfo):
        for aanvraag in self.aanvragen:
            return aanvraag.timestamp == new_aanvraag.timestamp and \
               aanvraag.docInfo.studnr == new_aanvraag.docInfo.studnr and \
               aanvraag.docInfo.datum == new_aanvraag.docInfo.datum and \
               aanvraag.docInfo.versie == new_aanvraag.docInfo.versie
    def contains(self, new_aanvraag: AanvraagInfo):
        for aanvraag in self.aanvragen: 
            if aanvraag == new_aanvraag:
                return True
        return False

class AanvraagDatabase:
    def __init__(self, xls_filename, new_file = False):
        self.xls = AanvraagDataXLS(xls_filename, new_file)
        self.data = AanvraagData()
        self.__read_xls()
    def __read_xls(self):
        for row_nr in range(1,self.xls.number_rows()):
            self.data.add_aanvraag(self.xls.read_aanvraag(row_nr))
    def is_in_database(self, new_aanvraag: AanvraagDocumentInfo):
        return self.data.contains(new_aanvraag)
    def read_directory(self, directory, min_date = None):
        AD = AanvraagDirectory(directory)        
        for aanvraag in sorted(AD.read_files(min_date), key=lambda aanvraag: (aanvraag.timestamp,aanvraag.docInfo.student)):
            if self.is_in_database(aanvraag):
                print(f'***WARNING***: Duplicate {aanvraag}; skipping')
            else:
                self.data.add_aanvraag(aanvraag)
                self.xls.create_aanvraag(aanvraag)            
        self.xls.save()


#TODO: check update and delete (low prio)
ADB = AanvraagDatabase('aria.xlsx', True)
for aanvraag in ADB.data.aanvragen:
    print(aanvraag)
ADB.read_directory(r'C:\repos\doct\test2')
ADB.read_directory(r'C:\repos\doct\jimi')
ADB.read_directory(r'C:\repos\doct\test3')
for aanvraag in ADB.data.aanvragen:
    print(aanvraag)




    # def __write_aanvraag(self, sheet, aanvraag: AanvraagInfo):
    #     info = aanvraag.docInfo
    #     row = [aanvraag.timestamp, info.student, info.studnr, info.telno, info.email, info.datum, info.versie, info.bedrijf, info.titel, '']
    #     sheet.append(row)
    # def save(self):
    #     self.sort()
    #     with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
    #         sheet = writer.sheets['Sheet1']
    #         for aanvraag in self.aanvragen:
    #             self.__write_aanvraag(sheet, aanvraag)

    # def __init_xls(self, xls_filename, new_file):
    #     if new_file:
    #         pd.DataFrame(columns=COLMAP.keys()).to_excel(xls_filename, index=False)
    #     else:
    #         self.read_aanvragen()
    # def add_aanvraag(self, aanvraag: AanvraagInfo, allow_duplicates = False):
    #     if allow_duplicates or not self.is_duplicate(aanvraag):
    #         self.aanvragen.append(aanvraag)
    # def __read_aanvraag(self, row)->AanvraagInfo:
    #     def get_col(heading):
    #         return row[COLMAP[heading]].value
    #     return AanvraagInfo(AanvraagDocumentInfo(datum=get_col('datum'), student=get_col('student'), studnr=get_col('studentnr'), 
    #                             telno=get_col('telefoonnummer'), email=get_col('email'), bedrijf=get_col('bedrijf'), titel=get_col('titel')), 
    #                             get_col('timestamp'))
    #                             # datetime.datetime.strptime(get_col('timestamp'),  '%a %b %d %H:%M:%S %Y'))
    # def is_duplicate(self, new_aanvraag: AanvraagInfo):
    #     for aanvraag in self.aanvragen:
    #         if aanvraag == new_aanvraag:
    #             print('duplo')
    #             return True
    #     return False
    # def read_aanvragen(self, skip=True):
    #     with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
    #         sheet = writer.sheets['Sheet1']
    #         for i, row in enumerate(sheet): 
    #             if i == 0: # skip headings
    #                 continue
    #             self.add_aanvraag(self.__read_aanvraag(row))

    # def __write_aanvraag(self, sheet, aanvraag: AanvraagInfo):
    #     info = aanvraag.docInfo
    #     row = [aanvraag.timestamp, info.student, info.studnr, info.telno, info.email, info.datum, info.versie, info.bedrijf, info.titel, '']
    #     sheet.append(row)
    # def save(self):
    #     self.sort()
    #     with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
    #         sheet = writer.sheets['Sheet1']
    #         for aanvraag in self.aanvragen:
    #             self.__write_aanvraag(sheet, aanvraag)

