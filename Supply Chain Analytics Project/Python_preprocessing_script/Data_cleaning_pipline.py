import pandas as pd
import numpy as np
import os
import random

# =========================================================
# PATHS
# =========================================================

BASE_PATH = r"C:\Users\HP\Downloads\Data Analytics Projects\Final Projects\Supply Chain Analytics Project\Raw_Data"

INPUT_FILE = os.path.join(BASE_PATH, "SCMS_Delivery_History_Dataset.csv")

OUTPUT_CLEANED = os.path.join(BASE_PATH, "scms_cleaned.csv")
OUTPUT_SUPPLIER = os.path.join(BASE_PATH, "supplier_master.csv")
OUTPUT_INVENTORY = os.path.join(BASE_PATH, "inventory_table.csv")

# =========================================================
# LOAD DATA
# =========================================================

print("Loading dataset...")

df = pd.read_csv(
    INPUT_FILE,
    encoding="latin1",
    low_memory=False
)

print("Dataset Loaded Successfully")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# =========================================================
# COLUMN NAME CLEANING
# =========================================================

print("\nCleaning column names...")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("/", "_")
    .str.replace("#", "")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)

# =========================================================
# FIX ENCODING ISSUES
# =========================================================

print("Fixing encoding issues...")

df["country"] = df["country"].replace({
    "CÃ´te d'Ivoire": "Côte d'Ivoire"
})

# =========================================================
# DATE COLUMN CLEANING
# =========================================================

print("Cleaning date columns...")

date_columns = [
    "pq_first_sent_to_client_date",
    "po_sent_to_vendor_date",
    "scheduled_delivery_date",
    "delivered_to_client_date",
    "delivery_recorded_date"
]

# Replace invalid text values
invalid_date_values = [
    "Pre-PQ Process",
    "Date Not Captured"
]

for col in date_columns:
    df[col] = df[col].replace(invalid_date_values, np.nan)

    # Convert to datetime
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )

# =========================================================
# FREIGHT COST CLEANING
# =========================================================

print("Cleaning freight cost column...")

# Create freight_status column
df["freight_status"] = "Actual Cost"

# Detect text rows
included_mask = df["freight_cost_usd"].astype(str).str.contains(
    "Freight Included",
    case=False,
    na=False
)

invoice_mask = df["freight_cost_usd"].astype(str).str.contains(
    "Invoiced Separately",
    case=False,
    na=False
)

df.loc[included_mask, "freight_status"] = "Included"

df.loc[invoice_mask, "freight_status"] = "Separate Invoice"

# Convert numeric freight values
df["freight_cost_usd"] = pd.to_numeric(
    df["freight_cost_usd"],
    errors="coerce"
)

# =========================================================
# WEIGHT COLUMN CLEANING
# =========================================================

print("Cleaning weight column...")

df["weight_status"] = "Actual Weight"

separate_mask = df["weight_kilograms"].astype(str).str.contains(
    "Weight Captured",
    case=False,
    na=False
)

reference_mask = df["weight_kilograms"].astype(str).str.contains(
    "See ASN",
    case=False,
    na=False
)

df.loc[separate_mask, "weight_status"] = "Separate"

df.loc[reference_mask, "weight_status"] = "Referenced ASN"

df["weight_kilograms"] = pd.to_numeric(
    df["weight_kilograms"],
    errors="coerce"
)

# =========================================================
# NUMERIC COLUMN CLEANING
# =========================================================

print("Converting numeric columns...")

numeric_columns = [
    "line_item_quantity",
    "line_item_value",
    "pack_price",
    "unit_price",
    "line_item_insurance_usd"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# =========================================================
# REMOVE EXACT DUPLICATES
# =========================================================

print("Removing duplicate rows...")

before_rows = df.shape[0]

df.drop_duplicates(inplace=True)

after_rows = df.shape[0]

print(f"Removed {before_rows - after_rows} duplicate rows")

# =========================================================
# CREATE SUPPLIER MASTER TABLE
# =========================================================

print("Creating supplier master table...")

supplier_df = (
    df[[
        "vendor",
        "country",
        "vendor_inco_term"
    ]]
    .drop_duplicates()
    .reset_index(drop=True)
)

supplier_df["supplier_id"] = [
    f"S{i+1:04d}" for i in range(len(supplier_df))
]

supplier_df.rename(columns={
    "vendor": "supplier_name",
    "country": "supplier_region",
    "vendor_inco_term": "contract_type"
}, inplace=True)

# Random ratings for demo analytics
supplier_df["supplier_rating"] = np.random.randint(
    3,
    6,
    size=len(supplier_df)
)

supplier_df = supplier_df[[
    "supplier_id",
    "supplier_name",
    "supplier_region",
    "supplier_rating",
    "contract_type"
]]

# =========================================================
# CREATE INVENTORY TABLE
# =========================================================

print("Creating inventory table...")

inventory_df = (
    df[[
        "item_description",
        "line_item_value"
    ]]
    .drop_duplicates()
    .reset_index(drop=True)
)

inventory_df["product_id"] = [
    f"P{i+1:05d}" for i in range(len(inventory_df))
]

inventory_df["warehouse_id"] = np.random.choice(
    ["WH001", "WH002", "WH003", "WH004"],
    size=len(inventory_df)
)

inventory_df["stock_qty"] = np.random.randint(
    100,
    5000,
    size=len(inventory_df)
)

inventory_df["reorder_level"] = np.random.randint(
    50,
    500,
    size=len(inventory_df)
)

inventory_df["safety_stock"] = np.random.randint(
    25,
    300,
    size=len(inventory_df)
)

inventory_df["inventory_value"] = (
    inventory_df["line_item_value"] *
    np.random.uniform(0.5, 2.0, size=len(inventory_df))
).round(2)

inventory_df.drop(columns=["line_item_value"], inplace=True)

inventory_df.rename(columns={
    "item_description": "product_name"
}, inplace=True)

inventory_df = inventory_df[[
    "product_id",
    "product_name",
    "warehouse_id",
    "stock_qty",
    "reorder_level",
    "safety_stock",
    "inventory_value"
]]

# =========================================================
# EXPORT FILES
# =========================================================

print("\nExporting cleaned files...")

df.to_csv(
    OUTPUT_CLEANED,
    index=False,
    encoding="utf-8-sig"
)

supplier_df.to_csv(
    OUTPUT_SUPPLIER,
    index=False,
    encoding="utf-8-sig"
)

inventory_df.to_csv(
    OUTPUT_INVENTORY,
    index=False,
    encoding="utf-8-sig"
)

# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n==============================")
print("DATA CLEANING COMPLETED")
print("==============================")

print(f"\nCleaned File:")
print(OUTPUT_CLEANED)

print(f"\nSupplier Table:")
print(OUTPUT_SUPPLIER)

print(f"\nInventory Table:")
print(OUTPUT_INVENTORY)

print("\nAll files exported successfully.")