import datetime
import pandas as pd
from aanvraag_directory import AanvraagDirectory
from aanvraag_info import AanvraagDocumentInfo, AanvraagInfo
from haslog import HasLog

class DataException(Exception): pass

VOLDOENDE = 'voldoende'
COLMAP = {'timestamp':0, 'student':1, 'studentnr':2, 'voornaam':3, 'telefoonnummer':4, 'email':5, 'datum':6, 'versie':7, 'bedrijf':8, 'titel':9, 'beoordeling':10}
class AanvraagDataXLS(HasLog):   
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
    def __to_sheet_row(self, aanvraag: AanvraagInfo):
        def get_datum_str(datum, versie):
            if datum:
                return f'{datum:%d-%m-%Y}'
            else:
                return versie if versie else ''
        def get_versie_str(datum, versie):
            if datum:
                return versie if versie else ''
            else:
                return ''        
        def get_passed_str(passed: bool):
            if passed:
                return VOLDOENDE
            else:
                return ''
        def get_first_name(student: str):
            if student:
                words = student.split(' ')
                if words:
                    return words[0]
            return ''
        info = aanvraag.docInfo
        return [aanvraag.timestamp, info.student, info.studnr, get_first_name(info.student), info.telno, info.email, get_datum_str(info.datum, info.versie), get_versie_str(info.datum, info.versie), info.bedrijf, info.titel, get_passed_str(aanvraag.passed)]
    def __from_sheet_row(self, row_nr: int)->AanvraagInfo:
        def get_col(heading):
            if value := row[COLMAP[heading]].value:
                return value
            else:
                return ''
        def get_datum_str():
            if versie:= get_col("versie"):
                return f'{get_col("datum")} / {versie}'
            else:
                return f'{get_col("datum")}'
        def get_passed(pass_string):
            return pass_string == VOLDOENDE
        row = self.sheet[row_nr]
        return AanvraagInfo(AanvraagDocumentInfo(datum_str=get_datum_str(), student=get_col('student'), studnr=get_col('studentnr'), 
                                telno=get_col('telefoonnummer'), email=get_col('email'), bedrijf=get_col('bedrijf'), titel=get_col('titel')), 
                                get_col('timestamp'), get_passed(get_col('beoordeling')))
    def number_rows(self):
        return self.sheet.max_row
    def create_aanvraag(self, aanvraag: AanvraagInfo):
        self.sheet.append(self.__to_sheet_row(aanvraag))
        return self.number_rows()
    def read_aanvraag(self, row_nr: int)->AanvraagInfo:
        return self.__from_sheet_row(row_nr)
    def __find_aanvraag_row(self, aanvraag: AanvraagInfo):
        row_nr = self.number_rows()
        while row_nr > 0 and (a:=self.read_aanvraag(row_nr)) != aanvraag:
            row_nr -=1
        return row_nr            
    def update_aanvraag(self, aanvraag: AanvraagInfo, row_nr: int=-1, **kwargs):        
        if row_nr == -1 and (row_nr := self.__find_aanvraag_row(aanvraag)) == 0:
            self.warning(f'aanvraag {aanvraag} not found. Can not be updated. Skipping.')
            return
        aanvraag.modify(**kwargs)
        row = self.sheet[row_nr]
        for col_nr,value in enumerate(self.__to_sheet_row(aanvraag)):
            row[col_nr].value = value
    def close(self):
        self.writer.close()
        self.info(f'Saved data to {self.xls_filename}.')
    def save(self):
        self.close()
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
       
class AanvraagDatabase(HasLog):
    def __init__(self, xls_filename, new_file = False):
        self.xls = AanvraagDataXLS(xls_filename, new_file)
        self.data = AanvraagData()
        self.index = []
        self.__read_xls()
    @property
    def aanvragen(self):
        return self.data.aanvragen
    def filter_aanvragen_timestamp(self, min_date:datetime.datetime = None):
        return list(filter(lambda aanvraag: aanvraag.timestamp >= min_date, self.aanvragen))
    def filter_aanvragen_voldoende(self, is_passed = True):
        return list(filter(lambda aanvraag: (not is_passed) ^ aanvraag.passed, self.aanvragen))
    def nr_aanvragen(self):
        return len(self.aanvragen)
    def add_aanvraag(self, aanvraag: AanvraagInfo, row_nr: int=0):
        self.data.add_aanvraag(aanvraag)
        if row_nr <= 1:
            row_nr = self.xls.create_aanvraag(aanvraag)           
        self.index.append({row_nr: aanvraag})
    def __read_xls(self):
        for row_nr in range(2,self.xls.number_rows()+1): #skip heading, rows are indexed from 1 in ExcelWriter
            self.add_aanvraag(self.xls.read_aanvraag(row_nr), row_nr)
    def is_in_database(self, new_aanvraag: AanvraagDocumentInfo):
        return self.data.contains(new_aanvraag)
    def read_directory(self, directory, min_date:datetime.datetime = None)->int:
        AD = AanvraagDirectory(directory)        
        result = 0
        for aanvraag in sorted(AD.read_files(min_date), key=lambda aanvraag: (aanvraag.timestamp,aanvraag.docInfo.student)):
            if self.is_in_database(aanvraag):
                self.warning(f'Duplicate {aanvraag}; skipping.')
            else:
                self.add_aanvraag(aanvraag)
                result +=1
        self.xls.save()
        return result
    def update_grade(self, aanvraag:AanvraagInfo, passed: bool):
        if not self.is_in_database(aanvraag):
            raise DataException(f'aanvraag {aanvraag} is not in database.')
        self.xls.update_aanvraag(aanvraag, passed=passed)  #note: this also modifies the aanvraag record should be done through keys
    def find_aanvragen(self, studnr: str)->list[AanvraagInfo]:
        result = []
        for aanvraag in self.aanvragen:
            if aanvraag.docInfo.studnr == studnr:
                result.append(aanvraag)
        return result
    def flush(self):
        self.xls.save()

#TODO: check update and delete (low prio)
#TODO: keep sorted on timestamp/student for full spreadsheet

if __name__=="__main__":
    ADB = AanvraagDatabase('koolzaad.xlsx', False)
    # ADB.read_directory(r'C:\repos\doct\jimi')
    # ADB.read_directory(r'C:\repos\doct\test3')
    for aanvraag in ADB.aanvragen:
        print(aanvraag)
    # ADB.read_directory(r'C:\repos\doct\test2')
    # ADB.read_directory(r'C:\repos\doct\jimi')
    # ADB.read_directory(r'C:\repos\doct\test3')
    print('filter ing')    
    for aanvraag in ADB.filter_aanvragen_voldoende():
        print(aanvraag)
    for aanvraag in ADB.filter_aanvragen_voldoende(False):
        print(aanvraag)
    # for aanvraag in ADB.filter_aanvragen_timestamp(datetime.datetime(2022, 12,1)):
    #     print(aanvraag)
    #     ADB.update_grade(aanvraag, True)
    #     ADB.flush()
    #     print(aanvraag)

    # for aanvraat in ADB.find_aanvragen('3480487'):
    #     print(aanvraat)
    #     ADB.update_grade(aanvraat, True)
    #     ADB.flush()
    #     print(aanvraat)

    
