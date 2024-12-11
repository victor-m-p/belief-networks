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
data_complete = data_complete[data_complete['year']==2020]
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

# Drop 'ID' column
data = data_total.drop(columns='ID')

# --- Preprocessing --- #
X = data.drop("answer", axis=1)
y = data["answer"]

# Identify categorical columns (all columns in this case are categorical)
categorical_columns = X.columns.tolist()

# OneHotEncode categorical features
ohe = OneHotEncoder()
X_encoded = ohe.fit_transform(X).toarray()
encoded_feature_names = ohe.get_feature_names_out(categorical_columns)

# Combine processed features (only one-hot encoded features)
X_processed = X_encoded
all_feature_names = list(encoded_feature_names)

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

class_index = 1
shap_values_class = shap_values[:, :, class_index]
fig, ax = plt.subplots()
shap.summary_plot(shap_values_class, X_test, feature_names=all_feature_names, show=False)
plt.savefig("ml/shap_novote.png", dpi=300, bbox_inches="tight")
plt.close()

class_index = 3
shap_values_class = shap_values[:, :, class_index]
fig, ax = plt.subplots()
shap.summary_plot(shap_values_class, X_test, feature_names=all_feature_names, show=False)
plt.savefig("ml/shap_cons.png", dpi=300, bbox_inches="tight")
plt.close()

'''
What if we are interested in the importance of QUESTIONS rather than ANSWERS. 
i.e., a QUESTION with many levels will be dilluted in the feature importance.
'''

shap_values_aggregated = pd.DataFrame(shap_values_mean, columns=all_feature_names)
shap_cols = shap_values_aggregated.columns
feature_dict = {col: col.split('_')[0] for col in shap_cols}
shap_aggregated = shap_values_aggregated.groupby(feature_dict, axis=1).sum()
question_importance = shap_aggregated.abs().mean().sort_values(ascending=False)
question_importance

### local
class_idx = 3 
classes = ['Democrat', 'No Vote', 'Other', 'Republican']
class_of_interest = 'Republican'

correct_idx = np.where((y_test == class_of_interest) & (y_pred == class_of_interest))[0][0]
incorrect_idx = np.where((y_test == class_of_interest) & (y_pred != class_of_interest))[0][0]

# correctly classified (consistent) republican
'''
The model does not really understand, than
when it has already learned that the person
is identified as R then it does not learn 
anything from figuring out that the person is not D.
It does not understand that dependency. 
'''

shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[correct_idx, :, class_idx],
        base_values = explainer.expected_value[class_index],
        data=X_test[correct_idx, :],
        feature_names = all_feature_names
    ),
    max_display=10,
    show=False
)
plt.tight_layout()
plt.savefig("ml/shap_correct.png", dpi=300)
plt.close();
shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[incorrect_idx, :, class_idx],
        base_values = explainer.expected_value[class_idx],
        data=X_test[incorrect_idx, :],
        feature_names = all_feature_names
    ),
    max_display=10,
    show=False
)
plt.tight_layout()
plt.savefig("ml/shap_incorrect.png", dpi=300)
plt.close();

res = shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[correct_idx, :, class_idx],
        base_values=explainer.expected_value[class_idx],
        data=X_test[correct_idx, :],
        feature_names=all_feature_names,
    ),
    max_display=10,
    show=False
)

# Check what 'res' is
print(res)

X_test[correct_idx, :].shape
shap_values[3][:,].shape
explainer.expected_value[3]

print("X_test shape:", X_test.shape)  # e.g., (n_samples, 48)
print("shap_values shape:", np.array(shap_values).shape) # For multiclass: (n_classes, n_samples, n_features)


def plot_shap_explanation_precomputed(shap_values, X, index, feature_names, class_index, save_path=None):
    """
    Plot SHAP explanation for a single observation using precomputed SHAP values.

    Parameters:
        shap_values: List of SHAP value arrays (one array per class)
        X: Test dataset (already preprocessed)
        index: Index of the observation to explain
        feature_names: List of feature names
        class_index: Index of the class to explain
        save_path: Path to save the plot (optional)
    """
    # Ensure SHAP values and feature names align
    if X.shape[1] != len(feature_names):
        raise ValueError("Feature names do not match the dimensions of X!")

    # Extract SHAP values for the specific class and observation
    shap_values_obs = shap_values[class_index][index]
    observation = X[index]

    # Generate force plot
    shap.force_plot(
        explainer.expected_value[class_index],
        shap_values_obs,
        observation,
        feature_names=feature_names,
        matplotlib=True
    )
    
    # Save or show the plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


plot_shap_explanation_precomputed(
        shap_values,
        X_test,
        correct_idx,
        all_feature_names,
        class_index=3,
        #save_path="ml/shap_correct_class_3.png"
    )

# individual SHAP explanations # 


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