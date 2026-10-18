
import pandas as pd
import os


# ============================================================
# 1. CREATE OUTPUT FOLDER
# ============================================================

os.makedirs("featured_data", exist_ok=True)


# ============================================================
# 2. LOAD CLEANED DATASETS
# ============================================================

orders = pd.read_csv("cleaned_data/orders_cleaned.csv")
order_items = pd.read_csv("cleaned_data/order_items_cleaned.csv")
payments = pd.read_csv("cleaned_data/payments_cleaned.csv")
customers = pd.read_csv("cleaned_data/customers_cleaned.csv")
reviews = pd.read_csv("cleaned_data/reviews_cleaned.csv")


print("Cleaned datasets loaded successfully.")


# ============================================================
# 3. CONVERT DATE COLUMNS
# ============================================================

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in order_date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )


reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)


# ============================================================
# 4. ORDER DELIVERY FEATURES
# ============================================================

# Calculate delivery duration in days
orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400


# Calculate delivery delay compared with the estimated date
orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400


# Classify delivery performance
orders["delivery_performance"] = "Not Delivered"

orders.loc[
    orders["delivery_delay_days"] < 0,
    "delivery_performance"
] = "Early"

orders.loc[
    orders["delivery_delay_days"] == 0,
    "delivery_performance"
] = "On Time"

orders.loc[
    orders["delivery_delay_days"] > 0,
    "delivery_performance"
] = "Late"


# Calculate approval time in hours
orders["approval_hours"] = (
    orders["order_approved_at"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 3600


# Calculate carrier handover time in hours after purchase
orders["purchase_to_carrier_hours"] = (
    orders["order_delivered_carrier_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 3600


# Extract purchase date and time components
orders["purchase_date"] = (
    orders["order_purchase_timestamp"].dt.date
)

orders["purchase_year"] = (
    orders["order_purchase_timestamp"].dt.year
)

orders["purchase_month"] = (
    orders["order_purchase_timestamp"].dt.month
)

orders["purchase_month_name"] = (
    orders["order_purchase_timestamp"].dt.month_name()
)

orders["purchase_day"] = (
    orders["order_purchase_timestamp"].dt.day
)

orders["purchase_day_of_week"] = (
    orders["order_purchase_timestamp"].dt.day_name()
)

orders["purchase_hour"] = (
    orders["order_purchase_timestamp"].dt.hour
)


# ============================================================
# 5. ORDER VALUE FEATURES
# ============================================================

# Calculate item subtotal for each order
item_summary = (
    order_items.groupby("order_id")
    .agg(
        total_items=("order_item_id", "count"),
        unique_products=("product_id", "nunique"),
        unique_sellers=("seller_id", "nunique"),
        item_subtotal=("price", "sum"),
        total_freight=("freight_value", "sum")
    )
    .reset_index()
)


# Calculate total order value
item_summary["order_value"] = (
    item_summary["item_subtotal"]
    + item_summary["total_freight"]
)


# Merge item summary into Orders
orders = orders.merge(
    item_summary,
    on="order_id",
    how="left",
    validate="one_to_one"
)


# ============================================================
# 6. PAYMENT FEATURES
# ============================================================

# Aggregate payments by order
payment_summary = (
    payments.groupby("order_id")
    .agg(
        total_payment_value=("payment_value", "sum"),
        payment_count=("payment_sequential", "count"),
        payment_method_count=("payment_type", "nunique"),
        max_installments=("payment_installments", "max")
    )
    .reset_index()
)


# Merge payment summary into Orders
orders = orders.merge(
    payment_summary,
    on="order_id",
    how="left",
    validate="one_to_one"
)


# ============================================================
# 7. CUSTOMER PURCHASE FEATURES
# ============================================================

# Count orders per customer
customer_order_summary = (
    orders.groupby("customer_id")
    .agg(
        customer_order_count=("order_id", "nunique"),
        customer_total_order_value=("order_value", "sum")
    )
    .reset_index()
)


# Merge customer metrics into Orders
orders = orders.merge(
    customer_order_summary,
    on="customer_id",
    how="left",
    validate="many_to_one"
)


# Add customer-level metrics to Customers
customers = customers.merge(
    customer_order_summary,
    on="customer_id",
    how="left",
    validate="one_to_one"
)

customers["customer_order_count"] = (
    customers["customer_order_count"].fillna(0).astype(int)
)

customers["customer_total_order_value"] = (
    customers["customer_total_order_value"].fillna(0)
)


# ============================================================
# 8. REVIEW FEATURES
# ============================================================

review_summary = (
    reviews.groupby("order_id")
    .agg(
        average_review_score=("review_score", "mean"),
        review_count=("review_id", "nunique")
    )
    .reset_index()
)


# Merge review metrics into Orders
orders = orders.merge(
    review_summary,
    on="order_id",
    how="left",
    validate="one_to_one"
)


# ============================================================
# 9. CREATE A SIMPLE ORDER VALUE CATEGORY
# ============================================================

orders["order_value_category"] = "Unknown"

valid_order_values = orders["order_value"].notna()

orders.loc[
    valid_order_values & (orders["order_value"] < 100),
    "order_value_category"
] = "Low"

orders.loc[
    valid_order_values
    & (orders["order_value"] >= 100)
    & (orders["order_value"] < 500),
    "order_value_category"
] = "Medium"

orders.loc[
    valid_order_values & (orders["order_value"] >= 500),
    "order_value_category"
] = "High"


# ============================================================
# 10. SAVE FEATURE-ENGINEERED DATASETS
# ============================================================

orders.to_csv(
    "featured_data/orders_featured.csv",
    index=False
)

customers.to_csv(
    "featured_data/customers_featured.csv",
    index=False
)

item_summary.to_csv(
    "featured_data/order_items_summary.csv",
    index=False
)

payment_summary.to_csv(
    "featured_data/payment_summary.csv",
    index=False
)

review_summary.to_csv(
    "featured_data/review_summary.csv",
    index=False
)


# ============================================================
# 11. DISPLAY RESULTS
# ============================================================

print("\nFeature engineering completed successfully!")

print("\nOrders Featured Shape:")
print(orders.shape)

print("\nCustomers Featured Shape:")
print(customers.shape)

print("\nDelivery Performance Distribution:")
print(orders["delivery_performance"].value_counts())

print("\nOrder Value Categories:")
print(orders["order_value_category"].value_counts())

print("\nSample Feature-Engineered Orders:")
print(
    orders[
        [
            "order_id",
            "delivery_days",
            "delivery_delay_days",
            "delivery_performance",
            "total_items",
            "order_value",
            "total_payment_value",
            "customer_order_count",
            "average_review_score"
        ]
    ].head(10)
)

print("\nFeature-engineered files saved in featured_data/.")
