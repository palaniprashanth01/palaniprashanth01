# Setup — auto-updating profile README

Three files, one-time setup. After this, your README updates itself every 6 hours from your **pinned repos** on github.com.

## What goes where

In your `palaniprashanth01/palaniprashanth01` repo, the layout looks like this:

```
palaniprashanth01/
├── README.md                              ← your profile readme
├── .github/
│   └── workflows/
│       └── update-readme.yml              ← runs every 6 hours
└── scripts/
    └── update_readme.py                   ← fetches pinned repos
```

## One-time setup (5 minutes)

1. **Push the three files** above into your `palaniprashanth01/palaniprashanth01` repo, preserving the folder structure.

2. **Pin 6 repos** on your GitHub profile — go to github.com/palaniprashanth01, click "Customize your pins", select Macha.ai, SkySense, DocSense, the *Sense series, etc.

3. **Allow Actions to write back to the repo:**
   - Go to `Settings → Actions → General`
   - Scroll to **Workflow permissions**
   - Select **Read and write permissions**
   - Save

4. **Trigger the first run manually** to confirm it works:
   - Go to the `Actions` tab
   - Click `Update README with pinned repos` in the left sidebar
   - Click `Run workflow` → `Run workflow`
   - Wait ~30 seconds, then refresh your profile

## Day-to-day — what you actually do now

| You want to… | You do… |
|---|---|
| Show a new project | Push the repo, pin it on github.com |
| Hide a project | Unpin it on github.com |
| Reorder | Drag in the pin UI on github.com |
| Force an immediate refresh | Actions tab → Run workflow |

**You never edit README.md again.** The script only touches the block between `<!-- PINNED:START -->` and `<!-- PINNED:END -->`. Everything else — your intro, stack, stats, contact — stays exactly as you wrote it.

## How it works

- GitHub gives every Actions workflow a free, scoped `GITHUB_TOKEN` — no PAT, no secrets to manage.
- The script hits GitHub's GraphQL API to grab your 6 pinned repos with their stars, forks, language, and description.
- It renders them into a 2×3 grid and rewrites only the marked region of README.md.
- If nothing changed (same pins, same stars), the commit step is skipped — no spammy commit history.

## Troubleshooting

- **Workflow runs but README doesn't change** → Check that `<!-- PINNED:START -->` and `<!-- PINNED:END -->` are still present in README.md, exactly as written.
- **403 / permission denied on push** → Step 3 above (workflow permissions). Most common cause.
- **GraphQL error in logs** → Confirm `GH_USERNAME` in the workflow file matches your real username.
