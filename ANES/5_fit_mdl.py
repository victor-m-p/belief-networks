from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

# Load data
data_complete = pd.read_csv('data/anes_complete.csv')

# start with 2016
data_complete = data_complete[data_complete['year']==2016]
data_complete = data_complete[data_complete['question'] != 'vote']
data_beliefs = data_complete[~data_complete['question'].isin(['who', 'pref'])]
data_voting = data_complete[data_complete['question'] == 'who']


# data voting is now easy to use as outcome y
data_voting = data_voting[['ID', 'answer']].drop_duplicates()

# data beliefs 
# need this in wide format 
data_beliefs_wide = data_beliefs.pivot(index='ID', columns='question', values='answer').reset_index()

# okay try to merge this 
data_total = data_beliefs_wide.merge(data_voting, on='ID', how='inner')
data = data_total.dropna()

# --- Preprocessing --- #
X = data.drop("answer", axis=1)
y = data["answer"]

# Preprocess
categorical_columns = X.select_dtypes(include="object").columns.tolist()
numeric_columns = X.select_dtypes(include="number").columns.tolist()

# OneHotEncode categorical features
ohe = OneHotEncoder()
X_encoded = ohe.fit_transform(X[categorical_columns]).toarray()
encoded_feature_names = ohe.get_feature_names_out(categorical_columns)

# Standardize numeric features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[numeric_columns])

# Combine processed features
X_processed = np.hstack((X_scaled, X_encoded))
all_feature_names = numeric_columns + list(encoded_feature_names)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

# Model
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)

# Evaluate
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

## ------ SHAP ------ ## 
explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_test)

# Aggregate feature importance
shap_values_mean = np.mean(np.abs(shap_values), axis=2)  # Shape: (n_samples, n_features)
fig, ax = plt.subplots()
shap.summary_plot(shap_values_mean, X_test, feature_names=all_feature_names, show=False)
plt.savefig("ml/shap_overall.png", dpi=300, bbox_inches="tight")
plt.tight_layout()
plt.close()

# For specific class (e.g., Liberal)
class_index = 0
shap_values_class = shap_values[:, :, class_index]
fig, ax = plt.subplots()
shap.summary_plot(shap_values_class, X_test, feature_names=all_feature_names, show=False)
plt.savefig("ml/shap_lib.png", dpi=300, bbox_inches="tight")
plt.close()

# figure out what the features actually are # 
class_index = 3
shap_values_class = shap_values[:, :, class_index]
shap.summary_plot(shap_values_class, X_test, feature_names=all_feature_names)

'''
What if we are interested in the importance of QUESTIONS rather than ANSWERS. 
i.e., a QUESTION with many levels will be dilluted in the feature importance.
'''

shap_values_aggregated = pd.DataFrame(shap_values_mean, columns=all_feature_names)
shap_values_aggregated = shap_values_aggregated.drop(columns='ID')
shap_cols = shap_values_aggregated.columns
feature_dict = {col: col.split('_')[0] for col in shap_cols}
shap_aggregated = shap_values_aggregated.groupby(feature_dict, axis=1).sum()
question_importance = shap_aggregated.abs().mean().sort_values(ascending=False)
question_importance

'''
So here we get (by far) party identification.
Then temperature, focus, abortion, immigration, ...
Church attendance (behavior) is the worst. 
'''

'''
How to think about these SHAPLEY values
- marginal contribution (unique contribution); but can also "steal" variance + capture some interaction
'''

# recursive feature elimination (RFE)


'''
Suggestions for Improvement

    Address Class Imbalance:
        Use techniques like oversampling ("Other") with SMOTE or undersampling dominant classes.
        Consider weighted loss functions in the model.

    Feature Engineering:
        Look for features that help separate "Other" more effectively.
        Perform exploratory data analysis (EDA) to better understand class overlap.

    Hyperparameter Tuning:
        Fine-tune your Random Forest or experiment with other models (e.g., XGBoost, LightGBM).

    Advanced Methods:
        Try ensemble methods or neural networks with embeddings for categorical features.

'''