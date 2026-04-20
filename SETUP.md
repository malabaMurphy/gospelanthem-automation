# SETUP — One-Time Instructions

This is the only part of the project that requires manual work. After this, the system runs forever on its own.

Plan for **30–60 minutes**, ideally on a laptop. You'll do this once.

---

## Part 1 — Prepare your Instagram account (5 minutes)

1. **Convert `@gospelanthem` to a Business or Creator account.**
   - Open the Instagram app on your phone → Profile → ☰ menu → Settings → For professionals → Switch to Professional Account.
   - Pick **Creator** (recommended) or **Business**. Either works for the API.

2. **Create a Facebook Page** (this is required by Meta — Instagram posting goes *through* a linked Page).
   - Go to https://www.facebook.com/pages/create
   - Pick a category (e.g., "Religious Organization" or "Personal Blog")
   - Name: "Gospel Anthem" (or whatever you like)

3. **Link the Instagram account to the Facebook Page.**
   - On the Facebook Page → Settings → Linked accounts → Instagram → Connect.
   - Log in with your `@gospelanthem` Instagram credentials.

---

## Part 2 — Create the Meta Developer App (15 minutes)

1. Go to https://developers.facebook.com and click **My Apps** → **Create App**.

2. Choose use case: **Other** → click **Next**.

3. App type: **Business** → **Next**.

4. Fill in:
   - App name: `Gospel Anthem Poster` (anything you want)
   - App contact email: your email
   - Business portfolio: leave default or create a new one

5. After the app is created, you'll land on the App Dashboard.
   - In the left sidebar click **Add Product**.
   - Find **Instagram** and click **Set up**. (If you see "Instagram Graph API" specifically, choose that — Meta has been renaming things.)

6. In the Instagram product, go to **API setup with Instagram login** (or "Generate access tokens"):
   - Under "Generate access tokens", click **Add account** and select your Instagram account (`gospelanthem`).
   - Authorize all permissions it asks for (`instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`).

7. **Copy two values** that appear in the dashboard:
   - **Instagram User ID** (looks like a long number, e.g., `17841400000000000`) — save it.
   - **Access Token** (a very long string starting with `EAA...`) — save it.

> ⚠️ The token shown by default is **short-lived (1 hour)**. We must convert it to a long-lived token in the next step.

---

## Part 3 — Generate a long-lived token (5 minutes)

The default access token expires in 1 hour. You need a **long-lived token** that lasts ~60 days. (We'll set up a refresh strategy in Part 6 so you never have to think about this again.)

1. Visit https://developers.facebook.com/tools/debug/accesstoken/ and paste your short-lived token to confirm it's working.

2. To exchange it for a long-lived one, run this URL in your browser (replace the placeholders):

   ```
   https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN
   ```

   - **App ID** and **App Secret** are on your app dashboard under **App Settings → Basic**.
   - The response will be JSON like: `{"access_token":"EAA...VERYLONG", "expires_in": 5183999}`.
   - That's your **60-day token**. Save it.

> 💡 Quick alternative: paste the short token into Meta's [Access Token Tool](https://developers.facebook.com/tools/accesstoken/) and click "Extend Access Token".

---

## Part 4 — Create the GitHub repository (5 minutes)

1. Go to https://github.com/new and create a **private** repository named `gospelanthem-automation`.

2. On your computer, unzip the project folder I gave you and push it:

   ```bash
   cd gospelanthem-automation
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/gospelanthem-automation.git
   git push -u origin main
   ```

3. *(Or use GitHub Desktop if you prefer a UI — the result is the same.)*

---

## Part 5 — Add your secrets to GitHub (2 minutes)

1. On GitHub, open your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

2. Add these two secrets:

   | Name                 | Value                                       |
   | -------------------- | ------------------------------------------- |
   | `INSTAGRAM_USER_ID`  | The Instagram User ID from Part 2 step 7    |
   | `IG_ACCESS_TOKEN`    | The **long-lived** token from Part 3        |

3. Done. The secrets are encrypted and only the workflow can read them.

---

## Part 6 — Test it (5 minutes)

1. On GitHub, go to your repo → **Actions** tab.

2. If you see "Workflows aren't being run on this fork", click **Enable workflows**.

3. Click **Daily Instagram Post** in the left sidebar → **Run workflow** → **Run workflow** (green button).

4. Watch the run. If it succeeds:
   - ✅ A new image appears in the `posted/` folder of the repo
   - ✅ A new post appears on `@gospelanthem` Instagram

5. If it fails, click into the run to see the error. Most common issues:
   - **Token expired** → regenerate (see Part 7)
   - **Instagram User ID wrong** → re-check step 7 of Part 2
   - **Permission denied on push** → repo Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save

---

## Part 7 — Long-term maintenance (this is the only ongoing thing)

The 60-day token will eventually expire. You have two options:

### Option A — Manual refresh every ~50 days (simplest)
- Set a calendar reminder for every 50 days.
- Generate a new long-lived token using the URL in Part 3.
- Update the `IG_ACCESS_TOKEN` secret on GitHub.
- That's it — 2 minutes, 7 times a year.

### Option B — Automated refresh (more advanced, optional)
- Add a second weekly workflow that calls the token-refresh endpoint and updates the secret using the GitHub API. (I can build this for you later if Option A becomes annoying.)

---

## Changing the post time

Edit `.github/workflows/daily_post.yml` line:

```yaml
- cron: "0 5 * * *"
```

Cron is in **UTC**. Tanzania is UTC+3, so:
- `0 5 * * *` → 8:00 AM in Mwanza
- `0 4 * * *` → 7:00 AM in Mwanza
- `30 18 * * *` → 9:30 PM in Mwanza

Use https://crontab.guru to test other times.

---

## Adding more verses

Open `src/verses.json` and append more entries in the same format:

```json
{"text": "...", "ref": "Book Chapter:Verse", "theme": "..."}
```

The system automatically picks them up — no code changes needed.

---

## Troubleshooting

- **"Permissions error when pushing the poster"** → Repo Settings → Actions → General → Workflow permissions → choose "Read and write permissions" → Save.
- **"Invalid OAuth access token"** → Token expired. Regenerate per Part 3.
- **Post doesn't show up but workflow succeeded** → Check the Instagram app — sometimes posts take 1-2 minutes to appear in the feed.
- **"image_url unreachable"** → Repo might be private. Either make it public, OR (if you want to keep it private) we'll need to switch to a different image-hosting approach. Tell me and I'll add S3 / Cloudinary support.
