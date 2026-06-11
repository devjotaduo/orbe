# Agent authentication (GitHub)

How automated agents (CI jobs, Claude Code on the web, bots) authenticate to
push branches and open pull requests on this repository — **without** anyone
committing a personal access token.

> **Golden rule:** never commit a token (`ghp_…`, `github_pat_…`) or a private
> key to the repository, and never paste one into a chat or issue. Tokens that
> leak must be revoked immediately at <https://github.com/settings/tokens>.

## Recommended: a GitHub App as a service account

A GitHub App mints **short-lived installation tokens** (valid ~1h, generated on
demand) scoped to only this repository. Nothing long-lived circulates, the
identity is not tied to a person, and actions are auditable as the app.

### One-time setup (repo/org owner)

1. Create the app: <https://github.com/settings/apps/new>
   - **Permissions → Repository:**
     - `Contents`: Read and write
     - `Pull requests`: Read and write
     - `Metadata`: Read-only (required)
   - **Webhook:** uncheck *Active* (not needed for this use).
2. **Install** the app on `devjotaduo/orbe` (Install App → select this repo).
3. Note the **App ID** and generate a **private key** (`.pem`).
4. Store them as secrets — **never in the repo**:
   - GitHub Actions: *Settings → Secrets and variables → Actions* →
     `APP_ID`, `APP_PRIVATE_KEY`.
   - Other runners / Claude Code on the web: inject them as environment
     variables via the environment configuration, sourced from your secrets
     manager (Vault / 1Password / Doppler / …).

### How agents consume it

In GitHub Actions, exchange the App ID + private key for an installation token
that lives only for the duration of the job. See
[`.github/workflows/example-agent-auth.yml`](../.github/workflows/example-agent-auth.yml):

```yaml
- uses: actions/create-github-app-token@v1
  id: app-token
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
# then use ${{ steps.app-token.outputs.token }} for git push / gh / the API
```

Outside Actions, an agent generates the token the same way (App JWT →
`POST /app/installations/{id}/access_tokens`) and uses it as
`Authorization: Bearer <token>` or
`git push https://x-access-token:<token>@github.com/devjotaduo/orbe.git`.

## Fallback: a fine-grained PAT on a service account

Acceptable only if a GitHub App is not viable. Use a dedicated bot account, a
**fine-grained** token limited to `devjotaduo/orbe` with `Contents: RW` +
`Pull requests: RW`, a short expiry, and store it **only** in a secrets manager
/ Actions secret. Rotate on a schedule. Still never commit it.

## What not to do

- ❌ Commit a token or `.pem` to the repo (even in a "private" file).
- ❌ Share a personal PAT for team use.
- ❌ Paste tokens into chats, issues, or PR comments.
- ❌ Grant `repo`-wide classic scopes when fine-grained per-repo access suffices.
