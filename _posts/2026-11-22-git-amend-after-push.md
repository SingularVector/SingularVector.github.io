---
title: "Git Amend After Push: Fix the Last Commit and Run CI Again"
date: 2026-11-22
categories:
  - git
  - version-control
tags:
  - git
  - commits
  - GitHub Actions
  - troubleshooting
description: "Fix a forgotten file or README typo with git commit --amend, update a pushed branch using an explicit lease, and understand when GitHub Actions runs again."
toc: true
---

You commit, push, and open GitHub. Everything looks good.

Then you notice the missing file. Or the README sentence that would benefit from the comma you left somewhere between the keyboard and the commit.

You could add another commit called `Fix typo`, followed by `Actually fix typo`. Git would happily record both. Sometimes, though, you want the correction included in the change you just made, with the pipeline checking the corrected version.

That is a useful job for **`git commit --amend`**.

In [Git Recovery Without Panic]({% post_url 2026-10-29-git-recovery-without-panic %}), we looked at undoing and recovering work. Here, we will replace the latest commit, including the extra step needed when it has already been pushed.

## One Commit in the History, a New Commit ID

Amending does not edit the original commit object. It creates a replacement commit and moves the current branch to it. For our ordinary, non-merge example, both versions have the same parent:

```text
Before:       A---B       local branch and remote branch

After amend:  A---B       remote branch
               \
                B'       local branch, including the correction
```

`B'` has a different commit ID. After the remote branch accepts the replacement, its history ends at `B'` too. There is still one commit after `A` on that branch.

The old commit can remain in other clones, reflogs or references. Rewriting a branch is not a way to erase a leaked secret; exposed credentials need rotation.

## Decide Whether This Branch Is Yours to Rewrite

This walkthrough assumes you are correcting the **latest commit on your own feature branch**, it has not been merged, and nobody is building work on top of it. There is no merge or rebase in progress.

For a shared branch, coordinate first or add a normal correction commit. A one-character fix is still a history rewrite if you amend a published commit.

GitHub [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) can block force pushes. If the server rejects the rewrite because of a rule, use the repository's normal review process. A cleaner-looking log is not a reason to turn off protection on `main` or `master`.

The examples use `feature/readme` on `origin`. Substitute your own branch and remote names.

## Check the Starting Point

Before editing, start with a clean working tree and inspect the destination:

```bash
git switch feature/readme
git status
git remote -v
git fetch origin
git rev-parse HEAD origin/feature/readme
```

For this already-pushed example, the last command must print **the same full commit ID twice**. If the IDs differ, stop and inspect the history before using this sequence. Your local and remote branches are not at the same starting point.

Record that original commit with a local backup branch:

```bash
git branch backup/before-amend
```

Use a fresh backup name if this one exists, and use that same name in the push command below. This reference preserves the original commit; it does not save uncommitted files.

## Add the Missing Change to the Last Commit

Make the correction. In this example, fix `README.md` and add the forgotten `examples/settings.json` file, then review and stage them:

```bash
git diff -- README.md
git status --short
git add -- README.md examples/settings.json
git diff --cached
git commit --amend --no-edit
git show --stat --oneline HEAD
git status
```

Review the new file's contents before staging it too: an untracked file does not appear in a plain `git diff`.

The amend uses the staged snapshot. Check the whole staged diff so an unrelated change does not come along for the ride. Naming files deliberately also avoids the enthusiastic reach of `git add .`.

[`--no-edit`](https://git-scm.com/docs/git-commit) keeps the existing commit message. To revise the message as well, use `git commit --amend` instead; Git opens the editor. These are alternatives, not two commands to run consecutively.

Amend replaces only the current tip. Correcting an older commit while keeping later work needs a different workflow, usually an interactive rebase.

If the commit had **never been pushed**, an ordinary push would be enough. The next section is for replacing the version already on the remote.

## Push the Replacement with an Explicit Lease

A normal push will usually reject this update as non-fast-forward: the new tip does not descend from the old one.

Use this command for our example:

```bash
git push --force-with-lease=refs/heads/feature/readme:backup/before-amend origin HEAD:refs/heads/feature/readme
```

Read it as: update remote `feature/readme` to my current `HEAD`, **only if that remote branch still points to the original commit saved in `backup/before-amend`**.

The [Git push documentation](https://git-scm.com/docs/git-push) describes this explicit expected-value form. It avoids relying on a remote-tracking reference that an editor's background fetch can update. The shorter `--force-with-lease` uses those remote-tracking references instead.

If somebody pushes another commit while you are editing, the explicit lease rejects your update. Stop, fetch and review their work. Keep the backup reference at the original commit while investigating; moving it just to make the command pass defeats the check.

The lease checks the remote branch tip. It cannot tell you whether another person has already fetched the old commit and started working locally. That is why the branch ownership assumption still matters.

## Will This Run the Pipeline Again?

The push updates the remote branch to the corrected commit. GitHub Actions can start a new run when the configured event and filters match. A force push does not override those filters.

For example, this workflow listens for pushes to our example branch:

```yaml
on:
  push:
    branches:
      - feature/readme
```

Treat this as the trigger section of an existing workflow, not a complete workflow file.

Check the actual [workflow triggers](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), including branch and path filters. A README correction will not run a workflow restricted to changes under `src/**`. A workflow configured only for pull requests also needs a matching pull request event.

Because we preserved the commit message, any existing [skip instruction](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs), such as `[skip ci]`, is preserved too. Remove it deliberately if you want the affected push or pull request workflow to run.

In the Actions page, verify that the new run refers to the amended commit ID. A green check for the earlier commit has not checked your correction.

## If Nothing Changed, Rerun the Existing Workflow

Sometimes the commit is already correct and a build failed because a dependency download or external service had a bad moment.

In that case, open the existing run under **Actions** and choose **Re-run all jobs** or **Re-run failed jobs**, as appropriate. You need write permission, and GitHub allows reruns within 30 days of the initial run.

A [rerun uses the original event's commit SHA and ref](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs). It does not pick up your later amended commit. Use it when you want to retry the same revision; check the new push's run when you want to test changed files.

There is no need to manufacture a history change just to ask CI to try again.

## Verify What GitHub Received

After a successful amended push:

```bash
git fetch origin
git rev-parse HEAD origin/feature/readme
git log --oneline -3 origin/feature/readme
```

The two IDs should match again. Inspect the updated files on GitHub and the workflow run for that ID.

You have kept the correction with the change it belongs to, and checked the version that will actually be reviewed or deployed.

The comma can finally relax.
