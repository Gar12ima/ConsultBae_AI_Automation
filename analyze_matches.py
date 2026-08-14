import pandas as pd
from pathlib import Path
import re
from contextlib import redirect_stdout
import io
# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_FILE = BASE_DIR / "match_output.txt"


# -----------------------------
# Load Data
# -----------------------------

naukri = pd.read_csv(
    DATA_DIR / "source1_naukri_applicants.csv"
)

gig = pd.read_csv(
    DATA_DIR / "source2_gig_workers.csv"
)

cbnexus = pd.read_csv(
    DATA_DIR / "source3_cbnexus_contacts.csv"
)



# -----------------------------
# Normalization Functions
# -----------------------------

def normalize_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip().lower()



def normalize_phone(value):

    if pd.isna(value):
        return ""

    digits = re.sub(
        r"\D",
        "",
        str(value)
    )

    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    return digits



# -----------------------------
# Create Normalized Columns
# -----------------------------

naukri["name_norm"] = (
    naukri["Full Name"]
    .apply(normalize_text)
)


naukri["email_norm"] = (
    naukri["Email"]
    .apply(normalize_text)
)


naukri["phone_norm"] = (
    naukri["Phone"]
    .apply(normalize_phone)
)



gig["name_norm"] = (
    gig["worker_name"]
    .apply(normalize_text)
)


gig["email_norm"] = (
    gig["email_id"]
    .apply(normalize_text)
)



cbnexus["name_norm"] = (
    cbnexus["Name"]
    .apply(normalize_text)
)


cbnexus["phone_norm"] = (
    cbnexus["Phone Number"]
    .apply(normalize_phone)
)



# -----------------------------
# Analysis Function
# -----------------------------

def run_analysis():

    print("=" * 70)
    print("MATCH ANALYSIS")
    print("=" * 70)



    # Naukri - Gig Email Match

    print("\nNaukri <-> Gig Workers")
    print("-" * 50)


    naukri_emails = (
        set(naukri["email_norm"])
        - {""}
    )


    gig_emails = (
        set(gig["email_norm"])
        - {""}
    )


    email_matches = (
        naukri_emails
        &
        gig_emails
    )


    print(
        "Exact email matches:",
        len(email_matches)
    )


    for email in sorted(email_matches):

        n = naukri[
            naukri["email_norm"] == email
        ]["Full Name"].iloc[0]


        g = gig[
            gig["email_norm"] == email
        ]["worker_name"].iloc[0]


        print(
            f"{n} <-> {g} | {email}"
        )




    # Naukri - CBNexus Phone Match


    print("\nNaukri <-> CBNexus")
    print("-" * 50)


    naukri_phone = (
        set(naukri["phone_norm"])
        - {""}
    )


    cb_phone = (
        set(cbnexus["phone_norm"])
        - {""}
    )


    phone_matches = (
        naukri_phone
        &
        cb_phone
    )


    print(
        "Exact phone matches:",
        len(phone_matches)
    )



    for phone in sorted(phone_matches):

        n = naukri[
            naukri["phone_norm"] == phone
        ]["Full Name"].iloc[0]


        c = cbnexus[
            cbnexus["phone_norm"] == phone
        ]["Name"].iloc[0]


        print(
            f"{n} <-> {c} | {phone}"
        )




    # Gig - CBNexus Name Match


    print("\nGig Workers <-> CBNexus")
    print("-" * 50)


    gig_names = (
        set(gig["name_norm"])
        - {""}
    )


    cb_names = (
        set(cbnexus["name_norm"])
        - {""}
    )


    name_matches = (
        gig_names
        &
        cb_names
    )


    print(
        "Exact normalized name matches:",
        len(name_matches)
    )


    for name in sorted(name_matches):

        g = gig[
            gig["name_norm"] == name
        ]["worker_name"].iloc[0]


        c = cbnexus[
            cbnexus["name_norm"] == name
        ]["Name"].iloc[0]


        print(
            f"{g} <-> {c}"
        )




    # Missing Data Check


    print("\nData Quality Check")
    print("-" * 50)


    missing = gig[
        [
            "email_id",
            "worker_name",
            "rate",
            "location",
            "status",
            "skill_tags"
        ]
    ].isna().any(axis=1)



    print(
        gig[missing].to_string(index=False)
    )



    print("\n" + "=" * 70)
    print("END OF MATCH ANALYSIS")
    print("=" * 70)




# -----------------------------
# Save Output
# -----------------------------


# Run analysis and save output

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()

    with redirect_stdout(buffer):
        run_analysis()

    output = buffer.getvalue()

    f.write(output)

    print(output)