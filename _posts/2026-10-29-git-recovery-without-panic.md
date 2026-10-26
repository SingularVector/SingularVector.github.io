---
title: "Git Recovery Without Panic"
date: 2026-10-28
categories:
  - git
  - version-control
tags:
  - git
  - recovery
  - troubleshooting
  - version-control
description: "Undo Git changes with confidence: choose restore, revert or reset, and use reflog to find commits after a mistake, with practical examples and diagrams."
---

> In the [previous article]({{ '/git/version-control/git-fetch-vs-pull-vs-push/' | relative_url }}), we shared commits between repositories. Now let’s deal with the moment you realise one of those changes was not quite the improvement you had in mind.

You stage the wrong configuration value, commit something that fails its first test, or run a reset and suddenly become very interested in whether Git has an undo button.

The temptation is to search for “*undo last Git change*” and try the first or shortest answer. We have all been there :)

But an unstaged edit, a staged file and a commit your colleagues have already pulled are different situations. Before choosing a command, ask: **what exactly am I undoing, and what do I want to keep?**

---

## First, Look at What You Have

```bash
git status
git diff
git diff --cached
git log --oneline --graph --decorate --all -10
```

`status` describes your branch and files. `diff` compares working files with the staging area; `diff --cached` compares the staging area with the current commit.

The log shows ten commits (`-10`) with short entries (`--oneline`), connections (`--graph`) and reference labels (`--decorate`). `--all` includes history reachable from local references, including remote-tracking branches. None of these commands contacts the remote.

Keep three places in mind:

- **Working tree:** files you are editing.
- **Staging area**, or index: versions prepared for the next commit.
- **`HEAD`:** normally refers to your checked-out branch and its current commit.

![Working files are staged in the index, then recorded in a commit. Restore can copy a staged file back to the working tree or HEAD back to the index.]({{ '/assets/images/git-recovery/working-tree-index-head.svg' | relative_url }})

*“Undo the file” is ambiguous until you know which version you want to recover.*

These examples assume no merge or rebase is in progress. If you intend to cancel one, use its corresponding `git merge --abort` or `git rebase --abort` operation first.

Before discarding work, save what you need. A branch preserves a commit, **not uncommitted edits**. Copy those elsewhere or save them deliberately; `git stash push -u` includes untracked files but excludes ignored files. Check what you actually saved.

---

## “I Staged the Wrong File”

You ran `git add logging.txt`, then realised the edit should not be in the next commit. Unstage it while keeping the working file:

```bash
git restore --staged -- logging.txt
git status
git diff -- logging.txt
```

`--staged` selects the index as the destination; its default source is `HEAD`. The working file stays untouched. The `--` separates options from paths.

In a repository with an existing commit, this also unstages a newly added file, leaving it on disk as untracked. You changed what is prepared for the next commit, which is all you wanted.

---

## “I Want to Throw Away This Uncommitted Edit”

Perhaps you changed `level=info` to `level=debug` for troubleshooting and want to discard it.

**The restore command below overwrites unstaged changes in the named tracked file.** Review them first:

```bash
git diff -- logging.txt
```

If those are the changes you want to discard:

```bash
git restore -- logging.txt
```

Plain `restore` copies from the index into the working tree. If you staged `level=warning` before editing again to `level=debug`, it restores `level=warning`, not the committed `level=info`.

To discard **both staged and unstaged changes** and restore the committed version:

```bash
git restore --source=HEAD --staged --worktree -- logging.txt
```

`--source=HEAD` chooses the commit; the other options select both destinations. Review both diffs first. A newly added path absent from `HEAD` can be removed from disk by this operation.

The reflog is not an undo history for your editor. Do not rely on it to recover discarded, uncommitted work.

---

## “That Commit Was Wrong, and I Already Shared It”

Imagine commit `C` enabled debug logging across a shared environment. Useful for the investigation, less useful once the logs start growing with enthusiasm... and without control.

Use `git revert` to record a correction while keeping the shared **history** intact. Start with a clean working tree and inspect the commit:

```bash
git log --oneline -5
git show c3d4e5f
```

Replace `c3d4e5f` with the actual hash of the ordinary, single-parent commit you want to undo:

```bash
git revert c3d4e5f
```

Git reverses that commit’s change in a **new commit**. If it opens an editor for the message, save and close it to finish.

![Revert adds a new commit R after C to reverse C's change. Reset moves a local branch back to B, leaving C outside that branch's history.]({{ '/assets/images/git-recovery/revert-vs-reset.svg' | relative_url }})

*Revert records the correction. Reset changes where the branch points.*

Revert does not restore the entire project to its state before `C`. Later changes remain except where the inverse change affects them, which can cause conflicts.

If it conflicts, inspect `git status`, resolve the files, review and test, then stage the resolved paths and run `git revert --continue`. To cancel an in-progress revert, use `git revert --abort`.

Afterwards, test and share the correction through the project’s normal process. Reverting a merge commit also requires choosing a mainline parent; that needs a separate explanation before using it.

---

## “I Want to Redo My Last Local Commit”

If your latest commit is **unshared**, you can move your branch back while keeping the work to commit differently.

These alternatives assume a checked-out branch, a clean working tree and a latest commit with a parent. **Choose one; do not run them in sequence.** First preserve the current commit:

```bash
git branch backup/before-reset
```

Use a fresh backup name if needed. It preserves the commit, not uncommitted edits.

### Keep the Changes Staged

```bash
git reset --soft HEAD~1
```

`HEAD~1` selects the current commit’s first parent. `--soft` moves your branch there, leaving the index and working files untouched. From our clean starting state, the undone commit’s changes are staged for another commit.

### Keep the Working Changes, but Unstage Them

Alternatively, from the same original state:

```bash
git reset --mixed HEAD~1
```

The branch moves and the index resets to the target; working files stay untouched, ready to stage in smaller pieces. Files introduced by the undone commit may become untracked. `--mixed` is the default for this form of reset.

### Discard the Changes as Well

```bash
git reset --hard HEAD~1
```

**This resets the branch, index and tracked working files to the target. It can discard uncommitted tracked edits and remove untracked paths that obstruct writing the target’s files.**

The word *hard* is doing actual work here. It is not the choice for keeping your work and improving the commit.

| Mode | Branch | Index | Working files |
| --- | --- | --- | --- |
| `--soft` | Moves to target | Unchanged | Unchanged |
| `--mixed` | Moves to target | Reset to target | Unchanged |
| `--hard` | Moves to target | Reset to target | Tracked files reset; obstructing untracked paths can be removed |

This table describes `git reset MODE COMMIT`, without paths. For unstaging individual files, use the earlier `restore --staged` example.

Resetting locally does not remove a shared commit from the remote. Making the remote match may require rewriting shared history; for an ordinary shared mistake, prefer a revert.

---

## “I Reset the Branch, and Now My Commit Is Gone”

Gone from the branch does not necessarily mean gone from the repository. That is where the (hi)story gets interesting.

The **reflog** records local reference movements. To see the ten latest entries for `HEAD`, with local timestamps:

```bash
git reflog --date=local -10
```

After a reset, you might see:

```text
b2c3d4e HEAD@{Mon Oct 26 14:10:00 2026}: reset: moving to HEAD~1
c3d4e5f HEAD@{Mon Oct 26 14:05:00 2026}: commit: Enable debug logging
```

The older entry identifies the displaced commit. Inspect it, then preserve it with a branch name, substituting your actual hash:

```bash
git show c3d4e5f
git branch rescue/logging c3d4e5f
```

![Find an earlier commit hash in the local reflog, inspect it with git show, then create rescue/logging pointing to that commit.]({{ '/assets/images/git-recovery/reflog-rescue.svg' | relative_url }})

*Put a name on the commit first. Decide how to integrate it afterwards.*

Creating the branch neither switches branches nor overwrites working files. Once your working tree is clean, `git switch rescue/logging` lets you inspect the recovered work there.

I prefer this to immediately running another reset. With a name on the commit, there is less pressure to fix everything with the next command.

Reflogs are local, are not pushed, and do not travel with a fresh clone. Entries expire and unreachable objects can eventually be removed. **Recover promptly; this is not a backup policy.** A displaced commit may be recoverable; uncommitted edits overwritten by a hard reset may not be.

---

## Try It Somewhere That Does Not Matter

Practise in a new, empty directory, with your Git author identity already configured:

```bash
git init
```

Create `logging.txt` containing `level=info`, then:

```bash
git add logging.txt
git commit -m "Add logging configuration"
```

Change it to `level=debug` and commit again:

```bash
git add logging.txt
git commit -m "Enable debug logging"
git log --oneline -2
```

Copy the latest commit hash. Now move back while keeping the edit:

```bash
git reset --mixed HEAD~1
git status
git diff -- logging.txt
git reflog -5
```

The branch points to the earlier commit; `level=debug` remains as an unstaged edit. Name the displaced commit using your copied hash:

```bash
git branch rescue/logging c3d4e5f
git show rescue/logging:logging.txt
```

The last command reads the file from that commit without checking it out. It should show `level=debug` too.

You have kept the edit and recovered a name for the commit. No hard reset required, and no important repository volunteered for the demonstration.

---

## Choose the Operation That Matches the Problem

| What do you want to do? | Starting point |
| --- | --- |
| Unstage a file while keeping edits | `git restore --staged -- file` |
| Discard unstaged edits to a tracked file | Review, then `git restore -- file` |
| Undo an ordinary shared commit | `git revert COMMIT` |
| Redo an unshared last commit, keeping changes staged | `git reset --soft HEAD~1` |
| Redo it with working files preserved but changes unstaged | `git reset --mixed HEAD~1` |
| Find and inspect a displaced commit | `git reflog`, then `git show COMMIT` |
| Preserve that commit without switching branches | `git branch rescue/name COMMIT` |

Replace `file` and `COMMIT` with your intended path or hash, and check your starting state before choosing.

---

## What’s Next?

Start by finding what still exists. Preserve the useful work, choose the smallest operation that solves the problem, and inspect the result.

You do not need to become fearless around Git. Knowing where to pause is a more useful skill.

Next, [Why Is Git Asking for an Upstream?]({{ '/git/version-control/why-is-git-asking-for-an-upstream/' | relative_url }}) looks at the relationships behind a plain `pull` or `push`.

### Further Reading

- [Git restore documentation](https://git-scm.com/docs/git-restore)
- [Git revert documentation](https://git-scm.com/docs/git-revert)
- [Git reset documentation](https://git-scm.com/docs/git-reset)
- [Git reflog documentation](https://git-scm.com/docs/git-reflog)
- [Reset demystified in Pro Git](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified)
