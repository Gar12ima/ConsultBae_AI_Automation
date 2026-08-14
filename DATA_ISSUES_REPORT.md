# TASK 4 - Data Issues Report

## Overview

During the data processing and database creation process, multiple data quality issues were identified in the provided CSV datasets.

The identified issues were analyzed and handled before storing the final cleaned records into the database.

---

# Data Quality Issues Identified

## 1. Duplicate Records

### Issue:
The same person appeared multiple times across different CSV files.

### Solution:
Implemented matching logic using available attributes such as:

- Name
- Email
- Phone Number
- Other available personal details

Duplicate records were identified and merged into a single unique person record.

---

## 2. Missing Values

### Issue:
Some records contained missing information in certain fields.

### Solution:

- Checked available information from other data sources.
- Kept unavailable values as NULL.
- Ensured database consistency during insertion.

---

## 3. Inconsistent Name Formats

### Issue:
Names were present in different formats:

- Different capitalization
- Extra spaces
- Minor spelling variations

### Solution:

Applied data cleaning techniques:

- Removed unnecessary spaces.
- Converted text into a consistent format.
- Used normalized values during matching.

---

## 4. Duplicate Contact Information

### Issue:
Some records contained repeated phone numbers or email addresses.

### Solution:

Validated contact details and used matching rules to prevent creation of multiple records for the same person.

---

## 5. Different Data Formats

### Issue:
Different CSV files contained inconsistent formats for similar fields.

### Solution:

- Standardized column names.
- Converted data into a common database structure.
- Applied preprocessing before database insertion.

---

# Data Cleaning Approach

The following steps were performed:

1. Data inspection
2. Data cleaning
3. Duplicate identification
4. Record matching
5. Database insertion verification

---

# Final Result

After applying cleaning and matching logic:

- Duplicate records were reduced.
- Data consistency was improved.
- Final database contained structured and unique records.

---

# Tools Used

- Python
- Pandas
- SQLite
- Data Processing Techniques