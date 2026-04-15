# =============================================================
#  FA Glass — HR Master Data Module for SynthGrid HR DB Synth
#  Source: master_zed.xlsx (Zahid Khan's OneDrive)
#  Mode: Read-Only | On-demand query
#  Password: zed (msoffcrypto decryption)
# =============================================================

import pandas as pd
import requests
import msoffcrypto
import io
from functools import lru_cache

# ── CONFIG ────────────────────────────────────────────────────
ONEDRIVE_URL = "https://ecsfaglass-my.sharepoint.com/:x:/g/personal/zahid_khan_faglass_com/IQDjaqEg8ZRIT7Y_xX_zJV1gAX24bwgwyW3lfkEjHoRThXY?download=1"
FILE_PASSWORD = "zed"

# Sheets to expose to the Synth
SHEET_CONFIG = {
    "active_employees":   {"sheet": "FAG - Master",         "skip": 0},
    "legacy_employees":   {"sheet": "MASTER",               "skip": 0},
    "exited_employees":   {"sheet": "EXIT",                 "skip": 0},
    "outsource":          {"sheet": "Outsourace Emp",       "skip": 0},
    "blue_collar_ot":     {"sheet": "Blue Collar - OT",     "skip": 0},
    "white_collar":       {"sheet": "White Collar - No OT", "skip": 0},
    "kra":                {"sheet": "KRA",                  "skip": 0},
}

# ── DATA LOADER ───────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_workbook() -> dict:
    """
    Fetches the Excel file from OneDrive, decrypts it using msoffcrypto,
    and loads all configured sheets into DataFrames.
    Cached — subsequent calls return the same data without re-fetching.
    """
    print("📥 Fetching HR Master from OneDrive...")
    response = requests.get(ONEDRIVE_URL, timeout=30)
    response.raise_for_status()
    print("✅ File fetched successfully.")

    # Decrypt the password-protected file
    print("🔓 Decrypting file with password...")
    encrypted = io.BytesIO(response.content)
    decrypted = io.BytesIO()
    office_file = msoffcrypto.OfficeFile(encrypted)
    office_file.load_key(password=FILE_PASSWORD)
    office_file.decrypt(decrypted)
    print("✅ File decrypted successfully.")

    data = {}
    for key, cfg in SHEET_CONFIG.items():
        try:
            decrypted.seek(0)
            df = pd.read_excel(
                decrypted,
                sheet_name=cfg["sheet"],
                skiprows=cfg["skip"],
                dtype=str
            )
            df.columns = [str(c).strip() for c in df.columns]
            df.dropna(how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            data[key] = df
            print(f"   ✅ {key}: {len(df)} rows loaded")
        except Exception as e:
            print(f"   ⚠️  Could not load '{cfg['sheet']}': {e}")
            data[key] = pd.DataFrame()

    return data


def refresh_data():
    """Force a fresh fetch — clears the cache."""
    _load_workbook.cache_clear()
    return _load_workbook()


# ── QUERY FUNCTIONS ───────────────────────────────────────────

def get_all_active_employees() -> pd.DataFrame:
    return _load_workbook()["active_employees"].copy()


def get_employee_by_id(emp_id: str) -> pd.DataFrame:
    data = _load_workbook()
    results = []
    for sheet_key in ["active_employees", "legacy_employees"]:
        df = data[sheet_key]
        id_col = next((c for c in df.columns if "emp" in c.lower() and "id" in c.lower()), None)
        if id_col:
            match = df[df[id_col].astype(str).str.strip() == str(emp_id).strip()]
            if not match.empty:
                match = match.copy()
                match["_source"] = sheet_key
                results.append(match)
    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


def get_employees_by_department(department: str) -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    dept_col = next((c for c in df.columns if "department" in c.lower()), None)
    if not dept_col:
        return pd.DataFrame()
    mask = df[dept_col].str.contains(department, case=False, na=False)
    return df[mask].reset_index(drop=True)


def get_employees_by_division(division: str) -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    div_col = next((c for c in df.columns if "division" in c.lower()), None)
    if not div_col:
        return pd.DataFrame()
    mask = df[div_col].str.contains(division, case=False, na=False)
    return df[mask].reset_index(drop=True)


def get_employees_by_nationality(nationality: str) -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    nat_col = next((c for c in df.columns if "nationality" in c.lower()), None)
    if not nat_col:
        return pd.DataFrame()
    mask = df[nat_col].str.contains(nationality, case=False, na=False)
    return df[mask].reset_index(drop=True)


def get_exited_employees(reason: str = None) -> pd.DataFrame:
    df = _load_workbook()["exited_employees"].copy()
    if reason:
        reason_col = next((c for c in df.columns if "reason" in c.lower()), None)
        if reason_col:
            mask = df[reason_col].str.contains(reason, case=False, na=False)
            df = df[mask].reset_index(drop=True)
    return df


def get_kra_by_employee(name_or_code: str) -> pd.DataFrame:
    df = _load_workbook()["kra"].copy()
    if df.empty:
        return df
    mask = df.apply(
        lambda row: row.astype(str).str.contains(name_or_code, case=False, na=False).any(),
        axis=1
    )
    return df[mask].reset_index(drop=True)


def get_headcount_by_department() -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    dept_col = next((c for c in df.columns if "department" in c.lower()), None)
    if not dept_col:
        return pd.DataFrame()
    return (
        df[dept_col]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Department", dept_col: "Headcount"})
    )


def get_headcount_by_nationality() -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    nat_col = next((c for c in df.columns if "nationality" in c.lower()), None)
    if not nat_col:
        return pd.DataFrame()
    return (
        df[nat_col]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Nationality", nat_col: "Headcount"})
    )


def get_blue_collar_ot_list() -> pd.DataFrame:
    return _load_workbook()["blue_collar_ot"].copy()


def get_white_collar_list() -> pd.DataFrame:
    return _load_workbook()["white_collar"].copy()


def get_outsource_employees() -> pd.DataFrame:
    return _load_workbook()["outsource"].copy()


def search_employees(query: str) -> pd.DataFrame:
    df = _load_workbook()["active_employees"].copy()
    mask = df.apply(
        lambda row: row.astype(str).str.contains(query, case=False, na=False).any(),
        axis=1
    )
    return df[mask].reset_index(drop=True)


# ── ENTRY POINT (manual test) ─────────────────────────────────

if __name__ == "__main__":
    print("\n=== FA Glass HR Module — Test Run ===\n")

    print("📊 Headcount by Department:")
    print(get_headcount_by_department().to_string(index=False))

    print("\n📊 Headcount by Nationality (top 10):")
    print(get_headcount_by_nationality().head(10).to_string(index=False))

    print("\n✅ Module loaded successfully.")
