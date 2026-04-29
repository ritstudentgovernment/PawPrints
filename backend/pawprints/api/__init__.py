from pawprints.api.admin_petition_router import router as admin_petition_router
from pawprints.api.auth_router import router as auth_router
from pawprints.api.committee_router import router as committee_router
from pawprints.api.image_router import router as image_router

# from pawprints.api.general import router as general_router
from pawprints.api.permissions_router import router as permission_router
from pawprints.api.petition_router import router as petition_router
from pawprints.api.roles_router import router as role_router
from pawprints.api.settings_router import router as settings_router
from pawprints.api.stats_router import router as stats_router
from pawprints.api.tag_router import router as tag_router
from pawprints.api.user_router import router as user_router

__all__ = [
    "admin_petition_router",
    "auth_router",
    "committee_router",
    "permission_router",
    "petition_router",
    "role_router",
    "settings_router",
    "stats_router",
    "tag_router",
    "user_router",
    "image_router",
]
