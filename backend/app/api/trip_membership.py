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


@router.post(
    "/members",
    response_model=AddTripMemberResponse,
)
async def add_membership(
    trip_id: uuid.UUID,
    request: AddMemberRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership_service = TripMembershipService(db)

    membership = await membership_service.create_membership(
        trip_id=trip_id,
        user_id=request.user_id,
        current_user_id=current_user.id,
    )

    await db.commit()

    return AddTripMemberResponse(
        status_code=201,
        message="Member added successfully",
        data=TripMemberResponse(
            id=membership.id,
                trip_id=membership.trip_id,
                user_id=membership.user_id,
                joined_at=membership.joined_at,
                left_at=membership.left_at,
                status=membership.status,
                created_at=membership.created_at,
                updated_at=membership.updated_at,

        ),
    )


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

    members = await membership_service.get_all_members(trip_id)

    return TripMemberListResponse(
        members=[
            TripMemberResponse(
                id=member.id,
                trip_id=member.trip_id,
                user_id=member.user_id,
                joined_at=member.joined_at,
                left_at=member.left_at,
                status=member.status,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members
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

    member = await membership_service.get_member_by_id(
        trip_id,
        member_id,
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    return TripMemberResponse(
        id=member.id,
        trip_id=member.trip_id,
        user_id=member.user_id,
        joined_at=member.joined_at,
        left_at=member.left_at,
        status=member.status,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


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

    member = await membership_service.remove_member(
        trip_id,
        member_id,
        current_user.id,
    )

    return TripMemberResponse(
        id=member.id,
        trip_id=member.trip_id,
        user_id=member.user_id,
        joined_at=member.joined_at,
        left_at=member.left_at,
        status=member.status,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )