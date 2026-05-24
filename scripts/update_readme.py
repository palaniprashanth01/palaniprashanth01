"""
Fetches the user's pinned repos from GitHub's GraphQL API
and rewrites the section between the markers in README.md.

Markers (must exist in README.md, exactly as written):
    <!-- PINNED:START -->
    <!-- PINNED:END -->

Runs in GitHub Actions every 6 hours. Idempotent — if nothing changed,
the commit step is a no-op.
"""

import os
import sys
import textwrap
import requests

USERNAME = os.environ["GH_USERNAME"]
TOKEN    = os.environ["GITHUB_TOKEN"]
README   = "README.md"

START = "<!-- PINNED:START -->"
END   = "<!-- PINNED:END -->"

# GitHub GraphQL — pinned items + their stars, lang, description, url
QUERY = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          description
          url
          stargazerCount
          forkCount
          primaryLanguage { name color }
        }
      }
    }
  }
}
"""


def fetch_pinned():
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["pinnedItems"]["nodes"]


def card(repo):
    """Render one repo as half-width markdown — pairs with another to make a row."""
    name = repo["name"]
    url  = repo["url"]
    desc = (repo["description"] or "No description yet.").strip()
    lang = repo["primaryLanguage"]
    lang_name = lang["name"] if lang else "—"
    stars = repo["stargazerCount"]
    forks = repo["forkCount"]

    # Two-line description max — looks neat in the grid
    if len(desc) > 110:
        desc = desc[:107].rstrip() + "…"

    return textwrap.dedent(f"""\
        #### [{name}]({url})

        {desc}

        <sub>`{lang_name}` &nbsp; · &nbsp; ★ {stars} &nbsp; · &nbsp; ⑂ {forks}</sub>
        """)


def render_grid(repos):
    """Build a 2-column table of up to 6 pinned repos."""
    if not repos:
        return ("<p align=\"center\"><sub><i>Pin some repositories on your GitHub "
                "profile and they'll appear here.</i></sub></p>")

    rows = []
    for i in range(0, len(repos), 2):
        left  = card(repos[i])
        right = card(repos[i + 1]) if i + 1 < len(repos) else ""
        rows.append(
            "<tr><td width=\"50%\" valign=\"top\">\n\n"
            + left
            + "\n</td><td width=\"50%\" valign=\"top\">\n\n"
            + right
            + "\n</td></tr>"
        )

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main():
    repos = fetch_pinned()
    grid  = render_grid(repos)

    with open(README, encoding="utf-8") as f:
        content = f.read()

    if START not in content or END not in content:
        sys.exit(f"Markers {START} / {END} missing from {README}")

    pre, _, rest = content.partition(START)
    _, _, post   = rest.partition(END)

    new = f"{pre}{START}\n\n{grid}\n\n{END}{post}"

    if new == content:
        print("No change — README is already up to date.")
        return

    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"Updated README with {len(repos)} pinned repos.")


if __name__ == "__main__":
    main()
