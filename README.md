# qa-pipeline

QA-owned **mono repo** for AI-assisted mobile test automation (Claude Code + Maestro). One framework,
many apps. App code stays in the dev teams' repos — here, each app is just a folder that says **which
build to test**, like `baseURL` in a Playwright config.

```
ticket ─► spec.md ─► CASES.md ─► <case>.yaml ─► PR (human) ─► CI: install build → Maestro (no AI)
Stage 1   Stage 2     Stage 3      Stage 4        Stage 5          Stage 6
```

- **New here?** Start with the onboarding / rebuild guide: [`docs/huong-dan-xay-dung.md`](docs/huong-dan-xay-dung.md).
- Rules and layout: [`CLAUDE.md`](CLAUDE.md). Full design spec: [`docs/requirements.md`](docs/requirements.md).

## Quick start

```bash
bin/qa apps                                            # list apps under test
bin/qa run shopdemo                                    # install the configured build + run all tests
bin/qa run shopdemo --build ~/Downloads/ShopDemo.app.zip   # test a local build
bin/qa run shopdemo --build https://…/ShopDemo.app.zip     # test a build from a link
bin/qa run shopdemo --module auth --no-install         # re-run one module on the installed app
bin/qa install shopdemo                                # install only (before writing new flows)
```

Build references (`build:` in `apps/<app>/app.config.yml`, or `--build`): a local path (`.app` /
`.app.zip`), an `https://` URL (optional `$QA_BUILD_TOKEN` bearer), or
`gh-release:<owner>/<repo>@<tag|latest>/<asset>` (uses `gh` auth / `$GH_TOKEN`). iOS needs a
**simulator** build — an `.ipa` is rejected.

## Apps

| App | Platform | Build source | CI |
|---|---|---|---|
| [shopdemo](apps/shopdemo) | iOS | releases of `leelovefree/ios-shop-demo` | [`app-shopdemo.yml`](.github/workflows/app-shopdemo.yml) |

## Status

Stages 2–6 proven end-to-end on one iOS app. Not built yet: Stage 7 (repair-agent), Stage 8 (reporter),
Android runner.
