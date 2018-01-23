import sys

import numpy as np

def confusion_matrix(pred, real):
    if not len(pred) == len(real):
        print("预测和真实长度不一致！无法做统计")
        sys.exit(1)
    print("预测长度：%d , 实际长度：%d" % (len(pred), len(real)))
    cm = {"TP":[], "FP":[], "TN":[], "FN":[]}
    unique = list(sorted(set(np.append(real, pred))))
    for v in unique:
        tp, fp, tn, fn = 0, 0, 0, 0
        for i in range(len(real)):
            if (real[i] == v) and (pred[i] == v):
                tp += 1
            elif (not real[i] == v) and (pred[i] == v):
                fp += 1
            elif (real[i] == pred[i]) and (not pred[i] == v):
                tn += 1    
            elif (not real[i] == pred[i]) and (not pred[i] == v):
                fn += 1
        cm["TP"].append(tp)
        cm["FP"].append(fp)
        cm["TN"].append(tn)
        cm["FN"].append(fn)
    #print(len(real))
    #print(cm)
    return cm

def precision_score(metrix, average = "micro"):
    """
    precision_score = tp / (tp + fp)
    """
    if  average == "micro":
        return (np.sum(metrix["TP"]) / (np.sum(metrix["TP"]) + np.sum(metrix["FP"])))   
    elif average == "macro":
        percla =  metrix["TP"] / np.add(metrix["TP"], metrix["FP"])
        return np.sum(percla) / len(percla)
    elif average == None:
        return (metrix["TP"] / np.add(metrix["TP"], metrix["FP"]))

def recall_score(metrix, average = "micro"):
    """
    recall_score = tp / (tp + fn)，召回率也称灵敏性
    """
    if  average == "micro":
        return (np.sum(metrix["TP"]) / (np.sum(metrix["TP"]) + np.sum(metrix["FN"])))   
    elif average == "macro":
        percla =  metrix["TP"] / np.add(metrix["TP"], metrix["FN"])
        return np.sum(percla) / len(percla)
    elif average == None:
        return (metrix["TP"] / np.add(metrix["TP"], metrix["FN"]))

def spcificity_score(metrix, average = "micro"):
    """
    spcificity_score = tn / (tn + fp) 
    """
    if  average == "micro":
        return (np.sum(metrix["TN"]) / (np.sum(metrix["TN"]) + np.sum(metrix["FP"])))   
    elif average == "macro":
        percla =  metrix["TN"] / np.add(metrix["TN"], metrix["FP"])
        return np.sum(percla) / len(percla)
    elif average == None:
        return (metrix["TN"] / np.add(metrix["TN"], metrix["FP"]))

def accuracy_score(metrix):
    """
    accuracy_score = (tp + tn) / (tp + fp + tn + fn)
    """
    acc = np.add(np.sum(metrix["TP"]), np.sum(metrix["TN"]))
    total = np.add(acc, np.add(np.sum(metrix["FP"]), np.sum(metrix["FN"])))
    return (acc / total)

def f1_score(metrix, average = "micro"):
    """
    f1_score = 2 * (precision * recall) / (precision + recall)
    """
    ps = precision_score(metrix, average)
    rs = recall_score(metrix, average)
    return (2 * (ps * rs) / (ps + rs))

def g_mean(metrix, average = "micro"):
    """
    g_mean = (spcificity * recall) ^ (1/2)
    """
    ss = spcificity_score(metrix, average)
    rs = recall_score(metrix, average)
    return np.sqrt(ss * rs)

def MCC(metrix):
    """
    MCC = (tp * tn - fp * fn) / (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn) ^ (1/2)
    """
    tp = np.sum(metrix["TP"])
    fp = np.sum(metrix["FP"])
    tn = np.sum(metrix["TN"])
    fn = np.sum(metrix["FN"])
    return (tp * tn - fp * fn) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    
def performance(pred, real, average = "micro"):
    """
    performance：返回所有的性能指标
    """
    cm = confusion_matrix(pred, real)
    print("总共类别：%d" % len(cm["TP"]))
    print("TP: %f" % np.sum(cm["TP"]))
    print("FP: %f" % np.sum(cm["FP"]))
    print("TN: %f" % np.sum(cm["TN"]))
    print("FN: %f" % np.sum(cm["FN"]))
    ps = precision_score(cm, average)
    rs = recall_score(cm, average)
    ss = spcificity_score(cm, average)
    acc = accuracy_score(cm)
    gm = g_mean(cm, average)
    fs = f1_score(cm, average)
    mcc = MCC(cm)
    return [ps, rs, ss, acc, gm, fs, mcc]

from sklearn.metrics import precision_score, accuracy_score, f1_score, recall_score, confusion_matrix, precision_recall_fscore_support
if __name__ == "__main__":
    real = [0, 1, 2, 0, 1, 2, 0, 0, 2, 1, 1]
    pred = [0, 2, 1, 0, 0, 1, 2, 0, 1, 1, 0]
    rs = recall_score(real, pred, average="micro")
    matrix = confusion_matrix(real, pred)
    ps = precision_score(real, pred, average="micro")
    prf = precision_recall_fscore_support(real, pred, average="micro")
    prf = list(prf[:(len(prf) - 1)])
    tmp = []
    print(tmp.append(rs))
    #prf.extend(tmp)

    print(prf)
    print(matrix)
    print(rs)
    print(ps)
    """
    #print(confusion_metrix(pred, real))
    cm = confusion_matrix(pred, real)
    
    ps = precision_score(cm, average="micro")
    ps = precision_score(cm, average="macro")
    ps = precision_score(cm, average=None)
    rs = recall_score(cm, average="micro")
    rs = recall_score(cm, average="macro")  
    rs = recall_score(cm, average=None)
    fs = f1_score(cm, average="micro")
    fs = f1_score(cm, average=None)  
    asc = accuracy_score(cm) 
    ss = spcificity_score(cm, average="macro")  
    
    gm = g_mean(cm, average=None)  
    
    #mcc = MCC(cm)
    print(gm)
    #print(3 * 2 - 1)
    """
    #print(performance(pred, real, "micro"))

