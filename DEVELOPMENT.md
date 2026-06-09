# OpenRD Development Preparation

This document captures the current development readiness state and the next setup work needed before feature implementation.

## Current State

- The repository currently has a static HTML prototype in `demo/`.
- `frontend/` and `backend/` are placeholders only.
- There are no install, build, test, lint, migration, or dev-server commands yet.
- The product source documents live in `docs/`.

## Stage 0: Align Decisions

Complete these decisions before initializing code:

- Frontend package manager and Node version.
- Backend runtime, framework, package manager, and language.
- Database engine and migration tool.
- Authentication model: session, JWT, or hybrid.
- Authorization model: role templates plus fine-grained permissions.
- API contract format: OpenAPI, typed RPC, or another documented contract.
- File attachment storage strategy.
- Deployment target and environment naming.

## Stage 1: Frontend Initialization

Recommended setup:

- Vue 3 + Vite + TypeScript.
- Vue Router for route-level role guards.
- Pinia for auth, current user, demand/task state, and UI state.
- ESLint + Prettier for formatting and static checks.
- A local design-token layer matching the existing Webflow-inspired prototype.

Initial migration order:

1. App shell, router, layout, and top navigation.
2. Login, register, forgot password, and onboarding.
3. Home and role workbench.
4. Demand list/detail and demand-to-task conversion.
5. Task list/detail and team detail.
6. Message center and profile.
7. Governance pages for super admin.

## Stage 2: Backend Initialization

Recommended first modules:

- Health check and application config.
- Auth and current-user endpoint.
- Users, profiles, roles, permissions.
- Demands, demand conversations, and conversion records.
- Tasks, teams, member applications, assignments, and milestones.
- Messages and notification state.
- Audit logs.

Keep the first backend milestone small enough to support the frontend shell and the core demand-to-task flow.

## Stage 3: API Contract

Document API contracts before connecting the Vue app to backend data.

Minimum endpoint groups:

- `auth`
- `users`
- `roles`
- `permissions`
- `demands`
- `tasks`
- `teams`
- `messages`
- `audit-logs`

Each endpoint should document request shape, response shape, permissions, validation errors, and audit behavior.

## Stage 4: Local Development Commands

Add concrete commands only after projects are initialized. Expected future command groups:

- Install dependencies.
- Start frontend dev server.
- Start backend dev server.
- Run frontend type check and lint.
- Run backend tests.
- Run migrations.
- Build production artifacts.

## Stage 5: Definition of Ready

Development is ready to start when:

- `frontend/package.json` and frontend config files exist.
- `backend` has a selected runtime and executable local server.
- Database and migrations are configured.
- `.env.example` matches the selected stack.
- README files contain real commands that have been verified locally.
- API contract documentation exists for the first end-to-end flow.
