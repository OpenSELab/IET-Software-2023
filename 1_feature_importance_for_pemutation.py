# -*- coding: utf-8 -*-
"""1-feature_importance_for_Pemutation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14yJ77QSQKywN5VIHjGRNre66NgBEr5D-
"""

!pip install eli5
!pip install shap

import scipy.io.arff
import pandas as pd
import numpy as np
from sklearn.utils import resample # for Bootstrap sampling
import shutil
import os

from numpy import array

#Import resampling and modeling algorithms

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import matthews_corrcoef

import warnings

warnings.filterwarnings("ignore")

# click load google drive
rootpath = "/content/drive/MyDrive/Colab Notebooks/1/"

datasets_original = "datasets-original/"
datasets_discretize = "datasets-discretize/"
datasets_log = "datasets-log/"
datasets_minmax = "datasets-min-max/"
datasets_standardize = "datasets-standardize/"

AEEEM = ["EQ"]
ReLink = ["Zxing", "Apache", "Safe"]
Promise = [ "camel-1.2", "ivy-1.1", "jedit-3.2", "log4j-1.1", "lucene-2.0", "lucene-2.2", "lucene-2.4",
        "poi-1.5", "poi-2.5", "poi-3.0", "xalan-2.5", "xalan-2.6"]

ARFF = "ARFF/"
CSV = "CSV/"

BOOTSTRAP = "BOOTSTRAP/"


# CLS = [RandomForestClassifier(),LogisticRegression(),GaussianNB(),DecisionTreeClassifier(),KNeighborsClassifier(),MLPClassifier()]
CLS = [RandomForestClassifier(random_state=0),LogisticRegression(random_state=0),GaussianNB(),DecisionTreeClassifier(random_state=0),KNeighborsClassifier(),MLPClassifier(random_state=0)]

# some data sets imbanlance so we exclude it because these classifier have precision recall and f1 = 0  so we select 30-70% percent of defective

def setDir(filepath):
    #if filepath not exist then create  ！

    if not os.path.exists(filepath):
        pass
    else:
        shutil.rmtree(filepath,ignore_errors=True)

# 这是来自eli5包的可解释性方法
import eli5
from eli5.sklearn import PermutationImportance


# Lets configure Bootstrap
sample_times = 25  #No. of bootstrap samples to be repeated (created) seed is 0-24
# Lets run Bootstrap
# change the datasets name in turn

readfilepath = rootpath + datasets_standardize + ARFF

outfilepath = rootpath + datasets_standardize

performance_list = list()
permutation_train_list = list()
permutation_test_list = list()
for i in range(len(Promise)):

  readfile = readfilepath + "Promise/" + Promise[i] + ".arff"
  data,meta = scipy.io.arff.loadarff(readfile) # NOTE: ReLink original has bug{Y,N}->error  correct is bug {Y,N}

  df = pd.DataFrame(data)
  df_features = list(df)
  #print(df_features[:-1]) # delete bug column
  print("performance_list")
  print(performance_list)
  print("permutation_train_list")
  print(permutation_train_list)
  print("permutation_test_list")
  print(permutation_test_list)

  # bug has a b'Y' and b'N'
  df["bug"] = (df["bug"]== b"Y").astype(int)  # then bug into N->0 Y->1 !!!

  for j in range(len(CLS)):

    # Bootstrap
    for k in range(sample_times):

      #prepare train & test sets
      #Sampling with replacement..whichever is not used in training data will be used in test data
      train = resample(df, random_state = k)

      #picking rest of the data not considered in training sample test = df - train
      test = pd.concat([df, train, train]).drop_duplicates(keep = False)

      train = np.array(train)
      test = np.array(test)

      #fit model
      model = CLS[j] # can change max_iter=1000
      model.fit(train[:,:-1], train[:,-1]) #model.fit(X_train,y_train) i.e model.fit(train set, train label as it is a classifier)
      #evaluate model
      predictions = model.predict(test[:,:-1]) #model.predict(X_test)

      perm_train = PermutationImportance(model, random_state=0, scoring = 'accuracy', n_iter = 25).fit(train[:,:-1], train[:,-1]) #第一次是 roc_auc 导出文件不带标记 其余带标记
      perm_test = PermutationImportance(model, random_state=0, scoring = 'accuracy', n_iter = 25).fit(test[:,:-1], test[:,-1])


      accuracy = accuracy_score(test[:,-1], predictions) #accuracy_score(y_test, y_pred)
      precision = precision_score(test[:,-1], predictions)
      recall = recall_score(test[:,-1], predictions)
      f1 = f1_score(test[:,-1], predictions)
      auc = roc_auc_score(test[:,-1], predictions)
      mcc = matthews_corrcoef(test[:,-1], predictions)
      out_list_train = []
      out_list_test = []
      out_list_train = [Promise[i],str(CLS[j])+str(k)] + perm_train.feature_importances_.tolist()
      out_list_test = [Promise[i],str(CLS[j])+str(k)] + perm_test.feature_importances_.tolist()

      performance_list.append((Promise[i],str(CLS[j])+str(k),accuracy,precision,recall,f1,auc,mcc))
      permutation_train_list.append(out_list_train)
      permutation_test_list.append(out_list_test)


print("end")
print(performance_list)
print(permutation_train_list)
print(permutation_test_list)
# save as csv files
out_file_train_path = outfilepath + "Promise-permutation-train-accuracy.csv"
out_file_test_path = outfilepath + "Promise-permutation-test-accuracy.csv"
setDir(out_file_train_path)
setDir(out_file_test_path)

out_columns = ["project","cls_boot"] + df_features[:-1]

out_file_train = pd.DataFrame(permutation_train_list,columns=out_columns)
out_file_test = pd.DataFrame(permutation_test_list,columns=out_columns)

out_file_train.to_csv(out_file_train_path,index=False,columns=out_columns)
out_file_test.to_csv(out_file_test_path,index=False,columns=out_columns)

#计算结束

perm = PermutationImportance(model, random_state=0, scoring = 'roc_auc', n_iter = 25).fit(test[:,:-1], test[:,-1])
eli5.show_weights(perm, feature_names = df_features[:-1])

print(df_features[:-1])
perm.feature_importances_

# 这是来自 sklearn 包的可解释性方法
from sklearn.inspection import permutation_importance
scoring = ['accuracy']
#scoring参数可以同时加入多个计算指标，这样比重复使用permutation_importance更有效率，因为预测值能被用来计算不同的指标
r_multi = permutation_importance(model, test[:,:-1], test[:,-1], n_repeats=30, random_state=0, scoring=scoring)

for metric in r_multi:
    print(f"{metric}")
    r = r_multi[metric]
    for m in r.importances_mean.argsort()[::-1]:
        if r.importances_mean[m] - 2 * r.importances_std[m] > 0:
            print(f"    {df_features[m]:<8}"
                  f"{r.importances_mean[m]:.3f}"
                  f" +/- {r.importances_std[m]:.3f}")

import shap
#summary plot 为每个样本绘制其每个特征的SHAP值，这可以更好地理解整体模式，并允许发现预测异常值。

explainer = shap.KernelExplainer(model.predict,test[:,:-1])
shap_values = explainer.shap_values(train[:,:-1])
shap.summary_plot(shap_values, train[:,:-1], plot_type="bar")

# 下面不要动！！！

# 这是来自eli5包的可解释性方法
import eli5
from eli5.sklearn import PermutationImportance


# Lets configure Bootstrap
sample_times = 1  #No. of bootstrap samples to be repeated (created) seed is 0-24
# Lets run Bootstrap
# change the datasets name in turn

readfilepath = rootpath + datasets_log + ARFF

outfilepath = rootpath + datasets_log

performance_list = list()
for i in range(len(AEEEM)):

  readfile = readfilepath + "AEEEM/" + AEEEM[i] + ".arff"
  data,meta = scipy.io.arff.loadarff(readfile) # NOTE: ReLink original has bug{Y,N}->error  correct is bug {Y,N}

  df = pd.DataFrame(data)
  df_features = list(df)
  print(df_features[:-1]) # delete bug column

  # bug has a b'Y' and b'N'
  df["bug"] = (df["bug"]== b"Y").astype(int)  # then bug into N->0 Y->1 !!!

  for j in range(len(CLS)):

    # Bootstrap
    for k in range(sample_times):

      #prepare train & test sets
      #Sampling with replacement..whichever is not used in training data will be used in test data
      train = resample(df, random_state = k)

      #picking rest of the data not considered in training sample test = df - train
      test = pd.concat([df, train, train]).drop_duplicates(keep = False)

      train = np.array(train)
      test = np.array(test)

      #fit model
      model = CLS[j] # can change max_iter=1000
      model.fit(train[:,:-1], train[:,-1]) #model.fit(X_train,y_train) i.e model.fit(train set, train label as it is a classifier)
      #evaluate model
      predictions = model.predict(test[:,:-1]) #model.predict(X_test)


      accuracy = accuracy_score(test[:,-1], predictions) #accuracy_score(y_test, y_pred)
      precision = precision_score(test[:,-1], predictions)
      recall = recall_score(test[:,-1], predictions)
      f1 = f1_score(test[:,-1], predictions)
      auc = roc_auc_score(test[:,-1], predictions)
      mcc = matthews_corrcoef(test[:,-1], predictions)

      performance_list.append((AEEEM[i],str(CLS[j])+str(k),accuracy,precision,recall,f1,auc,mcc))

print(performance_list)

perm = PermutationImportance(model, random_state=0, scoring = 'roc_auc', n_iter = 25).fit(test[:,:-1], test[:,-1])
eli5.show_weights(perm, feature_names = df_features[:-1])