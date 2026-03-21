type DailyCount = {
  date: string;
  total: number;
  reddit: number;
  news: number;
  gdelt: number;
};

type Props = {
  statusCounts: { pending: number; approved: number; matched: number; evidence: number; discarded: number };
  dailyCounts: DailyCount[];
  pipelineHealthy: boolean;
  lastExtractionAgo: string;
};

function StatusCard({
  label,
  count,
  colorClass,
}: {
  label: string;
  count: number;
  colorClass: string;
}) {
  return (
    <div className={`rounded-lg border px-4 py-3 ${colorClass}`}>
      <div className="text-xs font-medium uppercase tracking-wider opacity-80">
        {label}
      </div>
      <div className="text-2xl font-mono font-bold mt-1">
        {count.toLocaleString()}
      </div>
    </div>
  );
}

export function PipelineStats({
  statusCounts,
  dailyCounts,
  pipelineHealthy,
  lastExtractionAgo,
}: Props) {
  const maxTotal = Math.max(...dailyCounts.map((d) => d.total), 1);

  return (
    <div className="border-b border-[var(--bg-tertiary)] px-6 py-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-[var(--font-headline)] text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
          Pipeline Stats
        </h2>
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              pipelineHealthy ? "bg-[var(--green-base)]" : "bg-[var(--red-base)]"
            }`}
          />
          <span className={pipelineHealthy ? "text-[var(--green-base)]" : "text-[var(--red-base)]"}>
            {pipelineHealthy ? "Healthy" : "Stale"} &mdash; last extraction {lastExtractionAgo}
          </span>
        </div>
      </div>

      {/* Status summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <StatusCard
          label="Pending"
          count={statusCounts.pending}
          colorClass="bg-[var(--amber-bg)] border-[var(--amber-base)]/20 text-[var(--amber-base)]"
        />
        <StatusCard
          label="Approved"
          count={statusCounts.approved}
          colorClass="bg-[var(--green-bg)] border-[var(--green-border)] text-[var(--green-base)]"
        />
        <StatusCard
          label="Matched"
          count={statusCounts.matched}
          colorClass="bg-[var(--blue-bg)] border-[var(--blue-border)] text-[var(--blue-base)]"
        />
        <StatusCard
          label="Evidence"
          count={statusCounts.evidence}
          colorClass="bg-purple-500/10 border-purple-500/20 text-purple-400"
        />
        <StatusCard
          label="Discarded"
          count={statusCounts.discarded}
          colorClass="bg-[var(--red-bg)] border-[var(--red-border)] text-[var(--red-base)]"
        />
      </div>

      {/* Daily extraction chart */}
      {dailyCounts.length > 0 && (
        <div className="space-y-1.5">
          <h3 className="text-xs font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
            Daily Extractions (last 14 days)
          </h3>
          <div className="space-y-1">
            {dailyCounts.map((day) => {
              const widthPct = (day.total / maxTotal) * 100;
              const redditPct = day.total > 0 ? (day.reddit / day.total) * widthPct : 0;
              const newsPct = day.total > 0 ? (day.news / day.total) * widthPct : 0;
              const gdeltPct = day.total > 0 ? (day.gdelt / day.total) * widthPct : 0;

              return (
                <div key={day.date} className="flex items-center gap-3">
                  <span className="text-xs font-mono text-[var(--text-tertiary)] w-20 flex-shrink-0">
                    {day.date.slice(5)}
                  </span>
                  <div className="flex-1 h-5 flex rounded overflow-hidden bg-[var(--bg-primary)]">
                    {day.reddit > 0 && (
                      <div
                        className="bg-orange-500/70 h-full"
                        style={{ width: `${redditPct}%` }}
                        title={`Reddit: ${day.reddit}`}
                      />
                    )}
                    {day.news > 0 && (
                      <div
                        className="bg-blue-500/70 h-full"
                        style={{ width: `${newsPct}%` }}
                        title={`News: ${day.news}`}
                      />
                    )}
                    {day.gdelt > 0 && (
                      <div
                        className="bg-purple-500/70 h-full"
                        style={{ width: `${gdeltPct}%` }}
                        title={`GDELT: ${day.gdelt}`}
                      />
                    )}
                  </div>
                  <span className="text-xs font-mono text-[var(--text-secondary)] w-10 text-right flex-shrink-0">
                    {day.total}
                  </span>
                </div>
              );
            })}
          </div>
          {/* Legend */}
          <div className="flex gap-4 text-xs text-[var(--text-tertiary)] pt-1">
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-2 rounded-sm bg-orange-500/70" /> Reddit
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-2 rounded-sm bg-blue-500/70" /> News
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-2 rounded-sm bg-purple-500/70" /> GDELT
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
