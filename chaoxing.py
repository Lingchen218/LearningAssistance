# -- coding: utf-8 --
import asyncio

import requests,re,json,hashlib,time
from bs4 import BeautifulSoup
from urllib.parse import quote
from pyDes import des, PAD_PKCS5
import pyaes
import base64
import binascii
version = '1.2.3'


def pkcs7_padding(s, block_size=16):
    bs = block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs).encode()

def split_to_data_blocks(byte_str, block_size=16):
    length = len(byte_str)
    j, y = divmod(length, block_size)
    blocks = []
    shenyu = j * block_size
    for i in range(j):
        start = i * block_size
        end = (i + 1) * block_size
        blocks.append(byte_str[start:end])
    stext = byte_str[shenyu:]
    if stext:
        blocks.append(stext)
    return blocks

def encrypt(plaintext: str):
    ciphertext = b''

    cbc = pyaes.AESModeOfOperationCBC("u2oh6Vu^HWe4_AES".encode("utf8"), "u2oh6Vu^HWe4_AES".encode("utf8"))
    plaintext = plaintext.encode('utf-8')
    blocks = split_to_data_blocks(pkcs7_padding(plaintext))
    for b in blocks:
        ciphertext = ciphertext + cbc.encrypt(b)
    base64_text = base64.b64encode(ciphertext).decode("utf8")
    return base64_text


class chaoxing():
    def __init__(self,**kwargs):
        '''
        headers:成功登录的headers cookie头

        bofzhuangt_:tk 文字标签的播放状态更新

        start_:tk 开始刷课的按钮对象
        '''

        self.jia = kwargs["_jia"]()
        self.host_url = None
        self.logging = kwargs['logging']

        self._session = None

    def __int__(self):
        pass
    def login(self,user,password):
        self._session = requests.session()

        # 初始化heade 的 user-agent
        self._session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            "Sec-Ch-Ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        }


        try:
            busp = BeautifulSoup(self._session.get('http://www.chaoxing.com/', timeout=5).text, 'html.parser')
        except Exception as e:
            self.logging.error(e)
            return None
        url = busp.find('p', {'class': 'loginbefore'}).a.get('href')
        logo_url = 'https://' + re.findall('//(.*?)/', url)[0] + '/fanyalogin'


        data = {
            'fid': '-1',
            'uname': encrypt(user),
            'password': encrypt(password),
            't': True,
            "refer": "https%3A%2F%2Fi.chaoxing.com",
            "forbidotherlogin": 0,
            "validate": "",
            "doubleFactorLogin": 0,
            "independentId": 0
        }
        try:
            response = self._session.post(logo_url,  data=data, timeout=10)
            if response.json()["status"] == True:
                return True
            else:
                error = {
                    "chaoxing":response.json(),
                    "用户名":"用户名或密码错误"
                }
                self.logging.error(error)
                return False
        except Exception as e:
            self.logging.error(e)
            return False


    def getheaders(self):
        return self._session.headers
    def GetCookies(self):
        return self._session.cookies
    def huoqukecheng(self):
        # 旧接口
        indexs_url = 'https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courses/list'

        # 新接口post
        courselistdata_posturl = "https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courselistdata"
        _data = {
            "courseType": 1,
            "courseFolderId": 0,
            "query": "",
            "superstarClass": 0
        }

        _resp = self._session.post(courselistdata_posturl, data=_data)

        #  解析 html

        _soup = BeautifulSoup(_resp.text, "lxml")
        _raw_courses = _soup.select("#stuNormalCourseListDiv div")
        _course_list = list()
        for course in _raw_courses:
            if not course.select_one("a.not-open-tip"):
                _course_detail = {}
                if (course.attrs.get("id", None) == None):
                    continue
                _course_detail["id"] = course.attrs["id"]
                _course_detail["info"] = course.attrs["info"]
                _course_detail["roleid"] = course.attrs["roleid"]
                _course_detail["clazzId"] = course.select_one("input.clazzId").attrs["value"]
                _course_detail["courseId"] = course.select_one("input.courseId").attrs["value"]
                _course_detail["cpi"] = re.findall("cpi=(.*?)&", course.select_one("a").attrs["href"])[0]
                _course_detail["title"] = course.select_one("span.course-name").attrs["title"]
                _course_detail["desc"] = course.select_one("p.margint10").attrs["title"]
                _course_detail["teacher"] = course.select_one("p.color3").attrs["title"]
                _course_list.append(_course_detail)
        #  解析结束 html



        try:
            response = self._session.get(indexs_url)

            busp = BeautifulSoup(response.text,'html.parser')

            lilist = busp.findAll('div',{"class":"course-cover"})
        except Exception as e:
            self.logging.error(e)
            return  {}





        kec = {}
        # self.host_url = re.findall('//(.*?)/',url)[0]
        for i, ii in zip(lilist, range(0, len(lilist))):
            # print(i.find('div',{'class':'Mconright httpsClass'}).h3.a.get("title"))
            if not i.span:
                url = re.sub('amp;', '',    i.a.get('href'))
                kec[ii] = {i.next_sibling.next_sibling.h3.a.span.get("title"):url.strip()}
        return kec
    def huoquzhangjie(self,ke_cheng_url,msgbox):

        self.msgbox = msgbox
        self.ke_cheng_url = ke_cheng_url
        reg = 'courseid=(.*?)&'
        courseid = re.findall(reg, ke_cheng_url)[0]
        url = self._session.get(ke_cheng_url, allow_redirects=False).headers['Location']
        self.host_url = re.findall(r'://(.*?)/',ke_cheng_url)[0]


        url if url else self.logging.error("没有找到返回地址")

        reg = 'clazzid=(.*?)&'
        clazzid = re.findall(reg, url)[0]
        reg = 'cpi=(.*?)&'
        cpi = re.findall(reg, url)[0]
        url_data = {
            'courseid': courseid,
            'clazzid': clazzid,
            'cpi': cpi
        }
        url = 'https://mooc2-ans.chaoxing.com/mycourse/studentcourse'
        html = self._session.get(url, params=url_data,  allow_redirects=False)
        reg = 'var enc = "(.*?)";'
        enc = re.findall(reg, html.text)[0]
        sudu = BeautifulSoup(html.text, 'html.parser').findAll('span', {'class': 'catalog_points_yi'})
        fe = {}
        fe['cpi'] = cpi
        if len(sudu) > 0:
            for i, ii in zip(sudu, range(0, len(sudu))):  # 循环有多少没有任务点没有完成
                a_ = i.parent.parent.parent
                if a_.a:
                    name = a_.a.text.strip()
                else:
                    name = a_.findAll('a', {'class': 'clicktitle'})[0].text.strip()  # 视频的名称
                msgbox("添加到准备列表中   " + name)  # 输入用户日志
                str_usr = a_.parent.get('onclick')  # 进入播放页面的url
                reg = "'(.*?)'"
                idstr = re.findall(reg, str_usr)
                courseid = idstr[0]
                knowledgeId = idstr[1]
                clazzid = idstr[2]
                url = 'https://' + self.host_url + '/mycourse/studentstudy?chapterId=' + str(
                    knowledgeId) + '&courseId=' + str(courseid) + '&clazzid=' + \
                      str(clazzid) + '&enc=' + enc + '&mooc2=1'
                url = quote(url, 'utf-8')
                url = 'https://' + self.host_url + '/mycourse/transfer?moocId=' + str(courseid) + '&clazzid=' + str(
                    clazzid) + '&ut=s&refer=' + url
                reg = 'https://fystat-ans.chaoxing.com/log/setlog\?personid=(.*?)&'
                url_dtoken = url
                try:
                    html_bof = self._session.get(url_dtoken,  allow_redirects=False).headers[
                        'Location']  # 进入播放页面
                    # print("44",html_bof)
                    response_ = self._session.get(html_bof, )
                    if response_.status_code != 200:
                        continue
                    dtoken_ = re.findall(reg, response_.text)[0]  # 取得视频播放需要的参数
                except Exception as e:
                    pass
                    # print(html_bof)
                    # print(e)
                    # print(html_bof)

                reg = 'utEnc="(.*?)"'
                utEnc = re.findall(reg, response_.text)  # 自动答题需要
                if not utEnc:
                    # 权限不足，接口变更
                    continue
                utEnc = utEnc[0]
                reg = 'chapterId=(.*?)&courseId=(.*?)&clazzid=(.*?)&'
                # knowledgeid, courseId, clazzid = re.findall(reg, str_usr)[0]  # 返回播放视频需要的参数
                knowledgeid = knowledgeId
                courseId = courseid
                clazzid = clazzid
                url = 'https://' + self.host_url + '/knowledge/cards'  # 播放视频的url
                fq = {}
                for num in range(0, 5):  # 每个课程的探测深度
                    data_url = {
                        'clazzid': clazzid,
                        'courseid': courseId,
                        'knowledgeid': knowledgeid,
                        'num': num,
                    }
                    html = self._session.get(url, params=data_url).text
                    reg = 'mArg = ([{][\s\S.]*?);'
                    mArg = re.findall(reg, html)
                    # print(mArg[0])
                    if len(mArg) == 1:
                        mArg = json.loads(mArg[0])
                    if "attachments" in mArg:  # 如果有就说明有课程
                        for attachments, j in zip(mArg['attachments'], range(len(mArg['attachments']))):  # 循环一个章节有多少课程
                            if 'type' in attachments:
                                type = attachments['type']  # 类型
                                if type == 'video':  # 视频
                                    if 'job' in attachments:  # 视频没有播放
                                        jobid = attachments['jobid']  # 播放视频需要的
                                        headOffset = attachments.get('headOffset', 0)  # 上次视频播放进度
                                        otherInfo = attachments['otherInfo']
                                        objectid = attachments['property']['objectid']
                                        urls = 'https://' + self.host_url + '/ananas/status/' + objectid
                                        params = {
                                            '_dc': str(int(time.time() * 1000)),
                                            'flag': 'normal',
                                            # 'k':'29619' # 学习ID 暂时用不上
                                        }
                                        self.getheaders()['Referer'] = 'https://' + self.host_url


                                        req = self._session.get(urls, params=params,  timeout=10).json()



                                        uid = self.GetCookies().get("UID",None)
                                        ship_ = {}
                                        daand = {}
                                        daand[j] = {'clazzid': clazzid,
                                                    'jobid': jobid,
                                                    'objectid': objectid,
                                                    'duration': req['duration'],
                                                    'otherInfo': otherInfo,
                                                    'dtoken': dtoken_ + '/' + req['dtoken'],
                                                    'uid': uid,
                                                    'name': name,
                                                    'headOffset': headOffset,
                                                    }
                                        ship_['video'] = daand
                                        fe[ii] = fq[j] = ship_
                                elif type == 'workid':  # 答题
                                    if 'job' in attachments:
                                        knowledgeid = mArg['defaults']['knowledgeid']  # 答题需要的
                                        courseid = mArg['defaults']['courseid']  # 答题需要的
                                        clazzId = mArg['defaults']['clazzId']  # 答题需要的
                                        enc = attachments['enc']  # 答题需要的
                                        jobid_dati = attachments['jobid']  # 答题需要的

                                        workId = attachments['property']['workid']  # 答题需要的
                                        cpi = mArg['defaults']['cpi']
                                        ktoken = mArg['defaults']['ktoken']
                                        title = attachments['property']['title']  # 答题的标题
                                        dati = {}
                                        dati['workid'] = {
                                            'knowledgeid': knowledgeid,
                                            'courseid': courseid,
                                            'clazzId': clazzId,
                                            'enc': enc,
                                            'jobid_dati': jobid_dati,
                                            'workId': workId,
                                            'utEnc': utEnc,
                                            'cpi': cpi,
                                            'ktoken': ktoken,
                                            'title': title
                                        }
                                        fe[ii] = fq[j] = dati
                                    else:
                                        pass  # 可以尝试收集答案
                                elif type == 'document':  # 阅读pdf
                                    if 'job' in attachments:
                                        url = 'https://mooc1-1.chaoxing.com/ananas/job/document'
                                        data = {
                                            'jobid': attachments['jobid'],
                                            'knowledgeid': mArg['defaults']['knowledgeid'],
                                            'courseid': mArg['defaults']['courseid'],
                                            'clazzid': mArg['defaults']['clazzId'],
                                            'jtoken': attachments['jtoken'],
                                            '_dc': int(time.time() * 1000)
                                        }
                                        respon = self._session.get(url, params=data,
                                                              allow_redirects=False).url
                            else:
                                break
                    else:
                        break
            return fe
        else:
            return "当前课程已经完成"




    def goo_post(self, bofang, clazzId, userid, jobid, objectid, duration_, dtoken, otherInfo, name,**kwargs):
        self.logging.info('正在播放'+ name+" " + str(bofang) + "总时长" + str(duration_) )
        self.msgbox('正在播放: '+  name+" 已观看" + str(bofang) + "秒 总时长" + str(duration_) + "每隔60刷新一次，到完成时可能会重复几次")
        objectId = objectid
        zifu = "d_yHJ!$pdA~5"
        currentTimeSec = bofang * 1000
        duration = duration_ * 1000
        clipTime = '0_' + str(duration_)
        zz = "[%s][%s][%s][%s][%s][%s][%s][%s]" % (
            clazzId, userid, jobid, objectId, currentTimeSec, zifu, duration, clipTime)
        enc = hashlib.md5(zz.encode()).hexdigest()
        # print(str(kwargs.get('cpi')))

        url = 'https://'+self.host_url+'/multimedia/log/a/' + dtoken

        _t = int(time.time() * 1000)
        url_post = {
            'clazzId': clazzId,
            'playingTime': bofang,
            'duration': duration_,
            'clipTime': '0_' + str(duration_),
            'objectId': objectid,
            'otherInfo': otherInfo[0:otherInfo.find('&courseId=')],
            'courseId':otherInfo[otherInfo.find("&courseId=")+len("&courseId="):],
            'jobid': jobid,
            'userid': userid,
            'isdrag': '3',
            'view': 'pc',
            'enc': enc,
            'rt': '0.9',
            'dtype': 'Video',
            '_t': _t,

        }

        try:

            url = self._session.get(url, url_post)
            return url.json()['isPassed']
        except:
            self.logging.error("提交参数有误")
            return False
    def play_speed(self, speed,fe):
        '''
                :param speed: 播放速度1-100
                :return:
                '''
        # print(fe)
        if fe:
            for i, j in fe.items():
                # 播放视频
                if 'video' in j:  # 播放视频

                    for jj, x in j['video'].items():

                        i1 = x
                        duration = i1["duration"]  # 视频总秒数

                        videoendtime = int(duration - duration * (speed / 100))
                        clazzid = i1['clazzid']  # 课程的ID
                        userid = i1['uid']  # 用户ID
                        jobid = i1['jobid']
                        objectid = i1['objectid']
                        cpi = fe['cpi']
                        dtoken = i1['dtoken']  # 提交用的
                        otherInfo = i1['otherInfo']
                        name = i1['name']
                        ic = int(i1['headOffset']/1000)  # 当前视频播放的位置

                        while ic < duration:
                            bofang = ic
                            if videoendtime - bofang < 60:
                                # time.sleep(abs(videoendtime - bofang))  # 等待
                                while True:
                                    if self.goo_post(duration, clazzid, userid, jobid, objectid, duration,
                                                     dtoken,
                                                     otherInfo, name,cpi=cpi):
                                        break
                                break
                            else:
                                if self.goo_post(bofang, clazzid, userid, jobid, objectid, duration, dtoken,
                                                 otherInfo, name,cpi=cpi):
                                    self.logging.info('播放完毕' + str(name))

                                    break

                            ic += 60
                            time.sleep(60)  # 等待 65秒
                else:
                    self.logging.info('课程视频播放完毕')
                # 答题
                if 'workid' in j:  # 答题
                    x = j['workid']
                    data_url = {
                        'workId': x['workId'],
                        'jobid': x['jobid_dati'],
                        'knowledgeid': x['knowledgeid'],
                        'clazzId': x['clazzId'],
                        'enc': x['enc'],
                        'utenc': x['utEnc'],
                        'courseid': x['courseid'],
                        'api': '1',
                        'needRedirect': 'true',
                        'ut': 's',
                        'cpi':x['cpi'],
                        'ktoken':x['ktoken'],
                    }
                    self.get_Answer(data_url,x['title'])
                else:
                    self.logging.info("课程题目已完成")
    def get_Answer(self, data_url,title):
        '''获取题目
        '''
        # self.bofzhuangt_.config(text='正在答题  '+title)
        url = 'https://'+self.host_url+'/api/work'
        html = self._session.get(url, params=data_url,  allow_redirects=False).url
        url = self._session.get(html,  allow_redirects=False)
        url = url.headers['Location']
        url = self._session.get(url,  allow_redirects=False).headers['Location']
        html = self._session.get(url,  allow_redirects=False).text
        busp = BeautifulSoup(html, 'html.parser')
        sudo = busp.findAll('div', {'class': 'TiMu'})  # 题目的数量
        ti = {}
        for i in range(0, len(sudo)):
            ti[i] = {}
            reg = '【...】(.*?)</div>'
            title = re.findall(reg, html)[i]  # 题目
            title = re.sub('<span style="font-size:14px;font-family:&#39;Calibri&#39;,&#39;sans-serif&#39;">','', title)
            title = re.sub('<p>', '', title)
            title = re.sub('</p>', '', title)
            title = re.sub('&nbsp;',"",title)
            if title.find('<img') == -1:

                ti[i]['topic'] = title.strip()
                reg = '【(...)】'
                topic_type = re.findall(reg, html)[i]  # 题目类型
                ti[i]['topic_type'] = topic_type
                xuan = []
                if topic_type == '判断题':
                    xuan.append('')
                elif topic_type == '单选题':
                    ti1 = sudo[i].findAll('div')[2].findAll('li')
                    for ti11, isd in zip(ti1, range(0, len(ti1))):
                        # print(ti11.a.text)
                        xuan.append(ti11.find('a').text.strip())
                    pass
                elif topic_type == '多选题':
                    ti1 = sudo[i].findAll('div')[2].findAll('li')
                    for ti11, isd in zip(ti1, range(0, len(ti1))):
                        xuan.append(ti11.find('a').string.strip())
                ti[i]['ti'] = xuan  # 选项
                # print('题目', title)
                # print('选项',xuan)
                # print('题目类型',topic_type)
            else:
                stbb = re.findall('<img(.*?)/>', title)[0]
                title = re.sub('<img' + stbb + '/>', '', title)
                ti[i]['topic'] = title.strip()
                reg = '【(...)】'
                topic_type = re.findall(reg, html)[i]  # 题目类型

                ti[i]['topic_type'] = topic_type
                xuan = []
                if topic_type == '判断题':
                    xuan.append('')
                elif topic_type == '单选题':
                    ti1 = sudo[i].findAll('div')[2].findAll('li')
                    for ti11, isd in zip(ti1, range(0, len(ti1))):
                        xuan.append(ti11.find('a').string)
                    pass
                elif topic_type == '多选题':
                    ti1 = sudo[i].findAll('div')[2].findAll('li')
                    for ti11, isd in zip(ti1, range(0, len(ti1))):
                        xuan.append(ti11.find('a').string)
                ti[i]['ti'] = xuan  # 选项
        daan_op = self.daoru(ti)  # 获得到答案

        if daan_op:
            self.Answer(url, daan_op)
        else:
            self.logging.info("未找到答案")
    def daoru(self, ti):
        '''
        把题目提交到数据库查询有无答案 如果有答案找出答案序号 ABCD
        :param ti:
        :return:
        ///
        题目导入格式
        {
            0: {
            'topic': '“眼不见为净” ，这属于自我防御机制中的（  ）。',
            'topic_type': '单选题',
            'ti': ['投射', '否认', '隔离', '转移','补偿']
        }

        返回 {0: 'B'}
        ///
        '''

        topic = json.dumps(ti, ensure_ascii=False)

        url = self.jia['url']+'/shuake_urser_logo.php?action=topic'
        self.jia['topic'] = topic
        op = self._session.post(url, data=self.jia, timeout=25)  # 答案
        try:
            op = op.json()
            if op['0'] == '': # 没有答案
                # choa().fasongdata('超星刷课','没有答案')
                return False
            else:
                daan_op = {}
                for j, x in ti.items():
                    if x['topic_type'] == '单选题':

                        num = self.chin_get_str(x['ti'])[0]

                        daan_op[j] = chr(self.chin_get_str(x['ti']).index(self.chin_get_str(op[str(j)])) + 65)
                    if x['topic_type'] == '多选题':
                        ddaan = ""
                        for i in op[str(j)].split('&'):
                            if i != "":
                                ddaan += (chr(self.chin_get_str(x['ti']).index(self.chin_get_str(i)) + 65))
                        daan_op[j] = ddaan
                    if x['topic_type'] == '判断题':
                        daan_op[j] = op[str(j)].lower()
                return daan_op
        except Exception as e:
            self.logging.warning("获取答案失败" + str(e))
            return False
    def Answer(self, url, daan, kaoshi=False):
        '''构建答题请求
        url 答题页面
        daan 是服务器返回的答案
        kaoshi  默认是打章节测试的题目 如果是true就是 考试自动答题
        '''
        busp = BeautifulSoup(self._session.get(url).text, 'html.parser')
        # 进入考试自动答题
        if kaoshi:
            duoxuanti = 0
            dati_url = re.sub('keyboardDisplayRequiresUserAction=1&', '',
                              'https://'+self.host_url + busp.form.get('action') + '&tempSave=true')  # 提交答案的
            score = busp.find('input', {'name': re.compile('type(\d+)')}).input.get('name')
            kaishi = []
            if daan[0] == 'true':
                kaishi.append(('answer' + score[5:], daan[0]))
            elif daan[0] == 'false':
                kaishi.append(('answer' + score[5:], daan[0]))
            elif len(daan[0]) > 1:
                kaishi.append(('answers' + score[5:], daan[0]))
                for i in daan[0]:
                    kaishi.append(('answer' + score[5:], i))
            else:
                kaishi.append(('answer' + score[5:], daan[0]))
            # 判断为考试
            kaishi.append(('courseId', busp.findAll('input', {'id': 'courseId'})[0].get('value')))
            kaishi.append(('paperId', busp.findAll('input', {'id': 'paperId'})[0].get('value')))
            kaishi.append(('testPaperId', busp.findAll('input', {'id': 'testPaperId'})[0].get('value')))
            kaishi.append(('testUserRelationId', busp.findAll('input', {'id': 'testUserRelationId'})[0].get('value')))
            kaishi.append(('tId', busp.findAll('input', {'id': 'tId'})[0].get('value')))
            kaishi.append(('remainTime', busp.findAll('input', {'id': 'remainTime'})[0].get('value')))
            kaishi.append(('encRemainTime', busp.findAll('input', {'id': 'encRemainTime'})[0].get('value')))
            kaishi.append(('encLastUpdateTime', busp.findAll('input', {'id': 'encLastUpdateTime'})[0].get('value')))
            kaishi.append(('tempSave', busp.findAll('input', {'id': 'tempSave'})[0].get('value')))
            kaishi.append(('type', busp.findAll('input', {'id': 'type'})[0].get('value')))
            kaishi.append(('timeOver', busp.findAll('input', {'id': 'timeOver'})[0].get('value')))
            kaishi.append(('classId', busp.findAll('input', {'id': 'classId'})[0].get('value')))
            kaishi.append(('enc', busp.findAll('input', {'id': 'enc'})[0].get('value')))
            kaishi.append(('examsystem', busp.findAll('input', {'id': 'examsystem'})[0].get('value')))
            kaishi.append(('start', busp.findAll('input', {'name': 'start'})[0].get('value')))
            kaishi.append(('userId', busp.findAll('input', {'id': 'userId'})[0].get('value')))
            kaishi.append(('randomOptions', busp.findAll('input', {'id': 'randomOptions'})[0].get('value')))
            kaishi.append(('cpi', busp.findAll('input', {'id': 'cpi'})[0].get('value')))
            kaishi.append(('openc', busp.findAll('input', {'id': 'openc'})[0].get('value')))
            kaishi.append(('questionId', busp.findAll('input', {'id': 'questionId'})[0].get('value')))
            kaishi.append(('questionScore', busp.findAll('input', {'id': 'questionScore'})[0].get('value')))
            kaishi.append((score, busp.findAll('input', {'name': score})[0].get('value')))
            kaishi.append(('type' + score[5:], busp.findAll('input', {'name': 'type' + score[5:]})[0].get('value')))
            if busp.find('div', {'class': 'leftBottom'}).findAll('a')[2].get('class')[0] == 'saveYl01':
                response = self._session.post(dati_url[:-4], data=kaishi).json()
                if response['status'] == 'error':
                    self.logging.warning(response['msg'])# 是设置了限时提交
                elif response['status'] == 'success':
                    self.logging.warning("提交成功，考试结束")
                else:
                    self.logging.error("考试出现未知错误。请联系客服")
            else:
                response = self._session.post(dati_url, data=kaishi).json()
                st = re.findall('&start=(\d)', url)[0]
                st_str = '&start=' + str(int(st) + 1)
                url = re.sub('&start=' + st, st_str, url)
                self.kaoshi(url)
        else:
            # 下面是答章节测试的
            tijiao_data = []
            # try:# 构建post参数
            tijiao_data.append(('courseId', busp.findAll('input', {'id': 'courseId'})[0].get('value')))
            tijiao_data.append(('totalQuestionNum', busp.findAll('input', {'id': 'totalQuestionNum'})[0].get('value')))
            tijiao_data.append(('fullScore', busp.findAll('input', {'id': 'fullScore'})[0].get('value')))
            tijiao_data.append(('oldWorkId', busp.findAll('input', {'id': 'oldWorkId'})[0].get('value')))
            tijiao_data.append(('workRelationId', busp.findAll('input', {'id': 'workRelationId'})[0].get('value')))
            tijiao_data.append(('enc_work', busp.findAll('input', {'id': 'enc_work'})[0].get('value')))
            tijiao_data.append(('userId', busp.findAll('input', {'id': 'userId'})[0].get('value')))
            answertype = busp.findAll('input', {'id': re.compile('answertype')})  # 题目id
            answer_id = []
            for i in range(0, len(answertype)):
                answer_id.append(re.sub('answertype', '', answertype[i].get('id')))
            tijiao_data.append(('api', busp.findAll('input', {'id': 'api'})[0].get('value')))
            tijiao_data.append(('classId', busp.findAll('input', {'id': 'classId'})[0].get('value')))
            tijiao_data.append(('knowledgeid', busp.findAll('input', {'id': 'knowledgeid'})[0].get('value')))
            tijiao_data.append(('jobid', busp.findAll('input', {'id': 'jobid'})[0].get('value')))
            tijiao_data.append(('workAnswerId', busp.findAll('input', {'id': 'workAnswerId'})[0].get('value')))
            id_jihe = ''
            answercheck = ''
            for i, (x, j) in zip(answer_id, daan.items()):  # 遍历题目id 并把答案写入
                if j.isupper():
                    if len(j) > 1:
                        tijiao_data.append(
                            ('answertype' + i, 1))  # answertype123 登录0是 123是题目id  0是题目类型  0是单选题 1是多选题 3是判断题
                        tijiao_data.append(('answer' + i, j))  # 答案选项
                        for jsx in j:
                            tijiao_data.append(("answercheck" + i, jsx))
                    else:
                        tijiao_data.append(
                            ('answertype' + i, 0))  # answertype123 登录0是 123是题目id  0是题目类型  0是单选题 1是多选题 3是判断题
                        tijiao_data.append(('answer' + i, j))  # 答案选项
                else:
                    tijiao_data.append(
                        ('answertype' + i, 3))  # answertype123 登录0是 123是题目id  0是题目类型  0是单选题 1是多选题 3是判断题
                    tijiao_data.append(('answer' + i, j))  # 答案选项

                id_jihe = id_jihe + i + ","
            # print(answercheck)
            tijiao_data.append(('answerwqbid', id_jihe))

            url_data = {'classId': busp.findAll('input', {'id': 'classId'})[0].get('value'),'courseId': busp.findAll('input', {'id': 'courseId'})[0].get('value'),'_': self.jia['time']}
            url22 = 'https://'+self.host_url+'/work/validate'
            json = self._session.get(url22, params=url_data).json()
            # 构建get请求
            get_dizhi = 'https://'+self.host_url+'/work/' + busp.findAll('form', {'id': 'form1'})[0].get('action')
            headers = self.headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            try:
                try:
                    response = self._session.post(url=get_dizhi, data=tijiao_data,  allow_redirects=False).json()
                except Exception as e:
                    self.logging.error("答题出错" + str(e))
            except Exception as e:
                self.logging.error("此题可能已经完成" + str(e))
    def jiekou_Answer(self, topic):
        url_data = {
            'question': topic
        }
        url = 'https://erya.unixeno.com/home/index/search.html'
        url_post = 'https://cx.icodef.com/v2/answer?platform=cx'  # 超星插件答题接口
        data = {
            'topic[0]': '在公务信函里,署名宜为写信者全名。必要时,亦可同时署上其行政职务与职称、学衔。',
        }
        response = self._session.post(url_post, data=data).json()
        daanneirong = response
        daan_str = ''
        # for ji in daanneirong[0]['result'][0]['correct']:
        #     daan_str += ji['content']+'&'
        # print(daanneirong[0]['result'][0]['correct'][0]['content'])
        url_post = 'http://106.13.35.129/tiku.aspx'
        data = {
            '__VIEWSTATE': '/wEPDwUKLTY1ODc5MTg4OA8WAh4TVmFsaWRhdGVSZXF1ZXN0TW9kZQIBZGQwN1lgu9fYSP3ApJzXKP3BoHXck7HigDcmSmbdYOHntw==',
            '__VIEWSTATEGENERATOR': 'C2F6633C',
            '__EVENTVALIDATION': '/wEdAAPt6A0Rw8MgjCQ58v/THcI39XDtxOeWDVhUDB3OayhOrqPpJucgJILabyLcPgnZw+nOjxFHTftJnpMJIqIcNjmkHkeHxCwKK/xReqhl/00QEw==',
            'ctl00$ContentPlaceHolder1$gen': '查询',
            'ctl00$ContentPlaceHolder1$timu': '【单选题】如果在你的餐巾前有大、中、小、高脚杯四个杯子,应该分别装( )。'
        }
    def texty(self):
        print(self.chin_get_str(['nid你的', '我的，df', 'kk看kk', 'wid我的，dsf岁的法国，fgsdfg']))
    def chin_get_str(self, str_):
        regex_str = ".*?([\u4E00-\u9FA5]+).*?"
        retu = None
        if isinstance(str_, str):
            for i, j in zip(re.findall(regex_str, str_), range(0, 2)):
                if j > 0:
                    retu += i
                else:
                    retu = i
            return retu
        if isinstance(str_, list):
            str__ = []
            for list_str in str_:
                for i, j in zip(re.findall(regex_str, list_str), range(0, 2)):
                    if j > 0:
                        retu += i
                    else:
                        retu = i
                str__.append(retu)
            return str__
    def exam(self):

        # 进入考试需要的url
        # 拿到课程的url 然后进入考试查看有没有考试
        response = self._session.get(self.ke_cheng_url,allow_redirects=False).headers['Location']
        response = self._session.get(response,  allow_redirects=False)
        url = BeautifulSoup(response.text, 'html.parser').findAll('a', {'mode': 'yiji'})[1].get('data')
        classId = re.findall('classId=(.*?)&', url)[0]
        courseId = re.findall('courseId=(.*?)&', url)[0]
        url_data_yem = {
            'classId': classId,
            'courseId': courseId
        }
        url = 'https://'+re.findall('//(.*?)/', self.ke_cheng_url)[0] + url
        response = self._session.get(url,  allow_redirects=False)
        busp1 = BeautifulSoup(response.text, 'html.parser')
        cpi = busp1.findAll('input', {'name': 'cpi'})[0].get('value')
        busp = busp1.findAll('div', {'class': 'ulDiv'})[0].ul
        examId = ''
        for i in busp.findAll('li'):
            if i.findAll('strong')[0].get_text().strip() == "待做":
                self.logging.info("有考试")
                examId += str(re.findall(',(.*?),', i.findAll('a', {'class': 'aBtn bRed_1'})[0].parent.findAll('a', {
                    'href': 'javascript:void(0)'})[0].get('onclick'))[0])
            elif i.findAll('strong')[0].get_text().strip() == "待重考":
                examId += str(re.findall(',(.*?),', i.findAll('a', {'class': 'aBtn bRed_1'})[0].parent.findAll('a', {
                    'href': 'javascript:void(0)'})[0].get('onclick'))[0])
        if len(examId) > 1:
            url_data_yem['examId'] = examId
            url_data_yem['cpi'] = cpi
            url = 'https://mooc1-api.chaoxing.com/exam/phone/start'
            try:
                url = re.sub('&isphone=true', '', self._session.get(url, params=url_data_yem, allow_redirects=False).headers['Location'])  # 进入考试 # 如果进入不了看看时间或者另一场考试没有停止
                # 考试开始
                url = re.sub('protocol_v=1#INNER', '', url)
                url = re.sub('&ut=s', '', url)
                url = re.sub('&tag=1', '', url)
                url = re.sub('&source=0', '', url) + 'start=0'
                self.kaoshi(url)
            except Exception as e:
                self.logging.error(str(e))
        else:
            self.logging.info("没有待做的考试")
    def kaoshi(self, url):
        '''
        拿去题目并传入题库中查询 返回答案如果没有就返回false
        :param url: 进入考试地址的url
        :return:
        '''

        response = self._session.get(url).text  # 进入考试
        busp = BeautifulSoup(response, 'html.parser')
        ccs = 0
        topic_type = ''
        for i in busp.find('a', {'class': 'current'}).parent.previous_elements:
            if ccs == 1:
                topic_type += i
            ccs += 1
        anse = busp.find('div', {'class': 'Cy_TItle clearfix'}).div.p.get_text()  # 题目
        xuanxiang = []  # 选项
        if topic_type == '判断题':
            pass
        elif topic_type == "多选题":
            for i in busp.find('ul', {'class': 'Cy_ulTop w-top'}).findAll('li'):
                xuanxiang.append(i.div.a.p.get_text())
        elif topic_type == "单选题":
            for i in busp.find('ul', {'class': 'Cy_ulTop w-top'}).findAll('li'):
                xuanxiang.append(i.div.a.p.get_text())
        else:
            self.logging.error("题目类型是" + str(topic_type) + " 未知错误请联系客服")
        aic = {}
        aic[0] = {
            'topic': anse,
            'topic_type': topic_type,
            'ti': xuanxiang
        }
        daan = self.daoru(aic)
        if daan:
            self.Answer(url, daan, True)
        else:
            self.logging.info("没有找到答案")
if __name__=="__main__":
    # headers = chaoxinglogin('手机号','密码')
    #ke_cheng_url = "https://mooc1-1.chaoxing.com/visit/stucoursemiddle?courseid="
    #main = chaoxing(headers,ke_cheng_url)
    #zhangjie = main.play_speed(99)
    # chaoxi = chaoxing(headers,_jia=_jia)
    #print(chaoxi.huoqukecheng())
    ti = {0: {'topic': '“眼不见为净” ，这属于自我防御机制中的（  ）。', 'topic_type': '单选题', 'ti': ['投射', '否认', '隔离', '转移','补偿']}
          }
    # aaa = chaoxi.daoru(ti)
    url = 'https://mooc2-ans.chaoxing.com/mycourse/stu?courseid='
    def a(a):
        pass
    #print(chaoxi.huoqukecheng())
    #chaoxi.play_speed(1,fe)
