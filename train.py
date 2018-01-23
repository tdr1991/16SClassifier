#coding:utf-8

import random
import os
import sys
import string
import argparse
from copy import deepcopy
import time

#过滤警告
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
from sklearn.metrics import precision_score, accuracy_score, f1_score, recall_score, confusion_matrix, precision_recall_fscore_support

import trainBase
import trainnew
import RNN
import BD_RNN
import rna_GAN
import extrafeature
import rna_DCGAN
import performance as pf

def GetRandomNum(dir):
    res = []
    cont = open(dir + "randomnum.txt", "r").readlines()   
    l2 = cont[0].strip().strip("\n").split()
    size = len(l2)
    for num in l2:
        res.append(int(num))   
    return res

def WritePerfo(fmean, fm):
    mt = np.mean(fmean, axis=0)
    vt = np.var(fmean, axis=0)
    st = np.std(fmean, axis=0)
    #[ps, rs, ss, acc, gm, fs, mcc]
    #results = "\t" + "ps" + "  " + "rs" + "  " + "ss" + "  " + "acc" + "  " + "gm" + "  " + "fs" + "  " + "mcc" + "\n"
    results = "\t" + "ps" + "  " + "rs" + "  " + "fs" + "\n"
    results += "平均" + "  "
    for j in range(len(mt)):
        results += str(mt[j]) + "  "
    results += "\n"
    results += "方差" + "  "
    for j in range(len(vt)):
        results += str(vt[j]) + "  "
    results += "\n"
    results += "标准差" + "  "
    for j in range(len(st)):
        results += str(st[j]) + "  "
    results += "\n"
    open(fm, "a+").write(results)

def KFoldCross(dir, dname, lname, uname, aname, rname, k, batch_size, epochs):
    
    resData = trainBase.ReadDataFile(dname)
    anno = open(aname, "r").readlines()
    resLables = trainBase.ReadLableFile(lname, anno)
    
    #ranSam = random.sample(range(len(resData)), len(resData))   
    """
    randomNum = ""
    for num in ranSam:       
        randomNum += str(num) + " "
    randomNum = randomNum.strip() + "\n"
    open(dir + "randomnum.txt", "w").write(randomNum) 
    """
    """
    anno = open(aname, "r").readlines()
    labelData = extrafeature.WriteDigit(dname, 5000)
    labelData = np.array(labelData)
    #print(labelData.ndim)
    #print(np.shape(labelData))
    #unlabelData = extrafeature.WriteDigit(uname, 5000)
    resLables = trainBase.ReadLableFile(lname, anno)
    
    resData = labelData
    #msize = int(len(labelData) / k)  
    """
    #ranSam = GetRandomNum(dir)
    ranSam = random.sample(range(len(resData)), len(resData))   

    msize = int(len(resData) / k)  

    fmean = []

    for i in range(k):    
        trainData = []
        trainLables = [] 
        testData = [] 
        testLables = []  
        reIndex = ranSam[(i * msize):((i + 1) * msize)]  
        for ind in ranSam:
            if ind in reIndex:
                testData.append(resData[ind])
                testLables.append(resLables[ind])
            else:
                trainData.append(resData[ind])   
                trainLables.append(resLables[ind]) 

        #train_feature, test_feature = rna_DCGAN.Train(unlabelData, trainData, testData, batch_size, epochs)
    
        #pre = trainBase.Train(dir, train_feature, trainLables, test_feature, batch_size,  epochs)   
        
        #pre = trainBase.Train(dir, trainData, trainLables, testData, batch_size,  epochs)

        pre= trainnew.Train(dir, trainData, trainLables, testData, testLables, batch_size, epochs)

        rlables = np.argmax(testLables, axis=1)
        """
        precision = precision_score(rlables, pre, average="micro")
        accuracy = accuracy_score(rlables, pre)
        recall = recall_score(rlables, pre, average="micro")
        fscore = f1_score(rlables, pre, average="micro")
        matrix = confusion_matrix(rlables, pre)
        tp, fp = 0, 0
        print("预测类别： {}".format(len(set(pre))))
        print("实际类别： {}".format(len(set(rlables))))
        print("相加后的类别：{}".format(len(set(np.append(pre, rlables)))))
        print("类别：{}".format(len(matrix)))
        for j in range(len(matrix)):
            tp += matrix[j, j]
            if j == 0:
                fp += np.sum(matrix[(j + 1):, j])
                continue
            if j == (len(matrix) - 1):
                fp += np.sum(matrix[0:j, j])
                continue
            fp += np.sum(matrix[0:j, j]) + np.sum(matrix[(j + 1):, j])
        print("TP: {}".format(tp))
        print("FP: {}".format(fp))
            
        
        metrics = ""
        metrics += "precision" + "\t" + "accuracy" + "\t" + "recall" + "\t" + "fscore" + "\n"
        metrics += str(precision) + "\t" + str(accuracy) + "\t" + str(recall) + "\t" + str(fscore) + "\n"       
        open(args.outdir + "train_results_2.txt", "a+").write(metrics)
        """
        #tmp = pf.performance(pre, rlables, "micro")
        tmp = precision_recall_fscore_support(rlables, pre, average="micro")
        tmp = list(tmp[:(len(tmp) - 1)])
        acc = trainBase.StatiRankAccu(dir, rname, pre, rlables, anno)
        #tmp = [precision, accuracy, recall, fscore]
        
        tmp.extend(acc)
        fmean.append(tmp)
    print(fmean)
    WritePerfo(fmean, dir + "train_results_4.txt")
    

def RandomTest(dir, dname, lname, uname, aname, rname, trainSize, testSize, batch_size, epochs):
    anno = open(aname, "r").readlines()
    labelData = extrafeature.WriteDigit(dname, is_thread=False)
    unlabelData = extrafeature.WriteDigit(uname, is_thread=False)

    trainData, trainLables, testData, testLables = trainBase.RandomData(labelData, lname, trainSize, testSize, anno)
    
    train_feature, test_feature = rna_DCGAN.Train(unlabelData, trainData, testData, batch_size, epochs)
    
    pre = trainBase.Train(dir, train_feature, trainLables, test_feature, batch_size,  epochs)
    
    #pre = trainBase.Train(dir, trainData, trainLables, testData, batch_size,  epochs)
    rlables = np.argmax(testLables, 1)
    trainBase.StatiRankAccu(dir, rname, pre, rlables, anno)
    """
    for i in range(4):
        if i == 0:
            pre= trainnew.Train(dir, trainData, trainLables, testData, testLables, batch_size, epochs)
        else:
            pre = trainBase.Train(dir, trainData, trainLables, testData, testLables, batch_size, epochs, i)
        rlables = np.argmax(testLables, 1)
        trainBase.StatiRankAccu(dir, rname, pre, rlables, anno)
    #print(pre)
    """
    
       
def LOOTest(dir, dname, lname, aname, rname, batch_size, epochs):
    """
    LOOTest：leave-one-out测试模式，即每次从训练集中选取一条作为测试，其余作为训练
    """
    resData = trainBase.ReadDataFile(dname)
    anno = open(aname, "r").readlines()
    resLables = trainBase.ReadLableFile(lname, anno)
    rlables = np.argmax(resLables, 1)
    res = []
    for i in range(len(resData)):
        trainData = deepcopy(resData)   
        trainData.remove(trainData[i])

        trainLables = deepcopy(resLables)       
        trainLables.remove(trainLables[i])

        testData = [resData[i]]
        testLables = [resLables[i]]

        pre = trainBase.Train(trainData, trainLables, testData, testLables, batch_size, epochs)
        res.append(pre[0])    
    trainBase.StatiRankAccu(dir, rname, pre, rlables, anno)

if __name__ == "__main__":
    
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="(必须的)输入文件，fasta文件")
    parser.add_argument("-l", "--lables", help="(必须的)输入文件，标签文件的数值化数据，一连串 0/1值")
    parser.add_argument("-u", "--ufasta", help="(必须的)无标签序列文件，fasta文件")
    parser.add_argument("-a", "--annotation", help="(必须的)输入文件，唯一标签列表")
    parser.add_argument("-r", "--deeprank", help="(必须的)输入文件，深度分类等级")
    parser.add_argument("-m", "--model", help="(可选的)指定训练模式，如果给定训练集和测试集则可不给，默认0随机模式", type=int, default=0)
    parser.add_argument("-k", "--kfold", help="(可选的)k折交叉模式，默认为10", type=int, default=10)
    parser.add_argument("-t", "--trainsize", help="(必须的)训练集大小，如果是leave-one-out和k折交叉模式则可不给", type=int)
    parser.add_argument("-s", "--testsize", help="(必须的)测试集大小，如果是leave-one-out和k折交叉模式则可不给", type=int)
    parser.add_argument("-b", "--batchsize", help="(可选的)minibatch大小即每次更新权重处理的数据大小，默认80", type=int, default=80)
    parser.add_argument("-e", "--epochs", help="(可选的)epochs次数即全部数据集轮几次，默认20", type=int, default=20)
    parser.add_argument("-o", "--outdir", help="(可选的)指定具体的输出目录，默认是输入文件目录或者当前目录")
    args = parser.parse_args()
    if not args.input:
        print(parser.print_help())
        sys.exit(1)
    if not args.ufasta:
        print(parser.print_help())
        sys.exit(1)
    if not args.lables:
        print(parser.print_help())
        sys.exit(1)
    if not args.annotation:
        print(parser.print_help())
        sys.exit(1)
    if not args.deeprank:
        print(parser.print_help())
        sys.exit(1)
    if args.model == 0:
        if not args.trainsize:
            print(parser.print_help())
            sys.exit(1)
        if not args.testsize:
            print(parser.print_help())
            sys.exit(1)
    currDir = os.getcwd()
    args.input = args.input.strip()
    if not os.path.isfile(args.input) or not os.path.isfile(currDir + os.sep + args.input):
        print("*** 错误, %s 不存在.***"%(args.input))
        sys.exit(1)
    args.ufasta = args.ufasta.strip()
    if not os.path.isfile(args.ufasta) or not os.path.isfile(currDir + os.sep + args.ufasta):
        print("*** 错误, %s 不存在.***"%(args.ufasta))
        sys.exit(1)
    args.lables = args.lables.strip()
    if not os.path.isfile(args.lables) or not os.path.isfile(currDir + os.sep + args.lables):
        print("*** 错误, %s 不存在.***"%(args.lables))
        sys.exit(1)
    args.annotation = args.annotation.strip()
    if not os.path.isfile(args.annotation) or not os.path.isfile(currDir + os.sep + args.annotation):
        print("*** 错误, %s 不存在.***"%(args.annotation))
        sys.exit(1)
    args.deeprank = args.deeprank.strip()
    if not os.path.isfile(args.deeprank) or not os.path.isfile(currDir + os.sep + args.deeprank):
        print("*** 错误, %s 不存在.***"%(args.deeprank))
        sys.exit(1)
    if args.outdir:
        if not os.path.exists(args.outdir):
            try:
                args.outdir = args.outdir.strip()                        
                os.makedirs(args.outdir)
            except:
                print("***错误, %s 目录不存在，创建也不成功.***\n" %(args.outdir))
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
    res += "训练集大小：" + str(args.trainsize) + \
            "\t" + "测试集大小：" + str(args.testsize) + "\t" + "batchsiz：" + \
            str(args.batchsize) + "\t" + "epochs：" + str(args.epochs) + "\n"
    if args.model == 0:
        res = "随机训练模式" + "\t" + res
        #res += "只有分类器，无自编码器" + "\n"
        open(args.outdir + "train_results.txt", "a+").write(res)
        RandomTest(args.outdir, args.input, args.lables, args.ufasta, args.annotation, args.deeprank, args.trainsize, args.testsize, args.batchsize, args.epochs)
    elif args.model == 1:
        res = "留一法模式" + "\t" + res
        open(args.outdir + "train_results.txt", "a+").write(res)
        LOOTest(args.outdir, args.input, args.lables, args.annotation, args.deeprank, args.batchsize, args.epochs)
    elif args.model == 2:
        res += "k-mer分词" + "\n"
        res = str(args.kfold) + " 折交叉模式" + "\t" + res
        open(args.outdir + "train_results_4.txt", "a+").write(res)
        KFoldCross(args.outdir, args.input, args.lables, args.ufasta, args.annotation, args.deeprank, args.kfold, args.batchsize, args.epochs)
    end = time.time()
    res = ""
    res += "总共用时：" + str(end - start) + " 秒" + "\n\n"
    open(args.outdir + "train_results_4.txt", "a+").write(res)
    
    