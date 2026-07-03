DROP DATABASE IF EXISTS supply_chain_analytics;
CREATE DATABASE supply_chain_analytics;

USE supply_chain_analytics;

DROP TABLE IF EXISTS scms_data;
DROP TABLE IF EXISTS supplier_master;
DROP TABLE IF EXISTS inventory_table;

CREATE TABLE scms_data (
    id INT,
    project_code VARCHAR(50),
    pq VARCHAR(100),
    po_so_no VARCHAR(50),
    asn_dn_no VARCHAR(50),
    country VARCHAR(100),
    managed_by VARCHAR(100),
    fulfill_via VARCHAR(100),
    vendor_inco_term VARCHAR(50),
    shipment_mode VARCHAR(50),

    pq_first_sent_to_client_date DATE,
    po_sent_to_vendor_date DATE,
    scheduled_delivery_date DATE,
    delivered_to_client_date DATE,
    delivery_recorded_date DATE,

    product_group VARCHAR(100),
    sub_classification VARCHAR(100),
    vendor TEXT,
    item_description TEXT,
    molecule_test_type TEXT,
    brand VARCHAR(100),
    dosage VARCHAR(100),
    dosage_form VARCHAR(100),

    unit_of_measure_per_pack VARCHAR(50),

    line_item_quantity FLOAT,
    line_item_value FLOAT,
    pack_price FLOAT,
    unit_price FLOAT,

    manufacturing_site TEXT,
    first_line_designation VARCHAR(20),

    weight_kilograms FLOAT,
    freight_cost_usd FLOAT,
    line_item_insurance_usd FLOAT,

    freight_status VARCHAR(50),
    weight_status VARCHAR(50)
);

CREATE TABLE supplier_master (
    supplier_id VARCHAR(20),
    supplier_name TEXT,
    supplier_region VARCHAR(100),
    supplier_rating INT,
    contract_type VARCHAR(50)
);

CREATE TABLE inventory_table (
    product_id VARCHAR(20),
    product_name TEXT,
    warehouse_id VARCHAR(20),

    stock_qty INT,
    reorder_level INT,
    safety_stock INT,

    inventory_value FLOAT
);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Downloads/Data Analytics Projects/Final Projects/Supply Chain Analytics Project/Output_Files/scms_cleaned.csv'
INTO TABLE scms_data
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SELECT COUNT(*) FROM scms_data;

SELECT * FROM scms_data LIMIT 10;

LOAD DATA LOCAL INFILE 'C:/Users/HP/Downloads/Data Analytics Projects/Final Projects/Supply Chain Analytics Project/Output_Files/supplier_master.csv'
INTO TABLE supplier_master
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/Users/HP/Downloads/Data Analytics Projects/Final Projects/Supply Chain Analytics Project/Output_Files/inventory_table.csv'
INTO TABLE inventory_table
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SELECT COUNT(*) FROM supplier_master;
SELECT COUNT(*) FROM inventory_table;


-- 1. INVENOTORY PERFORMANCE 

SELECT
    warehouse_id,
    SUM(stock_qty) AS total_stock,
    SUM(inventory_value) AS total_inventory_value,
    AVG(reorder_level) AS avg_reorder_level,
    AVG(safety_stock) AS avg_safety_stock
FROM inventory_table
GROUP BY warehouse_id;

 -- 2.SUPPLIER PERFORMANCE
 
 SELECT
    supplier_name,
    supplier_region,
    supplier_rating,

    COUNT(*) AS total_orders,

    ROUND(AVG(freight_cost_usd), 2) AS avg_freight_cost,

    ROUND(AVG(DATEDIFF(
        delivered_to_client_date,
        scheduled_delivery_date
    )), 2) AS avg_delivery_delay_days

FROM scms_data s
JOIN supplier_master sm
ON s.vendor = sm.supplier_name

GROUP BY
    supplier_name,
    supplier_region,
    supplier_rating

ORDER BY total_orders DESC;

-- 3.ORDER FULFILLMENT ANALYSIS

SELECT
    country,
    shipment_mode,

    COUNT(id) AS total_orders,

    SUM(line_item_quantity) AS total_quantity,

    SUM(line_item_value) AS total_sales_value

FROM scms_data

GROUP BY
    country,
    shipment_mode

ORDER BY total_sales_value DESC;

-- 4. LEAD TIME ANALYSIS

SELECT
    vendor,
    shipment_mode,

    ROUND(AVG(DATEDIFF(
        delivered_to_client_date,
        po_sent_to_vendor_date
    )), 2) AS avg_lead_time_days

FROM scms_data

WHERE delivered_to_client_date IS NOT NULL
AND po_sent_to_vendor_date IS NOT NULL

GROUP BY
    vendor,
    shipment_mode

ORDER BY avg_lead_time_days DESC;

-- 5. LOGISTICS COST ANALYSIS

SELECT
    shipment_mode,
    freight_status,

    COUNT(*) AS total_shipments,

    ROUND(SUM(freight_cost_usd), 2) AS total_freight_cost,

    ROUND(AVG(freight_cost_usd), 2) AS avg_freight_cost

FROM scms_data

GROUP BY
    shipment_mode,
    freight_status

ORDER BY total_freight_cost DESC;

