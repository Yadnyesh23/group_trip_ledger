from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import UserModel
from app.schemas.reports import (
    ReportResponseSchema,
    ReportExpenseListResponse,
)
from app.schemas.trip_membership import TripMemberListResponse
from app.schemas.balances import TripBalanceListResponse
from app.schemas.settlements import SettlementListResponse
from app.services.reports import ReportService
from app.services.report_pdf import generate_trip_report_pdf


router = APIRouter(
    prefix="/api/v1/trip/{trip_id}/reports",
    tags=["Reports"],
)


def build_report_response(report_data: dict) -> ReportResponseSchema:
    """Convert the service data into the validated report response schema."""
    return ReportResponseSchema(
        members=TripMemberListResponse(
            members=report_data["members"],
        ),
        expenses=ReportExpenseListResponse(
            total_expenses=len(report_data["expenses"]),
            expenses=report_data["expenses"],
        ),
        balances=TripBalanceListResponse(
            balances=report_data["balances"],
        ),
        settlements=SettlementListResponse(
            settlements=report_data["settlements"],
        ),
    )


@router.get(
    "/",
    response_model=ReportResponseSchema,
    summary="Get trip report",
    description=(
        "Returns trip members, expenses, allocations, balances, "
        "and suggested settlements."
    ),
)
async def get_reports(
    trip_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponseSchema:
    report_service = ReportService(db)

    report_data = await report_service.generate_report(
        current_user_id=current_user.id,
        trip_id=trip_id,
    )

    return build_report_response(report_data)


@router.get(
    "/pdf",
    summary="Download trip report as PDF",
    responses={
        200: {
            "description": "Trip report PDF",
            "content": {
                "application/pdf": {},
            },
        },
    },
)
async def download_trip_report_pdf(
    trip_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    report_service = ReportService(db)

    report_data = await report_service.generate_report(
        current_user_id=current_user.id,
        trip_id=trip_id,
    )

    report = build_report_response(report_data)

    pdf_bytes = generate_trip_report_pdf(report)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="trip_report_{trip_id}.pdf"'
            ),
        },
    )
