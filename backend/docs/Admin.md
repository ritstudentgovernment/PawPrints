# Admin Dashboard Guide

This document outlines the necessary features and corresponding API routes for building the admin dashboard. The front-end team can use this guide to understand the available functionalities and how to interact with the backend.

**Base URL**: All API routes are prefixed with `/api/v1` (except authentication which uses `/saml2`)

## Authentication

All admin endpoints require authentication. The API supports two authentication methods:

1. **JWT Bearer Token** (Production): Include in the `Authorization` header
   ```
   Authorization: Bearer <your-jwt-token>
   ```

2. **Cookie-based** (Production): Token stored in `pawcess` cookie (automatically set after SAML login)

3. **Development Mode**: Uses `DEV_USERNAME` environment variable (no token required)

### SAML Authentication Flow

- **Initiate Login**: `GET /saml2/` - Redirects to SAML Identity Provider
- **ACS Callback**: `POST /saml2/acs` - Handles SAML response and sets authentication cookie
- **Metadata**: `GET /saml2/metadata` - Returns service provider metadata XML

After successful authentication, the JWT token is valid for the duration specified in `ACCESS_TOKEN_EXPIRE_MINUTES` configuration.

## Permission-Based Access Control

All admin endpoints use **granular permission checks**. Users must have the appropriate permission assigned to their role to access each endpoint. The permission system follows a hierarchical structure:

- **Role**: A collection of permissions (e.g., "admin", "president", "student")
- **Permission**: Specific action rights (e.g., `user.list`, `role.create`)
- **User-Role Assignment**: Users can have multiple roles

### Common Permissions

- **User Management**: `user.list`, `user.read`, `user.create`, `user.update`, `user.role.assign`
- **Role Management**: `role.list`, `role.read`, `role.create`, `role.update`, `role.delete`, `role.permission.assign`
- **Permission Management**: `permission.list`, `permission.read`
- **Committee Management**: `committee.list`, `committee.read`, `committee.create`, `committee.update`, `committee.delete`, `committee.member.add`, `committee.member.remove`, `committee.member.list`
- **Petition Management**: `petition.create`, `petition.update.own`, `petition.update.any`, `petition.delete.own`, `petition.delete.any`, `petition.list`, `petition.read`, `petition.sign`

## Features Overview

The admin dashboard should provide administrators with the tools to manage users, roles, permissions, and committees effectively.

### 1. User Management

- **View All Users**: Display a paginated list of all users in the system
  - **Permission Required**: `user.list`
- **View Current User Profile**: Get profile information for the authenticated user
  - **Permission Required**: Authenticated user (no special permission)
- **Filter Users by Role**: Allow admins to filter the user list based on assigned roles (e.g., view all "admin" users)
  - **Permission Required**: `user.list`
- **Assign/Update a User's Role**: Change the role for a specific user (cannot change own role)
  - **Permission Required**: `user.role.assign`

### 2. Role Management

- **View All Roles**: Display a list of all available roles
  - **Permission Required**: `role.list`
- **View Roles with Permissions**: Show roles along with their assigned permissions
  - **Permission Required**: `role.list`
- **Create a New Role**: Add a new role to the system with optional permissions upon creation
  - **Permission Required**: `role.create`
- **Update a Role**: Modify the name and description of an existing role
  - **Permission Required**: `role.update`
- **Delete a Role**: Remove a role from the system (cascades to remove user assignments)
  - **Permission Required**: `role.delete`
- **Manage Role Permissions**: Update the set of permissions assigned to an existing role
  - **Permission Required**: `role.permission.assign`

### 3. Permission Management

- **View All Permissions**: Display a list of all possible permissions available in the system for assigning to roles
  - **Permission Required**: `permission.list`

### 4. Committee Management

- **View All Committees**: Display a list of all committees
  - **Permission Required**: `committee.list`
- **View Committee Members**: See a list of all users who are members of a specific committee
  - **Permission Required**: `committee.member.list`
- **Create a New Committee**: Add a new committee to the system
  - **Permission Required**: `committee.create`
- **Delete a Committee**: Remove a committee (cascades to remove member associations)
  - **Permission Required**: `committee.delete`
- **Add a User to a Committee**: Assign a user to a specific committee
  - **Permission Required**: `committee.member.add`
- **Remove a User from a Committee**: Remove a user from a specific committee (endpoint exists in service but not exposed in router yet)
  - **Permission Required**: `committee.member.remove`

### 5. Petition Management (User Context)

- **Sign a Petition**: Sign a specific petition as the current user
  - **Permission Required**: Authenticated user
- **Unsign a Petition**: Remove signature from a petition
  - **Permission Required**: Authenticated user
- **Check if User Can Sign**: Verify if the current user can sign a specific petition
  - **Permission Required**: Authenticated user

---

## API Routes for UI Development

Here are the specific API endpoints the front-end team should use to implement the features listed above. All endpoints return standardized error responses with error codes (see Error Handling section below).

### Authentication Endpoints

#### SAML Login Flow

- **Initiate SAML Login**:
  - **Endpoint**: `GET /saml2/`
  - **Description**: Redirects to SAML Identity Provider
  - **Response**: 302 redirect to IdP

- **Handle SAML Response** (ACS - Assertion Consumer Service):
  - **Endpoint**: `POST /saml2/acs`
  - **Body**: `SAMLResponse` (form data)
  - **Response**: Sets `pawcess` cookie and redirects to application
  - **Cookie**: `pawcess` contains JWT token

- **Get SAML Metadata**:
  - **Endpoint**: `GET /saml2/metadata`
  - **Description**: Returns service provider metadata XML
  - **Response**: XML document

### User Management

- **Get All Users**:
  - **Endpoint**: `GET /api/v1/users/`
  - **Permission**: `user.list`
  - **Query Params**:
    - `page` (int, default: 1) - Page number for pagination
    - `items_per_page` (int, default: 10) - Number of items per page
    - `role_name` (string, optional) - Filter users by role name
  - **Response**:
    ```json
    {
      "page_info": {
        "page": 1,
        "items": 10,
        "total_items": 50,
        "total_pages": 5
      },
      "users": [
        {
          "username": "abc1234",
          "first_name": "John",
          "last_name": "Doe",
          "roles": [
            {
              "id": 1,
              "name": "admin",
              "description": "Administrator role",
              "permissions": []
            }
          ]
        }
      ]
    }
    ```

- **Get Current User Profile**:
  - **Endpoint**: `GET /api/v1/users/me`
  - **Permission**: Authenticated user
  - **Response**: User profile with roles, committees, and petition statistics

- **Update a User's Role**:
  - **Endpoint**: `PUT /api/v1/users/{username}/role`
  - **Permission**: `user.role.assign`
  - **Path Params**: `username` (string) - Target user's username
  - **Body**:
    ```json
    {
      "role_id": 2
    }
    ```
  - **Response**: Success message
  - **Note**: Users cannot change their own role (returns 403 Permission Denied)

- **Sign a Petition**:
  - **Endpoint**: `POST /api/v1/users/{petition_id}/sign`
  - **Permission**: Authenticated user
  - **Path Params**: `petition_id` (int)
  - **Response**: `{ "message": "Petition signed successfully", "status_code": 200 }`

- **Unsign a Petition**:
  - **Endpoint**: `POST /api/v1/users/{petition_id}/unsign`
  - **Permission**: Authenticated user
  - **Path Params**: `petition_id` (int)
  - **Response**: `{ "message": "Petition unsigned successfully", "status_code": 200 }`

- **Check if User Can Sign**:
  - **Endpoint**: `GET /api/v1/users/{petition_id}/can_sign`
  - **Permission**: Authenticated user
  - **Path Params**: `petition_id` (int)
  - **Response**: `{ "message": "User can sign the petition", "status_code": 200 }`
  - **Note**: Returns error if user cannot sign (already signed, petition expired, etc.)

### Role Management

- **Get All Roles**:
  - **Endpoint**: `GET /api/v1/roles/`
  - **Permission**: `role.list`
  - **Response**:
    ```json
    {
      "roles": [
        {
          "id": 1,
          "name": "admin",
          "description": "Administrator role",
          "permissions": []
        }
      ]
    }
    ```

- **Get All Roles with Permissions**:
  - **Endpoint**: `GET /api/v1/roles/permissions`
  - **Permission**: `role.list`
  - **Response**: Same as Get All Roles, but with `permissions` array populated
  - **Note**: This endpoint is more expensive - use only when permission details are needed

- **Create a New Role**:
  - **Endpoint**: `POST /api/v1/roles/`
  - **Permission**: `role.create`
  - **Body**:
    ```json
    {
      "name": "moderator",
      "description": "Moderator role with limited permissions",
      "permissions": [
        {
          "id": 1,
          "name": "petition.list"
        },
        {
          "id": 2,
          "name": "petition.update.any"
        }
      ]
    }
    ```
  - **Response**: Created role object
  - **Error**: Returns 6001 (409 Conflict) if role name already exists

- **Update a Role's Name/Description**:
  - **Endpoint**: `PUT /api/v1/roles/{role_id}`
  - **Permission**: `role.update`
  - **Path Params**: `role_id` (int)
  - **Body**:
    ```json
    {
      "name": "updated_name",
      "description": "Updated description"
    }
    ```
  - **Response**: Updated role object

- **Delete a Role**:
  - **Endpoint**: `DELETE /api/v1/roles/{role_id}`
  - **Permission**: `role.delete`
  - **Path Params**: `role_id` (int)
  - **Response**: `{ "message": "Role deleted successfully.", "status_code": 200 }`

- **Update Role Permissions**:
  - **Endpoint**: `PUT /api/v1/roles/{role_id}/permissions`
  - **Permission**: `role.permission.assign`
  - **Path Params**: `role_id` (int)
  - **Body**:
    ```json
    {
      "permission_ids": [1, 2, 3, 5]
    }
    ```
  - **Response**: Updated role object with new permissions
  - **Note**: This replaces all existing permissions with the provided list

### Permission Management

- **Get All Permissions**:
  - **Endpoint**: `GET /api/v1/permissions/`
  - **Permission**: `permission.list`
  - **Response**:
    ```json
    {
      "permissions": [
        {
          "id": 1,
          "name": "user.list",
          "description": "List all users"
        },
        {
          "id": 2,
          "name": "user.role.assign",
          "description": "Assign roles to users"
        }
      ]
    }
    ```

### Committee Management

- **Get All Committees**:
  - **Endpoint**: `GET /api/v1/committees/`
  - **Permission**: `committee.list`
  - **Response**:
    ```json
    [
      {
        "id": 1,
        "name": "Academic Affairs",
        "description": "Handles academic-related petitions"
      }
    ]
    ```

- **Get Members of a Committee**:
  - **Endpoint**: `GET /api/v1/committees/{committee_id}/members`
  - **Permission**: `committee.member.list`
  - **Path Params**: `committee_id` (int)
  - **Response**: Array of UserSchema objects

- **Create a New Committee**:
  - **Endpoint**: `POST /api/v1/committees/create`
  - **Permission**: `committee.create`
  - **Body**:
    ```json
    {
      "name": "Student Life",
      "description": "Manages student life and campus activities"
    }
    ```
  - **Response**: Created committee object (status 201)

- **Delete a Committee**:
  - **Endpoint**: `DELETE /api/v1/committees/delete`
  - **Permission**: `committee.delete`
  - **Query Params**: `committee_id` (int)
  - **Response**: Status 201 (no body)

- **Add a User to a Committee**:
  - **Endpoint**: `POST /api/v1/committees/{committee_id}/members`
  - **Permission**: `committee.member.add`
  - **Path Params**: `committee_id` (int)
  - **Body**:
    ```json
    {
      "username": "abc1234"
    }
    ```
  - **Response**:
    ```json
    {
      "user": { /* UserSchema */ },
      "committee": { /* CommitteeSchema */ }
    }
    ```
  - **Status**: 201 Created

---

## Error Handling

All API endpoints use a standardized error response format. When an error occurs, you'll receive:

```json
{
  "detail": {
    "code": "2001",
    "message": "User lacks required permission: `role.create`",
    "context": {
      "username": "abc1234",
      "permission": "role.create",
      "op": "has_permission"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Category | Description |
|------|-------------|----------|-------------|
| 1000 | 500 | Database/Server | Internal server error or database failure |
| 2000 | 401 | Authentication | Authentication failed (missing or invalid token) |
| 2001 | 403 | Authorization | Permission denied (user lacks required permission) |
| 3000 | 400 | Validation | Invalid request body or parameters |
| 4000 | 404 | Petition | Petition not found |
| 4001 | 409 | Petition | Petition already signed |
| 5000 | 404 | User | User not found |
| 5001 | 404 | Committee | Committee not found |
| 5002 | 404 | Committee | Committee member not found |
| 5003 | 409 | Committee | User already in committee |
| 5004 | 409 | Committee | Committee already exists |
| 5005 | 400 | Petition | User has not signed petition |
| 6000 | 404 | Role | Role not found |
| 6001 | 409 | Role | Role already exists |
| 6002 | 404 | Permission | Permission not found |

### Common Error Scenarios

1. **Missing Authentication** (2000):
   - No `Authorization` header or `pawcess` cookie provided
   - Solution: Include JWT token in request

2. **Permission Denied** (2001):
   - User lacks required permission for the endpoint
   - User has no roles assigned
   - Solution: Check user's role assignments and role permissions

3. **Invalid Request Body** (3000):
   - Request body doesn't match expected schema
   - Required fields missing
   - Solution: Validate request body against schemas

4. **Self-Role Assignment** (2001):
   - User attempting to change their own role
   - Solution: Use different admin account or have another admin update the role

---

## Request/Response Examples

### Example: Creating a Role with Permissions

**Request**:
```bash
curl -X POST https://api.pawprints.example.com/api/v1/roles/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "content_moderator",
    "description": "Can moderate petitions and comments",
    "permissions": [
      {"id": 10, "name": "petition.update.any"},
      {"id": 15, "name": "petition.delete.any"}
    ]
  }'
```

**Success Response** (201):
```json
{
  "id": 5,
  "name": "content_moderator",
  "description": "Can moderate petitions and comments",
  "permissions": [
    {
      "id": 10,
      "name": "petition.update.any",
      "description": "Update any petition"
    },
    {
      "id": 15,
      "name": "petition.delete.any",
      "description": "Delete any petition"
    }
  ]
}
```

**Error Response** (409 - Role Already Exists):
```json
{
  "detail": {
    "code": "6001",
    "message": "Role 'content_moderator' already exists.",
    "context": {
      "op": "role_create",
      "name": "content_moderator"
    }
  }
}
```

### Example: Updating User Role

**Request**:
```bash
curl -X PUT https://api.pawprints.example.com/api/v1/users/jdoe123/role \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 3
  }'
```

**Success Response** (200):
```json
{
  "message": "User role updated successfully",
  "status_code": 200
}
```

---

## Best Practices for Frontend Implementation

1. **Token Management**:
   - Store JWT token securely (httpOnly cookies preferred)
   - Refresh token before expiration
   - Clear token on logout

2. **Permission Checking**:
   - Cache user permissions on login
   - Show/hide UI elements based on permissions
   - Always expect permission denied errors from backend

3. **Error Handling**:
   - Use error codes to determine user-friendly messages
   - Handle 401 errors by redirecting to login
   - Handle 403 errors by showing permission denied message
   - Use `context` field for debugging

4. **Pagination**:
   - Implement pagination UI for user lists
   - Allow users to adjust `items_per_page`
   - Show total pages and current page

5. **Loading States**:
   - Show loading indicators during API calls
   - Disable buttons during mutations
   - Handle network failures gracefully

6. **Optimistic Updates**:
   - Update UI optimistically for better UX
   - Revert on error
   - Show success/error notifications

---

## Development Mode

When running in development mode (`MODE=DEV`), authentication is simplified:

- No JWT token required
- Uses `DEV_USERNAME` environment variable
- Permission checks are bypassed in some cases
- **Do not use in production!**

---

## Additional Resources

- **Error Code Reference**: See `docs/ErrorCodes.md` for complete error code documentation
- **Petition Search**: See `docs/PetitionSearch.md` for petition search and filtering capabilities
- **Tag System**: See `docs/TAG_SYSTEM.md` for petition tagging functionality
- **API Documentation**: Interactive API docs available at `/docs` endpoint (Swagger UI)
