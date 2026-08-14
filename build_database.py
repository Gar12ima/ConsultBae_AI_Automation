import pandas as pd
import sqlite3
import re
from pathlib import Path
from datetime import datetime


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "consultbae.db"


# =========================================================
# NORMALIZATION FUNCTIONS
# =========================================================

def clean_text(value):
    """Convert missing values to empty strings and trim spaces."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_name(value):
    """Normalize names for matching."""
    value = clean_text(value).lower()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_email(value):
    """Normalize email addresses."""
    value = clean_text(value).lower()
    return value


def normalize_phone(value):
    """
    Keep only digits.
    Convert Indian +91 / 91 numbers to 10-digit format.
    """
    if pd.isna(value):
        return ""

    digits = re.sub(r"\D", "", str(value))

    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    return digits


def normalize_city(value):
    """Standardize common city variations."""
    value = clean_text(value).lower()

    city_map = {
        "gurgaon": "Gurgaon",
        "gurugram": "Gurgaon",
        "bangalore": "Bengaluru",
        "bengaluru": "Bengaluru",
        "new delhi": "New Delhi",
        "delhi": "Delhi",
        "delhi ncr": "Delhi NCR",
        "noida": "Noida",
        "pune": "Pune",
    }

    return city_map.get(value, value.title())


def clean_status(value):
    """Standardize worker status."""
    value = clean_text(value).lower()

    if value == "active":
        return "Active"

    if value == "inactive":
        return "Inactive"

    if value == "paused":
        return "Paused"

    return value.title()


def clean_verified(value):
    """Standardize CBNexus verification values."""
    value = clean_text(value).lower()

    if value in {"y", "yes"}:
        return "Yes"

    if value in {"n", "no"}:
        return "No"

    return value.title()


def clean_skills(value):
    """Normalize comma-separated skills."""
    if pd.isna(value):
        return ""

    skills = [
        skill.strip().lower()
        for skill in str(value).split(",")
        if skill.strip()
    ]

    # Remove duplicate skills while preserving order
    skills = list(dict.fromkeys(skills))

    return ", ".join(skills)


def clean_date(value):
    """
    Convert supported date formats into YYYY-MM-DD.
    Explicit formats are used instead of pandas guessing.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()

    formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Preserve unexpected values rather than silently deleting them
    return value


# =========================================================
# LOAD SOURCE FILES
# =========================================================

naukri = pd.read_csv(
    DATA_DIR / "source1_naukri_applicants.csv"
)

gig = pd.read_csv(
    DATA_DIR / "source2_gig_workers.csv"
)

cbnexus = pd.read_csv(
    DATA_DIR / "source3_cbnexus_contacts.csv"
)


# =========================================================
# DATA QUALITY TRACKING
# =========================================================

quality_issues = []


def add_quality_issue(
    source_name,
    row_number,
    issue_type,
    description,
    action_taken
):
    quality_issues.append({
        "source_name": source_name,
        "source_row_number": row_number,
        "issue_type": issue_type,
        "description": description,
        "action_taken": action_taken
    })


# =========================================================
# REMOVE COMPLETELY EMPTY GIG ROWS
# =========================================================

original_gig = gig.copy()

for index, row in original_gig.iterrows():

    if row.isna().all():

        add_quality_issue(
            "gig_workers",
            index + 2,
            "completely_blank_row",
            "Entire Gig Worker row contains missing values.",
            "Excluded from the master people table."
        )

# Remove completely blank rows
gig = gig.dropna(how="all").copy()


# =========================================================
# REPAIR MALFORMED GIG ROWS
# =========================================================

"""
One Gig Worker row has shifted columns.

Expected:

email_id | worker_name | rate | location | status | skill_tags

Observed malformed pattern:

skills | email | name | rate | location | status

We detect this structurally rather than depending only on the
person's name.
"""

for idx in gig.index:

    email_value = clean_text(gig.at[idx, "email_id"])
    worker_value = clean_text(gig.at[idx, "worker_name"])
    rate_value = clean_text(gig.at[idx, "rate"])
    location_value = clean_text(gig.at[idx, "location"])
    status_value = clean_text(gig.at[idx, "status"])
    skills_value = clean_text(gig.at[idx, "skill_tags"])

    # Detect shifted row:
    # first field is not email,
    # second field is an email,
    # third field looks like a person's name,
    # remaining fields are shifted.
    looks_malformed = (
        "@" not in email_value
        and "@" in worker_value
        and rate_value
        and "/" in location_value
        and status_value
    )

    if looks_malformed:

        original_skills = email_value
        original_email = worker_value
        original_name = rate_value
        original_rate = location_value
        original_location = status_value
        original_status = skills_value

        gig.at[idx, "email_id"] = original_email
        gig.at[idx, "worker_name"] = original_name
        gig.at[idx, "rate"] = original_rate
        gig.at[idx, "location"] = original_location
        gig.at[idx, "status"] = original_status
        gig.at[idx, "skill_tags"] = original_skills

        add_quality_issue(
            "gig_workers",
            idx + 2,
            "malformed_shifted_row",
            "Columns were shifted: skills appeared in email_id, email appeared in worker_name, and subsequent values were shifted.",
            "Reconstructed the row using the detected column pattern before processing."
        )


# =========================================================
# REMOVE REPEATED HEADER ROW FROM CBNEXUS
# =========================================================

original_cbnexus = cbnexus.copy()

for index, row in original_cbnexus.iterrows():

    if clean_text(row["Name"]).lower() == "name":

        add_quality_issue(
            "cbnexus",
            index + 2,
            "repeated_header",
            "A header row appears inside the CBNexus data.",
            "Removed before processing."
        )

cbnexus = cbnexus[
    cbnexus["Name"].astype(str).str.strip().str.lower() != "name"
].copy()


# =========================================================
# NORMALIZE SOURCE DATA
# =========================================================

# Naukri
naukri["name_norm"] = naukri["Full Name"].apply(normalize_name)
naukri["email_norm"] = naukri["Email"].apply(normalize_email)
naukri["phone_norm"] = naukri["Phone"].apply(normalize_phone)

# Gig Workers
gig["name_norm"] = gig["worker_name"].apply(normalize_name)
gig["email_norm"] = gig["email_id"].apply(normalize_email)

# CBNexus
cbnexus["name_norm"] = cbnexus["Name"].apply(normalize_name)
cbnexus["phone_norm"] = cbnexus["Phone Number"].apply(normalize_phone)


# =========================================================
# IDENTIFY DUPLICATE IDENTIFIERS INSIDE NAUKRI
# =========================================================

email_counts = naukri[
    naukri["email_norm"] != ""
]["email_norm"].value_counts()

for email, count in email_counts.items():

    if count > 1:

        add_quality_issue(
            "naukri",
            None,
            "duplicate_email",
            f"Email {email} appears {count} times in Naukri.",
            "Records with the same email were treated as the same person."
        )


phone_counts = naukri[
    naukri["phone_norm"] != ""
]["phone_norm"].value_counts()

for phone, count in phone_counts.items():

    if count > 1:

        add_quality_issue(
            "naukri",
            None,
            "duplicate_phone",
            f"Phone {phone} appears {count} times in Naukri.",
            "Records with the same phone were treated as the same person."
        )


# =========================================================
# DATABASE SETUP
# =========================================================

if DB_PATH.exists():
    DB_PATH.unlink()

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


# =========================================================
# MASTER PEOPLE TABLE
# =========================================================

cursor.execute("""
CREATE TABLE people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,

    experience_years REAL,
    current_ctc REAL,
    applied_date TEXT,

    skills TEXT,

    gig_rate TEXT,
    gig_status TEXT,
    gig_skills TEXT,

    cbnexus_verified TEXT,
    projects_completed INTEGER,

    match_method TEXT,

    created_at TEXT
)
""")


# =========================================================
# SOURCE AUDIT TABLE
# =========================================================

cursor.execute("""
CREATE TABLE source_records (
    source_record_id INTEGER PRIMARY KEY AUTOINCREMENT,

    person_id INTEGER,

    source_name TEXT,
    source_row_number INTEGER,

    source_name_value TEXT,
    source_email TEXT,
    source_phone TEXT,

    match_method TEXT,

    FOREIGN KEY(person_id) REFERENCES people(person_id)
)
""")


# =========================================================
# DATA QUALITY TABLE
# =========================================================

cursor.execute("""
CREATE TABLE data_quality_issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_name TEXT,
    source_row_number INTEGER,

    issue_type TEXT,
    description TEXT,
    action_taken TEXT
)
""")


# =========================================================
# PERSON MATCHING
# =========================================================

people = []


def find_person(email="", phone=""):
    """
    Match using strong identifiers only.

    Priority:
    1. Exact normalized email
    2. Exact normalized phone

    Name alone is NEVER used for automatic merging.
    """

    email = normalize_email(email)
    phone = normalize_phone(phone)

    # First: exact email match
    if email:

        email_matches = [
            person
            for person in people
            if person["email"] == email
        ]

        if len(email_matches) == 1:
            return email_matches[0]

    # Second: exact phone match
    if phone:

        phone_matches = [
            person
            for person in people
            if person["phone"] == phone
        ]

        if len(phone_matches) == 1:
            return phone_matches[0]

    # No confident match
    return None


def create_person(
    name="",
    email="",
    phone="",
    city="",
    experience_years=None,
    current_ctc=None,
    applied_date="",
    skills="",
    gig_rate="",
    gig_status="",
    gig_skills="",
    cbnexus_verified="",
    projects_completed=None,
    match_method="new_record"
):

    person = {
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,

        "experience_years": experience_years,
        "current_ctc": current_ctc,
        "applied_date": applied_date,

        "skills": skills,

        "gig_rate": gig_rate,
        "gig_status": gig_status,
        "gig_skills": gig_skills,

        "cbnexus_verified": cbnexus_verified,
        "projects_completed": projects_completed,

        "match_method": match_method
    }

    people.append(person)

    return person


def merge_value(old_value, new_value):
    """
    Fill missing master values from another source.

    Existing non-empty values are preserved.
    """

    if old_value in (None, "") and new_value not in (None, ""):
        return new_value

    return old_value


def merge_skills(old_skills, new_skills):

    old_list = [
        x.strip()
        for x in clean_text(old_skills).split(",")
        if x.strip()
    ]

    new_list = [
        x.strip()
        for x in clean_text(new_skills).split(",")
        if x.strip()
    ]

    combined = list(dict.fromkeys(old_list + new_list))

    return ", ".join(combined)


def merge_person(person, updates):

    for key, value in updates.items():

        if value in (None, ""):
            continue

        if key in {"skills", "gig_skills"}:

            person[key] = merge_skills(
                person.get(key, ""),
                value
            )

        else:

            person[key] = merge_value(
                person.get(key),
                value
            )


# =========================================================
# PROCESS NAUKRI
# =========================================================

for index, row in naukri.iterrows():

    email = row["email_norm"]
    phone = row["phone_norm"]

    person = find_person(
        email=email,
        phone=phone
    )

    if person is not None:

        merge_person(
            person,
            {
                "name": clean_text(row["Full Name"]),
                "email": email,
                "phone": phone,
                "city": normalize_city(row["City"]),
                "experience_years": row["Experience (Years)"],
                "current_ctc": row["Current CTC"],
                "applied_date": clean_date(row["Applied Date"]),
                "skills": clean_skills(row["Skills"])
            }
        )

        # Keep existing match method but mark duplicate
        if person["match_method"] == "naukri":
            person["match_method"] = "naukri_duplicate"

    else:

        create_person(
            name=clean_text(row["Full Name"]),
            email=email,
            phone=phone,
            city=normalize_city(row["City"]),
            experience_years=row["Experience (Years)"],
            current_ctc=row["Current CTC"],
            applied_date=clean_date(row["Applied Date"]),
            skills=clean_skills(row["Skills"]),
            match_method="naukri"
        )


# =========================================================
# PROCESS GIG WORKERS
# =========================================================

for index, row in gig.iterrows():

    email = row["email_norm"]

    # Only accept a value as an email if it actually
    # contains an @ symbol.
    if "@" not in email:
        email = ""

    person = find_person(
        email=email
    )

    if person is not None:

        merge_person(
            person,
            {
                "name": clean_text(row["worker_name"]),
                "email": email,
                "city": normalize_city(row["location"]),
                "gig_rate": clean_text(row["rate"]),
                "gig_status": clean_status(row["status"]),
                "gig_skills": clean_skills(row["skill_tags"])
            }
        )

        if person["match_method"] in {
            "naukri",
            "naukri_duplicate"
        }:
            person["match_method"] = "naukri_gig_email_match"

    else:

        create_person(
            name=clean_text(row["worker_name"]),
            email=email,
            city=normalize_city(row["location"]),
            gig_rate=clean_text(row["rate"]),
            gig_status=clean_status(row["status"]),
            gig_skills=clean_skills(row["skill_tags"]),
            match_method="gig_only"
        )


# =========================================================
# PROCESS CBNEXUS
# =========================================================

for index, row in cbnexus.iterrows():

    phone = row["phone_norm"]

    person = find_person(
        phone=phone
    )

    if person is not None:

        merge_person(
            person,
            {
                "name": clean_text(row["Name"]),
                "phone": phone,
                "city": normalize_city(row["City"]),
                "cbnexus_verified": clean_verified(row["Verified"]),
                "projects_completed": row["Projects Completed"]
            }
        )

        if person["match_method"] in {
            "naukri",
            "naukri_duplicate"
        }:
            person["match_method"] = "naukri_cbnexus_phone_match"

        elif person["match_method"] == "naukri_gig_email_match":
            person["match_method"] = "naukri_gig_cbnexus_match"

    else:

        create_person(
            name=clean_text(row["Name"]),
            phone=phone,
            city=normalize_city(row["City"]),
            cbnexus_verified=clean_verified(row["Verified"]),
            projects_completed=row["Projects Completed"],
            match_method="cbnexus_only"
        )


# =========================================================
# INSERT MASTER PEOPLE
# =========================================================

person_id_map = {}


for person in people:

    cursor.execute("""
        INSERT INTO people (
            name,
            email,
            phone,
            city,
            experience_years,
            current_ctc,
            applied_date,
            skills,
            gig_rate,
            gig_status,
            gig_skills,
            cbnexus_verified,
            projects_completed,
            match_method,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        person["name"],
        person["email"],
        person["phone"],
        person["city"],
        person["experience_years"],
        person["current_ctc"],
        person["applied_date"],
        person["skills"],
        person["gig_rate"],
        person["gig_status"],
        person["gig_skills"],
        person["cbnexus_verified"],
        person["projects_completed"],
        person["match_method"],
        datetime.now().isoformat(timespec="seconds")
    ))

    person_id = cursor.lastrowid

    person_id_map[id(person)] = person_id


# =========================================================
# HELPER: FIND MASTER PERSON ID
# =========================================================

def get_person_id(email="", phone=""):

    email = normalize_email(email)
    phone = normalize_phone(phone)

    # Email first
    if email:

        matches = [
            person
            for person in people
            if person["email"] == email
        ]

        if len(matches) == 1:
            return person_id_map[id(matches[0])]

    # Phone second
    if phone:

        matches = [
            person
            for person in people
            if person["phone"] == phone
        ]

        if len(matches) == 1:
            return person_id_map[id(matches[0])]

    return None


# =========================================================
# SOURCE AUDIT - NAUKRI
# =========================================================

for index, row in naukri.iterrows():

    email = row["email_norm"]
    phone = row["phone_norm"]

    person_id = get_person_id(
        email=email,
        phone=phone
    )

    cursor.execute("""
        INSERT INTO source_records (
            person_id,
            source_name,
            source_row_number,
            source_name_value,
            source_email,
            source_phone,
            match_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        "naukri",
        index + 2,
        clean_text(row["Full Name"]),
        email,
        phone,
        "email_or_phone"
    ))


# =========================================================
# SOURCE AUDIT - GIG WORKERS
# =========================================================

for index, row in gig.iterrows():

    email = row["email_norm"]

    if "@" not in email:
        email = ""

    person_id = get_person_id(
        email=email
    )

    cursor.execute("""
        INSERT INTO source_records (
            person_id,
            source_name,
            source_row_number,
            source_name_value,
            source_email,
            source_phone,
            match_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        "gig_workers",
        index + 2,
        clean_text(row["worker_name"]),
        email,
        "",
        "email_or_new"
    ))


# =========================================================
# SOURCE AUDIT - CBNEXUS
# =========================================================

for index, row in cbnexus.iterrows():

    phone = row["phone_norm"]

    person_id = get_person_id(
        phone=phone
    )

    cursor.execute("""
        INSERT INTO source_records (
            person_id,
            source_name,
            source_row_number,
            source_name_value,
            source_email,
            source_phone,
            match_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        person_id,
        "cbnexus",
        index + 2,
        clean_text(row["Name"]),
        "",
        phone,
        "phone_or_new"
    ))


# =========================================================
# INSERT DATA QUALITY ISSUES
# =========================================================

for issue in quality_issues:

    cursor.execute("""
        INSERT INTO data_quality_issues (
            source_name,
            source_row_number,
            issue_type,
            description,
            action_taken
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        issue["source_name"],
        issue["source_row_number"],
        issue["issue_type"],
        issue["description"],
        issue["action_taken"]
    ))


# =========================================================
# COMMIT DATABASE
# =========================================================

connection.commit()


# =========================================================
# SUMMARY
# =========================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM people
""")

people_count = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM source_records
""")

source_count = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM data_quality_issues
""")

issue_count = cursor.fetchone()[0]


# Match statistics
cursor.execute("""
    SELECT COUNT(*)
    FROM people
    WHERE match_method LIKE '%gig%'
""")

gig_match_count = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM people
    WHERE match_method LIKE '%cbnexus%'
""")

cbnexus_match_count = cursor.fetchone()[0]


connection.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n" + "=" * 70)
print("DATABASE BUILD COMPLETE")
print("=" * 70)

print("\nRAW SOURCE RECORDS:")
print(f"  Naukri:       {len(naukri)}")
print(f"  Gig Workers:  {len(gig)}")
print(f"  CBNexus:      {len(cbnexus)}")

print("\nMASTER PEOPLE:")
print(f"  Unique people: {people_count}")

print("\nAUDIT:")
print(f"  Source records: {source_count}")

print("\nDATA QUALITY:")
print(f"  Issues recorded: {issue_count}")

print("\nDATABASE:")
print(f"  {DB_PATH}")

print("\n" + "=" * 70)