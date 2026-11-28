# SingularVector blog: working instructions

These instructions apply throughout this repository. Before writing, revising or planning articles, read [EDITORIAL_GUIDE.md](EDITORIAL_GUIDE.md). Before changing site features, also read the maintenance sections at the top of [README.md](README.md). Follow the user's current request when it changes a standing preference.

## Source of truth and scope

- This is the SingularVector GitHub Pages blog. The checkout's historical directory name does not define the site's identity. Verify the current Git root, remote, configuration and working-tree state before editing.
- Work in the repository. ZIP files, screenshots and snippets are derived outputs; they do not establish that an implementation has changed.
- Preserve unrelated work and user edits. Read the actual article and relevant implementation before describing either. Do not rely on a previous chat's snapshot for current project status.
- Keep changes focused. Prefer the existing theme, data files and static-site capabilities over new services, dependencies or infrastructure.
- Do not commit, push, deploy or publish unless the user explicitly authorises that specific action for the current task. This applies to every change, including configuration, workflows and documentation. Requests to implement, fix or prepare changes do not authorise a commit; leave changes uncommitted for the user to review. Permission to commit does not by itself authorise pushing, deploying or publishing.

## Editorial essentials

- Write as Daniele: an experienced systems and infrastructure engineer. Preserve the established senior positioning; do not describe him as starting over or pivoting into engineering. Verify any numeric experience claim against the current site copy.
- Human text in his style, no repetition and no posting for the sake of it. Lead with a concrete problem, engineering decision or useful experiment; explain consequences and tradeoffs.
- Keep the prose conversational and concise, with restrained humour. Avoid dry manual-like inventories, marketing language, generic introductions and manufactured enthusiasm.
- Make difficult concepts easy to grasp. Introduce one idea at a time, start with the simplest useful example, and explain unfamiliar commands, options and syntax before expecting the reader to use them. Do not assume that an experienced engineer already knows a particular utility. Avoid adding secondary concepts or defensive settings that distract from the lesson; split complex commands into readable steps and keep short utility articles focused on one clear takeaway.
- Never invent personal experience, incidents, employers, tests, results or project maturity. Use a clearly hypothetical example when actual experience is not supplied.
- Use the original older author-written samples identified in `EDITORIAL_GUIDE.md` as the primary voice references; later revised articles are secondary presentation examples. Read related published posts before drafting, link to existing explanations and preserve useful proofreading additions when shortening.
- New project posts need a distinct lesson or meaningful milestone. If lab testing only confirms the design, update existing material instead of inventing another instalment.

## Publication and links

- Default new work to an unpublished draft. Follow an explicitly requested file location; otherwise use `_drafts/`. A draft stored in `_posts/` must have `published: false` until scheduling/publication is authorised.
- For approved dated posts, use the existing `YYYY-MM-DD-descriptive-slug.md` convention and matching front-matter date in Europe/Zurich. The existing Pages workflow rebuilds daily; use that workflow for publishing rather than creating separate per-article tasks. See README.md for manual dispatch and deployment checks.
- Preserve published filenames, categories, permalinks and canonical URLs unless changing them is explicitly in scope. These fields can define URLs. Topic labels can be improved without recategorising old posts.
- Use `relative_url` for local assets and site links. Only use `post_url` when the target is available in that build; future/draft references need publication-aware resolution.
- Do not imply that renamed, dated or locally prepared files have been deployed. Distinguish a successful build, live deployment, crawling and indexing.

## Code and visuals

- Prefer readable examples: four spaces, no tabs; braces on their own lines, including single-statement blocks; aligned equals signs in PowerShell splats/hashtables; blank lines between logical steps; comments explaining decisions and non-obvious behaviour. Prefer `switch` over chained `if`/`elseif` where it improves clarity.
- Prefer splatted PowerShell commands, especially when passing several parameters. Use descriptive splat names, aligned equals signs and one parameter per line so calls are easy to read and maintain.
- Readability is a primary requirement. Comment code generously to explain its purpose, logical steps, assumptions and decisions, including in article examples and companion scripts. Keep comments useful and accurate as the code changes; favour clarity over clever shortcuts or compressed code.
- Keep examples short in the article. Put long runnable companions under `assets/code/` or link to the maintained source repository.
- Use informative SVG diagrams when they clarify a concept. Match the restrained site palette, provide useful alt text and inspect the rendered result. Do not add decorative images just to fill space.

## Maintenance and verification

- Homepage selections use `featured`, optional `feature_title`/`feature_description`, `_includes/home-featured.html` and `assets/js/home-featured.js`. Preserve the daily topic mix, stable selection on refresh and working static fallback.
- Reading paths use `_data/reading_paths.yml`; tools use `_data/tools.yml`. Keep source filenames correct, companion links useful and draft/future/hidden content excluded. Avoid unnecessary parallel paths or automatically promoting every new post.
- RSS uses the existing feed. Comments use the configured giscus integration. Sharing previews use article overrides or the branded fallback. Verify current configuration before changing any of these; keep descriptions of enabled services accurate.
- For article work, check metadata, filename/date agreement for new scheduled files, links, assets, code fences and relevant examples. Verify technical claims against current primary sources or the actual implementation; state the limits of local testing.
- For code/template changes, run targeted behaviour and rendering checks, including empty and unpublished-content cases where relevant. Do not add tests that merely duplicate trivial implementation details.
- The user handles normal Jekyll builds. Do not install build dependencies or run a full build for routine content edits unless requested. If a build is requested, use the repository's configured tooling and checks; do not replace its dependency set. Report targeted checks separately from full build/CI status.
- Run `git diff --check`, inspect the final diff/status and report changed files with material limitations. Leave existing URLs and redirects stable while improving discovery. Never promise rankings, indexing or traffic gains.

Keep `AGENTS.md` and `EDITORIAL_GUIDE.md` excluded from the generated site. Update these instructions when the user explicitly changes a durable convention; do not turn them into a transcript or dated progress log.
