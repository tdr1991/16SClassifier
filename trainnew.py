#coding:utf-8

import math

import tensorflow as tf
import numpy as np

import gpuManager
import trainBase

def Weight(shape):
    init = tf.truncated_normal(shape, stddev = 0.1)
    return tf.Variable(init)

def Bias(shape):
    init = tf.constant(0.1, shape = shape)
    return tf.Variable(init)

def Conv1d(x, W):
    return tf.nn.conv1d(x, W, 1, "SAME")

def MaxPool_2x1(x):    
    return tf.layers.max_pooling1d(x, 2, 2)

def ConvFC(x, isize, osize, fcunits):
    with tf.name_scope("reshape"):
        x_new = tf.reshape(x, [-1, isize, 1])
    with tf.name_scope("conv1"):
        oshape = x_new.get_shape().as_list()[-1]
        W_conv1 = Weight([5, oshape, 32])
        b_conv1 = Bias([32])
        o_conv1 = tf.nn.relu(Conv1d(x_new, W_conv1) + b_conv1)
        
    with tf.name_scope("pool1"):
        o_pool1 = MaxPool_2x1(o_conv1)
    with tf.name_scope("conv2"):
        oshape = o_pool1.get_shape().as_list()[-1]
        W_conv2 = Weight([5, oshape, 64])
        b_conv2 = Bias([64])
        o_conv2 = tf.nn.relu(Conv1d(o_pool1, W_conv2) + b_conv2)
        
    with tf.name_scope("pool2"):
        o_pool2 = MaxPool_2x1(o_conv2)
    with tf.name_scope("fc1"):
        oshape = o_pool2.get_shape().as_list()
        oshape = oshape[-1] * oshape[-2]
        o_pool2_flat = tf.reshape(o_pool2, [-1, oshape])
        W_fc1 = Weight([oshape, fcunits])
        b_fc1 = Bias([fcunits])
        o_fc1 = tf.nn.relu(tf.matmul(o_pool2_flat, W_fc1) + b_fc1)
    with tf.name_scope("dropout"):
        keep_prob = tf.placeholder(tf.float32)
        o_fc1_drop = tf.nn.dropout(o_fc1, keep_prob)
    with tf.name_scope("fc2"):
        W_fc2 = Weight([fcunits, osize])
        b_fc2 = Bias([osize])
        y = tf.matmul(o_fc1_drop, W_fc2) + b_fc2
    return y, keep_prob

def leakyrule(x, alpha=0.2):
    return 0.5 * (1 + alpha) * x + 0.5 * (1 - alpha) * abs(x)

def Classifier(x, is_training, outputSize):
    with tf.variable_scope("Classifier"): 
        x_dim = x.get_shape().as_list()
        x = tf.reshape(x, [-1, x_dim[1], 1])
        x = tf.layers.conv1d(x, 8, 3, strides=2, padding="same")  
        x = tf.layers.batch_normalization(x, training=is_training)
        x = leakyrule(x)

        x = tf.layers.conv1d(x, 8, 3, strides=2, padding="same") 
        x = tf.layers.batch_normalization(x, training=is_training)
        x = leakyrule(x)
                    
        x = tf.layers.conv1d(x, 8, 3, strides=2, padding="same")   
        x = tf.layers.batch_normalization(x, training=is_training)
        x = leakyrule(x)

        x = tf.layers.conv1d(x, 8, 3, strides=2, padding="same") 
        x = tf.layers.batch_normalization(x, training=is_training)
        x = leakyrule(x)
        """
        x = tf.layers.conv2d(x, 8, 3, strides=(2, 1), padding="same")  
        x = tf.layers.batch_normalization(x, training=is_training)
        x = leakyrule(x)
        """
        x_dim = x.get_shape().as_list()
        print(x_dim)
        
        x = tf.reshape(x, shape=[-1, x_dim[1] * x_dim[2]])
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

def Train(dir, trainData, trainLables, testData, testLables, batch_size, epochs):
    trainData = np.array(trainData)
    trainLables = np.array(trainLables)
    testData = np.array(testData)
    testLables = np.array(testLables)
    isize = np.shape(trainData)[1]
    osize = np.shape(trainLables)[1]
    # Create the model
    hunits = 1000

    tf.reset_default_graph()

    x = tf.placeholder(tf.float32, [None, isize])
    y_ = tf.placeholder(tf.float32, [None, osize])
    
    is_training = tf.placeholder(tf.bool)

    #open(dir + "train_results.txt", "a+").write("新的卷积全连接模型\n")
    #y, keep_prob = ConvFC(x, isize, osize, hunits)

    y = Classifier(x, is_training, osize)

    with tf.name_scope("loss"):
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels = y_, logits = y)
    cross_entropy = tf.reduce_mean(cross_entropy)
    
    """
    with tf.name_scope("adm_optimizer"):
        train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    """

    c_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope="Classifier")

    c_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS, scope="Classifier")
    
    with tf.control_dependencies(c_update_ops):
        train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy, var_list=c_vars)

    prediction = tf.nn.softmax(y)

    with tf.name_scope("accuracy"):
        correct_prediction = tf.equal(tf.argmax(prediction, axis=1), tf.argmax(y_, axis=1))
        correct_prediction = tf.cast(correct_prediction, tf.float32)
        accuracy = tf.reduce_mean(correct_prediction)

    y_op = tf.argmax(prediction, axis=1)

    init = tf.global_variables_initializer()

    testPre = None

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
        with tf.Session() as sess:
            sess.run(init)
            
            for epo in range(epochs):
                trainSize = np.shape(trainData)[0]  
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
                    train_accuracy = accuracy.eval(feed_dict={x: tbatchData, y_: lbatchData, is_training:True})
                    print('第 %d 轮, training accuracy %g' % (epo, train_accuracy))
            #testPre = sess.run(y_op, feed_dict={x: testData, is_training:False})
            
            if num_gpus > 0: 
                testPre = trainBase.Mutil_GPUS_Data(num_gpus, testData, sess, y_op, x, is_training)
            else:
                testPre = sess.run(y_op, feed_dict={x:testData, is_training:False}) 
            
    return testPre





