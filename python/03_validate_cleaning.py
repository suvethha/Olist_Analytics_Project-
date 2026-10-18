
import pandas as pd
import os


# ============================================================
# 1. LOAD CLEANED DATASETS
# ============================================================

folder = "cleaned_data"

orders = pd.read_csv(
    os.path.join(folder, "orders_cleaned.csv")
)

customers = pd.read_csv(
    os.path.join(folder, "customers_cleaned.csv")
)

order_items = pd.read_csv(
    os.path.join(folder, "order_items_cleaned.csv")
)

products = pd.read_csv(
    os.path.join(folder, "products_cleaned.csv")
)

sellers = pd.read_csv(
    os.path.join(folder, "sellers_cleaned.csv")
)

payments = pd.read_csv(
    os.path.join(folder, "payments_cleaned.csv")
)

reviews = pd.read_csv(
    os.path.join(folder, "reviews_cleaned.csv")
)

category_translation = pd.read_csv(
    os.path.join(folder, "category_translation_cleaned.csv")
)

geolocation = pd.read_csv(
    os.path.join(folder, "geolocation_cleaned.csv")
)


# ============================================================
# 2. CHECK ROW COUNTS
# ============================================================

print("\nCLEANED DATASET ROW COUNTS")

datasets = {
    "Orders": orders,
    "Customers": customers,
    "Order Items": order_items,
    "Products": products,
    "Sellers": sellers,
    "Payments": payments,
    "Reviews": reviews,
    "Category Translation": category_translation,
    "Geolocation": geolocation
}

for name, dataframe in datasets.items():
    print(f"{name}: {len(dataframe)} rows")


# ============================================================
# 3. CHECK DUPLICATE IDENTIFIERS
# ============================================================

print("\nDUPLICATE IDENTIFIER CHECKS")

print(
    "Duplicate order IDs:",
    orders["order_id"].duplicated().sum()
)

print(
    "Duplicate product IDs:",
    products["product_id"].duplicated().sum()
)

print(
    "Duplicate seller IDs:",
    sellers["seller_id"].duplicated().sum()
)

print(
    "Duplicate order-item combinations:",
    order_items[
        ["order_id", "order_item_id"]
    ].duplicated().sum()
)


# ============================================================
# 4. CHECK QUALITY FLAGS
# ============================================================

print("\nQUALITY FLAG COUNTS")

print(
    "Delivery date issues:",
    orders["delivery_date_issue"].sum()
)

print(
    "Delivered orders missing customer date:",
    orders["delivered_missing_customer_date"].sum()
)

print(
    "Delivered orders missing carrier date:",
    orders["delivered_missing_carrier_date"].sum()
)

print(
    "Product measurement issues:",
    products["product_measurement_issue"].sum()
)

print(
    "Price/freight issues:",
    order_items["price_freight_issue"].sum()
)

print(
    "Payment issues:",
    payments["payment_issue"].sum()
)

print(
    "Invalid review scores:",
    reviews["invalid_review_score"].sum()
)


# ============================================================
# 5. CHECK CATEGORY CLEANING
# ============================================================

print("\nPRODUCT CATEGORY CHECK")

print(
    "Missing product categories:",
    products["product_category_name"].isna().sum()
)

print(
    "Uncategorized products:",
    products["product_category_name"]
    .eq("Uncategorized")
    .sum()
)


# ============================================================
# 6. FINAL VALIDATION MESSAGE
# ============================================================

print("\nValidation completed.")
