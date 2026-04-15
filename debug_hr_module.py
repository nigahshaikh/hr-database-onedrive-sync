"""
Diagnostic script to debug hr_master_module data loading
"""

import sys
import traceback
from hr_master_module import (
    _load_workbook, 
    get_all_active_employees,
    get_headcount_by_department,
    get_headcount_by_nationality,
    get_exited_employees,
    SHEET_CONFIG
)

print("=" * 70)
print("HR MASTER MODULE - DEBUG DIAGNOSTICS")
print("=" * 70)

# 1. Check configuration
print("\n1️⃣  MODULE CONFIGURATION:")
print(f"   OneDrive URL: {SHEET_CONFIG}")
for sheet_key, config in SHEET_CONFIG.items():
    print(f"   • {sheet_key}: Sheet='{config['sheet']}', Skip={config['skip']}")

# 2. Try to load workbook
print("\n2️⃣  LOADING WORKBOOK...")
try:
    data = _load_workbook()
    print("   ✅ Workbook loaded")
    
    # Print what was loaded
    print("\n3️⃣  DATA LOADED BY SHEET:")
    for sheet_key, df in data.items():
        rows = len(df) if not df.empty else 0
        cols = len(df.columns) if not df.empty else 0
        print(f"   • {sheet_key}: {rows} rows × {cols} columns")
        if rows > 0:
            print(f"      Columns: {list(df.columns)[:5]}{'...' if cols > 5 else ''}")
            print(f"      Sample (first row): {df.iloc[0, :min(3, cols)].to_dict()}")
        else:
            print(f"      ⚠️  EMPTY!")
    
except Exception as e:
    print(f"   ❌ ERROR loading workbook:")
    print(f"      {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

# 3. Test each query function
print("\n4️⃣  TESTING QUERY FUNCTIONS:")

try:
    result = get_all_active_employees()
    print(f"   • get_all_active_employees(): {len(result)} rows")
except Exception as e:
    print(f"   • get_all_active_employees(): ❌ {e}")

try:
    result = get_headcount_by_department()
    print(f"   • get_headcount_by_department(): {len(result)} rows")
    if len(result) > 0:
        print(f"      {result.head().to_string()}")
except Exception as e:
    print(f"   • get_headcount_by_department(): ❌ {e}")

try:
    result = get_headcount_by_nationality()
    print(f"   • get_headcount_by_nationality(): {len(result)} rows")
    if len(result) > 0:
        print(f"      {result.head().to_string()}")
except Exception as e:
    print(f"   • get_headcount_by_nationality(): ❌ {e}")

try:
    result = get_exited_employees()
    print(f"   • get_exited_employees(): {len(result)} rows")
except Exception as e:
    print(f"   • get_exited_employees(): ❌ {e}")

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)
print("\n📝 NEXT STEPS:")
print("   1. Check if OneDrive URL is accessible")
print("   2. Verify password 'zed' is correct")
print("   3. Confirm sheet names match Excel file")
print("   4. Ensure Excel file has data in specified sheets")
