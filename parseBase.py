#coding:utf-8

import os
import argparse
import sys

def Permutation(s, iter):
    """
    Permutation：以iter为长度枚举集合s的所有排列
    s：集合，以16S rRNA为例，s="acgt"
    iter：排列元素的长度
    """
    s.lower()
    iter -= 1
    if iter:
        temp = Permutation(s, iter)
        res = []
        for t in temp:
            for c in s:
                res.append(t + c)
        return res
    else:
        res = []
        for c in s:
            res.append(c)
        return res

def WriteFeature(dir, k):
    """
    WriteFeature：将枚举的排列写入文件
    """
    res = Permutation("acgt", k)
    ftPath = dir + "feature.txt"
    fp = open(ftPath, "w")
    ft = ""
    for s in res:
        ft += s + "\n"
    fp.write(ft)
    fp.close()

def SeqDigitized(dir, k, block=10000):
    """
    SeqDigitized：将原始数据的序列数值化
    k：以 k 个字符为长度枚举序列的所有情况
    block：每block条序列执行一次文件写入
    """
    fp = open(dir + "feature.txt", "r")
    feature = []
    for f in fp.readlines():
        feature.append(f.strip().strip("\n"))
    fp = open(dir + "process_data.fa", "r")
    cont = fp.readlines()
    lseqDigit = []
    for i in range(0, len(cont), 2):
        i += 1
        line = cont[i].lower()
        temp = [0 for j in range(len(feature))]
        num = []
        """如果序列总长为N，则共有N-k+1种情况"""
        for n in range(len(line) - k + 1):
            if line[n:n + k] in feature:          
                num.append(feature.index(line[n:n + k]))
        for index in num:
            temp[index] = 1
        lseqDigit.append(temp)
        """每block条序列执行一次文件写入，主要考虑内存不够"""
        if (i % block) == 1:
            WriteDigit(dir, lseqDigit)
            lseqDigit = []
    """最后的序列数可能不是block的倍数"""
    WriteDigit(dir, lseqDigit)
    
def WriteDigit(dir, lseqDigit):
    seqDigit = ""
    for sd in lseqDigit:
        for d in sd:
            seqDigit += str(d)
        seqDigit += "\n"
    open(dir + "input_data.txt", "a+").write(seqDigit)
    
def WriteInfo(dir, lsrctax):
    lanno = list(sorted(set(lsrctax)))
    anno = ""
    for st in lanno:
        anno += str(st) + "\n"
    lables = []
    for lt in lsrctax:
        index = lanno.index(lt)
        lables.append(index)
    slabs = ""
    for lb in lables:
        slabs += str(lb)
        slabs += "\n"
    open(dir + "lables.txt", "w").write(slabs)
    open(dir + "annotation.txt", "w").write(anno)

