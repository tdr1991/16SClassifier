#coding:utf-8

import os
import sys
import shutil
import random
import time

import numpy as np


def SearchFiles(fileList, sDir="./", suffixName=""):
    """
    SearchFiles：搜索以suffixName为后缀的文件或所有的文件
    fileList：返回的文件列表
    sDir：文件夹路径，默认当前文件夹
    suffixName：文件后缀，默认为空
    """   
    if os.path.isdir(sDir):             
        for sChild in os.listdir(sDir):
            sChildPath = os.path.join(sDir,sChild)
            if os.path.isdir(sChildPath):
                SearchFiles(fileList, sChildPath, suffixName)
            else:    
                if suffixName == "":
                    fileList.append(sChildPath)
                else:
                    if os.path.splitext(sChildPath)[1] == suffixName :
                        fileList.append(sChildPath)
    else :
        errorInfo = "输入的路劲参数非文件夹"
        print(errorInfo)   

def SelectFiles(fsa, sDir):
    """
    SelectFiles：把fsa中的文件随机选择拷贝至sDir目录。此函数主要作用是选取少量样本用于编程测试用。
    fsa：序列文件的路径
    sDir：需拷贝到的目录
    """
    if not os.path.exists(sDir):
        os.makedirs(sDir)
    #去掉重复的元素
    fsa = list(set(fsa))
    size = len(fsa)  
    if size > 50:
        k = size / 100
        k = int(k) 
        select = random.sample(range(0, size - 1), k)   
        for i in select:           
            shutil.copy(fsa[i], sDir)
    else:
        for i in fsa:
            shutil.copy(i, sDir)

def RandomSelSeq(srcf, destf, n):
    """
    RandomSelSeq：从srcf文件随机选取2n行到destf文件
    """
    if os.path.exists(srcf):
        fp = open(srcf, "r")
        seq = fp.readlines()
        if (2 * n) > len(seq):
            n = int(len(seq) / 2)
        ranSam = random.sample(range(0, len(seq) - 1), n)
        ranSam = sorted(ranSam)
        subSeq = []        
        for i in ranSam:
            if i % 2 == 1:
                #避免重复选取，所以此法选取的序列未必是n条，条数 <=n
                if (i - 1) in ranSam:
                    continue
                subSeq.append(seq[i - 1])
                subSeq.append(seq[i])
            else:
                subSeq.append(seq[i])
                subSeq.append(seq[i + 1])
        
        fp = open(destf, "w")
        fp.writelines(subSeq)
        fp.close()

def DeleteDir(dir):
    """
    DeleteDir：删除dir目录及其文件和子目录。省去手动删除。
    """
    if os.path.exists(dir):
        filelist = []  
        filelist = os.listdir(dir)  
        for f in filelist:  
            filepath = os.path.join(dir, f)  
            if os.path.isfile(filepath):  
                os.remove(filepath)  
            elif os.path.isdir(filepath):  
                shutil.rmtree(filepath,True)
        shutil.rmtree(dir, True) 
 
def WriteMapFile(fileName, content):
    """
    WriteMapFile：创建map文件
    fileName：文件路径
    """ 
    fp = open(fileName, "a+")
    fp.write(content)
    fp.close()    

def IsInclude(lt, arr):
    """
    IsInclude：判断lt是否存在于arr中，存在则返回索引，可以视为真，不存在返回-1，可以视为假
    """
    for i in range(len(arr)):
        col = arr[i]
        col = col[1:]
        if IsEqual(lt, col):
            return i
    return -1


def DictToString(info, s):
    """
    DictToString：将字典转成字符串
    """
    for i in info:
        s += str(info[i])
        s += "\t"
    s += "\n"  
    return s


def TwoArrToStr(arr, s):
    """
    TwoArrToStr：将数组转成字符串
    """
    #arr = np.array(arr)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            s += str(arr[i][j])
            s += "\t"
        s += "\n"
    return s

def IsEqual(lt1, lt2):
    """
    IsEqual：判断两个列表是否相等
    """
    res = True
    if len(lt1) == len(lt2):
        for i in range(len(lt1)):
            if lt1[i] != lt2[i]:
                res = False
                break
    else:
        res = False
    return res

def ProcessData(dataDir):
    """
    GetMapInfo：获取序列的描述信息
    dataDir：包含16S rRNA核酸序列的原始文件的目录
    """
    seqPath = ["V1-V3_seq.fsa", "V3-V5_seq.fsa", "V6-V9_seq.fsa"]
    prefixDir = "proinfo/" 
    if not os.path.exists(prefixDir):
        os.makedirs(prefixDir)
    for n in range(len(seqPath)):
        seqPath[n] = prefixDir + seqPath[n]      
    smapPath = prefixDir + "sample_map.tsv"
    mapSample = "mID\tSampleID\tBarcode\tPrimer\tSubject\tBodySite\tCenter\n"
    seqMapPath = ["V1-V3_map.tsv", "V3-V5_map.tsv", "V6-V9_map.tsv"]
    V13MapCon = "sID\tmID\tseq_len\n"
    V35MapCon = "sID\tmID\tseq_len\n"
    V69MapCon = "sID\tmID\tseq_len\n"
    for i in range(len(seqMapPath)):
        seqMapPath[i] = prefixDir + seqMapPath[i]        
    infoPath = prefixDir + "info.tsv"
    wholeInfo = "Region\ttotal_num\tseq_min\tseq_max\tseq_total\tseq_mean\tseq_std\tseq_var\n"
    V13Info = {"total_num":0, "seq_min":sys.maxsize, "seq_max":-1, "seq_total":0, "seq_mean":0, "seq_std":0, "seq_var":0}
    V35Info = {"total_num":0, "seq_min":sys.maxsize, "seq_max":-1, "seq_total":0, "seq_mean":0, "seq_std":0, "seq_var":0}
    V69Info = {"total_num":0, "seq_min":sys.maxsize, "seq_max":-1, "seq_total":0, "seq_mean":0, "seq_std":0, "seq_var":0}
    #存储每个区文件的路径
    V13fl = []
    V35fl = []
    V69fl = []
    mapContent = []   
    V13SeqCon = ""
    V35SeqCon = ""
    V69SeqCon = ""
    V13SeqLen = []
    V35SeqLen = []
    V69SeqLen = []
    fsaList = []
    SearchFiles(fsaList, dataDir, ".fsa")
    #此值是唯一的，表示sample_map文件中的每一行
    mID = 0
    lastMap = []
    for fsa in fsaList:
        fp = open(fsa, "r")
        content = fp.readlines()
        for i in range(0, len(content), 2):     
            meta = {}  
            seqHeader = content[i].split()
            #获得每条序列的描述信息，由于源文件分隔符是空格，导致属性名与属性值不好分别
            for j in range(1, len(seqHeader) - 1):
                if "=" in seqHeader[j - 1] and "=" in seqHeader[j + 1] and "=" not in seqHeader[j]:
                    seqHeader[j - 1] = seqHeader[j - 1] + " " + seqHeader[j]                  
            for m in seqHeader:
                m = m.split("=")
                if len(m) > 1:
                    #采用字典更好把属性和值对应，列表可能就会乱
                    meta[m[0]] = m[1]           
            temp = [meta["sample"], meta["rbarcode"], meta["primer"], meta["subject"], meta["body_site"], meta["center"]]            
            smID = mID
            #如果lastMap == temp说明上条序列的描述与本条一致，不必对mID进行操作
            if not IsEqual(lastMap, temp):
                index = IsInclude(temp, mapContent)
                #序列描述不存在，需要写入文件
                if index < 0:
                    mID += 1                  
                    tl = [[]] * (len(temp) + 1)
                    tl[0] = mID
                    tl[1:] = temp
                    mapContent.append(tl)
                    smID = mID                   
                elif index > 0:
                    smID = mapContent[index][0]
            sequece = content[i + 1]
            if meta["primer"] == "V1-V3":
                V13Info["total_num"] += 1                
                sequece = sequece.strip()                
                size = len(sequece)
                V13MapCon += str(V13Info["total_num"]) + "\t" + str(smID) + "\t" + str(size) + "\n"
                V13SeqLen.append(size)               
                V13SeqCon += ">" + str(V13Info["total_num"]) + "\n" + sequece + "\n"
                V13fl.append(fsa)
            elif meta["primer"] == "V3-V5":
                V35Info["total_num"] += 1               
                sequece = sequece.strip()
                size = len(sequece)
                V35MapCon += str(V35Info["total_num"]) + "\t" + str(smID) + "\t" + str(size) + "\n"
                V35SeqLen.append(size)               
                V35SeqCon += ">" + str(V35Info["total_num"]) + "\n" + sequece + "\n"
                V35fl.append(fsa)
            elif meta["primer"] == "V6-V9":
                V69Info["total_num"] += 1
                sequece = sequece.strip()
                size = len(sequece)
                V69MapCon += str(V69Info["total_num"]) + "\t" + str(smID) + "\t" + str(size) + "\n"
                V69SeqLen.append(size)               
                V69SeqCon += ">" + str(V69Info["total_num"]) + "\n" + sequece + "\n"
                V69fl.append(fsa)
            lastMap = temp
        fp.close()
    if len(V13SeqLen) > 0:        
        arr = np.array(V13SeqLen)
        V13Info["seq_min"] = np.min(arr)
        V13Info["seq_max"] = np.max(arr)
        V13Info["seq_total"] = np.sum(arr)
        V13Info["seq_mean"] = np.mean(arr)
        V13Info["seq_std"] = np.std(arr)
        V13Info["seq_var"] = np.var(arr)
    wholeInfo += "V1-V3\t"
    wholeInfo = DictToString(V13Info, wholeInfo)
    if len(V35SeqLen) > 0:
        arr = np.array(V35SeqLen)
        V35Info["seq_min"] = np.min(arr)
        V35Info["seq_max"] = np.max(arr)
        V35Info["seq_total"] = np.sum(arr)
        V35Info["seq_mean"] = np.mean(arr)
        V35Info["seq_std"] = np.std(arr)
        V35Info["seq_var"] = np.var(arr)
    wholeInfo += "V3-V5\t"
    wholeInfo = DictToString(V35Info, wholeInfo)
    if len(V69SeqLen) > 0:
        arr = np.array(V69SeqLen)
        V69Info["seq_min"] = np.min(arr)
        V69Info["seq_max"] = np.max(arr)
        V69Info["seq_total"] = np.sum(arr)
        V69Info["seq_mean"] = np.mean(arr)
        V69Info["seq_std"] = np.std(arr)
        V69Info["seq_var"] = np.var(arr)
    wholeInfo += "V6-V9\t"
    wholeInfo = DictToString(V69Info, wholeInfo)
    WriteMapFile(infoPath, wholeInfo)
    mapSample = TwoArrToStr(mapContent, mapSample)
    WriteMapFile(smapPath, mapSample)
    WriteMapFile(seqMapPath[0], V13MapCon)
    WriteMapFile(seqMapPath[1], V35MapCon)
    WriteMapFile(seqMapPath[2], V69MapCon)
    WriteMapFile(seqPath[0], V13SeqCon)
    WriteMapFile(seqPath[1], V35SeqCon)
    WriteMapFile(seqPath[2], V69SeqCon)

    SelectFiles(V13fl, "ofsa")
    SelectFiles(V35fl, "ofsa")
    SelectFiles(V69fl, "ofsa")

if __name__ == "__main__":
    """
    start = time.time()
    DeleteDir("proinfo")
    DeleteDir("ofsa")
    ProcessData("HMPTRD")
    #ProcessData("testdata")
    RandomSelSeq("proinfo/V3-V5_seq.fsa", "V3-V5_sub_seq.fsa", 60000)
    end = time.time()
    print("总共用时：%d 秒" % (end - start))
    """
    RandomSelSeq("/home/yp.cai/tdr/HMP/HM16STR/RDP_old/11.5/k=5/all/process_data.fa", "/home/yp.cai/tdr/HMP/HM16STR/RDP_old/11.5/k=5/all/RDPsub.fa", 100000)
    
  
 
    
    
    