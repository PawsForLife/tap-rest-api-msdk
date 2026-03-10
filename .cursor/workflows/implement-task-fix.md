# Implement Single Bug Fix Task

Implement one task from the bug fix pipeline. Invoked once per task with a fresh agent context. The plan is pre-created by the architect in the per-task planning phase. For features, use `implement-task-feature.md` instead. For full bug fix implementation, use `implement-fix.md`.

## Regression Rules (MANDATORY)

- **Regression is not acceptable.** Failing tests that are not explicitly marked as expected failures (e.g., `@pytest.mark.xfail`, `@unittest.expectedFailure`) are regressions and must be fixed before the task is considered complete.
- **Expected failures are acceptable.** Tests annotated with framework-level expected-failure markers are excluded from the regression gate. Do not remove or alter these markers without explicit user approval.
- **Do not claim tests are unrelated.** If a test fails after your changes, it is your responsibility to fix it. You may not dismiss failing tests as "unrelated" or "pre-existing" without explicit user confirmation.
- **Full test suite requirement:** Before marking a task complete, run the full test suite for affected component(s). All tests must pass (excluding expected failures).

## Prerequisites

- Task document exists in `{bugs_dir}/{bug_name}/tasks/{task_file}.md`
- Task plan exists in `{bugs_dir}/{bug_name}/plans/tasks/{task_file}.md` (created by architect)
- User provides: bug name, task file name (e.g. `01-add-regression-test.md`)

## Instructions

Execute these phases in order. Focus only on this single task.

## Completion Checklist

**Check off each item as you complete it.**

**Phase 1: Context Gathering**
- [ ] Step 1.1: Read relevant codebase context from `{context_docs_dir}/`
- [ ] Step 1.2: Read root `CHANGELOG.md` (or create if it doesn't exist)
- [ ] Step 1.3: Read task document and task plan
- [ ] Step 1.4: Read `{scratchpad}` for context
- [ ] Step 1.5: Identified affected component(s)

**Phase 2: Implementation**
- [ ] Step 2.1: Wrote tests first (TDD), regression tests when feasible
- [ ] Step 2.2: Verified tests FAIL before implementation
- [ ] Step 2.3: Implemented code changes following the approved plan
- [ ] Step 2.4: Ran project code quality tools and fixed issues
- [ ] Step 2.5: Ran full test suite and verified all tests PASS (no regressions)
- [ ] Step 2.6: Completed validation steps from plan (reproduction, regression)

**Phase 3: Completion**
- [ ] Step 3.1: Updated root `CHANGELOG.md` under `## [Unreleased]` in `### Fixed`
- [ ] Step 3.2: Updated relevant documentation in `{context_docs_dir}/` and READMEs (if applicable)
- [ ] Step 3.3: Archived task and plan files to `{archive_dir}/fix-{bug_name}/`
- [ ] Step 3.4: Ran full test suite again; all tests passed
- [ ] Step 3.5: Verified no code quality errors remain
- [ ] Step 3.6: Updated `{scratchpad}` with "Task {task_file} completed, tests passing"

---

## Phase 1: Context Gathering

### Step 1.1: Read Codebase Context

Read relevant files from `{context_docs_dir}/` based on task scope:
- **Always read**: AI_CONTEXT_QUICK_REFERENCE.md, AI_CONTEXT_REPOSITORY.md
- **If affecting specific components**: Read the corresponding component context files in `{context_docs_dir}/`
- **Always read**: AI_CONTEXT_PATTERNS.md

### Step 1.2: Read Changelog

Read root `CHANGELOG.md` (create if it doesn't exist). Understand recent changes and changelog format.

### Step 1.3: Read Task and Plan

1. Read the task from `{bugs_dir}/{bug_name}/tasks/{task_file}.md`
2. Read the plan from `{bugs_dir}/{bug_name}/plans/tasks/{task_file}.md`
3. If the plan seems incomplete, request the architect to update it before proceeding

### Step 1.4: Read Scratchpad

Read `{scratchpad}` for bug name, pipeline state, and prior task completions.

### Step 1.5: Analyze Scope

Determine which service(s) or component(s) are affected based on the task and plan.

---

## Phase 2: Implementation

Follow the TDD workflow. Run the project's test suite and code quality tools as defined in project rules; reference `@.cursor/workflows/implement-feature.md` for the full workflow.

Emphasize:
- Regression tests that reproduce the bug before fix
- Validation steps from `{bugs_dir}/{bug_name}/plans/master/validation.md`
- Black box testing - validate functionality, not internal behavior

### Step 2.1: Write Tests First

Create or update tests per the task plan's Test Strategy. Prioritize regression tests when feasible.

### Step 2.2: Verify Tests Fail

Run tests and verify they FAIL before implementation. If they pass, adjust tests until they correctly validate expected behavior and fail.

### Step 2.3: Implement Code Changes

Implement following the plan's Implementation Order. Follow component-specific patterns from AI_CONTEXT_PATTERNS.md.

### Step 2.4: Run Code Quality Tools

Run the project's code quality tools and fix any issues.

### Step 2.5: Run Full Test Suite

Run the **full** test suite for affected component(s). **All tests must pass (excluding expected failures).** Any failing test not explicitly marked as an expected failure is a regression and must be fixed before proceeding. Do not claim failures are "unrelated" to your changes.

### Step 2.6: Validation

Complete validation steps from `{bugs_dir}/{bug_name}/plans/master/validation.md` to confirm fix and prevent regression.

---

## Phase 3: Completion

### Step 3.1: Update Changelog

Add entry under `### Fixed` in `## [Unreleased]`:

```markdown
### Fixed
- Brief description of the bug fix
  - Plan: [task-name]({archive_dir}/fix-{bug_name}/plans/tasks/{task_file})
  - Task: [task-name]({archive_dir}/fix-{bug_name}/tasks/{task_file})
```

### Step 3.2: Update Documentation

Update relevant files in `{context_docs_dir}/` and component READMEs based on what changed.

### Step 3.3: Archive Task and Plan

Move task and plan to archive:

```
mkdir -p {archive_dir}/fix-{bug_name}/tasks
mkdir -p {archive_dir}/fix-{bug_name}/plans/tasks
mv {bugs_dir}/{bug_name}/tasks/{task_file} {archive_dir}/fix-{bug_name}/tasks/
mv {bugs_dir}/{bug_name}/plans/tasks/{task_file} {archive_dir}/fix-{bug_name}/plans/tasks/
```

### Step 3.4: Final Validation

Run full test suite again. All tests must pass. Verify no code quality errors.

### Step 3.5: Update Scratchpad

Add to `{scratchpad}`: "Task {task_file} completed, tests passing"

---

## Notes

- This workflow is invoked **once per task** with a fresh agent context
- Do not proceed to the next task until this task is fully complete and all tests pass
- The plan was created by the architect in the per-task planning phase; do not create a new plan
- Archive path uses `fix-` prefix: `{archive_dir}/fix-{bug_name}/`
