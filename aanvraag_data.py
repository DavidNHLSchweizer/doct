from dataclasses import dataclass
import datetime
import time
import pandas as pd


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

class AanvraagInfo:
    def __init__(self, docInfo: AanvraagDocumentInfo, timestamp = datetime.datetime.now()):
        self.docInfo = docInfo
        self.timestamp = timestamp
    def __str__(self):
        return f'{str(self.docInfo)} [{self.timestamp}]'

class AanvraagData:
    def __init__(self, xls_filename):
        self.xls_filename = xls_filename
        self.__init_xls(xls_filename)
        self._aanvragen:list[AanvraagInfo] = []
    def __init_xls(self, xls_filename):
        columns = ['timestamp', 'student', 'studentnr', 'telefoonnummer', 'email', 'datum/versie', 'bedrijf', 'titel', 'beoordeling']
        pd.DataFrame(columns=columns).to_excel(xls_filename, index=False)
    def add_aanvraag(self, aanvraag: AanvraagInfo, save_now = False):
        self.aanvragen.append(aanvraag)
        if save_now:
            self._write_aanvraag(aanvraag)
    def _write_aanvraag(self, aanvraag: AanvraagInfo):
        with pd.ExcelWriter(self.xls_filename, engine='openpyxl', mode='a') as writer:
            sheet = writer.sheets['Sheet1']
            info = aanvraag.docInfo
            row = [time.ctime(aanvraag.timestamp), info.student, info.studnr, info.telno, info.email, info.datum, info.bedrijf, info.titel, '']
            sheet.append(row)
            
    @property
    def aanvragen(self):
        return self._aanvragen


