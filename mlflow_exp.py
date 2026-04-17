import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.datasets import make_regression

X,y=make_regression(n_samples=100,n_features=1,noise=10)

for alpha in [0.1,0.5,1.0]:
    with mlflow.start_run():
        model=LinearRegression()
        model.fit(X,y)

        preds=model.predict(X)
        mse=mean_squared_error(y,preds)

        mlflow.log_param("alpha",alpha)
        mlflow.log_metric("mse",mse)
        mlflow.sklearn.log_model(model,"model")