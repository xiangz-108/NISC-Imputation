#####################################
#Author: Xiang Zhang
#Email: xiangzhang@email.arizona.edu
#####################################
#Purpose: The goal of this code is to impute data using NISC method.
#It requires input data stored as 2D numpy array, with name "data.npy" - 
#whose rows indicating the genes, cols indicating the cells.
#It will store the imputed data with name "data_nisc.npy"

import os
import random
import numpy as np
import tensorflow as tf
import time

def run_tf(gene_num,data_orig,input_tf,output_tf,current_loss,data_count_maximum):
    graph = tf.Graph()

    with graph.as_default():
        images_ph = tf.placeholder(tf.float32, [None,gene_num])
        labels_ph = tf.placeholder(tf.float32, [None,gene_num])
        weight_ph = tf.placeholder(tf.float32, [None,gene_num])
        hl_1 = tf.contrib.layers.fully_connected(images_ph, gene_num*2 , tf.nn.relu)
        hl_2 = tf.contrib.layers.fully_connected(hl_1, np.int(np.floor(gene_num/2)), tf.nn.leaky_relu)
        hl_3 = tf.contrib.layers.fully_connected(hl_2, gene_num*2, tf.nn.relu)
        predicted_labels = tf.contrib.layers.fully_connected(hl_3, gene_num, tf.nn.relu)

        loss = tf.div(tf.sqrt(tf.reduce_sum(tf.multiply(tf.div(weight_ph,49+weight_ph),tf.pow(tf.log(predicted_labels+1)-tf.log(labels_ph+1), 2)))),gene_num)
        l2_loss = tf.losses.get_regularization_loss()
        loss = loss+l2_loss*0.1

        train = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
        init = tf.global_variables_initializer()

    # Train Model
    session = tf.Session(graph=graph)

    _=session.run([init])

    
    #Pass training data and return loss
    for i in range(gene_num*5):
        _, loss_value = session.run([train, loss], feed_dict={weight_ph: data_orig[:,:], images_ph: input_tf[:,:], labels_ph: output_tf[:,:]})
        #Monitor loss for every 10 iterations
        if i%10 == 0:
            print("Loss at iteration" + str(i) + "is" + str(loss_value)+ "\n")
            
    pred = session.run([predicted_labels],feed_dict={weight_ph: data_orig[:,:],images_ph:input_tf[:,:]})
    nn_output=np.asarray(pred)[0,:,:]
    nn_output=nn_output.transpose()
    nn_output=np.log(nn_output+1)
    nn_output=nn_output*data_count_maximum
    nn_output=np.exp(nn_output)-1
    np.save("data_nisc", nn_output)
    print('nn output generated')
    return loss_value



data_count=np.load('data.npy')
data_count=np.log(data_count+1)
data_count_maximum=np.amax(data_count)
data_count=data_count/data_count_maximum
data_count=np.exp(data_count)-1
data_count_orig=np.load('data.npy')


data=data_count
gene_num=data.shape[0]


data_orig=data_count_orig.transpose()
input_tf=data.transpose()
output_tf=data.transpose()

current_loss=1000;


for i in range(1):
    current_loss=run_tf(gene_num,data_orig,input_tf,output_tf,current_loss,data_count_maximum)
    
