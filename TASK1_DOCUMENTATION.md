# Task 1 - Database Merge and Matching

## Objective

The objective of this task was to merge data from multiple sources, identify duplicate records using normalization techniques, and create a unified database without relying on a common unique identifier.

## Input Data Sources

Three CSV files were used as input:

1. Source 1 - Naukri Applications
2. Source 2 - Gig Workers
3. Source 3 - CBNexus Workers


## Implementation Details

### build_database.py

This script performs the following operations:

- Reads data from all three CSV files
- Normalizes fields like name, email and phone number
- Matches records across different sources
- Creates the master database
- Stores source audit information
- Records data quality issues


### verify_database.py

This script verifies:

- Master records count
- Audit records count
- Source record consistency
- Data quality issue tracking


### analyze_matches.py

This script analyzes possible duplicate matches between different data sources using normalized email, phone number, and name-based matching techniques. It also generates a match analysis report for validation.


## Final Results

Total source records processed: 103

Unique people identified: 60

Data quality issues recorded: 6


## Database Output

Database created successfully:

consultbae.db


## Verification Result

All database verification checks passed successfully:

- Master people records available
- Audit records available
- No orphan source records
- Data quality issues recorded


## Challenges Faced

During implementation, some records had missing values and different formats across datasets.

Data cleaning and normalization steps were performed before merging the records.

Database verification scripts were used to check record consistency and data quality.

## Evidence Screenshots

Screenshots are available in the screenshots folder:

- task1_database_creation.png
- task1_verification.png
- task1_match_analysis.png