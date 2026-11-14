#!/usr/bin/env python3
"""Generate a static portfolio. Requires only the Python standard library."""

import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path
from shutil import copytree
from string import Template
from urllib.parse import urlsplit
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
LOCALES = {'pt': 'Português', 'en': 'English', 'fr': 'Français', 'de': 'Deutsch'}
LOCALE_FLAGS = {'pt': '🇧🇷', 'en': '🇬🇧', 'fr': '🇫🇷', 'de': '🇩🇪'}


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def safe_link(label, url):
    if urlsplit(url).scheme not in ('https', 'http', 'mailto'):
        raise ValueError(f'Unsupported link scheme: {url!r}')
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def fetch_github_profile(profile, github_username):
    if not github_username or not profile.get('sync_github_name', False):
        return None
    request = Request(
        f'https://api.github.com/users/{github_username}',
        headers={
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'static-portfolio-builder',
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
        if not isinstance(data, dict):
            raise ValueError('Invalid GitHub profile response')
        if data.get('name') is not None and not isinstance(data['name'], str):
            raise ValueError('Invalid GitHub display name')
        return data
    except (URLError, OSError, ValueError) as error:
        print(
            f'Could not refresh the GitHub profile ({type(error).__name__}); '
            'using local content.',
            file=sys.stderr,
        )
        return None


def resolve_name(profile, github_username, github_profile):
    fallback = profile.get('name', '')
    if not profile.get('sync_github_name', False) or not github_username:
        return fallback
    if github_profile is None:
        return fallback or github_username
    # A GitHub account may have no public display name.
    return (github_profile.get('name') or '').strip() or github_username


def build():
    profile = read_json('content/profile.json')
    github_username = profile.get('github_username', '')
    if not isinstance(github_username, str) or (
        github_username
        and not re.fullmatch(
            r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?',
            github_username,
        )
    ):
        raise ValueError(
            'github_username must be a GitHub username, '
            'or an empty string to hide the photo.'
        )
    github_profile = fetch_github_profile(profile, github_username)
    name = resolve_name(profile, github_username, github_profile)
    template = Template((ROOT / 'templates/page.html').read_text(encoding='utf-8'))
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    year = str(date.today().year)

    for locale in LOCALES:
        content = read_json(f'content/{locale}.json')
        values = {key: escape(value) for key, value in content.items()}
        values['year'] = year
        if name:
            values['name'] = escape(name)
        values['avatar'] = ''
        if github_username:
            # Keep the live URL: GitHub supplies the current photo when a browser loads it.
            alt = escape(
                content['avatar_alt'].format(username=github_username),
                quote=True,
            )
            values['avatar'] = (
                '<img class="avatar" '
                f'src="https://github.com/{github_username}.png?size=192" '
                f'alt="{alt}" width="96" height="96" '
                'decoding="async" referrerpolicy="no-referrer">'
            )

        language_links = []
        for code, label in LOCALES.items():
            text = (
                f'<span aria-hidden="true">{LOCALE_FLAGS[code]} {code.upper()}</span>'
                f'<span class="sr-only">{label}</span>'
            )
            if code == locale:
                language_links.append(
                    f'<strong lang="{code}" aria-current="page" '
                    f'title="{label}">{text}</strong>'
                )
            else:
                language_links.append(
                    f'<a href="/{code}/" lang="{code}" hreflang="{code}" '
                    f'title="{label}">{text}</a>'
                )
        values['language_links'] = ' '.join(language_links)

        projects = []
        for project in profile['projects']:
            title = escape(project['title'][locale])
            description = escape(project['description'][locale])
            details = ''
            if project.get('details'):
                details = (
                    '<ul>'
                    + ''.join(
                        f'<li>{escape(detail)}</li>'
                        for detail in project['details'][locale]
                    )
                    + '</ul>'
                )
            link = ''
            if project.get('url'):
                link = (
                    '<p>'
                    + safe_link(project['link_label'][locale], project['url'])
                    + '</p>'
                )
            projects.append(
                f'<article><details class="project"><summary><h3>{title}'
                '<span class="project-arrow" aria-hidden="true"></span></h3></summary>'
                f'<div class="project-content"><p>{description}</p>{details}{link}</div>'
                '</details></article>'
            )
        values['project_list'] = ''.join(projects) or (
            f'<article><details class="project"><summary><h3>{values["project_title"]}'
            '<span class="project-arrow" aria-hidden="true"></span></h3></summary>'
            f'<div class="project-content"><p>{values["project_description"]}</p></div>'
            '</details></article>'
        )

        contacts = []
        for item in profile['contacts']:
            contact = (
                safe_link(item['label'], item['url'])
                if item.get('url')
                else escape(item['label'])
            )
            contacts.append(f'<li>{contact}</li>')
        values['contact_list'] = (
            '<ul>' + ''.join(contacts) + '</ul>'
            if contacts
            else f'<p>{values["contact_empty"]}</p>'
        )

        destination = output / locale
        destination.mkdir(exist_ok=True)
        (destination / 'index.html').write_text(
            template.substitute(values),
            encoding='utf-8',
        )

    copytree(ROOT / 'assets', output / 'assets', dirs_exist_ok=True)
    (output / 'index.html').write_text(
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Idiomas / Languages</title><link rel="stylesheet" href="/assets/style.css">'
        '<h1>Idiomas / Languages</h1><nav>'
        + ' '.join(
            f'<p><a href="/{code}/" lang="{code}">{label}</a></p>'
            for code, label in LOCALES.items()
        )
        + '</nav></html>',
        encoding='utf-8',
    )
    print('Built four languages in dist/')


if __name__ == '__main__':
    build()
