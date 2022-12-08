import logging
from mailmerge import MailMerge

class MailMerger:
    def __init__(self, template_doc: str):
        self.template_doc = template_doc
    def process(self, output_file_name: str, **kwds):
        try:
            document = MailMerge(self.template_doc)
            document.merge(**kwds)
            document.write(output_file_name)
        except Exception as E:
            logging.error(f'Error merging document (template:{self.template_doc}) to {output_file_name}: {E}')

