import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "consultbae.db"


connection = sqlite3.connect(DB_PATH)


print("\n" + "=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)


# =========================================================
# 1. MASTER RECORD COUNT
# =========================================================

people = pd.read_sql_query(
    "SELECT * FROM people",
    connection
)

print("\n1. MASTER PEOPLE COUNT")
print("-" * 50)
print(f"Unique people: {len(people)}")


# =========================================================
# 2. RECORDS WITH INFORMATION FROM MULTIPLE SOURCES
# =========================================================

multi_source = people[
    people["match_method"].str.contains(
        "match",
        case=False,
        na=False
    )
]

print("\n2. MERGED RECORDS")
print("-" * 50)
print(f"Records matched across sources: {len(multi_source)}")


# =========================================================
# 3. SHOW MERGED RECORDS
# =========================================================

print("\n3. SAMPLE MERGED RECORDS")
print("-" * 50)

columns = [
    "person_id",
    "name",
    "email",
    "phone",
    "city",
    "gig_rate",
    "gig_status",
    "cbnexus_verified",
    "projects_completed",
    "match_method"
]

print(
    people[
        people["match_method"].str.contains(
            "match",
            case=False,
            na=False
        )
    ][columns].head(15).to_string(index=False)
)


# =========================================================
# 4. DATA QUALITY ISSUES
# =========================================================

issues = pd.read_sql_query(
    """
    SELECT
        source_name,
        source_row_number,
        issue_type,
        description,
        action_taken
    FROM data_quality_issues
    """,
    connection
)

print("\n4. DATA QUALITY ISSUES")
print("-" * 50)

print(
    issues.to_string(index=False)
)


# =========================================================
# 5. SOURCE AUDIT COUNT
# =========================================================

audit = pd.read_sql_query(
    """
    SELECT
        source_name,
        COUNT(*) AS records
    FROM source_records
    GROUP BY source_name
    ORDER BY source_name
    """,
    connection
)

print("\n5. SOURCE AUDIT")
print("-" * 50)

print(
    audit.to_string(index=False)
)


# =========================================================
# 6. CHECK FOR ORPHAN SOURCE RECORDS
# =========================================================

orphans = pd.read_sql_query(
    """
    SELECT COUNT(*) AS orphan_records
    FROM source_records sr
    LEFT JOIN people p
        ON sr.person_id = p.person_id
    WHERE p.person_id IS NULL
    """,
    connection
)

print("\n6. ORPHAN SOURCE RECORDS")
print("-" * 50)

print(
    f"Orphan source records: "
    f"{orphans.iloc[0]['orphan_records']}"
)


# =========================================================
# 7. FINAL CHECKS
# =========================================================

print("\n7. FINAL CHECKS")
print("-" * 50)

checks = {
    "Master people = 60": len(people) == 60,
    "Audit records = 103": len(pd.read_sql_query(
        "SELECT * FROM source_records",
        connection
    )) == 103,
    "No orphan source records": (
        orphans.iloc[0]["orphan_records"] == 0
    ),
    "Data quality issues recorded": len(issues) > 0
}


for check, result in checks.items():

    status = "PASS" if result else "CHECK"

    print(f"[{status}] {check}")


connection.close()


print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)