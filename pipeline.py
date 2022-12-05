import os
from pathlib import Path

def path_with_suffix(filename, suffix):
    path = Path(filename)
    return path.parent.joinpath(f'{path.stem}{suffix}')

class FileProcessor:
    def __init__(self, input_directory, input_filename, data = None):
        self.input_directory = Path(input_directory)
        self.input_filename = Path(input_filename).name
        self.data = data
    def process(self):
        pass

class PipeLine:
    def __init__(self, input_directory):
        self.input_directory = Path(input_directory)
        self._file_processors: list[FileProcessor] = []
    @property
    def file_processors(self):
        return self._file_processors
    def add_processor(self, processor: FileProcessor):
        self.file_processors.append(processor)
    def process(self, p1=0, p2=None): 
        for p, fp in enumerate(self.file_processors):
            if p >= p1 and (not p2 or p <= p2):
                fp.process()

class MockProcessor(FileProcessor):
    def process(self):
        print(f'processing ...{self.input_filename}')

PL = PipeLine(os.getcwd())
PL.add_processor(MockProcessor(PL.input_directory,'first.txt'))
PL.add_processor(MockProcessor(PL.input_directory,'second.txt'))
PL.add_processor(MockProcessor(PL.input_directory,'third.txt'))

PL.process(1,1)

# class FileProcessor:
#     def __init__(self, input_directory, output_directory, input_filename, output_extension):
#         self.input_directory = Path(input_directory)
#         self.output_directory = Path(output_directory)
#         self.input_filename = Path(input_filename).name
#         self.output_filename = path_with_suffix(output_directory.joinpath(self.input_filename), output_extension)




