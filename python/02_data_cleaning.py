import os
import pandas as pd

# 1. Create output folder
os.makedirs("cleaned_data", exist_ok=True)

# 2. Load raw datasets. Read ZIP prefixes as strings to preserve leading zeros.
orders = pd.read_csv("dataset/olist_orders_dataset.csv")
customers = pd.read_csv(
    "dataset/olist_customers_dataset.csv",
    dtype={"customer_zip_code_prefix": "string"},
)
order_items = pd.read_csv("dataset/olist_order_items_dataset.csv")
products = pd.read_csv("dataset/olist_products_dataset.csv")
sellers = pd.read_csv(
    "dataset/olist_sellers_dataset.csv",
    dtype={"seller_zip_code_prefix": "string"},
)
payments = pd.read_csv("dataset/olist_order_payments_dataset.csv")
reviews = pd.read_csv("dataset/olist_order_reviews_dataset.csv")
category_translation = pd.read_csv(
    "dataset/product_category_name_translation.csv",
    dtype={"product_category_name": "string"},
)
geolocation = pd.read_csv(
    "dataset/olist_geolocation_dataset.csv",
    dtype={"geolocation_zip_code_prefix": "string"},
)

# 3. Orders: convert dates and flag issues (do not delete records)
order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for column in order_date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

orders["delivery_date_issue"] = (
    orders["order_delivered_customer_date"]
    < orders["order_delivered_carrier_date"]
).fillna(False)

orders["delivered_missing_customer_date"] = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_customer_date"].isna()
)
orders["delivered_missing_carrier_date"] = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_carrier_date"].isna()
)
orders["duplicate_order_id"] = orders["order_id"].duplicated(keep=False)

# 4. Customers: trim whitespace in IDs
customers["customer_id"] = customers["customer_id"].str.strip()
customers["customer_unique_id"] = customers["customer_unique_id"].str.strip()

# 5. Order items: convert date and flag invalid values
order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"], errors="coerce"
)
order_items["price_freight_issue"] = (
    order_items["price"].lt(0) | order_items["freight_value"].lt(0)
).fillna(False)
order_items["duplicate_order_item"] = order_items.duplicated(
    subset=["order_id", "order_item_id"], keep=False
)

# 6. Products: flag missing/non-positive measurements
measurement_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]
products["product_measurement_issue"] = (
    products[measurement_columns].isna().any(axis=1)
    | products[measurement_columns].le(0).any(axis=1)
)

# Standardize the two known untranslated category names
category_mapping = {
    "pc_gamer": "gaming_pc",
    "portateis_cozinha_e_preparadores_de_alimentos":
        "kitchen_portables_and_food_preparers",
}
products["product_category_name"] = (
    products["product_category_name"].replace(category_mapping)
)

# Check translation keys before merge; don't silently choose conflicting translations
duplicate_translation_keys = category_translation[
    category_translation.duplicated(
        subset=["product_category_name"], keep=False
    )
]
if not duplicate_translation_keys.empty:
    raise ValueError(
        "Duplicate product_category_name values found in the translation table. "
        "Review these rows before merging."
    )

products = products.merge(
    category_translation,
    on="product_category_name",
    how="left",
    validate="many_to_one",
)
products["product_category_name"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"])
)
products = products.drop(columns=["product_category_name_english"])
products["product_category_name"] = (
    products["product_category_name"].fillna("Uncategorized")
)

# 7. Sellers: trim whitespace in IDs
sellers["seller_id"] = sellers["seller_id"].str.strip()

# 8. Payments: flag suspicious values
payments["payment_issue"] = (
    payments["payment_value"].lt(0)
    | payments["payment_installments"].le(0)
).fillna(False)

# 9. Reviews: convert dates and flag issues
review_date_columns = ["review_creation_date", "review_answer_timestamp"]
for column in review_date_columns:
    reviews[column] = pd.to_datetime(reviews[column], errors="coerce")

reviews["invalid_review_score"] = (
    ~reviews["review_score"].isin([1, 2, 3, 4, 5])
)
reviews["review_text_missing"] = (
    reviews["review_comment_title"].isna()
    & reviews["review_comment_message"].isna()
)

# 10. Remove exact duplicate rows in lookup/reference tables only
category_translation = category_translation.drop_duplicates()
geolocation = geolocation.drop_duplicates()

# 11. Save cleaned datasets (raw CSV files remain unchanged)
cleaned_datasets = {
    "orders_cleaned.csv": orders,
    "customers_cleaned.csv": customers,
    "order_items_cleaned.csv": order_items,
    "products_cleaned.csv": products,
    "sellers_cleaned.csv": sellers,
    "payments_cleaned.csv": payments,
    "reviews_cleaned.csv": reviews,
    "category_translation_cleaned.csv": category_translation,
    "geolocation_cleaned.csv": geolocation,
}
for filename, dataframe in cleaned_datasets.items():
    output_path = os.path.join("cleaned_data", filename)
    dataframe.to_csv(output_path, index=False)
    print(f"Saved: {output_path} | Rows: {len(dataframe):,}")

print("\nAll cleaned datasets saved successfully!")
print("Output folder: cleaned_data/")