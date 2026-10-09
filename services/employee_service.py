import secrets
from typing import Any

from playwright.sync_api import Page


def _validated_pagination_page(
    response: Any, endpoint: str
) -> tuple[list[Any], int]:
    if not response.ok:
        raise RuntimeError(
            f"Failed to fetch {endpoint}: HTTP {response.status}"
        )

    try:
        payload = response.json()
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            f"Invalid JSON response from {endpoint}"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            f"Invalid pagination response from {endpoint}: "
            "expected a JSON object"
        )

    batch = payload.get("data")
    if not isinstance(batch, list):
        raise RuntimeError(
            f"Invalid pagination response from {endpoint}: "
            "'data' must be a list"
        )

    metadata = payload.get("meta")
    if not isinstance(metadata, dict) or "total" not in metadata:
        raise RuntimeError(
            f"Invalid pagination response from {endpoint}: "
            "'meta.total' is required"
        )

    total = metadata["total"]
    if type(total) is not int or total < 0:
        raise RuntimeError(
            f"Invalid pagination response from {endpoint}: "
            "'meta.total' must be a non-negative integer"
        )

    return batch, total


class EmployeeService:

    @staticmethod
    def get_available_employee(page):
        # Get all employees
        employees = []
        offset = 0
        limit = 50
        expected_total = None
        base_url = "https://opensource-demo.orangehrmlive.com"

        while True:

            response = page.request.get(
                f"{base_url}/web/index.php/api/v2/pim/employees"
                f"?limit={limit}&offset={offset}"
            )

            batch, total = _validated_pagination_page(
                response, "employee list"
            )
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise RuntimeError(
                    "Employee pagination metadata changed during retrieval: "
                    f"expected {expected_total} records, got {total}"
                )
            employees.extend(batch)

            if len(employees) >= total:
                break

            if not batch:
                raise RuntimeError(
                    "Employee pagination made no progress: "
                    f"received an empty page at {len(employees)} of {total} records"
                )

            offset += len(batch)

        # Get all existing System Users
        system_users = []
        offset = 0
        expected_total = None

        while True:
            response = page.request.get(
                f"{base_url}/web/index.php/api/v2/admin/users"
                f"?limit={limit}&offset={offset}"
            )

            batch, total = _validated_pagination_page(
                response, "system-user list"
            )
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise RuntimeError(
                    "System-user pagination metadata changed during "
                    f"retrieval: expected {expected_total} records, got {total}"
                )
            system_users.extend(batch)

            if len(system_users) >= total:
                break

            if not batch:
                raise RuntimeError(
                    "System-user pagination made no progress: "
                    f"received an empty page at "
                    f"{len(system_users)} of {total} records"
                )

            offset += len(batch)

        # Employees who already have a System User account
        assigned_employee_numbers = {
            user["employee"]["empNumber"]
            for user in system_users
            if user.get("employee")
            and user.get("deleted", False) is False
        }

        # Find an active employee without a System User account
        for employee in employees:

            if employee.get("terminationId") is not None:
                continue

            emp_number = employee.get("empNumber")

            if emp_number in assigned_employee_numbers:
                continue

            employee_id = employee.get("employeeId")
            first_name = employee.get("firstName", "")
            middle_name = employee.get("middleName", "")
            last_name = employee.get("lastName", "")

            employee_name = " ".join(
                part
                for part in [first_name, middle_name, last_name]
                if part
            )

            if not employee_id or not employee_name:
                continue

            return {
                "empNumber": emp_number,
                "employeeId": employee_id,
                "employeeName": employee_name,
                "firstName": first_name,
                "middleName": middle_name,
                "lastName": last_name,
            }

        raise RuntimeError(
            "No active employee without an existing System User "
            "account was found."
        )

    @staticmethod
    def generate_unused_employee_id(page: Page) -> str:
        employees: list[dict] = []
        offset = 0
        limit = 50
        total = 1
        expected_total = None

        endpoint = (
            "https://opensource-demo.orangehrmlive.com"
            "/web/index.php/api/v2/pim/employees"
        )

        while offset < total:
            response = page.request.get(
                endpoint,
                params={
                    "limit": limit,
                    "offset": offset
                },
            )

            batch, total = _validated_pagination_page(
                response, "employee list"
            )
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise RuntimeError(
                    "Employee pagination metadata changed during retrieval: "
                    f"expected {expected_total} records, got {total}"
                )

            employees.extend(batch)

            if not batch and offset < total:
                raise RuntimeError(
                    f"Employee pagination made no progress at "
                    f"{len(employees)} of {total}"
                )

            offset += len(batch)

        existing_ids = {
            str(employee["employeeId"])
            for employee in employees
            if employee.get("employeeId") is not None
        }

        available_ids = [
            str(employee_id)
            for employee_id in range(1000, 10000)
            if str(employee_id) not in existing_ids
        ]

        if not available_ids:
            raise RuntimeError(
                "No unused 4-digit Employee Id is available"
            )

        return secrets.choice(available_ids)