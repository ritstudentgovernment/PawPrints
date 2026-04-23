# Petitions — Search & Filter (Frontend Guide)

* **Filter-only list:** `GET /api/v1/petitions`
* **Search + filters:** `GET /api/v1/petitions/search`

---

## Table of Contents

1. [What each endpoint does](#what-each-endpoint-does)
2. [Response shape](#response-shape)
3. [Parameters (shared + search-only)](#parameters-shared--search-only)
4. [Encoding rules (must-read)](#encoding-rules-must-read)
5. [Common URL patterns](#common-url-patterns)
6. [How filters combine](#how-filters-combine)
7. [Sorting rules](#sorting-rules)
8. [Includes (expanding related data)](#includes-expanding-related-data)
9. [UX guidelines](#ux-guidelines)
10. [Edge cases & pitfalls](#edge-cases--pitfalls)
11. [Performance checklist](#performance-checklist)
12. [QA scenarios](#qa-scenarios)
13. [Status values](#status-values)
14. [Future-proofing for vector search](#future-proofing-for-vector-search)
15. [Quick reference](#quick-reference)

---

## What each endpoint does

### `GET /api/v1/petitions` — Filter-only list

Use this when you want to **browse or filter** without a text query.

* Supports **all filters** (status, committees, ranges, etc.).
* Supports sorting by **`created_at`** and **`total_signatures`**.
* **No** text search and **no** `rank` sorting here.

### `GET /api/v1/petitions/search` — Search + filters

Use this when you want **full-text search** (title + description) **plus** the same filters as above.

* Adds the `query` parameter (user text).
* Adds **`rank`** sorting (only meaningful when `query` is present).
* If `query` is omitted, it behaves like filter-only (default sort is newest).

> **No results:** both endpoints return **404** when there are no matches. Treat that as an **empty state** in the UI, not a fatal error.

---

## Response shape

Both endpoints return the same structure on success:

```json
{
  "page_info": {
    "page": 1,
    "items": 10,
    "total_items": 123,
    "total_pages": 13
  },
  "petitions": [
    {
      "id": 123,
      "title": "Fix the bus lane",
      "description": "…",
      "author": { "username": "alice", "first_name": "Alice", "last_name": "Doe", "email": "…" },
      "total_signatures": 245,
      "created_at": "2025-10-01T12:34:56Z",
      "status": 0,
      "expires": "2026-04-29T12:34:56Z",
      "has_response": false,
      "is_draft": false,

      // present only if requested via include=
      "committees": [{ "id": 3, "name": "Transport", "description": "…" }],
      "response": { "message": "…", "is_draft": false, "is_approved": true, "created_at": "…" },
      "updates": [{ "message": "…", "is_draft": true, "is_approved": false, "created_at": "…" }]
    }
  ]
}
```

---

## Parameters (shared + search-only)

### Shared filter parameters (work on **both** endpoints)

| Name              | Type            | Example                                  | Notes                                                                         |
| ----------------- | --------------- | ---------------------------------------- | ----------------------------------------------------------------------------- |
| `page`            | int (≥1)        | `page=1`                                 | 1-based pagination.                                                           |
| `per_page`        | int (1..100)    | `per_page=10`                            | Page size. (`items_per_page` may be supported as an alias.)                   |
| `status`          | repeated int    | `status=0&status=2`                      | 0=ACTIVE, 1=CHARGED, 2=RESPONDED, 3=EXPIRED. Repeat to OR them.               |
| `committee_id`    | repeated int    | `committee_id=3&committee_id=7`          | Repeatable.                                                                   |
| `committee_match` | `any` | `all`   | `committee_match=all`                    | `any` (default) = OR; `all` = must be in **all** listed committees.           |
| `has_response`    | boolean         | `has_response=true`                      | Lowercase `true`/`false`.                                                     |
| `is_draft`        | boolean         | `is_draft=false`                         | Defaults to `false`.                                                          |
| `signatures`      | range           | `signatures=50..100`                     | Format `min..max`. Open ends: `100..` or `..200`.                             |
| `created`         | date range      | `created=2025-01-01..2025-10-17`         | Dates `YYYY-MM-DD`. Open ends allowed.                                        |
| `sort`            | repeated string | `sort=created_at&sort=-total_signatures` | On `/`, allowed keys: `created_at`, `total_signatures` (prefix `-` for desc). |
| `include`         | repeated string | `include=committees&include=response`    | Expands data: `committees`, `updates`, `response`.                            |

### Search-only parameters (only for **`/search`**)

| Name    | Type   | Example                      | Notes                                                  |
| ------- | ------ | ---------------------------- | ------------------------------------------------------ |
| `query` | string | `query=Reopen the`           | Full-text search (web-style parsing; raw input is OK). |
| `sort`  | string | `sort=-rank&sort=created_at` | `rank` is meaningful **only when** `query` is present. |

---

## Encoding rules (must-read)

* **Arrays:** repeat the key (e.g., `status=0&status=2`). Do **not** comma-join.
* **Ranges:** send a **single string** with `..` (e.g., `signatures=100..`, `..200`, or `50..100`).
* **Booleans:** send lowercase `true` / `false`.
* **Default sort:** if `query` is missing, the backend defaults to `created_at desc`.
* **`rank` without `query`:** ignored server-side; prefer not to send it.

---

## Common URL patterns

### Filter-only (`/api/v1/petitions`)

* Newest:
  `/api/v1/petitions?page=1&per_page=10`

* Active **or** Responded:
  `/api/v1/petitions?status=0&status=2&page=1&per_page=10`

* Committees **ALL** (must be in 3 and 7):
  `/api/v1/petitions?committee_id=3&committee_id=7&committee_match=all&page=1&per_page=10`

* ≥100 signatures & has response:
  `/api/v1/petitions?signatures=100..&has_response=true&page=1&per_page=10`

* Created in range (ANY committees 1 or 3):
  `/api/v1/petitions?committee_id=1&committee_id=3&committee_match=any&created=2025-01-01..2025-10-17&page=1&per_page=10`

### Search + filters (`/api/v1/petitions/search`)

* Best match then newest:
  `/api/v1/petitions/search?query=Reopen%20the&sort=-rank&sort=created_at&page=1&per_page=10`

* Search “SHED”, include committees + response:
  `/api/v1/petitions/search?query=SHED&include=committees&include=response&page=1&per_page=10`

---

## How filters combine

* **`status`**: OR across repeated values → `status=0&status=2` returns Active **or** Responded.
* **`committee_id`**:

  * `committee_match=any` (default) behaves like OR.
  * `committee_match=all` requires presence in **all** listed committees.
* **Ranges** (`signatures`, `created`): intersect with other filters.
* **`has_response`**: yes/no filter applied to the set.
* **`include`** doesn’t change which rows match; it only expands each row.

---

## Sorting rules

* **`/api/v1/petitions` (filter-only):**
  Allowed: `created_at`, `total_signatures` (prefix `-` for descending).

* **`/api/v1/petitions/search` (search + filters):**
  Allowed: `rank`, `created_at`, `total_signatures`.
  Use **`rank`** only when `query` is present (typically `sort=-rank&sort=created_at`).

* **If no sort is provided:** newest first (`created_at desc`).

---

## Includes (expanding related data)

* `include=committees` → adds `committees: Committee[]` to each petition.
* `include=response` → adds the final `response` object (if any).
* `include=updates` → adds all `updates` (heavier payload).
* Request **only what you need** on list views. Use more includes on detail views.

---

## UX guidelines

* **URL-synced state:** keep all filters in the URL so views are shareable and history works.
* **Debounce** `query` (250–300 ms) on `/search`.
* **Guard `rank`:** only offer `rank` sort when `query` is present.
* **Empty state:** treat **404** as “no matches”; show a friendly empty state and a **Clear filters** action.
* **Chips:** render chips for active filters with quick remove actions.
* **Accessibility:** keyboard-navigable controls, ARIA labels; announce result counts.

---

## Edge cases & pitfalls

* Clearing the search box → **remove** `query` from the URL (don’t send `query=` empty).
* Sending `rank` without `query` → server ignores it; remove it client-side.
* Invalid ranges (`min > max`) → normalize or drop the bad side before sending.
* Unknown committee IDs → expect 404 (no matches).
* Arrays must repeat keys; don’t send `status=0,2`.
* Booleans must be lowercase `true`/`false`.

---

## Performance checklist

* Debounce text input.
* Keep `per_page` modest (10–20).
* Avoid heavy `include` fields on list views unless needed.
* Cache by **full parameter set** (e.g., React Query key includes all params).
* Batch URL updates to avoid excessive history entries.

---

## QA scenarios

1. **Filter-only, no filters** → newest petitions appear; paging works.
2. **Search Phrases** (`Reopen the`, `SHED`, `Help Me`) → results look reasonable; `rank` active.
3. **Status OR** (`0` + `2`) → both types appear.
4. **Committees ANY vs ALL** → ALL reduces set as expected.
5. **Range filters**: `signatures=100..`, `..50`, `25..100`; `created` open/closed intervals.
6. **Has response** toggles.
7. **404** → UI shows empty state, not an error toast.
8. **Includes** → fields present only when requested.
9. **Deep links** → pasting a complex URL reconstructs state.
10. **Rank guard** → `rank` option hidden/disabled when `query` is empty.

---

## Status values

* `0` — **Active**
* `1` — **Charged** (assigned to committee)
* `2` — **Responded** (final response exists)
* `3` — **Expired** (auto-closed after ~7 months)

---

## Future-proofing for vector search

If semantic (vector) search is added later:

* The **same filters** and URL patterns continue to work.
* You may see a new param like `mode=fts|vector|hybrid`; treat it like any other param.
* Keep the UI label for `rank` generic (e.g., “Best match”) so wording stays accurate.

---

## Quick reference

* **Filter-only, newest:**
  `/api/v1/petitions?page=1&per_page=10`

* **Filter-only, Active or Responded:**
  `/api/v1/petitions?status=0&status=2&page=1&per_page=10`

* **Search, best match + newest:**
  `/api/v1/petitions/search?query=Reopen%20the&sort=-rank&sort=created_at&page=1&per_page=10`

* **Search with includes:**
  `/api/v1/petitions/search?query=SHED&include=committees&include=response&page=1&per_page=10`

---
