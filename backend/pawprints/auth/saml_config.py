from functools import lru_cache
import logging
import os
import os as _os
from typing import Any
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from saml2 import BINDING_HTTP_POST
from saml2.config import Config as SamlConfig, SPConfig
from saml2.metadata import entity_descriptor

logger = logging.getLogger("pawprints.saml")


def _bool_env(name: str, default: bool = False) -> bool:
    """
    Parse a boolean environment variable.

    Parameters
    ----------
    name : str
        Environment variable name.
    default : bool, optional
        Fallback if the variable is unset.

    Returns
    -------
    bool
        Parsed boolean value.
    """
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _required_env(name: str) -> str:
    """
    Get a required environment variable or raise a clear error.

    Parameters
    ----------
    name : str
        Environment variable name.

    Returns
    -------
    str
        The variable's value.

    Raises
    ------
    RuntimeError
        If the variable is not set or empty.
    """
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def _load_env() -> None:
    """
    Load environment variables from `.env` or `.env.dev` depending on MODE.

    Notes
    -----
    - If ``MODE=PROD``, loads ``.env``.
    - Otherwise, loads ``.env.dev``.
    - Existing env vars are overridden to ensure predictable behavior.
    """
    mode = os.getenv("MODE", "DEV").upper()
    filename = ".env" if mode == "PROD" else ".env.dev"
    # Resolve relative to project root if needed; here we assume CWD contains the file.
    load_dotenv(dotenv_path=filename, override=True)


@lru_cache(maxsize=1)
def build_saml_config() -> tuple[SamlConfig, dict[str, Any]]:
    """
    Build and validate the SAML2 Service Provider configuration.

    Returns
    -------
    (SamlConfig, dict)
        A tuple of the loaded ``SamlConfig`` instance and the raw configuration dict
        (compatible with pysaml2).

    Raises
    ------
    RuntimeError
        If required environment variables are missing.

    Notes
    -----
    Required environment variables:
        - ISSUER
        - CALLBACK_URL
        - IDP_METADATA_PATH
        - SP_KEY_PATH
        - SP_CERT_PATH
        - XMLSEC1_PATH

    Optional environment variables:
        - MODE (default: "DEV")
        - SP_NAME (default: "pawprints2")
        - ORGANIZATION_NAME (default: "RIT Student Government")
        - ORGANIZATION_DISPLAY_NAME (default: "RIT SG")
        - ORGANIZATION_URL (default: "https://your-app-domain.example.com")
        - TECH_CONTACT_NAME (default: "Admin")
        - TECH_CONTACT_EMAIL (default: "admin@example.com")
        - ALLOW_UNSOLICITED (bool; default: True)
        - AUTHN_REQUESTS_SIGNED (bool; default: False)
    """
    _load_env()

    # Required
    issuer = _required_env("ISSUER")
    acs_url = _required_env("CALLBACK_URL")
    idp_metadata_path = _required_env("IDP_METADATA_PATH")
    sp_key_path = _required_env("SP_KEY_PATH")
    sp_cert_path = _required_env("SP_CERT_PATH")
    xmlsec_path = _required_env("XMLSEC1_PATH")

    # Optionals
    sp_name = os.getenv("SP_NAME", "pawprints2")
    org_name = os.getenv("ORGANIZATION_NAME", "RIT Student Government")
    org_display = os.getenv("ORGANIZATION_DISPLAY_NAME", "RIT SG")
    org_url = os.getenv("ORGANIZATION_URL", "https://your-app-domain.example.com")
    tech_contact_name = os.getenv("TECH_CONTACT_NAME", "Admin")
    tech_contact_email = os.getenv("TECH_CONTACT_EMAIL", "admin@example.com")
    allow_unsolicited = _bool_env("ALLOW_UNSOLICITED", default=True)
    authn_requests_signed = _bool_env("AUTHN_REQUESTS_SIGNED", default=False)
    attribute_map_dir = os.path.join(os.path.dirname(__file__), "attributemaps")

    config_dict: dict[str, Any] = {
        "entityid": issuer,
        "name": sp_name,
        "attribute_map_dir": attribute_map_dir,
        "service": {
            "sp": {
                "allow_unsolicited": allow_unsolicited,
                "authn_requests_signed": authn_requests_signed,
                "endpoints": {
                    "assertion_consumer_service": [
                        (acs_url, BINDING_HTTP_POST),
                    ],
                },
                "required_attributes": [
                    "uid",
                    "givenName",
                    "sn",
                    "mail",
                    "ritEduAccountType",
                ],
                "optional_attributes": [
                    "ritEduCampusU",
                    "ritEduCampusG",
                    "ritEduCollegeU",
                    "ritEduCollegeG",
                ],
                "name": "RIT Student Government Service",
                "description": "RIT SG Petition Platform",
                "name_id_format": ["urn:oasis:names:tc:SAML:2.0:nameid-format:transient"],
            },
        },
        "metadata": {
            "local": [idp_metadata_path],
            "remote": [],
        },
        "allow_unknown_attributes": True,
        "metadata_key_usage": "both",
        "key_file": sp_key_path,
        "cert_file": sp_cert_path,
        "encryption_keypairs": [
            {"key_file": sp_key_path, "cert_file": sp_cert_path},
        ],
        "xmlsec_binary": xmlsec_path,
        "delete_tmpfiles": True,
        "organization": {
            "name": [(org_name, "en")],
            "display_name": [(org_display, "en")],
            "url": [(org_url, "en")],
        },
        "contact_person": [
            {
                "given_name": tech_contact_name,
                "email_address": [tech_contact_email],
                "contact_type": "technical",
            },
        ],
    }

    sc = SamlConfig()
    sc.load(config_dict)
    return sc, config_dict


def get_saml_config() -> tuple[SamlConfig, dict[str, Any]]:
    """
    Public accessor for the lazily built SAML configuration.

    Returns
    -------
    (SamlConfig, dict)
        The cached SAML configuration and its raw dict.

    Notes
    -----
    Results are memoized; changes to environment variables after the first call
    will not be reflected unless the process restarts.
    """
    return build_saml_config()


def generate_sp_metadata(config_dict: dict[str, Any], pretty: bool = True) -> str:
    """
    Generate SP metadata XML from a pysaml2 config dict.

    Parameters
    ----------
    config_dict : dict
        A pysaml2-compatible Service Provider configuration dictionary.
    pretty : bool, optional
        If True, returns indented XML for readability; otherwise returns a compact XML string.

    Returns
    -------
    str
        The generated SP metadata as an XML string.

    Raises
    ------
    ValueError
        If the entity descriptor could not be generated.
    """
    sp_config = SPConfig()
    # IdP metadata is not needed to describe the SP itself; omitting it avoids
    # FileNotFoundError when the IdP metadata file is absent (e.g. local dev).
    sp_config.load({**config_dict, "metadata": {"local": [], "remote": []}})

    ed = entity_descriptor(sp_config)
    if ed is None:
        logger.error("Could not generate entity descriptor from SP configuration.")
        raise ValueError("Could not generate entity descriptor from SP configuration.")

    xml_bytes = str(ed).encode("utf-8")

    if not pretty:
        return xml_bytes.decode("utf-8")

    xml_tree = ET.fromstring(xml_bytes)
    ET.indent(xml_tree)
    return ET.tostring(xml_tree, encoding="unicode")


def get_logout_url():
    """
    Returns the default RIT IDP logout URL. Application needs to redirect here to initiate an IDP logout.

    Still needs to delete cookies and sessions from this app.
    """
    return os.getenv("LOGOUT_ENTRY_POINT", "https://your-idp.example.com/logout.html")


# Only materialise the SAML config at import time in PROD.
# In DEV the env vars won't be present and the late imports inside AuthService
# guard access anyway.

if _os.getenv("MODE", "DEV").upper() == "PROD":
    saml_config, raw_config = get_saml_config()
else:
    saml_config, raw_config = None, {}  # type: ignore[assignment]
