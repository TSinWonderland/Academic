#libaries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("adultcensusincome.csv")
df.head()

#missing

df.replace('?', np.nan, inplace=True)


df.dropna(inplace=True)

df.isnull().sum()

df['income'].value_counts(normalize=True)


#age 


sns.countplot(x='income', data=df)
plt.title("Income Distribution")
plt.show()


#'' distro


sns.histplot(df['age'], kde=True)
plt.title("Age Distribution")
plt.show()

#education


plt.figure(figsize=(8,5))
sns.countplot(y='education', data=df)
plt.title("Education Distribution")
plt.show()



sns.countplot(x='education.num', data=df)
plt.title("Years of Education Distribution")
plt.show()

#Marital


df['marital.status'].value_counts().plot.pie(autopct='%1.1f%%')
plt.title("Marital Status Distribution")
plt.ylabel("")
plt.show()

#comparison


sns.countplot(x='income', hue='sex', data=df)
plt.title("Income vs Sex")
plt.show()

sns.countplot(x='income', hue='education', data=df)
plt.title("Income vs Education")
plt.show()

sns.countplot(x='income', hue='marital.status', data=df)
plt.title("Income vs Marital Status")
plt.show()

##correlation


from sklearn.preprocessing import LabelEncoder

df_corr = df.copy()
le = LabelEncoder()

for col in df_corr.select_dtypes(include='object'):
    df_corr[col] = le.fit_transform(df_corr[col])

plt.figure(figsize=(10,8))
sns.heatmap(df_corr.corr(), cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()


#clean 

df.columns = df.columns.str.strip()

from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import RandomOverSampler

le = LabelEncoder()

df_encoded = df.copy()
for col in df_encoded.select_dtypes(include='object'):
    df_encoded[col] = le.fit_transform(df_encoded[col])

# Split features and target
X = df_encoded.drop('income', axis=1)
y = df_encoded['income']

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Handle class imbalance
ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X_scaled, y)


#Train


df.columns = df.columns.str.strip()

from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import RandomOverSampler

le = LabelEncoder()

df_encoded = df.copy()
for col in df_encoded.select_dtypes(include='object'):
    df_encoded[col] = le.fit_transform(df_encoded[col])

X = df_encoded.drop('income', axis=1)
y = df_encoded['income']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X_scaled, y)

#print

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC(),
    "Naive Bayes": GaussianNB(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42)
}

results = []

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    results.append([name, acc, f1])

results_df = pd.DataFrame(
    results,
    columns=["Model", "Accuracy", "F1 Score"]
)

print(results_df.sort_values(by="F1 Score", ascending=False))
