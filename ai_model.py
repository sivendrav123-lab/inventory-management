import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load data
data = pd.read_csv("sales_data.csv")

# Input features
X = data[["Current_Stock", "Previous_Sales"]]

# Output
y = data["Demand"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "sales_model.pkl")

print("AI model trained successfully!")
print("Model saved as sales_model.pkl")