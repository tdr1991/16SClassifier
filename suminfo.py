#coding:utf-8
def Get_Fasta_Info(fname):
    fp = open(fname)
    meta = {}
    fsa = fp.readlines()
    count = len(fsa)
    for i in range(0, count, 2):
        
        sd = fsa[i].split("\t")
        ms = fsa[i + 1]
        for m in sd:
            m = m.split("=")
            if len(m) > 1:
                meta[m[0]] = m[1]
    outf = fname.split(".")[0]
    outf += ".tsv"
    fp = open(outf, "a")
    heads = "#"
    info = ""
    for key in meta:
        heads += key
        heads += "\t"
        info += meta[key]
        info += "\t"
    fp.writelines(heads)
    fp.writelines("\n")
    fp.writelines(info)
    fp.writelines("\n")
    fp.close()


if __name__ == "__main__":
    """
    Get_Fasta_Info("HMPTDR/SRS098218.fsa")
    fp = open("testdata/SRS066188.fsa", "a+")
    fp.write("\ntestdata\n")
    fp.close()
    
    import re
    if re.match("\d+$", "123424134"):
        print(True)
    else:
        print(False)
        
    a = [[1, 2, 3], [4, 5, 6]]
    if 5 in a[1]:
        print(True)
    else:
        print(False)
       
    if 10 > 0 and 10 < 20 and 30 < 25 < 50:
        print(True)
    else:
        print(False)
    
    dc = {"a":"1", "b":"2", "c":"7", "d":"100", "e":"145", "f":"25"}
    print(dc, type(dc))
    print(dc.values())
    dc = sorted(dc.items(), key=lambda d:d[1])
    print(dc, type(dc[1]), dc[1][1])
   
    lt = ["1", "5", "132", "24", "1000", "450"]
    lc = [lt[i] for i in range(len(lt))]
     
    print(lt, type(lt))
    
    lt.sort()
    print(lt, type(lt))
    
    for i in range(len(lc)):
        lc[i] = int(lc[i])
    lc.sort()
    print(lc, type(lc))
    print(lt, type(lt))
    """
    a = [1, 2, 3, 4, 5, 6]
    print(a[1:2])
 
