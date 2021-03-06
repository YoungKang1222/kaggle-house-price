# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import torch
from torch import nn
from utils import train_model, pred


train = pd.read_csv('./all/train.csv')
test = pd.read_csv('./all/test.csv')
# print(train.head())
# print('training set shape:', train.shape)
# print('testing set shape:', test.shape)

all_features = pd.concat((train.loc[:, 'MSSubClass':'SaleCondition'],
                          test.loc[:, 'MSSubClass':'SaleCondition']))
# print(all_features.shape)
numeric_feats = all_features.dtypes[all_features.dtypes != "object"].index  # 取出所有的数值特征
all_features[numeric_feats] = all_features[numeric_feats].apply(lambda x: (x - x.mean())/ (x - x.std()))  # 减去均值，除以方差
train['SalePrice'] = np.log(train['SalePrice'])  # 对预测的价格取 log# 对预测的价
all_features = pd.get_dummies(all_features, dummy_na=True)  # 转换成种类表示
all_features = all_features.fillna(all_features.mean())  # 数据的均值填入到丢失数据中
feat_dim = all_features.shape[1]

num_train = int(0.9 * train.shape[0])  # 划分训练样本和验证集样本
indices = np.arange(train.shape[0])
np.random.shuffle(indices)  # shuffle 顺序
train_indices = indices[:num_train]
valid_indices = indices[num_train:]

# 提取训练集和验证集的特征
train_features = all_features.iloc[train_indices].values.astype(np.float32)
train_features = torch.from_numpy(train_features)
valid_features = all_features.iloc[valid_indices].values.astype(np.float32)
valid_features = torch.from_numpy(valid_features)
train_valid_features = all_features[:train.shape[0]].values.astype(np.float32)
train_valid_features = torch.from_numpy(train_valid_features)

# 提取训练集和验证集的label
train_labels = train['SalePrice'].values[train_indices, None].astype(np.float32)
train_labels = torch.from_numpy(train_labels)
valid_labels = train['SalePrice'].values[valid_indices, None].astype(np.float32)
valid_labels = torch.from_numpy(valid_labels)
train_valid_labels = train['SalePrice'].values[:, None].astype(np.float32)
train_valid_labels = torch.from_numpy(train_valid_labels)

# 提取训练集和验证集的特征
test_features = all_features[train.shape[0]:].values.astype(np.float32)
test_features = torch.from_numpy(test_features)


def get_model():
    net = nn.Sequential(nn.Linear(feat_dim, 1))
    return net


# 可以调整的超参
batch_size = 128
epochs = 100
lr = 0.01
wd = 0
use_gpu = True

net = get_model()
# train_model(net, train_features, train_labels, valid_features, valid_labels, epochs,
#             batch_size, lr, wd, use_gpu)
train_model(net, train_valid_features, train_valid_labels, None, None, epochs,
            batch_size, lr, wd, use_gpu)

pred(net, test, test_features)