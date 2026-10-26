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

> In the [previous article]({{ '/git/version-control/git-fetch-vs-pull-vs-push/' | relative_url }}), we looked at sharing commits between repositories. This time, let’s deal with the moment you realise one of those changes was not quite the improvement you had in mind.

You edit a configuration file, stage it, and then notice the wrong value. Or you commit a change that looked perfectly reasonable until you actually test it. Perhaps you run a reset, look at the history, and suddenly become very interested in whether Git has an undo button.

The temptation is to search for “*undo last Git change*” and try the first or shortest answer. We all have been there :)

The difficulty is that *change* can mean several different things. An edit in your working files, a staged version, a local commit and a commit your colleagues have already pulled are different situations. They deserve different operations.

Before reaching for a command, ask: **what exactly am I undoing, and what do I want to keep?**

That question will get us further than memorising four commands and hoping we choose the right one under pressure.

---

## First, Look at What You Have

Start with:

```bash
git status
git diff
git diff --cached
git log --oneline --graph --decorate --all -10
```

`git status` tells you about your branch and the state of your files. `git diff` compares your working files with the staging area; `git diff --cached` compares the staging area with the current commit.

The log gives you a compact picture of the history: `--oneline` shortens each entry, `--graph` draws the connections, `--decorate` adds reference labels, and `--all` includes history reachable from local references, including remote-tracking branches. `-10` limits the output to ten commits. None of these commands contacts the remote.

Three places matter for the examples below:

- **Working tree:** the files you are editing.
- **Staging area**, also called the index: the versions prepared for your next commit.
- **`HEAD`:** normally a reference to your checked-out branch, which points to its current commit.

![Working files are staged in the index, then recorded in a commit. Restore can copy a staged file back to the working tree or HEAD back to the index.]({{ '/assets/images/git-recovery/working-tree-index-head.svg' | relative_url }})

*“Undo the file” is ambiguous until you know which version you want to recover.*

If Git says a merge or rebase is already in progress, deal with that operation first. Use `git merge --abort` or `git rebase --abort` when you intend to cancel it; the examples here assume neither is in progress.

Before an operation that might discard work, copy anything you need outside the repository, or save it deliberately. A temporary commit on a separate branch can preserve tracked work; `git stash push -u` can save tracked changes and untracked files, but excludes ignored files. Check what you have saved rather than treating any of these as a universal backup.

---

## “I Staged the Wrong File”

Suppose you edited `logging.txt` and staged it:

```bash
git add logging.txt
```

Then you realise it should not be in the next commit. Keep the edit, but remove it from the staging area:

```bash
git restore --staged -- logging.txt
git status
git diff -- logging.txt
```

Here, `--staged` selects the staging area as the destination. The default source for that operation is `HEAD`, so the staged version is reset to the committed version. Your working file stays as it is.

The `--` separates options from file paths. It makes it explicit that `logging.txt` is a path to operate on.

This also works for a newly added file in a repository that already has a commit: unstaging it leaves the file on disk as untracked.

Nothing has been deleted. You have changed what is prepared for the next commit, which is all you wanted to do.

---

## “I Want to Throw Away This Uncommitted Edit”

Perhaps you changed `level=info` to `level=debug` while troubleshooting and now want to discard that edit.

**The next command overwrites the unstaged changes in the named tracked file.** Inspect them first:

```bash
git diff -- logging.txt
```

If those are the changes you want to discard:

```bash
git restore -- logging.txt
```

With no source or destination options, `restore` copies the file from the staging area into the working tree. If you have not staged a different version, that usually means returning it to the committed content.

But suppose you staged `level=warning`, then edited the file again to say `level=debug`. A plain `git restore -- logging.txt` takes the working file back to the staged `level=warning`, not the committed `level=info`.

That distinction is worth understanding before the command becomes muscle memory.

To discard **both staged and unstaged changes** to this tracked file and return both versions to `HEAD`:

```bash
git restore --source=HEAD --staged --worktree -- logging.txt
```

`--source=HEAD` chooses the committed version; `--staged` and `--worktree` select both destinations. Review both diffs first, because this replaces both versions. If the path was newly added and is absent from `HEAD`, restoring both destinations can remove it from disk as well.

The reflog does not record every edit you make in an editor. If you discard work that was never committed or otherwise saved, it is not a reliable way to get that work back.

---

## “That Commit Was Wrong, and I Already Shared It”

Imagine that commit `C` enabled debug logging across a shared environment. Useful for the investigation, less useful once the logs start growing with enthusiasm... and without control.

The commit is already on the shared branch. You want to undo its change while keeping a **history** that your colleagues can follow.

This is a good use for `git revert`.

Start with a clean working tree, find the commit, and inspect it:

```bash
git log --oneline -5
git show c3d4e5f
```

`c3d4e5f` is an example hash: replace it with the actual hash of the ordinary, single-parent commit you intend to undo. Then run:

```bash
git revert c3d4e5f
```

Git applies the inverse of that commit’s change and records it in a **new commit**. It may open your editor for the commit message. Save and close the editor to finish.

![Revert adds a new commit R after C to reverse C's change. Reset moves a local branch back to B, leaving C outside that branch's history.]({{ '/assets/images/git-recovery/revert-vs-reset.svg' | relative_url }})

*Revert records the correction. Reset changes where the branch points. Those are different decisions.*

Revert does not simply replace your whole project with the snapshot before `C`. Later changes remain, except where reversing `C` affects them. If those changes overlap, the revert can conflict.

When that happens, inspect `git status`, resolve the conflicted files, review and test the result, then stage the resolved paths and run:

```bash
git revert --continue
```

To cancel an in-progress revert instead:

```bash
git revert --abort
```

After a successful revert, test the result and share it through the project’s normal process, whether that means a pull request or a permitted direct push.

Reverting a merge commit needs an additional decision about its mainline parent. That deserves its own example; do not apply the simple command above to a merge commit without understanding that choice.

---

## “I Want to Redo My Last Local Commit”

Now consider a different situation. Your latest commit has **not been shared**, and you want to split it into two better commits. You want to keep the work, just change how you recorded it.

This is where a branch-moving `git reset` can help.

The following alternatives assume you are on a branch, the latest commit has a parent, and the working tree is clean. They are separate choices, not a sequence to run one after another.

First, give the current commit another name:

```bash
git branch backup/before-reset
```

Choose another backup name if that one already exists. This preserves a reference to the current commit; it does **not** save uncommitted edits.

### Keep the Changes Staged

```bash
git reset --soft HEAD~1
```

`HEAD~1` means the first parent of the current commit. For our simple linear history, that is the preceding commit.

`--soft` moves the current branch back to that commit and leaves the staging area and working files untouched. With our clean starting state, the undone commit’s changes are now staged, ready to commit again.

### Keep the Changes, but Unstage Them

As an alternative, starting from the same original state:

```bash
git reset --mixed HEAD~1
```

This moves the branch back and resets the staging area to the target commit, while leaving the working files alone. The changes are available to review and stage in smaller pieces. Files introduced by the undone commit may now appear as untracked.

`--mixed` is the default mode for this form of reset, but writing it out makes the intention easier to see.

### Discard the Changes as Well

There is also:

```bash
git reset --hard HEAD~1
```

**This moves the branch and resets both the staging area and tracked working files to the target commit. It can discard uncommitted tracked changes and delete untracked files or directories that obstruct writing the target’s tracked files.**

It is not the command to choose when you want to keep the work and improve the commit. The word *hard* is doing actual work here.

| Mode | Current branch | Staging area | Working files |
| --- | --- | --- | --- |
| `--soft` | Moves to target | Left alone | Left alone |
| `--mixed` | Moves to target | Reset to target | Left alone |
| `--hard` | Moves to target | Reset to target | Reset tracked files to target; obstructing untracked paths can be removed |

These descriptions apply to `git reset MODE COMMIT`, without file paths. The path-based form of reset has different behaviour; for unstaging a file, we used `git restore --staged` earlier.

If the commit is already shared, moving your local branch back does not remove it from the remote. Trying to make the remote match can require rewriting shared history. For an ordinary shared mistake, a revert is usually the more appropriate correction.

---

## “I Reset the Branch, and Now My Commit Is Gone”

Gone from the branch history does not necessarily mean gone from the repository. That is where the (hi)story, pun not intended, gets interesting.

Git’s **reflog** records local reference movements. It can help you find a commit after a reset, rebase or other operation moved a reference away from it.

Run:

```bash
git reflog --date=local -10
```

This shows the ten most recent entries for `HEAD`, with local timestamps. After a simple reset, you might see:

```text
b2c3d4e HEAD@{Mon Oct 26 14:10:00 2026}: reset: moving to HEAD~1
c3d4e5f HEAD@{Mon Oct 26 14:05:00 2026}: commit: Enable debug logging
```

Your timestamps and hashes will differ. The hash at the start of each entry identifies the position recorded by that movement. Here, the older entry points to the commit we want to inspect:

```bash
git show c3d4e5f
```

Once you have confirmed it is the right commit, give it a branch name:

```bash
git branch rescue/logging c3d4e5f
```

![Find an earlier commit hash in the local reflog, inspect it with git show, then create rescue/logging pointing to that commit.]({{ '/assets/images/git-recovery/reflog-rescue.svg' | relative_url }})

*Put a name on the commit first. You can decide how to integrate the recovered work afterwards.*

Creating the rescue branch does not switch branches or overwrite your current working files. When you are ready, and your working tree is clean, you can inspect it on that branch:

```bash
git switch rescue/logging
```

I prefer this approach to immediately running another reset. Once the commit has a branch name, there is less pressure to solve everything with the next command.

### What the Reflog Cannot Promise

Reflogs belong to the local repository. They are not pushed to GitHub or your git server, and a fresh clone does not contain the reflog from your other machine.

Entries also expire, and unreachable objects can eventually be removed by maintenance tasks. Default expiry periods are commonly 90 days for reachable entries and 30 days for unreachable entries, but configuration and maintenance can change what is available. *Treat recovery as something to attempt promptly, not a backup policy.*

Most importantly, a reflog entry points to a recorded commit position. It is not a recording of your editor session. A commit displaced by reset may be recoverable; unstaged edits overwritten by a hard reset may not be.

---

## Try It Somewhere That Does Not Matter

Reading about recovery is useful. Seeing the result in a disposable repository is better, especially before you need it in a production one.

In a new, empty directory, initialise a repository. These commands assume Git already has your author name and email configured:

```bash
git init
```

Create `logging.txt` in your editor containing `level=info`, then commit it:

```bash
git add logging.txt
git commit -m "Add logging configuration"
```

Change the file to `level=debug` and commit again:

```bash
git add logging.txt
git commit -m "Enable debug logging"
git log --oneline -2
```

Copy the hash of the latest commit somewhere handy. Now move back while keeping the edit:

```bash
git reset --mixed HEAD~1
git status
git diff -- logging.txt
git reflog -5
```

The file still contains `level=debug`. The branch points to the earlier commit, and the debug change is now unstaged.

Create a rescue branch using the hash you copied, replacing the example below:

```bash
git branch rescue/logging c3d4e5f
git show rescue/logging:logging.txt
```

The last command reads the file from the rescued commit without checking it out. You should see `level=debug` there as well.

You have moved the branch, kept the working edit and recovered a name for the displaced commit. No hard reset required, and no important repository volunteered for the demonstration.

---

## Choose the Operation That Matches the Problem

| What do you want to do? | Starting point |
| --- | --- |
| Unstage a file while keeping its edits | `git restore --staged -- file` |
| Discard unstaged edits to a tracked file | Review the diff, then `git restore -- file` |
| Undo an ordinary shared commit with a new commit | `git revert COMMIT` |
| Redo an unshared last commit, keeping changes staged | `git reset --soft HEAD~1` |
| Redo an unshared last commit, keeping working files | `git reset --mixed HEAD~1` |
| Find a displaced local commit | `git reflog`, then `git show COMMIT` |
| Preserve a recovered commit without switching branches | `git branch rescue/name COMMIT` |

The table is a reminder of the choices, not a substitute for checking your starting state. Replace `file` and `COMMIT` with the path or commit you actually intend to use.

---

## What’s Next?

Git gives us several ways to undo work because there are several different things we might mean by undoing it. Once you separate the working files, the staged version and the recorded history, the commands become much easier to reason about.

When something goes wrong, start by finding out what still exists. Preserve the useful work, choose the smallest operation that solves the problem, and inspect the result before moving on.

You do not need to become fearless around Git. Knowing where to pause is a more useful skill.

Next, we will take a closer look at `origin`, remote-tracking branches and upstream relationships: why a branch can exist in several places, and how Git decides where a plain `pull` or `push` should go.

### Further Reading

- [Git restore documentation](https://git-scm.com/docs/git-restore)
- [Git revert documentation](https://git-scm.com/docs/git-revert)
- [Git reset documentation](https://git-scm.com/docs/git-reset)
- [Git reflog documentation](https://git-scm.com/docs/git-reflog)
- [Reset demystified in Pro Git](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified)
