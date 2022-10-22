import socket

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
URL = "web.stanford.edu"
fileName = "01-intro.pdf"
# URL = "www.example.com"
# fileName = "index.html"

def _getIP(LINK):
    return socket.gethostbyname(LINK)

def _const(LINK):
    host = "Host: {}\r\n".format(LINK)
    connection = "Connection: Keep-Alive\r\n"
    return [host, connection]


def _message():
    LINK = URL
    TAG = "class/cs224w/slides/01-intro.pdf"
    # TAG = ""
    const = _const(LINK)
    
    MESSAGE = "GET /{} HTTP/1.1\r\n{}\r\n".format(TAG, "".join(const))
    return MESSAGE

def _connect():
    IP = _getIP(URL)
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
    tmp = responde.split("Content-Length: ")[1].split('\r\n')
    return int(tmp[0])

def _sendRequest():
    f = open(fileName, "w", encoding="latin-1")
    dataLen = 1024*1024
    print(dataLen)
    MESSAGE = _message()
    print(MESSAGE)
    CLIENT.send(MESSAGE.encode())
    data = CLIENT.recv(dataLen)

    responde = data.decode("latin-1").split("\r\n\r\n")[0]
    ContentLength = _getContentLength(responde)
    DATA = data.decode("latin-1").split("\r\n\r\n")[1]
    
    try:
        while (True):        
            d = '\n'.join(DATA.split("\r\n"))
            f.write(d)
            ContentLength -= len(DATA)
            print(len(data), len(DATA), len(d), ContentLength)
            if ContentLength==0:
                break
            data = CLIENT.recv(dataLen)
            DATA = data.decode("latin-1")
    except:
        print("ERROR")
    
    f.close()
    CLIENT.close()


def _main():
    _connect()
    _sendRequest()

_main()





