# Petition Tag System Documentation

## Overview

The petition tag system allows administrators to categorize petitions with a single tag per petition. Tags help organize and filter petitions by topic or category.

## Database Schema

### Tags Table
- **id**: Primary key (auto-increment)
- **name**: Unique tag name (max 50 chars)
- **description**: Optional description (max 255 chars)
- **color**: Hex color code for UI display (e.g., "#FF5733")
- **created_at**: Timestamp of creation

### Petition Tags Table
- **petition_id**: Foreign key to petitions (primary key, unique - enforces one tag per petition)
- **tag_id**: Foreign key to tags
- **assigned_at**: Timestamp when tag was assigned
- **assigned_by**: Username of who assigned the tag (nullable)

**Constraint**: Each petition can have at most ONE tag (enforced by unique constraint on petition_id)

## Permissions

### Tag Management
- `tag.create` - Create new tags
- `tag.update` - Update existing tags
- `tag.delete` - Delete tags
- `tag.list` - List all tags
- `tag.read` - Read individual tag details

### Petition Tagging
- `petition.tag.add` - Add or update tag on a petition
- `petition.tag.remove` - Remove tag from a petition

## API Endpoints

### Tag Management

#### Create Tag
```
POST /api/v1/tags
Permission: tag.create

Request Body:
{
  "name": "Academics",
  "description": "Academic-related petitions",
  "color": "#3B82F6"
}

Response: 201 Created
{
  "id": 1,
  "name": "Academics",
  "description": "Academic-related petitions",
  "color": "#3B82F6",
  "created_at": "2025-11-19T12:00:00Z"
}
```

#### List Tags
```
GET /api/v1/tags?page=1&items_per_page=50
Permission: tag.list

Response: 200 OK
{
  "page_info": {
    "page": 1,
    "items": 8,
    "total_items": 8,
    "total_pages": 1
  },
  "tags": [
    {
      "id": 1,
      "name": "Academics",
      "description": "Academic-related petitions",
      "color": "#3B82F6",
      "created_at": "2025-11-19T12:00:00Z"
    },
    ...
  ]
}
```

#### Get Tag
```
GET /api/v1/tags/{tag_id}
Permission: tag.read

Response: 200 OK
{
  "id": 1,
  "name": "Academics",
  "description": "Academic-related petitions",
  "color": "#3B82F6",
  "created_at": "2025-11-19T12:00:00Z"
}
```

#### Update Tag
```
PUT /api/v1/tags/{tag_id}
Permission: tag.update

Request Body:
{
  "description": "Updated description",
  "color": "#FF5733"
}

Response: 200 OK
{
  "id": 1,
  "name": "Academics",
  "description": "Updated description",
  "color": "#FF5733",
  "created_at": "2025-11-19T12:00:00Z"
}
```

#### Delete Tag
```
DELETE /api/v1/tags/{tag_id}
Permission: tag.delete

Response: 204 No Content
```

### Petition Tagging

#### Add/Update Tag on Petition
```
POST /api/v1/tags/petition/{petition_id}
Permission: petition.tag.add

Request Body:
{
  "tag_id": 1
}

Response: 200 OK
{
  "petition_id": 123,
  "tag": {
    "id": 1,
    "name": "Academics",
    "description": "Academic-related petitions",
    "color": "#3B82F6",
    "created_at": "2025-11-19T12:00:00Z"
  },
  "assigned_at": "2025-11-19T13:00:00Z",
  "assigned_by": "admin_user"
}

Note: If a tag already exists on the petition, it will be replaced with the new tag.
```

#### Remove Tag from Petition
```
DELETE /api/v1/tags/petition/{petition_id}
Permission: petition.tag.remove

Response: 204 No Content
```

#### Get Petition's Tag
```
GET /api/v1/tags/petition/{petition_id}
Permission: petition.read

Response: 200 OK
{
  "petition_id": 123,
  "tag": {
    "id": 1,
    "name": "Academics",
    "description": "Academic-related petitions",
    "color": "#3B82F6",
    "created_at": "2025-11-19T12:00:00Z"
  },
  "assigned_at": "2025-11-19T13:00:00Z",
  "assigned_by": "admin_user"
}

Returns null if no tag is assigned.
```

## Petition Retrieval

When retrieving petitions through existing endpoints (list, search, etc.), the tag is automatically included in the response:

```json
{
  "page_info": {...},
  "petitions": [
    {
      "id": 123,
      "title": "Improve Library Hours",
      "description": "...",
      "author": {...},
      "total_signatures": 50,
      "created_at": "2025-11-19T12:00:00Z",
      "status": 0,
      "expires": "2025-06-19T12:00:00Z",
      "has_response": false,
      "is_draft": false,
      "response": null,
      "updates": null,
      "committees": null,
      "tag": {
        "id": 1,
        "name": "Academics",
        "description": "Academic-related petitions",
        "color": "#3B82F6",
        "created_at": "2025-11-19T12:00:00Z"
      }
    }
  ]
}
```

The `tag` field will be `null` if no tag is assigned to the petition.

## Setup Instructions

### 1. Database Migration

Run the SQL migration scripts:

```bash
# Apply tag tables
psql -U <username> -d <database> -f dbSetup/add_tag_tables.sql

# Add permissions
psql -U <username> -d <database> -f dbSetup/add_tag_permissions.sql
```

Or use Alembic:

```bash
env/bin/alembic upgrade head
```

### 2. Assign Permissions to Roles

You need to assign the new tag permissions to appropriate roles. Example for admin role:

```sql
-- Get admin role ID
SELECT id FROM roles WHERE name = 'Admin';

-- Get tag permission IDs
SELECT id, name FROM permissions WHERE name LIKE 'tag.%' OR name LIKE 'petition.tag.%';

-- Assign permissions (replace <role_id> with actual ID)
INSERT INTO role_permissions (role_id, permission_id)
SELECT <role_id>, id FROM permissions
WHERE name IN (
  'tag.create', 'tag.update', 'tag.delete', 'tag.list', 'tag.read',
  'petition.tag.add', 'petition.tag.remove'
)
ON CONFLICT DO NOTHING;
```

### 3. Default Tags

The migration script includes 8 default tags:
- Academics (#3B82F6)
- Campus Life (#10B981)
- Housing (#F59E0B)
- Dining (#EF4444)
- Safety (#8B5CF6)
- Sustainability (#14B8A6)
- Technology (#6366F1)
- Health (#EC4899)

You can add more tags via the API or directly in the database.

## Implementation Details

### Service Layer
- **TagService**: Located at `pawprints/api/service/tag_service.py`
  - Handles all tag and petition-tag operations
  - Validates existence of petitions and tags
  - Enforces business rules (one tag per petition)

### ORM Models
- **Tag**: Located at `pawprints/models/orm.py`
  - Represents a tag entity
  - Has one-to-many relationship with PetitionTag

- **PetitionTag**: Located at `pawprints/models/orm.py`
  - Association table linking petitions to tags
  - One-to-one relationship with Petition (enforced by unique constraint)

### Schemas
Located at `pawprints/models/schema.py`:
- **TagCreate**: For creating new tags
- **TagUpdate**: For updating tags (all fields optional)
- **TagSchema**: For returning tag data
- **TagListResponse**: Paginated list of tags
- **PetitionTagAssign**: For assigning tags to petitions
- **PetitionTagResponse**: For returning petition-tag assignments

### Router
- **tag_router**: Located at `pawprints/api/tag_router.py`
  - Registers all tag-related endpoints
  - Enforces permission checks via dependencies

### Exceptions
- **TagNotFoundError** (8000): Tag doesn't exist
- **TagAlreadyExistsError** (8001): Duplicate tag name

## Usage Examples

### Python Client Example

```python
import requests

BASE_URL = "https://api.example.com"
headers = {"Authorization": "Bearer <token>"}

# Create a tag
response = requests.post(
    f"{BASE_URL}/api/v1/tags",
    json={"name": "Campus Safety", "color": "#FF0000"},
    headers=headers
)
tag = response.json()

# Tag a petition
requests.post(
    f"{BASE_URL}/api/v1/tags/petition/123",
    json={"tag_id": tag["id"]},
    headers=headers
)

# Get petitions (tags included automatically)
response = requests.get(
    f"{BASE_URL}/api/v1/petitions?page=1",
    headers=headers
)
petitions = response.json()["petitions"]
for petition in petitions:
    if petition["tag"]:
        print(f"Petition {petition['id']}: {petition['tag']['name']}")
```

## Notes

- **One Tag Per Petition**: The system enforces that each petition can have at most one tag. If you assign a new tag to a petition that already has a tag, the old tag will be replaced.

- **Cascade Delete**: If a tag is deleted, all petition-tag associations using that tag are automatically removed.

- **Tag Filtering**: While not implemented in this version, you can extend the petition search/filter endpoints to support filtering by tag_id.

- **Performance**: Tags are eager-loaded with petitions to avoid N+1 queries.
