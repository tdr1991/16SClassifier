#coding:utf-8

import os
import re
import sys

import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')   #加上此句是指定matplotlib的backend为agg，否则默认的TkAgg通过ssh执行出错

import process_data


def GetSeqMap(file):
    """
    GetSeqMap：获取序列的map信息
    """
    seqMap = []
    if os.path.exists(file):
        fp = open(file, "r")
        content = fp.readlines()[1:]
        #将索引与编号统一
        seqMap = [0] * (len(content) + 1)
        for line in content:
            line = line.split("\t")
            if len(line) > 1:
                seqMap[int(line[0])] = int(line[1])
        fp.close()
    return seqMap

def GetSamMap(file):
    """
    GetSamMap：获取样本的map信息
    """
    samMap = []
    if os.path.exists(file):
        fp = open(file, "r")
        content = fp.readlines()[1:]
        #将索引与编号统一。循环创建是因为避免浅拷贝时修改某个元素导致整列发生改变       
        samMap = [[0 for i in range(2)] for i in range(len(content) + 1)]
        for line in content:
            line = line.split("\t")
            if len(line) > 1:                
                samMap[int(line[0])][0] = line[4]
                samMap[int(line[0])][1] = line[5]
        fp.close()
    return samMap

def GetListColUiq(lst, col):
    """
    GetListColUiq：获得二维某列的切片，返回的去重一维数组
    lst：二维列表
    col：列索引
    """
    sub = []
    for i in range(len(lst)):
        if col in range(len(lst[i])):
            sub.append(lst[i][col])
    sub = sub[1:]      
    sub = list(set(sub))
    return sub

def WriteField(fname, field):
    """
    WriteField：将field字段的值写入文件，其中的field字段值唯一且排序好的
    """
    fp = open(fname, "a+")
    fp.write(field)
    fp.close()

def ListToStr(lt):
    """
    ListToStr：将列表转成字符串
    """
    s = ""
    for i in range(len(lt)):
        s += str(lt[i]) + "\n"
    return s



def JudgePerSam(fname):
    """
    JudgePerSam：判断同一人的样本编号是否一样
    """
    samMap = []
    if os.path.exists(fname):
        fp = open(fname, "r")
        content = fp.readlines()[1:]
        #将索引与编号统一。循环创建是因为避免浅拷贝时修改某个元素导致整列发生改变       
        samMap = [[0 for i in range(2)] for i in range(len(content) + 1)]
        for line in content:
            line = line.split("\t")
            if len(line) > 1:                
                samMap[int(line[0])][0] = line[1]
                samMap[int(line[0])][1] = line[4]
        fp.close()
    person = GetListColUiq(samMap, 1)
    res = dict()
    for p in person:
        res[p] = []
    for i in range(1, len(samMap)):
        res[samMap[i][1]].append(samMap[i][0])
    ps = "列出所有同一个体不同的样本号\n"
    ps += "人体号\t样本号\n"
    for key in res.keys():
        res[key] = list(set(res[key]))
        if len(res[key]) > 1:
            ps += key + "\t"
            for cl in res[key]:
                ps += cl + "\t"
            ps += "\n"
    fp = open("statinfo/persam.txt", "w")
    fp.write(ps)
    fp.close()

def WriteLog(log):
    """
    WriteLog：将结果写入日志文件
    """
    fp = open("log.txt", "a+")
    fp.write(log)
    fp.close()

def GetPerBody(samMap):
    """
    GetPerBody：获得人体编号和人体部位信息
    """
    prefixDir = "statinfo/"
    if not os.path.exists(prefixDir):
        os.makedirs(prefixDir) 
    person = GetListColUiq(samMap, 0)
    person.sort()
    header = "统计个人的编号\n"
    fname = prefixDir + "person.txt"
    WriteField(fname, header)
    WriteField(fname, ListToStr(person))
    bodySites = GetListColUiq(samMap, 1)
    bodySites.sort()
    header = "统计人体的部位\n"
    fname = prefixDir + "bodySites.txt"
    WriteField(fname, header)
    WriteField(fname, ListToStr(bodySites))
    return person, bodySites

def GetFastaNo(file):
    """
    GetFastaNo: 获得fasta文件的序列编号
    """
    fno = []
    if os.path.exists(file):
        cont = open(file, "r").readlines()
        for i in range(0, len(cont), 2):
            head = cont[i].strip().strip("\n")
            if head.startswith(">"):
                fno.append(int(head[1:]))
    else:
        print("{} 文件不存在".format(file))
        sys.exit(1)
    return fno

def Descend(ad, sites):
    for i in range(len(ad) - 1):
        maxIndex = i
        for j in range(i + 1, len(ad)):
            if ad[maxIndex] < ad[j]:
                maxIndex = j
        if not (maxIndex == i):
            tmp = ad[i]
            ad[i] = ad[maxIndex]
            ad[maxIndex] = tmp
            tmp = sites[i]
            sites[i] = sites[maxIndex]
            sites[maxIndex] = tmp
    return ad, sites

def DrawSites(ad, sites, dis):
    ad, sites = Descend(ad, sites)
    width = 0.4  
    ind = np.linspace(0.5, len(ad) - 0.5, len(ad))  
    fig, ax = plt.subplots()
    plt.bar(ind, ad, width)
    plt.xticks(ind, sites, rotation=90) # x 轴刻度值逆时针旋转45度  
    plt.xlabel("Bodysites")
    plt.ylabel("#OTU")
    plt.title("each bodysite OTUs")
    plt.grid(True)  
    plt.tight_layout()
    #plt.show()  
    plt.savefig("statinfo/bs_{}.jpg".format(dis))  
    plt.close()  
"""
def DrawSites(ad, sites):
    ad, sites = Descend(ad, sites)
    width = 0.4  
    ind = np.linspace(0.5, len(ad) - 0.5, len(ad))  
    fig, ax = plt.subplots()
    plt.barh(ind, ad, width)
    #plt.xticks(ind, sites, rotation=90) # x 轴刻度值逆时针旋转45度
    plt.yticks(ind, sites)
    
    plt.ylabel("Bodysites")
    plt.xlabel("#OTU")
    plt.title("each bodysite OTUs")
    plt.grid(True)  
    #plt.show()  
    plt.savefig("statinfo/bs.jpg")  
    plt.close()  
"""
def DrawSamples(ad, sample, dis):
    #fig, ax = plt.subplot()
    x = range(len(sample))
    #x = range(30)
    plt.plot(x, ad)
    plt.xlabel("samples")
    plt.ylabel("#OTU")
    plt.title("each sample OTUs")
    plt.grid(True)  
    plt.tight_layout()
    #plt.show()  
    plt.savefig("statinfo/sp_{}.jpg".format(dis))  
    plt.close()  

def DrawSampleSites(ad, sample, sites, dis):
    ax = plt.subplot(111)
    x = range(len(sample))
    for i in range(len(ad)):
        plt.plot(x, ad[i], label="%s"%(sites[i]))
    plt.legend(loc="center", ncol=3, shadow=True)
    plt.xlabel("samples")
    plt.ylabel("#OTU")
    plt.title("each sample's bodysite OTUs")
    plt.grid(True)  
    plt.tight_layout()
    #plt.show()  
    plt.savefig("statinfo/spst_{}.jpg".format(dis))  
    plt.close()  

def DrawDistance(mp, ms, dis):
    fig, ax = plt.subplots()
    #dis = np.array(dis)
    x = np.linspace(0.01, dis[len(dis) - 1] + 0.02 , len(dis))
    #x = x / 100.0 
    plt.plot(x, mp, label="sample mean OTU")
    plt.plot(x, ms, label="sites mean OTU")
    plt.legend(loc="best", shadow=True)
    plt.xlabel("distance")
    plt.ylabel("#OTU")
    plt.title("mean OTUs")
    plt.grid(True)  
    plt.tight_layout()
    #plt.show()  
    plt.savefig("statinfo/disspst.jpg")  
    plt.close()  

"""   
def DrawDistance(mp, sp, ms, ss, dis):
    bar_width = 0.005
    fig, ax = plt.subplots()
    dis = np.array(dis)
    plt.bar(dis - bar_width / 2, mp, bar_width, yerr=sp, label="Sample")
    plt.bar(dis + bar_width / 2, ms, bar_width, yerr=ss, label="Bodysite")
    plt.legend(loc="best", shadow=True)
    plt.xlabel("Distance")
    plt.ylabel("mean OTU")
    plt.title("each sample's bodysite OTUs")
    plt.grid(True)  
    #plt.show()  
    plt.savefig("statinfo/disspst_{}.jpg".format(dis))  
    plt.close()  
"""
def ParseOTU(file, fsa):
    """
    ParseOTU：解析ES-Tree生成的聚类信息
    """
    if os.path.exists(file):
        #prefixDir = "statinfo/"
        prefixDir = "statinfo/"
        if not os.path.exists(prefixDir):
            os.makedirs(prefixDir)
        fp = open(file, "r")
        content = fp.readlines()
        size = len(content) 
        seqMap = GetSeqMap("proinfo/V3-V5_map.tsv")
        samMap = GetSamMap("proinfo/sample_map.tsv")               
        person, bodySites = GetPerBody(samMap)      
        fno = GetFastaNo(fsa) 
        #print(len(fno))
        dis = []
        mean_sam = []
        mean_sites = []
        for li in content:
            li = li.split("|")
            line = li[1:]     
            otuNum = 0
            ad = [[0 for i in range(len(person))] for i in range(len(bodySites))]
            adSam = [0 for i in range(len(person))]
            adSites = [0 for i in range(len(bodySites))]       
            for col in line:
                otuNum += 1
                pb = [[0 for i in range(len(person))] for i in range(len(bodySites))]                
                col = col.split(" ")
                for num in col:
                    #保证num都是数字型字符串
                    if re.match(r"\d+$", num):  
                        #print(num)  
                        seqID = fno[int(num)]
                        if seqID in range(len(seqMap)):                                                                
                            samID = seqMap[seqID]                                                 
                            if 0 < seqID < len(seqMap) and 0 < samID < len(samMap):
                                i = person.index(samMap[samID][0])
                                j = bodySites.index(samMap[samID][1])
                                if i in range(len(person)) and j in range(len(bodySites)):
                                    pb[j][i] += 1                        
                staRes = ""
                staRes += ">\t" + li[0] + "\t水平第\t" + str(otuNum) + "\t个OTU" + "\n"               
                pb = np.array(pb)
                sumSite = []
                for i in range(len(pb)):  
                    sumSite.append(np.sum(pb[i]))
                    if sumSite[i] > 0:
                        adSites[i] += 1
                    staRes += str(sumSite[i]) + " "                   
                    for j in range(len(pb[i])):
                        if pb[i][j] > 0:
                            ad[i][j] += 1
                        staRes += str(pb[i][j]) + " "
                    staRes += "\n"
                staRes += str(np.sum(sumSite)) + " "
                for j in range(len(pb[0])):
                    sumPerson = np.sum(pb[:, j])
                    if sumPerson > 0:
                        adSam[j] += 1
                    staRes += str(sumPerson) + " "                  
                staRes += "\n"
                otuName = prefixDir + li[0] + ".txt"
                sfp = open(otuName, "a+")
                sfp.write(staRes)
                sfp.close()
            adRes = ""
            adRes += "每个部位丰度的统计" + "\n"
            adRes += ">\t" + li[0] + "\t水平" + "\n" 
            ad = np.array(ad)
            for i in range(len(ad)):  
                adRes += str(np.max(ad[i])) + " "
                for j in range(len(ad[i])):                    
                    adRes += str(ad[i][j]) + " "
                adRes += "\n" 
            otuName = prefixDir + "abundance" + ".txt"
            sfp = open(otuName, "a+")
            sfp.write(adRes)
            sfp.close()
            DrawSites(adSites, bodySites, li[0])
            DrawSamples(adSam, person, li[0])
            DrawSampleSites(ad, person, bodySites, li[0])
            mean_sam.append(np.mean(adSam)) 
            mean_sites.append(np.mean(adSites))
            """
            mean_sam = np.mean(adSam)
            std_sam = np.std(adSam)
            mean_sites = np.mean(adSites)
            std_sites = np.std(adSites)
            """
            dis.append(float(li[0]))

        DrawDistance(mean_sam, mean_sites, dis)
            #break
        fp.close()

def ParseUC(file):
    """
    ParseUC：解析vsearch生成的聚类信息
    """
    if os.path.exists(file):
        prefixDir = "statinfo/"
        if not os.path.exists(prefixDir):
            os.makedirs(prefixDir)
        fp = open(file, "r")
        content = fp.readlines()
        size = len(content)        
        seqMap = GetSeqMap("proinfo/V3-V5_map.tsv")
        samMap = GetSamMap("proinfo/sample_map.tsv")       
        person, bodySites = GetPerBody(samMap)
        ucDict = dict()       
        for li in content:
            li = li.split("\t")
            if li[0] == "S" or li[0] == "H":
                #生成的ucDict是一个二维字典
                ucDict.setdefault(li[1], {})[len(ucDict[li[1]])] = int(li[8])           
        otuNum = 0 
        totalSeqID = ""  
        for key in ucDict.keys():
            otuNum += 1
            pb = [[0 for i in range(len(person))] for i in range(len(bodySites))]                           
            #按值排序，排序后数据类型改变，第二维变成列表，列表里的索引和值以元组存在
            ucDict[key] = sorted(ucDict[key].items(), key=lambda d:d[1])
            for lt in ucDict[key]:
                num = lt[1]
                totalSeqID += str(num) + "\t"  
                seqID = num
                if seqID in range(len(seqMap)):                                                                
                    samID = seqMap[seqID]                                                 
                    if 0 < seqID < len(seqMap) and 0 < samID < len(samMap):
                        i = person.index(samMap[samID][0])
                        j = bodySites.index(samMap[samID][1])
                        if i in range(len(person)) and j in range(len(bodySites)):
                            pb[j][i] += 1                        
            totalSeqID += "\n"
            staRes = ""
            staRes += ">\t" + "0.90" + "\t水平第\t" + str(otuNum) + "\t个OTU" + "\n"               
            for i in range(len(pb)):                    
                for j in range(len(pb[i])):
                    staRes += str(pb[i][j]) + "\t"
                staRes += "\n"
            staRes += "\n"
            otuName = prefixDir + "parseUC" + ".txt"
            sfp = open(otuName, "a+")
            sfp.write(staRes)
            sfp.close()  
        otuSeqID = prefixDir + "otuSeqID" + ".txt"       
        fp = open(otuSeqID, "w")
        fp.write(totalSeqID) 
        fp.close()

if __name__ == "__main__":
    """
    seqMap = GetSeqMap("info/V3-V5_sub_map.tsv")
    samMap = GetSamMap("info/sample_map.tsv")
    bodySites = list(set(samMap[1:]))
    """
    process_data.DeleteDir("statinfo")
    ParseOTU("subESTProRes/V3-V5_sub_seq_Clean.org.Clusters", "V3-V5_sub_seq.fsa")
    #st = "0.01"
    #print(float(st))
    """
    ParseUC("clusters.uc")
    pt = "proinfo/sample_map.tsv"
    JudgePerSam(pt)
    print()
    
    a = [5, 37, 1, 10, 100, 8, 6, 7]
    b = [5, 37, 1, 5, 7, 8, 6, 7]
    print(Descend(a, b))
    """
    """
    import numpy as np  
    import matplotlib.pyplot as plt  
    import matplotlib as mpl  
    
    def draw_bar(labels,quants):  
        width = 0.4  
        ind = np.linspace(0.5,9.5,10)  
        # make a square figure  
        fig = plt.figure(1)  
        ax  = fig.add_subplot(111)  
        # Bar Plot  
        ax.bar(ind,quants,width,color='green')  
        # Set the ticks on x-axis  
        ax.set_xticks(ind)  
        ax.set_xticklabels(labels, rotation=45)  
        # labels  
        ax.set_xlabel('Country')  
        ax.set_ylabel('GDP (Billion US dollar)')  
        # title  
        ax.set_title('Top 10 GDP Countries', bbox={'facecolor':'0.8', 'pad':5})  
        plt.grid(True)  
        plt.show()  
        #plt.savefig("bar.jpg")  
        plt.close()  
    
    labels   = ['USA', 'China', 'India', 'Japan', 'Germany', 'Russia', 'Brazil', 'UK', 'France', 'Italy']  
    
    quants   = [15094025.0, 11299967.0, 4457784.0, 4440376.0, 3099080.0, 2383402.0, 2293954.0, 2260803.0, 2217900.0, 1846950.0]  
    
    draw_bar(labels,quants)  
    """