from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import hr_master_module as hr
import pandas as pd
import math
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

METADATA = {
    "protocolVersion": 3,
    "moduleVersion": "2.0.0",
    "moduleName": "hr_master",
    "description": (
        "Provides real-time read-only access to the FA Glass employee master data. "
        "Use this module to search employees, retrieve personal details, contact information, "
        "document expiry dates, headcount summaries, and separation records. "
        "Data is sourced live from Zahid Khan's Excel master file on OneDrive."
    ),
    "actions": [
        {
            "name": "searchEmployees",
            "description": "Search all active employees by any keyword — name, employee ID, department, nationality, or designation. Returns matching employee records.",
            "route": "/action/searchEmployees",
            "riskLevel": "safe",
            "pictogram": "user--search",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Any search term: employee name, ID, department, designation, or nationality."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "getEmployeeDetails",
            "description": (
                "Returns full personal and employment details for a matched employee. "
                "Includes: Emp.ID, Department, DOB, Passport, Passport Expiry Date, Visa Expiry Date, "
                "Emirates ID, Contact Number UAE, Contact Home Country, Address in Home Country, "
                "Highest Qualification, School/University, Year of Completion, Email ID, "
                "Gender, Marital Status, Religion, Probation Completion Details, Service Tenure."
            ),
            "route": "/action/getEmployeeDetails",
            "riskLevel": "safe",
            "pictogram": "user--profile",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Employee name or Emp.ID to look up."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "getEmployeeContactInfo",
            "description": (
                "Returns contact details for a specific employee. "
                "Includes: Emp.ID, Contact Number UAE, Contact Home Country, "
                "Address in Home Country, Email ID."
            ),
            "route": "/action/getEmployeeContactInfo",
            "riskLevel": "safe",
            "pictogram": "phone",
            "typicalHumanProcessTime": 30,
            "input": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Employee name or Emp.ID."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "getEmployeesByDepartment",
            "description": "Returns all active employees belonging to a specified department.",
            "route": "/action/getEmployeesByDepartment",
            "riskLevel": "safe",
            "pictogram": "group",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Department name e.g. Sales, Finance, Technical, HR, IT."
                    }
                },
                "required": ["department"]
            }
        },
        {
            "name": "getEmployeesByGender",
            "description": "Returns all active employees filtered by gender.",
            "route": "/action/getEmployeesByGender",
            "riskLevel": "safe",
            "pictogram": "person",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "gender": {
                        "type": "string",
                        "description": "Gender value e.g. Male, Female."
                    }
                },
                "required": ["gender"]
            }
        },
        {
            "name": "getEmployeesByReligion",
            "description": "Returns all active employees filtered by religion.",
            "route": "/action/getEmployeesByReligion",
            "riskLevel": "safe",
            "pictogram": "person",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "religion": {
                        "type": "string",
                        "description": "Religion value e.g. Islam, Hindu, Christian."
                    }
                },
                "required": ["religion"]
            }
        },
        {
            "name": "getEmployeesByMaritalStatus",
            "description": "Returns all active employees filtered by marital status.",
            "route": "/action/getEmployeesByMaritalStatus",
            "riskLevel": "safe",
            "pictogram": "person",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Marital status e.g. Single, Married, Divorced."
                    }
                },
                "required": ["status"]
            }
        },
        {
            "name": "getEmployeesByQualification",
            "description": "Returns all active employees filtered by highest educational qualification.",
            "route": "/action/getEmployeesByQualification",
            "riskLevel": "safe",
            "pictogram": "education",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "qualification": {
                        "type": "string",
                        "description": "Qualification level e.g. Bachelor, Master, Diploma, High School."
                    }
                },
                "required": ["qualification"]
            }
        },
        {
            "name": "getExpiringPassports",
            "description": (
                "Returns active employees whose passport is expiring within a given number of days. "
                "Useful for proactive HR document management. Defaults to 90 days if not specified."
            ),
            "route": "/action/getExpiringPassports",
            "riskLevel": "safe",
            "pictogram": "warning",
            "typicalHumanProcessTime": 120,
            "input": {
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead. Default is 90."
                    }
                }
            }
        },
        {
            "name": "getExpiringVisas",
            "description": (
                "Returns active employees whose visa is expiring within a given number of days. "
                "Useful for proactive HR document management. Defaults to 90 days if not specified."
            ),
            "route": "/action/getExpiringVisas",
            "riskLevel": "safe",
            "pictogram": "warning",
            "typicalHumanProcessTime": 120,
            "input": {
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead. Default is 90."
                    }
                }
            }
        },
        {
            "name": "getHeadcountByDepartment",
            "description": "Returns a summary of active employee headcount grouped by department.",
            "route": "/action/getHeadcountByDepartment",
            "riskLevel": "safe",
            "pictogram": "chart--bar",
            "typicalHumanProcessTime": 120,
            "input": {"type": "object", "properties": {}}
        },
        {
            "name": "getHeadcountByNationality",
            "description": "Returns a summary of active employee headcount grouped by nationality.",
            "route": "/action/getHeadcountByNationality",
            "riskLevel": "safe",
            "pictogram": "earth",
            "typicalHumanProcessTime": 120,
            "input": {"type": "object", "properties": {}}
        },
        {
            "name": "getExitedEmployees",
            "description": "Returns employees who have left FA Glass. Optionally filter by separation reason.",
            "route": "/action/getExitedEmployees",
            "riskLevel": "safe",
            "pictogram": "logout",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Optional separation reason filter e.g. Resigned, Terminated, Absconded."
                    }
                }
            }
        },
        {
            "name": "getExitedEmployeeDetails",
            "description": (
                "Returns full exit record for a searched employee. "
                "Includes: DOJ, Designation, Grade, Category, Division, Department, Section, "
                "Work Location, Nationality, DOB, Passport, Passport Expiry Date, Visa Expiry Date, "
                "Emirates ID, Contact Number UAE, Contact Home Country, Address in Home Country, "
                "Highest Qualification, School/University, Year of Completion, Email ID, "
                "Gender, Marital Status, Religion, Probation Completion Details, Service Tenure, "
                "Last Working Date, Reason for Separation."
            ),
            "route": "/action/getExitedEmployeeDetails",
            "riskLevel": "safe",
            "pictogram": "user--profile",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Exited employee name or ID."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "getExitsByDepartment",
            "description": "Returns all exited employees from a specified department with full exit details.",
            "route": "/action/getExitsByDepartment",
            "riskLevel": "safe",
            "pictogram": "logout",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Department name."
                    }
                },
                "required": ["department"]
            }
        },
        {
            "name": "getExitsByReason",
            "description": "Returns all exited employees filtered by their separation reason.",
            "route": "/action/getExitsByReason",
            "riskLevel": "safe",
            "pictogram": "logout",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Separation reason e.g. Resigned, Terminated, Absconded."
                    }
                },
                "required": ["reason"]
            }
        },
        {
            "name": "getExitsByDesignation",
            "description": "Returns all exited employees filtered by their job designation.",
            "route": "/action/getExitsByDesignation",
            "riskLevel": "safe",
            "pictogram": "logout",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "designation": {
                        "type": "string",
                        "description": "Job designation e.g. Engineer, Manager, Supervisor, Operator."
                    }
                },
                "required": ["designation"]
            }
        },
        {
            "name": "getExitsByDivision",
            "description": "Returns all exited employees filtered by division.",
            "route": "/action/getExitsByDivision",
            "riskLevel": "safe",
            "pictogram": "logout",
            "typicalHumanProcessTime": 60,
            "input": {
                "type": "object",
                "properties": {
                    "division": {
                        "type": "string",
                        "description": "Division name e.g. Glass, Glazing."
                    }
                },
                "required": ["division"]
            }
        },
        {
            "name": "getExitsSummaryByReason",
            "description": "Returns a count of all employee exits grouped by separation reason.",
            "route": "/action/getExitsSummaryByReason",
            "riskLevel": "safe",
            "pictogram": "chart--bar",
            "typicalHumanProcessTime": 120,
            "input": {"type": "object", "properties": {}}
        },
        {
            "name": "getExitsSummaryByDepartment",
            "description": "Returns a count of all employee exits grouped by department.",
            "route": "/action/getExitsSummaryByDepartment",
            "riskLevel": "safe",
            "pictogram": "chart--bar",
            "typicalHumanProcessTime": 120,
            "input": {"type": "object", "properties": {}}
        },
        {
            "name": "refreshData",
            "description": (
                "Clears the cached HR data and forces a fresh fetch from Zahid's OneDrive Excel file. "
                "Use this whenever Zahid has updated the master file to ensure the Synth is working with current data."
            ),
            "route": "/action/refreshData",
            "riskLevel": "safe",
            "pictogram": "renew",
            "typicalHumanProcessTime": 30,
            "input": {"type": "object", "properties": {}}
        }
    ],
    "data": []
}

# ── META ──────────────────────────────────────────────────────

@app.get("/meta")
def meta():
    return JSONResponse(METADATA)

# ── HELPER ────────────────────────────────────────────────────

async def parse_body(request: Request) -> dict:
    body = await request.body()
    if not body:
        return {}
    return await request.json()

def df_to_json_safe(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-safe list of dicts, handling NaN and inf values."""
    if df.empty:
        return []
    records = []
    for _, row in df.iterrows():
        record = {}
        for col, val in row.items():
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (datetime, pd.Timestamp)):
                record[col] = str(val)
            elif isinstance(val, float):
                # JSON doesn't support NaN, Inf, or -Inf
                if math.isfinite(val):
                    record[col] = val
                else:
                    record[col] = None
            elif isinstance(val, (int, bool)):
                record[col] = val
            elif isinstance(val, str):
                record[col] = val
            else:
                record[col] = str(val)
        records.append(record)
    return records

# ── ACTION ENDPOINTS ──────────────────────────────────────────

@app.post("/action/searchEmployees")
async def search_employees(request: Request):
    try:
        payload = await parse_body(request)
        query = payload.get("query", "")
        df = hr.search_employees(query)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeeDetails")
async def get_employee_details(request: Request):
    try:
        payload = await parse_body(request)
        query = payload.get("query", "")
        df = hr.get_employee_details(query)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeeContactInfo")
async def get_employee_contact_info(request: Request):
    try:
        payload = await parse_body(request)
        query = payload.get("query", "")
        df = hr.get_employee_contact_info(query)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeesByDepartment")
async def get_by_department(request: Request):
    try:
        payload = await parse_body(request)
        dept = payload.get("department", "")
        df = hr.get_employees_by_department(dept)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"department": dept, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeesByGender")
async def get_by_gender(request: Request):
    try:
        payload = await parse_body(request)
        gender = payload.get("gender", "")
        df = hr.get_employees_by_gender(gender)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"gender": gender, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeesByReligion")
async def get_by_religion(request: Request):
    try:
        payload = await parse_body(request)
        religion = payload.get("religion", "")
        df = hr.get_employees_by_religion(religion)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"religion": religion, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeesByMaritalStatus")
async def get_by_marital_status(request: Request):
    try:
        payload = await parse_body(request)
        status = payload.get("status", "")
        df = hr.get_employees_by_marital_status(status)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"marital_status": status, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getEmployeesByQualification")
async def get_by_qualification(request: Request):
    try:
        payload = await parse_body(request)
        qualification = payload.get("qualification", "")
        df = hr.get_employees_by_qualification(qualification)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"qualification": qualification, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExpiringPassports")
async def get_expiring_passports(request: Request):
    try:
        payload = await parse_body(request)
        days = int(payload.get("days_ahead", 90))
        df = hr.get_employees_expiring_passports(days)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"days_ahead": days, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExpiringVisas")
async def get_expiring_visas(request: Request):
    try:
        payload = await parse_body(request)
        days = int(payload.get("days_ahead", 90))
        df = hr.get_employees_expiring_visas(days)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"days_ahead": days, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getHeadcountByDepartment")
async def headcount_by_dept(request: Request):
    try:
        payload = await parse_body(request)
        df = hr.get_headcount_by_department()
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"headcount": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getHeadcountByNationality")
async def headcount_by_nat(request: Request):
    try:
        payload = await parse_body(request)
        df = hr.get_headcount_by_nationality()
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"headcount": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitedEmployees")
async def exited_employees(request: Request):
    try:
        payload = await parse_body(request)
        reason = payload.get("reason", None)
        df = hr.get_exited_employees(reason)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitedEmployeeDetails")
async def exited_employee_details(request: Request):
    try:
        payload = await parse_body(request)
        query = payload.get("query", "")
        df = hr.get_exited_employee_details(query)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsByDepartment")
async def exits_by_dept(request: Request):
    try:
        payload = await parse_body(request)
        dept = payload.get("department", "")
        df = hr.get_exits_by_department(dept)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"department": dept, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsByReason")
async def exits_by_reason(request: Request):
    try:
        payload = await parse_body(request)
        reason = payload.get("reason", "")
        df = hr.get_exits_by_reason(reason)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"reason": reason, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsByDesignation")
async def exits_by_designation(request: Request):
    try:
        payload = await parse_body(request)
        designation = payload.get("designation", "")
        df = hr.get_exits_by_designation(designation)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"designation": designation, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsByDivision")
async def exits_by_division(request: Request):
    try:
        payload = await parse_body(request)
        division = payload.get("division", "")
        df = hr.get_exits_by_division(division)
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"division": division, "count": len(records), "employees": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsSummaryByReason")
async def exits_summary_by_reason(request: Request):
    try:
        payload = await parse_body(request)
        df = hr.get_exits_summary_by_reason()
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"summary": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/getExitsSummaryByDepartment")
async def exits_summary_by_dept(request: Request):
    try:
        payload = await parse_body(request)
        df = hr.get_exits_summary_by_department()
        records = df_to_json_safe(df)
        return {"status": "success", "data": {"summary": records}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}

@app.post("/action/refreshData")
async def refresh_data(request: Request):
    try:
        payload = await parse_body(request)
        hr.refresh_data()
        return {"status": "success", "data": {"message": "HR data refreshed from OneDrive successfully."}}
    except Exception as e:
        return {"status": "failure", "error": {"message": str(e)}}