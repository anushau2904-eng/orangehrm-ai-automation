from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from services.employee_service import (
    EmployeeService,
    _validated_pagination_page,
)


class StubResponse:
    def __init__(
        self,
        payload: Any,
        *,
        status: int = 200,
        json_error: Exception | None = None,
    ) -> None:
        self.ok = 200 <= status < 400
        self.status = status
        self.payload = payload
        self.json_error = json_error

    def json(self) -> Any:
        if self.json_error is not None:
            raise self.json_error
        return self.payload


class StubRequest:
    def __init__(self, responses: list[StubResponse]) -> None:
        self.responses = iter(responses)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, url: str, **kwargs: Any) -> StubResponse:
        self.calls.append((url, kwargs))
        try:
            return next(self.responses)
        except StopIteration as exc:
            raise AssertionError("Unexpected additional API request") from exc


class StubPage:
    def __init__(self, responses: list[StubResponse]) -> None:
        self.request = StubRequest(responses)


def _response(data: list[dict[str, Any]], total: int) -> StubResponse:
    return StubResponse({"data": data, "meta": {"total": total}})


def _offsets_from_url_calls(
    calls: list[tuple[str, dict[str, Any]]],
) -> list[int]:
    return [
        int(parse_qs(urlparse(url).query)["offset"][0])
        for url, _ in calls
    ]


def test_get_available_employee_paginates_without_skipping_short_pages() -> None:
    employee_one = {
        "empNumber": 1,
        "employeeId": "E001",
        "firstName": "Alex",
        "middleName": "",
        "lastName": "One",
        "terminationId": None,
    }
    employee_two = {
        "empNumber": 2,
        "employeeId": "E002",
        "firstName": "Sam",
        "middleName": "",
        "lastName": "Two",
        "terminationId": None,
    }
    page = StubPage(
        [
            _response([employee_one], 2),
            _response([employee_two], 2),
            _response(
                [{"employee": {"empNumber": 1}, "deleted": False}], 2
            ),
            _response(
                [{"employee": {"empNumber": 99}, "deleted": False}], 2
            ),
        ]
    )

    result = EmployeeService.get_available_employee(page)

    assert result == {
        "empNumber": 2,
        "employeeId": "E002",
        "employeeName": "Sam Two",
        "firstName": "Sam",
        "middleName": "",
        "lastName": "Two",
    }
    assert _offsets_from_url_calls(page.request.calls) == [0, 1, 0, 1]


def test_get_available_employee_handles_empty_zero_total_lists() -> None:
    page = StubPage([_response([], 0), _response([], 0)])

    with pytest.raises(RuntimeError, match="No active employee"):
        EmployeeService.get_available_employee(page)

    assert len(page.request.calls) == 2


def test_generate_unused_employee_id_paginates_short_pages() -> None:
    page = StubPage(
        [
            _response([{"employeeId": "1000"}], 3),
            _response(
                [{"employeeId": "1001"}, {"employeeId": "1002"}], 3
            ),
        ]
    )

    result = EmployeeService.generate_unused_employee_id(page)

    assert result in {str(value) for value in range(1003, 10000)}
    assert [
        call[1]["params"]["offset"] for call in page.request.calls
    ] == [0, 1]


def test_generate_unused_employee_id_handles_zero_total() -> None:
    page = StubPage([_response([], 0)])

    result = EmployeeService.generate_unused_employee_id(page)

    assert result.isdigit()
    assert 1000 <= int(result) <= 9999
    assert len(page.request.calls) == 1


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"meta": {"total": 0}},
        {"data": {}, "meta": {"total": 0}},
        {"data": [], "meta": []},
        {"data": [], "meta": {}},
        {"data": [], "meta": {"total": True}},
        {"data": [], "meta": {"total": -1}},
        {"data": [], "meta": {"total": 1.5}},
        {"data": [], "meta": {"total": "1"}},
    ],
)
def test_pagination_response_rejects_invalid_structures(
    payload: Any,
) -> None:
    with pytest.raises(RuntimeError, match="Invalid pagination response"):
        _validated_pagination_page(StubResponse(payload), "test endpoint")


def test_pagination_response_rejects_invalid_json() -> None:
    response = StubResponse(None, json_error=ValueError("invalid JSON"))

    with pytest.raises(RuntimeError, match="Invalid JSON response"):
        _validated_pagination_page(response, "test endpoint")


def test_pagination_response_reports_http_errors() -> None:
    with pytest.raises(RuntimeError, match="HTTP 503"):
        _validated_pagination_page(
            StubResponse({}, status=503), "employee list"
        )


def test_get_available_employee_fails_on_empty_employee_page_before_total() -> None:
    page = StubPage([_response([], 1)])

    with pytest.raises(RuntimeError, match="Employee pagination made no progress"):
        EmployeeService.get_available_employee(page)

    assert len(page.request.calls) == 1


def test_get_available_employee_fails_on_empty_system_user_page_before_total() -> None:
    employee = {
        "empNumber": 1,
        "employeeId": "E001",
        "firstName": "Alex",
        "middleName": "",
        "lastName": "One",
        "terminationId": None,
    }
    page = StubPage([_response([employee], 1), _response([], 1)])

    with pytest.raises(
        RuntimeError, match="System-user pagination made no progress"
    ):
        EmployeeService.get_available_employee(page)

    assert len(page.request.calls) == 2


def test_generate_unused_employee_id_fails_on_empty_nonterminal_page() -> None:
    page = StubPage([_response([], 3)])

    with pytest.raises(RuntimeError, match="Employee pagination made no progress"):
        EmployeeService.generate_unused_employee_id(page)

    assert len(page.request.calls) == 1


def test_generate_unused_employee_id_fails_if_total_changes_between_pages() -> None:
    page = StubPage(
        [
            _response([{"employeeId": "1000"}], 3),
            _response([{"employeeId": "1001"}], 4),
        ]
    )

    with pytest.raises(
        RuntimeError, match="pagination metadata changed during retrieval"
    ):
        EmployeeService.generate_unused_employee_id(page)

    assert len(page.request.calls) == 2
