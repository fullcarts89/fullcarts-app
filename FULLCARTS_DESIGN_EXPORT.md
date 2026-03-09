# FullCarts - Complete Design System & Component Library

## Platform Overview

**Name:** FullCarts  
**Mission:** Making Shrinkflation Impossible to Hide  
**Type:** Shrinkflation Intelligence Platform  
**Aesthetic:** Investigative Journalism meets Modern Product Design  
**Target Audience:** Consumers seeking transparency in product sizing changes

---

## Visual Design Language

### Core Design Philosophy
- **Evidence-Driven:** Every visual element reinforces data credibility
- **High-Contrast:** Dark UI with strategic accent colors for maximum impact
- **Investigative Credibility:** Professional, serious, journalism-grade aesthetic
- **Consumer-First:** Built for shoppers, not shareholders
- **Transparency:** All data sources visible and verifiable

### Mood & Tone
- Bold but not aggressive
- Serious but accessible
- Data-focused but human
- Investigative but not conspiratorial
- Empowering but not alarmist

---

## Color System

### Foundation Colors

#### Background Palette
```css
--bg-primary: #0a0b0d        /* Deep graphite - main canvas */
--bg-secondary: #161719      /* Card backgrounds, elevated surfaces */
--bg-tertiary: #2a2b2d       /* Interactive elements, hover states */
--bg-hover: #1a1b1d          /* Card hover state */
```

#### Text Palette
```css
--text-primary: #f5f4f0      /* Cream - headlines, primary content */
--text-secondary: #a0a0a5    /* Gray - descriptions, metadata, labels */
--text-tertiary: #656569     /* Dark gray - disabled, de-emphasized */
```

### Semantic Color System

#### Alert Red (Shrinkflation Indicator)
**Usage:** Shrinkflation events, offenders, negative changes, urgent CTAs, active states
```css
--red-base: #dc2626
--red-hover: #ef4444
--red-bg: rgba(220, 38, 38, 0.1)
--red-border: rgba(220, 38, 38, 0.2)
```

**Application Examples:**
- Shrinkflation badges
- Negative trend indicators
- Size reduction metrics
- Offender status labels
- Primary action buttons
- Active filter states
- Card title hover states

#### Signal Green (Transparency Indicator)
**Usage:** Good actors, verified data, positive changes, approvals
```css
--green-base: #10b981
--green-hover: #059669
--green-bg: rgba(16, 185, 129, 0.1)
--green-border: rgba(16, 185, 129, 0.2)
```

**Application Examples:**
- Good actor badges
- Verified checkmarks
- Acceptance indicators
- High confidence ratings
- Positive change metrics

#### Data Blue (Neutral Information)
**Usage:** Neutral data, methodology, informational elements
```css
--blue-base: #3b82f6
--blue-hover: #2563eb
--blue-bg: rgba(59, 130, 246, 0.1)
--blue-border: rgba(59, 130, 246, 0.2)
```

**Application Examples:**
- Neutral metrics
- Data visualization
- Methodology steps
- Informational badges
- Medium confidence ratings

#### Amber (Warning/Review)
**Usage:** Under review, warnings, pending states
```css
--amber-base: #f59e0b
--amber-hover: #d97706
--amber-bg: rgba(245, 158, 11, 0.1)
--amber-border: rgba(245, 158, 11, 0.2)
```

**Application Examples:**
- Under review status
- Low confidence ratings
- Warning sections
- Correction policies

### Border & Divider System
```css
--border-subtle: rgba(255, 255, 255, 0.1)   /* Default borders */
--border-medium: rgba(255, 255, 255, 0.2)   /* Hover borders */
--border-strong: rgba(255, 255, 255, 0.3)   /* Active borders */
```

---

## Typography System

### Font Stack

#### Display & Headlines
```css
font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif;
font-weight: 700;
letter-spacing: -0.025em;
```

**Characteristics:**
- Geometric, modern sans-serif
- Excellent readability at large sizes
- Professional, authoritative feel
- Use for: Headlines, navigation, buttons, emphasis

#### Body Copy
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
font-weight: 400 | 500;
letter-spacing: normal;
```

**Characteristics:**
- Optimized for screen reading
- Clean, neutral, highly legible
- Excellent at small sizes
- Use for: Paragraphs, descriptions, UI text

#### Data & Monospace
```css
font-family: 'JetBrains Mono', 'Courier New', monospace;
font-weight: 500 | 700;
letter-spacing: normal;
```

**Characteristics:**
- Fixed-width for data alignment
- Technical, precise appearance
- Use for: Metrics, percentages, dates, labels, badges

### Type Scale

#### Headlines (Space Grotesk)
```tsx
/* Hero Headline */
className="font-headline text-5xl sm:text-6xl lg:text-7xl font-bold"
// 48px → 60px → 72px

/* Page Title */
className="font-headline text-4xl sm:text-5xl font-bold"
// 36px → 48px

/* Section Heading */
className="font-headline text-3xl sm:text-4xl font-bold"
// 30px → 36px

/* Subsection Heading */
className="font-headline text-2xl sm:text-3xl font-bold"
// 24px → 30px

/* Card Title */
className="font-headline text-xl font-bold"
// 20px

/* Small Headline */
className="font-headline text-lg font-bold"
// 18px
```

#### Body Text (Inter)
```tsx
/* Large Body */
className="text-xl"
// 20px - intros, feature text

/* Base Body */
className="text-base"
// 16px - standard paragraphs

/* Small Body */
className="text-sm"
// 14px - captions, helper text

/* Tiny Text */
className="text-xs"
// 12px - labels, timestamps
```

#### Data Text (JetBrains Mono)
```tsx
/* Hero Metric */
className="font-mono text-5xl font-bold"
// 48px - homepage stats

/* Large Metric */
className="font-mono text-4xl font-bold"
// 36px - dashboard cards

/* Medium Metric */
className="font-mono text-2xl font-bold"
// 24px - inline stats

/* Small Metric */
className="font-mono text-xl font-bold"
// 20px - compact displays

/* Label */
className="font-mono text-sm font-medium uppercase"
// 14px - data labels

/* Badge */
className="font-mono text-xs font-medium uppercase"
// 12px - status badges
```

### Text Color Application
```tsx
/* Primary text - headlines, important content */
text-[#f5f4f0]

/* Secondary text - descriptions, body copy */
text-[#a0a0a5]

/* Alert text - shrinkflation indicators */
text-[#dc2626]

/* Success text - good actors */
text-[#10b981]

/* Info text - neutral data */
text-[#3b82f6]

/* Warning text - under review */
text-[#f59e0b]
```

---

## Spacing & Layout System

### Container Widths
```tsx
/* Standard content container */
className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
// max-width: 1280px with responsive padding

/* Narrow content (articles, forms) */
className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8"
// max-width: 896px

/* Extra narrow (newsletter signup) */
className="mx-auto max-w-2xl px-4 sm:px-6"
// max-width: 672px
```

### Vertical Spacing
```tsx
/* Section spacing */
className="py-24"           // 96px - between major sections
className="py-16"           // 64px - between subsections
className="py-12"           // 48px - content groups

/* Component spacing */
className="mb-16"           // 64px - large gap
className="mb-12"           // 48px - medium gap
className="mb-8"            // 32px - standard gap
className="mb-6"            // 24px - small gap
className="mb-4"            // 16px - tight gap
className="mb-2"            // 8px - minimal gap

/* Stack spacing */
className="space-y-8"       // 32px between children
className="space-y-6"       // 24px between children
className="space-y-4"       // 16px between children
className="space-y-3"       // 12px between children
```

### Grid Systems
```tsx
/* Responsive 2-column */
className="grid gap-6 md:grid-cols-2"

/* Responsive 3-column */
className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"

/* Responsive 4-column (metrics) */
className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4"

/* Auto-fit cards */
className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(300px,1fr))]"

/* Masonry layout (Evidence Wall) */
<ResponsiveMasonry columnsCountBreakPoints={{ 350: 1, 750: 2, 1024: 3 }}>
  <Masonry gutter="24px">
    {/* Cards */}
  </Masonry>
</ResponsiveMasonry>
```

### Responsive Breakpoints
```tsx
sm: 640px   // Small tablets
md: 768px   // Tablets
lg: 1024px  // Small laptops
xl: 1280px  // Desktops
2xl: 1536px // Large screens
```

---

## Component Library

### 1. Buttons

#### Primary CTA
```tsx
<button className="rounded-lg bg-[#dc2626] px-8 py-4 font-headline text-lg font-bold text-[#f5f4f0] transition-all hover:bg-[#ef4444] focus:outline-none focus:ring-2 focus:ring-[#dc2626]/50">
  Get Started
</button>
```

#### Secondary Button
```tsx
<button className="rounded-lg border border-white/20 bg-transparent px-8 py-4 font-headline text-lg font-bold text-[#f5f4f0] transition-all hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-white/20">
  Learn More
</button>
```

#### Small Primary
```tsx
<button className="rounded-lg bg-[#dc2626] px-4 py-2 text-sm font-medium text-[#f5f4f0] transition-all hover:bg-[#ef4444]">
  View Details
</button>
```

#### Text Link Button
```tsx
<button className="font-medium text-[#dc2626] transition-colors hover:text-[#ef4444]">
  View All →
</button>
```

#### Filter Button (Inactive)
```tsx
<button className="rounded-lg bg-[#2a2b2d] px-4 py-2 text-sm font-medium text-[#f5f4f0] transition-colors hover:bg-[#3a3b3d]">
  All Categories
</button>
```

#### Filter Button (Active)
```tsx
<button className="rounded-lg bg-[#dc2626] px-4 py-2 text-sm font-medium text-[#f5f4f0]">
  Snacks
</button>
```

### 2. Cards

#### Standard Card
```tsx
<div className="rounded-xl border border-white/10 bg-[#161719] p-6 transition-all hover:border-white/20 hover:bg-[#1a1b1d]">
  {/* Content */}
</div>
```

#### Stat Card
```tsx
<div className="rounded-xl border border-white/10 bg-[#161719] p-6">
  <div className="mb-2 flex items-center gap-2">
    <TrendingDown className="h-5 w-5 text-[#dc2626]" />
    <span className="text-xs font-medium uppercase tracking-wide text-[#a0a0a5]">
      Shrink Events
    </span>
  </div>
  <div className="font-mono text-4xl font-bold text-[#dc2626]">186</div>
  <div className="mt-2 text-sm text-[#a0a0a5]">Last 30 days</div>
</div>
```

#### Gradient Card
```tsx
<div className="rounded-xl border border-white/10 bg-gradient-to-br from-[#161719] to-[#0a0b0d] p-8">
  {/* Content */}
</div>
```

#### Alert Card (Red)
```tsx
<div className="rounded-2xl border border-[#dc2626]/20 bg-gradient-to-br from-[#dc2626]/10 to-transparent p-8">
  {/* Content */}
</div>
```

#### Info Card (Blue)
```tsx
<div className="rounded-xl border border-[#3b82f6]/20 bg-[#3b82f6]/5 p-6">
  {/* Content */}
</div>
```

#### Success Card (Green)
```tsx
<div className="rounded-xl border border-[#10b981]/20 bg-[#10b981]/5 p-6">
  {/* Content */}
</div>
```

#### Warning Card (Amber)
```tsx
<div className="rounded-xl border border-[#f59e0b]/20 bg-[#f59e0b]/5 p-6">
  {/* Content */}
</div>
```

### 3. Badges & Labels

#### Offender Badge
```tsx
<span className="flex items-center gap-1 rounded-full bg-[#dc2626]/20 px-2 py-1">
  <AlertCircle className="h-3 w-3 text-[#dc2626]" />
  <span className="text-xs font-medium text-[#dc2626]">Offender</span>
</span>
```

#### Good Actor Badge
```tsx
<span className="flex items-center gap-1 rounded-full bg-[#10b981]/20 px-2 py-1">
  <CheckCircle className="h-3 w-3 text-[#10b981]" />
  <span className="text-xs font-medium text-[#10b981]">Good Actor</span>
</span>
```

#### Status Badge (Verified)
```tsx
<span className="rounded bg-[#dc2626]/20 px-2 py-1 font-mono text-xs font-medium uppercase text-[#dc2626]">
  Verified
</span>
```

#### Category Label
```tsx
<span className="rounded bg-[#dc2626]/20 px-3 py-1 font-mono text-xs font-medium uppercase text-[#dc2626]">
  Snacks
</span>
```

#### Severity Badge (High)
```tsx
<span className="rounded-lg bg-[#dc2626]/20 px-2 py-1 font-mono text-xs font-medium uppercase text-[#dc2626]">
  High
</span>
```

#### Severity Badge (Medium)
```tsx
<span className="rounded-lg bg-[#f59e0b]/20 px-2 py-1 font-mono text-xs font-medium uppercase text-[#f59e0b]">
  Medium
</span>
```

#### Severity Badge (Low)
```tsx
<span className="rounded-lg bg-[#3b82f6]/20 px-2 py-1 font-mono text-xs font-medium uppercase text-[#3b82f6]">
  Low
</span>
```

### 4. Icons & Icon Containers

#### Icon Library
**Package:** lucide-react

**Commonly Used Icons:**
- `TrendingDown` - Size reductions, negative changes
- `TrendingUp` - Price increases, positive metrics
- `AlertCircle` - Warnings, offender status
- `CheckCircle` - Verification, good actors
- `Package` - Products
- `Search` - Discovery, methodology
- `Database` - Data sources
- `Users` - Community, human review
- `FileCheck` - Verification
- `AlertTriangle` - Important notices
- `Shield` - Trust, methodology
- `Target` - Mission, goals
- `Zap` - Speed, innovation
- `ExternalLink` - External links
- `Bell` - Notifications
- `Menu` - Mobile navigation

#### Small Icon Container
```tsx
<div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#dc2626]/20">
  <AlertCircle className="h-4 w-4 text-[#dc2626]" />
</div>
```

#### Medium Icon Container
```tsx
<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#dc2626]/20">
  <TrendingDown className="h-6 w-6 text-[#dc2626]" />
</div>
```

#### Large Icon Container
```tsx
<div className="flex h-16 w-16 items-center justify-center rounded-lg bg-[#dc2626]/20">
  <Package className="h-8 w-8 text-[#dc2626]" />
</div>
```

### 5. Form Elements

#### Text Input
```tsx
<input
  type="text"
  className="w-full rounded-lg border border-white/20 bg-[#161719] px-6 py-4 text-[#f5f4f0] placeholder-[#a0a0a5] transition-all focus:border-[#dc2626] focus:outline-none focus:ring-2 focus:ring-[#dc2626]/50"
  placeholder="Enter text..."
/>
```

#### Email Input
```tsx
<input
  type="email"
  className="w-full rounded-lg border border-white/20 bg-[#161719] px-6 py-4 text-[#f5f4f0] placeholder-[#a0a0a5] transition-all focus:border-[#dc2626] focus:outline-none focus:ring-2 focus:ring-[#dc2626]/50"
  placeholder="your.email@example.com"
/>
```

#### Label
```tsx
<label className="mb-2 block text-sm font-medium text-[#f5f4f0]">
  Email Address
</label>
```

#### Helper Text
```tsx
<p className="mt-2 text-sm text-[#a0a0a5]">
  We'll never share your email with anyone else.
</p>
```

#### Error Message
```tsx
<p className="mt-2 text-sm text-[#dc2626]">
  Please enter a valid email address.
</p>
```

### 6. Navigation Components

#### Logo
```tsx
<div className="flex items-center gap-2">
  <div className="flex h-8 w-8 items-center justify-center rounded bg-[#dc2626]">
    <span className="font-mono text-sm font-bold text-[#f5f4f0]">FC</span>
  </div>
  <span className="font-headline text-xl font-bold tracking-tight text-[#f5f4f0]">
    FullCarts
  </span>
</div>
```

#### Navigation Bar
```tsx
<nav className="fixed left-0 right-0 top-0 z-50 border-b border-white/10 bg-[#0a0b0d]/95 backdrop-blur-sm">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="flex h-16 items-center justify-between">
      {/* Logo */}
      {/* Nav Links */}
      {/* CTA */}
    </div>
  </div>
</nav>
```

#### Nav Link (Active)
```tsx
<Link
  to="/dashboard"
  className="font-medium text-[#f5f4f0] transition-colors hover:text-[#dc2626]"
>
  Dashboard
</Link>
```

#### Nav Link (Inactive)
```tsx
<Link
  to="/about"
  className="font-medium text-[#a0a0a5] transition-colors hover:text-[#f5f4f0]"
>
  About
</Link>
```

### 7. Metric Display Components

#### Large Counter with Animation
```tsx
<div className="text-center">
  <div className="font-mono text-5xl font-bold text-[#dc2626] sm:text-6xl">
    <CounterAnimation value={1247} />+
  </div>
  <div className="mt-2 text-sm font-medium uppercase tracking-wide text-[#a0a0a5]">
    Products Tracked
  </div>
</div>
```

#### Change Percentage (Negative)
```tsx
<div className="flex items-center gap-2">
  <TrendingDown className="h-5 w-5 text-[#dc2626]" />
  <span className="font-mono text-2xl font-bold text-[#dc2626]">-15%</span>
</div>
```

#### Change Percentage (Positive)
```tsx
<div className="flex items-center gap-2">
  <TrendingUp className="h-5 w-5 text-[#10b981]" />
  <span className="font-mono text-2xl font-bold text-[#10b981]">+8%</span>
</div>
```

#### Confidence Rating Display
```tsx
<div className="flex items-center justify-between">
  <div>
    <h3 className="font-headline text-lg font-bold text-[#10b981]">
      High Confidence
    </h3>
    <p className="mt-1 text-sm text-[#a0a0a5]">
      Multiple verified sources
    </p>
  </div>
  <div className="font-mono text-2xl font-bold text-[#10b981]">95%+</div>
</div>
```

### 8. Product Card Component

```tsx
<div className="group overflow-hidden rounded-xl border border-white/10 bg-[#161719] transition-all hover:border-white/20 hover:bg-[#1a1b1d]">
  {/* Header */}
  <div className="p-6">
    <div className="mb-2 flex items-center justify-between">
      <span className="font-mono text-xs font-medium uppercase text-[#a0a0a5]">
        Snacks
      </span>
      <span className="flex items-center gap-1 rounded-full bg-[#dc2626]/20 px-2 py-1">
        <AlertCircle className="h-3 w-3 text-[#dc2626]" />
        <span className="text-xs font-medium text-[#dc2626]">Offender</span>
      </span>
    </div>
    
    <h3 className="mb-2 font-headline text-xl font-bold text-[#f5f4f0]">
      Doritos Cool Ranch
    </h3>
    
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <TrendingDown className="h-5 w-5 text-[#dc2626]" />
        <span className="font-mono text-lg font-bold text-[#dc2626]">-15%</span>
      </div>
      <span className="text-sm text-[#a0a0a5]">9.75oz → 8.5oz</span>
    </div>
    
    <div className="mt-3 text-sm text-[#a0a0a5]">
      <span className="font-mono">$0.47/oz</span> current price per unit
    </div>
  </div>
  
  {/* Sparkline Chart */}
  <div className="h-16 border-t border-white/10 bg-[#0a0b0d]/50 px-6 py-2">
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={sparklineData}>
        <Line
          type="monotone"
          dataKey="size"
          stroke="#dc2626"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
</div>
```

### 9. Before/After Comparison Component

```tsx
<div className="grid gap-8 md:grid-cols-2">
  {/* Before */}
  <div className="rounded-xl border border-white/10 bg-[#161719] p-6">
    <div className="mb-4 flex items-center justify-between">
      <h3 className="font-headline text-xl font-bold text-[#f5f4f0]">Before</h3>
      <span className="font-mono text-sm text-[#a0a0a5]">March 2023</span>
    </div>
    
    <div className="mb-4 aspect-square rounded-lg bg-[#2a2b2d]">
      {/* Product image */}
    </div>
    
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Size</span>
        <span className="font-mono font-medium text-[#f5f4f0]">9.75 oz</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Price</span>
        <span className="font-mono font-medium text-[#f5f4f0]">$3.99</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Price/oz</span>
        <span className="font-mono font-medium text-[#f5f4f0]">$0.41</span>
      </div>
    </div>
  </div>
  
  {/* After */}
  <div className="rounded-xl border border-[#dc2626]/20 bg-[#161719] p-6">
    <div className="mb-4 flex items-center justify-between">
      <h3 className="font-headline text-xl font-bold text-[#f5f4f0]">After</h3>
      <span className="font-mono text-sm text-[#a0a0a5]">Oct 2024</span>
    </div>
    
    <div className="mb-4 aspect-square rounded-lg bg-[#2a2b2d]">
      {/* Product image */}
      <div className="absolute right-2 top-2">
        <span className="rounded bg-[#dc2626] px-2 py-1 font-mono text-xs font-bold text-[#f5f4f0]">
          -15%
        </span>
      </div>
    </div>
    
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Size</span>
        <span className="font-mono font-medium text-[#dc2626]">8.5 oz</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Price</span>
        <span className="font-mono font-medium text-[#dc2626]">$3.99</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-[#a0a0a5]">Price/oz</span>
        <span className="font-mono font-medium text-[#dc2626]">$0.47</span>
      </div>
    </div>
  </div>
</div>
```

### 10. Footer Component

```tsx
<footer className="border-t border-white/10 bg-[#0a0b0d] py-12">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="grid gap-8 md:grid-cols-4">
      {/* Column 1: Brand */}
      <div>
        {/* Logo */}
        <p className="mt-4 text-sm text-[#a0a0a5]">
          Making shrinkflation impossible to hide.
        </p>
      </div>
      
      {/* Column 2: Navigate */}
      <div>
        <h4 className="mb-4 font-headline text-sm font-bold uppercase tracking-wide text-[#f5f4f0]">
          Navigate
        </h4>
        <ul className="space-y-2">
          <li>
            <Link to="/" className="text-sm text-[#a0a0a5] transition-colors hover:text-[#f5f4f0]">
              Home
            </Link>
          </li>
          {/* More links */}
        </ul>
      </div>
      
      {/* Column 3: Resources */}
      <div>
        <h4 className="mb-4 font-headline text-sm font-bold uppercase tracking-wide text-[#f5f4f0]">
          Resources
        </h4>
        <ul className="space-y-2">
          <li>
            <Link to="/methodology" className="text-sm text-[#a0a0a5] transition-colors hover:text-[#f5f4f0]">
              Methodology
            </Link>
          </li>
          {/* More links */}
        </ul>
      </div>
      
      {/* Column 4: Community */}
      <div>
        <h4 className="mb-4 font-headline text-sm font-bold uppercase tracking-wide text-[#f5f4f0]">
          Community
        </h4>
        <ul className="space-y-2">
          <li>
            <Link to="/join" className="text-sm text-[#a0a0a5] transition-colors hover:text-[#f5f4f0]">
              Join Us
            </Link>
          </li>
          {/* More links */}
        </ul>
      </div>
    </div>
    
    <div className="mt-12 border-t border-white/10 pt-8 text-center text-sm text-[#a0a0a5]">
      © 2024 FullCarts. Built for shoppers, not shareholders.
    </div>
  </div>
</footer>
```

---

## Data Visualization Components

### Chart Library
**Package:** recharts

### Chart Configuration

#### Line Chart (Trend Over Time)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
    <XAxis
      dataKey="date"
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <YAxis
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <Tooltip
      contentStyle={{
        backgroundColor: "#161719",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: "8px",
        color: "#f5f4f0",
      }}
    />
    <Line
      type="monotone"
      dataKey="shrinkEvents"
      stroke="#dc2626"
      strokeWidth={2}
      name="Shrink Events"
    />
  </LineChart>
</ResponsiveContainer>
```

#### Bar Chart (Category Distribution)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
    <XAxis
      dataKey="category"
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <YAxis
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <Tooltip
      contentStyle={{
        backgroundColor: "#161719",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: "8px",
        color: "#f5f4f0",
      }}
    />
    <Bar dataKey="count" fill="#dc2626" />
  </BarChart>
</ResponsiveContainer>
```

#### Sparkline (Product Card)
```tsx
<ResponsiveContainer width="100%" height={60}>
  <LineChart data={data}>
    <Line
      type="monotone"
      dataKey="size"
      stroke="#dc2626"
      strokeWidth={2}
      dot={false}
    />
  </LineChart>
</ResponsiveContainer>
```

#### Area Chart (Volume Over Time)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <AreaChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
    <XAxis
      dataKey="month"
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <YAxis
      stroke="#a0a0a5"
      tick={{ fill: "#a0a0a5", fontSize: 12 }}
    />
    <Tooltip
      contentStyle={{
        backgroundColor: "#161719",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: "8px",
        color: "#f5f4f0",
      }}
    />
    <Area
      type="monotone"
      dataKey="value"
      stroke="#dc2626"
      fill="rgba(220, 38, 38, 0.1)"
    />
  </AreaChart>
</ResponsiveContainer>
```

### Chart Color Palette
```tsx
/* Negative/Shrinkflation */
stroke="#dc2626"
fill="#dc2626"
fill="rgba(220, 38, 38, 0.1)"  /* For area charts */

/* Positive/Growth */
stroke="#10b981"
fill="#10b981"
fill="rgba(16, 185, 129, 0.1)"

/* Neutral/Data */
stroke="#3b82f6"
fill="#3b82f6"
fill="rgba(59, 130, 246, 0.1)"

/* Warning */
stroke="#f59e0b"
fill="#f59e0b"
fill="rgba(245, 158, 11, 0.1)"

/* Grid & Axis */
stroke="rgba(255,255,255,0.1)"  /* Grid lines */
stroke="#a0a0a5"                /* Axis lines */
fill="#a0a0a5"                  /* Axis labels */
```

---

## Animation System

### Animation Library
**Package:** motion (from "motion/react")

**Import:**
```tsx
import { motion, AnimatePresence } from "motion/react"
```

### Entrance Animations

#### Fade Up
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8 }}
>
  {/* Content */}
</motion.div>
```

#### Fade Scale
```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.9 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.8, delay: 0.2 }}
>
  {/* Content */}
</motion.div>
```

#### Stagger Children
```tsx
<motion.div
  initial="hidden"
  animate="visible"
  variants={{
    visible: { transition: { staggerChildren: 0.1 } }
  }}
>
  <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}>
    {/* Child 1 */}
  </motion.div>
  <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}>
    {/* Child 2 */}
  </motion.div>
</motion.div>
```

#### Mobile Menu Slide Down
```tsx
<AnimatePresence>
  {mobileMenuOpen && (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Menu content */}
    </motion.div>
  )}
</AnimatePresence>
```

#### Modal Fade In
```tsx
<AnimatePresence>
  {isOpen && (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm"
      />
      
      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className="fixed inset-0 flex items-center justify-center p-4"
      >
        {/* Modal content */}
      </motion.div>
    </>
  )}
</AnimatePresence>
```

### Counter Animation Component

```tsx
import { useEffect, useState } from "react";

interface CounterAnimationProps {
  value: number;
  duration?: number;
}

export function CounterAnimation({ value, duration = 2000 }: CounterAnimationProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * value));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);

  return <>{count.toLocaleString()}</>;
}
```

### CSS Transitions

#### Standard Transition
```tsx
className="transition-all duration-200"
```

#### Color Transition
```tsx
className="transition-colors duration-200"
```

#### Opacity Transition
```tsx
className="transition-opacity duration-300"
```

#### Transform Transition
```tsx
className="transition-transform duration-200"
```

#### Group Hover Effects
```tsx
<div className="group">
  <h3 className="text-[#f5f4f0] transition-colors group-hover:text-[#dc2626]">
    Title
  </h3>
  <div className="opacity-0 transition-opacity group-hover:opacity-100">
    Revealed content
  </div>
</div>
```

---

## Background Patterns & Textures

### Grid Pattern (Hero Sections)
```tsx
<div className="absolute inset-0 overflow-hidden opacity-10">
  <div
    className="absolute inset-0"
    style={{
      backgroundImage: `
        repeating-linear-gradient(
          0deg,
          rgba(245,244,240,0.05) 0px,
          transparent 1px,
          transparent 2px,
          rgba(245,244,240,0.05) 3px
        ),
        repeating-linear-gradient(
          90deg,
          rgba(245,244,240,0.05) 0px,
          transparent 1px,
          transparent 2px,
          rgba(245,244,240,0.05) 3px
        )
      `,
    }}
  />
</div>
```

### Gradient Overlays

#### Card Gradient (Subtle Depth)
```tsx
className="bg-gradient-to-br from-[#161719] to-[#0a0b0d]"
```

#### Alert Gradient (Red)
```tsx
className="bg-gradient-to-br from-[#dc2626]/10 to-transparent"
```

#### Hero Gradient (Vignette)
```tsx
className="bg-gradient-to-t from-[#0a0b0d] via-transparent to-transparent"
```

#### Image Overlay (Darken)
```tsx
className="absolute inset-0 bg-gradient-to-t from-[#0a0b0d] to-transparent opacity-60"
```

---

## Interactive State Patterns

### Hover States

#### Button Hover
```tsx
/* Red button */
hover:bg-[#ef4444]

/* Outline button */
hover:bg-white/5

/* Text link */
hover:text-[#ef4444]

/* Secondary link */
hover:text-[#f5f4f0]
```

#### Card Hover
```tsx
hover:border-white/20
hover:bg-[#1a1b1d]
```

#### Icon Hover
```tsx
hover:scale-110
transition-transform
```

### Focus States

#### Input Focus
```tsx
focus:border-[#dc2626]
focus:outline-none
focus:ring-2
focus:ring-[#dc2626]/50
```

#### Button Focus
```tsx
focus:outline-none
focus:ring-2
focus:ring-[#dc2626]/50
focus:ring-offset-2
focus:ring-offset-[#0a0b0d]
```

### Active States

#### Active Navigation Link
```tsx
className="text-[#f5f4f0]"  /* Active */
className="text-[#a0a0a5]"  /* Inactive */
```

#### Active Filter
```tsx
className="bg-[#dc2626] text-[#f5f4f0]"              /* Active */
className="bg-[#2a2b2d] text-[#f5f4f0] hover:bg-[#3a3b3d]"  /* Inactive */
```

#### Active Tab
```tsx
className="border-b-2 border-[#dc2626] text-[#f5f4f0]"  /* Active */
className="border-b-2 border-transparent text-[#a0a0a5]"  /* Inactive */
```

### Disabled States
```tsx
disabled:opacity-50
disabled:cursor-not-allowed
disabled:hover:bg-[#dc2626]  /* Prevent hover effect */
```

---

## Responsive Design Patterns

### Mobile-First Approach
All designs start mobile and scale up.

### Navigation Patterns

#### Desktop Navigation
```tsx
<div className="hidden md:flex items-center gap-8">
  {/* Desktop nav links */}
</div>
```

#### Mobile Menu Toggle
```tsx
<button className="md:hidden">
  <Menu className="h-6 w-6" />
</button>
```

### Layout Patterns

#### Stack on Mobile, Grid on Desktop
```tsx
className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
```

#### Hide on Mobile
```tsx
className="hidden md:block"
```

#### Show on Mobile Only
```tsx
className="md:hidden"
```

#### Responsive Padding
```tsx
className="px-4 sm:px-6 lg:px-8"
```

#### Responsive Text Size
```tsx
className="text-4xl sm:text-5xl lg:text-6xl"
```

### Breakpoint Usage Guidelines
- **Mobile (< 640px):** Single column, stacked layout, larger tap targets
- **Tablet (640px - 1023px):** 2-column grids, condensed nav
- **Desktop (1024px+):** Full layout, 3-4 column grids, all features visible

---

## Content Writing Guidelines

### Voice & Tone
- **Direct:** No corporate speak, get to the point
- **Evidence-Based:** Always cite sources, show data
- **Consumer-Focused:** "You" language, advocate for shoppers
- **Serious but Accessible:** Professional without being stuffy
- **Action-Oriented:** Clear next steps, strong CTAs

### Headline Patterns
```
"Making [Problem] Impossible to Hide"
"[Number]+ [Things] Tracked"
"Zero Tolerance for [Issue]"
"Built for [Audience], Not [Opposite]"
"Evidence-Driven [Value Prop]"
```

### CTA Patterns
```
"Track the Evidence"
"Join the Movement"
"See the Data"
"Submit Evidence"
"Stay Informed"
"Demand Transparency"
```

### Data Label Patterns
```
"[Metric] → [Metric]"  // Change indicator
"[Number]% [Direction]"  // Percentage change
"[Value] per [Unit]"  // Per-unit pricing
"Last [Time Period]"  // Recency
"Since [Date]"  // Historical
"[Status]: [Value]"  // Status indicator
```

---

## Technical Implementation Notes

### Routing
**Package:** react-router (NOT react-router-dom)

```tsx
// App.tsx
import { RouterProvider } from 'react-router';
import { router } from './routes';

function App() {
  return <RouterProvider router={router} />;
}

// routes.ts
import { createBrowserRouter } from "react-router";

export const router = createBrowserRouter([
  { path: "/", Component: Home },
  { path: "/dashboard", Component: Dashboard },
  { path: "/evidence", Component: EvidenceWall },
  { path: "/methodology", Component: Methodology },
  { path: "/product/:id", Component: ProductDetail },
  { path: "/about", Component: About },
  { path: "/join", Component: Join },
  { path: "*", Component: NotFound },
]);
```

### Package Dependencies
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-router": "^6.0.0",
    "motion": "^10.0.0",
    "lucide-react": "^0.400.0",
    "recharts": "^2.0.0",
    "react-responsive-masonry": "^2.0.0"
  }
}
```

### Font Loading
```css
/* /src/styles/fonts.css */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
```

### Theme Configuration
```css
/* /src/styles/theme.css */
@theme {
  --font-headline: 'Space Grotesk', sans-serif;
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

---

## Page Structure Reference

### Home Page
- Hero section with grid background
- Key metrics with counter animations
- Featured shrinkflation cases
- Product category highlights
- How it works section
- Newsletter signup CTA

### Dashboard Page
- Key metrics cards (4-column grid)
- Time range filters
- Trend chart (line chart)
- Category distribution (bar chart)
- Product list with filters
- Export/share functionality

### Evidence Wall Page
- Masonry grid layout
- Category filters
- Severity filters
- Evidence cards with images
- Modal detail view
- Share functionality

### Methodology Page
- Verification pipeline (4 steps)
- Valid evidence criteria (2 columns)
- Confidence ratings (3 levels)
- Correction policy
- Provenance principles

### Product Detail Page
- Product header with badges
- Key metrics (3 cards)
- Size history chart (line chart)
- Before/after comparison
- Evidence documentation
- Related products

### About Page
- Mission statement
- Core values (grid)
- How it started
- Brand voice principles
- Team/community

### Join Page
- Newsletter signup form
- Community benefits
- Alert preferences
- Submit evidence CTA
- Social links

---

## Accessibility Standards

### WCAG AA Compliance
- **Color Contrast:** All text meets 4.5:1 ratio minimum
- **Focus Indicators:** Visible on all interactive elements
- **Semantic HTML:** Proper heading hierarchy, landmarks
- **Keyboard Navigation:** All features accessible via keyboard
- **Screen Readers:** ARIA labels on icon-only buttons

### Best Practices
```tsx
/* Icon button with label */
<button aria-label="Open menu">
  <Menu className="h-6 w-6" />
</button>

/* Status indicator */
<span className="sr-only">Warning:</span>
<AlertCircle aria-hidden="true" />

/* Form label association */
<label htmlFor="email">Email</label>
<input id="email" type="email" />

/* Link purpose */
<Link to="/product/123" aria-label="View Doritos Cool Ranch details">
  View Details
</Link>
```

---

## Design Tokens Summary

```tsx
// Color Tokens
const colors = {
  bg: {
    primary: '#0a0b0d',
    secondary: '#161719',
    tertiary: '#2a2b2d',
    hover: '#1a1b1d',
  },
  text: {
    primary: '#f5f4f0',
    secondary: '#a0a0a5',
    tertiary: '#656569',
  },
  alert: {
    red: '#dc2626',
    redHover: '#ef4444',
  },
  signal: {
    green: '#10b981',
    greenHover: '#059669',
  },
  data: {
    blue: '#3b82f6',
    blueHover: '#2563eb',
  },
  warning: {
    amber: '#f59e0b',
    amberHover: '#d97706',
  },
  border: {
    subtle: 'rgba(255, 255, 255, 0.1)',
    medium: 'rgba(255, 255, 255, 0.2)',
  },
};

// Spacing Tokens
const spacing = {
  section: '96px',     // py-24
  subsection: '64px',  // py-16
  large: '48px',       // gap-12
  medium: '32px',      // gap-8
  small: '24px',       // gap-6
  xs: '16px',          // gap-4
};

// Border Radius Tokens
const radius = {
  sm: '0.5rem',   // 8px
  md: '0.75rem',  // 12px
  lg: '1rem',     // 16px
  xl: '1.5rem',   // 24px
};

// Shadow Tokens (minimal usage)
const shadows = {
  card: 'none',  // Rely on borders instead
  focus: '0 0 0 2px rgba(220, 38, 38, 0.5)',
};
```

---

## Quick Reference: Common Patterns

### Section Header
```tsx
<div className="mb-12 text-center">
  <h2 className="font-headline text-4xl font-bold text-[#f5f4f0] sm:text-5xl">
    Section Title
  </h2>
  <p className="mt-4 text-xl text-[#a0a0a5]">
    Supporting description text
  </p>
</div>
```

### Metric Display
```tsx
<div className="text-center">
  <div className="font-mono text-5xl font-bold text-[#dc2626]">
    <CounterAnimation value={1247} />+
  </div>
  <div className="mt-2 text-sm font-medium uppercase tracking-wide text-[#a0a0a5]">
    Label
  </div>
</div>
```

### Split Section
```tsx
<div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
  <div>{/* Left content */}</div>
  <div>{/* Right content */}</div>
</div>
```

### List with Icons
```tsx
<ul className="space-y-4">
  <li className="flex items-start gap-3">
    <CheckCircle className="h-5 w-5 flex-shrink-0 text-[#10b981]" />
    <span className="text-[#a0a0a5]">List item text</span>
  </li>
</ul>
```

### Bordered Section
```tsx
<section className="border-y border-white/10 bg-[#161719] py-24">
  {/* Content */}
</section>
```

---

**Document Version:** 2.0  
**Last Updated:** March 9, 2026  
**Platform:** FullCarts Shrinkflation Intelligence  
**Status:** Production Design System
