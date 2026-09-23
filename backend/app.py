
# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize Flask app with a name
superkart_api = Flask("SuperKart")

# Load the trained model pipeline (includes the one-hot encoder + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Define a route for the home page - useful as a quick health check
@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API"

# Define an endpoint to predict sales for a single product
@superkart_api.post('/v1/predict')
def predict_sales():
    # Get JSON data sent in the request body
    data = request.get_json()

    # Extract the 10 features the model was trained on
    sample = {
        'Product_Weight': data['Product_Weight'],
        'Product_Sugar_Content': data['Product_Sugar_Content'],
        'Product_Allocated_Area': data['Product_Allocated_Area'],
        'Product_MRP': data['Product_MRP'],
        'Store_Size': data['Store_Size'],
        'Store_Location_City_Type': data['Store_Location_City_Type'],
        'Store_Type': data['Store_Type'],
        'Product_Id_char': data['Product_Id_char'],
        'Store_Age_Years': data['Store_Age_Years'],
        'Product_Type_Category': data['Product_Type_Category']
    }

    # Convert the extracted data into a one-row DataFrame
    # (the pipeline expects a DataFrame with named columns, not a plain list)
    input_data = pd.DataFrame([sample])

    # Make a prediction - the pipeline handles the one-hot encoding internally
    prediction = model.predict(input_data).tolist()[0]

    # Convert to a plain Python float and round, so jsonify can serialize it
    prediction = round(float(prediction), 2)

    # Return the prediction as a JSON response
    return jsonify({'Sales': prediction})

# Define an endpoint to predict sales for a batch of products
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the file into a DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for every row in the batch
    predictions = model.predict(input_data).tolist()

    # Create an output dictionary mapping row index to predicted sales
    output_dict = {str(i): round(float(pred), 2) for i, pred in enumerate(predictions)}

    return output_dict


# Run the Flask app in debug mode when executed directly.
# In the container, Gunicorn runs the app instead (see the Dockerfile).
if __name__ == '__main__':
    superkart_api.run(debug=True)
