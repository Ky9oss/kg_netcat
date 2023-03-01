import socket
import re
import sys



whoami = socket.gethostname()

# 返回ip号，如果输入为域名，则自动转化为ip号
def NameToNumber():
    while True:
        print("请输入目标ip或域名：")
        i1 = input()
        if i1 == 'q':
            print('再见！')
            sys.exit()
        else:
            pattern1 = re.compile(r'\d+\.\d+\.\d+\.\d+')
            m = pattern1.match(i1)
            # 如果输入的格式为ipv4号
            if m is not None:
                try:
                    hostname = socket.gethostbyaddr(i1)
                except:
                    print("没有找到该ip的对应域名")
                else:
                    print('找到了该ip的对应域名为:'+hostname[0])
                finally:
                    print('已选择你要连接的目标：'+i1)
                    print('-------------------------------')
                    return i1
            # 如果输入的格式为域名
            else:
                try:
                    hostnumber = socket.gethostbyname(i1)
                except:
                    print("Wrong!无法找到您输入的域名的对应ip。请检查是否输入错误，或尝试输入目标ip代替域名。")
                else:
                    print("您输入的域名是："+i1)
                    print('找到了其对应ip是：'+hostnumber)
                    print('-------------------------------')
                    return hostnumber


# 返回目标端口号
def GetPort():
    while True:
        i2 = input('请输入目标端口号：')
        if i2 == 'q':
            print('再见！')
            sys.exit()
        else:
            if re.match(r'\d+', i2) is not None:
                print('已确定目标端口号：' + i2)
                print('-------------------------------')
                return i2
            else:
                print("你输入的端口号有误！请重新输入！")
                


# 主函数
def main():
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        try:
            s1.connect((NameToNumber(), int(GetPort())))
        except:
            print("连接失败！请查看你输入的端口号或目标ip是否正确！")
        else:
            print('请输入你要发送给对方的数据：')
            while True:
                i3 = input()
                s1.send(i3.encode('utf-8'))
                print("已发送："+i3)

                #i4 = input('请选择你要接受的数据每个报文段的大小：')
                #print("已选择："+i4)

                response = s1.recv(4096)
                print('对方回答：'+response.decode())
                print('-------------------------------')
                if response.decode('utf-8') == 'GOODBYE':
                    print("连接已关闭！再见！")
                    s1.shutdown(socket.SHUT_RDWR)
                    sys.exit()
                else:
                    print('可以继续发送数据，退出请按Ctrl+C')


    except KeyboardInterrupt:
        s1.close()
        print("再见！")



if __name__ == '__main__':
    main()
