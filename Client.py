import socket

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 60)
        # overrides value shown by sysctl net.ipv4.tcp_keepalive_probes
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 4)
        # overrides value shown by sysctl net.ipv4.tcp_keepalive_intvl
CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 15)
url = "http://web.stanford.edu/class/cs231a/project.html"
class constant:
    def __init__(self, url):
        index = 0
        if (url.find("http://")>=0) :
            index = 1 
        if (url[len(url)-1]!='/' and len(url.split("http://"))==1): url = url + '/'
        path = url.split("http://")[index].split("/")
        self.link = path[0]
        self.fileName = path[len(path)-1]
        if (self.fileName=="") : 
            self.fileName = "index.html"
        path.pop(0)
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


def _sendRequestWithChunked():
    pass

def _sendRequestWithContentLength(fileName, ContentLength, data):
    f = open(fileName, "wb")
    dataLen = 1024*1024

    try:
        while (True):        
            print(ContentLength, len(data))
            f.write(data)
            ContentLength -= len(data)
            if ContentLength==0:
                break
            print(ContentLength, len(data))
            data = CLIENT.recv(dataLen)
    except socket.error as e:
        print(f"Socket error: {e}")
    f.close()
    CLIENT.close()


def _sendRequest(const):
    dataLen = 1024*1024
    Message = _message(const)
    CLIENT.send(Message.encode())
    data = CLIENT.recv(dataLen)
    
    responde = data.decode("latin-1").split("\r\n\r\n")[0]
    ContentLength = _getContentLength(responde)
    D = data.decode("latin-1").split("\r\n\r\n")[1]

    print(responde)

    if (ContentLength==-1) :
        _sendRequestWithChunked()
    else : _sendRequestWithContentLength(const.fileName, ContentLength, D.encode("latin-1"))

    

def _main():
    const = constant(url)
    # print(const.fileName)
    # print(const.link)
    # print(const.tag)
    _connect(const)
    _sendRequest(const)

_main()




