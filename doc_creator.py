from pathlib import Path
import pandas as pd
from mailmerge import MailMerge

TEMPLATE = "template 0.6.docx"
def nrows(table):
    return table.shape[0]

class DocumentCreator:
    def __init__(self, data: pd.DataFrame, template: str, output_directory, output_prefix: str):
        for row in range(0,nrows(data)):
            student,bedrijf,titel,datum,versie=data.values[row][0],data.values[row][6],data.values[row][7],data.values[row][4],data.values[row][5]
            if isinstance(versie,float):
                versie = ''
            document = MailMerge(template)
            document.merge(student=student,bedrijf=bedrijf,titel=titel,datum=str(datum), versie=versie)
            output_name = Path(output_directory).joinpath(f'{output_prefix} {student}.docx')            
            document.write(output_name)
            print(f'{student} written to {output_name}')

if __name__=='__main__':
    p = pd.read_excel('aanvragen.xlsx')
    DocumentCreator(p, TEMPLATE, 'beoordelingen', 'test' )