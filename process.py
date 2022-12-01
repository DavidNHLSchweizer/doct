import pandas as pd
from aanvraag_reader import AanvraagDirectory, ExcelConvertor
from doc_creator import TEMPLATE, DocumentCreator


class AanvraagProcessor:
    def __init__(self, directory, aanvraag_excel, output_directory, output_prefix, word_template):
        self.directory = directory
        self.aanvraag_excel = aanvraag_excel
        self.output_directory = output_directory
        self.output_prefix = output_prefix
        self.word_template = word_template
    def process(self):
        print(f'*** START READING DIRECTORY {self.directory} ***')
        AD = AanvraagDirectory(self.directory)
        print(f'*** END READING DIRECTORY ({len(AD.aanvragen)} read) ***')
        EC = ExcelConvertor(AD)        
        EC.write_to_excel(self.aanvraag_excel)
        print(f'*** SUMMARY WRITTEN TO EXCEL {self.aanvraag_excel} ***')
        DocumentCreator(pd.read_excel(self.aanvraag_excel), self.word_template, self.output_directory, self.output_prefix)
        print(f'*** WORD DOCUMENTS CREATED IN {self.output_directory} ***')


AanvraagProcessor(r'C:\repos\doct\test', 'aanvragen.xlsx','beoordelingen', 'Beoordeling', TEMPLATE).process()