from pathlib import Path
from aanvraag_data import AanvraagDatabase
from aanvraag_info import AanvraagDocumentInfo, AanvraagInfo
from mail_merge import MailMerger


class BeoordelingenMailMerger(MailMerger):
    def __init__(self, template_doc, output_directory):
        self.output_directory = Path(output_directory)
        super().__init__(template_doc)
    def __get_output_filename(self, info: AanvraagDocumentInfo):
        return self.output_directory.joinpath(f'Beoordeling aanvraag {info.student} ({info.bedrijf}).docx')
    def __merge_document(self, info: AanvraagDocumentInfo):
        self.process(self.__get_output_filename(info), student=info.student,bedrijf=info.bedrijf,titel=info.titel,datum=info.datum_str, versie=info.versie)
    def merge_documents(self, aanvragen: list[AanvraagInfo]):
        for aanvraag in aanvragen:
            self.__merge_document(aanvraag.docInfo)



if __name__=="__main__":
    ADB = AanvraagDatabase('prullaria.xlsx', False)
    for aanvraag in ADB.data.aanvragen:
        print(aanvraag)
    Merger = BeoordelingenMailMerger(r'.\templates\template 0.7.docx', r'.\tem')
    Merger.merge_documents(ADB.data.aanvragen)
