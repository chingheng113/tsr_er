from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.svm import SVC
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join('/data/linc9/tsr_er/')))
from data import data_util, data_generator
from data import selected_columns as sc

training_data_name = os.path.join('..', 'data', 'training_data_processed.pkl')
testing_data_name = os.path.join('..', 'data', 'testing_data_processed.pkl')
if os.path.isfile(training_data_name) & os.path.isfile(testing_data_name):
    id_train, X_train, y_train = data_util.load_variable(training_data_name)
    id_test, X_test, y_test = data_util.load_variable(testing_data_name)
else:
    id_train, id_test, X_train, X_test, y_train, y_test = data_generator.get_training_testing_data()
    # saving data
    data_util.save_variables(training_data_name, [id_train, X_train, y_train])
    data_util.save_variables(testing_data_name, [id_test, X_test, y_test])

# clf = RandomForestClassifier(n_estimators=1000, random_state=123, class_weight='balanced')
clf = SVC(probability=True)

# NIHSS
X_train_nih = X_train.drop(sc.gcs_vital_column+sc.dgfa_column_converted+sc.lb_column, axis=1)
X_test_nih = X_test.drop(sc.gcs_vital_column+sc.dgfa_column_converted+sc.lb_column, axis=1)
clf.fit(X_train_nih, y_train)
y_predict = clf.predict(X_test_nih)
print(classification_report(y_test, y_predict))
mc = confusion_matrix(y_test, y_predict)
print(mc)
y_probas_nihs = clf.predict_proba(X_test_nih)
fpr, tpr, thresholds = roc_curve(y_test, y_probas_nihs[:, 1])
roc_auc = auc(fpr, tpr)
print(roc_auc)


# NIHSS+VS
X_train_nih_vs = X_train.drop(sc.dgfa_column_converted+sc.lb_column, axis=1)
X_test_nih_vs = X_test.drop(sc.dgfa_column_converted+sc.lb_column, axis=1)
clf.fit(X_train_nih_vs, y_train)
y_predict = clf.predict(X_test_nih_vs)
print(classification_report(y_test, y_predict))
mc = confusion_matrix(y_test, y_predict)
print(mc)
y_probas_nihs_vs = clf.predict_proba(X_test_nih_vs)
fpr, tpr, thresholds = roc_curve(y_test, y_probas_nihs_vs[:, 1])
roc_auc = auc(fpr, tpr)
print(roc_auc)


# NIHSS+VS+FS
X_train_nih_lb = X_train.drop(sc.lb_column, axis=1)
X_test_nih_lb = X_test.drop(sc.lb_column, axis=1)
clf.fit(X_train_nih_lb, y_train)
y_predict = clf.predict(X_test_nih_lb)
print(classification_report(y_test, y_predict))
mc = confusion_matrix(y_test, y_predict)
print(mc)
y_probas_nihs_lb = clf.predict_proba(X_test_nih_lb)
fpr, tpr, thresholds = roc_curve(y_test, y_probas_nihs_lb[:, 1])
roc_auc = auc(fpr, tpr)
print(roc_auc)


# all (NIHSS + VS + Risk Factor + LB )
clf.fit(X_train, y_train)
y_predict = clf.predict(X_test)
print(classification_report(y_test, y_predict))
mc = confusion_matrix(y_test, y_predict)
print(mc)
y_probas = clf.predict_proba(X_test)
fpr, tpr, thresholds = roc_curve(y_test, y_probas[:, 1])
roc_auc = auc(fpr, tpr)
print(roc_auc)

# ElasticNet Features
X_train_Lasso = X_train[sc.Lasso_column]
X_test_Lasso = X_test[sc.Lasso_column]
clf.fit(X_train_Lasso, y_train)
y_predict = clf.predict(X_test_Lasso)
print(classification_report(y_test, y_predict))
mc = confusion_matrix(y_test, y_predict)
print(mc)
y_probas_elastic = clf.predict_proba(X_test_Lasso)
fpr, tpr, thresholds = roc_curve(y_test, y_probas_elastic[:, 1])
roc_auc = auc(fpr, tpr)
print(roc_auc)


predict_results = np.stack((y_probas_nihs[:, 1],
                            y_probas_nihs_vs[:,1],
                            y_probas_nihs_lb[:, 1],
                            y_probas[:, 1],
                            y_probas_elastic[:,1]
                            ), axis=1)
columns = ['n', 'nv', 'nvl', 'nvlr', 'se']
df_ = pd.DataFrame(columns=columns, data=predict_results)
df_.to_csv('predict_result.csv', index=False)