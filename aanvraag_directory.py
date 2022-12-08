from dataclasses import dataclass
import datetime
from pathlib import Path
from aanvraag_info import AanvraagInfo
from aanvraag_reader import ERRCOMMENT, AanvraagReaderFromPDF

@dataclass
class FileData:
    filename: str = ''
    timestamp: datetime.datetime = None
    
class AanvraagDirectory:
    def __init__(self, directory):
        self.directory = directory
        self.__filedatas = self.__get_filedatas(directory)
    def __get_filedatas(self, directory)->list[FileData]:
        files = []
        for filename in Path(directory).glob('*.pdf'):
            files.append(FileData(filename, datetime.datetime.fromtimestamp(Path(filename).stat().st_mtime)))
        return files
    def read_files(self, min_date:datetime.datetime = None)->list[AanvraagInfo]:            
        def test_date(filedata: FileData):
            return filedata.timestamp >= min_date
        result = []
        for filedata in self.__filedatas:
            print(filedata.filename)
            try:           
                if not min_date or test_date(filedata):
                    result.append(aanvraag:=AanvraagReaderFromPDF(filedata.filename, filedata.timestamp).aanvraag)
                    print(aanvraag)
                else:
                    print(f'skipped: file (timestamp: {filedata.timestamp}) older than {min_date:%d-%m-%Y}.')
            except Exception as E:
                print(f'***ERROR***: Kan bestand {filedata.filename}  niet lezen: {E}\n{ERRCOMMENT}.')
        return sorted(result, key=lambda filedata: filedata.timestamp) 
    
if __name__=='__main__':
    AD = AanvraagDirectory(r'C:\repos\doct\test3')
    for file in AD.read_files(min_date=datetime.datetime(2022,11,29)):
        print(file)
