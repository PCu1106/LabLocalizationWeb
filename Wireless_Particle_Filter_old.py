#!/usr/bin/env python
# coding: utf-8


import pickle
import numpy as np
import csv
import random
import statistics
from collections import Counter
import pandas as pd
import os
#import Hashing_KNN as HK


#os.chdir('C:\\Master_Code_92589')
position_list = [[1,1],[2,1],[3,1],[4,1],[5,1],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],
[1,6],[2,6],[3,6],[4,6],[5,6],[6,6],[7,6],[8,6],[9,6],[10,6],[11,6],
[1,11],[2,11],[3,11],[4,11],[5,11],[6,11],[7,11],[8,11],[9,11],[10,11],[11,11],
[1,2],[1,3],[1,4],[1,5],[1,7],[1,8],[1,9],[1,10],
[11,2],[11,3],[11,4],[11,5],[11,7],[11,8],[11,9],[11,10],
                 ]  # 連轉角也看成有左右 方便particle用


# 寫一個函式 把 605 換成第5列 第6行


def to_Table(pos):
    if '.0' in pos:
        invalid=1
    else:    
        pos=str(pos)
        row = int(pos[-2:])
        col = int(pos[0:-2])
    
        return [row, col]


# 以實驗室 上為北  左下角為實驗室0,0
# table 的左上 代表實驗室的左下
table = np.array([
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,0,0,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
])



def add_weight(particle_weight_map, pos, particle_num, alpha, c, spread=3):

    # add weight to target position, and spread to neighbor
    alpha_1 = alpha*c
    alpha_2 = alpha_1*c
    alpha_3 = alpha_2*c
    num = to_Table(pos)
    for direction in range(4):
        particle_weight_map = add_weight_dir(
            particle_weight_map, num, direction, alpha * particle_num)
    #

    #
    x = num[0]  # row in table
    y = num[1]  # col

    if spread > 0:

        neighbor_1 = [[x+1, y], [x, y+1], [x-1, y], [x, y-1]]
        neighbor_2 = [[x+1, y+1], [x-1, y+1], [x+1, y-1],
                      [x-1, y-1], [x+2, y], [x, y+2], [x-2, y], [x, y-2]]
        neighbor_3 = [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2], [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2],
                      [x+3, y], [x, y+3], [x-3, y], [x, y-3]]

        neighbor_list = [neighbor_1, neighbor_2, neighbor_3]
        parameter_list = [alpha_1, alpha_2, alpha_3]

        for i in range(spread):
            for neighbor_pos in neighbor_list[i]:
                if neighbor_pos in position_list:
                    for direction in range(4):
                        particle_weight_map = add_weight_dir(
                            particle_weight_map, neighbor_pos, direction, parameter_list[i] * particle_num)

    return particle_weight_map


def add_weight_dir(particle_weight_map, pos, direction, particle_num):
    particle_weight_map[pos[0]][pos[1]][direction] += particle_num
    return particle_weight_map


def proportion_init(particle_weight_map, p_count_knn):

    # spread particles
    w_sum = 0
    for i in range(int(p_count_knn/4)):
        for d in range(4):
            pos = position_list[random.randint(0, 48)]
            particle_weight_map[pos[0]][pos[1]][d] += (1/p_count_knn)
            w_sum += (1/p_count_knn)

    return particle_weight_map  # 3/27修正


def euclidean_distance(p1, p2):
    return np.sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))


def avg_normalization(particle_weight_map_i):
    w_sum = 0
    for i in range(particle_weight_map_i.shape[0]):  # ?????
        for j in range(particle_weight_map_i.shape[1]):
            for d in range(4):
                w_sum += particle_weight_map_i[i][j][d]

    for i in range(particle_weight_map_i.shape[0]):
        for j in range(particle_weight_map_i.shape[1]):
            for d in range(4):
                particle_weight_map_i[i][j][d] /= w_sum

    return particle_weight_map_i


def normalization(particle_weight_map_i):
    return avg_normalization(particle_weight_map_i)


def calculate(knn_candidates, i):
    p_count_knn = 2000
    alpha = 1
    c = 0.5
    particle_prev_count = 20000#可能代表過去粒子比起新一輪的重要性 原:20000  如果要提升先前粒子的重要性  調到30000或40000
    with open('../walk/particle_prev_count.txt','r') as file:
        particle_prev_count = file.read()
        particle_prev_count = int(particle_prev_count)
    spread = 3


# map的部分用np save 和np load 讀寫就好 不用傳入

    # for i in range(len(knn_candidates)): # for 每個 KNN 預測的位置

    max_weight = 0
    max_pos = [0, 0]

    if i == 0 or os.path.isfile('./particle_weight_map.npy')==False:  # if 第一個位置 (是特例，沒有前一個位置)
        # 將該位置候選人以票數做 weight, 更新 partcle weight
        particle_weight_map = np.zeros((13, 13, 4))
        particle_weight_map = proportion_init(particle_weight_map, p_count_knn)
        # 每一輪預測KNN的參考位置 ( all 候選人 )----->[i]放 一個list("1":"5票" "2":6票).....?
        candidate_list = list(knn_candidates.keys())
        # 每一輪預測 KNN 的參考位置的次數 ( all 候選人票數 )
        candidate_vote_list = list(knn_candidates.values())
        all_vote = sum(candidate_vote_list)  # 總票數

        # 由得票數設定 weight
        for k in range(len(candidate_vote_list)):  # 每一個參考位置的比例分配
            candidate_vote_list[k] /= all_vote

        # 把 weight佈到 map上
        for j, element in enumerate(candidate_list):  # 每一輪KNN的每一個參考位置
            particle_weight_map = add_weight(
                particle_weight_map, element, 1*candidate_vote_list[j], alpha, c, spread)

        # 找地圖重心
        weight_sum = 0
# 打出整個position list 比較好------------------------------------------------------------------------------------------------------------------------
        for pos in position_list:
            for d in range(4):
                if max_weight < particle_weight_map[pos[0]][pos[1]][d]:
                    max_weight = particle_weight_map[pos[0]][pos[1]][d]
                    max_pos = pos

        particle_weight_map = normalization(particle_weight_map)
        # 想辦法把map存起來
        np.save('particle_weight_map', particle_weight_map)
        finalpos=pos_to_final(max_pos)
        return finalpos
    else:
        particle_weight_map = np.load('particle_weight_map.npy')
        for pos in position_list:
            for d in range(4):
                particle_weight_map[pos[0]][pos[1]][d] *= particle_prev_count

        # 每一輪預測KNN的參考位置 ( all 候選人 )
        candidate_list = list(knn_candidates.keys())
        # 每一輪預測 KNN 的參考位置的次數 ( all 候選人票數 )
        candidate_vote_list = list(knn_candidates.values())
        #print(candidate_list,'k',candidate_vote_list)



        all_vote = sum(candidate_vote_list)  # 總票數

        # 由得票數設定 weight
        for k in range(len(candidate_vote_list)):  # 每一個參考位置的比例分配
            candidate_vote_list[k] /= all_vote

        for j, element in enumerate(candidate_list):  # 每一輪 KNN 的每一個參考位置
            particle_weight_map = add_weight(particle_weight_map, element,
                                             p_count_knn*candidate_vote_list[j], alpha, c, spread)

        # 找地圖重心
        weight_sum = 0
        for pos in position_list:
            for d in range(4):
                if max_weight < particle_weight_map[pos[0]][pos[1]][d]:
                    max_weight = particle_weight_map[pos[0]][pos[1]][d]
                    max_pos = pos

        particle_weight_map = normalization(particle_weight_map)
        # 想辦法把map存起來
        np.save('particle_weight_map', particle_weight_map)
        finalpos=pos_to_final(max_pos)
        return finalpos


# 給 max_pos 和 particle_weight_map回去

# 把全是數字的pos變回final position  [2,1]->102
def pos_to_final(max_pos):
    if(max_pos[0]<10):
        final_pos = str(max_pos[1])+'0'+str(max_pos[0])
    else:
        final_pos = str(max_pos[1])+str(max_pos[0])

    
    return final_pos

