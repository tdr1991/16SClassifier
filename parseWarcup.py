#coding:utf-8

import os
import argparse
import sys

import parseBase
import parseRDP

def ParseWarcup(dir, ffas, frank):
    """
    ParseRDP：解析RDP数据库的参考文件，获取标签并进行数值化
    """
    fp = open(ffas, "r")
    cont = fp.readlines()
    fasta = ""
    anno = ""
    lanno = []
    srctax = ""
    lsrctax = []
    perGenus = ""
    tmpGenus = dict()
    rankTax = parseRDP.GetRankTax(frank)
    stax = ""
    statNum = dict()
    sdpTax = ""
    for key in rankTax.keys():
        statNum.setdefault(key, 0)
        tmpRank = parseRDP.RankAbbre(key)
        sdpTax += str(tmpRank) + "\t" + str(key) + "\n"
    open(dir + "deepRank.txt", "w").write(sdpTax)
    for key in rankTax:
        stax += str(key) + ":" + str(len(rankTax[key])) + "\n"
    open(dir + "ranktax.txt", "w").write(stax)
    for i in range(0, len(cont) - 1, 2):
        l1 = cont[i].strip("\n").split("\t")
        if len(l1) > 1:
            l2 = l1[1].split(";")
            # 去掉种一级分类，只到属这一级
            l2 = l2[:len(l2) - 1]
            
            if l2[len(l2) - 1].strip("\"") in rankTax["genus"].keys():              
                totalTax = ""
                for col in l2:
                    totalTax += str(col).strip("\"") + "/"
                lsrctax.append(totalTax)
                srctax += str(totalTax) + "\n"
                fasta += str(l1[0]) + "\n" + str(cont[i + 1]).strip("\n") + "\n"                       
    lanno = list(sorted(set(lsrctax)))
    rankCount = ""
    for key in statNum.keys():
        rankCount += str(key) + "\t" + str(statNum[key]) + "\n"   
    open(dir + "rank_count.txt", "w").write(rankCount)
    for st in lanno:
        anno += str(st) + "\n"
    lables = []
    for lt in lsrctax:
        temptax = [0 for k in range(len(lanno))]
        index = lanno.index(lt)
        temptax[index] = 1
        lables.append(temptax)
    slabs = ""
    for lb in lables:
        for ns in lb:
            slabs += str(ns)
        slabs += "\n"
    open(dir + "lables.txt", "w").write(slabs)
    open(dir + "process_data.fa", "w").write(fasta)
    open(dir + "taxonomy.txt", "w").write(srctax)
    open(dir + "annotation.txt", "w").write(anno)
    fp.close()

if __name__ == "__main__":
    #rankTax = GetRankTax("RDP\\RTS16\\trainset16_db_taxid.txt")
    #ParseRTS("RDP\\RTS16\\", "RDP\\RTS16\\trainset16_022016.fa", "RDP\\RTS16\\trainset16_db_taxid.txt")
    #parseBase.SeqDigitized("RDP\\RTS16\\", 5)
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", help="(必须的)输入文件(fasta格式)包含训练和测试序列，使用的是参考数据库")
    parser.add_argument("-r", "--rank", help="(必须的)输入文件(普通文本格式)，各级的分类名和级别")
    parser.add_argument("-k", "--kmer", default=5, type=int, help="(可选的)kmer分词的k大小，默认k=5")
    parser.add_argument("-d", "--outdir", help="(可选的)指定具体的输出目录，默认是输入文件目录或者当前目录")
    args = parser.parse_args()
    if not args.fasta:
        print("请输入fasta文件")
        print(parser.print_help())
        sys.exit(1)
    if not args.rank:
        print("请输入rank文件")
        print(parser.print_help())
        sys.exit(1)
    currDir = os.getcwd()
    args.fasta = args.fasta.strip()
    args.rank = args.rank.strip()
    if not os.path.isfile(args.fasta) \
       or not os.path.isfile(currDir + os.sep + args.fasta) \
       or not os.path.isfile(args.rank) \
       or not os.path.isfile(currDir + os.sep + args.rank):
        print("*** 错误, %s 不存在.***"%(args.fasta))
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
        tmp = os.path.dirname(args.fasta)
        if not tmp == "":
            args.outdir = tmp
        else:
            args.outdir = currDir
    if not args.outdir.endswith(os.sep):
        args.outdir += os.sep
    parseBase.WriteFeature(args.outdir, args.kmer)
    ParseWarcup(args.outdir, args.fasta, args.rank)
    parseBase.SeqDigitized(args.outdir, args.kmer)
    
    
    
        
