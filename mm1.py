import pandas as pd
from mailmerge import MailMerge

template = "template 0.6.docx"

# data = pd.read_excel('aanvragen.xlsx')
# print(data)

def nrows(table):
    return table.shape[0]

class DocumentCreator:
    def __init__(self, data: pd.DataFrame, template: str, output_prefix: str):
        for row in range(1,nrows(data)):
            student,bedrijf,titel,datumversie=data.values[row][0],data.values[row][5],data.values[row][6],data.values[row][4]
            document = MailMerge(template)
            document.merge(student=student,bedrijf=bedrijf,titel=titel,datumversie=datumversie)
            output_name = f'{output_prefix} {student}.docx'
            document.write(output_name)
            print(f'{student} written to {output_name}')

DocumentCreator(pd.read_excel('aanvragen.xlsx'), template, r'beoordelingen\Beoordeling')