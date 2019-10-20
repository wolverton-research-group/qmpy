from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import cross_validation
from sklearn.decomposition import PCA
from sklearn import linear_model
from sklearn import grid_search

from qmpy import *

elts = Element.objects.filter(symbol__in=element_groups['simple-metals'])
out_elts = Element.objects.exclude(symbol__in=element_groups['simple-metals'])
models = Calculation.objects.filter(path__contains='icsd')
models = models.filter(converged=True, label__in=['static', 'standard'])
models = models.exclude(composition__element_set=out_elts)
data = models.values_list('composition_id', 'output__volume_pa')

y = []
X = []
X2 = []
for c, v in data:
    y.append(v)
    X.append(get_basic_composition_descriptors(c).values())
    X2.append(get_composition_descriptors(c).values())

X = np.array(X)
X2 = np.array(X)
y = np.array(y)

#pca = PCA(n_components=10, whiten=True)
#X = pca.fit_transform(X)

train_x, test_x, train_y, test_y = cross_validation.train_test_split(
        X, y, train_size=0.5)

clf = linear_model.LinearRegression()

clf.fit(train_x, train_y)
train_y -= clf.predict(train_x)

parameters = {
    'n_estimators': [10, 100, 500],
    'max_depth': [2,3,4], 
    'min_samples_split': [1,2,3,4] ,
    'learning_rate': [0.001, 0.01, 0.1]}
#gbr = GradientBoostingRegressor()
#clf = grid_search.GridSearchCV(gbr, parameters)
clf = SVR()

clf.fit(train_x, train_y)

print clf.score(test_x, test_y)
