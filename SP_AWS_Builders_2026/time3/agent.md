# Business App - AI Agent Instructions & Project Context

> **Hackathon Repository**: [henriqueleandro-arch/LatamHackathon](https://github.com/henriqueleandro-arch/LatamHackathon)  
> **Sub-project**: `business/` (SvelteKit + TiDB/MySQL + Drizzle ORM)

---

## 1. Project Overview & Context

This project is part of the **TiDB LATAM Hackathon** (`LatamHackathon`). The `business` workspace is a full-stack web application designed for airline operations, business intelligence, booking management, and flight analytics, powered by a TiDB / MySQL distributed database.

### Core Domain Entities
The application manages and analyzes data across the following core domains:
- **Aviation & Fleet**: `airline`, `airplane`, `airplane_type`, `airport`, `airport_geo`
- **Schedules & Flights**: `flight`, `flightschedule` (routes, departure/arrival schedules, weekly recurrence)
- **Reservations & Customers**: `passenger`, `passengerdetails`, `booking` (seat assignments, fares)
- **Operations & Personnel**: `employee` (departments, credentials, payroll)
- **Telemetry & Environment**: `weatherdata` (temperature, pressure, wind, precipitation events)

---

## 2. Technical Stack

| Category | Technology | Notes |
| :--- | :--- | :--- |
| **Framework** | [SvelteKit 2](https://kit.svelte.dev/) & [Svelte 5](https://svelte.dev/) | Utilizes Svelte 5 Runes (`$state`, `$derived`, `$props`, `$effect`) |
| **Language** | TypeScript (v6) | Strict type checking via `svelte-check` & `tsconfig.json` |
| **Styling** | Tailwind CSS v4 (`@tailwindcss/vite`) | Integrated typography & forms plugins |
| **Database** | TiDB / MySQL | Relational data layer running locally via Docker or TiDB Cloud |
| **ORM** | Drizzle ORM (`drizzle-orm`, `drizzle-kit`, `mysql2`) | Type-safe schema, migrations, queries, and relations |
| **Testing** | Vitest & Playwright | Browser testing and component unit tests |
| **Package Manager**| `pnpm` | Standard package manager for all commands |

---

## 3. Directory Structure

```
business/
├── .env                  # Local environment configuration (DATABASE_URL, etc.)
├── .env.example          # Environment variable template
├── compose.yaml          # Local MySQL/TiDB Docker service definition
├── drizzle.config.ts     # Drizzle Kit configuration (schema path, dialect, SSL)
├── package.json          # Project scripts and dependencies
├── src/
│   ├── app.d.ts          # App-wide ambient TypeScript declarations
│   ├── app.html          # HTML shell template
│   ├── lib/
│   │   ├── index.ts      # Shared library exports
│   │   ├── assets/       # Static assets & icons
│   │   └── server/
│   │       └── db/       # Database layer
│   │           ├── index.ts      # MySQL connection pool & Drizzle client instance
│   │           ├── schema.ts     # MySQL Drizzle schema table definitions
│   │           ├── relations.ts  # Drizzle relational mappings
│   │           └── meta/         # Drizzle migration metadata
│   └── routes/           # SvelteKit file-based routing
│       ├── +layout.svelte # Root layout shell
│       ├── +page.svelte   # Landing / Dashboard page
│       └── layout.css     # Global CSS and Tailwind directives
└── static/               # Public static assets
```

---

## 4. Key Commands & Workflow

All commands should be executed from within the `business/` folder using `pnpm`:

### Development
```bash
# Start Vite development server
pnpm dev

# Type check across Svelte components and TS files
pnpm check

# Run linter & formatter checks
pnpm lint
pnpm format
```

### Database Operations
```bash
# Start local database container
pnpm db:start

# Pull/introspect schema from database into Drizzle schema
pnpm db:pull

# Push schema changes directly to the database
pnpm db:push

# Generate new migration files based on schema.ts
pnpm db:generate

# Apply pending migrations
pnpm db:migrate

# Open Drizzle Studio visual GUI
pnpm db:studio
```

### Testing & Build
```bash
# Run unit & component tests
pnpm test

# Build for production
pnpm build

# Preview production build
pnpm preview
```

---

## 5. Development Guidelines for AI Agents

### Svelte 5 Best Practices
- **Use Runes**: Always use Svelte 5 runes (`let count = $state(0)`, `$derived(...)`, `$effect(...)`, `let { prop1 } = $props()`). Do **not** use legacy Svelte 3/4 reactive declarations (`$: ...`) or `export let`.
- **Server Loaders**: Database queries should be executed server-side in `+page.server.ts` or `+layout.server.ts` using the exported `db` instance from `$lib/server/db`.
- **Form Actions & API**: Prefer SvelteKit Form Actions for mutations (`+page.server.ts: actions`) to ensure progressive enhancement.

### Database & Drizzle ORM
- Import `db` exclusively from `$lib/server/db`.
- When querying related tables, leverage Drizzle's relational query API (`db.query.flight.findMany({ with: { airline: true, bookings: true } })`) as defined in `src/lib/server/db/relations.ts`.
- Ensure environment variable `DATABASE_URL` is configured in `.env` matching TiDB / MySQL connection format:
  ```env
  DATABASE_URL="mysql://root:mysecretpassword@127.0.0.1:3306/local"
  ```
- Keep `schema.ts` and `relations.ts` in sync whenever database tables or foreign keys are updated.

### Code Quality & Standards
- Maintain strict typing for database responses, API payloads, and component props.
- Ensure all new components and utilities are tested with `pnpm check` and `pnpm test`.
