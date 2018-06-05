# coding=UTF-8
# get provider information by phoneNumber
from urllib2 import urlopen
import re

def getPageCode(url):
    try:
        file = urlopen(url,data=None, timeout=3)
        text = file.read()
        file.close()
    except:
        text=None
    #  text = text.decode("utf-8")   # depending on coding of source code responded
    return text

def parseString(src):
    pat = []
    pat.append('(?<=归属地：</span>).+(?=<br />)')
    pat.append('(?<=卡类型：</span>).+(?=<br />)')
    pat.append('(?<=运营商：</span>).+(?=<br />)')
    pat.append('(?<=区号：</span>)\d+(?=<br />)')
    pat.append('(?<=邮编：</span>)\d+(?=<br />)')
    pat.append("(?<=省份：</span>)<a.*?>(.*?)</a>(?=<br />)")
    pat.append("(?<=城市：</span>)<a.*?>(.*?)</a>(?=<br />)")

    item = []
    for i in range(len(pat)):
        m = re.search(pat[i], src)
        if m:
            if i == 5 or i == 6:
                v = m.group(1)
            else:
                v = m.group(0)
            item.append(v)
    return item

def bnc_getProvider(phoneNum):
    url = "http://www.sjgsd.com/n/?q=%s" % phoneNum
    text = getPageCode(url)
    if text :
      item = parseString(text)
    else:
        item =None
    # result.append((phoneNum, item))
    return item