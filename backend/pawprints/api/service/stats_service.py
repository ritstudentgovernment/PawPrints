from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
import logging
from typing import Annotated

from fastapi import Depends
import sqlalchemy as sa
from sqlalchemy import and_, cast, distinct, exists, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from pawprints.database.session import get_async_db_session
from pawprints.logger import get_logger
from pawprints.models.orm import (
    Committee,
    CommitteeAssignment,
    Petition,
    PetitionDeletion,
    PetitionSignature,
    PetitionTag,
    PetitionUpdate,
    Report,
    StatsActivityLog,
    StatsPetitionDaily,
    StatsPetitionSignatureVelocity,
    StatsTagUsage,
    StatsUserSnapshot,
    StatusEnum,
    Tag,
    Update,
    User,
)
from pawprints.models.schema import (
    ActivityDayResponse,
    ActivityEndpointGroup,
    ActivityHourSlot,
    ActivityTrendPoint,
    ActivityTrendResponse,
    CommitteePerformanceResponse,
    CommitteePerformanceStats,
    PetitionTimeline,
    PetitionTimelinePoint,
    ResponseTimeResponse,
    ResponseTimeStats,
    SignatureVelocityItem,
    SignatureVelocityResponse,
    StatsOverview,
    StatsRefreshResult,
    StatusBreakdown,
    StatusBreakdownResponse,
    TagBreakdownResponse,
    TagStats,
    UserBreakdownByAccountType,
    UserBreakdownByCollege,
    UserBreakdownResponse,
    UserGrowthPoint,
    UserGrowthResponse,
)

_GRANULARITY_MAP: dict[str, str] = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
    "yearly": "year",
}
_DEFAULT_LOOKBACK_DAYS = 365


def _no_deletion(petition_id_col) -> sa.BinaryExpression:
    return ~exists(select(1).where(PetitionDeletion.petition_id == petition_id_col))


def _live_petitions() -> sa.BinaryExpression:
    return and_(Petition.is_draft.is_(False), _no_deletion(Petition.id))


class StatsService:
    def __init__(self, session: AsyncSession, logger: logging.Logger) -> None:
        self.session = session
        self.logger = logger

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    async def get_overview(self) -> StatsOverview:
        """Return high-level headline numbers computed from live data."""
        rows = (
            await self.session.execute(
                select(Petition.status, func.count().label("cnt"))
                .where(_live_petitions())
                .group_by(Petition.status)
            )
        ).fetchall()

        by_status: dict[StatusEnum, int] = {r.status: r.cnt for r in rows}
        total_petitions = sum(by_status.values())

        total_signatures = (
            await self.session.execute(
                select(func.coalesce(func.sum(Petition.total_signatures), 0)).where(
                    _live_petitions()
                )
            )
        ).scalar() or 0

        total_users = (
            await self.session.execute(select(func.count()).select_from(User))
        ).scalar() or 0

        total_committees = (
            await self.session.execute(select(func.count()).select_from(Committee))
        ).scalar() or 0

        total_tags = (
            await self.session.execute(select(func.count()).select_from(Tag))
        ).scalar() or 0

        responded = by_status.get(StatusEnum.RESPONDED, 0)
        pct = round((responded / total_petitions * 100) if total_petitions else 0.0, 2)

        return StatsOverview(
            total_petitions=total_petitions,
            active_petitions=by_status.get(StatusEnum.ACTIVE, 0),
            charged_petitions=by_status.get(StatusEnum.CHARGED, 0),
            responded_petitions=responded,
            expired_petitions=by_status.get(StatusEnum.EXPIRED, 0),
            total_signatures=int(total_signatures),
            total_users=total_users,
            total_committees=total_committees,
            total_tags=total_tags,
            petitions_with_response_pct=pct,
        )

    # ------------------------------------------------------------------
    # Petition timeline
    # ------------------------------------------------------------------

    async def get_petition_timeline(
        self,
        granularity: str = "weekly",
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> PetitionTimeline:
        """Return petition creation / resolution counts bucketed by time."""
        trunc_key = _GRANULARITY_MAP.get(granularity, "week")
        today = datetime.now(UTC).date()
        from_date = from_date or (today - timedelta(days=_DEFAULT_LOOKBACK_DAYS))
        to_date = to_date or today

        period_col = func.date_trunc(trunc_key, Petition.created_at).label("period")
        stmt = (
            select(
                period_col,
                func.count().label("created"),
                func.sum(cast(Petition.has_response, sa.Integer)).label("responded"),
                func.sum(cast(Petition.status == StatusEnum.EXPIRED, sa.Integer)).label("expired"),
                func.sum(cast(Petition.status == StatusEnum.CHARGED, sa.Integer)).label("charged"),
                func.coalesce(func.sum(Petition.total_signatures), 0).label("signatures"),
            )
            .where(
                _live_petitions(),
                Petition.created_at >= from_date,
                Petition.created_at <= to_date,
            )
            .group_by(period_col)
            .order_by(period_col)
        )

        rows = (await self.session.execute(stmt)).fetchall()
        return PetitionTimeline(
            granularity=granularity,
            data=[
                PetitionTimelinePoint(
                    period=(
                        r.period.strftime("%Y-%m-%d")
                        if hasattr(r.period, "strftime")
                        else str(r.period)
                    ),
                    created=r.created,
                    responded=int(r.responded or 0),
                    expired=int(r.expired or 0),
                    charged=int(r.charged or 0),
                    signatures=int(r.signatures or 0),
                )
                for r in rows
            ],
        )

    # ------------------------------------------------------------------
    # Status breakdown
    # ------------------------------------------------------------------

    async def get_status_breakdown(self) -> StatusBreakdownResponse:
        """Return live petition count grouped by lifecycle status."""
        rows = (
            await self.session.execute(
                select(Petition.status, func.count().label("cnt"))
                .where(_live_petitions())
                .group_by(Petition.status)
                .order_by(Petition.status)
            )
        ).fetchall()

        total = sum(r.cnt for r in rows)
        _name = {s.value: s.name for s in StatusEnum}
        return StatusBreakdownResponse(
            total=total,
            breakdown=[
                StatusBreakdown(
                    status=_name.get(
                        r.status.value if hasattr(r.status, "value") else int(r.status),
                        str(r.status),
                    ),
                    count=r.cnt,
                    percentage=round((r.cnt / total * 100) if total else 0.0, 2),
                )
                for r in rows
            ],
        )

    # ------------------------------------------------------------------
    # Tag breakdown
    # ------------------------------------------------------------------

    async def get_tag_breakdown(self, limit: int = 50) -> TagBreakdownResponse:
        """Return petition counts per tag, sorted by popularity."""
        stmt = (
            select(
                Tag.id.label("tag_id"),
                Tag.name.label("tag_name"),
                Tag.color,
                func.count(PetitionTag.petition_id).label("petition_count"),
            )
            .outerjoin(PetitionTag, Tag.id == PetitionTag.tag_id)
            .outerjoin(
                Petition,
                and_(
                    PetitionTag.petition_id == Petition.id,
                    _live_petitions(),
                ),
            )
            .group_by(Tag.id, Tag.name, Tag.color)
            .order_by(func.count(PetitionTag.petition_id).desc())
            .limit(limit)
        )

        rows = (await self.session.execute(stmt)).fetchall()
        total_tagged = sum(r.petition_count for r in rows)
        return TagBreakdownResponse(
            total_tagged_petitions=total_tagged,
            breakdown=[
                TagStats(
                    tag_id=r.tag_id,
                    tag_name=r.tag_name,
                    color=r.color,
                    petition_count=r.petition_count,
                    percentage=round(
                        (r.petition_count / total_tagged * 100) if total_tagged else 0.0, 2
                    ),
                )
                for r in rows
            ],
        )

    # ------------------------------------------------------------------
    # Response time
    # ------------------------------------------------------------------

    async def get_response_time(self) -> ResponseTimeResponse:
        """Return average days from petition creation to final response, per committee."""
        delta_days = func.extract("epoch", Update.created_at - Petition.created_at) / 86400.0
        stmt = (
            select(
                Committee.id.label("committee_id"),
                Committee.name.label("committee_name"),
                func.avg(delta_days).label("avg_days"),
                func.min(delta_days).label("min_days"),
                func.max(delta_days).label("max_days"),
                func.count().label("sample_size"),
            )
            .select_from(Petition)
            .join(
                PetitionUpdate,
                and_(
                    PetitionUpdate.petition_id == Petition.id,
                    PetitionUpdate.is_response.is_(True),
                ),
            )
            .join(Update, Update.id == PetitionUpdate.update_id)
            .outerjoin(CommitteeAssignment, CommitteeAssignment.petition_id == Petition.id)
            .outerjoin(Committee, Committee.id == CommitteeAssignment.committee_id)
            .where(Petition.has_response.is_(True), _live_petitions())
            .group_by(Committee.id, Committee.name)
            .order_by(func.avg(delta_days))
        )

        rows = (await self.session.execute(stmt)).fetchall()

        overall = (
            await self.session.execute(
                select(func.avg(delta_days))
                .select_from(Petition)
                .join(
                    PetitionUpdate,
                    and_(
                        PetitionUpdate.petition_id == Petition.id,
                        PetitionUpdate.is_response.is_(True),
                    ),
                )
                .join(Update, Update.id == PetitionUpdate.update_id)
                .where(Petition.has_response.is_(True))
            )
        ).scalar()

        return ResponseTimeResponse(
            overall_avg_days=float(overall) if overall is not None else None,
            by_committee=[
                ResponseTimeStats(
                    committee_id=r.committee_id,
                    committee_name=r.committee_name,
                    avg_days_to_response=float(r.avg_days) if r.avg_days is not None else None,
                    min_days=float(r.min_days) if r.min_days is not None else None,
                    max_days=float(r.max_days) if r.max_days is not None else None,
                    sample_size=r.sample_size,
                )
                for r in rows
            ],
        )

    # ------------------------------------------------------------------
    # Signature velocity
    # ------------------------------------------------------------------

    async def get_signature_velocity(self, limit: int = 10) -> SignatureVelocityResponse:
        """Return top petitions by signature count with first/last/peak timing."""
        stmt = (
            select(
                Petition.id.label("petition_id"),
                Petition.title,
                Petition.total_signatures,
                func.min(PetitionSignature.signed_at).label("first_sig_at"),
                func.max(PetitionSignature.signed_at).label("latest_sig_at"),
            )
            .join(PetitionSignature, PetitionSignature.petition_id == Petition.id)
            .where(_live_petitions())
            .group_by(Petition.id, Petition.title, Petition.total_signatures)
            .order_by(Petition.total_signatures.desc())
            .limit(limit)
        )

        rows = (await self.session.execute(stmt)).fetchall()
        if not rows:
            return SignatureVelocityResponse(petitions=[])

        pid_list = [r.petition_id for r in rows]
        vel_rows = (
            await self.session.execute(
                select(
                    StatsPetitionSignatureVelocity.petition_id,
                    StatsPetitionSignatureVelocity.peak_daily_signatures,
                    StatsPetitionSignatureVelocity.peak_day,
                ).where(StatsPetitionSignatureVelocity.petition_id.in_(pid_list))
            )
        ).fetchall()

        vel_map = {r.petition_id: r for r in vel_rows}
        return SignatureVelocityResponse(
            petitions=[
                SignatureVelocityItem(
                    petition_id=r.petition_id,
                    petition_title=r.title,
                    total_signatures=r.total_signatures,
                    first_signature_at=r.first_sig_at,
                    latest_signature_at=r.latest_sig_at,
                    peak_daily_signatures=(
                        vel_map[r.petition_id].peak_daily_signatures
                        if r.petition_id in vel_map
                        else None
                    ),
                    peak_day=(
                        str(vel_map[r.petition_id].peak_day)
                        if r.petition_id in vel_map and vel_map[r.petition_id].peak_day
                        else None
                    ),
                )
                for r in rows
            ]
        )

    # ------------------------------------------------------------------
    # User growth
    # ------------------------------------------------------------------

    async def get_user_growth(
        self,
        granularity: str = "monthly",
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> UserGrowthResponse:
        """Return new and cumulative user counts bucketed by time."""
        trunc_key = _GRANULARITY_MAP.get(granularity, "month")
        today = datetime.now(UTC).date()
        from_date = from_date or (today - timedelta(days=_DEFAULT_LOOKBACK_DAYS))
        to_date = to_date or today

        period_col = func.date_trunc(trunc_key, User.created_at).label("period")
        stmt = (
            select(period_col, func.count().label("new_users"))
            .where(User.created_at >= from_date, User.created_at <= to_date)
            .group_by(period_col)
            .order_by(period_col)
        )

        rows = (await self.session.execute(stmt)).fetchall()
        total_before = (
            await self.session.execute(
                select(func.count()).select_from(User).where(User.created_at < from_date)
            )
        ).scalar() or 0

        running = int(total_before)
        data: list[UserGrowthPoint] = []
        for r in rows:
            running += r.new_users
            data.append(
                UserGrowthPoint(
                    period=(
                        r.period.strftime("%Y-%m-%d")
                        if hasattr(r.period, "strftime")
                        else str(r.period)
                    ),
                    new_users=r.new_users,
                    total_users=running,
                )
            )
        return UserGrowthResponse(granularity=granularity, data=data)

    # ------------------------------------------------------------------
    # User breakdown
    # ------------------------------------------------------------------

    async def get_user_breakdown(self) -> UserBreakdownResponse:
        """Return user distribution by RIT college and account type."""
        total = (await self.session.execute(select(func.count()).select_from(User))).scalar() or 0

        college_rows = (
            await self.session.execute(
                select(User.rit_edu_college_u.label("college"), func.count().label("cnt"))
                .group_by(User.rit_edu_college_u)
                .order_by(func.count().desc())
            )
        ).fetchall()

        type_rows = (
            await self.session.execute(
                select(User.rit_edu_account_type.label("account_type"), func.count().label("cnt"))
                .group_by(User.rit_edu_account_type)
                .order_by(func.count().desc())
            )
        ).fetchall()

        return UserBreakdownResponse(
            total_users=total,
            by_college=[
                UserBreakdownByCollege(
                    college=r.college,
                    user_count=r.cnt,
                    percentage=round((r.cnt / total * 100) if total else 0.0, 2),
                )
                for r in college_rows
            ],
            by_account_type=[
                UserBreakdownByAccountType(
                    account_type=r.account_type,
                    user_count=r.cnt,
                    percentage=round((r.cnt / total * 100) if total else 0.0, 2),
                )
                for r in type_rows
            ],
        )

    # ------------------------------------------------------------------
    # Committee performance
    # ------------------------------------------------------------------

    async def get_committee_performance(self) -> CommitteePerformanceResponse:
        """Return throughput and response-time metrics per committee."""
        delta_days = func.extract("epoch", Update.created_at - Petition.created_at) / 86400.0
        stmt = (
            select(
                Committee.id.label("committee_id"),
                Committee.name.label("committee_name"),
                func.count(CommitteeAssignment.petition_id).label("petitions_assigned"),
                func.coalesce(func.sum(cast(Petition.has_response, sa.Integer)), 0).label(
                    "petitions_responded"
                ),
                func.avg(delta_days).label("avg_response_days"),
                func.coalesce(
                    func.sum(
                        cast(
                            and_(
                                Petition.has_response.is_(False),
                                Petition.status != StatusEnum.EXPIRED,
                            ),
                            sa.Integer,
                        )
                    ),
                    0,
                ).label("pending_count"),
            )
            .outerjoin(CommitteeAssignment, Committee.id == CommitteeAssignment.committee_id)
            .outerjoin(Petition, CommitteeAssignment.petition_id == Petition.id)
            .outerjoin(
                Update,
                and_(Update.id == Petition.response_id, Petition.has_response.is_(True)),
            )
            .group_by(Committee.id, Committee.name)
            .order_by(Committee.name)
        )

        rows = (await self.session.execute(stmt)).fetchall()
        return CommitteePerformanceResponse(
            committees=[
                CommitteePerformanceStats(
                    committee_id=r.committee_id,
                    committee_name=r.committee_name,
                    petitions_assigned=r.petitions_assigned or 0,
                    petitions_responded=int(r.petitions_responded or 0),
                    response_rate_pct=round(
                        (
                            (int(r.petitions_responded or 0) / r.petitions_assigned * 100)
                            if r.petitions_assigned
                            else 0.0
                        ),
                        2,
                    ),
                    avg_response_days=(
                        float(r.avg_response_days) if r.avg_response_days is not None else None
                    ),
                    pending_count=int(r.pending_count or 0),
                )
                for r in rows
            ]
        )

    # ------------------------------------------------------------------
    # Refresh: populate stats_* tables
    # ------------------------------------------------------------------

    async def refresh_all(self, target_date: date | None = None) -> StatsRefreshResult:
        """Recompute all stats_* tables for ``target_date`` (defaults to today)."""
        target_date = target_date or datetime.now(UTC).date()
        refreshed: list[str] = []

        for method, table_name in [
            (self._refresh_petition_daily, "stats_petition_daily"),
            (self._refresh_user_snapshot, "stats_user_snapshot"),
            (self._refresh_signature_velocity, "stats_petition_signature_velocity"),
            (self._refresh_tag_usage, "stats_tag_usage"),
        ]:
            try:
                if (
                    method == self._refresh_user_snapshot
                    or method == self._refresh_signature_velocity
                ):
                    await method()
                else:
                    await method(target_date)
                refreshed.append(table_name)
            except Exception as exc:
                self.logger.error("refresh failed for %s: %s", table_name, exc)

        return StatsRefreshResult(refreshed_tables=refreshed, target_date=str(target_date))

    async def _refresh_petition_daily(self, target_date: date) -> None:
        """Upsert one row in stats_petition_daily for target_date."""
        petitions_created = (
            await self.session.execute(
                select(func.count()).where(
                    Petition.is_draft.is_(False),
                    func.date(Petition.created_at) == target_date,
                )
            )
        ).scalar() or 0

        petitions_expired = (
            await self.session.execute(
                select(func.count()).where(
                    Petition.status == StatusEnum.EXPIRED,
                    func.date(Petition.expires) == target_date,
                )
            )
        ).scalar() or 0

        petitions_responded = (
            await self.session.execute(
                select(func.count())
                .join(
                    PetitionUpdate,
                    and_(
                        PetitionUpdate.petition_id == Petition.id,
                        PetitionUpdate.is_response.is_(True),
                    ),
                )
                .join(Update, Update.id == PetitionUpdate.update_id)
                .where(
                    Petition.has_response.is_(True),
                    func.date(Update.created_at) == target_date,
                )
            )
        ).scalar() or 0

        petitions_charged = (
            await self.session.execute(
                select(func.count())
                .select_from(CommitteeAssignment)
                .where(func.date(CommitteeAssignment.assigned_at) == target_date)
            )
        ).scalar() or 0

        signatures_cast = (
            await self.session.execute(
                select(func.count()).where(func.date(PetitionSignature.signed_at) == target_date)
            )
        ).scalar() or 0

        unique_signers = (
            await self.session.execute(
                select(func.count(distinct(PetitionSignature.user_id))).where(
                    func.date(PetitionSignature.signed_at) == target_date
                )
            )
        ).scalar() or 0

        reports_filed = (
            await self.session.execute(
                select(func.count()).where(func.date(Report.reported_at) == target_date)
            )
        ).scalar() or 0

        now = datetime.now(UTC)
        stmt = (
            pg_insert(StatsPetitionDaily)
            .values(
                date=target_date,
                petitions_created=petitions_created,
                petitions_expired=petitions_expired,
                petitions_responded=petitions_responded,
                petitions_charged=petitions_charged,
                signatures_cast=signatures_cast,
                unique_signers=unique_signers,
                reports_filed=reports_filed,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=["date"],
                set_=dict(
                    petitions_created=petitions_created,
                    petitions_expired=petitions_expired,
                    petitions_responded=petitions_responded,
                    petitions_charged=petitions_charged,
                    signatures_cast=signatures_cast,
                    unique_signers=unique_signers,
                    reports_filed=reports_filed,
                    updated_at=now,
                ),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def _refresh_user_snapshot(self) -> None:
        """Upsert today's row in stats_user_snapshot."""
        today = datetime.now(UTC).date()

        total_users = (
            await self.session.execute(select(func.count()).select_from(User))
        ).scalar() or 0

        new_users = (
            await self.session.execute(
                select(func.count()).where(func.date(User.created_at) == today)
            )
        ).scalar() or 0

        type_counts = (
            await self.session.execute(
                select(User.rit_edu_account_type, func.count().label("cnt")).group_by(
                    User.rit_edu_account_type
                )
            )
        ).fetchall()

        by_type: dict[str, int] = {}
        for r in type_counts:
            key = (r.rit_edu_account_type or "other").lower()
            by_type[key] = r.cnt

        known = {"student", "faculty", "staff"}
        other_count = sum(v for k, v in by_type.items() if k not in known)

        stmt = (
            pg_insert(StatsUserSnapshot)
            .values(
                snapshot_date=today,
                snapshot_at=datetime.now(UTC),
                total_users=total_users,
                new_users=new_users,
                account_type_student=by_type.get("student", 0),
                account_type_faculty=by_type.get("faculty", 0),
                account_type_staff=by_type.get("staff", 0),
                account_type_other=other_count,
            )
            .on_conflict_do_update(
                index_elements=["snapshot_date"],
                set_=dict(
                    snapshot_at=datetime.now(UTC),
                    total_users=total_users,
                    new_users=new_users,
                    account_type_student=by_type.get("student", 0),
                    account_type_faculty=by_type.get("faculty", 0),
                    account_type_staff=by_type.get("staff", 0),
                    account_type_other=other_count,
                ),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def _refresh_signature_velocity(self) -> None:
        """Recompute peak-daily-signatures for every petition that has at least one signature."""
        petition_ids = (
            (await self.session.execute(select(distinct(PetitionSignature.petition_id))))
            .scalars()
            .all()
        )

        now = datetime.now(UTC)
        for pid in petition_ids:
            bounds = (
                await self.session.execute(
                    select(
                        func.min(PetitionSignature.signed_at).label("first"),
                        func.max(PetitionSignature.signed_at).label("latest"),
                        func.count().label("total"),
                    ).where(PetitionSignature.petition_id == pid)
                )
            ).fetchone()

            peak = (
                await self.session.execute(
                    select(
                        func.date(PetitionSignature.signed_at).label("sig_date"),
                        func.count().label("cnt"),
                    )
                    .where(PetitionSignature.petition_id == pid)
                    .group_by(func.date(PetitionSignature.signed_at))
                    .order_by(func.count().desc())
                    .limit(1)
                )
            ).fetchone()

            stmt = (
                pg_insert(StatsPetitionSignatureVelocity)
                .values(
                    petition_id=pid,
                    first_signature_at=bounds.first if bounds else None,
                    latest_signature_at=bounds.latest if bounds else None,
                    total_signatures_snapshot=bounds.total if bounds else 0,
                    peak_daily_signatures=peak.cnt if peak else 0,
                    peak_day=peak.sig_date if peak else None,
                    updated_at=now,
                )
                .on_conflict_do_update(
                    index_elements=["petition_id"],
                    set_=dict(
                        first_signature_at=bounds.first if bounds else None,
                        latest_signature_at=bounds.latest if bounds else None,
                        total_signatures_snapshot=bounds.total if bounds else 0,
                        peak_daily_signatures=peak.cnt if peak else 0,
                        peak_day=peak.sig_date if peak else None,
                        updated_at=now,
                    ),
                )
            )
            await self.session.execute(stmt)

        await self.session.commit()

    async def _refresh_tag_usage(self, target_date: date) -> None:
        """Upsert cumulative petition-per-tag counts for target_date."""
        stmt_fetch = (
            select(
                PetitionTag.tag_id,
                func.count(PetitionTag.petition_id).label("cnt"),
            )
            .join(Petition, Petition.id == PetitionTag.petition_id)
            .where(
                Petition.is_draft.is_(False),
                func.date(Petition.created_at) <= target_date,
            )
            .group_by(PetitionTag.tag_id)
        )
        rows = (await self.session.execute(stmt_fetch)).fetchall()

        for r in rows:
            upsert = (
                pg_insert(StatsTagUsage)
                .values(tag_id=r.tag_id, date=target_date, petition_count=r.cnt)
                .on_conflict_do_update(
                    index_elements=["tag_id", "date"],
                    set_=dict(petition_count=r.cnt),
                )
            )
            await self.session.execute(upsert)

        await self.session.commit()

    # ------------------------------------------------------------------
    # Activity log queries
    # ------------------------------------------------------------------

    async def get_activity_day(self, target_date: date) -> ActivityDayResponse:
        """Return full activity breakdown for a single day."""
        rows = (
            await self.session.execute(
                select(
                    StatsActivityLog.endpoint_group,
                    StatsActivityLog.method,
                    StatsActivityLog.hour,
                    StatsActivityLog.request_count,
                    StatsActivityLog.unique_users,
                    StatsActivityLog.login_count,
                )
                .where(StatsActivityLog.date == target_date)
                .order_by(StatsActivityLog.endpoint_group, StatsActivityLog.hour)
            )
        ).fetchall()

        # Group: endpoint_group+method → list of hour slots
        from collections import defaultdict

        groups: dict[tuple, dict] = defaultdict(
            lambda: {"request_count": 0, "unique_users": 0, "login_count": 0, "hours": []}
        )
        for r in rows:
            key = (r.endpoint_group, r.method)
            groups[key]["request_count"] += r.request_count
            groups[key]["unique_users"] = max(groups[key]["unique_users"], r.unique_users)
            groups[key]["login_count"] += r.login_count
            if r.hour is not None:
                groups[key]["hours"].append(
                    ActivityHourSlot(
                        hour=r.hour,
                        request_count=r.request_count,
                        unique_users=r.unique_users,
                        login_count=r.login_count,
                    )
                )

        total_requests = sum(g["request_count"] for g in groups.values())
        total_unique = max((g["unique_users"] for g in groups.values()), default=0)
        total_logins = sum(g["login_count"] for g in groups.values())

        return ActivityDayResponse(
            date=str(target_date),
            total_requests=total_requests,
            total_unique_users=total_unique,
            total_logins=total_logins,
            by_endpoint=[
                ActivityEndpointGroup(
                    endpoint_group=ep,
                    method=meth,
                    request_count=g["request_count"],
                    unique_users=g["unique_users"],
                    login_count=g["login_count"],
                    by_hour=sorted(g["hours"], key=lambda h: h.hour),
                )
                for (ep, meth), g in sorted(groups.items())
            ],
        )

    async def get_activity_trend(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> ActivityTrendResponse:
        """Return daily activity totals over a date range."""
        today = datetime.now(UTC).date()
        from_date = from_date or (today - timedelta(days=30))
        to_date = to_date or today

        rows = (
            await self.session.execute(
                select(
                    StatsActivityLog.date,
                    func.sum(StatsActivityLog.request_count).label("total_requests"),
                    func.max(StatsActivityLog.unique_users).label("total_unique"),
                    func.sum(StatsActivityLog.login_count).label("total_logins"),
                )
                .where(
                    StatsActivityLog.date >= from_date,
                    StatsActivityLog.date <= to_date,
                )
                .group_by(StatsActivityLog.date)
                .order_by(StatsActivityLog.date)
            )
        ).fetchall()

        return ActivityTrendResponse(
            data=[
                ActivityTrendPoint(
                    date=str(r.date),
                    total_requests=int(r.total_requests or 0),
                    total_unique_users=int(r.total_unique or 0),
                    total_logins=int(r.total_logins or 0),
                )
                for r in rows
            ]
        )


# ------------------------------------------------------------------
# Dependency injection
# ------------------------------------------------------------------


async def get_stats_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> StatsService:
    return StatsService(session=session, logger=get_logger())


StatsServiceDep = Annotated[StatsService, Depends(get_stats_service)]
