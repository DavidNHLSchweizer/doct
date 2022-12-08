import datetime
import logging
from pathlib import Path
import pandas as pd
from aanvraag_data import AanvraagDatabase
from beoordelingen import BeoordelingOordeelReader, BeoordelingenMailMerger, is_voldoende
from haslog import HasLog
from word_reader import WordReader

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
    def transfer_beoordelingen(self, oordeel_directory:str):
        for file in Path(oordeel_directory).glob('*.docx'):
            if file.name.find('~$')==0: #temp file picked up in glob
                continue
            reader = BeoordelingOordeelReader(str(file.resolve()))
            student, oordeel = reader.read_data()
            if is_voldoende(oordeel):
                self.database.update_grade_for_student(student, True)
                w = WordReader(str(file.resolve()))
                w.save_as_pdf()
                w.close()
        self.database.flush()

if __name__ == "__main__":
    zumzum = r'.\zmzmzm'
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cutoff = datetime.datetime(2022, 11, 1)
    processor = AanvraagProcessor('koolzaad.xlsx')
    # print('=== reading new files ===')
    # processor.read_new_files(r'C:\repos\doct\test2', cutoff)
    # processor.read_new_files(r'C:\repos\doct\jimi', cutoff)
    # print('=== creating forms ===')
    # processor.create_beoordelings_formulieren(r'.\templates\template 0.7.docx', zumzum, cutoff)
    print('=== transferring grades from forms ===')
    processor.transfer_beoordelingen(zumzum)
    