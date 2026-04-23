# Error Code Reference

This document provides a comprehensive reference for standardized error codes used within the Pawprints API. A consistent error response format is used to ensure predictable and actionable error handling for API clients.

## Error Response Format

When an error occurs, the API will respond with a JSON object containing the following fields:

```json
{
  "detail": {
    "code": "<error_code>",
    "message": "<error_message>",
    "context": {
      "field": "field_name",
      "reason": "detailed reason for the error"
    }
  }
}
```

-   `code`: A unique and stable error code from this document.
-   `message`: A human-readable message summarizing the error.
-   `context`: (Optional) Additional details about the error, such as which field was invalid.

---

## General Errors (1xxx)

### 1000 - Internal Server Error

-   **Message**: "An unexpected error occurred on the server."
-   **HTTP Status**: 500
-   **Description**: This is a generic error for unexpected server-side issues. It indicates a bug or a problem with the server's configuration.
-   **Action**: The client should not retry the request without modification. The error should be logged and reported.

### 1001 - Service Unavailable

-   **Message**: "The service is temporarily unavailable."
-   **HTTP Status**: 503
-   **Description**: The server is currently unable to handle the request due to a temporary overload or maintenance.
-   **Action**: The client can retry the request after a short delay.

---

## Authentication & Authorization Errors (2xxx)

### 2000 - Authentication Failed

-   **Message**: "Authentication failed. Invalid credentials provided."
-   **HTTP Status**: 401
-   **Description**: The request lacks valid authentication credentials. This could be due to a missing, invalid, or expired token.
-   **Action**: The client should obtain a new token and retry the request.

### 2001 - Permission Denied

-   **Message**: "You do not have permission to perform this action."
-   **HTTP Status**: 403
-   **Description**: The authenticated user is not authorized to access the requested resource or perform the requested action.
-   **Action**: Ensure the user has the necessary roles or permissions.

---

## Validation Errors (3xxx)

### 3000 - Invalid Request Body

-   **Message**: "The request body is malformed or invalid."
-   **HTTP Status**: 400
-   **Description**: The server could not parse the request body, or it fails validation checks.
-   **Action**: The client should check the request body against the API specification and correct any errors. The `context` field in the response may provide more details.

### 3001 - Invalid Parameter

-   **Message**: "An invalid parameter was provided in the request."
-   **HTTP Status**: 400
-   **Description**: A query parameter or a field in the request body has an invalid value.
-   **Action**: The client should check the parameter value and retry. The `context` field will specify the problematic parameter.

---

## Resource-Specific Errors (4xxx - Petitions, 5xxx - Users, etc.)

### 4000 - Petition Not Found

-   **Message**: "The requested petition could not be found."
-   **HTTP Status**: 404
-   **Description**: The petition with the specified ID does not exist.
-   **Action**: Verify the petition ID.

### 4001 - Petition Already Signed

-   **Message**: "You have already signed this petition."
-   **HTTP Status**: 409 (Conflict)
-   **Description**: The user has already signed the petition and cannot sign it again.
-   **Action**: No action needed. Inform the user that they have already signed.

### 5000 - User Not Found

-   **Message**: "The requested user could not be found."
-   **HTTP Status**: 404
-   **Description**: The user with the specified username or ID does not exist.
-   **Action**: Verify the user identifier.

### 5001 - Committee Not Found

-   **Message**: "The requested committee could not be found."
-   **HTTP Status**: 404
-   **Description**: The committee with the specified ID does not exist.
-   **Action**: Verify the committee ID.

### 5002 - Committee Member Not Found

-   **Message**: "No committee members found."
-   **HTTP Status**: 404
-   **Description**: The requested committee has no members.
-   **Action**: Add members to the committee.

### 5003 - User Already in Committee

-   **Message**: "User is already a member of this committee."
-   **HTTP Status**: 409 (Conflict)
-   **Description**: The user is already a member of the committee.
-   **Action**: No action needed.

### 5004 - Committee Already Exists

-   **Message**: "Committee already exists."
-   **HTTP Status**: 409 (Conflict)
-   **Description**: A committee with the same name already exists.
-   **Action**: Use a different name for the committee.

### 5005 - User Has Not Signed Petition

-   **Message**: "User has not signed this petition."
-   **HTTP Status**: 400 (Bad Request)
-   **Description**: The user has not signed the petition they are trying to unsign.
-   **Action**: No action needed.

---

## Role & Permission Errors (6xxx)

### 6000 - Role Not Found

-   **Message**: "The requested role could not be found."
-   **HTTP Status**: 404
-   **Description**: The role with the specified ID does not exist.
-   **Action**: Verify the role ID.

### 6001 - Role Already Exists

-   **Message**: "Role already exists."
-   **HTTP Status**: 409 (Conflict)
-   **Description**: A role with the same name already exists.
-   **Action**: Use a different name for the role.

### 6002 - Permission Not Found

-   **Message**: "The requested permission could not be found."
-   **HTTP Status**: 404
-   **Description**: The permission with the specified ID does not exist.
-   **Action**: Verify the permission ID.
