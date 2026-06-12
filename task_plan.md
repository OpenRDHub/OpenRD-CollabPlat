# OpenRD Demo Planning

## Goal
Maintain persistent planning context for OpenRD work in this repository. The current conversation goal is to read the project, improve project documentation, and prepare the codebase for frontend/backend development.

## Current Status
- Status: active
- Current phase: Phase 23 complete — task detail demo feedback adjustments

## Phases
| Phase | Status | Notes |
|---|---|---|
| Phase 1: Initialize planning files | complete | Created task_plan.md, findings.md, progress.md in project root. |
| Phase 2: Community home page demo | complete | Created `demo/home.html` with navigation, stats, profile hover card, and task/demand hall tabs. |
| Phase 3: Demand submission modal | complete | Added modal opened from `提需求`, with lightweight fields, validation, attachment feedback, and toast. |
| Phase 4: Workbench demo | complete | Created `demo/workbench.html` with role-based information cards and feature tiles. |
| Phase 5: User management demo | complete | Created `demo/user-management.html` with editable user table, phone field, and modal. |
| Phase 6: Permission management demo | complete | Created `demo/permission-management.html` with role templates and manual permission grants. |
| Phase 7: System log demo | complete | Created `demo/system-log.html` as a super-admin-only audit log page. |
| Phase 8: My tasks and task detail demo | complete | Created `demo/my-tasks.html` and `demo/task-detail.html` for personal task tracking and shared detail viewing. |
| Phase 9: Unified platform top navigation | complete | Applied the community homepage top navigation pattern across topnav-based demo pages. |
| Phase 10: My demands demo | complete | Created `demo/my-demands.html` as a submitter-oriented demand tracking page. |
| Phase 11: Profile demo | complete | Created `demo/profile.html` with profile display, editable modal, and skill tags. |
| Phase 12: Message center demo | complete | Created `demo/message-center.html` with categorized in-site messages and unread operations. |
| Phase 13: Team detail demo | complete | Created `demo/team-detail.html` as a task-bound team detail page from captain perspective. |
| Phase 14: Demand detail demo | complete | Created `demo/demand-detail.html` with demand info and operations/publisher conversation area. |
| Phase 15: Task and demand management demo | complete | Created admin-style task and demand management pages and linked workbench tiles. |
| Phase 16: Demo collection and entry logic | complete | Created `demo/index.html` and connected major presentation flows. |
| Phase 17: Task detail layout refinement | complete | Refined `demo/task-detail.html` information hierarchy, resources, and edit modal. |
| Phase 18: Continuous demo optimization baseline | in_progress | Understand current project, preserve planning context, and prepare for iterative demo improvements. |
| Phase 19: Role experience demos | complete | Built role-specific demo folders with scoped navigation, local mock data, welcome pages, and unified role entrance. |
| Phase 20: Documentation and development preparation | complete | Read current repository state, corrected documentation paths, and added development onboarding docs. |
| Phase 21: Chinese README rewrite from formal PRD | complete | Read the archived-docs project state and formal PRD, then rewrote all README files in Chinese. |
| Phase 22: Open collaboration governance and SOP document | complete | Summarized the user's operating concerns, governance ideas, subtask-system design, and reusable open-source project SOP. |
| Phase 23: Task detail demo feedback adjustments | complete | Updated task detail page labels, task-info work-order fields, edit modal, and module order across active demo role folders. |
| Phase 26: OpenRD-UI component library | complete | Built 20 Ord-prefixed Vue 3 components based on Reka UI + demo visual extraction. Structure: frontend/src/components/ui/. |
| Phase 27: UI showcase page | complete | Full showcase at /dev with all 20 components, dev server verified at localhost:5174. |

## Phase 5 Requirements
- Independent page: `demo/user-management.html`.
- Use table/list layout for user records.
- Fields: UUID, platform ID, nickname, identity, role/position, registration time, introduction, participated projects, phone, password, edit action.
- UUID must be read-only and immutable.
- Edit action opens modal form in same Webflow style.
- Modal should allow editing all mutable fields and show registration time as read-only.

## Phase 6 Requirements
- Independent page: `demo/permission-management.html`.
- Keep the same Webflow-inspired management-page style.
- Show member permission overview similar to user management.
- Support role permission templates for requester, co-builder, operation admin, and super admin.
- Allow manually adding individual permissions beyond the selected role template.
- Use a modal for fine-grained permission editing.

## Phase 7 Requirements
- Independent page: `demo/system-log.html`.
- Keep the same Webflow-inspired management-page style.
- Present the page as visible only to super admins.
- Show comprehensive audit logs for login, permission, user, task, demand, and system configuration operations.
- Provide filters for keyword, module, risk level, and result status.
- Use a modal for detailed audit context.

## Phase 8 Requirements
- Independent page: `demo/my-tasks.html`.
- Independent shared detail page: `demo/task-detail.html`.
- Keep the same Webflow-inspired style and task hall list pattern.
- Use participant perspective for my tasks.
- Provide status tabs: all, pending, in progress, completed.
- Link task rows to `task-detail.html?id=TASK_ID`.
- Detail page should render task overview, progress, role, team, demand source, milestones, attachments, notes, and actions.

## Phase 9 Requirements
- Use the community homepage top navigation pattern on all demo pages that have a topnav.
- Keep platform brand text, `提需求`, `工作台`, and hover profile card consistent.
- Preserve page-specific content and scripts outside the navigation.

## Phase 10 Requirements
- Independent page: `demo/my-demands.html`.
- Use submitter perspective for demand tracking.
- Keep unified platform top navigation and Webflow-inspired style.
- Provide lifecycle tabs: all, pending review, communicating, converted to task, closed.
- Show demand details, submitted time, review status, conversion status, related task, and progress.
- Keep demand detail as a future feature; detail buttons show toast only.

## Phase 11 Requirements
- Independent page: `demo/profile.html`.
- Keep unified platform top navigation and Webflow-inspired style.
- Show avatar, nickname, platform ID, phone, identity, occupation, personal intro, region, and skill tags.
- Support identities: co-builder, requester, super admin, operation admin.
- Reference account onboarding fields for region, skill tags, and personal intro.
- Provide edit modal; platform ID remains read-only.
- Skill tags support custom additions up to 6.

## Phase 12 Requirements
- Independent page: `demo/message-center.html`.
- Keep unified platform top navigation and Webflow-inspired style.
- Use a Bilibili-like in-site message layout with left categories and right message list.
- Categories include all, system, task, demand, team application, and reply/private message.
- Support unread counts, search, unread-only filter, mark read, mark all read, delete, and detail drawer.

## Phase 13 Requirements
- Independent page: `demo/team-detail.html`.
- Bind team detail to task ID via `?task=TASK_ID`.
- Use captain perspective and show full team detail.
- Include bound task, team overview, members, join applications, assignments, and team timeline.
- Provide invite, assignment adjustment, approve, and reject actions as toast feedback.

## Phase 14 Requirements
- Independent page: `demo/demand-detail.html`.
- Read demand by `?id=REQ_ID`.
- Use two-column layout: left demand information and right operations/publisher conversation area.
- Show demand status, conversion status, related task, attachments, platform feedback, and processing timeline.
- Support sending messages and simulated supplemental attachments in conversation area.
- Link my demands detail buttons to this page.

## Phase 15 Requirements
- Independent admin page: `demo/task-management.html`.
- Independent admin page: `demo/demand-management.html`.
- Reference user management and permission management layout patterns.
- Keep unified platform top navigation and Webflow-inspired style.
- Task management should show summary cards, keyword/status/team filters, task table, and edit modal.
- Demand management should show summary cards, keyword/review/conversion filters, demand table, and edit modal.
- Use “已转任务” terminology for converted demands.
- Link workbench task and demand management tiles to the new pages.

## Phase 16 Requirements
- Add a complete demo collection hub at `demo/index.html` for client presentation.
- Improve entry logic across existing demo pages so major flows can be demonstrated without manually typing URLs.
- Connect auth flow: login to workbench, register to onboarding, forgot password back to login, onboarding to workbench.
- Add details buttons where list/table pages lacked obvious detail entry points.
- Add profile and message center tiles to the role-based workbench.
- Keep all changes static and demo-only using HTML, CSS, and JavaScript.

## Phase 17 Requirements
- Refine `demo/task-detail.html` layout.
- Merge hero and info grid into a single task overview container.
- Add edit action to the task description and milestone card.
- Move team detail entry into the team members card.
- Merge demand source and attachment areas into one resource card.
- Add project resource entries such as repository, documentation, staging, or archive links.

## Phase 18 Requirements
- Treat the ongoing conversation as focused on optimizing the existing demo.
- Preserve static demo constraints: plain HTML, CSS, and JavaScript; no build tool unless explicitly requested.
- Prioritize client presentation quality: clear entry flow, connected page journeys, coherent information hierarchy, and Webflow-inspired visual consistency.
- Use `demo/index.html` as the collection hub and `demo/workbench.html`, `demo/home.html`, `demo/task-detail.html`, and `demo/demand-detail.html` as key narrative anchors.
- Keep discoveries in `findings.md` and implementation/session notes in `progress.md`.

## Phase 19 Requirements
- Preserve the existing root `demo/*.html` pages as the working demo source.
- Create `demo/all-pages/` as a full-page snapshot folder containing all current demo HTML pages.
- Create `demo/requester/` as the first role experience demo for the demand requester role.
- Create `demo/builder/` as the second role experience demo for the co-builder role.
- The requester role demo should start from a welcome/index page, introduce OpenRD and the requester role definition, then route into login.
- Keep requester navigation scoped to pages the requester can directly access or needs for the flow: auth, onboarding, workbench, home, my demands, demand detail, task tracking, messages, profile, and related task/team detail pages.
- Use a local mock-data file for role-level state synchronization.
- Builder role demo should start from a welcome/index page, define the co-builder role, then route into login and a co-builder-scoped workbench.
- Create `demo/operator/` as the third role experience demo for operation admin/product manager.
- Operator role demo should start from a welcome/index page, define the operation admin/product manager role, then route into login and community home.
- Operator workbench should be scoped to operation/admin-product-manager capabilities, keeping demand detail communication and task conversion as the core path.
- Operator/product-manager role should not enter task management or demand management; only super admin can modify those management pages.
- Operator local mock data should default the key demand to unconverted state so the demo can show demand-to-task conversion clearly.
- After conversion, operator role should continue into task detail tracking rather than full management tables.
- Create `demo/superadmin/` as the fourth role experience demo for the super administrator role.
- Super admin role demo should start from a welcome/index page, define global platform governance responsibility, then route into login and community home.
- Super admin workbench should be scoped to a single super-admin role and expose all governance entry points: user management, permission management, system log, task management, demand management, messages, profile, and personal task/demand pages.
- Super admin local mock data should store role metadata, governance metrics, and the presentation flow.
- Add a unified role experience entrance at `demo/index.html` that links to requester, builder, operator, and super-admin demos.

## Phase 20 Requirements
- Treat the repository as a static prototype plus not-yet-initialized frontend/backend workspace.
- Correct documentation that points to non-existent paths such as `docs/prototype/demo/` and `docs/design-system/`.
- Document that `demo/index.html` is the current role-experience entry and that `demo/all-pages/index.html` is the full snapshot entry.
- Document the current development readiness state: no package manifests, no configured dev servers, and no database/API implementation yet.
- Add a development preparation guide that makes the next frontend/backend initialization steps explicit.
- Keep product source documents discoverable from `docs/README.md`.

## Phase 21 Requirements
- Use `docs/OpenRD协作平台PRD正式版.md` as the current authoritative product understanding source.
- Treat historical redundant docs under `docs/backup/` as archived reference material.
- Remember the project structure: this is one repository containing frontend and backend projects in their own folders: `frontend/` and `backend/`.
- Rewrite all README files in Chinese, including root, frontend, backend, docs, and backup README files that remain in the repository.
- Update README terminology to match the formal PRD: 需求者、共建者、产品经理、超级管理员.
- Capture that the product is composed of two connected systems: demand intake between requesters and product managers, and project collaboration between product managers and co-builders.

## Phase 22 Requirements
- Create a complete Chinese discussion/report document under `docs/`.
- Include the user's concerns: single-person dependency, handover risk, unstable volunteer participation, capability/time differences, and whether a close technical team affects openness.
- Include the user's ideas: lightweight governance organization, platform self-improvement tasks, resource/architecture/task-splitting/teaching capability centers, and SOP-first operation.
- Include the proposed solution: project management committee, capability centers, maintainer/reviewer model, contributor task pool, anti-single-point rules, and documentation-first handover.
- Include Phase 2 product design for a subtask system.
- Abstract the validated flow into a reusable open-source project development and operation SOP for future demand-to-task conversion and project delivery.

## Phase 23 Requirements
- Apply demo test feedback to task detail pages.
- Rename `任务说明与项目进度` to `项目进度`.
- Rename `需求来源与项目资源` to `任务信息与项目资源`.
- Replace `需求来源` display with task work-order fields from demand-to-task conversion.
- Update the edit modal to edit corresponding task information fields.
- Swap module order so `任务信息与项目资源` appears before `项目进度`, and `团队成员` follows after `项目进度`.
- Update active demo pages in `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`; keep `demo/backup/` as archive.

## Phase 24 Requirements
- Apply demo test feedback to demand detail pages.
- In the demand-to-task conversion modal, replace phase/subtask-like `任务类型` options with complete project-level categories.
- Add an `关联已有类似需求` action for product/operation-admin view.
- The new association modal should search converted root demands that are not themselves linked to another demand, then let the current demand point to that converted demand's task.
- After association, update demand status, conversion status, linked task id, feedback, timeline, and conversation system message.
- Preserve operator demo local-state synchronization.
- Update active demo pages in `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`; keep `demo/backup/` as archive.

## Phase 25 Requirements
- Continue P0 demand detail page feedback.
- Add attachment upload constraints in the communication area: quantity and size limits are required, file type/spec restrictions are not required yet.
- Add message revoke support in the communication area.
- Add a `查看` action for contact information.
- Contact details should remain masked by default; only product manager/operator and superadmin pages can reveal retained patient contact information.
- Update active demo pages in `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`; keep `demo/backup/` as archive.

## Phase 18 Active Optimization Notes
- Updated `demo/demand-detail.html` to use an operation-admin/product-manager processing model.
- Demand detail now presents multiple product manager evaluation cards instead of a generic chat stream.
- Primary hero action is now task conversion/view task rather than copying the demand ID.
- Conversion requires a product manager to claim the demand first; converted demands route to task detail.
- Added a conversion draft modal that copies demand context into a task work order.
- Revised `demo/demand-detail.html` again to match the corrected model: no separate claim step; the product manager who converts the demand becomes the owner.
- Added product/requester view switching in the hero area.
- Reworked the right-side area back into a communication zone with separate operation-admin/product-manager conversation threads.
- Swapped the main layout so the communication zone is the primary left area and demand information/timeline sit on the right.
- Refined the communication zone into a WeChat-like split panel with PM conversation list on the left and message stream/input on the right.
- Corrected the role visibility: product/operation-admin view only sees the current admin's own conversation, while requester view can see conversations from multiple admins.
- Product/operation-admin view exposes task conversion as the primary action; converting the demand represents that admin taking ownership.

## Decisions
- Planning files live in project root: `E:\MyCode\OpenRD`.
- External/web findings must go in `findings.md`, not this file.
- Continue updating `progress.md` after each implementation phase.
- `demo/index.html` is now the unified role experience entrance; `demo/all-pages/index.html` remains the full-page snapshot/collection entry.
- For Phase 20, do not assume runnable frontend/backend projects exist until package/config files are added.
- New and edited markdown documentation should be UTF-8; PowerShell reads existing Chinese docs correctly when `-Encoding UTF8` is used.
- From Phase 21 onward, all README files should be written in Chinese.
- Current project structure convention: one repository, with frontend and backend code stored under `frontend/` and `backend/` respectively.
- `docs/OpenRD协作平台PRD正式版.md` is the current primary PRD; `docs/backup/` contains archived historical documents.

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| `git status --short` failed because `E:\MyCode\OpenRD` is not a Git repository | 1 | Treat workspace as non-git static project; avoid relying on git diff/status for change tracking. |
| PowerShell parsed an `rg` pattern incorrectly because of embedded double quotes and pipes | 1 | Re-ran searches with single-quoted regex patterns. |
| PowerShell parsed JavaScript regex passed to `node -e` while checking DOM references | 1 | Re-ran the check using PowerShell-native regex extraction instead. |
| `rg` failed while searching `demo/index.html` because PowerShell/regex quoting stripped the intended `href=\"` pattern | 1 | Use simpler `Select-String` or single-purpose patterns for documentation validation. |
| Bulk task-detail update script failed because Chinese text with curly quotes was used inside PowerShell quoted hash keys | 1 | Reworked replacements to use here-strings and object pairs. |
| Bulk task-detail update script failed because `-replace` expressions inside method arguments were parsed as extra `.Replace()` parameters | 2 | Moved replacement strings into variables before calling `.Replace()`. |
