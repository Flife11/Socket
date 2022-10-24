import chunk
import socket
import time

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 60)
        # overrides value shown by sysctl net.ipv4.tcp_keepalive_probes
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 4)
        # overrides value shown by sysctl net.ipv4.tcp_keepalive_intvl
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 15)
url = "anglesharp.azurewebsites.net/Chunked"
class constant:
    def __init__(self, url):
        if (url[len(url)-1]!='/' and len(url.split("/"))==1): url = url + '/'
        path = url.split("/")
        self.link = path[0]
        self.fileName = path[len(path)-1]
        if (self.fileName==""):
            path.pop(0)
        if (self.fileName=="" or self.fileName.find('.')==-1) : 
            self.fileName = "index.html"
        
        self.tag = '/'.join(path)


def _getIP(link):
    return socket.gethostbyname(link)

def _constHeader(link):
    host = "Host: {}\r\n".format(link)
    connection = "Connection: Keep-Alive\r\n"
    return [host, connection]


def _message(const):
    constHeader = _constHeader(const.link)
    MESSAGE = "GET /{} HTTP/1.1\r\n{}\r\n".format(const.tag, "".join(constHeader))
    return MESSAGE

def _connect(const):
    IP = _getIP(const.link)
    PORT = 80

    try:
        print(f"Connecting to {IP}:{PORT}")
        CLIENT.connect((IP, PORT))
        c = CLIENT.getsockname()
        print(f"By IP: {c}")
        print(f"Connect successful!\n")
    except socket.error as e:
        print(f"Socket error: {e}")


def _getContentLength(responde):
    if (responde.find("Content-Length: ")==-1) : return -1
    tmp = responde.split("Content-Length: ")[1].split('\r\n')
    return int(tmp[0])

def _cutChunkedLength(data):
    if (type(data)==type("1")):
        chunkSize = int(data[:data.find("\r\n")], base=16)
        D = data[data.find("\r\n")+2:]
        return (chunkSize + 2, D)
    else: 
        print(data)
        chunkSize = int(data.split(b'\r\n')[0].decode("latin-1"), base=16)
        data = data.split(b'\r\n')[1]
        return (chunkSize + 2, data)
        

#CHUNKED
def _sendRequestWithChunked(fileName, chunkSize, data):
    f = open(fileName, "wb")
    try:
        while (True):        
            chunkSize -= len(data)
            if (chunkSize==0): data = data.rstrip(b'\r\n')
            f.write(data)
            print(chunkSize)
            if (chunkSize==0): 
                print(data)
                data = CLIENT.recv(20)    
                tmp = _cutChunkedLength(data)
                chunkSize = tmp[0]
                data = tmp[1]
                print(data)
                print(f"new chunk: {chunkSize}")
                if chunkSize==2: break
            else:
                data = CLIENT.recv(chunkSize)
    except socket.error as e:
        print(f"Socket error: {e}")
    
    f.close()
    CLIENT.close()

# CONTENT LENGTH
def _sendRequestWithContentLength(fileName, dataLen, data):
    f = open(fileName, "wb")
    try:
        while (True):        
            if not data: break
            f.write(data)
            data = CLIENT.recv(dataLen)
    except socket.error as e:
        print(f"Socket error: {e}")
    
    f.close()
    CLIENT.close()


def Status(responde):
    status = responde.split("\r\n")[0].split(" ")[1]
    if (status=="200"): return 1
    return 0
    

def _sendRequest(const):
    dataLen = 10000
    Message = _message(const)
    CLIENT.send(Message.encode())

    data = CLIENT.recv(dataLen)

    responde = ""
    ContentLength = 0
    D = ""
    chunkSize = 0
    
    if ".html" in const.fileName:
        x = data.decode("latin-1").find("\r\n\r\n")
        responde = data.decode("latin-1")[:x]
        D = data.decode("latin-1")[x+4:]
    else:
        responde = data.decode("latin-1").split("\r\n\r\n")[0]
        D = data.decode("latin-1").split("\r\n\r\n")[1]

    if not Status(responde): 
        print("Request fail")
        print(responde)
        return
        
    #print(data)
    ContentLength = _getContentLength(responde)
    print(responde)
    if (ContentLength==-1) :
        #print(D.encode("latin-1"))
        tmp = _cutChunkedLength(D)
        chunkSize = tmp[0]
        D = tmp[1]
        print(chunkSize)
        _sendRequestWithChunked(const.fileName, chunkSize, D.encode("latin-1"))
    else : _sendRequestWithContentLength(const.fileName, ContentLength, D.encode("latin-1"))

    

def _main():
    const = constant(url)
    print(const.fileName)
    print(const.link)
    print(const.tag)
    #const.fileName = "test.jpg"

    _connect(const)
    _sendRequest(const)

_main()




