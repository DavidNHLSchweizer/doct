import win32com.client as win32

class WordReader:
    def __init__(self, doc_path):
        self.word= win32.Dispatch('word.application')
        self.word.visible = 0
        self.doc_path = doc_path
        print(doc_path)
        self.document = self.__open_document(str(doc_path))
    def __open_document(self, doc_path):
        self.word.Documents.Open(doc_path, ReadOnly=-1)
        return self.word.ActiveDocument
    def __del__(self):
        if self.document:
            self.document.Close()
            