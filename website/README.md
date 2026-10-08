# SpecialMe website

A single static page (`index.html`) announcing the app and collecting interest in the trial and demo.

## How the form works
- The form posts to a Supabase table, `trial_signups`, in the `specialme-website` project.
- The key in the page is a **publishable** key. It is meant to be public. The table's row-level security lets the public **insert only**. Nobody can read, change or delete rows from the website.
- Duplicate emails are ignored, and consent is required.
- It collects only email, first name, and the type of person. No health or school information.
- View sign-ups in the Supabase dashboard (Table Editor, `trial_signups`).

## Deploy
Any static host works. Cloudflare Pages, Netlify or Vercel can all deploy this folder from GitHub:
1. Connect this repository, set the publish folder to `website`, and no build command.
2. Add the custom domain `specialme.app`, then follow the host's DNS steps at the domain registrar.

## Before launch
- Add a privacy policy page and link it from the form.
- Add a contact email and mention it in the footer.
- Do not store anything more sensitive than an email in this project. The app itself gets a separate project with the HIPAA plan.
