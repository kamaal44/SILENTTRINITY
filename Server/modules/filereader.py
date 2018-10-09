class STModule:
    def __init__(self):
        self.name = 'filereader'
        self.description = 'Downloads files from remote systems'
        self.author = '@skelsec'
        self.options = {
            'FilePath': {
                'Description'   :   'The Path to the file',
                'Required'      :   True,
                'Value'         :   ""
            },
            'Offset': {
                'Description'   :   'Optional Offset to start read from',
                'Required'      :   False,
                'Value'         :   "0"
            },
            'Length': {
                'Description'   :   'Optional Length of data to download starting from offset',
                'Required'      :   False,
                'Value'         :   "-1"
            },
            'SearchPattern': {
                'Description'   :   'Optional Pattern to search for, search starting at offset',
                'Required'      :   False,
                'Value'         :   ""
            },
        }

    def payload(self):
        with open('modules/src/filereader.py', 'r') as module_src:
            src = module_src.read()
            src = src.replace("FILEPATH", self.options['FilePath']['Value'])
            src = src.replace("OFFSET", self.options['Offset']['Value'])
            src = src.replace("LENGTH", self.options['Length']['Value'])
            src = src.replace("SEARCHPATTERN", self.options['SearchPattern']['Value'])
            return src.encode()
