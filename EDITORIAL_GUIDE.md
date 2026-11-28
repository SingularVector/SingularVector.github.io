# SingularVector: editorial and maintenance guide

This is the portable guide for writing and maintaining Daniele's SingularVector technical blog. Use it with the latest article files and repository state. It records durable preferences, not proof that a project has shipped or a service is currently working.

## What the blog is for

SingularVector is an engineering notebook: practical work around infrastructure, systems and automation—guides, troubleshooting notes, tools and configurations built around real problems.

The author brings substantial professional systems and automation experience. Linux study notes or experiments with a new tool do not make him an engineering beginner. Keep that distinction in introductions, biographies and project narratives.

The defining editorial rule is: **human text in my style, no repetition and no posting for the sake of it.**

A post should leave the reader able to explain a behaviour, solve a problem, make a better decision or try a useful experiment. A longer archive is not an objective by itself.

## Voice and prose

- Sound like an experienced colleague walking through something worth understanding. Use concrete situations and plain English.
- Start close to the problem: the script someone else needs to run, an ambiguous report, an unexpected command result, a configuration choice with consequences. Avoid broad openings about the importance of technology or automation.
- Use first person for supplied experience and genuine author judgements. Make invented examples explicitly hypothetical. Do not create autobiographical details to make an opening livelier.
- Explain what changed, why it mattered and what the result tells us. Keep the technical detail needed to understand the decision; move reference material to the source or documentation.
- Let a little humour arise from the situation. A small aside or occasional `:)` can fit. Do not sprinkle jokes, emojis or forced friendliness through every section.
- Keep useful personal additions when proofreading. Correct spelling and clarity without polishing all the author's character out of the text.
- Shorten by removing repeated setup, redundant examples, unused options and material already explained elsewhere. Preserve the important concept and the reason behind the choice.
- Prefer connected paragraphs. Use headings, tables and lists when they help readers navigate or compare; avoid turning every paragraph into a slogan or every article into the same checklist.
- Avoid marketing vocabulary, generic praise, exaggerated claims, clickbait and formulaic wrap-ups. A clear ending can state what the reader can now do, what remains uncertain, or why the design is sufficient.

### Primary voice references: the author's earlier writing

Use Daniele's original older posts as the primary prose references. Before drafting, read at least two relevant samples below. The current versions of several old posts were substantially revised later; an old publication date alone does not make today's wording an untouched author sample.

The original-source links below are pinned to repository revision `7292b79c401eb331b18d883aead84386c973ea2a` (24 October 2021), before the recent editorial rewrites. They preserve the historical wording. Use their voice and explanatory habits, while checking technical claims against current documentation and implementation.

| Original post | What to learn from it |
| --- | --- |
| [PowerShell string concatenation](https://github.com/SingularVector/singularvector.github.io/blob/7292b79c401eb331b18d883aead84386c973ea2a/_posts/2020-07-18-PowerShell-String-Concatenation.md) | Begin with something the author repeatedly does at work, explain the practical cost, demonstrate a better approach, and let a small joke interrupt the technical explanation naturally. |
| [Setup an internal PowerShell Repository with NuGet Step by Step](https://github.com/SingularVector/singularvector.github.io/blob/7292b79c401eb331b18d883aead84386c973ea2a/_posts/2021-06-02-Setup-Internal-PowerShell-Repository.md) | Connect a deployment walkthrough to how the author and colleagues distribute their own modules. Address the reader directly and allow a modest, self-deprecating aside. |
| [PowerShell — Command Splatting](https://github.com/SingularVector/singularvector.github.io/blob/7292b79c401eb331b18d883aead84386c973ea2a/_posts/2019-01-12-PowerShell-Command-Splatting.md) | Start with code the author often encounters, ask how to make it easier to read, then build the improvement in small steps before discussing a real pitfall. |
| [PowerShell delete old files](https://github.com/SingularVector/singularvector.github.io/blob/7292b79c401eb331b18d883aead84386c973ea2a/_posts/2018-12-27-PowerShell-Delete-Files-Older-Than-Days.md) | Move from a concrete operational need to scope questions and a small example. Make the motivation understandable before introducing the implementation. |
| [Back from a long holiday](https://github.com/SingularVector/singularvector.github.io/blob/7292b79c401eb331b18d883aead84386c973ea2a/_posts/2019-08-24-Back.md) | Hear the unguarded personal voice: candid, warm and plainly enthusiastic about writing and sharing useful work. Use this for personality, not as the structure of a technical guide. |

With a local checkout, the same historical source is available using `git show REVISION:_posts/FILENAME.md`, substituting the revision above and the chosen filename. Do not restore those historical files over the maintained articles.

### Voice cues carried with an uploaded copy

These short, verbatim excerpts keep some of the author's actual cadence available when this guide is uploaded without the repository:

From the original string-concatenation post:

> Many times when writing a PowerShell script I find myself manipulating lot of strings, for example appending *html* code to a notification mail body, to build what the final value I want to be.

And, immediately after an explanation of immutable strings:

> *TLTR* **It's magic.**
>
> I am just joking of course but we can easily benchmark the above statement with a code similar the following:

From the original internal-repository walkthrough:

> Once this is done go to _Build / Build Solution_ menu, or press F6 if you're lazy like me, to _package_ together all files making up the solution.

The pattern to carry forward is **a real reason to care, a direct explanation, a practical example and occasional understated personality**. Do not mechanically reuse the jokes, reproduce spelling/grammar mistakes, imitate old code formatting or preserve obsolete technical advice. Correct the language gently while keeping the author recognisable. Do not make every paragraph a punchline or replace his explanations with polished slogans.

### Secondary references: current article presentation

The following newer articles illustrate the current length, illustrations, backlinks and structure. They are secondary presentation references; do not use them to displace the original author samples when choosing the voice.

- [From a Script to a Tool](_posts/2026-11-07-from-a-script-to-a-tool.md): handover, practical consequences and restrained humour.
- [Git Recovery Without Panic](_posts/2026-10-29-git-recovery-without-panic.md): explain the decision before presenting commands.
- [A SQL Table, Not a Platform](_posts/2026-11-14-remove-oldfiles-when-a-report-becomes-a-delete.md): engineering judgement, scope reduction and a natural stopping point.

## Decide whether an article is worth writing

Before drafting, read the nearest existing posts and identify the new reader value in one sentence. If that sentence is mainly “another update on the same work”, reconsider.

For an ongoing project, publish when a milestone yields a worthwhile lesson: a design choice, a revealing failure, an operational result or a change in understanding. Several small fixes belong in the repository history and documentation. They do not each need an article.

For lab or study material, work from the supplied notes and actual experiments. Do not invent results or expand a chapter summary just to produce a post. A failed experiment can be useful when its conditions and evidence are clear.

For overlapping subjects, give each article a distinct job. Explain only what its reader needs, then link naturally to the fuller treatment. Close a series when its useful story is complete; do not attach an unrelated teaser to keep it going.

If new material is not ready, say so. Waiting for lab evidence is a valid editorial decision.

## Technical credibility

Use the current code repository as the source of truth. Check what a function or command actually does before describing its options or output. Link to maintained source, requirements and migration notes; distinguish version-specific examples from today's repository state.

Prefer official documentation and original sources for changing or specialised claims. Do not treat a search snippet, a successful package install or a previous conversation as proof of behaviour.

Examples must name their environment and assumptions where those affect the outcome. Explain consequential commands, defaults and output. Use disposable paths and data for exercises that change files. Never present an example as safe merely because it is short or familiar.

Record what was actually verified. A parser check is not an execution test; local mocks are not a Windows/SQL acceptance run; a build is not deployment; an HTTP response is not evidence of Google indexing. Avoid frozen test-count snapshots in narrative posts when a maintained verification document would serve readers better.

Use meaningful comments and readable formatting in code: four spaces, braces on separate lines, aligned PowerShell splats, blank lines between logical steps and straightforward control flow. Prefer `switch` over lengthy `if`/`elseif` chains where appropriate. Keep long implementations out of the article body and link to the companion file or repository.

## Illustrations and references

Use a diagram when it explains a relationship, flow, boundary or before/after state more clearly than prose. Prefer editable SVGs for technical illustrations and the existing restrained palette. Keep labels readable, include alt text and inspect the rendered image.

Screenshots must represent the current implementation. Label mock reports and synthetic data honestly. Update or remove an obsolete visual when the design changes.

Use links where they help the reader continue: a previous explanation, the implementation, official documentation or a prerequisite. A short Further Reading list is useful when it adds something; link volume is not a goal.

## Drafts and publication

Draft first unless the user explicitly requests publication preparation. Use the requested location, or `_drafts/` by default. If a draft lives under `_posts/`, keep `published: false` until the user approves scheduling or publication.

An approved scheduled article uses `YYYY-MM-DD-descriptive-slug.md` and the same date in front matter. Preserve requested dates. Follow the site's existing build/deployment process rather than creating a new scheduling service or task.

Publication dates use Europe/Zurich. The repository's Pages workflow rebuilds daily and deploys only validated output from master; a future date becomes eligible during a build, rather than triggering one itself. Keep `published: false` until scheduling is approved. See README.md for the daily schedule and fresh manual runs; do not create separate per-article automations.

Preserve an existing article's filename, categories, permalink and canonical URL during editorial changes. On this site categories can affect the URL. Do not rename old posts or change domains to make wording look tidier. Update modification dates only for actual substantive revisions, not as a freshness trick.

The user normally handles commits, pushes and Jekyll builds. Leave work ready for review, state what was checked, and do not claim it is published until deployment is verified. Perform those actions only when explicitly requested for the current task.

## Maintain discovery without adding noise

The repository's [README](README.md) documents the exact data fields and files. Verify the current implementation before modifying them.

### From the workbench

Set `featured: true` in a post to make it eligible. Optional `feature_title` and `feature_description` provide short card copy; otherwise the article supplies it. The first category determines the topic used for the mix.

Select useful, accurate, self-contained guides across topics. Older articles can qualify. Do not automatically feature everything new, entire project diaries or material that needs another instalment to make sense. Retire a selection by removing the marker or setting it to `false`.

Preserve the daily UTC rotation, a stable selection on refresh, no duplicate cards and working links without JavaScript. Published availability must remain a condition for inclusion.

### Reading paths and series panels

`_data/reading_paths.yml` stores an ordered list of article filenames without `.md`, short step descriptions and relevant topic IDs. The first topic supplies the series panel's destination.

A path should answer a reader's practical question and provide a sensible order. Keep each article in one primary path so its panel has a clear home. Do not add a path just because several posts share a tag.

Topic pages introduce the path; articles show their place in it. Drafts, hidden posts and future posts must not leak into either. Resolve available posts dynamically instead of creating `post_url` references to unavailable targets. Keep the ordinary archive available below the curated paths.

### Code & tools

`_data/tools.yml` connects a tool or runnable companion to its source and explanatory article. A card appears when its companion article is published. Keep requirements, compatibility boundaries and release-candidate status accurate; check the repository before claiming a stable release.

The source repository remains authoritative. A downloadable snapshot or a sample report does not replace it. Do not duplicate entire implementations into this index.

### RSS, comments and sharing

Use the existing `/feed.xml` feed and RSS invitation for subscriptions. Do not add a newsletter service or another external dependency without a concrete need and an explicit request.

Comments use giscus with GitHub Discussions. Check the actual configuration and installation rather than assuming that a successful build establishes working comments. Keep the site's description of enabled services accurate.

Sharing previews use article-specific header imagery when supplied, or the branded fallback. Keep the editable SVG and exported PNG consistent, ensure metadata uses an actual image URL, and preserve page-specific titles, descriptions and canonical URLs. Do not introduce a build-time image generator merely to maintain a small static fallback.

## Traffic and search

Improve useful entry points, clear titles, explanatory internal links and relevant next-reading suggestions. Avoid publishing filler, keyword stuffing, artificial modification dates or cosmetic changes presented as ranking improvements.

Preserve working URLs and redirects. Treat old-brand searches as evidence of recognition, not proof that a name caused or prevented traffic. Use current Search Console queries and landing-page evidence before diagnosing visibility or proposing a migration. A processed sitemap, an indexed article, search impressions and site visits are different observations.

No feature or article can guarantee traffic. Report the evidence and practical limits without turning each update into an SEO checklist.

## Reusing this guide in another chat

For repository work, keep `AGENTS.md` and this guide with the checkout. For a chat without repository access, upload this file and explicitly ask the assistant to follow it for SingularVector work. Supply the current draft, relevant existing posts or source code when the task depends on them; this document does not contain their full contents.

A ChatGPT Project can keep the guide alongside related chats and project instructions. Use a short project instruction such as: “For SingularVector articles and maintenance, read and follow the attached EDITORIAL_GUIDE.md. Preserve my voice, check existing coverage, and leave publication and commits to me unless I explicitly request otherwise.”

Repository files remain the master copies. Uploaded copies do not automatically update when Git changes; replace the project/chat attachment after revising the guide.
