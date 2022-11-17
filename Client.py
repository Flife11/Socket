
import socket
from bs4 import BeautifulSoup
import os
import sys
import concurrent.futures
import threading

# CLIENT.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
# CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 60)
#         # overrides value shown by sysctl net.ipv4.tcp_keepalive_probes
# CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 4)
#         # overrides value shown by sysctl net.ipv4.tcp_keepalive_intvl
# CLIENT.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 15)

class constant:
    def __init__(self, url):
        url = url.split("http://")[1]
        if (url[len(url)-1]!='/' and len(url.split("/"))==1): url = url + '/'
        path = url.split("/")
        self.link = path[0]
        self.fileName = path[len(path)-1]
        if (len(path)>2 and self.fileName==""): self.folder = 1
        else: self.folder = 0
            
        if (self.fileName=="" or self.fileName.find('.')==-1) : 
            self.fileName = "index.html"
        path.pop(0)
        self.folderName = self.link + "_" + path[len(path)-2] 
        self.tag = '/'.join(path)

        self.fileName = self.link + "_" + self.fileName


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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Connecting to {IP}:{PORT}")
        client.connect((IP, PORT))
        c = client.getsockname()
        print(f"By IP: {c}")
        print(f"Connect successful!\n")
    except socket.error as e:
        print(f"Socket error: {e}")
    return client


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
        chunkSize = int(data.split(b'\r\n')[0].decode("latin-1"), base=16)
        data = data.split(b'\r\n')[1]
        return (chunkSize + 2, data)
        

#CHUNKED
def _sendRequestWithChunked(client, fileName, chunkSize, data):
    f = open(fileName, "wb")
    try:
        while (True):        
            chunkSize -= len(data)
            if (chunkSize==0): data = data.rstrip(b'\r\n')
            f.write(data)
            if (chunkSize==0): 
                data = client.recv(20)    
                tmp = _cutChunkedLength(data)
                chunkSize = tmp[0]
                data = tmp[1]
                if chunkSize==2: break
            else:
                data = client.recv(chunkSize)
    except socket.error as e:
        print(f"Socket error: {e}")
    
    f.close()

# CONTENT LENGTH
def _sendRequestWithContentLength(client, fileName, dataLen, data):
    f = open(fileName, "wb")
    print(fileName)
    Length = dataLen
    try:
        while (True):        
            if not data: break
            f.write(data)
            Length -= len(data)
            if (Length==0): break
            data = client.recv(Length)
    except socket.error as e:
        print(f"Socket error: {e}")
    f.close()


def Status(responde):
    status = responde.split("\r\n")[0].split(" ")[1]
    if (status=="200"): return 1
    return 0
    

def _sendRequest(client, const):
    
    dataLen = 10000
    Message = _message(const)
    print(Message)
    client.send(Message.encode())

    data = client.recv(dataLen)

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

    print(responde)
    ContentLength = _getContentLength(responde)
    if (ContentLength==-1) :
        tmp = _cutChunkedLength(D)
        chunkSize = tmp[0]
        D = tmp[1]
        _sendRequestWithChunked(client, const.fileName, chunkSize, D.encode("latin-1"))
    else : _sendRequestWithContentLength(client, const.fileName, ContentLength, D.encode("latin-1"))

    

    
def _downloadAllFiles(client, url, fileName, folderName):
    # Get file name
    f = open(fileName)
    soup = BeautifulSoup(f, 'html.parser')
    links = []
    for a in soup.find_all('a'):
        link = a.get("href")
        if link.find('.')!=-1:
            links.append(link)

    # Make folder
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'{}'.format(folderName))
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    consts = list()
    for link in links:
        fileName = os.path.join(final_directory, link)
        c = constant(url + link)
        c.fileName = fileName
        consts.append(c)

    for const in consts:
        #print(const.fileName)
        _sendRequest(client, const)
    
    
def thread_function(url):
    
    const = constant(url)
    client = _connect(const)
    _sendRequest(client, const)

    if (const.folder==1):
        _downloadAllFiles(client, url, const.fileName, const.folderName)
    client.close()


def _main():
    URLS = sys.argv[1:]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(URLS)) as executor:
        executor.map(thread_function, URLS)



_main()




