# Progress

## 2026-05-26
- Initialized planning-with-files workflow in project root.
- Created `task_plan.md`, `findings.md`, and `progress.md`.
- Captured current demo file inventory and important implementation notes.

## 2026-05-26 — Community Homepage
- Started Phase 2: create community homepage demo with navigation, stats, and task/demand hall tabs.

- Created demo/home.html.
- Implemented top nav with logo, request/workbench actions, hover profile card.
- Implemented task/user metrics and task/demand hall tabs.
- Verified inline script syntax with Node.

- Adjusted demo/home.html: made .top-nav sticky at the top and compressed summary/stat cards to reduce vertical height.

- Updated demo/home.html: changed top nav to fixed full-width bar occupying the top edge; added page top offset for content.

- Updated demo/home.html: added .top-nav-inner so fixed full-width top nav background spans the viewport while nav content aligns to the 1460px main content area.

## 2026-05-26 — Demand Modal
- Started Phase 3: add demand submission modal to demo/home.html.

- Completed Phase 3 demand modal in demo/home.html.
- Added open/close modal behavior, overlay click close, Esc close, validation, drag/drop file name display, loading submit, and toast feedback.
- Verified inline script syntax with Node.

## 2026-05-26 — Workbench Demo
- Started Phase 4: create role-based workbench demo page.

- Completed Phase 4 workbench demo in demo/workbench.html.
- Implemented fixed top navigation, role switcher, dynamic information cards, dynamic function tiles, and tile toast interaction.
- Verified inline script syntax with Node.

## 2026-05-26 — User Management Demo
- Started Phase 5: create standalone user management demo page with editable table and modal.
- Added phone to the field set and plan to keep UUID immutable while registration time remains read-only.
- Completed Phase 5 user management demo in demo/user-management.html.
- Implemented fixed top navigation, summary cards, searchable user table, editable modal, phone field, read-only UUID/registration time, password show/hide, and save toast.
- Verified inline script syntax with Node.

## 2026-05-26 — Permission Management Demo
- Completed Phase 6 permission management demo in demo/permission-management.html.
- Implemented fixed top navigation, permission summary cards, searchable/filterable member table, role permission templates, grouped manual permission grants, locked inherited permissions, risk badges, and save toast.
- Verified inline script syntax with Node.

## 2026-05-26 — System Log Demo
- Completed Phase 7 system log demo in demo/system-log.html.
- Implemented fixed top navigation, super-admin-only visual label, summary cards, searchable/filterable audit table, log detail modal, risk/result badges, and export toast.
- Verified inline script syntax with Node.

## 2026-05-26 — My Tasks and Task Detail Demo
- Completed Phase 8 my tasks and shared task detail demos in demo/my-tasks.html and demo/task-detail.html.
- Implemented fixed top navigation, personal task summary cards, status tabs, search/status filters, task hall-style rows, detail links, shared task detail rendering, milestones, team members, demand source, attachments, and toast feedback.
- Verified inline script syntax for both pages with Node.

## 2026-05-27 — Unified Top Navigation
- Completed Phase 9 top navigation unification across all topnav-based demo pages.
- Reused the community homepage platform brand, demand/workbench actions, and hover profile card in workbench, user management, permission management, system log, my tasks, and task detail pages.
- Verified inline script syntax for all affected pages with Node.

## 2026-05-27 — My Demands Demo
- Completed Phase 10 my demands demo in demo/my-demands.html.
- Implemented unified top navigation, demand summary cards, lifecycle tabs, search/status filters, demand list rows, status/conversion badges, progress display, and future-detail toast.
- Verified inline script syntax with Node.

## 2026-05-27 — Profile Demo
- Completed Phase 11 profile demo in demo/profile.html.
- Implemented unified top navigation, profile display, base and extended fields, editable modal, read-only platform ID, identity selector, region selector, skill tag add/remove, six-tag limit, and save toast.
- Verified inline script syntax with Node.

## 2026-05-27 — Message Center Demo
- Completed Phase 12 message center demo in demo/message-center.html.
- Implemented unified top navigation, message summary cards, category sidebar, searchable message list, unread-only filter, unread counters, mark read, mark all read, delete, detail drawer, and toast feedback.
- Verified inline script syntax with Node.

## 2026-05-27 — Team Detail Demo
- Completed Phase 13 team detail demo in demo/team-detail.html.
- Implemented unified top navigation, task-bound team rendering via URL task parameter, captain-oriented overview, members, applications, assignments, timeline, empty state, and toast action feedback.
- Verified inline script syntax with Node.

## 2026-05-27 — Demand Detail Demo
- Completed Phase 14 demand detail demo in demo/demand-detail.html.
- Implemented unified top navigation, demand detail rendering via URL demand ID, left-side lifecycle information, right-side operations/publisher conversation, message sending, simulated attachment supplement, copy demand ID, and empty state.
- Updated demo/my-demands.html detail links to open demand-detail.html and verified inline script syntax for both pages with Node.

## 2026-05-27 — Task and Demand Management Demo
- Started Phase 15 to add admin-style task management and demand management pages.
- Added demo/task-management.html with unified top navigation, task summary stats, filters, table, edit modal, simulated saving, and export toast.
- Added demo/demand-management.html with unified top navigation, demand lifecycle stats, filters, table, edit modal, simulated saving, and export toast.
- Updated demo/workbench.html management tiles so task management and demand management open the new demo pages.

## 2026-05-27 — Demo Collection and Entry Logic
- Started Phase 16 to make all demos easier to present as a connected prototype set.
- Added demo/index.html as the complete demo collection hub with recommended presentation flow and categorized page cards.
- Connected auth flow transitions from login/register/forgot-password/account-onboarding to their next demo pages.
- Added task and demand detail buttons to the community homepage hall rows.
- Added details actions to task management and demand management tables while preserving edit modals.
- Added task detail links to team detail and demand detail, and added profile/message center tiles to workbench.
- Updated all topnav brand areas to link back to home and added logout links inside profile hover cards.

## 2026-06-03 — Task Detail Layout Refinement
- Started Phase 17 to improve task detail page layout and information hierarchy.
- Merged the hero area and info grid into one overview card in demo/task-detail.html.
- Added a task description/milestone edit button and moved team detail into the team members card.
- Rebuilt the lower content as one wide demand source and project resource card with attachments, resources, and collaboration actions.
- Verified demo/task-detail.html inline script syntax and layout markers with Node.
- Refined spacing, equal-height progress/team cards, scrollable project progress, resource-card demand detail/edit actions, and resource edit modal.
- Added more project progress entries and strengthened the scrollable milestone area with a bordered container, fade overlay, custom scrollbar, and scroll hint.
- Corrected the resource edit modal so demand source is read-only while project resources, attachments, and collaboration actions are editable.
- Re-ran all demo inline script syntax checks successfully after correcting a local validation command typo.

## 2026-06-04 — Project Understanding and Demo Optimization Baseline
- Used the planning-with-files workflow as requested and restored existing `task_plan.md`, `findings.md`, and `progress.md`.
- Confirmed the repository is a static demo workspace centered on `demo/` HTML pages and `doc/` product references.
- Confirmed `E:\MyCode\OpenRD` is not a Git repository, so future change tracking should rely on planning files and direct file inspection.
- Scanned page inventory and key route definitions across the demo hub, workbench, home, task detail, demand detail, task management, and demand management pages.
- Updated `task_plan.md` so Phases 15-17 are marked complete and Phase 18 tracks the ongoing goal: optimize the demo for presentation.
- Added a project understanding baseline to `findings.md` for future demo optimization turns.

## 2026-06-04 — Demand Detail PM Processing Optimization
- Updated `demo/demand-detail.html` according to the approved plan.
- Replaced the generic right-side chat panel with a product-manager processing desk: summary cards, multiple PM evaluation cards, claim actions, and publisher supplement card.
- Changed the hero action from copying the demand number to task conversion/view task behavior.
- Added claim-before-convert logic for in-progress demands and direct task navigation for already converted demands.
- Added a conversion work-order modal with source demand, owner, title, type, priority, scope, and acceptance fields.
- Reworked mock demand data from `chats` to structured `pmThreads`, `ownerPm`, `conversionReady`, and conversion task fields.
- Verified `demo/demand-detail.html` inline script syntax with Node.
- Verified script `querySelector('#id')` references resolve to existing DOM IDs.
- Verified old chat selectors and copy-demand button markers are no longer present.

## 2026-06-04 — Demand Detail Dual-View Conversation Correction
- Reworked `demo/demand-detail.html` after corrected product direction from the user.
- Removed the independent claim-before-convert interaction model from the page behavior.
- Added hero-level product/requester view switch buttons.
- Replaced the PM processing-card area with a communication zone using separate product-manager conversation threads.
- Updated mock data from `pmThreads`/`ownerPm` claim state to `threads`/`convertedBy` conversion ownership state.
- Product view can inspect PM conversations, send PM inquiries, and convert an information-sufficient thread into a task.
- Requester view can inspect all PM conversations, reply to the selected PM, and add a simulated attachment.
- Updated conversion modal owner field to represent the product manager performing conversion.
- Verified inline script syntax, DOM id references, and absence of old claim-flow markers.

## 2026-06-04 — Demand Detail WeChat-Style Layout
- Swapped `demo/demand-detail.html` main content order so the communication module is the left primary area and demand information/timeline are on the right.
- Reworked the communication module into a WeChat-like split panel with product-manager conversation list on the left and selected message stream/input on the right.
- Adjusted responsive behavior so the PM conversation list becomes a horizontal selector above the chat pane on narrower viewports.
- Removed unused legacy PM processing-card CSS selectors.
- Verified inline script syntax and DOM id references after the layout swap.

## 2026-06-04 — Demand Detail Layout Polish
- Refined `demo/demand-detail.html` after the user flagged the previous layout as visually weak.
- Reduced the card-stacking feel by making the communication area a single integrated IM workspace.
- Changed the right-side demand information area into a compact sticky sidebar with lighter cards and tighter spacing.
- Compressed the status cards and tuned the message list, thread list, bubbles, and input area for a more mature workbench feel.
- Re-verified inline script syntax and DOM id references.

## 2026-06-04 — Demand Detail Layout Reorder
- Reordered `demo/demand-detail.html` based on the user's corrected layout direction.
- The page now renders status cards first, then `需求信息` and `处理流程` panel cards side by side, then the full communication module below.
- Removed the left-chat/right-sidebar arrangement while preserving dual-view and multi-PM conversation behavior.
- Verified inline script syntax and DOM id references after reordering.
- Rechecked the current file after the latest instruction and confirmed the requested hierarchy is already present: `status-grid` first, then side-by-side `panel-card` sections for demand information and process flow, followed by the communication area below.

## 2026-06-04 — Demand Detail Operation-Admin Visibility
- Updated `demo/demand-detail.html` so product/operation-admin view only renders the current admin's own conversation thread.
- Kept requester view able to switch across multiple operation-admin conversations.
- Hid demand conversion actions from requester view and kept `转化任务` visible as the product/operation-admin primary action.
- Added copy explaining that the current admin can only view their own communication record.
- Verified inline script syntax and DOM id references after the interaction update.

## 2026-06-04 — Demand Detail Overview Header
- Merged the demand detail hero area and status cards into one `overview-card`, matching the top structure used by `demo/task-detail.html`.
- Moved the decorative grid treatment from the former standalone hero card onto the unified overview card.
- Kept the view switch, product-side conversion action, and four status cards inside the unified top card.
- Verified inline script syntax and DOM id references after the markup/CSS update.

## 2026-06-04 — Demand Conversion Demo Default
- Changed the default demand `REQ-2418` from converted to unconverted demo-ready state.
- Set its lifecycle to `沟通中 / 待转化`, cleared `convertedBy`, and set the related task display to `暂未生成`.
- Kept the current operation-admin thread information-sufficient with `canConvert: true` so the page can demonstrate converting a demand into a task immediately.
- Verified inline script syntax and DOM id references after the mock-data update.

## 2026-06-04 — Team Detail Overview And Lists
- Updated `demo/team-detail.html` so the hero area and status cards are merged into one `overview-card`, matching the demand/task detail direction.
- Added more pending join-application examples to the default team and updated the team timeline copy to match the larger application count.
- Added more default team members and wrapped the member list in a `member-scroll` container modeled after the task detail timeline scroll treatment.
- Verified inline script syntax and DOM id references after the layout and mock-data update.
- Fixed the entry-path issue where `TASK-1042` still had an empty `applications` array, so task-detail-to-team-detail demos showed no pending join applications.
- Added 3 pending application examples to `TASK-1042` and changed its status copy to `解决中 · 补充招募`.

## 2026-06-05 — Team Detail Scroll And Edit Modals
- Updated `demo/team-detail.html` so the join-application list also uses the same `member-scroll` style as the team member list.
- Added an invite-member modal opened by `邀请成员`, with editable invite target, role, platform ID, response date, and invite note fields.
- Added an assignment-adjustment modal opened by `调整分工`, with editable assignment rows for title, owner, deliverable, due date, and status.
- Switched team action handling to event delegation to avoid duplicate listeners after assignment re-rendering.
- Verified inline script syntax, DOM id references, and duplicate id checks after the update.
- Adjusted task assignment rows so their status tags align to the right and match the member-list status tag sizing.
- Added `增加分工` and per-row delete controls to the assignment adjustment modal using a draft assignment list before saving.
- Verified script syntax, DOM references, duplicate ids, and assignment mock-data status values after the add/delete update.

## 2026-06-05 — Requester Role Experience Demo
- Created `demo/all-pages/` and copied the current demo HTML pages into it as a full-page snapshot folder.
- Created `demo/requester/` and copied the requester-relevant flow pages into it, including post-conversion task/team tracking pages.
- Replaced `demo/requester/index.html` with a requester role welcome page that introduces OpenRD, defines the requester role, and routes to login.
- Added `demo/requester/local-data.js` for requester role metadata, flow steps, and demand summary state synchronized through `localStorage`.
- Scoped requester workbench to a single requester role and removed live links to admin-only pages.
- Updated requester login to route into `workbench.html` and adjusted current-user chrome/profile data to `陈北 · 需求者`.
- Set requester demand detail default view to `需求者视角`.
- Verified requester inline script syntax, internal href targets, local-data script load order, and absence of admin-page references.

## 2026-06-05 — Builder Role Experience Demo
- Created `demo/builder/` from the full-page snapshot in `demo/all-pages/`.
- Replaced `demo/builder/index.html` with a co-builder role welcome page that introduces OpenRD, defines the role, and routes to login.
- Added `demo/builder/local-data.js` for co-builder role metadata, flow steps, and task summary state synchronized through `localStorage`.
- Updated builder login to route into `workbench.html` and scoped the builder workbench to a single co-builder role.
- Removed live links to admin-only pages inside the builder role experience.
- Updated builder profile/current-user chrome to `林知行 · 共建者 · 后端开发`.
- Added local task summary overrides to `my-tasks.html` and synchronized saved team assignment edits back into builder local data.
- Verified builder inline script syntax, internal href targets, local-data script load order, and absence of admin-page references.
- Adjusted requester and builder role login pages so successful login enters `home.html` first, then users can navigate to role workbench or other flows from the community home page.

## 2026-06-05 — Demand Detail Hidden Message Scroll
- Updated demand detail message lists in `demo/all-pages/`, `demo/requester/`, and `demo/builder/` so the chat message area remains scrollable while hiding visible scrollbars.
- Added Firefox, legacy Edge/IE, and WebKit scrollbar hiding CSS for `.message-list`.
- Verified demand detail script syntax and DOM query references after the CSS-only sync.
- Fixed the surrounding conversation layout heights so `conversation-card`, `conversation-body`, and `chat-pane` no longer grow with content; the hidden-scroll `.message-list` now visibly acts as the scroll container.
- Corrected the height behavior after clarification: restored `conversation-card` and `conversation-body` to adaptive/min-height behavior and fixed only `.message-list` at 360px so messages scroll without expanding the outer card.

## 2026-06-05 — Operator Role Experience Demo
- Created and finalized `demo/operator/` as the operation admin/product manager role experience.
- Added `demo/operator/index.html` welcome page and `demo/operator/local-data.js` for role metadata, flow steps, demand state, and task state.
- Updated operator login so successful login enters `home.html` first.
- Scoped operator workbench to the operation/admin-product-manager experience while keeping demand management and task management as live entries.
- Updated operator chrome/profile data to `易然 · 运管 · 产品经理`.
- Set operator demand detail to product/operator view by default and kept the core `转化任务` action available.
- Adjusted operator local defaults so `REQ-2418` starts as `沟通中 / 待转化` and no converted task is preloaded.
- Synced demand conversion state into operator demand management and task management: before conversion the demand shows `暂未生成`, after conversion the generated task appears in task governance.
- Verified operator inline script syntax, internal href targets, local-data script load order, and default local data state.

## 2026-06-05 — Super Admin Role Experience Demo
- Created `demo/superadmin/` from the full-page snapshot in `demo/all-pages/`.
- Replaced `demo/superadmin/index.html` with a super-admin welcome page that introduces OpenRD, defines the role, and routes to login.
- Added `demo/superadmin/local-data.js` for super-admin role metadata, governance metrics, and presentation flow state.
- Updated super-admin chrome/profile data to `顾星河 · 超级管理员 · 平台治理负责人`.
- Scoped `demo/superadmin/workbench.html` to a single `超管体验` role and defaulted rendering to `superAdmin`.
- Kept all governance pages live in the super-admin folder, including user management, permission management, system log, task management, and demand management.
- Updated user management, permission management, and system log sample records so the super-admin account is `顾星河 / admin_guxinghe`.
- Verified super-admin inline script syntax, internal href targets, local-data defaults, and absence of old current-user role-switch residue.

## 2026-06-05 — Unified Role Entrance
- Added `demo/index.html` as a unified role experience entrance for requester, builder, operator, and super-admin demos.
- Included role cards, direct entry buttons, a recommended presentation order, and a secondary link to `demo/all-pages/index.html`.
- Verified `demo/index.html` script syntax and internal href targets.

## 2026-06-05 — Operator Permission Correction
- Updated the operator/product-manager permission model: operators no longer enter full task management or demand management pages.
- Changed `demo/operator/workbench.html` so the core operator entry is `需求沟通` pointing to `demand-detail.html?id=REQ-2418`.
- Removed unused task-management and demand-management tile definitions from operator workbench data.
- Replaced `demo/operator/task-management.html` and `demo/operator/demand-management.html` with permission-restricted fallback pages that explain only super admins can modify those management areas.
- Updated operator welcome/local-data flow copy to describe task-detail tracking after conversion rather than management-table access.

## 2026-06-08 — Documentation and Development Preparation
- Restored planning-with-files context and shifted the active goal from demo-only optimization to project documentation and development readiness.
- Confirmed the current project is not yet an initialized frontend/backend application: `frontend/` and `backend/` contain README placeholders only.
- Confirmed the current prototype entry is `demo/index.html`, with role-specific experiences under `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`.
- Confirmed product source documents are under `docs/` and should be read as UTF-8.
- Noted stale root README paths that need correction before development starts.
- Updated root `README.md` with the actual project status, demo entry, repository structure, product scope, and development direction.
- Added `DEVELOPMENT.md` with staged frontend/backend initialization decisions, first milestones, API contract preparation, and definition of ready.
- Updated `frontend/README.md` and `backend/README.md` to document placeholder status, responsibilities, and next setup decisions.
- Added `docs/README.md` as the product documentation map and corrected prototype reference to `../demo/`.
- Expanded `.env.example` with future shared, frontend, and backend environment variable placeholders.
- Validated all documented demo entries and product document paths exist.
- Confirmed stale paths `docs/prototype/demo/` and `docs/design-system/` are no longer present in the edited project docs.

## 2026-06-08 — Formal PRD README Rewrite
- Started Phase 21 after the user archived historical docs under `docs/backup/`.
- Read `docs/OpenRD协作平台PRD正式版.md` as the current formal PRD.
- Captured the updated role terminology: 需求者、共建者、产品经理、超级管理员.
- Captured the product model as two connected systems: demand intake/evaluation and project development collaboration.
- Captured the repository convention that frontend and backend live in separate `frontend/` and `backend/` folders inside one repository.
- Identified README files requiring Chinese rewrite: `README.md`, `frontend/README.md`, `backend/README.md`, and `docs/backup/README.md`.
- Rewrote `README.md` in Chinese around the formal PRD, current repo state, single-repo structure, role model, P0 scope, prototype entry, and development preparation.
- Rewrote `frontend/README.md` in Chinese with frontend status, PRD/prototype references, recommended stack, responsibilities, first milestone, and backend boundary.
- Rewrote `backend/README.md` in Chinese with backend status, PRD reference, responsibilities, core data tables, initialization decisions, first milestone, and frontend boundary.
- Restored/added `docs/README.md` in Chinese as the current formal documentation index.
- Rewrote `docs/backup/README.md` in Chinese as an archive notice.
- Verified README inventory now includes `README.md`, `frontend/README.md`, `backend/README.md`, `docs/README.md`, and `docs/backup/README.md`.
- Verified documented paths for the formal PRD, docs index, demo entries, frontend folder, backend folder, and backup folder exist.
- Verified stale English README section markers from the previous version are no longer present.

## 2026-06-08 — Open Collaboration Governance and SOP Document
- Started Phase 22 to summarize the user's operational concerns and governance ideas into a complete discussion document.
- Created `docs/OpenRD开源协作治理与SOP方案.md`.
- Documented the user's concerns around single-person dependency, handover risk, unstable contributors, ability/time differences, and the startup-team vs open-collaboration boundary.
- Documented the proposed governance model: project management committee, resource center, architecture center, task-splitting center, teaching/growth center, maintainer model, contributor task pool, and anti-single-point rules.
- Documented the platform self-bootstrapping idea: use OpenRD to manage OpenRD's own development.
- Added Phase 2 subtask-system design, including fields, states, difficulty levels, validation principles, and status flow.
- Added reusable SOP templates for demand intake, demand communication, task conversion, subtask splitting, contributor claiming, code review, acceptance, and handover/exit.
- Updated `docs/README.md` to include the new governance and SOP document.
- Updated `docs/OpenRD开源协作治理与SOP方案.md` with a staged governance evolution model.
- Added the idea that early projects should start with a small MVP承接团队 rather than a full management committee.
- Added the transition path where MVP developers gradually become project managers/maintainers after the MVP is validated.
- Added the principle that project owners should progressively delegate authority to the project management committee.

## 2026-06-09 — Task Detail Demo Feedback Adjustments
- Started Phase 23 for task detail page feedback from demo testing.
- Confirmed there is no root `demo/task-detail.html`; active task detail pages are in `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`.
- Kept `demo/backup/task-detail.html` unchanged as archive.
- Updated active task detail pages so `任务说明与项目进度` is now `项目进度`.
- Updated active task detail pages so `需求来源与项目资源` is now `任务信息与项目资源`.
- Replaced the old `需求来源` copy block with a structured `任务信息` field grid.
- Added task work-order data fields for each mock task: 来源需求、转化产品经理、任务类型、优先级、工单范围、验收标准.
- Updated the edit modal to edit task information fields and project resources; 来源需求 remains read-only.
- Reordered the content modules to show `任务信息与项目资源` first, followed by `项目进度`, then `团队成员`.
- Verified no active task detail page still contains the old labels or `demandSource` references.
- Verified inline script syntax with `node --check` for all five active task detail pages.

## 2026-06-09 — Demand Detail Demo Feedback Adjustments
- Started Phase 24 for demand detail page feedback from demo testing.
- Confirmed there is no root `demo/demand-detail.html`; active demand detail pages are in `demo/all-pages/`, `demo/requester/`, `demo/builder/`, `demo/operator/`, and `demo/superadmin/`.
- Kept `demo/backup/demand-detail.html` unchanged as archive.
- Updated the conversion modal field from `任务类型` to `项目分类`.
- Replaced phase/subtask-like conversion options with complete project categories: 工具开发项目、数据分析项目、内容/文档项目、流程优化项目、科研辅助项目、平台能力建设项目.
- Added `关联已有类似需求` action beside `转化任务` in product view.
- Added a similar-demand association modal with keyword search over converted root demand candidates.
- Implemented association behavior so the current demand can point to an existing converted demand's task instead of creating a duplicate task.
- Association updates demand status, conversion status, linked task id, platform feedback, timeline, and conversation system message.
- Preserved and extended operator local demo-state synchronization for associated demands.
- Verified old phase/subtask-like conversion options only remain in `demo/backup/demand-detail.html`.
- Verified inline script syntax with `node --check` for all five active demand detail pages.

## 2026-06-09 — Demand Detail P0 Interaction Adjustments
- Started Phase 25 for additional P0 demand detail feedback.
- Added attachment limit copy in the communication area:最多 5 个附件，单个不超过 20MB，格式不限.
- Reworked simulated attachment selection from a single pending file to a pending attachment list with count and size display.
- Added message revoke support; the current view can revoke messages sent by its own identity only.
- Revoked messages render as `该发言已撤回` and hide their attachment display.
- Added private contact fields to demand mock data while keeping the default contact display masked.
- Added a `查看` button in the contact field.
- Limited full contact reveal to operator/product-manager and superadmin role pages; requester, builder, and all-pages snapshots remain unauthorized.
- Verified inline script syntax with `node --check` for all five active demand detail pages.
- Reworked message revoke from a visible meta-row button into a custom right-click context menu on each message bubble.
- The message bubble context menu now supports `复制` and conditionally shows `撤回` only for messages owned by the current view identity.
- Verified inline script syntax again with `node --check` for all five active demand detail pages.

## 2026-06-09 — Detail Page Permission View Fixes
- Fixed demand detail view permissions so switching views no longer grants unauthorized operation rights.
- Demand detail pages now use three modes: 发布者视角、产品视角、只读.
- Requester demand detail defaults to 发布者视角 and can send communication replies only.
- Operator and superadmin demand detail default to 产品视角 and keep product conversion/linking permissions.
- Builder and all-pages demand detail default to 只读 and cannot send, convert, link, or reveal contact details.
- Added task detail view switch with three modes: 队长身份、共建者身份、只读.
- Task detail pages now update displayed role, current action, edit visibility, and submit-update visibility by selected mode.
- Default task detail modes: requester=只读, builder/all-pages=共建者身份, operator/superadmin=队长身份.
- Verified inline script syntax with `node --check` for all active demand detail and task detail pages.

## 2026-06-09 — Team Detail Permission View Fixes
- Added team detail permission modes: 队长视角、成员视角、只读.
- Team leader view can invite members, approve/reject join applications, and adjust task assignments.
- Member view can inspect members, applications, assignments, and timeline, but cannot manage the team.
- Read-only view hides management actions and shows applications as non-actionable records.
- Default team detail modes: requester=只读, builder/all-pages=成员视角, operator/superadmin=队长视角.
- Verified inline script syntax with `node --check` for all five active team detail pages.

## 2026-06-11 — Frontend Gitflow Planning Baseline
- Restored planning files and re-checked the current repository structure.
- Confirmed the repository now is a Git repo, but `frontend/` still has not been initialized as a runnable app.
- Read the root README, frontend README, formal PRD, API design doc, and demo-to-API mapping doc to extract frontend delivery scope.
- Confirmed current implementation reference pages live in `demo/all-pages/` plus role folders, while `frontend/` is the future product code location.
- Derived the recommended frontend task sequence for Gitflow-based team assignment: scaffold first, then shared shell/design system, then split into auth/account, demand lifecycle, task collaboration, personal center/message, and admin governance workstreams.
