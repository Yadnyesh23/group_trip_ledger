
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.schemas.trip_membership import (
    AddTripMemberResponse,
    AddMemberRequest,
    TripMemberListResponse,
    TripMemberResponse,
)
from app.models.users import UserModel
from app.core.dependencies import get_current_user
from app.services.trip_membership import TripMembershipService


router = APIRouter(
    prefix="/api/v1/trips/{trip_id}",
    tags=["Trip Membership"],
)


def build_member_response(
    member,
    user_name: str,
) -> TripMemberResponse:
    return TripMemberResponse(
        id=member.id,
        trip_id=member.trip_id,
        user_id=member.user_id,
        user_name=user_name,
        joined_at=member.joined_at,
        left_at=member.left_at,
        status=member.status,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


@router.post(
    "/members",
    response_model=AddTripMemberResponse,
    status_code=201,
)
async def add_membership(
    trip_id: uuid.UUID,
    request: AddMemberRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership_service = TripMembershipService(db)

    try:
        member, user_name = await membership_service.create_membership(
            trip_id=trip_id,
            display_name=request.display_name,
            current_user_id=current_user.id,
        )

        await db.commit()

        return AddTripMemberResponse(
            status_code=201,
            message="Member added successfully",
            data=build_member_response(member, user_name),
        )
    except Exception:
        await db.rollback()
        raise


@router.get(
    "/members",
    response_model=TripMemberListResponse,
)
async def get_members(
    trip_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership_service = TripMembershipService(db)
    members = await membership_service.get_all_members(trip_id, current_user.id)

    return TripMemberListResponse(
        members=[
            build_member_response(member, user_name)
            for member, user_name in members
        ]
    )


@router.get(
    "/members/{member_id}",
    response_model=TripMemberResponse,
)
async def get_member_by_id(
    trip_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership_service = TripMembershipService(db)

    result = await membership_service.get_member_by_id(
        trip_id,
        member_id,
        current_user.id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    member, user_name = result
    return build_member_response(member, user_name)


@router.delete(
    "/members/{member_id}",
    response_model=TripMemberResponse,
)
async def remove_member(
    trip_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership_service = TripMembershipService(db)

    try:
        member, user_name = await membership_service.remove_member(
            trip_id=trip_id,
            member_id=member_id,
            current_user_id=current_user.id,
        )

        await db.commit()
        return build_member_response(member, user_name)
    except Exception:
        await db.rollback()
        raise