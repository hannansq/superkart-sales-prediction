
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend.
# "backend" is the container name on the shared Docker network -
# Docker's internal DNS resolves it to the right container automatically.
BACKEND_URL = "http://backend:7860"

# Page title
st.title("SuperKart Sales Prediction")
st.write(
    "Enter the product and store details below to predict the total sales revenue "
    "for that product at that store."
)

# ---------------------------------------------------------------
# Section 1: Online (single) prediction
# ---------------------------------------------------------------
st.subheader("Online Prediction")

# Input fields for product details
Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
Product_Sugar_Content = st.selectbox(
    "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
)
Product_Allocated_Area = st.number_input(
    "Product Allocated Area (share of total display area)", min_value=0.0, value=0.027
)
Product_MRP = st.number_input("Product MRP (maximum retail price)", min_value=0.0, value=117.08)
Product_Id_char = st.selectbox(
    "Product Category Code (FD = Food, DR = Drinks, NC = Non-Consumable)",
    ["FD", "DR", "NC"]
)
Product_Type_Category = st.selectbox(
    "Product Type Category", ["Perishables", "Non Perishables"]
)

# Input fields for store details
Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
Store_Location_City_Type = st.selectbox(
    "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
)
Store_Type = st.selectbox(
    "Store Type",
    ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]
)
Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, value=16)

# Assemble the inputs into the JSON payload the API expects
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category
}

# Send the request when the button is clicked
if st.button("Predict", type="primary"):

    response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data)

    if response.status_code == 200:
        result = response.json()
        predicted_sales = result["Sales"]
        st.success(f"Predicted Product Store Sales Total: {predicted_sales:,.2f}")
    else:
        st.error("Unable to connect to the prediction API.")

# ---------------------------------------------------------------
# Section 2: Batch prediction
# ---------------------------------------------------------------
st.subheader("Batch Prediction")
st.write(
    "Upload a CSV containing the 10 feature columns to get a prediction for every row."
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:

    if st.button("Predict for Batch", type="primary"):

        response = requests.post(
            f"{BACKEND_URL}/v1/predictbatch",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:
            predictions = response.json()
            st.success("Batch predictions completed!")

            # Show the results as a tidy table
            results_df = pd.DataFrame(
                list(predictions.items()), columns=["Row", "Predicted Sales"]
            )
            st.write(results_df)
        else:
            st.error("Unable to connect to the prediction API.")
