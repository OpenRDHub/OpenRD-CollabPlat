# Findings

## Project Snapshot
- Repository is a lightweight demo/prototype workspace.
- Main demo files live under `demo/`.
- Current visual direction follows Webflow-inspired styling from AGENTS.md: white/near-black base, Webflow Blue `#146ef5`, small radii, crisp cards, restrained decorative elements.

## Existing Demo Pages
- `demo/login.html`: Login screen with left promotional panel and right login form.
- `demo/forgot-password.html`: Two-step password reset flow.
- `demo/register.html`: Registration form with platform ID, phone verification, password toggles.
- `demo/account-onboarding.html`: Three-step account initialization wizard with dynamic second step for patient/family vs volunteer.
- `demo/gesture-particles/index.html`: Independent camera gesture + Canvas particles demo.
- `demo/gesture-particles/README.md`: Usage documentation for gesture particles demo.

## Important Implementation Notes
- Auth pages use a unified desktop container size around `1460px × 640px`.
- Account onboarding also uses `1460px × 640px` desktop card, with responsive behavior on smaller screens.
- Gesture demo uses MediaPipe Tasks Vision from CDN and requires `localhost` or HTTPS for camera access.

## Community Homepage Demo
- Added demo/home.html as a Webflow-style community homepage demo.
- Includes top navigation, hover profile card, task overview metrics, registered user metrics, and tabbed task/demand hall list.
- Tab switch is handled with lightweight inline JavaScript.

## Demand Submission Modal
- Added a lightweight homepage demand submission modal in demo/home.html.
- Fields: demand title, demand detail, phone, WeChat, simulated attachment, privacy confirmation.
- Validation requires title, detail, either phone or WeChat, and privacy confirmation.

## Workbench Demo
- Added demo/workbench.html as a standalone role-based workbench page.
- Role switcher covers requester, co-builder, operation admin, and super admin.
- Info metrics and feature tiles render from inline role data; tile clicks show toast only.

## User Management Demo
- Added demo/user-management.html as a standalone user management page.
- The user table includes UUID, platform ID, nickname, identity, position, phone, registration time, introduction, participated projects, password, and edit action.
- Edit action opens a modal; UUID and registration time are read-only while mutable profile fields can be changed.
- Password editing includes show/hide behavior and table passwords are masked.

## Permission Management Demo
- Added demo/permission-management.html as a standalone permission management page.
- The page uses role permission templates as the base permission source and supports manually adding extra permissions per member.
- Permission editing opens a modal with inherited template permissions locked and additional permissions selectable by group.
- The table includes role filtering, keyword search, manual permission tags, risk level display, and update feedback.

## System Log Demo
- Added demo/system-log.html as a standalone super-admin-only audit log page.
- The page includes summary cards, module/risk/result filters, keyword search, audit table, detail modal, and export toast feedback.
- Mock logs cover login security, permission management, user management, task management, demand management, and system configuration.

## My Tasks and Task Detail Demo
- Added demo/my-tasks.html as a participant-oriented personal task list page.
- Added demo/task-detail.html as a shared detail page that reads task IDs from `?id=TASK_ID`.
- My tasks page includes summary cards, status tabs, keyword search, status filtering, progress display, and detail links.
- Task detail page includes overview, progress, role, team members, demand source, milestones, attachments, and action feedback.

## Unified Top Navigation
- Applied the community homepage topnav pattern to workbench, user management, permission management, system log, my tasks, and task detail pages.
- Unified platform brand text, demand/workbench actions, and hover profile card presentation across topnav-based demo pages.
- Adjusted removed topnav action listeners to be optional where page-specific buttons no longer live in the nav.

## My Demands Demo
- Added demo/my-demands.html as a submitter-oriented demand tracking page.
- The page includes demand summary cards, lifecycle tabs, keyword search, status filtering, demand hall-style rows, progress display, and future-detail toast feedback.
- Mock demands cover pending review, communication, converted-to-task, and closed lifecycle states.

## Profile Demo
- Added demo/profile.html as a standalone personal information page.
- The page includes unified top navigation, profile hero card, avatar initials, platform ID, phone, identity, occupation, region, personal intro, skill tags, and participation stats.
- Edit modal can update mutable profile fields while keeping platform ID read-only; skill tags can be added or removed with a six-tag limit.

## Message Center Demo
- Added demo/message-center.html as a standalone in-site message center page.
- The page uses left-side message categories and a right-side message list, similar to Bilibili-style station messages.
- Mock messages cover system notifications, task updates, demand progress, team applications, and replies/private messages.
- Interactions include unread counts, search, unread-only filter, mark read, mark all read, delete, detail drawer, and toast feedback.

## Team Detail Demo
- Added demo/team-detail.html as a task-bound team detail page using `?task=TASK_ID`.
- The page is designed from captain perspective and includes bound task overview, team stats, members, join applications, assignments, and timeline.
- Mock teams cover recruiting and active collaboration scenarios; actions show toast feedback only.

## Demand Detail Demo
- Added demo/demand-detail.html as a standalone demand detail page using `?id=REQ_ID`.
- The page uses a two-column layout with demand lifecycle information on the left and an operations/publisher conversation area on the right.
- Conversation area supports appending local messages and simulated supplemental attachments.
- Updated my-demands detail buttons to link to demand-detail.html with the demand ID.

## Task and Demand Management Demo
- Added demo/task-management.html for operation/admin task governance.
- The task management page includes task summary cards, keyword search, task status/team status filters, full-width table, progress bars, and edit modal.
- Added demo/demand-management.html for operation/admin demand governance.
- The demand management page includes demand lifecycle summary cards, keyword search, review/conversion filters, full-width table, progress bars, and edit modal.
- Workbench management tiles now navigate to the concrete demo pages, including task management and demand management.

## Demo Collection and Entry Logic
- Added demo/index.html as a client-facing demo collection hub with recommended presentation flow and all page entries.
- Auth demos now form a demonstrable chain: login -> workbench, register -> account onboarding, forgot password -> login, onboarding -> workbench.
- The community homepage hall rows now include details buttons for task and demand detail pages.
- Task and demand management tables now provide both details and edit actions.
- Task detail now links to both team detail and demand detail, reinforcing the task/team/demand relationship.
- Workbench now includes profile and message center tiles for all roles.

## Task Detail Layout Refinement
- Updated demo/task-detail.html so the hero area and info grid live inside one overview card.
- Added an edit button to the task description and milestone panel.
- Moved the team detail entry into the team members card header.
- Combined demand source, project attachments, project resources, and collaboration actions into one wide resource card.
- Added mock project resources such as GitHub repositories, documentation, staging environments, and archive pages.
- Added extra spacing between the overview and lower panels, equalized the progress/team card height, and changed milestones into a scrollable project progress area.
- Moved submit update back to the task progress card and added an edit modal for demand source and project resource information.

## 2026-06-04 Project Understanding Baseline
- Workspace root is `E:\MyCode\OpenRD`; it is not a Git repository.
- Main product demo is a static prototype under `demo/`, with one HTML file per page and inline CSS/JavaScript.
- There is no visible package/build setup in the root; continue treating changes as static demo-only unless the user asks otherwise.
- Important pages now include auth flow, onboarding, community home, role workbench, profile, message center, my tasks, task detail, team detail, my demands, demand detail, user/permission/system-log admin pages, task management, demand management, and demo collection hub.
- `demo/index.html` is the best client-presentation entry point. It links the recommended flow and every major page.
- `demo/workbench.html` drives role-based navigation through inline `roleData` and `tiles` definitions.
- `demo/home.html` is the community homepage and contains task/demand hall links plus the global demand submission modal.
- `demo/task-detail.html` and `demo/demand-detail.html` are key relationship anchors because they connect task, team, demand, resource, and communication narratives.
- Several source docs in `doc/` display with mojibake in the current terminal, but previous findings already capture the usable product direction.
- Future demo optimization should prioritize presentation flow, page-to-page continuity, visual consistency with the Webflow design system, and reducing dead-end/toast-only interactions where a concrete demo page exists.

## Demand Detail PM Processing Optimization
- `demo/demand-detail.html` now uses an operation-admin/product-manager processing desk instead of a normal chat panel.
- The right-side area follows the card/list rhythm of `demo/team-detail.html`: summary cards, product manager cards, status tags, and structured action buttons.
- Multiple product managers can ask different questions and record different evaluation conclusions for one demand.
- A demand must be claimed by a product manager before task conversion is available.
- Converted demands show a task-view action and route to the related task detail page.
- The conversion modal simulates two systems meeting: demand context becomes a task work-order draft with title, source demand, owner, task type, priority, scope, and acceptance criteria.
- Demand publisher supplements remain available, but they update the relevant PM processing card rather than driving the page as a chat UI.

## Demand Detail Dual-View Conversation Correction
- Corrected the demand detail model: product managers do not separately claim a demand before conversion.
- Whoever converts the demand to a task is considered the product manager who has accepted/owned that demand.
- The right-side area should be a communication zone, not a processing-card zone.
- Multiple product managers can each maintain a separate conversation with the same demand requester.
- The page now supports product/requester view switching in the hero area while preserving one shared page for demo explanation.
- Product view can send PM messages and convert an information-sufficient conversation into a task.
- Requester view can switch PM conversations, reply to the selected PM, and add supplemental attachments without seeing task-conversion controls.

## Demand Detail WeChat-Style Conversation Layout
- The demand detail page now prioritizes the communication experience by placing the conversation module on the left.
- Demand information and processing timeline now sit in the right column as supporting context.
- The conversation module uses a WeChat-like split layout: product manager conversation list on the left, selected message stream and input composer on the right.
- On tablet/mobile, the conversation list becomes a horizontally scrollable selector above the message pane.
- Visual refinement: the communication module should feel like one integrated IM workspace, while the demand information column should be a compact supporting sidebar rather than competing card stacks.

## Demand Detail Final Layout Direction
- The clearer preferred hierarchy is: status overview first, then demand information and processing flow as two side-by-side panel cards, then the communication module below.
- This keeps demand context visible before conversation while still preserving the multi-PM conversation model.

## Demand Detail Operation-Admin Visibility Rule
- In this demo, "产品经理" means the operation admin/product operator responsible for evaluating and converting demands.
- Product/operation-admin view must not expose other admins' private conversations with the requester.
- Requester view can see and switch between multiple operation-admin conversations because the requester is the common participant.
- The "转化任务" action belongs to the product/operation-admin view; conversion is the moment that admin effectively accepts/owns the demand.

## Requester Role Experience Demo
- `demo/all-pages/` is a full snapshot folder for all current demo HTML pages.
- `demo/requester/` is the first role-specific experience folder.
- The requester experience entry is `demo/requester/index.html`, which introduces OpenRD, defines the requester role, and routes to `login.html`.
- `demo/requester/local-data.js` stores requester role metadata, flow steps, and demand summaries in `localStorage`.
- Requester experience pages include auth/onboarding, workbench, home, my demands, demand detail, message center, profile, my tasks, task detail, and team detail so post-conversion tracking links do not break.
- The requester workbench is scoped to a single requester role instead of exposing all role-switch tabs.

## Builder Role Experience Demo
- `demo/builder/` is the second role-specific experience folder.
- The builder experience entry is `demo/builder/index.html`, which introduces OpenRD, defines the co-builder role, and routes to `login.html`.
- `demo/builder/local-data.js` stores builder role metadata, flow steps, and task summaries in `localStorage`.
- Builder experience pages include auth/onboarding, workbench, community home, my tasks, task detail, team detail, my demands, demand detail, message center, and profile.
- The builder workbench is scoped to a single co-builder role and admin-only pages are not linked.
- Team-detail assignment edits in the builder folder update the local builder task summary so `my-tasks.html` can reflect locally saved collaboration state.

## Operator Role Experience Demo
- `demo/operator/` is the operation admin/product manager role-specific experience folder.
- The operator experience entry is `demo/operator/index.html`, which introduces OpenRD, defines the operator/product-manager role, and routes to `login.html`.
- Operator login routes to `home.html` first, keeping the same role demo rule as requester and builder.
- `demo/operator/local-data.js` stores operator role metadata, flow steps, demand state, and task state under an operator-specific localStorage key.
- The key demo demand `REQ-2418` defaults to `沟通中 / 待转化`, and the operator local task list starts empty so the demand-to-task conversion is visible during the presentation.
- `demo/operator/demand-detail.html` defaults to product/operator view and writes conversion results back to operator local data.
- Operator/product-manager should not enter full demand management or task management; those are super-admin-only governance pages.
- Operator workbench now routes to demand detail communication instead of demand/task management tables.
- `demo/operator/demand-management.html` and `demo/operator/task-management.html` are permission-restricted fallback pages if opened directly.

## Super Admin Role Experience Demo
- `demo/superadmin/` is the super administrator role-specific experience folder.
- The super-admin experience entry is `demo/superadmin/index.html`, which introduces OpenRD, defines the super-admin role, and routes to `login.html`.
- Super-admin login inherits the role demo rule and routes to `home.html` first.
- `demo/superadmin/local-data.js` stores super-admin role metadata, governance metrics, and flow steps in localStorage.
- The current super-admin demo user is `顾星河 / admin_guxinghe / 超级管理员`.
- The super-admin workbench is scoped to a single `超管体验` role and exposes all governance pages: user management, permission management, system log, task management, demand management, messages, profile, my tasks, and my demands.
- User management, permission management, and system log sample data now include the `顾星河` super-admin account so the governance demos match the current role.

## Unified Role Entrance
- `demo/index.html` is now the unified entrance for the four role experience demos.
- It links directly to `demo/requester/index.html`, `demo/builder/index.html`, `demo/operator/index.html`, and `demo/superadmin/index.html`.
- It keeps a secondary entry to `demo/all-pages/index.html` for the full snapshot/collection page.
- The suggested presentation order is requester, operator, builder, then super admin.

## 2026-06-08 Documentation and Development Preparation
- Current workspace root is `E:\MyCode\OpenRD`.
- Root project currently contains `backend/`, `frontend/`, `docs/`, `demo/`, `.env.example`, `.gitignore`, `README.md`, `llms.txt`, and planning files.
- `backend/` and `frontend/` currently contain only README placeholders; there are no package manifests, Vite config, server config, lockfiles, Docker files, or database migration files.
- The current runnable/presentable artifact is the static HTML prototype under `demo/`; open `demo/index.html` directly in a browser for the role-experience entrance.
- `demo/` contains role-specific folders: requester, builder, operator, and superadmin. `demo/all-pages/` is the full snapshot folder.
- Existing root README is directionally useful but has stale paths: it points to `docs/prototype/demo/` and `docs/design-system/`, which do not currently exist.
- Product documentation source files live directly under `docs/`, including the PRD template, Feishu PRD export, platform design suggestions, platform concept notes, and role workbench tile matrix.
- Chinese product docs should be read as UTF-8 in PowerShell with `Get-Content -Encoding UTF8`; otherwise mojibake appears.
- Development preparation should focus on documenting decisions and initialization steps first, not claiming a runnable app exists.

## 2026-06-08 Formal PRD Understanding
- The user archived historical redundant docs into `docs/backup/`.
- The current authoritative PRD is `docs/OpenRD协作平台PRD正式版.md`.
- Product name in the formal PRD is `罕见病运营管理平台`; repository/project name remains OpenRD.
- Core product goal: users submit demands and claim tasks to collaboratively solve rare-disease problems.
- Business goals: improve operation efficiency, reduce manual operation cost, help new community members find projects, and move most demand-to-project setup work online.
- Product scope includes user registration/login, demand submission and management, task management and claiming, workbench/operation functions, and personal center.
- Explicitly out of current scope: community discussion, points/incentives, medical certification, and AI demand optimization; these are future phases or suggestions.
- Current role terminology: 需求者, 共建者, 产品经理, 超级管理员.
- Key business model: two connected systems. First, requesters and product managers handle demand intake/evaluation. Second, product managers publish converted tasks and co-builders collaborate on delivery.
- Product managers are screened capable operators who receive/evaluate demands, communicate with requesters, convert valid demands into tasks, and manage task progress.
- Co-builders browse task hall, apply to join teams, participate in development, and may become captain/leader in the task team flow.
- Super administrators manage users, permissions, system configuration, and security/audit concerns.
- Core P0 functions in PRD: registration, login, forgot password, demand submission, demand review/conversion, task hall, task detail/claiming, user management, permission management, demand management, task management, my demands, my tasks, and message notifications.
- Non-functional requirements include page load under 3 seconds, API response under 2 seconds, 1000 concurrent users, bcrypt password storage, HTTPS, authenticated APIs, operation logs, and frontend/backend authorization checks.
- Core data tables listed by PRD: users, demands, tasks, task_members, roles, permissions, role_permissions, system_logs, and demand_replies.
- User instruction: all README files should be written in Chinese.
- Project structure convention to remember: this is a single repository with separate `frontend/` and `backend/` folders for the frontend and backend projects.

## 2026-06-08 Open Collaboration Governance Discussion
- User is managing a long-term public-interest technical project driven by real patient needs.
- Major operational concerns: single-person dependency, future handover when the current product/project owner interns or steps away, unstable volunteer participation, uneven participant ability, uneven available time, and balancing a close startup technical team with open collaboration.
- Proposed strategic framing: OpenRD should use its own platform logic to manage OpenRD's own development; this makes the platform's self-improvement the first long-running operating case.
- Lightweight governance should focus on capabilities rather than heavy bureaucracy.
- Recommended capability centers: resource center, architecture center, task-splitting center, and teaching/growth center.
- A project management committee can coordinate direction, resources, key decisions, risk, and handover, but should not become a bottleneck.
- Core team should focus on documentation, task decomposition, review, merge, release, and teaching, while keeping contribution entry points open.
- Subtask system is a Phase 2 product priority because it lowers participation thresholds, improves handover, supports uneven contributor time, and turns large tasks into reviewable units.
- SOP is a core operating asset, not formality. Important SOPs include demand intake, demand communication, task conversion, subtask splitting, contributor claiming, code review, task acceptance, and handover/exit.
- If OpenRD's internal process works, it can become a reusable open-source project development SOP template for future demand-to-task conversion, development, maintenance, and operations.
- Governance structure should scale by project stage and size rather than starting with a full management team.
- A full four-center model can be too heavy early because two people per center already means eight managers.
- Recommended evolution: initial MVP team takes the task, ships MVP, then the original developers gradually transform into a project management body based on actual responsibilities.
- Project owner should gradually delegate planning, prioritization, task allocation, review/merge rules, acceptance organization, resources, permissions, and handover handling to the project management committee.

## 2026-06-09 Task Detail Feedback Adjustments
- Active task detail pages currently live under `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`; there is no root `demo/task-detail.html`.
- `demo/backup/task-detail.html` is treated as archived and was not modified.
- User feedback required the task detail page to rename `任务说明与项目进度` to `项目进度`.
- User feedback required `需求来源与项目资源` to become `任务信息与项目资源`.
- The old `需求来源` block has been replaced by a `任务信息` block using work-order fields: 来源需求, 转化产品经理, 任务类型, 优先级, 工单范围, and 验收标准.
- The edit modal now edits task information fields plus project resources, attachments, and collaboration actions. 来源需求 is read-only.
- Module order is now: `任务信息与项目资源`, then `项目进度`, then `团队成员`.
