import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import OneHotEncoder
import math

data_df = pd.read_csv('properties.csv', sep=';', encoding='utf-8')

print(data_df.describe())
print(data_df.head())


ohe = OneHotEncoder()
transformed = ohe.fit_transform(data_df[['location']])
print(transformed.toarray())
print(ohe.categories_)
data_df[ohe.categories_[0]] = transformed.toarray()
print(data_df.head())


x = data_df.drop(['title', 'location', 'price'], axis=1).values
y = data_df['price'].values

# Split the dataset in training set and test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# sample_weight
n_samples = 4113
x_mean = x_train.mean(axis=1)
x_var = x_train.var(axis=1)
print("Oto lista średnich")
print(x_mean)
print(len(x_mean))
print("Oto lista wariancji")
print(x_var)
sample_weight = np.random.uniform(0.6, 1, size=n_samples)
sample_weight = ((x_mean * sample_weight) / (np.log(x_var) + math.log10(math.pi) + math.log10(n_samples)))
sample_weight = sample_weight - np.log((n_samples * sample_weight) / x_mean)
print("Oto lista uzyskanych wag")
print(sample_weight)

# Train the model on the training set
ml = LinearRegression()
ml.fit(x_train, y_train)

# Predict the test set results
y_pred = ml.predict(x_test)
print("Tablica przewidzianych wartości")
print(y_pred)

# Evaluate the model
print("Współczynnik determinacji: ", r2_score(y_test, y_pred))
mse = np.mean((ml.predict(x_test) - y_test) ** 2)
print("średni Błąd dopasowania (kwadratowy): ", mse)
mae = np.mean(np.abs(ml.predict(x_test) - y_test))
print("Średni błąd bezwzględny: ", mae)

# Plot the results
plt.figure(figsize=(9, 6))
plt.scatter(y_test, y_pred)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs. Predicted')
plt.show()

# Predicted values
pred_y_df = pd.DataFrame({'Actual Value': y_test, 'Predicted value': y_pred, 'Difference': y_test - y_pred})
print(pred_y_df[0:20])
        