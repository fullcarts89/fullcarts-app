export default function Home() {
  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center px-6"
      style={{ background: "var(--bg-primary)" }}
    >
      {/* Subtle grid background */}
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(var(--text-tertiary) 1px, transparent 1px), linear-gradient(90deg, var(--text-tertiary) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <main className="relative z-10 flex max-w-2xl flex-col items-center text-center">
        {/* Logo mark */}
        <div
          className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl"
          style={{
            background: "var(--red-bg)",
            border: "1px solid var(--red-border)",
          }}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            className="h-8 w-8"
            style={{ color: "var(--red-base)" }}
          >
            <path
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {/* Wordmark */}
        <h1
          className="mb-4 text-5xl font-bold tracking-tight sm:text-6xl"
          style={{
            fontFamily: "var(--font-headline)",
            color: "var(--text-primary)",
          }}
        >
          Full
          <span style={{ color: "var(--red-base)" }}>Carts</span>
        </h1>

        {/* Tagline */}
        <p
          className="mb-2 uppercase"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-tertiary)",
            fontSize: "0.75rem",
            letterSpacing: "0.15em",
          }}
        >
          Making Shrinkflation Impossible to Hide
        </p>

        {/* Divider */}
        <div
          className="my-8 h-px w-32"
          style={{ background: "var(--bg-tertiary)" }}
        />

        {/* Description */}
        <p
          className="mb-10 max-w-md text-lg leading-relaxed"
          style={{
            fontFamily: "var(--font-sans)",
            color: "var(--text-secondary)",
          }}
        >
          We&apos;re rebuilding from the ground up. Verified evidence. Real
          product data. Brand accountability. Coming soon.
        </p>

        {/* Status badge */}
        <div
          className="inline-flex items-center gap-2 rounded-full px-4 py-2"
          style={{
            background: "var(--green-bg)",
            border: "1px solid var(--green-border)",
          }}
        >
          <span
            className="h-2 w-2 animate-pulse rounded-full"
            style={{ background: "var(--green-base)" }}
          />
          <span
            className="text-sm font-medium"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--green-base)",
            }}
          >
            In Development
          </span>
        </div>

        {/* Link to current site */}
        <a
          href="https://fullcarts.org"
          className="mt-6 text-sm transition-colors hover:opacity-80"
          style={{
            fontFamily: "var(--font-sans)",
            color: "var(--text-tertiary)",
          }}
        >
          Visit current site &rarr;
        </a>
      </main>

      {/* Footer */}
      <footer
        className="absolute bottom-6 text-xs"
        style={{
          fontFamily: "var(--font-mono)",
          color: "var(--text-tertiary)",
        }}
      >
        &copy; 2026 FullCarts
      </footer>
    </div>
  );
}
