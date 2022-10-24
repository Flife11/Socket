a = b"400\r\n\xd7\xf5\xfas\x9b\xed\\<98\xbaI\xd9i'"
c = b"\xf5\xfas\x9b\xed\\<98\xbaI\xd9i'"

def _cutChunkedLength(data):
    if (type(data)==type("1")):
        chunkSize = int(data[:data.find("\r\n")], base=16)
        D = data[data.find("\r\n")+2:]
        return (chunkSize + 2, D)
    else: 
        chunkSize = int(data.split(b'\r\n')[0].decode("latin-1"), base=16)
        data = data.split(b'\r\n')[1]
        print(data)
        return (chunkSize + 1, data)

d = _cutChunkedLength(a)
print(d)