import argparse
import threading
import sys
import textwrap
import socket
import signal
import subprocess
import shlex
#import ssl



# 全局变量
event = threading.Event()

#封装一个超时后跳过进程的函数
def Kskip(timeout):
    def wraps(func):
        def handler(signum, frame): #handler必须写signum，frame参数
            print('[*] 已超时，对方无应答')
            sys.exit()
        def mainSignal(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            print('[*] 开始计时')
            signal.alarm(timeout)
            try:
                result = func(*args, **kwargs)
            finally:
                print('[*] 执行完毕') #函数执行完毕
                signal.alarm(0)
            return result
        return mainSignal
    return wraps


#如果输入有误，重新执行while循环
def Check(i):
    if not i:
        print('[*] 输入有误，请重新输入！')
        return 'continue' #如果有return，则输入有误，没return则输入正确


# 定义了实例的属性，与函数主体并行
class KyCat:
    def __init__(self, args, buffer=None):
        self.args = args
        #self.buffer = buffer
        #if self.args.https:
            #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #My_SSLcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            #My_SSLcontext.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
            #context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            #context.load_verify_locations('/home/SSL/9368040_ky9oss.top.pem')
            #hostname = 'ky9oss.top'
            #self.socket = My_SSLcontext.wrap_socket(sock=sock,server_hostname=hostname, do_handshake_on_connect=True)
            #print('注意，已使用HTTPS')
        #else:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 多次调用同一socket发数据时，若两次调用间隔时间太短，并且前一次调用的应答时间太长，会造成端口被占用的假象，使用下面这行代码会告诉内核重用处于等待状态的socket，无需等待应答。  
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 启动程序
    def Kstart(self):
        try:
            if self.args.listen:
                self.Klisten()
            else:
                self.Ksend()
        except (KeyboardInterrupt, BrokenPipeError):
            print('[*] 已关闭，再见！')
            sys.exit()

    # 监听程序
    def Klisten(self):

        #查看子线程的信号是否为true
        #def CheckLive():
                #if not event.is_set():
                    #sys.exit()

        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5) #可以允许多个进程绑定同一端口！
        print(f'[*] listening on {self.args.target}:{self.args.port}')
        while True: #循环监听，一个断开后监听下一个
            #t = threading.Timer(4.0, CheckLive)
            #t.start()
            client, address = self.socket.accept() #accept()意味着接受connect(),为client返回一个已接受连接的socket对象
            print(f'[*] Receive message from {address[0]}:{address[1]}')

            new_thread = threading.Thread(target=self.Klistening, args=(address,client)) #target是新线程将使用的函数，args是新线程使用的函数的参数。client无法直接传入args里，但加个逗号就可以了。
            new_thread.start()
            #while True:
            #    if not event.is_set():
            #        sys.exit()



    #新的线程，在监听时，同时处理其他数据
    def Klistening(self, address, client):

        event.set() #信号为true

        #接收shell
        if self.args.shell:
            if self.args.receiveFile:
                print('--shell和--receiveFile不可以一起使用')
                sys.exit()
        
            else:
                def execute(cmd):
                    cmd = cmd.strip() #去掉前后空格
                    if not cmd:
                        return #啥都不干
                    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT) #记住这行，subprocess.check_ouput在命令行执行一条命令并返回其输出。shlex.split以Unix命令行格式改变cmd的格式，stderr=subprocess.STDOUT会在命令执行错误时返回错误信息
                    if output:
                        return output.decode()
                    else:
                        return 'Done!'


                while True:
                    receive_all_ex = b''
                    receive_ex = b''
                    try:
                        while '\n' not in receive_ex.decode('utf-8'):
                            receive_ex = client.recv(64)
                            if receive_ex:
                                print('[*] 已收到：'+ receive_ex.decode())
                            receive_all_ex += receive_ex
                        #if 'exit' in receive_all_ex.decode('utf-8'):
                        #    break
                        cmd = receive_all_ex.decode()
                        response = execute(cmd)
                        if response:
                            client.send(b'\n'+response.encode())
                    except Exception as e:
                        print(f'Wrong!{e}')
                        client.send(b'[!!] Wrong command!')


        #文件接收
        elif self.args.receiveFile:
            #client.send(b'If you want to leave, please send GOODBYE\n')
            data = ''
            while True:
                recv_for_file = client.recv(4096)
                if 'GOODBYE' in recv_for_file.decode():
                    client.send(b'GOODBYE')
                    break
                else:
                    print('[*] Received:'+ recv_for_file.decode('utf-8'))
                    client.send(b'I have received: '+ recv_for_file)
                    data += recv_for_file.decode()

            if data:
                with open(self.args.receiveFile, 'w') as f:
                    #print('打开文件')
                    f.write(data.encode())
                message = f'[*] 您的数据已经写入{self.args.receiveFile}'
                client.send(message)
                print(message)

            event.clear() #信号为false


        # 普通监听模式
        else:
            while True:
                try:
                    receive1 = client.recv(4096).decode('utf-8')
                    print('[*] Receive: '+receive1)
                    #如果收到GOODBYE，则回应GOODBYE，并断开连接
                    if 'GOODBYE' in receive1 :
                        client.sendto(b'GOODBYE', (address[0],address[1]))
                        break
                    #正常情况下，给对方一个ACK
                    else:
                        client.sendto(bytes('I have received: '+receive1, encoding='utf-8'), (address[0], address[1]))

                except BrokenPipeError: 
                    print('对方已断开连接！')
                    break


    # udp接收函数，单独用函数是为了配合装饰器，从而让函数定时退出
    @Kskip(4)
    def ReceiveU(self):
        receive2 = b''
        while True:
            #相比与recv，recvfrom的特殊性仅在于会返回一个元组，包括数据和地址
            #receive2 = self.socket_udp.recvfrom(4096)
            #print('[*] 对方回答：'+receive2[0].decode('utf-8')+f' from {receive2[1][1]}:{receive2[1][2]}')
            one_receive = self.socket_udp.recv(4096)
            receive2 += one_receive
            if len(one_receive) < 4096:
                break
        return receive2.decode()

    # tcp接收函数
    @Kskip(4)
    def ReceiveT(self):
        receive3 = b''
        while True:
            one_receive = self.socket.recv(4096)
            receive3 += one_receive
            if len(one_receive) < 4096:
                break
        return receive3.decode()

    #发送数据模块
    def Ksend(self):

        # udp模块
        if self.args.udp:
            print('[*] 请输入你要发送的数据：')
            while True:
                i1 = input('>> ')
                c1 = Check(i1)
                if c1:
                    continue
                i1 += '\n'
                self.socket_udp.sendto(bytes(i1, encoding='utf-8'),(self.args.target, self.args.port))
                receive2 = self.ReceiveU()
                print('[*] 对方回答：'+receive2)
                if receive2 == 'GOODBYE':
                    print('[*] 自动退出程序，再见！')
                    sys.exit()
                


        # tcp模块
        else:
            try:
                self.socket.connect((self.args.target, self.args.port))
            except ConnectionRefusedError:
                print('目标端口拒绝连接！')
                sys.exit()
            print(f'[*] 连接成功--{self.args.target}, {self.args.port}')
            while True:
                i2 = input(">> ")
                c2 = Check(i2)
                if c2:
                    continue
                i2 += '\n'
                self.socket.send(i2.encode())
                receive3 = self.ReceiveT()
                print('[*] 对方回答：'+receive3)
                if 'GOODBYE' in receive3:
                    print('[*] 自动退出程序，再见！')
                    self.socket.close()
                    sys.exit()





#程序执行入口
if __name__ == '__main__':
    print('''

██╗  ██╗██╗   ██╗ ██████╗  ██████╗ ███████╗███████╗
██║ ██╔╝╚██╗ ██╔╝██╔════╝ ██╔═══██╗██╔════╝██╔════╝
█████╔╝  ╚████╔╝ ██║  ███╗██║   ██║███████╗███████╗
██╔═██╗   ╚██╔╝  ██║   ██║██║   ██║╚════██║╚════██║
██║  ██╗   ██║   ╚██████╔╝╚██████╔╝███████║███████║
╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                                                                      
            ''')

    myparser = argparse.ArgumentParser(
            prog='kgcat', 
            description='This is a simple net tool like a small netcat :)', 
            formatter_class=argparse.RawDescriptionHelpFormatter, #表示description和epilog不需要自动换行
            epilog=textwrap.dedent( #textwrap.dedent表示自动将多行字符串的前面的空白补齐
            '''
            examples:
              python kgcat.py -t 127.0.0.1 -p 55555
              python kgcat.py -p 12345 -l

            default:
              The protocol is TCP if no '-u'
              The port is 12345 if no '-p' 
              The target is 127.0.0.1 if no '-t'
            '''
            ))
    myparser.add_argument('-s', '--shell', action='store_true', help='give others shell in listening') #aciont='store_true'意思是，当输入-c命令时，给命名空间返回true
    myparser.add_argument('-t', '--target', default='127.0.0.1', help='the target you want to hack')
    myparser.add_argument('-p', '--port', default=12345, type=int,help='the port you want to hack')
    myparser.add_argument('-u', '--udp', action='store_true', help='send UDP message')
    myparser.add_argument('-l', '--listen', action='store_true', help='listen in your port')
    myparser.add_argument('-rf', '--receiveFile', help='receive file in listening')
    #myparser.add_argument('-hs', '--https', action='store_true', help='send https message')
    args = myparser.parse_args() #args是命名空间，这行命令将用户输入的参数去掉双杠后作为命名空间的属性
    #if args.listen:
    #    buffer = ''
    #else:
        # sys.stdin是python自动打开的文件对象（linux万物皆文件）
        # 该文件对象用文件描述符0
    #    print('请输入你要发送的数据：')
    #    buffer = sys.stdin.readline()
    kc = KyCat(args)
    kc.Kstart()
