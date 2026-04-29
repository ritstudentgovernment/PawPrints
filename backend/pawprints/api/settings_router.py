"""Site-wide settings router."""

from fastapi import APIRouter, Depends

from pawprints.api.service.settings_service import SettingsServiceDep
from pawprints.auth.permission import has_permission
from pawprints.models.schema import PermissionEnum, SiteAlertSchema, SiteAlertUpdate

router = APIRouter(tags=["Settings"])


@router.get("/alert", response_model=SiteAlertSchema)
async def get_alert(ss: SettingsServiceDep) -> SiteAlertSchema:
    return await ss.get_alert()


@router.put(
    "/alert",
    response_model=SiteAlertSchema,
    dependencies=[Depends(has_permission(PermissionEnum.settings_update))],
)
async def update_alert(ss: SettingsServiceDep, data: SiteAlertUpdate) -> SiteAlertSchema:
    return await ss.update_alert(data)
