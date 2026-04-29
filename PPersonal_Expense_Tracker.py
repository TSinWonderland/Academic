#libraries


import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

#Bar Plot: Average Healthcare Visits by Health Status


plt.figure(figsize=(8, 5))
avg_health.sort_index().plot(kind="bar", color="steelblue")

plt.title("Average Healthcare Visits by Health Status")
plt.xlabel("Health Status")
plt.ylabel("Average Number of Visits")

plt.tight_layout()
plt.savefig("avg_visits_by_health.png")
plt.show()

###Bar Plot: Average Healthcare Visits by Region


plt.figure(figsize=(8, 5))
avg_region.sort_index().plot(kind="bar", color="darkgreen")

plt.title("Average Healthcare Visits by Region")
plt.xlabel("Region")
plt.ylabel("Average Number of Visits")

plt.tight_layout()
plt.savefig("avg_visits_by_region.png")
plt.show()

###Heatmap: Correlation Among Numerical Variables


plt.figure(figsize=(8, 6))

corr_matrix = df_processed.select_dtypes(include="number").corr()

sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Correlation Heatmap of Numerical Variables")
plt.tight_layout()
plt.savefig("correlation_heatmap.png")
plt.show()


###Box Plots: Identify Outliers in Age, Income, and Visits



plt.figure(figsize=(12, 6))

plt.subplot(1, 3, 1)
sns.boxplot(y=df_processed["age"], color="lightblue")
plt.title("Age Distribution")

plt.subplot(1, 3, 2)
sns.boxplot(y=df_processed["income"], color="lightgreen")
plt.title("Income Distribution")

plt.subplot(1, 3, 3)
sns.boxplot(y=df_processed["visits"], color="salmon")
plt.title("Healthcare Visits Distribution")

plt.tight_layout()
plt.savefig("boxplots_age_income_visits.png")
plt.show()
