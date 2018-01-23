#coding:utf-8

import os
import shutil
import subprocess
import time
import argparse
import sys
import random

import numpy as np
from sklearn.metrics import precision_recall_fscore_support

import performance as pf
import train

def GetRandomNum(fname):
    res = []
    cont = open(fname, "r").readlines()   
    l2 = cont[0].strip().strip("\n").split()
    size = len(l2)
    for num in l2:
        res.append(int(num))   
    return res


def RunClassifier(dir, tdata, labels, aname, rname, cpath, taxid, fname, k):   
    ranSam = GetRandomNum(fname)
    labIndex = open(labels, "r").readlines()
    
    msize = int(len(ranSam) / k)
    dataset = open(tdata, "r").readlines()
    fmean = []
    for i in range(k):
        sfasta = ""
        qfasta = ""
        rlables = []
        l2 = ranSam[(i * msize):((i + 1) * msize)]
        
        for l3 in ranSam:
            temp = ""
            temp += str(dataset[int(l3) * 2]) + str(dataset[(int(l3) * 2) + 1])
            if l3 in l2:
                qfasta += temp
                rlables.append(int(labIndex[int(l3)].strip("\n")))
            else:
                sfasta += temp               
        
        spath = dir + "traindata.fa"
        qpath = dir + "querydata.fa"
        if os.path.exists(spath):
            os.remove(spath)
        if os.path.exists(qpath):
            os.remove(qpath)                      
        open(spath, "w").write(sfasta)
        open(qpath, "w").write(qfasta)
        outdir = dir + "newtrian" + os.sep
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.mkdir(outdir)
        
        traincmd = "java -Xmx8g -jar " + cpath + " train -o " + outdir + \
                    " -s " + spath + " -t " + taxid 
        subprocess.run(traincmd, shell=True, check=True)
        cpcmd = "cp " + dir + "rRNAClassifier.properties " + outdir
        subprocess.run(cpcmd, shell=True, check=True)
        classifycmd = "java -Xmx8g -jar " + cpath + " classify -t " + \
                        outdir + "rRNAClassifier.properties -o " + dir + \
                        "RDP_classify.txt " + qpath
        if os.path.exists(dir + "RDP_classify.txt"):
            os.remove(dir + "RDP_classify.txt")
        subprocess.run(classifycmd, shell=True, check=True)
        
        tmp = StatiRankAccu(dir, rname, dir + "RDP_classify.txt", rlables, aname)
        fmean.append(tmp)
    print(fmean)
    train.WritePerfo(fmean, dir + "RDP_train_results.txt")
        

def StatiRankAccu(dir, rname, pname, rlables, aname):
    stati = dict()
    abbr = dict()
    cont = open(rname, "r").readlines()
    anno = open(aname, "r").readlines()
    pcont = open(pname, "r").readlines()
   
    for row in cont:
        row = row.strip().strip("\n")
        row = row.split("\t")
        if row[0] not in stati.keys():
            stati.setdefault(row[0], {})
            abbr.setdefault(row[1], row[0])
            stati[row[0]][0] = 0
            stati[row[0]][1] = row[1]
            stati[row[0]][2] = 0
    
    if not len(pcont) == len(rlables):
        print("预测与实际的数量不匹配 预测 %d  实际 %d" % (len(pcont), len(rlables)))
        sys.exit(1)
    
    trueIndex = ""
    comStr = ""
    
    ltable = []
    pretb = []
    for vl in anno:
        ltable.append(vl.strip("\n") + ";")
    for i in range(len(pcont)):
        trueLable = anno[int(rlables[i])]
        trueIndex += str(trueLable.strip("\n")) + "\n"
        pretemp = pcont[i].strip("\n").split("\t\t")
        pretemp = pretemp[1]
        pretemp = pretemp.split("\t")
        preLable = []
        for t in range(0, len(pretemp), 3):
            if t > (len(pretemp) - 2):
                break
            rankTmp = []
            if pretemp[t + 1] in abbr.keys() and pretemp[t + 1] not in rankTmp:
                stmp = ""
                stmp += str(abbr[pretemp[t + 1]]) + "__" + pretemp[t]
                preLable.append(stmp) 
                rankTmp.append(pretemp[t + 1])
        """
        #comStr += str(trueLable.strip("\n")) + "\n"
        #comStr += str(pcont[i].strip("\n")) + "\n"
        
        for lb in preLable:
            comStr += str(lb) + ";"
        comStr += "\n"
        """
    
        trueLable = trueLable.strip("\n").split(";")
        
        pbList = ""   
        # warcup2 需要去掉种那一级的    
        for pb in range(len(preLable) - 1):
        #for pb in range(len(preLable)):
            pbList += preLable[pb] + ";"
        pretb.append(pbList)
        
        size = np.min([len(preLable), len(trueLable)])       
        for j in range(size):
            pl = preLable[j].split("__")
            tl = trueLable[j].split("__")
            if pl == tl:
                stati[pl[0]][0] += 1
            else:
                #如果高级分类错误则认为其之后的更低一级分类也错误
                break
        rankTmp = []
        for k in range(len(trueLable)):           
            tl = trueLable[k].split("__")
            if tl[0] not in rankTmp:
                stati[tl[0]][2] += 1
                rankTmp.append(tl[0])
            else:
                print(trueLable)
    predIndex = []
    for p in pretb:
        predIndex.append(ltable.index(p))
    #perfo = pf.performance(predIndex, rlables, "micro") 
    perfo = precision_recall_fscore_support(rlables, predIndex, average="micro")
    perfo = list(perfo[:(len(perfo) - 1)])
    #open(dir + "truelabels.txt", "a+").write(trueIndex)
    res = ""
    res += "等级" + "\t" + "正确" + "\t" + "总数" + "\t" + "正确率" + "\n"
    acc = []
    for key in stati:
        res += str(stati[key][1]) + "\t" + str(stati[key][0]) + "\t" + str(stati[key][2]) + "\t" 
        if stati[key][2] > 0:
            tmp = stati[key][0] / stati[key][2]
            acc.append(tmp)
            res += str(tmp)
        res += "\n"
    open(dir + "RDP_train_results.txt", "a+").write(res)
    
    #open(dir + "compare_label.txt", "w").write(comStr)
    perfo.extend(acc)
    return perfo

    
if __name__ == "__main__":
    
    #StatiRankAccu("RDP\\Warcup2\\", "RDP\\Warcup2\\deepRank.txt", "RDP\\Warcup2\\RDP_classify.txt", "RDP\\Warcup2\\RDP_classify.txt", "RDP\\Warcup2\\annotation.txt")
    
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="(必须的)输入文件，原始fasta文件")
    parser.add_argument("-l", "--labels", help="(必须的)输入文件，标签文件的数值化数据，标签的索引")
    parser.add_argument("-a", "--annotation", help="(必须的)输入文件，唯一标签列表")
    parser.add_argument("-r", "--deeprank", help="(必须的)输入文件，深度分类等级")
    parser.add_argument("-c", "--classifier", help="(必须的)，分类器路径")
    parser.add_argument("-t", "--taxid", help="(必须的)，分类器所需的taxid文件")  
    parser.add_argument("-f", "--randomnum", help="(必须的)，随机序列数")
    parser.add_argument("-k", "--kfold", help="(可选的)k折交叉模式，默认为10", type=int, default=10)  
    parser.add_argument("-o", "--outdir", help="(可选的)指定具体的输出目录，默认是输入文件目录或者当前目录")
    args = parser.parse_args()
    if not args.input:
        print(parser.print_help())
        sys.exit(1)
    if not args.labels:
        print(parser.print_help())
        sys.exit(1)
    if not args.annotation:
        print(parser.print_help())
        sys.exit(1)
    if not args.deeprank:
        print(parser.print_help())
        sys.exit(1)
    if not args.randomnum:
        print(parser.print_help())
        sys.exit(1)
    if not args.classifier:
        print(parser.print_help())
        sys.exit(1)
    if not args.taxid:
        print(parser.print_help())
        sys.exit(1)
    
    currDir = os.getcwd()
    args.input = args.input.strip()
    if not os.path.isfile(args.input) or not os.path.isfile(currDir + os.sep + args.input):
        print("*** 错误, %s 不存在.***"%(args.input))
        sys.exit(1)
    args.labels = args.labels.strip()
    if not os.path.isfile(args.labels) or not os.path.isfile(currDir + os.sep + args.labels):
        print("*** 错误, %s 不存在.***"%(args.labels))
        sys.exit(1)
    args.annotation = args.annotation.strip()
    if not os.path.isfile(args.annotation) or not os.path.isfile(currDir + os.sep + args.annotation):
        print("*** 错误, %s 不存在.***"%(args.annotation))
        sys.exit(1)
    args.deeprank = args.deeprank.strip()
    if not os.path.isfile(args.deeprank) or not os.path.isfile(currDir + os.sep + args.deeprank):
        print("*** 错误, %s 不存在.***"%(args.deeprank))
        sys.exit(1)
    args.randomnum = args.randomnum.strip()
    if not os.path.isfile(args.randomnum) or not os.path.isfile(currDir + os.sep + args.randomnum):
        print("*** 错误, %s 不存在.***"%(args.randomnum))
        sys.exit(1)
    args.classifier = args.classifier.strip()
    if not os.path.isfile(args.classifier) or not os.path.isfile(currDir + os.sep + args.classifier):
        print("*** 错误, %s 不存在.***"%(args.classifier))
        sys.exit(1)
    args.taxid = args.taxid.strip()
    if not os.path.isfile(args.taxid) or not os.path.isfile(currDir + os.sep + args.taxid):
        print("*** 错误, %s 不存在.***"%(args.taxid))
        sys.exit(1)
    if args.outdir:
        if not os.path.exists(args.outdir):
            try:
                args.outdir = args.outdir.strip()                        
                os.makedirs(args.outdir)
            except:
                print("***错误, %s 目录不存在，创建也不成功.***\n" %(v))
                print(parser.print_help())
                sys.exit(1)             
    else:           
        tmp = os.path.dirname(args.input)
        if not tmp == "":
            args.outdir = tmp
        else:
            args.outdir = currDir
    if not args.outdir.endswith(os.sep):
        args.outdir += os.sep
    res = ""
    res += "RDP分类器 " + str(args.kfold) +" 折交叉测试" + "\n"
    open(args.outdir + "RDP_train_results.txt", "a+").write(res)
    RunClassifier(args.outdir, args.input, args.labels, args.annotation, args.deeprank, args.classifier, args.taxid, args.randomnum, args.kfold)
    end = time.time()
    res = ""
    res += "总共用时：" + str(end - start) + " 秒" + "\n\n"
    open(args.outdir + "RDP_train_results.txt", "a+").write(res)
    
    
            