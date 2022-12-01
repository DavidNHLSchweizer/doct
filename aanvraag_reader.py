import re
from attr import dataclass
from pathlib import Path
import pandas as pd
import tabula

ERRCOMMENT = 'Waarschijnlijk niet een aanvraagformulier'
class PDFReaderException(Exception): pass

@dataclass
class AanvraagInfo:
    datum: str = ''
    student: str = ''
    studnr: str = ''
    telno: str = ''
    email: str = ''
    bedrijf: str = ''
    titel: str = ''
    def __str__(self):
        return f'{self.student}({self.studnr}) - {self.datum}: {self.bedrijf} - "{self.titel}"'

def nrows(table: pd.DataFrame)->int:
    return table.shape[0]

class AanvraagReaderFromPDF:
    def __init__(self, pdf_file: str):
        self.aanvraag = AanvraagInfo()
        self.read_pdf(pdf_file)
    def read_pdf(self, pdf_file: str):
        tables = tabula.read_pdf(pdf_file,pages='all')
        self._parse_main_data(tables[0])
        self._parse_title(tables[2])
    def __convert_fields(self, fields_dict, translation_table):
        for field in translation_table:            
            setattr(self.aanvraag, translation_table[field], fields_dict.get(field, 'NOT FOUND'))
    def __parse_table(self, table: pd.DataFrame, start_row, end_row, translation_table):
        table_dict = {}
        if start_row >= nrows(table) or end_row >= nrows(table):
            raise PDFReaderException(f'Fout in parse_table ({start_row}, {end_row}): de tabel heeft {nrows(table)} rijen.\n{ERRCOMMENT}.')
        for row in range(start_row, end_row):
            table_dict[table.values[row][0]] = table.values[row][1]
        self.__convert_fields(table_dict, translation_table)
    def __rectify_table(self, table, row0, row1):
        #necessary because some students somehow introduce \r characters in the table first column
        for row in range(row0, row1):
            if isinstance(table.values[row][0], str): #sometimes there is an empty cell that is parsed by tabula as a float NAN
                table.values[row][0] = table.values[row][0].replace('\r', '')
    def _parse_main_data(self, table: pd.DataFrame):        
        student_dict_fields = {'Datum/revisie': 'datum', 'Student': 'student', 'Studentnummer': 'studnr', 'Telefoonnummer': 'telno', 'E-mailadres': 'email', 'Bedrijfsnaam': 'bedrijf'}
        student_dict_len  = len(student_dict_fields) + 5 # een beetje langer ivm bedrijfsnaam
        self.__rectify_table(table, 0, student_dict_len)
        self.__parse_table(table, 0, student_dict_len, student_dict_fields)        
    def _parse_title(self, table: pd.DataFrame)->str:
        #regex because some students somehow lose the '.' characters or renumber the paragraphs
        start_paragraph  = '\d.*\(Voorlopige, maar beschrijvende\) Titel van de afstudeeropdracht'
        end_paragraph = '\d.*Wat is de aanleiding voor de opdracht\?'         
        self.aanvraag.titel = ' '.join(self.__get_strings_from_table(table, start_paragraph, end_paragraph))
    def __get_strings_from_table(self, table:pd.DataFrame, start_paragraph_regex:str, end_paragraph_regex:str)->list[str]:
        def row_matches(table, row, pattern:re.Pattern):
            if isinstance(table.values[row][0], str):
                return pattern.match(table.values[row][0]) is not None
            else:
                return False
        result = []
        row = 0
        start_pattern = re.compile(start_paragraph_regex)
        while row < nrows(table) and not row_matches(table, row, start_pattern):
            row+=1
        row+=1
        end_pattern = re.compile(end_paragraph_regex)
        while row < nrows(table) and not row_matches(table, row, end_pattern):
            result.append(table.values[row][0])
            row+=1
        return result

class AanvraagDirectory:
    def __init__(self, directory):
        self.directory = directory
        self.aanvragen: list[AanvraagInfo] = []
        self.__read_files(directory)
        self.__sort_files()
    def __read_files(self, directory):
        for file in Path(directory).glob('*.pdf'):
            print(file)
            try:           
                self.aanvragen.append(aanvraag:=AanvraagReaderFromPDF(file).aanvraag)
                print(aanvraag)
            except Exception as E:
                print(f'***ERROR***: Kan bestand {file}  niet lezen: {E}\n{ERRCOMMENT}.')
    def __sort_files(self):
        self.aanvragen.sort(key=lambda aanvraag: (aanvraag.student, aanvraag.datum))
    
class ExcelConvertor:
    def __init__(self, AD: AanvraagDirectory):
        self.AD:AanvraagDirectory = AD
        self.table = self.__init_table()
    def write_to_excel(self, filename):
        self.table.to_excel(filename, index=False)
    def __init_table(self):
        columns = ['student', 'studentnr', 'telefoonnummer', 'email', 'datum/versie', 'bedrijf', 'titel']
        data = []
        for aanvraag in self.AD.aanvragen:
            data.append([aanvraag.student, aanvraag.studnr, aanvraag.telno, aanvraag.email, aanvraag.datum, aanvraag.bedrijf, aanvraag.titel])
        return pd.DataFrame(data=data, columns=columns)

if __name__=='__main__':
    AD = AanvraagDirectory(r'C:\repos\doct\data')
    EC = ExcelConvertor(AD)
    EC.write_to_excel('aanvragen.xlsx')
    # for aanvraag in AD.aanvragen:
    #     print(aanvraag)