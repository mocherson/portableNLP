
from obesity_text import *
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score,precision_score,recall_score
from sklearn.model_selection import GridSearchCV


corpusfile = 'CUI_text/CUIs_text_nofam_15.txt'
vocab_size = 10000
corpus = entity_corpus(filename = corpusfile)
word_cnt = {i:Counter(corpus[i]) for i in corpus}
cnt = pd.DataFrame.from_dict(word_cnt,'index').fillna(0)

train_dic = get_dic('Obesity_data/train_groundtruth.xml')
test_dic = get_dic('Obesity_data/test_groundtruth.xml')
rule_dic = get_dic('Obesity_data/rule_annotation.xml')

df_intuitive = pd.DataFrame(columns=['P-Micro','P-Macro','R-Micro','R-Macro','F-Micro','F-Macro'])
df_textual = pd.DataFrame(columns=['P-Micro','P-Macro','R-Micro','R-Macro','F-Micro','F-Macro'])


major = False
intuitive_save_file = 'results/allclasses/intuitive_nofam_15cui_rfcv.csv'
textual_save_file = 'results/allclasses/textual_nofam_15cui_rfcv.csv'
# classifier
#clf = LogisticRegression()
#clf = GridSearchCV(clf, {'C':[0.01,0.1,1,10,100]},scoring='f1_macro',n_jobs=20)
clf = RandomForestClassifier()
clf = GridSearchCV(clf, {'n_estimators':[5,10,30,50,80,100], 'criterion':('gini','entropy')},scoring='f1_macro',n_jobs=20)
#clf = DecisionTreeClassifier()
#clf = GridSearchCV(clf, {'criterion':('gini','entropy')},scoring='f1_macro',n_jobs=20)
#clf = SVC()
#clf = GridSearchCV(clf, {'C':[0.01,0.1,1,10,100],'kernel':('linear', 'rbf')},scoring='f1_macro',n_jobs=20)

pram=[]
df_test=pd.DataFrame()
df_pred=pd.DataFrame()
for d in train_dic['intuitive']:
    y_train = pd.DataFrame.from_dict(train_dic['intuitive'][d],'index')
    y_test = pd.DataFrame.from_dict(test_dic['intuitive'][d],'index')
    y_rule = pd.DataFrame.from_dict(rule_dic['intuitive'][d],'index')
    X_train =cnt.loc[y_train.index]
    X_test =cnt.loc[y_test.index]
    if major:
        y_train = y_train.loc[(y_train[0]=='Y') | (y_train[0]=='N')]
        X_train = X_train.loc[y_train.index]
    clf.fit(X_train, y_train[0])
    y_pred = pd.DataFrame(clf.predict(X_test),index=y_test.index)
    if major:
        y_pred.loc[y_rule[0]=='Q']='Q'
    df_intuitive.loc[d,'P-Micro'] = precision_score(y_test,y_pred, average='micro')
    df_intuitive.loc[d,'P-Macro'] = precision_score(y_test,y_pred, average='macro')
    df_intuitive.loc[d,'R-Micro'] = recall_score(y_test,y_pred, average='micro')
    df_intuitive.loc[d,'R-Macro'] = recall_score(y_test,y_pred, average='macro')
    df_intuitive.loc[d,'F-Micro'] = f1_score(y_test,y_pred,average='micro')
    df_intuitive.loc[d,'F-Macro'] = f1_score(y_test,y_pred,average='macro')
    if hasattr(clf, 'best_params_'):
    	if 'C' in clf.best_params_:
    		df_intuitive.loc[d,'C'] = clf.best_params_['C'] 
    	if 'kernel' in clf.best_params_:
    		df_intuitive.loc[d,'kernel'] = clf.best_params_['kernel'] 
    	if 'n_estimators' in clf.best_params_:
    		df_intuitive.loc[d,'n_estimators'] = clf.best_params_['n_estimators'] 
    	if 'criterion' in clf.best_params_:
    		df_intuitive.loc[d,'criterion'] = clf.best_params_['criterion'] 
    		
    df_test=pd.concat([df_test,y_test])
    df_pred=pd.concat([df_pred,y_pred])
    
df_intuitive.loc['overall'] = np.nan
df_intuitive.loc['overall',['P-Micro','P-Macro','R-Micro','R-Macro','F-Micro','F-Macro']] =  \
				[
					precision_score(df_test,df_pred, average='micro'),
                 	precision_score(df_test,df_pred, average='macro'),
                    recall_score(df_test,df_pred, average='micro'),
                    recall_score(df_test,df_pred, average='macro'),
                    f1_score(df_test,df_pred, average='micro'),
                    f1_score(df_test,df_pred, average='macro')
                 ]

df_intuitive.to_csv(intuitive_save_file)

df_test=pd.DataFrame()
df_pred=pd.DataFrame()
for d in train_dic['textual']:
    y_train = pd.DataFrame.from_dict(train_dic['textual'][d],'index')
    y_test = pd.DataFrame.from_dict(test_dic['textual'][d],'index')
    y_rule = pd.DataFrame.from_dict(rule_dic['textual'][d],'index')
    X_train =cnt.loc[y_train.index]
    X_test =cnt.loc[y_test.index]
    if major:
        y_train = y_train.loc[(y_train[0]=='Y') | (y_train[0]=='U')]
        X_train = X_train.loc[y_train.index]
    clf.fit(X_train, y_train[0])
    y_pred = pd.DataFrame(clf.predict(X_test),index=y_test.index)
    if major:
        y_pred.loc[(y_rule[0]=='Q') | (y_rule[0]=='N')]=y_rule.loc[(y_rule[0]=='Q') | (y_rule[0]=='N')]
    df_textual.loc[d,'P-Micro'] = precision_score(y_test,y_pred, average='micro')
    df_textual.loc[d,'P-Macro'] = precision_score(y_test,y_pred, average='macro')
    df_textual.loc[d,'R-Micro'] = recall_score(y_test,y_pred, average='micro')
    df_textual.loc[d,'R-Macro'] = recall_score(y_test,y_pred, average='macro')
    df_textual.loc[d,'F-Micro'] = f1_score(y_test,y_pred,average='micro')
    df_textual.loc[d,'F-Macro'] = f1_score(y_test,y_pred,average='macro')
    if hasattr(clf, 'best_params_' ):
    	if 'C' in clf.best_params_:
    		df_textual.loc[d,'C'] = clf.best_params_['C']  
    	if 'kernel' in clf.best_params_:
    		df_textual.loc[d,'kernel'] = clf.best_params_['kernel'] 
    	if 'n_estimators' in clf.best_params_:
    		df_textual.loc[d,'n_estimators'] = clf.best_params_['n_estimators'] 
    	if 'criterion' in clf.best_params_:
    		df_textual.loc[d,'criterion'] = clf.best_params_['criterion'] 
    
    df_test=pd.concat([df_test,y_test])
    df_pred=pd.concat([df_pred,y_pred])

df_textual.loc['overall'] = np.nan    
df_textual.loc['overall',['P-Micro','P-Macro','R-Micro','R-Macro','F-Micro','F-Macro']] =  \
				[
					precision_score(df_test,df_pred, average='micro'),
                 	precision_score(df_test,df_pred, average='macro'),
                    recall_score(df_test,df_pred, average='micro'),
                    recall_score(df_test,df_pred, average='macro'),
                    f1_score(df_test,df_pred, average='micro'),
                    f1_score(df_test,df_pred, average='macro')
                 ]

df_textual.to_csv(textual_save_file)   
    
