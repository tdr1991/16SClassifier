#coding:utf-8

import os
import argparse
import sys

import parseBase

def GetRankTax(file):
    fp = open(file, "r")
    cont = fp.readlines()
    rankTax = dict()
    for row in cont:
        row = row.strip("\n")
        row = row.split("*")
        if len(row) >= 4:
            rank = row[4].strip("")
            if rank not in rankTax.keys():
                rankTax.setdefault(rank, {})    
            row[1] = row[1].strip() 
            if row[1] not in rankTax[rank].keys():
                abbre = RankAbbre(rank)
                rankTax[rank][row[1].strip()] = abbre                     
    return rankTax

def SearchTax(rankTax, tax, backRank):
    for key in rankTax:
        if tax in rankTax[key].keys() and key not in backRank:
            return key

def RankAbbre(rank):
    if rank == "rootrank":
        return "r"
    elif rank == "domain":
        return "d"
    elif rank == "phylum":
        return "p"
    elif rank == "subphylum":
        return "w"
    elif rank == "class":
        return "c"
    elif rank == "subclass":
        return "v"
    elif rank == "order":
        return "o"
    elif rank == "suborder":
        return "u"
    elif rank == "family":
        return "f"
    elif rank == "genus":
        return "g"
    elif rank == "species":
        return "s"

def ParseRDP(dir, ffas, frank):
    """
    ParseRDP：解析RDP数据库的参考文件，获取标签并进行数值化
    """
    fp = open(ffas, "r")
    cont = fp.readlines()
    fasta = ""
    srctax = ""
    lsrctax = []
    statNum = dict()
    rankTax = GetRankTax(frank)
    sdpTax = ""
    for key in rankTax.keys():
        statNum.setdefault(key, 0)
        tmpRank = RankAbbre(key)
        sdpTax += str(tmpRank) + "\t" + str(key) + "\n"
    open(dir + "deepRank.txt", "w").write(sdpTax)
    stax = ""
    for key in rankTax:
        stax += str(key) + "\t" + str(len(rankTax[key])) + "\n"
    open(dir + "ranktax.txt", "w").write(stax)
    for i in range(0, len(cont) - 1, 2):
        l1 = cont[i].strip("\n").split("\t")
        if len(l1) > 1:           
            l2 = l1[1].split(";")
            currTax = ""
            backRank = []
            # 对于 Warcup2 数据库去掉种一级分类，只到属这一级
            #l2 = l2[:len(l2) - 1]
            for k in range(len(l2)):
                l3 = l2[k].strip()
                rank = SearchTax(rankTax, l3, backRank)
                backRank.append(rank)
                abbre = RankAbbre(rank)
                statNum[rank] += 1
                currTax += str(abbre) + "__" + str(l3)
                if k < (len(l2) - 1):
                    currTax += ";"
            lsrctax.append(currTax)
            srctax += str(currTax) + "\n"
            fasta += str(cont[i]).strip("\n") + "\n" + str(cont[i + 1]).strip("\n") + "\n"                       
    rankCount = ""
    for key in statNum.keys():
        rankCount += str(key) + "\t" + str(statNum[key]) + "\n"   
    open(dir + "rank_count.txt", "w").write(rankCount)
    parseBase.WriteInfo(dir, lsrctax)
    open(dir + "process_data.fa", "w").write(fasta)
    open(dir + "taxonomy.txt", "w").write(srctax)
    fp.close()

if __name__ == "__main__":
    #rankTax = GetRankTax("RDP\\RTS16\\trainset16_db_taxid.txt")
    #ParseRDP("RDP\RTS16\\", "RDP\RTS16\\trainset16_022016.fa", "RDP\RTS16\\trainset16_db_taxid.txt")
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
    ParseRDP(args.outdir, args.fasta, args.rank)
    parseBase.SeqDigitized(args.outdir, args.kmer)
  
    
    
        
