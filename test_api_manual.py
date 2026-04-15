"""
Manual test script for FA Glass HR API
Run with: python test_api_manual.py
This script makes requests to the API and displays the results
"""

import json
import requests
from typing import Dict, Any
from pprint import pprint

BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI color codes for console output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}→ {message}{Colors.END}")

def test_metadata():
    """Test /meta endpoint"""
    print_section("1. METADATA ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/meta")
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Metadata retrieved successfully")
        print_info(f"Module: {data['moduleName']} v{data['moduleVersion']}")
        print_info(f"Protocol Version: {data['protocolVersion']}")
        print_info(f"Description: {data['description']}")
        print_info(f"Available Actions: {len(data['actions'])}")
        
        print(f"\n{Colors.BOLD}Actions:{Colors.END}")
        for action in data['actions']:
            print(f"  • {action['name']:<35} - {action['description']}")
        
        return data
    except Exception as e:
        print_error(f"Failed to get metadata: {e}")
        return None


def test_search_employees():
    """Test searchEmployees action"""
    print_section("2. SEARCH EMPLOYEES")
    
    queries = ["", "a", "sales"]
    
    for query in queries:
        try:
            print_info(f"Searching for: '{query}' (empty = all)")
            response = requests.post(
                f"{BASE_URL}/action/searchEmployees",
                json={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                count = data["data"]["count"]
                print_success(f"Found {count} employees")
                
                if data["data"]["employees"] and count > 0:
                    print(f"\n  {Colors.BOLD}Sample employees (first 3):{Colors.END}")
                    for emp in data["data"]["employees"][:3]:
                        name = emp.get("Name") or emp.get("name") or "Unknown"
                        dept = emp.get("Department") or emp.get("department") or "N/A"
                        print(f"    • {name} ({dept})")
            else:
                print_error(f"API returned failure: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print_error(f"Error searching: {e}")
        
        print()


def test_employees_by_department():
    """Test getEmployeesByDepartment action"""
    print_section("3. EMPLOYEES BY DEPARTMENT")
    
    try:
        # First get all departments
        print_info("Fetching all departments...")
        response = requests.post(
            f"{BASE_URL}/action/getHeadcountByDepartment",
            json={}
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            departments = data["data"]["headcount"]
            print_success(f"Found {len(departments)} departments")
            print(f"\n  {Colors.BOLD}Departments:{Colors.END}")
            for dept in departments[:5]:
                dept_name = dept.get("Department") or dept.get("department")
                count = dept.get("Count") or dept.get("count") or 0
                print(f"    • {dept_name}: {count} employees")
            
            # Get employees from first department
            if departments:
                dept_name = departments[0].get("Department") or departments[0].get("department")
                print_info(f"\nFetching employees from '{dept_name}'...")
                
                response = requests.post(
                    f"{BASE_URL}/action/getEmployeesByDepartment",
                    json={"department": dept_name}
                )
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "success":
                    count = data["data"]["count"]
                    print_success(f"Found {count} employees in {dept_name}")
                    
                    if data["data"]["employees"]:
                        print(f"\n  {Colors.BOLD}Sample employees:{Colors.END}")
                        for emp in data["data"]["employees"][:3]:
                            name = emp.get("Name") or emp.get("name") or "Unknown"
                            status = emp.get("Status") or emp.get("status") or "N/A"
                            print(f"    • {name} - {status}")
    except Exception as e:
        print_error(f"Error fetching departments: {e}")


def test_headcount_by_department():
    """Test getHeadcountByDepartment action"""
    print_section("4. HEADCOUNT BY DEPARTMENT")
    
    try:
        response = requests.post(
            f"{BASE_URL}/action/getHeadcountByDepartment",
            json={}
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            headcount = data["data"]["headcount"]
            print_success(f"Retrieved headcount for {len(headcount)} departments")
            
            print(f"\n  {Colors.BOLD}Department Headcount:{Colors.END}")
            for dept in headcount:
                dept_name = dept.get("Department") or dept.get("department") or "Unknown"
                count = dept.get("Count") or dept.get("count") or 0
                print(f"    • {dept_name:<30} : {count} employees")
        else:
            print_error(f"API returned failure: {data.get('error', {}).get('message')}")
    except Exception as e:
        print_error(f"Error: {e}")


def test_headcount_by_nationality():
    """Test getHeadcountByNationality action"""
    print_section("5. HEADCOUNT BY NATIONALITY")
    
    try:
        response = requests.post(
            f"{BASE_URL}/action/getHeadcountByNationality",
            json={}
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            headcount = data["data"]["headcount"]
            print_success(f"Retrieved headcount for {len(headcount)} nationalities")
            
            print(f"\n  {Colors.BOLD}Nationality Headcount:{Colors.END}")
            for nat in headcount:
                nat_name = nat.get("Nationality") or nat.get("nationality") or "Unknown"
                count = nat.get("Count") or nat.get("count") or 0
                print(f"    • {nat_name:<30} : {count} employees")
        else:
            print_error(f"API returned failure: {data.get('error', {}).get('message')}")
    except Exception as e:
        print_error(f"Error: {e}")


def test_exited_employees():
    """Test getExitedEmployees action"""
    print_section("6. EXITED EMPLOYEES")
    
    reasons = [None, "Resigned", "Terminated", "Absconded"]
    
    for reason in reasons:
        try:
            reason_str = reason if reason else "All"
            print_info(f"Fetching exited employees ({reason_str})...")
            
            payload = {}
            if reason:
                payload["reason"] = reason
            
            response = requests.post(
                f"{BASE_URL}/action/getExitedEmployees",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                count = data["data"]["count"]
                print_success(f"Found {count} exited employees ({reason_str})")
                
                if data["data"]["employees"] and count > 0:
                    print(f"  {Colors.BOLD}Sample:{Colors.END}")
                    for emp in data["data"]["employees"][:2]:
                        name = emp.get("Name") or emp.get("name") or "Unknown"
                        exit_reason = emp.get("Exit Reason") or emp.get("exit_reason") or "N/A"
                        print(f"    • {name} - Reason: {exit_reason}")
            else:
                print_error(f"API returned failure: {data.get('error', {}).get('message')}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        print()


def test_refresh_data():
    """Test refreshData action"""
    print_section("7. REFRESH DATA")
    
    try:
        print_info("Refreshing HR data from OneDrive...")
        response = requests.post(
            f"{BASE_URL}/action/refreshData",
            json={}
        )
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            message = data["data"]["message"]
            print_success(message)
        else:
            print_error(f"API returned failure: {data.get('error', {}).get('message')}")
    except Exception as e:
        print_error(f"Error: {e}")


def test_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")
    
    try:
        response = requests.post(
            f"{BASE_URL}/action/searchEmployees",
            json={"query": ""}
        )
        response.raise_for_status()
        total_employees = response.json()["data"]["count"]
        
        response = requests.post(
            f"{BASE_URL}/action/getHeadcountByDepartment",
            json={}
        )
        response.raise_for_status()
        total_departments = len(response.json()["data"]["headcount"])
        
        response = requests.post(
            f"{BASE_URL}/action/getHeadcountByNationality",
            json={}
        )
        response.raise_for_status()
        total_nationalities = len(response.json()["data"]["headcount"])
        
        print(f"{Colors.BOLD}HR Database Statistics:{Colors.END}")
        print(f"  • Total Employees: {total_employees}")
        print(f"  • Total Departments: {total_departments}")
        print(f"  • Total Nationalities: {total_nationalities}")
        
        print_success("All API tests completed successfully!")
        
    except Exception as e:
        print_error(f"Error generating summary: {e}")


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}FA Glass HR Database API - Manual Test Suite{Colors.END}")
    print(f"{Colors.YELLOW}Base URL: {BASE_URL}{Colors.END}")
    
    try:
        # Check if API is running
        print_info("Checking API connection...")
        response = requests.get(f"{BASE_URL}/meta", timeout=5)
        if response.status_code == 200:
            print_success("✓ API is running and responding")
        else:
            print_error("API is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print_info("Make sure the API is running: python -m uvicorn api:app --reload")
        return
    
    # Run all tests
    test_metadata()
    test_search_employees()
    test_employees_by_department()
    test_headcount_by_department()
    test_headcount_by_nationality()
    test_exited_employees()
    test_refresh_data()
    test_summary()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}Testing completed!{Colors.END}\n")


if __name__ == "__main__":
    main()
