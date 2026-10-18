
import pandas as pd
import os


# ============================================================
# 1. CREATE OUTPUT FOLDER
# ============================================================

os.makedirs("powerbi_data", exist_ok=True)


# ============================================================
# 2. LOAD FEATURE-ENGINEERED DATA
# ============================================================

orders = pd.read_csv(
    "featured_data/orders_featured.csv"
)

customers = pd.read_csv(
    "featured_data/customers_featured.csv"
)

order_items = pd.read_csv(
    "cleaned_data/order_items_cleaned.csv"
)

products = pd.read_csv(
    "cleaned_data/products_cleaned.csv"
)

sellers = pd.read_csv(
    "cleaned_data/sellers_cleaned.csv"
)

payments = pd.read_csv(
    "cleaned_data/payments_cleaned.csv"
)

reviews = pd.read_csv(
    "cleaned_data/reviews_cleaned.csv"
)


# ============================================================
# 3. CREATE DATE TABLE
# ============================================================

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

date_range = pd.date_range(
    start=orders["order_purchase_timestamp"].min().normalize(),
    end=orders["order_purchase_timestamp"].max().normalize(),
    freq="D"
)

date_table = pd.DataFrame({
    "Date": date_range
})

date_table["Year"] = date_table["Date"].dt.year
date_table["Month Number"] = date_table["Date"].dt.month
date_table["Month Name"] = date_table["Date"].dt.month_name()
date_table["Quarter"] = "Q" + date_table["Date"].dt.quarter.astype(str)
date_table["Day"] = date_table["Date"].dt.day
date_table["Day Name"] = date_table["Date"].dt.day_name()
date_table["Year Month"] = date_table["Date"].dt.strftime("%Y-%m")


# ============================================================
# 4. SAVE TABLES FOR POWER BI
# ============================================================

tables = {
    "Orders.csv": orders,
    "Customers.csv": customers,
    "Order_Items.csv": order_items,
    "Products.csv": products,
    "Sellers.csv": sellers,
    "Payments.csv": payments,
    "Reviews.csv": reviews,
    "Date_Table.csv": date_table
}

for filename, dataframe in tables.items():
    dataframe.to_csv(
        os.path.join("powerbi_data", filename),
        index=False
    )


print("Power BI datasets created successfully!")
print("Files saved in powerbi_data/")
