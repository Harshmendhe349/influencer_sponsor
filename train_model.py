from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

import pandas as pd

# Load dataset (Make sure the CSV file is in the same directory)
df = pd.read_csv("synthetic_influencer_data.csv")

# Check the first few rows
print(df.head())


# Combine category & niche into a single text feature
df['text_data'] = df['category'] + " " + df['niche']

# Convert text into numerical values using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english')
text_features = vectorizer.fit_transform(df['text_data'])

# Normalize numerical features (reach & engagement rate)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[['reach', 'engagement_rate']])

# Convert features to DataFrame
text_features_df = pd.DataFrame(text_features.toarray(), columns=vectorizer.get_feature_names_out())
scaled_features_df = pd.DataFrame(scaled_features, columns=['reach', 'engagement_rate'])

# Combine all features
X = pd.concat([text_features_df, scaled_features_df], axis=1)

# Set target variable (we will later change this to real campaign matching data)
y = df['reach']

# Split data into training & test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Feature processing complete. Ready for model training!")










from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Initialize the model
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate model accuracy
mse = mean_squared_error(y_test, y_pred)
print(f"Model Training Complete! Mean Squared Error: {mse}")






import joblib

# Save the trained model
joblib.dump(model, "trained_model.pkl")
print("Model saved as trained_model.pkl")








# import matplotlib.pyplot as plt
# import seaborn as sns

# # Check feature importance from the trained model
# feature_importance = model.feature_importances_

# # Create a DataFrame
# importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importance})

# # Sort by importance
# importance_df = importance_df.sort_values(by="Importance", ascending=False)

# # Plot feature importance
# plt.figure(figsize=(10, 6))
# sns.barplot(x=importance_df["Importance"], y=importance_df["Feature"], palette="viridis")
# plt.title("Feature Importance")
# plt.xlabel("Importance Score")
# plt.ylabel("Feature")
# plt.show()






# from sklearn.model_selection import GridSearchCV

# # Define hyperparameters to tune
# param_grid = {
#     "n_estimators": [100, 200, 300],
#     "max_depth": [None, 10, 20],
#     "min_samples_split": [2, 5, 10],
#     "min_samples_leaf": [1, 2, 4]
# }

# # Grid Search
# grid_search = GridSearchCV(model, param_grid, cv=3, scoring="neg_mean_squared_error", verbose=2, n_jobs=-1)
# grid_search.fit(X_train, y_train)

# # Get best parameters
# best_params = grid_search.best_params_
# print("Best Hyperparameters:", best_params)

# # Train model with best params
# model = RandomForestRegressor(**best_params, random_state=42)
# model.fit(X_train, y_train)

# # Evaluate model
# y_pred = model.predict(X_test)
# mse = mean_squared_error(y_test, y_pred)
# print("Improved Mean Squared Error:", mse)
