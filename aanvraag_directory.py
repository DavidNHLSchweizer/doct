import datetime
from pathlib import Path
from aanvraag_info import AanvraagInfo
from aanvraag_reader import ERRCOMMENT, AanvraagReaderFromPDF

class AanvraagDirectory:
    def __init__(self, directory):
        self.directory = directory
        self.__filenames = self.__get_filenames(directory)
    def __get_filenames(self, directory):
        files = []
        for file in Path(directory).glob('*.pdf'):
            files.append(file)
        return files
    def read_files(self, min_date:datetime.datetime = None)->list[AanvraagInfo]:            
        def test_date(file):
            return datetime.datetime.fromtimestamp(Path(file).stat().st_mtime) >= min_date
        result = []
        for file in self.__filenames:
            print(file, datetime.datetime.fromtimestamp(Path(file).stat().st_mtime))
            try:           
                if not min_date or test_date(file):
                    result.append(aanvraag:=AanvraagReaderFromPDF(file).aanvraag)
                    print(aanvraag)
                else:
                    print(f'skipped: older than {min_date:%d-%m-%Y}')
            except Exception as E:
                print(f'***ERROR***: Kan bestand {file}  niet lezen: {E}\n{ERRCOMMENT}.')
        return result
    
if __name__=='__main__':
    AD = AanvraagDirectory(r'C:\repos\doct\test3')
    for file in AD.read_files(min_date=datetime.datetime(2022,11,29)):
        print(file)
