from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from pawprints.api.service.stats_service import StatsServiceDep
from pawprints.auth.permission import has_permission
from pawprints.models.orm import User
from pawprints.models.schema import (
    ActivityDayResponse,
    ActivityTrendResponse,
    CommitteePerformanceResponse,
    PermissionEnum,
    PetitionTimeline,
    ResponseTimeResponse,
    SignatureVelocityResponse,
    StatsOverview,
    StatsRefreshResult,
    StatusBreakdownResponse,
    TagBreakdownResponse,
    UserBreakdownResponse,
    UserGrowthResponse,
)

router = APIRouter(tags=["Statistics"])

_GRANULARITY_QUERY = Query(
    "weekly",
    pattern="^(daily|weekly|monthly|yearly)$",
    description="Time bucket: daily | weekly | monthly | yearly",
)


@router.get(
    "/overview",
    response_model=StatsOverview,
    summary="Platform overview",
    description="High-level headline numbers: petition counts by status, total signatures, users, committees, and tags.",
)
async def get_overview(service: StatsServiceDep):
    return await service.get_overview()


@router.get(
    "/petitions/timeline",
    response_model=PetitionTimeline,
    summary="Petition activity over time",
    description="Petition creation, responses, charges, and signature totals bucketed by the chosen granularity.",
)
async def get_petition_timeline(
    service: StatsServiceDep,
    granularity: str = _GRANULARITY_QUERY,
    from_date: date | None = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
):
    return await service.get_petition_timeline(granularity, from_date, to_date)


@router.get(
    "/petitions/status-breakdown",
    response_model=StatusBreakdownResponse,
    summary="Petition count by status",
    description="Live breakdown of petition counts across ACTIVE, CHARGED, RESPONDED, and EXPIRED.",
)
async def get_status_breakdown(service: StatsServiceDep):
    return await service.get_status_breakdown()


@router.get(
    "/petitions/by-tag",
    response_model=TagBreakdownResponse,
    summary="Petition distribution by tag",
    description="How many petitions carry each tag, sorted by most popular.",
)
async def get_petitions_by_tag(
    service: StatsServiceDep,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of tags to return"),
):
    return await service.get_tag_breakdown(limit=limit)


@router.get(
    "/petitions/response-time",
    response_model=ResponseTimeResponse,
    summary="Response time statistics",
    description="Average, min, and max days from petition creation to final response, overall and per committee.",
)
async def get_response_time(service: StatsServiceDep):
    return await service.get_response_time()


@router.get(
    "/signatures/velocity",
    response_model=SignatureVelocityResponse,
    summary="Signature velocity for top petitions",
    description="Top petitions by signature count with first/latest/peak-day timing from the stats_petition_signature_velocity cache.",
)
async def get_signature_velocity(
    service: StatsServiceDep,
    limit: int = Query(10, ge=1, le=100, description="Number of petitions to return"),
):
    return await service.get_signature_velocity(limit=limit)


@router.get(
    "/users/growth",
    response_model=UserGrowthResponse,
    summary="User registration growth",
    description="New and cumulative user registrations bucketed by the chosen granularity. Requires users.created_at column.",
)
async def get_user_growth(
    service: StatsServiceDep,
    granularity: str = Query(
        "monthly",
        pattern="^(daily|weekly|monthly|yearly)$",
        description="Time bucket: daily | weekly | monthly | yearly",
    ),
    from_date: date | None = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
):
    return await service.get_user_growth(granularity, from_date, to_date)


@router.get(
    "/users/breakdown",
    response_model=UserBreakdownResponse,
    summary="User distribution by college and account type",
    description="Segmentation of users by RIT college (rit_edu_college_u) and account type.",
)
async def get_user_breakdown(service: StatsServiceDep):
    return await service.get_user_breakdown()


@router.get(
    "/committees/performance",
    response_model=CommitteePerformanceResponse,
    summary="Committee performance metrics",
    description="Petitions assigned, responded, response rate, average response time, and pending count per committee.",
)
async def get_committee_performance(service: StatsServiceDep):
    return await service.get_committee_performance()


@router.get(
    "/tags/popularity",
    response_model=TagBreakdownResponse,
    summary="Tag popularity",
    description="Tags ranked by how many petitions use them.",
)
async def get_tag_popularity(
    service: StatsServiceDep,
    limit: int = Query(20, ge=1, le=100, description="Number of tags to return"),
):
    return await service.get_tag_breakdown(limit=limit)


@router.post(
    "/refresh",
    response_model=StatsRefreshResult,
    summary="Refresh stats tables (admin)",
    description=(
        "Recompute all stats_* tables for the given date. "
        "Requires the stats.refresh permission. "
        "Defaults to today if no date is provided."
    ),
)
async def refresh_stats(
    service: StatsServiceDep,
    target_date: date | None = Query(
        None, alias="date", description="Date to refresh (YYYY-MM-DD, defaults to today)"
    ),
    _current_user: User = Depends(has_permission(PermissionEnum.stats_refresh)),
):
    return await service.refresh_all(target_date)


@router.get(
    "/activity/day",
    response_model=ActivityDayResponse,
    summary="API activity for a single day",
    description="Request counts per endpoint group and hour, plus login counts for the given day.",
)
async def get_activity_day(
    service: StatsServiceDep,
    target_date: date = Query(..., alias="date", description="Date to inspect (YYYY-MM-DD)"),
):
    return await service.get_activity_day(target_date)


@router.get(
    "/activity/trend",
    response_model=ActivityTrendResponse,
    summary="API activity trend",
    description="Daily request totals, unique users, and logins over a date range (default: last 30 days).",
)
async def get_activity_trend(
    service: StatsServiceDep,
    from_date: date | None = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
):
    return await service.get_activity_trend(from_date, to_date)
