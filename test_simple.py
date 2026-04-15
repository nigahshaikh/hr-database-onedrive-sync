#!/usr/bin/env python
"""Simple test to debug the API issue"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("SIMPLE API TEST")
print("=" * 70)

# Test 1: Metadata
print("\n1. Testing /meta endpoint...")
try:
    resp = requests.get(f"{BASE_URL}/meta")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL: {resp.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Search Employees (empty query)
print("\n2. Testing /action/searchEmployees with empty query...")
try:
    resp = requests.post(
        f"{BASE_URL}/action/searchEmployees",
        json={"query": ""}
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: {json.dumps(data, indent=2)[:500]}")
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL: {resp.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Direct module test
print("\n3. Testing hr_master_module directly...")
try:
    import hr_master_module as hr
    print("   Loading employees...")
    df = hr.get_all_active_employees()
    print(f"   Loaded: {len(df)} employees")
    if len(df) > 0:
        print(f"   First employee: {df.iloc[0, :5].to_dict()}")
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL: No employees loaded")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
