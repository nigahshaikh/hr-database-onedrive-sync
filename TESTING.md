# FA Glass HR API - Testing Documentation

## Overview
This directory contains comprehensive testing suites for the FA Glass HR Database API. Tests verify that all endpoints are functioning correctly and returning actual data from the HR database.

## Test Files

### 1. `test_api.py` - Pytest Unit Tests
**Purpose**: Automated unit tests using pytest framework  
**Best For**: CI/CD pipelines, automated testing, regression testing

**Test Coverage**:
- ✓ Metadata endpoint validation
- ✓ Search employees (with various queries)
- ✓ Get employees by department
- ✓ Headcount by department
- ✓ Headcount by nationality
- ✓ Exited employees (all reasons)
- ✓ Data refresh functionality
- ✓ Response format consistency
- ✓ Data presence verification

**Classes**:
- `TestMetadataAndHealth` - Validates /meta endpoint
- `TestSearchEmployees` - Tests employee search with various queries
- `TestEmployeesByDepartment` - Tests department-based employee filtering
- `TestHeadcountByDepartment` - Validates department statistics
- `TestHeadcountByNationality` - Validates nationality statistics
- `TestExitedEmployees` - Tests employee exit reasons
- `TestRefreshData` - Tests data refresh functionality
- `TestResponseFormats` - Validates consistent response structure
- `TestDataPresence` - Confirms actual data exists in database

### 2. `test_api_manual.py` - Interactive Manual Tests
**Purpose**: Interactive testing with formatted output and real data display  
**Best For**: Development, debugging, demonstrations, manual validation

**Features**:
- Color-coded output (green for success, red for errors)
- Detailed data previews
- Section headers for easy navigation
- Real data samples from database
- Comprehensive summary statistics

**Test Sections**:
1. Metadata endpoint
2. Search employees
3. Employees by department
4. Headcount by department
5. Headcount by nationality
6. Exited employees
7. Data refresh
8. Overall summary

## Running the Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r test_requirements.txt

# Make sure the API is running
python -m uvicorn api:app --reload
```

### Option 1: Automated Tests (Pytest)

#### Run all tests with output
```bash
pytest test_api.py -v -s
```

#### Run specific test class
```bash
pytest test_api.py::TestSearchEmployees -v -s
```

#### Run specific test method
```bash
pytest test_api.py::TestSearchEmployees::test_search_employees_success -v -s
```

#### Run with coverage report
```bash
pytest test_api.py -v --cov=api --cov-report=html
```

#### Run tests and display print statements
```bash
pytest test_api.py -v -s --tb=short
```

### Option 2: Manual Interactive Tests

#### Run the interactive test suite
```bash
python test_api_manual.py
```

This will display:
- ✓ Connection verification
- ✓ API metadata
- ✓ Employee search results with samples
- ✓ Department information
- ✓ Headcount statistics
- ✓ Exited employees by reason
- ✓ Database statistics summary

## Expected Test Results

### Successful Test Run Output
```
✓ Metadata endpoint working - Found 6 actions
  Module: hr_master v1.0.0

✓ Search employees (all) - Found 150 employees
  Sample employee keys: ['Name', 'Email', 'Department', 'Status', ...]

✓ Found 8 departments: ['Sales', 'Finance', 'Technical', ...]

✓ Headcount by department - Found 8 departments

✓ Headcount by nationality - Found 15 nationalities

✓ Exited employees (all) - Found 12 employees
```

### What Gets Verified

1. **Status Codes**: All endpoints return HTTP 200
2. **Response Format**: All responses include required fields (status, data/error)
3. **Data Types**: Employees, departments, and statistics are properly formatted
4. **Actual Data**: Database contains employees, departments, and exit records
5. **Search Functionality**: Queries return correct filtered results
6. **Statistics**: Headcount and grouping calculations are working
7. **Error Handling**: Edge cases handled gracefully

## Sample Requests and Responses

### Search Employees
**Request**:
```json
POST /action/searchEmployees
{
  "query": "ahmed"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 3,
    "employees": [
      {
        "Name": "Ahmed Hassan",
        "Email": "ahmed.hassan@faglass.ae",
        "Department": "Sales",
        "Status": "Active",
        "Nationality": "Egyptian"
      }
    ]
  }
}
```

### Get Employees by Department
**Request**:
```json
POST /action/getEmployeesByDepartment
{
  "department": "Finance"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "department": "Finance",
    "count": 8,
    "employees": [...]
  }
}
```

### Headcount by Department
**Request**:
```json
POST /action/getHeadcountByDepartment
{}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "headcount": [
      {
        "Department": "Sales",
        "Count": 45
      },
      {
        "Department": "Finance",
        "Count": 8
      }
    ]
  }
}
```

## Troubleshooting

### Issue: "Connection refused"
**Solution**: Make sure API is running
```bash
python -m uvicorn api:app --reload
```

### Issue: "Module not found - hr_master_module"
**Solution**: Ensure `HR_Database.py` exists and is properly named as `hr_master_module.py`

### Issue: "No employees found in database"
**Solution**: Check that OneDrive connection is working and Excel file is accessible

### Issue: Tests pass but no sample data shown
**Solution**: Database may be empty. Run refresh:
```bash
python test_api_manual.py  # Will attempt refresh
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r test_requirements.txt
      - run: python -m uvicorn api:app &
      - run: pytest test_api.py -v
```

## Test Metrics

### Coverage
The test suite covers:
- ✓ 100% of API endpoints (6/6)
- ✓ All request/response patterns
- ✓ Error handling paths
- ✓ Data validation
- ✓ Search functionality
- ✓ Filtering operations

### Performance Baselines
- Metadata endpoint: <50ms
- Search endpoint: <100ms
- Headcount calculations: <200ms
- Data refresh: <5s

## Contributing

When adding new endpoints:
1. Add corresponding test to `test_api.py`
2. Add interactive test to `test_api_manual.py`
3. Run all tests: `pytest test_api.py -v`
4. Update this README with new test documentation

## Support

For issues or questions:
1. Check test output for specific error messages
2. Review API logs: Check terminal running the API server
3. Verify data source: Check OneDrive connection and Excel file
4. Run manual tests for interactive diagnostics: `python test_api_manual.py`
