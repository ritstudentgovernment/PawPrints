// src/app/api/specialRoute.ts

export const dynamic = 'force-dynamic';

// Server-side: prefers INTERNAL_API_URL (Docker-internal, e.g. http://api:8000) so SSR
// requests stay on the internal network instead of round-tripping through nginx.
// Client-side (and server fallback): uses NEXT_PUBLIC_API_URL baked in at build time.
export const API_URL =
  (typeof window === 'undefined' ? process.env.INTERNAL_API_URL : undefined) ??
  process.env.NEXT_PUBLIC_API_URL ??
  'http://localhost:8000';

const buildUrl = (path: string, params: Record<string, any>) => {
    const url = new URL(`${API_URL}${path}`);

    Object.entries(params).forEach(([key, value]) => {
        // Skip undefined, null, and empty string values so they are not included in the query
        if (value === undefined || value === null || value === '') return;

        if (Array.isArray(value)) {
            value.forEach(v => {
                if (v === undefined || v === null || v === '') return;
                url.searchParams.append(key, String(v));
            });
        } else {
            url.searchParams.append(key, String(value));
        }
    });

    return url.toString();
};


export async function GET(
    query: string | undefined, 
    status: string | undefined, 
    tag_id: string | undefined,
    page = 1,
    items_per_page = 40) {
    // Construct the URL: /api/v1/petitions/search?[maybe query=xyz]&page=1...
    if (query === undefined) query = '';

    const url = buildUrl('/api/v1/petitions/search?', {
        tag_id: tag_id,
        status: status,
        query: query,
        page: page,
        items_per_page: items_per_page
    });

    const res = await fetch(url, {
        method: 'GET', 
        headers: {
            "Content-type": "application/json"
        }
    });

    if (!res.ok) {
        return { petitions: [] };
    }

    return await res.json();
}

export async function GETTag(tag_id: string, page = 1, items_per_page = 40) {
    const url = buildUrl('/api/v1/petitions/search', {
        tag_id: tag_id,
        page: page,
        items_per_page: items_per_page
    });

    const res = await fetch(url, {
        method: 'GET', 
        headers: {
            "Content-type": "application/json"
        }
    });

    return await res.json();
}





