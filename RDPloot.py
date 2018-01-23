#coding:utf-8

import os
import shutil
import subprocess
import time
import argparse
import sys
import random
from copy import deepcopy

import numpy as np

import RDPclassifier

def RunLoot(dir, tdata, labels, aname, rname, cpath, taxid):   
    rlables = []
    labIndex = open(labels, "r").readlines()  
    for ind in labIndex:
        rlables.append(int(ind.strip("\n")))
    dataset = open(tdata, "r").readlines()
    lootpath = dir + "lootclassify.txt"
    for i in range(0, len(dataset), 2):
        subData = deepcopy(dataset)
        subData.remove(dataset[i])
        subData.remove(dataset[i + 1])
        sfasta = ""
        qfasta = ""
        qfasta += str(dataset[i].strip("\n")) + "\n" + str(dataset[i + 1].strip("\n"))
        for sd in subData:
            sfasta += str(sd.strip("\n")) + "\n"
        spath = dir + "subtraindata.fa"
        qpath = dir + "subquerydata.fa"
        if os.path.exists(spath):
            os.remove(spath)               
        if os.path.exists(qpath):
            os.remove(qpath)                      
        open(spath, "w").write(sfasta)
        open(qpath, "w").write(qfasta)
        
        outdir = dir + "subtrian" + os.sep
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.mkdir(outdir)
        
        traincmd = "java -Xmx8g -jar " + cpath + " train -o " + outdir + \
                    " -s " + spath + " -t " + taxid 
        subprocess.run(traincmd, shell=True, check=True)
        cpcmd = "cp " + dir + "rRNAClassifier.properties " + outdir
        subprocess.run(cpcmd, shell=True, check=True)
        
        subtemp = dir + "tempclassify.txt"
        
        classifycmd = "java -Xmx8g -jar " + cpath + " classify -t " + \
                        outdir + "rRNAClassifier.properties -o " + subtemp + \
                        " " + qpath
        if os.path.exists(subtemp):
            os.remove(subtemp)
        subprocess.run(classifycmd, shell=True, check=True)
        
        classify = ""
        clatemp = open(subtemp, "r").readlines()
        classify += clatemp[0].strip("\n") + "\n"
        open(lootpath, "a+").write(classify)   
    RDPclassifier.StatiRankAccu(dir, rname, lootpath, rlables, aname)


if __name__ == "__main__":
    
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="(必须的)输入文件，原始fasta文件")
    parser.add_argument("-l", "--labels", help="(必须的)输入文件，标签文件的数值化数据，标签的索引")
    parser.add_argument("-a", "--annotation", help="(必须的)输入文件，唯一标签列表")
    parser.add_argument("-r", "--deeprank", help="(必须的)输入文件，深度分类等级")
    parser.add_argument("-c", "--classifier", help="(必须的)，分类器路径")
    parser.add_argument("-t", "--taxid", help="(必须的)，分类器所需的taxid文件")   
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
    res += "RDP分类器留一法测试" + "\n"
    open(args.outdir + "RDP_train_results.txt", "a+").write(res)
    RunLoot(args.outdir, args.input, args.labels, args.annotation, args.deeprank, args.classifier, args.taxid)
    end = time.time()
    res = ""
    res += "总共用时：" + str(end - start) + " 秒" + "\n\n"
    open(args.outdir + "RDP_train_results.txt", "a+").write(res)
    
    
            