import pandas as pd

orders = pd.read_csv("dataset/olist_orders_dataset.csv")
customers = pd.read_csv("dataset/olist_customers_dataset.csv")
order_items = pd.read_csv("dataset/olist_order_items_dataset.csv")
products = pd.read_csv("dataset/olist_products_dataset.csv")
sellers = pd.read_csv("dataset/olist_sellers_dataset.csv")
payments = pd.read_csv("dataset/olist_order_payments_dataset.csv")
reviews = pd.read_csv("dataset/olist_order_reviews_dataset.csv")
category_translation = pd.read_csv(
    "dataset/product_category_name_translation.csv")
geolocation = pd.read_csv("dataset/olist_geolocation_dataset.csv")

print("Orders table loaded successfully!")
# Orders

print("\nOrders Shape:")
print(orders.shape)

print("\nOrders Header:")
print(orders.head())

print("\nOrders Column names:")
print(orders.columns)

print("\nOrders Data types:")
print(orders.dtypes)

print("\nOrders Missing values:")
print(orders.isnull().sum())

print("\nOrder Status Distribution")
print(orders["order_status"].value_counts())

print("\nMissing Delivery Dates by Order Status")
print(orders.groupby("order_status")[
      "order_delivered_customer_date"].apply(lambda x: x.isnull().sum()))

print("\nDuplicate Order IDs")
print(orders["order_id"].duplicated().sum())

# customers

print("\nCustomers Shape:")
print(customers.shape)

print("\nCustomers Header:")
print(customers.head())

print("\nCustomers Column Names")
print(customers.columns)

print("\nCustomers Data types:")
print(customers.dtypes)

print("\nCustomers Missing values:")
print(customers.isnull().sum())

print("\nCustomer IDs in Orders but not in Customers:")

missing_customers = orders[
    ~orders["customer_id"].isin(customers["customer_id"])
]

print(len(missing_customers))

# order_items

print("\nOrder Items Shape:")
print(order_items.shape)

print("\nOrder Items Columns:")
print(order_items.columns)

print("\nOrder Items Data Types:")
print(order_items.dtypes)

print("\nOrder Items Missing Values:")
print(order_items.isnull().sum())

missing_orders = order_items[
    ~order_items["order_id"].isin(orders["order_id"])
]

print("\nOrder IDs in Order Items but not in Orders:")
print(len(missing_orders))

print("\nDuplicate Order Items Record")
print(order_items.duplicated(subset=["order_id", "order_item_id"]).sum())

# products

print("\nProducts Shape:")
print(products.shape)

print("\nProducts Columns:")
print(products.columns)

print("\nProducts Data Types:")
print(products.dtypes)

print("\nProducts Missing Values:")
print(products.isnull().sum())

missing_products = order_items[
    ~order_items["product_id"].isin(products["product_id"])
]

print("\nProduct IDs in Order Items but not in Products:")
print(len(missing_products))


# sellers

print("\nSellers Shape:")
print(sellers.shape)

print("\nSellers Columns:")
print(sellers.columns)

print("\nSellers Data Types:")
print(sellers.dtypes)

print("\nSellers Missing Values:")
print(sellers.isnull().sum())

print("\nDuplicate Seller IDs:")
print(sellers["seller_id"].duplicated().sum())

missing_sellers = order_items[
    ~order_items["seller_id"].isin(sellers["seller_id"])
]
print("\nSeller IDs in Order items but not in Sellers:")
print(len(missing_sellers))

# payments

print("\nPayments Shape:")
print(payments.shape)

print("\nPayments Columns:")
print(payments.columns)

print("\nPayments Data Types:")
print(payments.dtypes)

print("\nPayments Missing Values:")
print(payments.isnull().sum())


missing_payment_orders = payments[
    ~payments["order_id"].isin(orders["order_id"])
]

print("\nOrder IDs in Payments but not in Orders:")
print(len(missing_payment_orders))


# reviews

print("\nReviews Shape:")
print(reviews.shape)

print("\nReviews Columns:")
print(reviews.columns)

print("\nReviews Data Types:")
print(reviews.dtypes)

print("\nReviews Missing Values:")
print(reviews.isnull().sum())

missing_review_orders = reviews[
    ~reviews["order_id"].isin(orders["order_id"])
]

print("\nOrder IDs in Reviews but not in Orders:")
print(len(missing_review_orders))

print("\nReview Score Distribution:")
print(reviews["review_score"].value_counts().sort_index())

invalid_reviews = reviews[
    ~reviews["review_score"].isin([1, 2, 3, 4, 5])
]

print("\nInvalid Review Scores:")
print(len(invalid_reviews))

# category translation
print("\nCategory Translation Shape:")
print(category_translation.shape)

print("\nCategory Translation Columns:")
print(category_translation.columns)

print("\nCategory Translation Missing Values:")
print(category_translation.isnull().sum())

missing_categories = products[
    ~products["product_category_name"].isin(
        category_translation["product_category_name"]
    )
]

print("\nProduct categories not found in translation table:")
print(len(missing_categories))


untranslated_categories = products[
    products["product_category_name"].notna() &
    ~products["product_category_name"].isin(
        category_translation["product_category_name"]
    )
]

print("\nUntranslated Product Categories:")
print(untranslated_categories["product_category_name"].unique())

print("\nNumber of Untranslated Categories:")
print(untranslated_categories["product_category_name"].nunique())

print("\nNumber of Products with Untranslated Categories:")
print(len(untranslated_categories))

# geolocation

print("\nGeolocation Shape:")
print(geolocation.shape)

print("\nGeolocation Columns:")
print(geolocation.columns)

print("\nGeolocation Data Types:")
print(geolocation.dtypes)

print("\nGeolocation Missing Values:")
print(geolocation.isnull().sum())

print("\nDuplicate Geolocation Records:")
print(geolocation.duplicated().sum())

print("\nUnique Geolocation ZIP Code Prefixes:")
print(geolocation["geolocation_zip_code_prefix"].nunique())


# check date consistency in Orders
order_dates = orders[
    [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
].apply(pd.to_datetime)

invalid_delivery_dates = order_dates[
    order_dates["order_delivered_customer_date"]
    < order_dates["order_purchase_timestamp"]
]

print("\nOrders with delivery before purchase:")
print(len(invalid_delivery_dates))


# Check Purchase -> Approval date consistency

invalid_approval_dates = order_dates[
    order_dates["order_approved_at"]
    < order_dates["order_purchase_timestamp"]
]

print("\nOrders approved before purchase:")
print(len(invalid_approval_dates))

# Check Carrier -> Customer delivery date consistency

invalid_carrier_delivery_dates = order_dates[
    order_dates["order_delivered_customer_date"]
    < order_dates["order_delivered_carrier_date"]
]

print("\nCustomer delivery before carrier delivery:")
print(len(invalid_carrier_delivery_dates))

print("\nDetails of Invalid Carrier/Customer Delivery Dates:")
print(
    orders.loc[
        invalid_carrier_delivery_dates.index,
        [
            "order_id",
            "order_status",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ]
)

print("\nCarrier vs Customer Delivery Dates:")

print(
    orders.loc[
        invalid_carrier_delivery_dates.index,
        [
            "order_id",
            "order_status",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].to_string(index=False)
)


print("\nDelivery Date Difference for Invalid Orders:")

invalid_delivery_check = orders.loc[
    invalid_carrier_delivery_dates.index,
    [
        "order_id",
        "order_delivered_carrier_date",
        "order_delivered_customer_date"
    ]
].copy()

invalid_delivery_check["difference_days"] = (
    pd.to_datetime(invalid_delivery_check["order_delivered_customer_date"])
    - pd.to_datetime(invalid_delivery_check["order_delivered_carrier_date"])
).dt.total_seconds() / (24 * 60 * 60)

print(invalid_delivery_check.to_string(index=False))


# Check Purchase -> Estimated Delivery date consistency

invalid_estimated_dates = order_dates[
    order_dates["order_estimated_delivery_date"]
    < order_dates["order_purchase_timestamp"]
]

print("\nOrders with estimated delivery before purchase:")
print(len(invalid_estimated_dates))
print("Hello")

