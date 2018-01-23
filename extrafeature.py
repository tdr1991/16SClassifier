#coding:utf-8

import os
import threading
import math
import sys

def AcidDigit(acid):
    """
    注意序列中是否存在简并碱基
    """
    acid = acid.lower()
    if acid == "-":
        return [0, 0, 0, 0]
    elif acid == "a":
        return [1, 0, 0, 0]
    elif acid == "t":
        return [0, 1, 0, 0]
    elif acid == "g":
        return [0, 0, 1, 0]
    elif acid == "c":
        return [0, 0, 0, 1]
    elif acid == "n":
        return [0.25, 0.25, 0.25, 0.25]
    elif acid == "r":
        return [0.5, 0, 0.5, 0]
    elif acid == "y":
        return [0, 0.5, 0, 0.5]
    elif acid == "m":
        return [0.5, 0, 0, 0.5]
    elif acid == "k":
        return [0, 0.5, 0.5, 0]
    elif acid == "s":
        return [0, 0, 0.5, 0.5]
    elif acid == "w":
        return [0.5, 0.5, 0, 0]
    elif acid == "h":
        return [1. / 3, 1. / 3, 0, 1. / 3]
    elif acid == "b":
        return [0, 1. / 3, 1. / 3, 1. / 3]
    elif acid == "v":
        return [1. / 3, 0, 1. / 3, 1. / 3]
    elif acid == "d":
        return [1. / 3, 1. / 3, 1. / 3, 0]
    

def SeqDigit(seq):
    res = []
    for acid in seq:
        res.append(AcidDigit(acid))
    return res

def ThreadDigit(seqList):
    res = []
    for seq in seqList:
        res.append(SeqDigit(seq))
    return res

class DigitThread(threading.Thread):
    """
    DigitThread：threading.Thread 线程的子类，构造函数中调用父类构造函数，重写父类的 run 方法
    """
    def __init__(self, func, args=()):
        super(DigitThread, self).__init__()
        self.func = func
        self.args = args
    
    def run(self):
        self.result = self.func(self.args)
    
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def SeqIntercept(seq):
    res = []
    lenList = []
    for s in seq:
        lenList.append(len(s))
    #avg = math.ceil(sum(lenList) / len(lenList))
    avg = max(lenList)
    #avg = 1000
    for s in seq:
        if len(s) < avg:
            dif = avg - len(s)
            tmp = ""
            for i in range(dif):
                tmp += "-"
            res.append(s + tmp)
        else:
            res.append(s[:avg])
    return res

def WriteDigit(fasta, tsize=0, is_thread=True):
    if not os.path.exists(fasta):
        print("输入的fasta文件不存在")
        return

    fp = open(fasta, "r")
    cont = fp.readlines()
    seqs = []
    for i in range(0, len(cont), 2):
        seqs.append(cont[i + 1].strip("\n"))
    
    seqs = SeqIntercept(seqs)

    CheckLength(seqs)
    
    seqsDigit = []
    if is_thread:
        size = len(seqs)
        
        k = math.ceil(size / float(tsize))
        lt = []
        for j in range(k):
            sindex = j * tsize
            eindex = (j + 1) * tsize
            if eindex > size:
                eindex = size
            if sindex < eindex:
                t = DigitThread(ThreadDigit, args=(seqs[sindex:eindex]))
                lt.append(t)
                t.start()
        for t in lt:
            t.join()           
            temp = t.get_result()
            for sd in temp:
                seqsDigit.append(sd)  
    else:
        seqsDigit =  ThreadDigit(seqs)
    """
    print(type(seqsDigit))
    import numpy as np
    seqsDigit = np.array(seqsDigit)
    seqShape = np.shape(seqsDigit)
    if len(seqShape) < 3:
        seqsDigit = np.reshape(seqsDigit, [-1, seqShape[1], 4])
    print(seqsDigit.ndim)
    
    print(len(seqsDigit[0][0]))
    for i in range(len(seqsDigit)):
        for j in range(len(seqsDigit[i])):
            try:
                if len(seqsDigit[i][j]) != 4:
                    print("i= %d  j= %d" % (i, j))
                    break
            except TypeError:
                print("i= %d  j= %d" % (i, j))
                break
    """        
    return seqsDigit
    

def CheckLength(seqs):
    """
    CheckLength：检查比对序列是否长度一致
    """
    lenList = []
    for s in seqs:
        if len(s) not in lenList:
            lenList.append(len(s))
    if len(lenList) > 1:
        print("比对的序列长度不一致，请重新比对序列")
        sys.exit(1)
    else:
        print("序列长度一致 %d" % (lenList[0]))
if __name__ == "__main__":
    seqsDigit = WriteDigit("RDP\\RTS16\\process_data_sub.fa", 5000)   
    #print(seqsDigit) 





