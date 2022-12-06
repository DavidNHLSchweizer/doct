import datetime
import pandas as pd
import pytest
import warnings
from aanvraag_data import AanvraagDocumentInfo, AanvraagInfo
from aanvraag_reader import AanvraagReaderFromPDF

#mock tables
table0=[['Studentgegevens',''],
['Datum/revisie',''],
['Student',''],
['Studentnummer',''],
['Telefoonnummer',''],
['E-mailadres',''],
['Bedrijfsgegevens',''],
['Bedrijfsnaam',''],
['Postadres',''],
['Postcode & plaats',''],
['Bezoekadres',''],
['Postcode & plaats',''],
['Telefoonnummer',''],
['Bedrijfsbegeleider',''],
['Naam',''],
['Functie',''],
['Afdeling',''],
['Telefoonnummer',''],
['E-mailadres',''],
['Overig',''],
['Afstudeerperiode (begindatum – einddatum)',''],
['Hoe heb je deze opdracht gevonden?',''],
]
def _generate_table_0(AI: AanvraagInfo)->pd.DataFrame:
    table = pd.DataFrame(data=table0)
    table.values[1][1]=AI.docInfo.datum
    table.values[2][1]=AI.docInfo.student
    table.values[3][1]=AI.docInfo.studnr
    table.values[4][1]=AI.docInfo.telno
    table.values[5][1]=AI.docInfo.email
    table.values[7][1]=AI.docInfo.bedrijf
    return table
table2=[{'value':'Omschrijving bedrijf'},
{'value':'Omschrijf hier beneden kort en helder de kenmerken van het bedrijf'},
{ 'value': '1. Kerntaken van het bedrijf'},
{ 'value': 'nog een regel1'},
{ 'value': 'nog een regel2'},
{ 'value': '1. Wat heeft de afstudeeropdracht te maken met dit primaire proces?'},
{ 'value': 'nog een regel3'},
{ 'value': 'nog een regel4'},
{ 'value': '3. Begeleiding'},
{ 'value': 'nog een regel5'},
{ 'value': 'nog een regel6'},
{ 'value': 'In te vullen door student'},
{ 'value': '2. (Voorlopige, maar beschrijvende) Titel van de afstudeeropdracht'},
{ 'value': '***TITEL***'},
{ 'value': '3. Wat is de aanleiding voor de opdracht? Waar lijkt het probleem vandaan te komen?'},
{ 'value': 'nog een regel7'},
{ 'value': 'nog een regel8'},
{ 'value': '4. Korte omschrijving van de opdracht:'},
{ 'value': 'nog een regel9'},
{ 'value': 'nog een regel10'},
{ 'value': '' },
{ 'value': 'EINDE'},
]
def _generate_table_2(AI: AanvraagInfo)->pd.DataFrame:
    table = pd.DataFrame.from_records(table2)
    table.values[13][0]=AI.docInfo.titel
    # print(table)
    return table
def generate_tables(AI: AanvraagInfo)->list[pd.DataFrame]:
    tables = [_generate_table_0(AI), pd.DataFrame(), _generate_table_2(AI), pd.DataFrame()]
    return tables
    
class MockTabulaReadPDF:
    def __init__(self, AI: AanvraagInfo):
        self.mock_tables = generate_tables(AI)
    def read_pdf(self, pdf_file, **kwds):
        return self.mock_tables

def test_AanvraagReaderFromPDF_end_to_end(mocker:pytest.MonkeyPatch):
    adi = AanvraagDocumentInfo(datum='1-2-2020', student='Erica Zandschulp', studnr='123456', telno='06-12345678', email='erica.zandschulp@nhlstenden.dom', bedrijf='Daar wil je niet bijhoren!', titel='Doe iets leuks!')       
    timestamp = datetime.datetime.now()
    ai = AanvraagInfo(adi, timestamp=timestamp)
    MTBF = MockTabulaReadPDF(ai)
    mocker.patch('aanvraag_reader.tabula', MTBF)
    mocker.patch('aanvraag_reader.get_file_timestamp', return_value=timestamp)
    AR = AanvraagReaderFromPDF('pdf.pdf')
    assert AR
    assert AR.aanvraag == ai

