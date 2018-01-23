#coding:utf-8

import ftplib
import os
import zipfile
from urllib.parse import urlparse
import process_data
import threading

def DownloadFile(url, outDir, uname="anonymous", passw=""):
    """
    DownloadFile：从ftp服务器下载文件，默认匿名登录
    """
    res = urlparse(url)
    remote_host = res[1]
    remote_file = res[2]  
    fileName = os.path.basename(url)
    fileName = outDir + fileName
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    try:
        ftp = ftplib.FTP(remote_host)
    except (socket.error, socket.gaierror):
        print("ERROR cannot reach '%s'" % remote_host)
        return
    print("..Connected to remote_host '%s'.." %remote_host)
    try:
        ftp.login() #使用匿名账号登陆也就是anonymous
    except ftplib.error_perm:
        print("ERROR cannot login anonymously")
        ftp.quit()
        return
    print("...logged in as 'anonymously'...")
    try:#传一个回调函数给retrbinary() 它在每接收一个二进制数据时都会被调用
        ftp.retrbinary("RETR %s" % remote_file, open(fileName, "wb").write)
    except ftplib.error_perm:
        print("ERROR cannot remote_file '%s'" % remote_file)
        os.unlink(remote_file)
    else:
        print(".....Download '%s' to ....." % remote_file)
    ftp.quit()
    return fileName

def DecomZip(filePath):
    """
    DecomZip：解压zip文件
    """
    outDir = os.path.split(filePath)[0] 
    zipfiles = zipfile.ZipFile(filePath, "r")
    zipfiles.extractall(outDir)
    zipfiles.close()

def Count(content, speSta, scount):
    """
    Count：计数
    """
    for row in content:
        line = row.split("\t|\t")
        for key in speSta.keys():
            if line[0] in speSta[key].values():
                if key in scount.keys():
                    scount[key] += 1
                else:
                    scount.setdefault(key, 1)
                break

def StaTaxaNum(url):
    """
    StaTaxaNum：统计物种在各个分类水平上的数量
    1.从服务器下载物种分类文件(物种分类会有更新，所以程序去获取比较好)；
    2.解压压缩文件；
    3.对其中的nodes.dmp文件解析，输出相应的统计信息；
    4.删除下载压缩文件(可选)。
    """
    zipFile = "taxa/taxdmp.zip"
    """
    zipDir = "taxa" + os.path.sep
    zipFile = DownloadFile(url, zipDir)
    DecomZip(zipFile)
    """
    fpath = os.path.split(zipFile)[0] + os.path.sep + "nodes.dmp"
    if os.path.exists(fpath):
        fp = open(fpath, "r")
        speSta = dict()
        for row in fp.readlines():
            line = row.split("\t|\t")
            speSta.setdefault(line[2], {})[len(speSta[line[2]])] = line[0]
        npath = os.path.split(zipFile)[0] + os.path.sep + "names.dmp"
        if os.path.exists(fpath):
            scount = dict()
            fp = open(npath, "r")
            lcot = [{} for i in range(100)]
            content = fp.readlines()
            size = len(content)
            per = size // 99
            for i in range(100):
                first = i * per                      
                last = (i + 1) * per
                if last >= size:
                    last = size - 1            
                if first >= last:
                    break
                """
                Count(content[0:20000], speSta, scount)
                break
                """
                t = threading.Thread(target=Count, args=(content[first:last], speSta, lcot[i]))
                t.setDaemon(True)
                t.start()
            t.join()
            for sd in lcot:
                for key in sd.keys():
                    if key in scount.keys():
                        scount[key] += sd[key]
                    else:
                        scount.setdefault(key, sd[key])                   
            """
            for row in fp.readlines():
                line = row.split("\t|\t")
                for key in speSta.keys():
                    if line[0] in speSta[key].values():
                        if key in scount.keys():
                            scount[key] += 1
                        else:
                            scount.setdefault(key, 1)
                        break
            """
            s = "分类名\t数量\n"
            for key in scount.keys():
                s += key + "\t" + str(scount[key]) + "\n"    
            #wfpath = os.path.split(zipFile)[0] + os.path.sep + "taxastanum.txt"
            wfpath = "taxastanum.txt"
            fp = open(wfpath, "w")
            fp.write(s)
            fp.close()

if __name__ == "__main__":
    url = "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
    #url = "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt"
    #process_data.DeleteDir("taxa")
    StaTaxaNum(url)
    #process_data.DeleteDir("taxa")
