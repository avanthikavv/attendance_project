import optuna
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

X, y = load_diabetes(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

baseline_model = Ridge(alpha=1.0)
baseline_model.fit(X_train, y_train)
baseline_pred = baseline_model.predict(X_test)
baseline_mse = mean_squared_error(y_test, baseline_pred)

print("Baseline MSE:", baseline_mse)

def objective(trial):
    alpha = trial.suggest_float("alpha", 0.01, 10.0)

    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    return mse

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=10)

print("Best Alpha:", study.best_params)
print("Best MSE:", study.best_value)