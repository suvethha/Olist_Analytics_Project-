
import pandas as pd
import matplotlib.pyplot as plt
import os


# ============================================================
# 1. LOAD FEATURE-ENGINEERED DATA
# ============================================================

orders = pd.read_csv(
    "featured_data/orders_featured.csv"
)

order_items = pd.read_csv(
    "cleaned_data/order_items_cleaned.csv"
)

products = pd.read_csv(
    "cleaned_data/products_cleaned.csv"
)

payments = pd.read_csv(
    "cleaned_data/payments_cleaned.csv"
)

reviews = pd.read_csv(
    "cleaned_data/reviews_cleaned.csv"
)

# Convert dates
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

print("EDA datasets loaded successfully!")


# ============================================================
# 2. GENERAL BUSINESS OVERVIEW
# ============================================================

print("\n========== BUSINESS OVERVIEW ==========")

print("Total Orders:", orders["order_id"].nunique())

print("Total Customers:", orders["customer_id"].nunique())

print("Total Products Sold:", len(order_items))

print(
    "Total Item Revenue:",
    order_items["price"].sum()
)

print(
    "Total Freight:",
    order_items["freight_value"].sum()
)

print(
    "Total Payment Value:",
    payments["payment_value"].sum()
)


# ============================================================
# 3. ORDER STATUS ANALYSIS
# ============================================================

print("\n========== ORDER STATUS ==========")

status_counts = orders["order_status"].value_counts()

print(status_counts)

status_counts.plot(kind="bar")

plt.title("Orders by Status")
plt.xlabel("Order Status")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 4. MONTHLY ORDER TREND
# ============================================================

print("\n========== MONTHLY ORDER TREND ==========")

orders["purchase_month"] = (
    orders["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype("string")
)

monthly_orders = (
    orders.groupby("purchase_month")["order_id"]
    .nunique()
)

print(monthly_orders)

monthly_orders.plot(kind="line", marker="o")

plt.title("Monthly Order Trend")
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 5. DELIVERY PERFORMANCE
# ============================================================

print("\n========== DELIVERY PERFORMANCE ==========")

if "delivery_performance" in orders.columns:
    delivery_counts = (
        orders["delivery_performance"]
        .value_counts()
    )

    print(delivery_counts)

    delivery_counts.plot(kind="bar")

    plt.title("Delivery Performance")
    plt.xlabel("Performance")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


# ============================================================
# 6. AVERAGE DELIVERY TIME
# ============================================================

print("\n========== DELIVERY TIME ==========")

orders["delivery_days"] = pd.to_numeric(
    orders["delivery_days"],
    errors="coerce"
)

delivered_orders = orders.loc[
    (orders["order_status"] == "delivered")
    & orders["delivery_days"].notna()
    & (orders["delivery_days"] >= 0)
]

print(
    "Average Delivery Days:",
    delivered_orders["delivery_days"].mean()
)

print(
    "Median Delivery Days:",
    delivered_orders["delivery_days"].median()
)


# ============================================================
# 7. PAYMENT METHOD ANALYSIS
# ============================================================

print("\n========== PAYMENT METHODS ==========")

payment_methods = (
    payments.groupby("payment_type")
    .agg(
        payment_count=("payment_type", "size"),
        total_payment=("payment_value", "sum")
    )
    .sort_values("total_payment", ascending=False)
)

print(payment_methods)

payment_methods["total_payment"].plot(kind="bar")

plt.title("Total Payment Value by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Payment Value")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 8. PRODUCT CATEGORY ANALYSIS
# ============================================================

print("\n========== PRODUCT CATEGORIES ==========")

category_sales = order_items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left",
    validate="many_to_one"
)

top_categories = (
    category_sales.groupby("product_category_name")
    .agg(
        items_sold=("order_id", "size"),
        item_revenue=("price", "sum")
    )
    .sort_values("item_revenue", ascending=False)
    .head(10)
)

print(top_categories)

top_categories["item_revenue"].plot(kind="bar")

plt.title("Top 10 Product Categories by Item Revenue")
plt.xlabel("Product Category")
plt.ylabel("Item Revenue")
plt.xticks(rotation=60, ha="right")
plt.tight_layout()
plt.show()


# ============================================================
# 9. CUSTOMER REVIEW ANALYSIS
# ============================================================

print("\n========== REVIEW SCORES ==========")

review_scores = reviews["review_score"].value_counts().sort_index()

print(review_scores)

review_scores.plot(kind="bar")

plt.title("Distribution of Review Scores")
plt.xlabel("Review Score")
plt.ylabel("Number of Reviews")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# ============================================================
# 10. SAVE SUMMARY TABLES
# ============================================================

os.makedirs("eda_results", exist_ok=True)

status_counts.rename("order_count").to_csv(
    "eda_results/order_status_summary.csv"
)

monthly_orders.rename("order_count").to_csv(
    "eda_results/monthly_orders_summary.csv"
)

payment_methods.to_csv(
    "eda_results/payment_method_summary.csv"
)

top_categories.to_csv(
    "eda_results/top_product_categories.csv"
)

review_scores.rename("review_count").to_csv(
    "eda_results/review_score_summary.csv"
)


print("\nEDA completed successfully!")
print("Summary files saved in eda_results/")
