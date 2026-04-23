"use client";

import { useEffect, useState, useCallback } from "react";
import { API_URL } from "../api/specialRoute";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import "./pawstats.css";

// ─── Types ────────────────────────────────────────────────────────────────────

type StatsOverview = {
  total_petitions: number;
  active_petitions: number;
  charged_petitions: number;
  responded_petitions: number;
  expired_petitions: number;
  total_signatures: number;
  total_users: number;
  total_committees: number;
  total_tags: number;
  petitions_with_response_pct: number;
};

type StatusBreakdownItem = {
  status: string;
  count: number;
  percentage: number;
};

type StatusBreakdownResponse = {
  total: number;
  breakdown: StatusBreakdownItem[];
};

type PetitionTimelinePoint = {
  period: string;
  created: number;
  responded: number;
  expired: number;
  charged: number;
  signatures: number;
};

type PetitionTimeline = {
  granularity: string;
  data: PetitionTimelinePoint[];
};

type TagStats = {
  tag_id: number;
  tag_name: string;
  color: string | null;
  petition_count: number;
  percentage: number;
};

type TagBreakdownResponse = {
  total_tagged_petitions: number;
  breakdown: TagStats[];
};

type CommitteePerformanceStats = {
  committee_id: number;
  committee_name: string;
  petitions_assigned: number;
  petitions_responded: number;
  response_rate_pct: number;
  avg_response_days: number | null;
  pending_count: number;
};

type CommitteePerformanceResponse = {
  committees: CommitteePerformanceStats[];
};

type UserGrowthPoint = {
  period: string;
  new_users: number;
  total_users: number;
};

type UserGrowthResponse = {
  granularity: string;
  data: UserGrowthPoint[];
};

type SignatureVelocityItem = {
  petition_id: number;
  petition_title: string;
  total_signatures: number;
  first_signature_at: string | null;
  latest_signature_at: string | null;
  peak_daily_signatures: number | null;
  peak_day: string | null;
};

type SignatureVelocityResponse = {
  petitions: SignatureVelocityItem[];
};

type ActivityTrendPoint = {
  date: string;
  total_requests: number;
  total_unique_users: number;
  total_logins: number;
};

type ActivityTrendResponse = {
  data: ActivityTrendPoint[];
};

type UserBreakdownByType = {
  account_type: string;
  user_count: number;
  percentage: number;
};

type UserBreakdownByCollege = {
  college: string | null;
  user_count: number;
  percentage: number;
};

type UserBreakdownResponse = {
  total_users: number;
  by_college: UserBreakdownByCollege[];
  by_account_type: UserBreakdownByType[];
};

// ─── Theme Colors ──────────────────────────────────────────────────────────────

const THEME = {
  darkBrown: "#2c1a0e",
  medBrown: "#6b3a2a",
  lightBrown: "#9d5f4b",
  orange: "#f36e21",
  orangeDim: "#c4581a",
  slate: "#36454F",
  slateDim: "#4e6270",
  cream: "#fdf8f4",
  border: "#e8ddd5",
  text: "#1a0a00",
  textMuted: "#7a5c4f",
};

const BAR_COLORS = [
  THEME.darkBrown,
  THEME.medBrown,
  THEME.lightBrown,
  THEME.orange,
  THEME.orangeDim,
  THEME.slate,
  THEME.slateDim,
];

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: THEME.orange,
  CHARGED: THEME.slate,
  RESPONDED: THEME.medBrown,
  EXPIRED: "#c0a898",
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function pct(n: number): string {
  return `${n.toFixed(1)}%`;
}

function shortPeriod(period: string): string {
  if (!period) return "";
  // e.g. "2025-01" → "Jan '25", "2025-W04" → "W04", "2025-01-15" → "Jan 15"
  const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const mMatch = period.match(/^(\d{4})-(\d{2})$/);
  if (mMatch) {
    const yr = mMatch[1].slice(2);
    const mo = parseInt(mMatch[2], 10);
    return `${monthNames[mo - 1]} '${yr}`;
  }
  const wMatch = period.match(/^(\d{4})-W(\d{2})$/);
  if (wMatch) return `W${wMatch[2]}`;
  const dMatch = period.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (dMatch) {
    const mo = parseInt(dMatch[2], 10);
    return `${monthNames[mo - 1]} ${dMatch[3]}`;
  }
  return period;
}

// ─── Sub-components ────────────────────────────────────────────────────────────

function KpiCard({
  icon,
  label,
  value,
  sub,
  accent,
}: {
  icon: string;
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="ps-kpi-card" style={{ borderTopColor: accent ?? THEME.orange }}>
      <div className="ps-kpi-icon" aria-hidden="true">
        <span className="material-symbols-outlined">{icon}</span>
      </div>
      <div className="ps-kpi-body">
        <p className="ps-kpi-label">{label}</p>
        <p className="ps-kpi-value">{typeof value === "number" ? fmt(value) : value}</p>
        {sub && <p className="ps-kpi-sub">{sub}</p>}
      </div>
    </div>
  );
}

function SectionTitle({ icon, title, desc }: { icon: string; title: string; desc?: string }) {
  return (
    <div className="ps-section-title">
      <h2>
        <span className="material-symbols-outlined ps-section-icon" aria-hidden="true">{icon}</span>
        {title}
      </h2>
      {desc && <p>{desc}</p>}
    </div>
  );
}

function ChartCard({ title, children }: { title?: string; children: React.ReactNode }) {
  return (
    <div className="ps-chart-card">
      {title && <p className="ps-chart-title">{title}</p>}
      {children}
    </div>
  );
}

function LoadingBar() {
  return <div className="ps-loading-bar"><span /><span /><span /></div>;
}

function EmptyState({ message }: { message: string }) {
  return <div className="ps-empty">{message}</div>;
}

// Custom tooltip styled to theme
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="ps-tooltip">
      <p className="ps-tooltip-label">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: <strong>{typeof p.value === "number" ? p.value.toLocaleString() : p.value}</strong>
        </p>
      ))}
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────────────────

export default function AdminPawstatsSection() {
  const [overview, setOverview] = useState<StatsOverview | null>(null);
  const [statusBreakdown, setStatusBreakdown] = useState<StatusBreakdownResponse | null>(null);
  const [timeline, setTimeline] = useState<PetitionTimeline | null>(null);
  const [tags, setTags] = useState<TagBreakdownResponse | null>(null);
  const [committees, setCommittees] = useState<CommitteePerformanceResponse | null>(null);
  const [userGrowth, setUserGrowth] = useState<UserGrowthResponse | null>(null);
  const [velocity, setVelocity] = useState<SignatureVelocityResponse | null>(null);
  const [activityTrend, setActivityTrend] = useState<ActivityTrendResponse | null>(null);
  const [userBreakdown, setUserBreakdown] = useState<UserBreakdownResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [timelineGranularity, setTimelineGranularity] = useState<"daily" | "weekly" | "monthly">("monthly");

  const fetchAll = useCallback(async (gran = timelineGranularity) => {
    setLoading(true);
    setError(null);
    try {
      const [
        ovRes,
        sbRes,
        tlRes,
        tgRes,
        cmRes,
        ugRes,
        vlRes,
        atRes,
        ubRes,
      ] = await Promise.all([
        fetch(`${API_URL}/api/v1/stats/overview`),
        fetch(`${API_URL}/api/v1/stats/petitions/status-breakdown`),
        fetch(`${API_URL}/api/v1/stats/petitions/timeline?granularity=${gran}`),
        fetch(`${API_URL}/api/v1/stats/tags/popularity?limit=12`),
        fetch(`${API_URL}/api/v1/stats/committees/performance`),
        fetch(`${API_URL}/api/v1/stats/users/growth?granularity=monthly`),
        fetch(`${API_URL}/api/v1/stats/signatures/velocity?limit=10`),
        fetch(`${API_URL}/api/v1/stats/activity/trend`),
        fetch(`${API_URL}/api/v1/stats/users/breakdown`),
      ]);

      const [ov, sb, tl, tg, cm, ug, vl, at, ub] = await Promise.all([
        ovRes.ok ? ovRes.json() : null,
        sbRes.ok ? sbRes.json() : null,
        tlRes.ok ? tlRes.json() : null,
        tgRes.ok ? tgRes.json() : null,
        cmRes.ok ? cmRes.json() : null,
        ugRes.ok ? ugRes.json() : null,
        vlRes.ok ? vlRes.json() : null,
        atRes.ok ? atRes.json() : null,
        ubRes.ok ? ubRes.json() : null,
      ]);

      setOverview(ov);
      setStatusBreakdown(sb);
      setTimeline(tl);
      setTags(tg);
      setCommittees(cm);
      setUserGrowth(ug);
      setVelocity(vl);
      setActivityTrend(at);
      setUserBreakdown(ub);
      setLastUpdated(new Date());
    } catch (e: any) {
      setError(e?.message ?? "Failed to load stats. Is the API running?");
    } finally {
      setLoading(false);
    }
  }, [timelineGranularity]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // ── Overview KPIs ────────────────────────────────────────────────────────────

  const overviewCards = overview ? (
    <div className="ps-kpi-grid">
      <KpiCard icon="description" label="Total Petitions" value={overview.total_petitions} accent={THEME.darkBrown} />
      <KpiCard icon="local_fire_department" label="Active" value={overview.active_petitions} accent={THEME.orange} />
      <KpiCard icon="check_circle" label="Responded" value={overview.responded_petitions} accent={THEME.medBrown} sub={pct(overview.petitions_with_response_pct) + " response rate"} />
      <KpiCard icon="bolt" label="Charged" value={overview.charged_petitions} accent={THEME.slate} />
      <KpiCard icon="draw" label="Total Signatures" value={overview.total_signatures} accent={THEME.darkBrown} />
      <KpiCard icon="group" label="Total Users" value={overview.total_users} accent={THEME.orange} />
      <KpiCard icon="corporate_fare" label="Committees" value={overview.total_committees} accent={THEME.medBrown} />
      <KpiCard icon="label" label="Tags" value={overview.total_tags} accent={THEME.slate} />
    </div>
  ) : null;

  // ── Status Breakdown ─────────────────────────────────────────────────────────

  const statusData = statusBreakdown?.breakdown.map((s) => ({
    name: s.status,
    count: s.count,
    pct: s.percentage,
  })) ?? [];

  // ── Timeline ─────────────────────────────────────────────────────────────────

  const timelineData = (timeline?.data ?? []).map((p) => ({
    ...p,
    period: shortPeriod(p.period),
  }));

  // ── Tag Popularity ───────────────────────────────────────────────────────────

  const tagData = (tags?.breakdown ?? []).map((t) => ({
    name: t.tag_name.length > 16 ? t.tag_name.slice(0, 14) + "…" : t.tag_name,
    count: t.petition_count,
  }));

  // ── User Growth ──────────────────────────────────────────────────────────────

  const growthData = (userGrowth?.data ?? []).map((p) => ({
    ...p,
    period: shortPeriod(p.period),
  }));

  // ── Committee Performance ────────────────────────────────────────────────────

  const committeeData = (committees?.committees ?? [])
    .sort((a, b) => b.petitions_assigned - a.petitions_assigned)
    .slice(0, 8)
    .map((c) => ({
      name: c.committee_name.length > 20 ? c.committee_name.slice(0, 18) + "…" : c.committee_name,
      assigned: c.petitions_assigned,
      responded: c.petitions_responded,
      pending: c.pending_count,
      rate: Math.round(c.response_rate_pct),
      avgDays: c.avg_response_days?.toFixed(1) ?? "—",
    }));

  // ── Signature Velocity ───────────────────────────────────────────────────────

  const velocityData = (velocity?.petitions ?? []).map((p) => ({
    name: p.petition_title.length > 22 ? p.petition_title.slice(0, 20) + "…" : p.petition_title,
    signatures: p.total_signatures,
    peak: p.peak_daily_signatures ?? 0,
  }));

  // ── Activity Trend ────────────────────────────────────────────────────────────

  // Show last 30 days; shorten date labels to "Mar 15" style
  const activityData = (activityTrend?.data ?? []).slice(-30).map((p) => {
    const [, mo, dy] = p.date.split("-");
    const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    return {
      date: `${monthNames[parseInt(mo, 10) - 1]} ${parseInt(dy, 10)}`,
      requests: p.total_requests,
      users: p.total_unique_users,
    };
  });

  // ── User Breakdown ────────────────────────────────────────────────────────────

  // Normalize account type casing and merge duplicates (e.g. "student" + "Student")
  const accountTypeData: { name: string; value: number }[] = [];
  (userBreakdown?.by_account_type ?? []).forEach((item) => {
    const key = item.account_type
      ? item.account_type.charAt(0).toUpperCase() + item.account_type.slice(1).toLowerCase()
      : "Unknown";
    const existing = accountTypeData.find((x) => x.name === key);
    if (existing) existing.value += item.user_count;
    else accountTypeData.push({ name: key, value: item.user_count });
  });
  accountTypeData.sort((a, b) => b.value - a.value);

  // Top 8 colleges + "Other" bucket; null → "Unknown"
  const allColleges = (userBreakdown?.by_college ?? []).map((c) => ({
    name: c.college ?? "Unknown",
    value: c.user_count,
  }));
  const topColleges = allColleges.slice(0, 8);
  const otherCount = allColleges.slice(8).reduce((s, c) => s + c.value, 0);
  if (otherCount > 0) topColleges.push({ name: "Other", value: otherCount });

  const ACCOUNT_COLORS = [THEME.darkBrown, THEME.medBrown, THEME.orange, THEME.slate, THEME.slateDim, THEME.lightBrown];

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="ps-root">
      {/* Header */}
      <div className="ps-header">
        <div>
          <h1 className="ps-main-title">Pawstats</h1>
          <p className="ps-main-sub">Platform analytics — real-time overview of petitions, users & engagement</p>
        </div>
        <div className="ps-header-actions">
          {lastUpdated && (
            <span className="ps-last-updated">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            className="ps-refresh-btn"
            onClick={() => fetchAll()}
            disabled={loading}
          >
            <span className={`material-symbols-outlined ${loading ? "ps-spin" : ""}`}>
              {loading ? "progress_activity" : "refresh"}
            </span>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="ps-error">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* ── KPI Grid ── */}
      <section className="ps-section">
        <SectionTitle icon="bar_chart" title="Platform Overview" desc="Headline numbers across the platform" />
        {loading ? <LoadingBar /> : overviewCards}
      </section>

      {/* ── Petition Activity & Status ── */}
      <section className="ps-section">
        <SectionTitle icon="article" title="Petition Activity" desc="Lifecycle and status distribution" />
        <div className="ps-timeline-controls">
          {(["daily", "weekly", "monthly"] as const).map((g) => (
            <button
              key={g}
              className={`ps-gran-btn ${timelineGranularity === g ? "active" : ""}`}
              onClick={() => {
                setTimelineGranularity(g);
                fetchAll(g);
              }}
            >
              {g.charAt(0).toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
        <div className="ps-charts-row">
          <ChartCard title="Creation & Response Timeline">
            {loading ? <LoadingBar /> : timelineData.length === 0 ? (
              <EmptyState message="No timeline data" />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={timelineData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                  <defs>
                    <linearGradient id="gradCreated" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={THEME.orange} stopOpacity={0.35} />
                      <stop offset="95%" stopColor={THEME.orange} stopOpacity={0.04} />
                    </linearGradient>
                    <linearGradient id="gradResponded" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={THEME.medBrown} stopOpacity={0.35} />
                      <stop offset="95%" stopColor={THEME.medBrown} stopOpacity={0.04} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} />
                  <XAxis dataKey="period" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                  <YAxis tick={{ fontSize: 11, fill: THEME.textMuted }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                  <Area type="monotone" dataKey="created" name="Created" stroke={THEME.orange} fill="url(#gradCreated)" strokeWidth={2} dot={false} />
                  <Area type="monotone" dataKey="responded" name="Responded" stroke={THEME.medBrown} fill="url(#gradResponded)" strokeWidth={2} dot={false} />
                  <Area type="monotone" dataKey="charged" name="Charged" stroke={THEME.slate} fill="none" strokeWidth={1.5} strokeDasharray="4 3" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </ChartCard>

          <ChartCard title="Status Distribution">
            {loading ? <LoadingBar /> : statusData.length === 0 ? (
              <EmptyState message="No status data" />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={95}
                    innerRadius={48}
                    paddingAngle={3}
                    label={({ name, percent }: any) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {statusData.map((entry, i) => (
                      <Cell
                        key={entry.name}
                        fill={STATUS_COLORS[entry.name] ?? BAR_COLORS[i % BAR_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(v: any, name: any) => [Number(v).toLocaleString(), name]}
                    contentStyle={{ background: "#fff", border: `1px solid ${THEME.border}`, borderRadius: 8, fontSize: 13 }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </ChartCard>
        </div>
      </section>

      {/* ── User Growth ── */}
      <section className="ps-section">
        <SectionTitle icon="group" title="User Growth" desc="New registrations over time" />
        <ChartCard title="Monthly Registrations">
          {loading ? <LoadingBar /> : growthData.length === 0 ? (
            <EmptyState message="No user growth data" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={growthData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                <defs>
                  <linearGradient id="gradNewUsers" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={THEME.darkBrown} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={THEME.darkBrown} stopOpacity={0.04} />
                  </linearGradient>
                  <linearGradient id="gradTotalUsers" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={THEME.orange} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={THEME.orange} stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} />
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <YAxis yAxisId="left" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Area yAxisId="right" type="monotone" dataKey="total_users" name="Total Users" stroke={THEME.orange} fill="url(#gradTotalUsers)" strokeWidth={1.5} dot={false} />
                <Area yAxisId="left" type="monotone" dataKey="new_users" name="New Users" stroke={THEME.darkBrown} fill="url(#gradNewUsers)" strokeWidth={2} dot={{ r: 3, fill: THEME.darkBrown }} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </section>

      {/* ── Committee Performance ── */}
      <section className="ps-section">
        <SectionTitle icon="corporate_fare" title="Committee Performance" desc="Petition assignment, response rate, and average response time" />
        <div className="ps-charts-row">
          <ChartCard title="Petitions Assigned vs Responded">
            {loading ? <LoadingBar /> : committeeData.length === 0 ? (
              <EmptyState message="No committee data" />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={committeeData} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11, fill: THEME.text }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="square" wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="assigned" name="Assigned" fill={THEME.slate} radius={[0, 3, 3, 0]} />
                  <Bar dataKey="responded" name="Responded" fill={THEME.orange} radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartCard>

          <ChartCard title="Response Rate & Avg Days">
            {loading ? <LoadingBar /> : committeeData.length === 0 ? (
              <EmptyState message="No committee data" />
            ) : (
              <div className="ps-committee-table-wrapper">
                <table className="ps-committee-table">
                  <thead>
                    <tr>
                      <th>Committee</th>
                      <th>Rate</th>
                      <th>Avg Days</th>
                      <th>Pending</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(committees?.committees ?? [])
                      .sort((a, b) => b.response_rate_pct - a.response_rate_pct)
                      .slice(0, 8)
                      .map((c) => (
                        <tr key={c.committee_id}>
                          <td className="ps-committee-name">{c.committee_name}</td>
                          <td>
                            <div className="ps-rate-bar-wrap">
                              <div
                                className="ps-rate-bar"
                                style={{ width: `${Math.min(c.response_rate_pct, 100)}%` }}
                              />
                              <span>{c.response_rate_pct.toFixed(0)}%</span>
                            </div>
                          </td>
                          <td className="ps-days">{c.avg_response_days?.toFixed(1) ?? "—"}</td>
                          <td className={`ps-pending ${c.pending_count > 0 ? "ps-pending-warn" : ""}`}>
                            {c.pending_count}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </ChartCard>
        </div>
      </section>

      {/* ── Tag Popularity ── */}
      <section className="ps-section">
        <SectionTitle icon="label" title="Tag Popularity" desc="Most-used petition tags" />
        <ChartCard title="Top Tags by Petition Count">
          {loading ? <LoadingBar /> : tagData.length === 0 ? (
            <EmptyState message="No tag data" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={tagData} margin={{ top: 8, right: 16, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: THEME.textMuted }}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Petitions" radius={[4, 4, 0, 0]}>
                  {tagData.map((_, i) => (
                    <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </section>

      {/* ── Signature Velocity ── */}
      <section className="ps-section">
        <SectionTitle icon="draw" title="Signature Velocity" desc="Top petitions by total signatures and peak daily activity" />
        <ChartCard title="Top 10 Petitions by Signatures">
          {loading ? <LoadingBar /> : velocityData.length === 0 ? (
            <EmptyState message="No signature velocity data" />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={velocityData} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11, fill: THEME.text }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="square" wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="signatures" name="Total Signatures" fill={THEME.darkBrown} radius={[0, 3, 3, 0]}>
                  {velocityData.map((_, i) => (
                    <Cell key={i} fill={i % 2 === 0 ? THEME.darkBrown : THEME.medBrown} />
                  ))}
                </Bar>
                <Bar dataKey="peak" name="Peak Daily" fill={THEME.orange} radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </section>

      {/* ── Platform Activity ── */}
      <section className="ps-section">
        <SectionTitle icon="monitoring" title="Platform Activity" desc="Daily request volume and unique active users over the last 30 days" />
        <ChartCard title="Daily Requests & Active Users">
          {loading ? <LoadingBar /> : activityData.length === 0 ? (
            <EmptyState message="No activity data" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={activityData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                <defs>
                  <linearGradient id="gradRequests" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={THEME.slate} stopOpacity={0.35} />
                    <stop offset="95%" stopColor={THEME.slate} stopOpacity={0.03} />
                  </linearGradient>
                  <linearGradient id="gradActiveUsers" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={THEME.orange} stopOpacity={0.45} />
                    <stop offset="95%" stopColor={THEME.orange} stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: THEME.textMuted }} interval={4} />
                <YAxis yAxisId="left" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Area yAxisId="left" type="monotone" dataKey="requests" name="Total Requests" stroke={THEME.slate} fill="url(#gradRequests)" strokeWidth={1.5} dot={false} />
                <Area yAxisId="right" type="monotone" dataKey="users" name="Unique Active Users" stroke={THEME.orange} fill="url(#gradActiveUsers)" strokeWidth={2} dot={{ r: 2, fill: THEME.orange }} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </section>

      {/* ── User Breakdown ── */}
      <section className="ps-section">
        <SectionTitle icon="manage_accounts" title="User Breakdown" desc="Account type distribution and college enrollment" />
        <div className="ps-charts-row">
          <ChartCard title="By Account Type">
            {loading ? <LoadingBar /> : accountTypeData.length === 0 ? (
              <EmptyState message="No breakdown data" />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={accountTypeData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    label={({ name, percent }: any) =>
                      percent > 0.04 ? `${name} ${(percent * 100).toFixed(0)}%` : ""
                    }
                    labelLine={false}
                  >
                    {accountTypeData.map((_, i) => (
                      <Cell key={i} fill={ACCOUNT_COLORS[i % ACCOUNT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: any) => v.toLocaleString()} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </ChartCard>

          <ChartCard title="By College (Top 8)">
            {loading ? <LoadingBar /> : topColleges.length === 0 ? (
              <EmptyState message="No college data" />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={topColleges} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: THEME.textMuted }} />
                  <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 11, fill: THEME.text }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" name="Users" radius={[0, 4, 4, 0]}>
                    {topColleges.map((_, i) => (
                      <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartCard>
        </div>
      </section>
    </div>
  );
}
