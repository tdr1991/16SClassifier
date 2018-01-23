#coding:utf-8

import argparse
import sys
import tempfile
import random
import math


import tensorflow as tf
import numpy as np

import gpuManager

def ReadDataFile(fname):
    """
    ReadFile：读取fname文件内容存入列表，文件以 \t 分隔，\n 换行 
    """
    fp = open(fname, "r")
    cont = fp.readlines()
    res = []       
    for line in cont:
        #line = line.split("\t")
        """如果行的最后一个元素是换行，则需要去掉"""
        if line[len(line) - 1] == "\n":
            line = line[:len(line) - 1]
        temp = []
        for element in line:
            temp.append(float(element))
        res.append(temp)
    fp.close()
    return res

def ReadLableFile(fname, anno):
    labIndex = open(fname, "r").readlines()
    res = []
    for z in range(len(labIndex)):
        tmp = [0 for k in range(len(anno))]
        labIndex[z] = labIndex[z].strip().strip("\n")
        index = labIndex[z]        
        tmp[int(index)] = 1
        res.append(tmp)
    return res

def RandomData(labelData, lname, trainSize, testSize, anno):
    """
    RandomData：从原始数据和标签中选取若干作为训练集和测试集
    dname：原始数据文件
    lname：标签文件
    """
    resData = labelData
    resLables = ReadLableFile(lname, anno)
    trainData = []
    trainLables = []
    testData = []
    testLables = []
    if (trainSize + testSize) > len(resData):
        print("选择用于训练和测试的数据比原始文件大，请重新选择合适大小")
        sys.exit(1)
    """
    ranSam = random.sample(range(len(resData)), trainSize + testSize)
    trainRan = ranSam[:trainSize]
    testRan = ranSam[trainSize:]
    for i in trainRan:
        trainData.append(resData[i])
        trainLables.append(resLables[i])
    for j in testRan:
        testData.append(resData[j])
        testLables.append(resLables[j])
    """
    resData = np.array(resData)
    resLables = np.array(resLables)
    trainData = resData[:trainSize]
    trainLables = resLables[:trainSize]
    testData = resData[trainSize:(trainSize + testSize)]
    testLables = resLables[trainSize:(trainSize + testSize)]
    return trainData, trainLables, testData, testLables


def Train(dir, trainData, trainLables, testData, batch_size, epochs):

    trainData = np.array(trainData)
    trainLables = np.array(trainLables)
    testData = np.array(testData)

    inputShape = np.shape(trainData)
    #print(inputShape)
    if len(inputShape) < 4:
        """
        如果输入数据是经过对抗生成网络处理的，那么是一个四维向量，如果没有则是一个三维的，需转成思维的
        """
        trainData = np.reshape(trainData, [-1, inputShape[1], inputShape[2], 1])
        inputShape = np.shape(trainData)
        testShape = np.shape(testData)
        testData = np.reshape(testData, [-1, testShape[1], testShape[2], 1])

    outputSize = np.shape(trainLables)[1]
    
    #如果在一个进程中循环调用该模型，会提示模型的内核已存在错误，因为模型定义了变量和命名
    #空间，此时程序并没有清空图，这些变量和命名空间仍存在，所以需要重置下
    tf.reset_default_graph()

    is_training = tf.placeholder(tf.bool)

    def leakyrule(x, alpha=0.2):
        return 0.5 * (1 + alpha) * x + 0.5 * (1 - alpha) * abs(x)

    def Classifier(x):
        with tf.variable_scope("Classifier"):
            
            x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)

            x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)
                       
            x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)

            x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)
            """
            x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)
            """
            x_dim = x.get_shape().as_list()
            print(x_dim)
            
            x = tf.reshape(x, shape=[-1, x_dim[1] * x_dim[2] * x_dim[3]])
            x = tf.layers.dense(x, 1024)
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)
            """
            x = tf.layers.dense(x, 1024)
            x = tf.layers.batch_normalization(x, training=is_training)
            x = leakyrule(x)
            """
            x = tf.layers.dense(x, outputSize)
        return x

    x = tf.placeholder(tf.float32, [None, inputShape[1], inputShape[2], inputShape[3]])

    y_ = tf.placeholder(tf.float32, [None, outputSize])

   
    y = Classifier(x)

    with tf.name_scope('loss'):
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)
        cross_entropy = tf.reduce_mean(cross_entropy)

    c_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope="Classifier")

    c_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS, scope="Classifier")
    
    with tf.control_dependencies(c_update_ops):
        train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy, var_list=c_vars)

    prediction = tf.nn.softmax(y)

    with tf.name_scope('accuracy'):
        correct_prediction = tf.equal(tf.argmax(prediction, axis=1), tf.argmax(y_, axis=1))
        correct_prediction = tf.cast(correct_prediction, tf.float32)
        accuracy = tf.reduce_mean(correct_prediction)

    y_op = tf.argmax(prediction, axis=1)

    init = tf.global_variables_initializer()

    #tensorflow在训练时默认占用所有GPU显存，通过设置 allow_growth，显存分配则按需求增长
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    num_gpus = 0
    sel_device = None
    if gpuManager.check_gpus():
        gm = gpuManager.GPUManager()
        num_gpus = gm.get_gpu_num()
        sel_device = gm.auto_choice()
    else:
        print("不存在GPU，将使用cpu")
        num_gpus = 0
        sel_device = tf.device("/cpu:0")

    with sel_device:
        with tf.Session(config=config) as sess:
            sess.run(init)
            for epo in range(epochs):
                trainSize = inputShape[0]  
                tbatchData = np.array([])
                lbatchData = np.array([])
                ptcount = int(math.ceil(trainSize / batch_size))
                for idx in range(ptcount):
                    s_index = idx * batch_size
                    e_index = (idx + 1) * batch_size
                    if e_index > trainSize:
                        e_index = trainSize
                        
                    if s_index < e_index:  
                        tbatchData = trainData[s_index:e_index]
                        lbatchData = trainLables[s_index:e_index]            
                        train_step.run(feed_dict={x: tbatchData, y_: lbatchData, is_training:True})
                print_freq = 5
                if epo + 1 == 1 or (epo + 1) % print_freq == 0:    
                    train_accuracy = accuracy.eval(feed_dict={ \
                        x: tbatchData, y_: lbatchData, is_training:True})                   
                    print('第 %d 轮, training accuracy %g' % (epo, train_accuracy))
                
            if num_gpus > 0: 
                testPre = Mutil_GPUS_Data(num_gpus, testData, sess, y_op, x, is_training)
            else:
                testPre = sess.run(y_op, feed_dict={x:testData, is_training:False})
    return testPre

#利用多GPU计算测试集，防止显存不足
def Mutil_GPUS_Data(num_gpus, testData, sess, y_op, x, is_training):
    testPre = None
    test_size = len(testData)
    psize = math.ceil(test_size / num_gpus)
    pre= [0 for k in range(num_gpus)]

    for i in range(num_gpus):
        start_idx = i * psize
        end_idx = (i + 1) * psize
        if end_idx > test_size:
            end_idx = test_size
        if start_idx < end_idx:
            ptData = testData[start_idx:end_idx]
            with tf.device("/gpu:%d" % i):
                ptsize = len(ptData)
                ptbatch = 200
                ptcount = int(math.ceil(ptsize / ptbatch))
                for idx in range(ptcount):
                    s_index = idx * ptbatch
                    e_index = (idx + 1) * ptbatch
                    if e_index > ptsize:
                        e_index = ptsize
                    if s_index < e_index: 
                        temp = sess.run(y_op, feed_dict={x: ptData[s_index:e_index], is_training:False})           
                        pre[i] = np.append(pre[i], temp)
    #print(pre)
    for p in range(len(pre)):
        #去除初始化时的第一个0
        pre[p] = pre[p][1:]
    #print(pre)
    testPre = AppendData(pre)
        
    return testPre

def AppendData(sdata):
    ddata = sdata[0]
    for j in range(1, len(sdata)):
        ddata = np.append(ddata, sdata[j])
    return ddata

def StatiRankAccu(dir, rname, pre, rlables, anno):
    stati = dict()
    cont = open(rname, "r").readlines()
    for row in cont:
        row = row.strip().strip("\n")
        row = row.split("\t")
        if row[0] not in stati.keys():
            stati.setdefault(row[0], {})
            stati[row[0]][0] = 0
            stati[row[0]][1] = row[1]
            stati[row[0]][2] = 0
    if not len(pre) == len(rlables):
        print("预测与实际的数量不匹配 预测 %d  实际 %d" % (len(pre), len(rlables)))
        sys.exit(1)
    preIndex = ""
    trueIndex = ""
    for i in range(len(pre)):
        preLable = anno[int(pre[i])]
        trueLable = anno[int(rlables[i])]
        preIndex += str(pre[i]) + " "
        trueIndex += str(rlables[i]) + " "
        preLable = preLable.strip("\n").split(";")
        trueLable = trueLable.strip("\n").split(";")
        size = np.min([len(preLable), len(trueLable)])
        for j in range(size):
            pl = preLable[j].split("__")
            tl = trueLable[j].split("__")
            if pl == tl:
                stati[pl[0]][0] += 1
            else:
                break
        for k in range(len(trueLable)):
            tl = trueLable[k].split("__")
            stati[tl[0]][2] += 1
    preIndex += "\n"
    trueIndex += "\n\n"
    open(dir + "compare.txt", "a+").write(preIndex + trueIndex)

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
    open(dir + "train_results_4.txt", "a+").write(res)
    return acc

