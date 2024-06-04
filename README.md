# LearningAssistance

目前支持 超星慕课
需要安装的环境 
requests pywin32 js2py BeautifulSoup4 pyDes

目前只能播放视频，不能自动答题，目前没有题库

视频倍速播放，比如视频100分钟，速度设置50，视频播放是前面50分钟时正常速度，到了50分钟的时候直接发送完成请求，结束视频播放自动跳到下一个视频

打包方式
_**pyinstaller -F -w -i  .\images\Bpp3.ico .\1.2.3.py -n ./1.2.3输出名称.exe**_

