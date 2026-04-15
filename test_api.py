"""
Comprehensive test suite for FA Glass HR Database API
Tests all endpoints to verify they return actual data
Run with: pytest test_api.py -v
"""

import pytest
import json
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


class TestMetadataAndHealth:
    """Test metadata and health endpoints"""
    
    def test_metadata_endpoint(self):
        """Test /meta endpoint returns METADATA"""
        response = client.get("/meta")
        assert response.status_code == 200
        data = response.json()
        
        # Verify METADATA structure
        assert "protocolVersion" in data
        assert "moduleVersion" in data
        assert "moduleName" in data
        assert data["moduleName"] == "hr_master"
        assert "actions" in data
        assert len(data["actions"]) > 0
        
        print(f"✓ Metadata endpoint working - Found {len(data['actions'])} actions")
        print(f"  Module: {data['moduleName']} v{data['moduleVersion']}")


class TestSearchEmployees:
    """Test searchEmployees action"""
    
    def test_search_employees_success(self):
        """Test searching for employees with a valid query"""
        response = client.post(
            "/action/searchEmployees",
            json={"query": ""}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert "count" in data["data"]
        assert "employees" in data["data"]
        
        print(f"✓ Search employees (all) - Found {data['data']['count']} employees")
        if data['data']['employees']:
            emp = data['data']['employees'][0]
            print(f"  Sample employee keys: {list(emp.keys())}")
    
    def test_search_employees_by_name(self):
        """Test searching for employees by name"""
        response = client.post(
            "/action/searchEmployees",
            json={"query": "a"}  # Search for names containing 'a'
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        count = data["data"]["count"]
        print(f"✓ Search employees by name 'a' - Found {count} employees")
    
    def test_search_employees_no_results(self):
        """Test searching with a query that has no results"""
        response = client.post(
            "/action/searchEmployees",
            json={"query": "xyznonexistentquery123"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["count"] == 0
        print(f"✓ Search with non-existent query - Correctly returned 0 results")
    
    def test_search_employees_missing_query(self):
        """Test search with missing query parameter"""
        response = client.post(
            "/action/searchEmployees",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should handle missing query gracefully
        assert "status" in data
        print(f"✓ Search with missing query handled gracefully - Status: {data['status']}")


class TestEmployeesByDepartment:
    """Test getEmployeesByDepartment action"""
    
    def test_get_all_departments_first(self):
        """First, get headcount by department to find available departments"""
        response = client.post(
            "/action/getHeadcountByDepartment",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        departments = data["data"]["headcount"]
        print(f"✓ Found {len(departments)} departments: {[d.get('Department', d.get('department', '?')) for d in departments[:3]]}...")
        
        return departments
    
    def test_get_employees_by_department(self):
        """Test getting employees from a specific department"""
        # First get a list of departments
        response = client.post(
            "/action/getHeadcountByDepartment",
            json={}
        )
        departments = response.json()["data"]["headcount"]
        
        if departments:
            # Get first department - key is 'Headcount' not 'Department'
            dept_name = departments[0].get("Headcount") or departments[0].get("Headcount") or departments[0].get("Department") or departments[0].get("department")
            
            response = client.post(
                "/action/getEmployeesByDepartment",
                json={"department": dept_name}
            )
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert data["data"]["department"] == dept_name
            assert "count" in data["data"]
            assert "employees" in data["data"]
            
            count = data["data"]["count"]
            print(f"✓ Get employees by department '{dept_name}' - Found {count} employees")
            
            if data["data"]["employees"]:
                emp = data["data"]["employees"][0]
                print(f"  Sample employee keys: {list(emp.keys())}")


class TestHeadcountByDepartment:
    """Test getHeadcountByDepartment action"""
    
    def test_headcount_by_department(self):
        """Test getting headcount grouped by department"""
        response = client.post(
            "/action/getHeadcountByDepartment",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert "headcount" in data["data"]
        
        headcount = data["data"]["headcount"]
        print(f"✓ Headcount by department - Found {len(headcount)} departments")
        
        for dept in headcount[:3]:
            print(f"  {dept}")


class TestHeadcountByNationality:
    """Test getHeadcountByNationality action"""
    
    def test_headcount_by_nationality(self):
        """Test getting headcount grouped by nationality"""
        response = client.post(
            "/action/getHeadcountByNationality",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert "headcount" in data["data"]
        
        headcount = data["data"]["headcount"]
        print(f"✓ Headcount by nationality - Found {len(headcount)} nationalities")
        
        for nat in headcount[:3]:
            print(f"  {nat}")


class TestExitedEmployees:
    """Test getExitedEmployees action"""
    
    def test_get_all_exited_employees(self):
        """Test getting all exited employees without filter"""
        response = client.post(
            "/action/getExitedEmployees",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert "count" in data["data"]
        assert "employees" in data["data"]
        
        count = data["data"]["count"]
        print(f"✓ Exited employees (all) - Found {count} employees")
        
        if data["data"]["employees"]:
            emp = data["data"]["employees"][0]
            print(f"  Sample employee keys: {list(emp.keys())}")
    
    def test_get_resigned_employees(self):
        """Test getting employees who resigned"""
        response = client.post(
            "/action/getExitedEmployees",
            json={"reason": "Resigned"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        count = data["data"]["count"]
        print(f"✓ Exited employees (Resigned) - Found {count} employees")
    
    def test_get_terminated_employees(self):
        """Test getting employees who were terminated"""
        response = client.post(
            "/action/getExitedEmployees",
            json={"reason": "Terminated"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        count = data["data"]["count"]
        print(f"✓ Exited employees (Terminated) - Found {count} employees")
    
    def test_get_absconded_employees(self):
        """Test getting employees who absconded"""
        response = client.post(
            "/action/getExitedEmployees",
            json={"reason": "Absconded"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        count = data["data"]["count"]
        print(f"✓ Exited employees (Absconded) - Found {count} employees")


class TestRefreshData:
    """Test refreshData action"""
    
    def test_refresh_data(self):
        """Test refreshing data from OneDrive"""
        response = client.post(
            "/action/refreshData",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "data" in data
        assert "message" in data["data"]
        
        message = data["data"]["message"]
        print(f"✓ Refresh data - {message}")


class TestResponseFormats:
    """Test response format consistency"""
    
    def test_all_responses_have_status(self):
        """Verify all action responses have status field"""
        actions = [
            ("/action/searchEmployees", {"query": ""}),
            ("/action/getEmployeesByDepartment", {"department": ""}),
            ("/action/getHeadcountByDepartment", {}),
            ("/action/getHeadcountByNationality", {}),
            ("/action/getExitedEmployees", {}),
            ("/action/refreshData", {}),
        ]
        
        for endpoint, payload in actions:
            response = client.post(endpoint, json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data, f"{endpoint} missing status field"
            assert data["status"] in ["success", "failure"], f"{endpoint} has invalid status"
        
        print(f"✓ All {len(actions)} endpoints have consistent response format with status field")
    
    def test_all_responses_have_data_or_error(self):
        """Verify all responses have either data or error field"""
        actions = [
            ("/action/searchEmployees", {"query": ""}),
            ("/action/getHeadcountByDepartment", {}),
        ]
        
        for endpoint, payload in actions:
            response = client.post(endpoint, json=payload)
            data = response.json()
            assert ("data" in data) or ("error" in data), f"{endpoint} missing data or error"
        
        print(f"✓ All responses have consistent structure with data/error fields")


class TestDataPresence:
    """Test that actual data is being returned from HR module"""
    
    def test_at_least_one_employee_exists(self):
        """Verify at least one employee exists in database"""
        response = client.post(
            "/action/searchEmployees",
            json={"query": ""}
        )
        data = response.json()
        assert data["data"]["count"] > 0, "No employees found in database"
        print(f"✓ Database contains {data['data']['count']} employees")
    
    def test_departments_exist(self):
        """Verify at least one department exists"""
        response = client.post(
            "/action/getHeadcountByDepartment",
            json={}
        )
        data = response.json()
        assert len(data["data"]["headcount"]) > 0, "No departments found"
        print(f"✓ Database contains {len(data['data']['headcount'])} departments")
    
    def test_nationalities_exist(self):
        """Verify at least one nationality exists"""
        response = client.post(
            "/action/getHeadcountByNationality",
            json={}
        )
        data = response.json()
        assert len(data["data"]["headcount"]) > 0, "No nationalities found"
        print(f"✓ Database contains {len(data['data']['headcount'])} nationalities")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
