import datetime
import logging
from pathlib import Path
import pandas as pd
from aanvraag_data import AanvraagDatabase
from beoordelingen import BeoordelingOordeelReader, BeoordelingenMailMerger, is_voldoende
from haslog import HasLog

class AanvraagProcessor(HasLog):
    def __init__(self, database_xls: str):
        exists = Path(database_xls).is_file()
        self.database = AanvraagDatabase(database_xls, not exists)
        if not exists:
            self.info(f'Created {database_xls}.')
        else:
            self.info(f'Opened {database_xls}. {self.database.nr_aanvragen()} aanvragen loaded.')

    def read_new_files(self, directory: str, min_date: datetime.datetime = None)->int:
        result = self.database.read_directory(directory, min_date)
        self.info(f'{result} files read from {directory}.')
        return result    
    def create_beoordelings_formulieren(self, template, output_directory, min_date: datetime.datetime = None):
        result = BeoordelingenMailMerger(template, output_directory).merge_documents(self.database.filter_aanvragen_timestamp(min_date))
        self.info(f'{result} formulieren created in {output_directory}.')
        return result
        

# class OldAanvraagProcessor:
#     def __init__(self, directory, aanvraag_excel, output_directory, output_prefix, word_template):
#         self.directory = directory
#         self.aanvraag_excel = aanvraag_excel
#         self.output_directory = output_directory
#         self.output_prefix = output_prefix
#         self.word_template = word_template
#     def process(self):
#         print(f'*** START READING DIRECTORY {self.directory} ***')
#         AD = AanvraagDirectory(self.directory)
#         print(f'*** END READING DIRECTORY ({len(AD.aanvragen)} read) ***')
#         EC = ExcelConvertor(AD)        
#         EC.write_to_excel(self.aanvraag_excel)
#         print(f'*** SUMMARY WRITTEN TO EXCEL {self.aanvraag_excel} ***')
#         DocumentCreator(pd.read_excel(self.aanvraag_excel), self.word_template, self.output_directory, self.output_prefix)
#         print(f'*** WORD DOCUMENTS CREATED IN {self.output_directory} ***')

if __name__ == "__main__":
    zumzum = r'.\zmzmzm'
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cutoff = datetime.datetime(2022, 11, 1)
    processor = AanvraagProcessor('lijnzaad.xlsx')
    print('=== reading new files ===')
    processor.read_new_files(r'C:\repos\doct\test2', cutoff)
    processor.read_new_files(r'C:\repos\doct\jimi', cutoff)
    print('=== creating forms ===')
    processor.create_beoordelings_formulieren(r'.\templates\template 0.7.docx', zumzum, cutoff)
    for file in Path(zumzum).glob('*.docx'):
        pad = file.resolve()
        print(pad)
        reader = BeoordelingOordeelReader(pad)
        oordeel = reader.read_beoordeling()
        print(f'oordeel: {oordeel}')
        print(f'is voldoende: {is_voldoende(oordeel)}')
    