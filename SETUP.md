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

The default access token expires in 1 hour. You need a **long-lived token** that lasts ~60 days.

> **Note:** The exact steps depend on which login flow your token uses. Look at the first 4 characters of your token:
> - **`IGAA...`** → Instagram Business Login flow → follow Part 3a below
> - **`EAA...`** → Facebook Login for Business flow → follow Part 3b below

---

### Part 3a — For IGAA tokens (Instagram Business Login)

1. In your Meta app dashboard → **Instagram** (left sidebar) → **API setup with Instagram login**.
2. Scroll down — you'll see **Instagram app ID** and **Instagram app secret**. Click the eye icon to reveal the secret. Copy it. *This is different from the Meta App Secret in App Settings → Basic.*
3. Open a new browser tab and paste this URL, replacing the placeholders:

   ```
   https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=YOUR_INSTAGRAM_APP_SECRET&access_token=YOUR_SHORT_IGAA_TOKEN
   ```

4. Press Enter. The response will be JSON like:
   ```json
   {"access_token":"IGAA...VERYLONG", "token_type":"bearer", "expires_in":5183999}
   ```
5. Copy the `access_token` value — that's your **60-day long-lived IGAA token**.

> ✅ The default `BASE_URL` in `src/publish_instagram.py` is set to `graph.instagram.com` for IGAA tokens — no code change needed.

---

### Part 3b — For EAA tokens (Facebook Login for Business)

1. Go to **App Settings → Basic** in the dashboard.
2. Copy the **App ID** and **App Secret** (click "Show" on the secret).
3. Open a new browser tab and paste this URL, replacing the placeholders:

   ```
   https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_EAA_TOKEN
   ```

4. Press Enter. The response will be JSON like:
   ```json
   {"access_token":"EAA...VERYLONGSTRING","token_type":"bearer","expires_in":5183999}
   ```
5. Copy the `access_token` value — that's your **60-day long-lived EAA token**.

> ⚠️ If you use EAA tokens, change `BASE_URL` in `src/publish_instagram.py` from `graph.instagram.com` to `graph.facebook.com`.

💡 **Easier alternative for EAA tokens only:** paste the short token into Meta's [Access Token Tool](https://developers.facebook.com/tools/accesstoken/) and click "Extend Access Token". (This shortcut does NOT work for IGAA tokens.)

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

# PART 6 — Enable workflow permissions, then test (5 min)

**Step 1.** Still in repo Settings, click **Actions** (left sidebar) → **General**.

**Step 2.** Scroll down to **Workflow permissions**. Select **Read and write permissions** → click **Save**.

**Step 3.** Go to the **Actions** tab (top of the repo).

**Step 4.** If you see a yellow banner "Workflows aren't being run", click **I understand my workflows, go ahead and enable them**.

**Step 5.** In the left sidebar, click **Daily Instagram Posts**.

**Step 6.** Click **Run workflow** (right side). A dropdown appears asking which **slot** to run:
- `morning` — feed post
- `midday` — story
- `evening` — feed post

Pick one, then click the green **Run workflow** button.

**Step 7.** Wait ~90 seconds. The run should turn green ✅.

**Step 8.** Verify:
- A fresh post (or story) appears on `@gospelanthem`
- A new file appears in the `posted/` folder of your repo

**Step 9.** Repeat steps 6-8 for each slot to test all three formats. Once all three work, you're done — they'll run automatically every day at 8 AM, 12 PM, and 6 PM Tanzania time.

🎉 **System is live.**

---

## Part 7 — Long-term maintenance (this is the only ongoing thing)

The 60-day token will eventually expire. With Instagram Business Login (IGAA tokens), refreshing is **dead simple** — no App ID or App Secret needed:

### Manual refresh every ~50 days (2 minutes)

1. Set a calendar reminder for every 50 days.
2. Open this URL in your browser, replacing the placeholder with your *current* long-lived token:

   ```
   https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=YOUR_CURRENT_LONG_LIVED_TOKEN
   ```

3. Copy the new `access_token` from the response.
4. On GitHub: Settings → Secrets and variables → Actions → click `IG_ACCESS_TOKEN` → **Update secret** → paste the new token → save.
5. Done. Good for another 60 days.

> 💡 You can refresh anytime after the token is at least 24 hours old. Each refresh resets the clock to 60 days from that moment.

### Automated refresh (advanced, optional)
- Add a second weekly workflow that calls the refresh endpoint and updates the secret using the GitHub API. Tell me if Option A becomes annoying and I'll build this for you.

---

## Changing the post times

Edit `.github/workflows/daily_post.yml`. There are **three cron lines** (one per slot):

```yaml
- cron: "0 5 * * *"    # 8:00 AM Tanzania (morning feed)
- cron: "0 9 * * *"    # 12:00 PM Tanzania (midday story)
- cron: "0 15 * * *"   # 6:00 PM Tanzania (evening feed)
```

Cron is in **UTC**. Tanzania is UTC+3, so subtract 3 from your desired local hour:
- `0 5 * * *` → 8:00 AM in Mwanza
- `30 14 * * *` → 5:30 PM in Mwanza
- `0 18 * * *` → 9:00 PM in Mwanza

Use https://crontab.guru to test other times.

⚠️ If you change a cron line, also update the corresponding `case` mapping in the "Determine slot" step of the same file so the workflow knows which slot the new cron triggers.

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
