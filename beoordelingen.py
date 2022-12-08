from pathlib import Path
from aanvraag_data import AanvraagDatabase
from aanvraag_info import AanvraagDocumentInfo, AanvraagInfo
from mail_merge import MailMerger
from word_reader import WordReader


class BeoordelingenMailMerger(MailMerger):
    def __init__(self, template_doc, output_directory):
        self.output_directory = Path(output_directory)
        super().__init__(template_doc)
    def __get_output_filename(self, info: AanvraagDocumentInfo):
        return self.output_directory.joinpath(f'Beoordeling aanvraag {info.student} ({info.bedrijf}).docx')
    def __merge_document(self, info: AanvraagDocumentInfo):
        self.process(self.__get_output_filename(info), student=info.student,bedrijf=info.bedrijf,titel=info.titel,datum=info.datum_str, versie=info.versie)
    def merge_documents(self, aanvragen: list[AanvraagInfo])->int:
        result = 0
        if len(aanvragen) > 0 and not self.output_directory.is_dir():
            self.output_directory.mkdir()
        for aanvraag in aanvragen:
            self.__merge_document(aanvraag.docInfo)
            result += 1
        return result

VOLDOENDE = 'voldoende'
def is_voldoende(beoordeling: str)->bool:
    print(f'[{beoordeling}]')
    return beoordeling.lower() == VOLDOENDE

class BeoordelingOordeelReader(WordReader):
    def read_beoordeling(self)->str:
        if (result := self.__find_table()):
            try:
                cell_text = result.Cell(Row=5,Column=2).Range.Text
                # returned cell_text for some reason ends with both an 0x0d and a 0x07
                return cell_text[:-2]
            except Exception as E:
                print(E)
                return ''
        return ''
    def __find_table(self):
        if self.document.Tables.Count > 0:
            return self.document.Tables(1)
        else:
            return None
  
if __name__=="__main__":
    ADB = AanvraagDatabase('maanzaad.xlsx', False)
    for aanvraag in ADB.data.aanvragen:
        print(aanvraag)
    Merger = BeoordelingenMailMerger(r'.\templates\template 0.7.docx', r'.\zaadmaan')
    Merger.merge_documents(ADB.data.aanvragen)
