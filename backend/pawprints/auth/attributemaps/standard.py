# Standard SAML attribute OID mappings.
# Required because attribute_map_dir replaces pysaml2's built-in maps entirely.
# These cover the core identity fields the app reads: uid, givenName, sn, mail.
MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
    "fro": {
        # Core identity — sent by RIT Shibboleth IdP
        "urn:oid:0.9.2342.19200300.100.1.1": "uid",
        "urn:oid:2.5.4.42": "givenName",
        "urn:oid:2.5.4.4": "sn",
        "urn:oid:0.9.2342.19200300.100.1.3": "mail",
        # eduPerson — RIT may send ePPN instead of/alongside uid
        "urn:oid:1.3.6.1.4.1.5923.1.1.1.6": "eduPersonPrincipalName",
        "urn:oid:1.3.6.1.4.1.5923.1.1.1.7": "eduPersonEntitlement",
        "urn:oid:1.3.6.1.4.1.5923.1.1.1.9": "eduPersonScopedAffiliation",
        "urn:oid:1.3.6.1.4.1.5923.1.1.1.1": "eduPersonAffiliation",
        # Common person attrs
        "urn:oid:2.5.4.3": "cn",
        "urn:oid:2.16.840.1.113730.3.1.241": "displayName",
    },
    "to": {
        "uid": "urn:oid:0.9.2342.19200300.100.1.1",
        "givenName": "urn:oid:2.5.4.42",
        "sn": "urn:oid:2.5.4.4",
        "mail": "urn:oid:0.9.2342.19200300.100.1.3",
        "eduPersonPrincipalName": "urn:oid:1.3.6.1.4.1.5923.1.1.1.6",
        "eduPersonEntitlement": "urn:oid:1.3.6.1.4.1.5923.1.1.1.7",
        "eduPersonScopedAffiliation": "urn:oid:1.3.6.1.4.1.5923.1.1.1.9",
        "eduPersonAffiliation": "urn:oid:1.3.6.1.4.1.5923.1.1.1.1",
        "cn": "urn:oid:2.5.4.3",
        "displayName": "urn:oid:2.16.840.1.113730.3.1.241",
    },
}
