

def FileReader(FilePath, Offset = "0", Length="-1", SearchPattern="", isBinary = False):
	"""
	fs = FileStream(FilePath)
	full_length = (int)fs.Length
	if not SearchPattern:
		if Length == -1 and Offset == 0:
			data = System.Array[full_length]
			fs.Read(data, 0, full_length)
		elif Length == -1:
			data = System.Array[full_length - Offset]
			fs.Read(data, Offset, full_length - Offset)
		else:
			data = System.Array[Length - Offset]
			fs.Read(data, Offset, Length - Offset)
	
	"""
	Offset = int(Offset)
	Length = int(Length)
	SearchPattern = None if SearchPattern == "" else SearchPattern
	print "[*] Path: {} Offset: {} Length: {} SearchPattern:{}".format(FilePath, Offset, Length, SearchPattern)
	with open(FilePath,'rb') as f:
		if Offset == 0 and Length == -1:
			return f.read()
		if Length != -1:
			f.seek(Offset, 0)
			return f.read(Length)
		else:
			f.seek(Offset, 0)
			return f.read()


print FileReader("FILEPATH","OFFSET", "LENGTH", "SEARCHPATTERN")
