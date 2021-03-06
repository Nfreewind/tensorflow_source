# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 16:37:08 2018

@author: lWX379138
"""
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

#环境重置
tf.reset_default_graph()

#导入MINST 数据集
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("data/",one_hot=True)

train_X = mnist.train.images
train_Y = mnist.train.labels
test_X  = mnist.test.images
test_Y  = mnist.test.labels

#定义占位符
n_input = 784
n_hidden_1 = 256    #第一层自编码

n_hidden_2 = 128    #第二层自编码
n_classes = 10

#占位符
#第一层输入
x = tf.placeholder("float",[None,n_input])
y = tf.placeholder("float",[None,n_input])
dropout_keep_prob = tf.placeholder('float')

#第二层输入
l2x = tf.placeholder("float",[None,n_hidden_1])
l2y = tf.placeholder("float",[None,n_hidden_1])

#第三层输入
l3x = tf.placeholder("float",[None,n_hidden_2])
l3y = tf.placeholder("float",[None,n_classes])

#定义学习参数
weights = {
    #网络1: 784-256-784
    'h1':tf.Variable(tf.random_normal([n_input,n_hidden_1])),
    'l1_h2':tf.Variable(tf.random_normal([n_hidden_1,n_hidden_1])),
    'l1_out':tf.Variable(tf.random_normal([n_hidden_1,n_input])),
    #网络2：256-128-256
    'l2_h1':tf.Variable(tf.random_normal([n_hidden_1,n_hidden_2])),
    'l2_h2':tf.Variable(tf.random_normal([n_hidden_2,n_hidden_2])),
    'l2_out':tf.Variable(tf.random_normal([n_hidden_2,n_hidden_1])),
    #网络3 128 - 10
    'out':tf.Variable(tf.random_normal([n_hidden_2,n_classes]))
}

biases = {
    'b1':tf.Variable(tf.zeros([n_hidden_1])),
    'l1_b2':tf.Variable(tf.zeros([n_hidden_1])),
    'l1_out':tf.Variable(tf.zeros(n_input)),
    
    'l2_b1':tf.Variable(tf.zeros([n_hidden_2])),
    'l2_b2':tf.Variable(tf.zeros([n_hidden_2])),
    'l2_out':tf.Variable(tf.zeros([n_hidden_1])),
    
    'out':tf.Variable(tf.zeros([n_classes]))
}

#第一层网络结构

#第一层的编码输出
l1_out = tf.nn.sigmoid(tf.add(tf.matmul(x,weights['h1']),biases['b1']))

#l1解码器MODEL
def noise_l1_autodecoder(layer_1,_weights,_bises,_keep_prob):
    layer_lout = tf.nn.dropout(layer_1,_keep_prob)
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_lout,_weights['l1_h2']),_bises['l1_b2']))
    layer_2out = tf.nn.dropout(layer_2,_keep_prob)
    return tf.nn.sigmoid(tf.matmul(layer_2out,_weights['l1_out']) + _bises['l1_out'])

#第一层的解码输出
l1_reconstruction = noise_l1_autodecoder(l1_out,weights,biases,dropout_keep_prob)

#计算cost
l1_cost = tf.reduce_mean(tf.pow(l1_reconstruction - y , 2))

#optimizer
l1_optm = tf.train.AdamOptimizer(0.01).minimize(l1_cost)

#l2解码器model
def l2_autodecoder(layer1_2,_weights,_biases):
    layer1_2out = tf.nn.sigmoid(tf.add(tf.matmul(layer1_2,_weights['l2_h2']),biases['l2_b2']))
    return tf.nn.sigmoid(tf.matmul(layer1_2out,_weights['l2_out']) + _biases['l2_out'])
pass

#第二层的编码输出
l2_out = tf.nn.sigmoid(tf.add(tf.matmul(l2x,weights['l2_h1']),biases['l2_b1']))
#第二层的解码输出
l2_reconstruction = l2_autodecoder(l2_out,weights,biases)

#cost
l2_cost = tf.reduce_mean(tf.pow(l2_reconstruction - l2y , 2))
#优化器
optm2 = tf.train.AdamOptimizer(0.01).minimize(l2_cost)

#第三层网络结构
l3_out = tf.matmul(l3x,weights['out'] )+ biases['out']
l3_cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=l3_out,labels=l3y))
l3_optm = tf.train.AdamOptimizer(0.01).minimize(l3_cost)

#定义次联网络结构
#3层次联
#1联2
l1_l2out = tf.nn.sigmoid(tf.add(tf.matmul(l1_out,weights['l2_h1']),biases['l2_b1']))
#2联3
pred = tf.matmul(l1_l2out,weights['out']) + biases['out']
#定义loss和优化器
cost3 = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred,labels=l3y))
optm3 = tf.train.AdamOptimizer(0.001).minimize(cost3)

#第一层网络训练
epochs = 50
batch_size = 100
disp_stp = 10

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    print("开始训练")
    for epoch in range(epochs):
        num_batch = int(mnist.train.num_examples / batch_size)
        total_cost = 0.
        for i in range(num_batch):
            batch_xs , batch_ys = mnist.train.next_batch(batch_size)
            batch_xs_noisy = batch_xs + 0.3 * np.random.randn(batch_size,784)   #加入噪声
            feeds = {x:batch_xs_noisy,y:batch_xs,dropout_keep_prob:0.5}
            sess.run(l1_optm,feed_dict=feeds)
            total_cost += sess.run(l1_cost,feed_dict=feeds)
            pass
        #显示信息
        if epoch % disp_stp == 0:
            print("Epoch %02d/%02d average cost :%.6f"%(epoch,epochs,total_cost/num_batch))
            pass
        pass
    
    print("完成训练")
    
    #结果可视化
    show_num = 10
    test_noisy = mnist.test.images[:show_num] + 0.3*np.random.randn(show_num,784)
    encode_decode = sess.run(l1_reconstruction,feed_dict={x:test_noisy,dropout_keep_prob:1.})
    f , a = plt.subplots(3,10,figsize=(10,3))
    for i in range(show_num):
        a[0][i].imshow(np.reshape(test_noisy[i],(28,28)))
        a[1][i].imshow(np.reshape(mnist.test.images[i],(28,28)))
        a[2][i].imshow(np.reshape(encode_decode[i],(28,28)),cmap = plt.get_cmap('gray'))
        pass
    plt.show()
    pass
pass
#第二层网络训练
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    print("开始训练")
    for epoch in range(epochs):
        num_batch = int(mnist.train.num_examples / batch_size)
        total_cost = 0.
        for i in range(num_batch):
            batch_xs ,batch_ys = mnist.train.next_batch(batch_size)
            
            l1_h = sess.run(l1_out,feed_dict={x:batch_xs,y:batch_xs,dropout_keep_prob:1.})
            _ , l2cost = sess.run([optm2,l2_cost],feed_dict={l2x:l1_h,l2y:l1_h})
            total_cost += l2cost
            pass
        #log输出
        if epoch % disp_stp == 0:
            print("Epoch %02d / %02d average cost:%.6f"%(epoch,epochs,total_cost/num_batch))
            pass
        pass
    print("完成layer_2训练")
    
    #结果可视化
    show_num = 10
    testvec = mnist.test.images[:show_num]
    out1vec = sess.run(l1_out,feed_dict={x:testvec,y:testvec,dropout_keep_prob:1.})
    out2vec = sess.run(l2_reconstruction,feed_dict={l2x:out1vec})
    
    f,a = plt.subplots(3,10,figsize=(10,3))
    for i in range(show_num):
        a[0][i].imshow(np.reshape(testvec[i],(28,28)))
        a[1][i].imshow(np.reshape(out1vec[i],(16,16)))
        a[2][i].imshow(np.reshape(out2vec[i],(16,16)),cmap=plt.get_cmap('gray'))
        pass
    plt.show()
    pass
pass
#第三层网络训练
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    print("开始训练")
    for epoch in range(epochs):
        num_batch = int(mnist.train.num_examples/batch_size)
        total_cost = 0.
        for i in range(num_batch):
            batch_xs,batch_ys = mnist.train.next_batch(batch_size)
            l1_h = sess.run(l1_out,feed_dict={x:batch_xs,y:batch_xs,dropout_keep_prob:1.})
            l2_h = sess.run(l2_out,feed_dict={l2x:l1_h,l2y:l1_h})
            _,l3cost = sess.run([l3_optm,l3_cost],feed_dict={l3x:l2_h,l3y:batch_ys})
            
            total_cost += l3cost
            pass
        #输出cost
        if epoch % disp_stp == 0:
            print("Epoch %02d/%02d average cost:%.6f"%(epoch,epochs,total_cost/num_batch))
            pass
        pass
    print("完成layer_3训练")
    #测试model
    correct_prediction = tf.equal(tf.argmax(pred,1),tf.argmax(l3y,1))
    #计算准确率
    accuracy = tf.reduce_mean(tf.cast(correct_prediction,"float"))
    print("accuracy:",accuracy.eval({x:mnist.test.images,l3y:mnist.test.labels}))
    pass
pass
#次级微调
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    print("开始训练")
    for epoch in range(epochs):
        num_batch = int(mnist.train.num_examples/batch_size)
        total_cost  = 0.
        for i in range(num_batch):
            batch_xs,batch_ys = mnist.train.next_batch(batch_size)
            
            feeds = {x:batch_xs,l3y:batch_ys}
            sess.run(optm3,feed_dict=feeds)
            total_cost += sess.run(cost3,feed_dict=feeds)
            pass
        #输出cost
        if epoch % disp_stp == 0:
            print("Epoch %02d/%02d average cost:%6f"%(epoch,epochs,total_cost/num_batch))
            pass
        pass
    print("完成 次联 训练")
