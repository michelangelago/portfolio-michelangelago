# Minimal multilingual portfolio

Static HTML and CSS generated with Python. No JavaScript, application server, or external Python dependencies. Portuguese, English, French, and German share one template.

## Build and preview

```sh
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000. The local root lists languages; nginx redirects the root based on the browser's first language, defaulting to Portuguese.

The switch to the left of the language links toggles between a white background and a black background. It uses a native checkbox and CSS `:has()`, with a translated accessible label, and can be operated with the keyboard. The choice applies to the current page and is not saved across navigation or language changes. No JavaScript or browser storage is used.

## Content

Edit `content/pt.json`, `en.json`, `fr.json`, and `de.json` to replace the example introduction and about text in each language. Keep the same keys in every language. The copyright footer uses your display name and the current year at build time.

`content/profile.json` holds your shared name, contacts, and projects. For example:

```json
{
  "name": "Your actual name",
  "github_username": "YOUR_USERNAME",
  "sync_github_name": true,
  "contacts": [{"label": "GitHub", "url": "https://github.com/YOUR_USERNAME"}],
  "projects": [{
    "title": {"pt": "Projeto", "en": "Project", "fr": "Projet", "de": "Projekt"},
    "description": {"pt": "Descrição", "en": "Description", "fr": "Description", "de": "Beschreibung"},
    "link_label": {"pt": "Código", "en": "Source code", "fr": "Code source", "de": "Quellcode"},
    "url": "https://github.com/YOUR_USERNAME/YOUR_PROJECT"
  }]
}
```

Text is HTML-escaped; links accept HTTP, HTTPS, or mailto URLs. An empty projects list shows a sample project until you add real entries.

Projects can also include `details`, an object with `pt`, `en`, `fr`, and `de` arrays of text. These appear as a list under the description. The `url` and `link_label` fields are optional for projects that do not yet have a source or live link, such as this portfolio.

Project entries start collapsed. Click a title or arrow, or focus it and press Enter or Space, to show or hide its description, details, and links. Native HTML `details` and `summary` elements provide this behavior without JavaScript.

Contacts use a `label` and an optional `url`. Omit `url` for plain text, such as a Discord username.

## GitHub profile photo

Set `github_username` in `content/profile.json` to your GitHub username (without `@` or a URL). It is currently set to `michelangelago`. Build and upload once to add the photo to all four languages.

The header loads `https://github.com/USERNAME.png?size=192` directly, using [GitHub's avatar URL](https://github.blog/developer-skills/github/github-protips-tips-tricks-hacks-and-secrets-from-jason-etcovitch/). Later photo changes on GitHub appear on subsequent page loads after GitHub/browser caches refresh; no portfolio rebuild, scheduled task, or JavaScript is needed. An already-open page does not refresh the photo automatically. The photo requires a connection to GitHub.

Set `github_username` to an empty string to hide the photo. Changing the username itself requires a rebuild and upload. Alternative text lives in each language's `avatar_alt` field; preserve its `{username}` placeholder.

## GitHub display name

With `sync_github_name` set to `true`, `python3 build.py` retrieves your public GitHub display name once and uses it in the heading and page title in all four languages. No token or JavaScript is required. If GitHub has no display name, the username is used.

The `name` field is the fallback for offline builds or API failures; it is currently `Michelangelago`. Set `sync_github_name` to `false` to always use that field instead of GitHub.

Name changes require a rebuild and upload because the name is part of the generated HTML. For automatic name updates after deployment, schedule that build-and-upload process. No scheduled deployment has been configured yet.

## AWS / nginx

Generate `dist/` locally or in CI, then upload its contents to `/var/www/portfolio/` on your VPS. Python is only needed to build, not to serve. Use `deploy/nginx.conf` as a starting configuration, replace the domain, and configure HTTPS before public launch. Allow ports 80 and 443 in AWS and the server firewall. Check configuration with `sudo nginx -t` before reloading nginx.

For deployment without partial updates, upload each build into a new release directory and atomically switch the symlink nginx serves. No AWS resources have been created or changed by this project.