"""Service layer for site-wide settings."""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import DBError
from pawprints.logger import get_logger
from pawprints.models.orm import SiteSettings
from pawprints.models.schema import SiteAlertSchema, SiteAlertUpdate


class SettingsService:
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        self.session = session
        self.logger = logger

    async def get_alert(self) -> SiteAlertSchema:
        result = await self.session.execute(select(SiteSettings).where(SiteSettings.id == 1))
        row = result.scalar_one_or_none()
        if row is None:
            row = SiteSettings(id=1, alert_enabled=False, alert_message="", updated_at=datetime.now(UTC))
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        return SiteAlertSchema.model_validate(row)

    async def update_alert(self, data: SiteAlertUpdate) -> SiteAlertSchema:
        result = await self.session.execute(select(SiteSettings).where(SiteSettings.id == 1))
        row = result.scalar_one_or_none()
        if row is None:
            row = SiteSettings(id=1)
            self.session.add(row)
        row.alert_enabled = data.alert_enabled
        row.alert_message = data.alert_message
        row.updated_at = datetime.now(UTC)
        try:
            await self.session.commit()
            await self.session.refresh(row)
            return SiteAlertSchema.model_validate(row)
        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to update site settings.",
                context={"error": str(e)},
            ) from e


def get_settings_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> SettingsService:
    return SettingsService(session=session, logger=logger)


SettingsServiceDep = Annotated[SettingsService, Depends(get_settings_service)]
