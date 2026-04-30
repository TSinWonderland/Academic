### importing libaries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import r2_score, mean_squared_error


##load data & check for nulls

df = pd.read_csv("FloridaBikeRentals.csv", encoding="latin1")

df.head()


##address missing values


num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())


cat_cols = df.select_dtypes(include="object").columns
df[cat_cols] = df[cat_cols].fillna(df[cat_cols].mode().iloc[0])


#conversion


df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

df["day"] = df["Date"].dt.day
df["month"] = df["Date"].dt.month
df["day_of_week"] = df["Date"].dt.dayofweek
df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)


#correlation heatmap


plt.figure(figsize=(14,10))
sns.heatmap(df.select_dtypes(include=np.number).corr(),
            cmap="coolwarm", annot=False)
plt.title("Correlation Heatmap")
plt.show()

##distro plot count


plt.figure(figsize=(8,5))
sns.histplot(df["Rented Bike Count"], kde=True, bins=50)
plt.title("Distribution of Rented Bike Count")
plt.show()

##histogram


df.select_dtypes(include=np.number).hist(figsize=(16,14), bins=30)
plt.tight_layout()
plt.show()


##box plot: rented vs features


categorical_features = ["Seasons", "Holiday", "Functioning Day", "is_weekend"]

for col in categorical_features:
    plt.figure(figsize=(6,4))
    sns.boxplot(x=df[col], y=df["Rented Bike Count"])
    plt.title(f"Rented Bike Count vs {col}")
    plt.show()

#catplot


features = ["Hour", "Holiday", "Rainfall(mm)", "Snowfall (cm)", "is_weekend"]

for col in features:
    sns.catplot(x=col, y="Rented Bike Count", data=df,
                aspect=1.5, kind="box")
    plt.title(f"Catplot: Rented Bike Count vs {col}")
    plt.show()

df_encoded = pd.get_dummies(
    df.drop("Date", axis=1),
    drop_first=True
)

X = df_encoded.drop("Rented Bike Count", axis=1)
y = df_encoded["Rented Bike Count"]



X = df_encoded.drop("Rented Bike Count", axis=1)
y = df_encoded["Rented Bike Count"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)





scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

    

models = {
    "Linear Regression": LinearRegression(),
    "Lasso Regression": Lasso(alpha=0.01),
    "Ridge Regression": Ridge(alpha=1.0)
}

results = []

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    results.append([name, r2, rmse])

    

results_df = pd.DataFrame(
    results,
    columns=["Model", "R² Score", "RMSE"]
)

results_df.sort_values(by="R² Score", ascending=False)

    






