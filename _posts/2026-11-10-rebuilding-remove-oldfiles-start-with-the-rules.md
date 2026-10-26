---
title: "Rebuilding Remove-OldFiles: Start with the Rules"
date: 2026-11-10
categories:
  - PowerShell
  - DevOps
tags:
  - automation
  - retention
  - PowerShell
  - engineering
  - Remove-OldFiles
description: "Revisit a real PowerShell cleanup project: separate retention policies from execution, define protected folders and make the rules explicit before rebuilding."
---

In [From a Script to a Tool]({% post_url 2026-11-07-from-a-script-to-a-tool %}), we looked at what changes when someone else needs to depend on your script: clear inputs, usable results, meaningful failures and tests for the behaviour you promise.

Now let’s put that into practice with a solution I actually used.

Back in [2018 (time flies...), I wrote about deleting old files with PowerShell]({% post_url 2018-12-27-PowerShell-Delete-Files-Older-Than-Days %}). The example grew into [Remove-OldFiles](https://github.com/SingularVector/Remove-Old-Files), used at a previous company to clean up logs from different automations and support other teams with similar needs. Different locations had different retention rules. A central CSV described them, with ignore markers and exception notifications around the execution.

The files were not the difficult part. The rules were.

“Delete old files” sounded like one job, until you asked whose files, how old, and which folders absolutely needed to be left alone. The original solution handled a useful operational problem; revisiting it gives us a chance to keep that value while questioning how the implementation expresses those decisions.

I had already considered moving the configuration into a database. We will come back to that, but first I want to answer a simpler question: **can we explain and test exactly what one cleanup policy means?**

This is where the rebuild starts. There will be code, but first there are a few promises to make—and a few old assumptions for me to revisit :)

---

## What Was Worth Keeping?

The useful design decision was putting policy outside the code. One row could keep logs for 90 days; another could keep exported files for seven. Supporting a different team did not require another copy of the script with another hard-coded path.

The CSV described four things: where to look, which extension to match, how many days to retain, and whether to recurse. A file named `ignore` offered a local way to protect a folder.

Those ideas still make sense. CSV is also easy to inspect and edit. Replacing it with a database will be useful when we need ownership, policy revisions and execution history, not simply because the project is older than some of the files it was supposed to remove.

---

## Read the Behaviour, Not Just the Comments

Reviewing the current repository exposed a few mismatches:

- The documented recursion value `0` is nonempty, and the implementation treats every nonempty value as enabled.
- Recursive ignore handling compares exact parent directories, so a protected folder’s deeper descendants are not reliably protected.
- Deletion counters can advance after nonterminating errors because the operation does not explicitly stop on error.
- The description talks about creation time, while selection uses last-write time.

There is also a mismatch between logging call sites and the embedded helper’s parameter names in the checked-in version. The logging function has evolved too; [New-LogEntry Revisited]({% post_url 2026-10-24-PowerShell-New-LogEntry-Revised %}) explains the current version, rather than assuming the embedded copy is interchangeable. These are findings from reading today’s source, not a reconstruction of every revision or local adjustment used historically.

The point of this exercise is to turn those observations into explicit behaviour and checks. Rewriting the same assumptions in cleaner code would not be much of an improvement.

---

## Decide What the Engine Promises

The [behaviour specification](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/retention-engine-specification.md) defines a deliberately small first milestone: **accept one policy, inspect its scope, and report eligible files without deleting anything**.

Its rules include:

- Last-write time in UTC, compared against one cutoff captured for the run. Exactly at the cutoff means not eligible.
- Explicit Boolean recursion and enabled settings. The string `"0"` is not an acceptable substitute for a Boolean.
- An `ignore` file protects its containing directory and the entire subtree. The walker does not enter that subtree just to count what it skipped.
- Links and reparse points are not followed; linked roots and ancestors are rejected too.
- A failed or incomplete inspection cannot masquerade as a successful empty result.

![Define the retention policy, inspect and report, verify the results, then add controlled execution. Central storage follows stable behaviour.]({{ '/assets/images/retention-rebuild/rebuild-stages.svg' | relative_url }})

*First make the selection explainable. Deletion and central management can build on that behaviour afterwards.*

There are tradeoffs here. Rejecting linked ancestors can also reject a convenient path alias. Including hidden files makes scope broader than a default directory listing. Both choices need documentation and tests, neither should be discovered during a cleanup run. Trust me you do not want to deal with that :)

---

## Keep the First Milestone Small

The original script remains in the repository. The rebuilt module sits alongside it and has no deletion command. That lets us examine policy validation, exclusions, boundaries and failure reporting without attaching a real cleanup action to the first iteration.

Next comes a CSV importer that translates the old fields into the new policy model. It must report defaults, reject invalid values and make broad matching explicit. Compatibility should preserve useful configuration, not accidentally preserve a bug.

Controlled deletion follows once we trust selection. Central policy storage and execution history come later, with decisions about ownership, workers and unavailable configuration before we pick a database.

It is less dramatic than unveiling a complete platform. It is also a better chance of ending up with something we can explain.

Next in the rebuild: the report-only engine, the tests that shaped it, and why “nothing found” must be different from “could not look.”

### Further Reading

- [Original Remove-OldFiles repository](https://github.com/SingularVector/Remove-Old-Files)
- [Behaviour specification](https://github.com/SingularVector/Remove-Old-Files/blob/main/docs/retention-engine-specification.md)
- [From a Script to a Tool]({% post_url 2026-11-07-from-a-script-to-a-tool %})
