###libraries



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

from imblearn.over_sampling import SMOTE


#data

df = pd.read_csv("HR_comma_sep.csv")


print(df.shape)

# nulls
print(df.isnull().sum())


df.info()

#data

df = pd.read_csv("HR_comma_sep.csv")


print(df.shape)

# nulls
print(df.isnull().sum())


df.info()

#distro plots


for col in ["satisfaction_level", "last_evaluation", "average_montly_hours"]:
    sns.histplot(df[col], kde=True)
    plt.title(f"Distribution of {col}")
    plt.show()

#bar graph

plt.figure(figsize=(8,5))
sns.countplot(x="number_project", hue="left", data=df)
plt.title("Project #'s vs Employee Turnover")
plt.show()

##prior employees


left_emp = df[df["left"] == 1][["satisfaction_level", "last_evaluation"]]

kmeans = KMeans(n_clusters=3, random_state=42)
left_emp["cluster"] = kmeans.fit_predict(left_emp)

plt.figure(figsize=(8,6))
sns.scatterplot(
    x="satisfaction_level",
    y="last_evaluation",
    hue="cluster",
    data=left_emp,
    palette="Set2"
)
plt.title("Employee Clusters (Employees Who Left)")
plt.show()

#smote 


cat_cols = ["sales", "salary"]

num_cols = df.drop(columns=cat_cols + ["left"])
cat_encoded = pd.get_dummies(df[cat_cols], drop_first=True)

X = pd.concat([num_cols, cat_encoded], axis=1)
y = df["left"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=123
)


smote = SMOTE(random_state=123)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)


#scale

scaler = StandardScaler()

X_train_sm = scaler.fit_transform(X_train_sm)
X_test = scaler.transform(X_test)

#CV


models = {
    "Logistic Regression": LogisticRegression(),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    y_pred = cross_val_predict(model, X_train_sm, y_train_sm, cv=cv)
    print(f"\n{name}")
    print(classification_report(y_train_sm, y_pred))


#AUC ROC


plt.figure(figsize=(8,6))

for name, model in models.items():
    model.fit(X_train_sm, y_train_sm)
    y_prob = model.predict_proba(X_test)[:,1]

    auc = roc_auc_score(y_test, y_prob)
    fpr, tpr, _ = roc_curve(y_test, y_prob)

    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.2f})")

plt.plot([0,1], [0,1], 'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve Comparison")
plt.legend()
plt.show()

#matrix


best_model = GradientBoostingClassifier(random_state=42)
best_model.fit(X_train_sm, y_train_sm)

y_pred_test = best_model.predict(X_test)

cm = confusion_matrix(y_test, y_pred_test)

sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

##classification


turnover_prob = best_model.predict_proba(X_test)[:, 1]


risk_df = pd.DataFrame(X_test, columns=X.columns)

# prob column
risk_df["Turnover_Probability"] = turnover_prob

# class function
def classify_risk(p):
    if p < 0.20:
        return "Safe Zone (Green)"
    elif p < 0.60:
        return "Low Risk (Yellow)"
    elif p < 0.90:
        return "Medium Risk (Orange)"
    else:
        return "High Risk (Red)"

# execute
risk_df["Risk_Zone"] = risk_df["Turnover_Probability"].apply(classify_risk)

# print
risk_df[["Turnover_Probability", "Risk_Zone"]].head()





