#--coding:utf-8--
import numpy as np
import sklearn
import pandas as pd
import json
import codecs
import matplotlib.pyplot as plt
pd.set_option('precision',4)
'''
该模块的功能设计：
目前仅针对结局是boolean的开发。
1、自动化的X折交叉实验及画图
2、自动化输出模型的一些预测结果。（准确率，AUROC，最佳阈值等等）
3、自动调参？好像还不如直接用gridsearch
'''
class LuwakMining:
    def __init__(self):
        self.splits=10
        print 'Welcome to LuwakMining!'
    def random_forest(self):
        return
    def flex_gridsearch(self,X,Y,model,params):
        return
    def predict_results_binary(self,model,X,Y):
        '''
        for certain types of models,we calculate predict results,accuracy,auroc,best thresholds
        '''
        assert len(X)==len(Y)
        assert type(model) in [sklearn.tree.tree.DecisionTreeClassifier,
                               sklearn.ensemble.gradient_boosting.GradientBoostingClassifier,
                               sklearn.ensemble.gradient_boosting.AdaBoostClassifier,
                               sklearn.ensemble.forest.RandomForestClassifier,
                               sklearn.linear_model.logistic.LogisticRegression
                               ]
        from sklearn.metrics import confusion_matrix,roc_curve,auc
        model.fit(X,Y)
        prob = pd.DataFrame(model.predict_proba(X=X)[:, 1], index=X.index, columns=[u'probablity'])
        predict = pd.Series(model.predict(X.iloc[:, :]),index=X.index,name='predict')
        result=prob.join(predict).join(Y)
        accuracy = (Y == predict).mean()
        cm=confusion_matrix(y_true=Y,y_pred=predict)
        fpr, tpr, threshold = roc_curve(Y, result.iloc[:, 0])
        auroc = auc(fpr, tpr)
        rate = pd.DataFrame(tpr - fpr)
        threshold_df = pd.DataFrame(threshold)
        for i in rate.index:
            if rate.ix[i, 0] == max(np.array(rate)):
                #             print max(tpr-fpr)
                max_i = i
                #             print '阈值为：',threshold_df.ix[max_i,0]
                best_threshold = threshold_df.ix[max_i, 0]
        print ('accuracy:',accuracy,'auroc:',auroc,'best_threshold:',best_threshold,'confusion_matrix:',cm)
        return result,accuracy,auroc,best_threshold,cm
    def cross_validation_binary(self,X,Y,model,splits,picture=True):
        '''
        For certain types of models, do the cross validation and plot the ROC results.
            X:features

            Y:Outcome

            model:Trained classification model

            splits:N of splits in k-fold cross validation

            picture:draw the ROC curve if True,default False
        '''
        if splits==None:
            splits=self.splits
            print ('use default splits=10')
        assert type(model) in [sklearn.tree.tree.DecisionTreeClassifier,
                               sklearn.ensemble.gradient_boosting.GradientBoostingClassifier,
                               sklearn.ensemble.gradient_boosting.AdaBoostClassifier,
                               sklearn.ensemble.forest.RandomForestClassifier,
                               sklearn.linear_model.logistic.LogisticRegression
                         ]
        # try:
        result,_,_,_,_=self.predict_results_binary(model=model,X=X,Y=Y)
        # except:
        #     print 'Error Getting predicted results!Please check!'
        #     return
        from sklearn.model_selection import StratifiedKFold
        # 10折交叉验证
        skf = StratifiedKFold(n_splits=splits)
        result_10 = pd.DataFrame()
        Y_10 = pd.Series()
        for train, test in skf.split(X,Y):
            #     model=tree.DecisionTreeClassifier(max_depth=3,max_leaf_nodes=5)
            #     print train,test
            X_train_10, X_test_10 = X.iloc[train, :], X.iloc[test, :]
            Y_train_10, Y_test_10 = Y.iloc[train], Y.iloc[test]
            #     print y_train_10,y_test_10
            model.fit(X=X_train_10, y=Y_train_10)
            try:
                Y_10 = Y_10.append(Y_test_10)
                result_10 = result_10.append(pd.DataFrame(model.predict_proba(X=X_test_10)[:, 1],
                                                          index=X_test_10.index,
                                                          columns=[u'预测']).join(Y_test_10))
            except:
                print 'Warning:Error in cross-validation'
                return
        from sklearn.metrics import roc_curve, auc
        fpr_10, tpr_10, threshold_10 = roc_curve(Y_10, result_10.iloc[:, 0])
        auroc_10 = auc(fpr_10, tpr_10)
        fpr, tpr, threshold = roc_curve(Y, result.iloc[:, 0])
        auroc = auc(fpr, tpr)
        rate = pd.DataFrame(tpr - fpr)
        threshold_df = pd.DataFrame(threshold)
        # for i in rate.index:
        #     if rate.ix[i, 0] == max(rate):
        #         #             print max(tpr-fpr)
        #         max_i = i
        #         #             print '阈值为：',threshold_df.ix[max_i,0]
        #         best_threshold = threshold_df.ix[max_i, 0]
        rate_10 = pd.DataFrame(tpr_10 - fpr_10)
        threshold_df = pd.DataFrame(threshold_10)
        # print rate_10,threshold_10
        for i in rate_10.index:
            if rate_10.ix[i, 0] == max(np.array(rate_10)):
                # print max(np.array(rate_10)),i
                #             print max(tpr-fpr)
                max_i = i
                #             print '阈值为：',threshold_df.ix[max_i,0]
                best_threshold_10 = threshold_df.ix[max_i, 0]
            else:
                pass
        # 画ROC曲线
        if picture:
            lw = 2
            plt.figure()
            plt.plot(fpr_10, tpr_10, label=u'ROC-10fold = %f' % auroc_10, lw=lw)
            plt.plot(fpr, tpr, label=u'ROC = %f' % auroc, lw=lw)
            plt.plot([0, 1], [0, 1], '--', lw=lw)
            plt.axis('square')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.xlabel(u'False Positive')
            plt.ylabel(u'True Positive')
            plt.title(u'ROC Curve')
            plt.legend(loc="lower right")
            plt.show()
        else:
            pass
        print ('auroc_10_fold:',auroc_10,'best_threshold_10_fold:',best_threshold_10)
        return auroc_10, best_threshold_10,tpr_10,fpr_10
