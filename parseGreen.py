#coding:utf-8

import os
import sys
import argparse

import parseBase

def ParseLables(dir, file):
    fp = open(file, "r")
    cont = fp.readlines()
    tax = dict()
    taxNO = dict()
    srctax = ""
    lsrctax = []
    currNO = 0
    anno = ""
    lanno = []
    taxID = ""
    statNum = {"k":0, "p":0, "c":0, "o":0, "f":0, "g":0, "s":0}

    for l1 in cont:
        l1 = l1.split("\t")
        l1[0] = l1[0].strip()
        l1[1] = l1[1].strip().strip("\n")  
        l2 = l1[1].split("; ")
        tmpTax = dict()
        for l3 in l2:
            l3 = l3.split("__")
            l3[0] = l3[0].strip()
            l3[1] = l3[1].strip().capitalize()
            if l3[1] == "":
                break
            tmpTax.setdefault(l3[0], l3[1])
            if l3[0] == "g":
                break
        if "g" not in tmpTax.keys():
            continue
        lastKey = ""
        rankDeep = 0
        for key in tmpTax.keys():           
            temp = dict()
            statNum[key] += 1
            rankDeep += 1
            if key in tax.keys():
                if tmpTax[key] in tax[key].keys():
                    lastKey = key 
                    continue           
            currNO += 1
            paraID = 0
            paraName = "Root"
            if not lastKey == "":               
                if tmpTax[lastKey] in tax[lastKey].keys():
                    paraID = tax[lastKey][tmpTax[lastKey]]["NO"] 
                    paraName = tmpTax[lastKey]
                    rankDeep = tax[lastKey][tmpTax[lastKey]]["deep"] + 1           
            temp["NO"] = currNO
            temp["paraID"] = paraID
            temp["deep"] = rankDeep
            temp["paraName"] = paraName
            tax.setdefault(key, {})[tmpTax[key]] = temp        
            lastKey = key      
        j = 0
        subTmp = ""
        lastKey = ""
        for key in tmpTax.keys():
            if not lastKey == "":
                if not tmpTax[lastKey] == tax[key][tmpTax[key]]["paraName"]:
                    break
            lastKey = key
            j += 1
            subTmp += str(key) + "__" + str(tmpTax[key])
            if j < len(tmpTax):
                subTmp += ";"
        if not j == len(tmpTax):
            continue      
        lsrctax.append(subTmp)
        taxNO.setdefault(l1[0], subTmp)
    lanno = list(sorted(set(lsrctax)))
    for st in lanno:
        anno += str(st) + "\n" 
    taxID += "0" + "*" + "Root" + "*" + "-1" + "*" + "0" + "*" + "rootrank" + "\n"
    stax = ""
    for key1 in tax.keys():
        deep, rank = KeyMapDeep(key1)
        for key2 in tax[key1].keys():
            NO = tax[key1][key2]["NO"]
            paraID = tax[key1][key2]["paraID"]
            deep = tax[key1][key2]["deep"]
            taxID += str(NO) + "*" + str(key2) + "*" + str(paraID) + "*" + str(deep) + "*" + str(rank) + "\n"
        
        stax += str(key1) + "\t" + str(len(tax[key1].keys())) + "\n"
    open(dir + "ranktax.txt", "w").write(stax)
    rankCount = ""
    deepRank = ""
    for key in statNum.keys():
        rankCount += str(key) + "\t" + str(statNum[key]) + "\n"
        deep, rname = KeyMapDeep(key)
        deepRank += str(key) + "\t" + str(rname) + "\n"
    open(dir + "deepRank.txt", "w").write(deepRank)
    open(dir + "rank_count.txt", "w").write(rankCount)
    open(dir + "97_otu_taxid.txt", "w").write(taxID) 
    open(dir + "annotation.txt", "w").write(anno)
    fp.close()
    return taxNO, lanno

def KeyMapDeep(key):
    if key == "k":
        return 1, "domain"
    elif key == "p":
        return 2, "phylum"
    elif key == "c":
        return 3, "class"
    elif key == "o":
        return 4, "order"
    elif key == "f":
        return 5, "family"
    elif key == "g":
        return 6, "genus"
    elif key == "s":
        return 7, "species"

def ParseGreen(dir, ffas, flab):
    """
    ParseRDP：解析RDP数据库的参考文件，获取标签并进行数值化
    """
    fp = open(ffas, "r")
    cont = fp.readlines()
    fasta = ""
    srctax = ""
    lsrctax = []
    perGenus = ""
    tmpGenus = dict()
    taxNO, lanno = ParseLables(dir, flab)
    for i in range(0,len(cont) - 1, 2):
        des = cont[i]
        des = des.strip().strip("\n")
        des = des[1:]
        if des in taxNO.keys():
            lsrctax.append(taxNO[des])
            srctax += str(taxNO[des]) + "\n"
            tmpTax = ""
            tmpTax += "Root" + ";"
            tax1 = taxNO[des].split(";")
            for k in range(len(tax1)):
                tax2 = tax1[k].split("__")
                if tax2[1].strip() == "":
                    break
                tmpTax += str(tax2[1].strip())
                if k < (len(tax1) - 1):
                    tmpTax += ";"
            fasta += str(cont[i].strip("\n")) + "\t" + tmpTax + "\n" + str(cont[i+1].replace("\n", "")) + "\n"        
    parseBase.WriteInfo(dir, lsrctax)  
    open(dir + "process_data.fa", "w").write(fasta)
    open(dir + "taxonomy.txt", "w").write(srctax)
    fp.close()    
 
if __name__ == "__main__":
    #ParseLables("GreenGene\\", "GreenGene\\97_otu_taxonomy.txt")
    #ParseGreen("GreenGene\\", "GreenGene\\97_otus.fasta", "GreenGene\\97_otu_taxonomy.txt")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", help="(必须的)输入文件(fasta格式)包含训练和测试序列，使用的是参考数据库")
    parser.add_argument("-l", "--lables", help="(必须的)输入文件(普通文本格式)包含训练和测试序列的标签，使用的是参考数据库。如果fasta文件包含序列标签，则可不给")
    parser.add_argument("-k", "--kmer", default=5, type=int, help="(可选的)kmer分词的k大小，默认k=5")
    parser.add_argument("-d", "--outdir", help="(可选的)指定具体的输出目录，默认是输入文件目录或者当前目录")
    args = parser.parse_args()
    if not args.fasta:
        print("请输入fasta文件")
        print(parser.print_help())
        sys.exit(1)
    if not args.lables:
        print("请输入lables文件")
        print(parser.print_help())
        sys.exit(1)
    currDir = os.getcwd()
    args.fasta = args.fasta.strip()
    if not os.path.isfile(args.fasta) or not os.path.isfile(currDir + os.sep + args.fasta):
        print("*** 错误, %s 不存在.***"%(args.fasta))
        sys.exit(1)
    args.lables = args.lables.strip()
    if not os.path.isfile(args.lables) or not os.path.isfile(currDir + os.sep + args.lables):
        print("*** 错误, %s 不存在.***"%(args.lables))
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
    ParseGreen(args.outdir, args.fasta, args.lables)
    parseBase.SeqDigitized(args.outdir, args.kmer)
   
    
        
