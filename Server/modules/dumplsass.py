class STModule:
    def __init__(self):
        self.name = 'dumplsass'
        self.description = 'Creates a minidump of the lsass.exe process. For... umm.. reasons'
        self.author = '@skelsec'
        self.options = {}

    def payload(self):
        with open('modules/src/dumplsass.py', 'r') as module_src:
            src = module_src.read()
            return src.encode()
