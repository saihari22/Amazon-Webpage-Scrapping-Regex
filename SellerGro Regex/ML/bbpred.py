import numpy
import xgboost
from sklearn import cross_validation
from sklearn.metrics import accuracy_score

dataset = numpy.loadtxt('totalnew.csv', delimiter=",")
X = dataset[:,0:10]
Y = dataset[:,10]
seed = 10
test_size = 0.33

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=test_size, random_state=seed)


model = xgboost.XGBClassifier(
    colsample_bytree=0.8,
    gamma=0,
    learning_rate=0.1,
    max_depth=5,
    min_child_weight=1,
    n_estimators=100,
    nthread=5,
    objective='binary:logistic',
    reg_alpha=0.005,
    reg_lambda=0.8,
    scale_pos_weight=1,
    seed=10,
    silent=True,
    subsample=0.8)


model.fit(X_train, y_train)
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]
accuracy = accuracy_score(y_test, predictions)

print model
print("\nPredictor Accuracy: %.6f%%" % (accuracy * 100.0))
print "Feature Importances:\n", model.feature_importances_

