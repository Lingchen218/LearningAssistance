# -- coding: utf-8 --

import cProfile
import logging
import asyncio
import time,re,hashlib,webbrowser,requests,json,threading,tkinter.messagebox,tempfile
from tkinter import ttk
from time import sleep
from bs4 import BeautifulSoup
from tkinter import messagebox
from DeviceInformation import DeviceInformation
import tkinter as tk
import platform
from SysTrayIcon import *
from tkinter.ttk import *
from chaoxing import chaoxing
from Imager.Imager import getIcon
import nest_asyncio
nest_asyncio.apply()
import aiohttp

os.environ['NO_PROXY'] = 'thenobleyou.com'  # 设置直接连接 不使用任何代理
os.environ['NO_PROXY'] = 'chaoxing.com'
version = '1.2.3'
logsPathNam = './logs/error.log'
a_diengyi = 0  # 如果等于1就说明登录成功
if not os.path.isdir(re.findall(r"/(.*)/",logsPathNam)[0]):  # 无文件夹时创建
    os.makedirs(re.findall(r"/(.*)/",logsPathNam)[0])
logging.basicConfig(level=logging.INFO,  # 设置级别，根据等级显示
                    filename=logsPathNam,
                    format='%(asctime)s-[%(filename)s-->line:%(lineno)d]-%(levelname)s:%(message)s')# 设置输出格式
# logging.debug('This is a debug log')
# logging.info('This is a debug info')
# logging.warning('This is a warning log')
# logging.error('This is a error log',456)
# logging.critical('This is a critical log')
class zhihuishu():
    def __init__(self,cookie):
        self.uuid = re.findall('%22%2C%22uuid%22%3A%22(.*?)%22',cookie)[0]
        self.headers = {'Cookie':cookie,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    def huoqukecheng(self):

        # 获取 课程url
        url = 'https://onlineservice.zhihuishu.com/student/course/share/queryShareCourseInfo'
        data = {'uuid': self.uuid,
                'pageSize': '5',
                'pageNo': '1',
                'status': '0'
                }
        response = requests.post(url, data=data, headers=self.headers, verify=False).json()
        if response['result']['totalCount']!=0:
            for kecheng in response['result']['courseOpenDtos']:
                k_c_name = kecheng['courseName']  # 课程名称
                logging.warning('课程名称' + str(k_c_name))
        else:

            logging.warning('没有课程，就去找 课程')
            # 获取学校id
            url = 'https://onlineservice.zhihuishu.com/student/home/index/getCertificateInfo?uuid={}'.format(self.uuid)
            school_id = requests.get(url,headers=self.headers).json()['result']['schoolId']
            url = 'http://onlineservice.zhihuishu.com/student/course/share/querySelectCourseInfo'
            params = {
                'schoolId':school_id,
                'uuid':self.uuid
            }
            # huod = requests.get(url,params=params,headers=self.headers).json()['result']
            # for ke_c in huod:
            #     print(ke_c)

class choa:
    def __init__(self,iswangluo):
        self.loop = asyncio.get_event_loop()
        self.ifc_file = './Bpp3.ico'
        self.defaultesaveconfig = '\config\config.ini'
        self.kaoshi_ss = False  # 是否开启考试
        # 日志消息列表
        self.listxiaox = []
        self.wanglu = iswangluo
        self.time = 0 # 当前默认显示

        self.time1 = 0  # 注册验证码时长
        self.data_json = None
        self.windowregret = None
        # 检测网络是否连通
        self.sysTrayIcon = None

        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        if self.wanglu:
            try:
                #
                self.data_json = requests.get('http://blog.thenobleyou.com/shuakelogo/json_data.php',headers=self.headers,timeout=3).json()
            except:
                self.data_json = False
        else:
            self.data_json = False
        self.timezhaohui = self.data_json.get("Retrievecount",60)  # 找回密码验证码时长
        self.timezhuce = self.data_json.get("Registercount",60)  # 注册验证码时长
        self.Devicesinfo = DeviceInformation()
        # 获取屏幕分辨率
        self.window = tk.Tk()
        self.screenWidth = self.window.winfo_screenwidth()
        self.screenHeight = self.window.winfo_screenheight()
        self.createconfigfile()
    # 创建配置文件
    def createconfigfile(self):
        tmpfd, tempfilename = tempfile.mkstemp()
        os.close(tmpfd)
        os.unlink(tempfilename)
        self.filename = tempfile.tempdir + '\\' + self.data_json['keysalt'] + self.defaultesaveconfig
        path = self.filename[0:self.filename.rfind("\\")]
        if not os.path.isdir(path):  # 无文件夹时创建
            os.makedirs(path)
        if not os.path.isfile(self.filename):  # 无文件时创建
            with open(self.filename, mode="w", encoding="utf-8"):
                pass

        with open(self.filename, mode='r',encoding="utf-8") as f:
            try:
                a = json.loads(f.read())
                self.user_xinxi = a.get('uid','')
                self.user_pass = a.get('passwd','')
            except:
                self.user_xinxi = ''
                self.user_pass = ''
        #
    # 存图标
    def ico_(self):
        while True:
            try:
                self.window.iconbitmap(self.ifc_file)
                break
            except:
                with open(self.ifc_file, 'wb')as f:
                    f.write(getIcon())
                self.window.iconbitmap(self.ifc_file)
                break
                # self.window.tk.call(PhotoImage('wm', 'iconphoto', self.window._w, file=self.ifc_file))
    # 软件打开显示提示框 判断网络是否联通，提示欢迎页面
    def shouyetishi(self):
        if not self.data_json:
            sleep(1)
            tk.messagebox.showinfo('提示', '网络连接超时',parent=self.window)  # 提示框
            self.window.destroy()
        else:
            sleep(1)
            tk.messagebox.showinfo('欢迎使用', '欢迎使用本软件'+self.data_json['announcement'],parent=self.window) # 提示框
    # 主函数
    async def main(self):
        self.th((self.shouyetishi,self.ico_,))

        self.window.title('超星刷课助手')
        self.window.geometry(self.Getsizecoor(800,600))  # 窗口大小
        menu_options = (('等待开发', None, self.switch_icon), ('大家好', None, (('io', None, self.switch_icon),)))
        self.sysTrayIcon = SysTrayIcon(self.ifc_file, '超星刷课', menu_options, default_menu_index=1,
                                       objmain=self.window, OnWinShow=self.OnwinShow, on_quit=self.exit)
        self.window.bind("<Unmap>", lambda event:self.Unmap() if self.window.state()=="iconic" else False )
        self.window.protocol('WM_DELETE_WINDOW', self.exit)  # 右上角的关闭事件
        self.logo_button = Button(self.window, text="登录",command=lambda:self.th((self.ruanjilogo, )))  # 登录按钮
        zhuci_button = Button(self.window, text="注册", command=lambda :self.registredet() )  # 注册按钮
        zhaohui_button = Button(self.window, text="找回密码", command=lambda:self.back() )  # 找回密码按钮
        updata_button = Button(self.window, text="软件更新", command=self.update, )  # 更新按钮
        logo = Label(self.window, text='账号')
        describe = str(self.data_json.get("describe","本软件支持超星的全部刷课流程 本次更新为9月17日 软件修复若干bug ")) + " 当前python版本" + platform.python_version()
        text_s = Label(self.window, text=describe)
        pass_text = Label(self.window, text='密码')
        self.confirmLabel = Label(self.window)  # 登录时的状态
        user_ = tk.StringVar()
        user_.set(self.user_xinxi)
        self.pass_Entry = Entry(self.window, textvariable=user_, width=25, font=("Times", 10, "bold"))  # 账号框
        passwd_ = tk.StringVar()
        passwd_.set(self.user_pass)
        self.namee_Entry = Entry(self.window, show="*", textvariable=passwd_, width=25,font=("Times", 10, "bold"))  # 密码框
        logo.place(relx=0.15, rely=0.2, relwidth=0.3, relheight=0.05)
        pass_text.place(relx=0.15, rely=0.3, relwidth=0.3, relheight=0.05)
        self.logo_button.place(relx=0.35, rely=0.4, relwidth=0.1, relheight=0.05)
        zhuci_button.place(relx=0.55, rely=0.4, relwidth=0.1, relheight=0.05)
        zhaohui_button.place(relx=0.66, rely=0.3, relwidth=0.1, relheight=0.05)
        updata_button.place(relx=0.66, rely=0.2, relwidth=0.1, relheight=0.05)
        self.pass_Entry.place(relx=0.35, rely=0.2, relwidth=0.3, relheight=0.05)
        self.namee_Entry.place(relx=0.35, rely=0.3, relwidth=0.3, relheight=0.05)
        self.confirmLabel.place(relx=0.35, rely=0.1, relwidth=0.3, relheight=0.05)
        text_s.place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.05)
        self.window.mainloop()
    # 输入自动输入账号密码
    def autoinputuserpass(self):
        self.pass_Entry.delete(0,tk.END)  # 用户名
        self.namee_Entry.delete(0,tk.END) #
        self.namee_Entry.insert(0,self.user_pass)
        self.pass_Entry.insert(0,self.user_xinxi)
    # 运行时软件图标
    def switch_icon(self, _sysTrayIcon, icons = 'caiji.ico'):
        _sysTrayIcon.icon = icons
        _sysTrayIcon.refresh_icon()
    # 软件退出
    def exit(self, _sysTrayIcon = None):

        if messagebox.askokcancel("退出", "退出后无法刷课?"):
            logging.warning('exit...')
            try:
                os.remove('Bpp3.ico')
            except:
                pass
            self.exitc()
    def exitc(self):
        self.window.destroy()
        self.window.quit()
        quit()
    def _jia(self,password='1'):
        if self.data_json:
            _t = int(time.time() * 1000)

            url = self.data_json['url']  # 关联的url
            updata_url = self.data_json['updata_url']  # 更新地址
            mdd = (str(_t + self.data_json['QQ']) + 'qq').encode()
            cookies = hashlib.md5(mdd).hexdigest()
            passwords = (password + self.data_json['keysalt']).encode()
            data = {
                'time': _t,
                'cookies': cookies,
                'version': version,
                'updata_url': updata_url,
                'url': url,
                'version_':version==self.data_json['viersion'],
                'password4':hashlib.md5(passwords).hexdigest(),
                'headers':{
                    'User-Agent':self.headers['User-Agent'],
                    'Cookie':cookies+'_'+str(_t),
                    'referer':self.data_json['url']
                }

            }
            return data
        else:
            return False
    # 找回密码
    def back(self):
        self.window.withdraw()
        self.windowregret = tk.Tk()
        self.windowregret.iconbitmap(self.ifc_file)
        self.windowregret.geometry(self.Getsizecoor(500,500))  # 窗口大小
        self.windowregret.title('超星助手找回密码')  # 窗口的title
        lb1 = Label(self.windowregret, text="邮箱地址")  # 邮箱
        lb2 = Label(self.windowregret, text="请输入邮箱验证码")  # 请输入邮箱验证码
        lb3 = Label(self.windowregret, text="请输入新密码")  # 请输入邮箱验证码
        self.emailinput = Entry(self.windowregret)  # 邮箱框
        inpu2_code = Entry(self.windowregret)  # 验证码框
        inpu3_password = Entry(self.windowregret,show="*")
        lb1.place(relx=0.15, rely=0.3, relwidth=0.3, relheight=0.05)
        lb2.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.05)
        lb3.place(relx=0.1, rely=0.5, relwidth=0.3, relheight=0.05)
        self.time = self.timezhaohui
        self.time1 = self.timezhaohui
        self.fasong = Button(self.windowregret, text="发送验证码",command=lambda: self.captchatcount('/shuakelogo/exmail.php?action=back'))  # 发送验证码
        but_ok = Button(self.windowregret, text="确认",command=lambda: queren())
        self.emailinput.place(relx=0.41, rely=0.3, relwidth=0.3, relheight=0.05)
        inpu2_code.place(relx=0.41, rely=0.4, relwidth=0.3, relheight=0.05)
        inpu3_password.place(relx=0.41, rely=0.5, relwidth=0.3, relheight=0.05)
        self.fasong.place(relx=0.72, rely=0.3, relwidth=0.2, relheight=0.05)
        but_ok.place(relx=0.41, rely=0.6, relwidth=0.3, relheight=0.05)

        def queren():
            exmai = self.enmail_yanz(self.emailinput.get())
            if exmai:
                if len(inpu2_code.get())>5and len(inpu3_password.get())>5:
                    data = self._jia()
                    data['captcha'] = inpu2_code.get()
                    data['password'] = self._jia(inpu3_password.get())['password4']
                    data['exmail'] = exmai

                    response1 = requests.post(data['url'] + '/shuakelogo/exmail.php?action=back', data=data,headers=data['headers'])

                    response = response1.json()
                    if response['status']=='1':
                        tk.messagebox.showinfo('提示', '修改成功，请使用新密码登录')
                        self.window.deiconify()
                        self.windowregret.destroy()
                    elif response['status']=='15':
                        tk.messagebox.showinfo('提示', '验证码错误')
                    elif response['status']=='16':
                        tk.messagebox.showinfo('提示', '邮箱输入有误或密码有误')
                    else:
                        tk.messagebox.showinfo('提示', '未知错误')
                else:
                    tk.messagebox.showinfo('提示', '邮箱输入有误或密码有误')
            else:
                tk.messagebox.showinfo('提示', '邮箱地址不存在')
        def on_closing():
            if tk.messagebox.askokcancel("找回密码", "是否退出？"):


                self.windowregret.destroy()
                self.windowregret.quit()
                self.window.deiconify()
        self.windowregret.protocol("WM_DELETE_WINDOW", on_closing) # 关闭窗口事件
        self.windowregret.mainloop()
    # 账号密码确定
    def ruanjilogo(self):
        self.logo_button.config(state=tk.DISABLED)
        self.mima = self.pass_Entry.get()
        self.ruan_user = self.namee_Entry.get()
        if len(self.mima) > 0 and len(self.ruan_user) > 0:
            self.confirmLabel.config(text='正在登录')
            self.user_logo()
        else:
            self.confirmLabel.config(text='请输入账号密码')
            self.logo_button.config(state=tk.NORMAL)

    #显示窗口位置
    def Getsizecoor(self,xsizeof,ysizeof):
        x = int((self.screenWidth - xsizeof) / 2)
        y = int((self.screenHeight - ysizeof) / 2)
        return "%sx%s+%s+%s" % (xsizeof, ysizeof, x, y)

    # 软件更新
    def update(self):
        url = 'http://blog.thenobleyou.com/shuake_urser_logo.php?action=registrered_update'
        if self._jia()['version_']:
            tk.messagebox.showinfo('提示', '已是最新版本')  # 提示框
        else:
            webbrowser.open(self._jia()['updata_url'])

    # 软件登录
    def user_logo(self):
        self.confirmLabel.config(text='正在登录')
        data = self._jia()
        passwords = ( self.ruan_user+ self.data_json['keysalt']).encode()
        self.username = self.pass_Entry.get()
        data['password'] = hashlib.md5(passwords).hexdigest()
        data['user'] = self.pass_Entry.get()
        #k,md5 = self.Devicesinfo.GetDeviceMac()
        #data['supermd5'] = md5
        #data['k'] = k
        url = self._jia()['url'] + '/shuake_urser_logo.php?action=login'
        try:
            response = requests.post(url, data, timeout=5,headers=data['headers']).json()
            req = response['error']
            if req == '255':

                self.confirmLabel.config(text='请更新版本')
                tk.messagebox.showinfo('提示', '请更新版本')  # 提示框

                self.update()

                self.logo_button.config(state=tk.NORMAL)
            elif req == '200':

                self.saveuserpass(self.mima,self.ruan_user)

                if response['status'] == 'activation':

                    self.confirmLabel.config(text='登录成功')

                    tk.messagebox.showinfo('提示', '恭喜您登录成功')  # 提示框
                    # return None
                    self.logo_button.config(state=tk.NORMAL)
                    self.confirmLabel.config(text='')
                    self.suss_()
                elif response['status'] == 'inactivated':
                    tk.messagebox.showinfo('提示', '账号未激活！请到邮箱中点击激活链接，如果没有请到垃圾邮件中看一下！')
                    self.logo_button.config(state=tk.NORMAL)
                elif response['status'] == 'Forbidden':
                    self.confirmLabel.config(text='你被禁止登录了，请联系客服！')
                    tk.messagebox.showinfo('提示', '你被禁止登录了，请联系客服！')
                    self.logo_button.config(state=tk.NORMAL)
            elif req == '300':
                self.logo_button.config(state=tk.NORMAL)
                self.confirmLabel.config(text='账号或密码错误')
                tk.messagebox.showinfo('提示', '账号或密码错误')  # 提示框
            elif req == '请重试':
                self.logo_button.config(state=tk.NORMAL)
                self.confirmLabel.config(text='你的网络时延太大，建议你跟换网络')
                tk.messagebox.showinfo('提示', '你的网络时延太大，建议你跟换网络')
        except Exception as e:
            if str(e) == 'Extra':
                self.confirmLabel.config(text='软件出现bug系客服')
                self.logo_button.config(state=tk.NORMAL)
                tk.messagebox.showinfo('提示', '软件出现bug请联系客服')  # 提示框
            elif str(e).find('HTTP') == 0:
                self.logo_button.config(state=tk.NORMAL)
                self.confirmLabel.config(text='网络连接超时')
                tk.messagebox.showinfo('提示', '网络连接超时')  # 提示框
            else:
                
                self.logo_button.config(state=tk.NORMAL)
                self.confirmLabel.config(text='未知错误请联系客服')
                tk.messagebox.showinfo('提示', '未知错误请联系客服')  # 提示框

    # 多线程
    def th(self,funcs = None):
        for func in funcs:
            t1 = threading.Thread(target=func)
            t1.daemon = True
            t1.start()

    # 保存用户密码
    def saveuserpass(self,user,password):
        self.user_xinxi = user
        self.user_pass = password
        with open(self.filename, 'w',encoding='utf-8') as f:
            s = {'uid': user, 'passwd':password }
            f.write(json.dumps(s))

    # 登陆成功的页面
    def suss_(self):
        global a_diengyi
        a_diengyi = 1
        self.th((self.monitor,))  # 监控在线状态
        self.top77 = self.window.winfo_toplevel()
        self.style = Style()
        self.TabStrip1 = Notebook(self.top77)

        self.TabStrip1.place(relx=0, rely=0, relwidth=1, relheight=1)
        def b(user_text,password_text,title_text,type_int):

            TabStrip1__Tab1 = Frame(self.TabStrip1)
            self.chaoxing_user = Label(TabStrip1__Tab1, text=user_text, )
            self.chaoxing_pass = Label(TabStrip1__Tab1, text=password_text, )
            if type_int == 0:
                self.gonggao = Label(TabStrip1__Tab1, text='输入内容时建议切换为英文输入法,不然会出现乱码欧!', )
            elif type_int == 1:
                self.gonggao = Label(TabStrip1__Tab1, text='智慧树功能并不完善，输入内容时建议切换为英文输入法,不然会出现乱码欧!', )
            self.chaoxing_user.place(relx=0.1, rely=0.2, relwidth=0.2, relheight=0.05)
            self.chaoxing_pass.place(relx=0.1, rely=0.3, relwidth=0.2, relheight=0.05)
            self.gonggao.place(relx=0.1, rely=0.03, relwidth=0.8, relheight=0.05)
            status = Label(TabStrip1__Tab1, text='状态', )
            status.place(relx=0.1, rely=0.1, relwidth=0.2, relheight=0.05)
            user__ = Entry(TabStrip1__Tab1, width=25, font=("Times", 10, "bold"))
            passwd_ = Entry(TabStrip1__Tab1, width=25, font=("Times", 10, "bold"))
            user__.place(relx=0.35, rely=0.2, relwidth=0.3, relheight=0.05)  # 账号输入框
            passwd_.place(relx=0.35, rely=0.3, relwidth=0.3, relheight=0.05)  # 密码输入框
            denglu_anniu = Button(TabStrip1__Tab1, text="登录",command=lambda: a(user__.get().strip(),passwd_.get().strip(),type_int,denglu_anniu,status,TabStrip1__Tab1))
            denglu_anniu.place(relx=0.35, rely=0.4, relwidth=0.1, relheight=0.05)  # 登录按钮
            Button(TabStrip1__Tab1, text='关闭', command=lambda: TabStrip1__Tab1.destroy()).place(relx=0.65, rely=0.1, relwidth=0.1,relheight=0.05)
            self.TabStrip1.add(TabStrip1__Tab1, text=title_text)  # 标题
        b('超星账号','超星密码','超星、学习通、雅尔',0)
        b('智慧树账号', '智慧树密码','智慧树',1)
        def a(user,password,type_int,denglu_anniu,status,TabStrip1__Tab1):

            if len(user)>5 and len(password)>5:
                denglu_anniu.config(text='正在登录中...',state=tk.DISABLED)
                t1 = threading.Thread(target=self.chao,args=(user,password,type_int,denglu_anniu,status,TabStrip1__Tab1))
                t1.daemon = True
                t1.start()
            else:
                tk.messagebox.showinfo('提示', '请输入正确的账号密码',parent=self.TabStrip1)  # 提示框
                logging.warning("请输入正确的账号密码")
    # 验证邮箱地址是否正确
    def enmail_yanz(self,email):
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", str(email).strip())!=None:
            return email.strip()
        else:
            return False
    # 软件注册
    def registredet(self):
        self.window.withdraw()  # 隐藏主程序
        self.windowregret = tk.Tk()
        #window1.after(1, lambda: self.window.focus_force())
        self.windowregret.geometry(self.Getsizecoor(500,500))  # 窗口大小
        self.windowregret.title('超星助手注册')  # 窗口的title
        self.windowregret.iconbitmap(self.ifc_file)
        lb1 = Label(self.windowregret, text="账号")
        lb1_yz = Label(self.windowregret)
        lb2 = Label(self.windowregret, text="密码")
        lb2_yz = Label(self.windowregret)
        lb3 = Label(self.windowregret, text="请确认密码")
        lb3_yz = Label(self.windowregret)
        lb4 = Label(self.windowregret, text="邮箱")  # 邮箱
        lb4_yz = Label(self.windowregret)
        lb5 = Label(self.windowregret, text="账号最少6位数字字母组合")
        lb6 = Label(self.windowregret, text="数字加字母大小写")
        lb7 = Label(self.windowregret, text="数字加字母大小写")
        lb8 = Label(self.windowregret, text="验证码")  # 邮箱验证码
        lb9_gonggao = Label(self.windowregret, text="公告 本软件输入框建议使用英文输入法不然容易乱码")  # 邮箱验证码
        def inpu1_z():
            if re.match("^[-_a-zA-Z0-9]{4,16}$", str(inpu1.get())) != None:
                lb1_yz.config(text='')
                return True
            else:
                return False
        def inpu1_c():
            lb1_yz.config(text='账号有误')
        inpu1 = Entry(self.windowregret, validate='focusout', validatecommand=inpu1_z, invalidcommand=inpu1_c) # 账号输入框
        def inpu2_z():
            passregular = self.data_json['passregular']
            if re.match(passregular, inpu2.get()) != None:
                lb2_yz.config(text='')
                return True
            else:
                return True
        def inpu2_c():
            lb2_yz.config(text='密码太弱了')
        inpu2 = Entry(self.windowregret, show="*", validate='focusout', validatecommand=inpu2_z, invalidcommand=inpu2_c) # 密码输入框
        def inpu3_z():
            if inpu2.get() == inpu3.get():
                lb3_yz.config(text="")
                return True
            else:

                return False
        def inpu3_c():
            lb3_yz.config(text='密码不一致')
        inpu3 = Entry(self.windowregret, show="*", validate='focusout', validatecommand=inpu3_z, invalidcommand=inpu3_c) # 密码确认框
        def inpu4_z():

            if re.match(self.data_json['passregular'], self.emailinput.get()) != None:
                lb1_yz.config(text='')
                return True
            else:
                return False
        def inpu4_c():
            lb4_yz.config(text='')  # 邮箱不正确
        self.emailinput = Entry(self.windowregret, validate='focusout', validatecommand=inpu4_z, invalidcommand=inpu4_c) # 邮箱输入框
        inpu5 = Entry(self.windowregret)
        lb1.place(relx=0.21, rely=0.08, relwidth=0.4, relheight=0.1)
        lb1_yz.place(relx=0.04, rely=0.08, relwidth=0.17, relheight=0.1)
        lb2.place(relx=0.21, rely=0.18, relwidth=0.3, relheight=0.1)
        lb2_yz.place(relx=0.04, rely=0.18, relwidth=0.17, relheight=0.1)
        lb3.place(relx=0.21, rely=0.28, relwidth=0.3, relheight=0.1)
        lb3_yz.place(relx=0.04, rely=0.28, relwidth=0.17, relheight=0.1)
        lb4.place(relx=0.21, rely=0.38, relwidth=0.3, relheight=0.1)
        lb4_yz.place(relx=0.04, rely=0.38, relwidth=0.17, relheight=0.1)
        lb5.place(relx=0.66, rely=0.08, relwidth=0.3, relheight=0.1)
        lb6.place(relx=0.66, rely=0.18, relwidth=0.3, relheight=0.1)
        lb7.place(relx=0.66, rely=0.28, relwidth=0.3, relheight=0.1)
        lb8.place(relx=0.21, rely=0.48, relwidth=0.3, relheight=0.1)
        inpu1.place(relx=0.35, rely=0.1, relwidth=0.3, relheight=0.05)  # 账号
        inpu2.place(relx=0.35, rely=0.2, relwidth=0.3, relheight=0.05)  # 密码
        inpu3.place(relx=0.35, rely=0.3, relwidth=0.3, relheight=0.05)  # 确认密码
        self.emailinput.place(relx=0.35, rely=0.4, relwidth=0.3, relheight=0.05)  # 邮箱
        inpu5.place(relx=0.35, rely=0.5, relwidth=0.3, relheight=0.05)  # 邮箱验证码
        lb9_gonggao.place(relx=0.15, rely=0.03, relwidth=0.7, relheight=0.05)



        def zhuci():

            if len(inpu1.get()) > 0 and len(inpu2.get()) > 0 and len(inpu3.get()) and len(self.emailinput.get()) and len(
                    inpu5.get()) > 0:
                if re.match("^[-_a-zA-Z0-9]{4,16}$", str(inpu1.get())) != None:  # 匹配账号
                    if inpu2.get() == inpu3.get():
                        if re.match(self.data_json['passregular'], inpu2.get()) != None:
                            password = str(inpu2.get().strip())
                            struser = str(inpu1.get().strip())
                            password_encode = (password + self.data_json['keysalt']).encode()
                            password_md5 = hashlib.md5(password_encode).hexdigest()
                            data = self._jia()
                            data['user'] = struser
                            data['password'] = password_md5
                            data['email'] = str(self.emailinput.get().strip())
                            data['captcha']=str(inpu5.get().strip())
                            k, md5 = self.Devicesinfo.GetDeviceMac()
                            data['supermd5'] = md5
                            data['k'] = k
                            url = data['url'] + '/shuake_urser_logo.php?action=registrered'
                            resonse = requests.post(url, data,headers=data['headers'])
                            resp=resonse.json()
                            if resp['error'] == '200':
                                self.saveuserpass(struser, password)
                                self.autoinputuserpass()
                                tk.messagebox.showinfo('提示', '注册成功',parent=self.windowregret)
                                self.zhuce1.config(state = tk.DISABLED)
                                self.window.deiconify()  # 显示主窗口
                                self.windowregret.quit()
                                self.windowregret.destroy()  # 把当前的窗口关闭
                                #更新当前输入框信息
                            elif resp['error'] == '205':
                                if resp['error1'] == '203':
                                    tk.messagebox.showinfo('提示', '用户名已存在,请重新注册',parent=self.windowregret)
                            elif resp['error']=='255':
                                tk.messagebox.showinfo('提示', '请更新软件',parent=self.windowregret)
                                self.update()
                            elif resp['error']=='256':
                                tk.messagebox.showinfo('提示', '验证码失效',parent=self.windowregret)
                        else:
                            tk.messagebox.showinfo('提示', '密码太弱了',parent=self.windowregret)
                    else:
                        tk.messagebox.showinfo('提示', '两次密码输入有误',parent=self.windowregret)
                else:
                    tk.messagebox.showinfo('提示', '账号输入有误',parent=self.windowregret)


            else:

                tk.messagebox.showinfo('提示', '请输入正确内容',parent=self.windowregret)  # 提示框
        self.zhuce1 = Button(self.windowregret, text='注册', command=lambda: zhuci())
        self.zhuce1.place(relx=0.35, rely=0.6, relwidth=0.3, relheight=0.05)
        self.time = self.timezhuce # 验证码倒计时时常
        self.time1 = self.timezhuce
        self.fasong = Button(self.windowregret, text='发送邮箱验证码', command=lambda:self.captchatcount('/shuakelogo/exmail.php?action=registrered_email_code'))  # 发送邮箱验证码

        self.fasong.place(relx=0.66, rely=0.4, relwidth=0.2, relheight=0.05)
        def handle_focus(event):
            pass  # 准备验证邮箱和账户
        self.windowregret.bind("<FocusIn>", handle_focus)  # 聚焦事件
        def on_closing():
            if messagebox.askokcancel("注册", "是否取消注册"):
                self.window.deiconify()  # 显示主窗口
                self.windowregret.quit()
                self.windowregret.destroy()  # 把当前的窗口关闭

        self.windowregret.protocol("WM_DELETE_WINDOW", on_closing) # 关闭窗口事件
        self.windowregret.mainloop()

    def captchatcount(self,url1):
        # 单击按钮调用该方法
        after = self.fasong.after(1000, func=lambda:self.captchatcount(url1))
        # 调用一次时间减一
        self.fasong['text'] = self.time
        # 延时1秒在此调用该方法
        self.time -= 1
        # 将按钮的文本设为倒计时时间
        self.fasong['state'] = 'disable'
        # 禁用按钮
        if int(self.fasong['text']) == self.time1:
            def emailsendcode():
                email = self.enmail_yanz(self.emailinput.get())
                if email:
                    data = self._jia()
                    url = data['url'] + url1
                    data['email'] = email
                    respon = requests.post(url, data, headers=data['headers'])

                    try:
                        print(respon.text)
                        resp = respon.json()

                        if resp.get("status",None) == '1':
                            logging.info('邮件发送成功')
                        elif resp.get('error',None) == '255':
                                self.update()
                                self.time = 1
                        else:
                            atext = None
                            if resp.get("status",None) == '2':
                                atext =  '发送邮件失败，请确认邮件地址正确'  # 提示框
                            elif resp.get("status",None) == '3':
                                atext = '邮箱已经存在，请找回密码'
                            elif resp.get("status",None) == '4':
                                atext = '邮箱输入有误'
                            elif resp.get("status",None) == '404':
                                atext = '邮箱不存在，请先注册'
                            elif resp.get('error', None):
                                atext = resp['msg']
                            else:
                                atext = '未知错误'
                            tk.messagebox.showinfo('提示', atext, parent=self.windowregret)  # 提示框
                            self.time = 1
                    except Exception as e:
                        logging.error(e)
                        logging.error(respon.text)
                        tk.messagebox.showinfo('提示', '服务器故障', parent=self.windowregret)  # 提示框
                else:
                    self.time = 1
                    tk.messagebox.showinfo('提示', '邮箱输入错误', parent=self.windowregret)

            self.th((emailsendcode,))
        elif self.time <= 0:
            # 倒计时结束
            self.time = self.time1
            # 重置倒计时时间
            self.fasong['state'] = 'normal'
            # 启用按钮
            self.fasong['text'] = '重新发送'
            # 将按钮文本设为重新发送
            self.fasong.after_cancel(after)
    # 软件超星登录
    def chao(self,user,password,type_int,denglu_anniu,status,TabStrip1__Tab1):  # 登录超星页面点击录按钮触发
        status.config(text='正在登录')
        bloginsuccess = False
        if type_int==0:
            self.chao_ = chaoxing(_jia=self._jia,logging=logging)
            bloginsuccess = self.chao_.login(user,password)
        elif type_int==1:
            # self.headers = self.zhihui_login(user,password)
            self.headers = False
            logging.info('智慧树登录开发中')

        if bloginsuccess:
            status.config(text='登录成功')
            for widget in TabStrip1__Tab1.winfo_children():
                widget.destroy()
            self.bofzhuangt_ = Label(TabStrip1__Tab1, text='播放状态--请稍等马上就开始刷课流！！大约等待1-5分钟')
            self.bofzhuangt_.place(relx=0.1, rely=0.48, relwidth=0.7, relheight=0.05)
            self.status = Label(TabStrip1__Tab1, text='状态', )
            self.status.place(relx=0.1, rely=0.1, relwidth=0.2, relheight=0.05)
            kec = None
            if type_int == 0:
                  # 超星获取课程
                kec = self.chao_.huoqukecheng()  #获取超星课程
            elif type_int == 1:
                chao_ = zhihuishu(self.headers) # 智慧树获取课程
                kec = chao_.huoqukecheng()
            self.huoqukecheng_status = Label(TabStrip1__Tab1, text='成功获取到课程')
            if not kec:
                self.huoqukecheng_status['text'] = "获取课程失败"
            self.huoqukecheng_status.place(relx=0.35, rely=0.1, relwidth=0.2, relheight=0.05)
            kecheng = []
            for i, isd in kec.items():
                for s, c in isd.items():
                    kecheng.append(s)
            kecheng = tuple(kecheng)
            comvalue = tk.StringVar()  # 窗体自带的文本，新建一个值
            comvalue.set('请选择课程')
            self.comboxlist = Combobox(TabStrip1__Tab1, textvariable=comvalue)  # 初始化
            self.comboxlist["values"] = kecheng
            self.comboxlist.configure(state="readonly")
            self.comboxlist.place(relx=0.35, rely=0.2, relwidth=0.2, relheight=0.05)
            kechengming = Label(TabStrip1__Tab1, text='请选择课程-->>')
            self.msgbox = tk.Text(TabStrip1__Tab1,width=100,height=3,fg='red')
            self.msgbox.insert('1.0', "登录成功\n")
            kechengming.place(relx=0.1, rely=0.2, relwidth=0.2, relheight=0.05)
            kechengming1 = Label(TabStrip1__Tab1, text='<<--点击右边的下拉箭头')
            kechengming1.place(relx=0.6, rely=0.2, relwidth=0.2, relheight=0.05)
            kechengming2 = Label(TabStrip1__Tab1, text='播放速度1-99-->>')
            kechengming2.place(relx=0.03, rely=0.3, relwidth=0.2, relheight=0.05)
            speed_ = Entry(TabStrip1__Tab1, width=50, font=("Times", 10, "bold"))
            speed_.insert(0, "1")
            speed_.place(relx=0.2, rely=0.3, relwidth=0.09, relheight=0.05)
            self.start_ = Button(TabStrip1__Tab1, text='开始刷课',command=lambda: a())
            self.kaoshi = Button(TabStrip1__Tab1, text='是否开启考试',command=lambda: a())
            self.start_.place(relx=0.4, rely=0.3, relwidth=0.3, relheight=0.05)
            Label(TabStrip1__Tab1, text='软件需要一直运行').place(relx=0.35, rely=0.6, relwidth=0.2, relheight=0.05)
            self.tishi_suc = Label(TabStrip1__Tab1, text='You can play games in the direction of chase drama!', )
            self.tishi_suc.place(relx=0.2, rely=0.55, relwidth=0.5, relheight=0.05)
            self.msgbox.pack()
            self.settings_s = Button(TabStrip1__Tab1, text='自动考试设置', )
            self.frame_r = TabStrip1__Tab1
            self.settings_s.bind("<Button-1>", self.settings_sa)
            self.settings_s.place(relx=0.03, rely=0.40, relwidth=0.15, relheight=0.05)
            def a():

                t1 = threading.Thread(target=self.shuake,args=(TabStrip1__Tab1,speed_))
                t1.daemon = True
                t1.start()
        else:
            status.config(text='密码输入错误')
            if type_int == 0:
                tk.messagebox.showinfo('提示', '超星账号密码输入错误! 如果多次输入密码错误 超星官方会冻结15分钟，请自行查看是否冻结',parent=self.TabStrip1)  # 提示框
            elif type_int == 1:
                tk.messagebox.showinfo('提示', '智慧树账号或密码输入错误',parent=self.TabStrip1)  # 提示框

            denglu_anniu.config(text='请重新登陆', state=tk.NORMAL)

    # 智慧树登录
    def zhihui_login(self,user,password):
        headers = {
            'User-Agent':self.headers['User-Ageng'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url_login = 'https://passport.zhihuishu.com/login'
        url_post = 'https://passport.zhihuishu.com/user/validateAccountAndPassword?u_asec=099%23KAFEH7E2EgdEhGTLEEEEEpEQz0yFD6fFDXR4G6NcSu3YW6DTSu34G60hS%2FUTEEaStIIEXyaSt3xVN3'
        SERVERID = requests.post(url_post,headers=headers,).headers

        
        response1 = requests.get(url_login,headers=headers,allow_redirects=False)
        cookie_ = response1.headers['Set-Cookie']
        route = 'route='+(re.findall('route=(.*?);',cookie_)[0]) +';'
        JSESSIONID = 'JSESSIONID=' + (re.findall('JSESSIONID=(.*?);', cookie_)[0]) + ';'
        headers['Cookie'] = JSESSIONID+route

        busp = BeautifulSoup(response1.text,'html.parser')
        lt = busp.find('input',{'name':'lt'}).get('value')
        execution = busp.find('input',{'name':'execution'}).get('value')
        data = {
            'lt': lt,
            '_eventId': 'submit',
            'username': user,
            'password': password,
            'execution':execution,
            'remember':'on'
        }
        
        response = requests.post(url_login,headers=headers,data=data,allow_redirects=False).headers
        if 'Location' in response:
            if response['Location']=='https://www.zhihuishu.com':
                return response['Set-Cookie']
            else:
                return False
        else:
            return False

    # 用户消息日志
    def print_msgbox(self,msgstr):



        if not self.sysTrayIcon.Isminmize:

            logging.info("显示")
            self.listxiaox.append(msgstr)
            self.OnwinShow()
        else:
            self.listxiaox.append(msgstr)
            logging.info("最小化到后台了隐藏")
            return None
    def OnwinShow(self,lparam=None):



        for xiaox in self.listxiaox:
            self.msgbox.insert(tk.END, xiaox + '\n')
            self.msgbox.see(tk.END)
        del self.listxiaox[:]
    # 软件的设置
    def settings_sa(self,event):
        aca = event.widget['text']
        if aca=='自动考试设置':
            a = tk.messagebox.askokcancel('提示', '是否开启自动考试', parent=self.frame_r)
            if a:
                self.kaoshi_ss = True

                self.frame_r.after(1000)
                self.settings_s.config(text="已开启自动考试")
                self.frame_r.update()
            else:
                self.kaoshi_ss = False
                self.settings_s.config(text="已关闭自动考试")
        elif aca=='已开启自动考试':
            a = tk.messagebox.askokcancel('提示', '是否关闭自动考试', parent=self.frame_r)
            if a:
                self.kaoshi_ss = False
                self.settings_s.config(text="已关闭自动考试")
            else:
                self.kaoshi_ss = True
                self.settings_s.config(text="已开启自动考试")
        elif aca=='已关闭自动考试':
            a = tk.messagebox.askokcancel('提示', '是否开启自动考试', parent=self.frame_r)
            if a:
                self.kaoshi_ss = True
                self.settings_s.config(text="已开启自动考试")
            else:
                self.kaoshi_ss = False
                self.settings_s.config(text="已关闭自动考试")


        # 设置的
        if False:
            self.window.withdraw()  # 隐藏主程序
            window3 = Tk()
            window3.iconbitmap(self.ifc_file)
            window3.title('超星刷课设置')
            # 设置主窗口标题
            # 设置窗口初始位置在屏幕居中
            window3.geometry("%sx%s+%s+%s" % (self.winWidth, self.winHeight, self.x, self.y))
            # 固定窗口大小
            window3.resizable(0, 0)
            tab = ttk.Notebook(window3)
            frame111 = tk.Frame(tab, bg="red")
            tab1 = tab.add(frame111, text="1")
            tab.pack(expand=True, fill=tk.BOTH)
            self.kaoshi_ss = True


            tab.select(frame111)
            def on_closing():
                if messagebox.askokcancel("设置", "是否保存当前设置"):
                    self.window.deiconify()  # 显示主窗口
                    window3.destroy()  # 把当前的窗口关闭
            window3.protocol("WM_DELETE_WINDOW", on_closing)  # 关闭窗口事件
            window3.mainloop()

    # 最小化需要的方法
    def Unmap(self):
        self.sysTrayIcon.Isminmize = True  # 最小化为真
        self.window.withdraw()
        self.sysTrayIcon.show_icon()
        # self.sysTrayIcon.activation()

    # 开始刷课
    def shuake(self,TabStrip1__Tab1,speed_):

        self.speed_ = speed_
        self.start_.config(text='正在初始化请稍等...',state=tk.DISABLED)
        name = self.comboxlist.get()  # 课程名称
        ke_ar = self.comboxlist.current()  # 判断当前是否被选中课程
        speed = self.speed_.get().strip()  # 获取播放速度
        def kaishi(speed,title_name):
            self.speed_.config(state=tk.DISABLED)
            TabStrip1__Tab1.after(1000)
            item = self.chao_.huoqukecheng()
            for title,url1 in item.items():
                if title_name in url1:
                    url = (url1[title_name])
                    break
            clazzid = re.findall('clazzid=(.*?)&', url)[0]
            kecheng_name = self.comboxlist.get()
            data = self._jia()
            data['clazzid'] = clazzid  # 课程的id
            data['kecheng_name'] = kecheng_name  # 课程的名字
            data['mima'] = str(self.mima)  # 本系统的用户名

            data['uid'] = self.chao_.getheaders()['Cookie']  # 超星的用户id
            try:

                def dengdai(isc):
                    start_text = self.bofzhuangt_['text']
                    while isc > -1:
                        TabStrip1__Tab1.after(1000)
                        self.start_.config(text='如果你的章节过多时间会很长' + str(isc), state=tk.DISABLED)
                        TabStrip1__Tab1.update()
                        if self.bofzhuangt_['text']=="当前课程播放完毕":
                            break
                        if start_text != self.bofzhuangt_['text']:
                            sleep(1)
                            self.start_.config(text='已经开始刷课了')
                            TabStrip1__Tab1.update()
                            break
                        isc -= 1
                def sddf( url, bofzhuangt_,kaoshi=False):
                    speed_ = int(speed)

                    a = self.chao_.huoquzhangjie( url,self.print_msgbox)

                    if a=="当前课程已经完成":
                        bofzhuangt_.config(text='当前课程播放完毕')
                        tk.messagebox.showinfo('提示', '当前课程已完成')
                        logging.info("该课程视频题目已完成内容已完成")
                        self.start_.config(text='开始刷课', state=tk.NORMAL)
                        self.speed_.config(state=tk.NORMAL)
                        return True
                    elif a=="":
                        logging.info("章节获取为空")

                    if not self.sysTrayIcon.Isminmize:
                        self.bofzhuangt_['text'] = "已经开始刷课了"
                        # tk.messagebox.showinfo('提示', '已经开始刷课了')

                    if kaoshi:
                        # 开启刷视频章节测试和考试
                        self.chao_.play_speed(speed_)
                        self.chao_.exam()
                    elif kaoshi=='1':
                        # 只刷考试
                        self.chao_.exam()
                    else:
                        # 只刷视频和章节测试

                        # self.loop.run_until_complete(self.chao_.play_speed(speed_,a))
                        self.chao_.play_speed(speed_, a)
                    tk.messagebox.showinfo('提示', '当前课程已完成')
                    self.start_.config(text='开始刷课', state=tk.NORMAL)
                    self.speed_.config(state=tk.NORMAL)
                def tijiao_kecheng(data):
                    url_kecheng = self._jia()['url'] + '/shuake_urser_logo.php?action=registrered_course_name'
                    requests.post(url_kecheng, data,headers=self._jia()['headers'])
                threads = []
                za = 300
                t1 = threading.Thread(target=dengdai, args=(za,))
                threads.append(t1)
                t2 = threading.Thread(target=sddf, args=( url, self.bofzhuangt_,self.kaoshi_ss,))
                threads.append(t2)
                t3 = threading.Thread(target=tijiao_kecheng, args=(data,))
                threads.append(t3)
                for t in threads:
                    t.daemon = True
                    t.start()
            except Exception as f:
                logging.error(f)
                TabStrip1__Tab1.after(1000)
                self.bofzhuangt_.config(text='连接服务失败')
                TabStrip1__Tab1.update()
        # 弹出确认框
        def querenkuang():
            a = tk.messagebox.askokcancel('提示', '你的播放速度较快建议1-10',parent=TabStrip1__Tab1)
            return a
        if ke_ar!=-1:
            try:
                if int(speed)<100 and len(name)>0:
                    self.huoqukecheng_status.place(relx=0, rely=0, relwidth=0, relheight=0)  # 隐藏“成功获取到课程”
                else:
                    tk.messagebox.showinfo('提示', '速度飞起来，不怕封号吗？', parent=self.window)  # 提示框
                    self.start_.config(text='开始刷课', state=tk.NORMAL)
                    self.status.config(text='请选择课程和输入播放速度')
            except :
                if len(speed)>0:

                    tk.messagebox.showinfo('提示', '请输入正确的数字', parent=self.window)  # 提示框
                    self.start_.config(text='开始刷课', state=tk.NORMAL)
                    self.speed_.config(state=tk.NORMAL)
                else:
                    tk.messagebox.showinfo('提示', '请输入数字', parent=self.window)  # 提示框
                    self.start_.config(text='开始刷课', state=tk.NORMAL)
            title_name = self.comboxlist.get()
            if int(speed) > 11:
                if querenkuang():
                    kaishi(speed,title_name)
                else:
                    self.start_.config(text='开始刷课', state=tk.NORMAL)
            else:
                kaishi(speed,title_name)
        else:
            tk.messagebox.showinfo('提示', '请选择课程', parent=self.window)  # 提示框
            self.start_.config(text='开始刷课', state=tk.NORMAL)
    # 监控在线情况
    def monitor(self):
        while True:

            try:
                global a_diengyi,data
                data = self._jia()

                if a_diengyi==1:

                    data['username']=str(self.username)  # 把用户名添加到发送里面
                    try:
                        responsejson = requests.post(data['url']+'/shuake_urser_logo.php?action=Online',headers=data['headers'],data=data,timeout=20).json()

                        if responsejson['status'] == '404':
                            tk.messagebox.showinfo('提示', '用户不存在', parent=self.TabStrip1)  # 提示框
                            self.exitc()
                    except:
                        tk.messagebox.showinfo('提示', '服务器故障', parent=self.TabStrip1)  # 提示框
                        self.exitc()  # 关闭python

            except:


                self.exitc()# 关闭python
            time.sleep(60)
if __name__=="__main__":
    try:
        Iswangluo = requests.get('https://www.baidu.com',timeout = 5).status_code==200
    except:
        Iswangluo = False


    Main = choa(Iswangluo)
    asyncio.run(Main.main())

    # cProfile.run('Main.main()')





