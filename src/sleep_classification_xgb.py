import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import _pickle as cPickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

print( "\nReading data from disk ...")
X = cPickle.load(open("../data/features_train.p", "rb"))
y = cPickle.load(open("../data/targets_train.p", "rb"))

X_train, X_test,  y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

print( "\nProcessing data for XGBoost ...")
lbl = LabelEncoder()
lbl.fit(list(y_train))
y_train = lbl.transform(list(y_train))


print(lbl.classes_)

print('Shape train: {}\nShape test: {}'.format(X_train.shape, X_test.shape))

y_mean = np.mean(y_train)

##### RUN XGBOOST

print("\nSetting up data for XGBoost ...")
# xgboost params
# use softmax multi-class classification
xgb_params = {
	'objective' : 'multi:softmax',
    'eta': 0.1,
    'max_depth': 6,
    'silent': 1,
    'num_class': 5 
}
dtrain = xgb.DMatrix(X_train, y_train)
dtest = xgb.DMatrix(X_test)

# cross-validation
#print( "Running XGBoost CV ..." )
#cv_result = xgb.cv(xgb_params, 
#                   dtrain, 
#                   nfold=5,
#                   num_boost_round=200,
#                   early_stopping_rounds=50,
#                   verbose_eval=10, 
#                   show_stdv=False
#                  )
#num_boost_rounds = len(cv_result)

# this gave 93% after crossval
num_boost_rounds = 200
print("Num_boost_rounds="+str(num_boost_rounds))

# train model
print( "\nTraining XGBoost ...")
model = xgb.train(dict(xgb_params, silent=1), dtrain, num_boost_round=num_boost_rounds)

print( "\nPredicting with XGBoost ...")
xgb_pred = model.predict(dtest)

pred = lbl.classes_[xgb_pred.astype(int)]


print( "\nXGBoost predictions:" )
print( pd.DataFrame(pred).head() )


print(pd.DataFrame(y_test).head() )

error_rate = np.sum(pred != y_test) / y_test.shape[0]
print('Test error using softmax = {}'.format(error_rate))



print( "\nFinished ..." )


#y_pred=[]

#for i,predict in enumerate(xgb_pred):
#    y_pred.append(str(round(predict,4)))

#y_pred=np.array(y_pred.astype(int))

#print( "\nPreparing results for write ..." )

#output = pd.DataFrame({'SleepStage': y_pred.astype(np.float32)})

#from datetime import datetime
#print( "\nWriting results to disk ..." )
#output.to_csv('sub{}.csv'.format(datetime.now().strftime('%Y%m%d_%H%M%S')), index=False)
