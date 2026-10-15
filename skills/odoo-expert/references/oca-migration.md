# OCA — migrating a module between Odoo versions

Source: `OCA/maintainer-tools` wiki, "Migration to version 17.0", consulted
2026-08-30. **The procedure is generic**; the deprecated-APIs table is
specific to each version jump — check the target's wiki before migrating.

## Before starting

1. Review the current OCA conventions (`oca-contributing.md`).
2. Subscribe to the project's mailing list.
3. **Announce the intention in the repo's migration issue**. It avoids duplicated
   work: someone else may be migrating the same module.
4. Install `pre-commit`.

## Git procedure (preserves history)

```sh
git clone https://github.com/OCA/$repo -b $NEW
cd $repo
git checkout -b $NEW-mig-$module origin/$NEW

# bring the module's history from the previous version, do not copy files
git format-patch --keep-subject --stdout origin/$NEW..origin/$OLD -- $module | git am -3 --keep

# 1st commit: automatic formatting only, isolated from the migration work
pre-commit run -a
git add -A
git commit -m "[IMP] $module: pre-commit auto fixes" --no-verify

# ... code adaptations ...

git add --all
git commit -m "[MIG] $module: Migration to $NEW"
git push $user_org $NEW-mig-$module --set-upstream
```

**Why `format-patch` and not copying:** it preserves the module's authorship and
history, which is what OCA requires. Copying files loses track of who wrote what.

**PR title:** `[$NEW][MIG] <module>: Migration to $NEW`

## What to always update

- **Manifest version** → `$NEW.1.0.0`.
- **Delete the previous version's `migrations/` folder**.
- Review `README.rst` and dependencies.

## What NOT to touch

**Do not change copyright years or original authors** in the headers.
The migration adds an author, it does not replace the previous ones.

## Deprecated APIs — example of the 16.0 → 17.0 jump

It illustrates the *kind* of change to look for. For another jump, consult its wiki.

| Before | Now |
|---|---|
| `name_get()` | override `_compute_display_name` |
| `get_resource_path` | `file_path` |
| hooks with `cr, uid` | they receive `env` |
| `active_id` in context | `id` |
| `active_model` in context | hardcoded model name |
| `attrs` and `states` in XML | Python expressions in `invisible`, `required`, `readonly` |
| `readonly=True` on the model | define `readonly` in the view |
| `invisible="1"` in tree | `column_invisible="1"` |
| `owl="1"` in templates | removed |

**Settings views:** `<div class="app_settings_block">` → `<app>`;
`o_settings_container` → `<block>`; `<h2>` → the `<block>`'s `title` attribute;
`o_setting_box` → `<setting>`; `o_setting_right_pane` /
`o_setting_left_pane` are removed.

## Tests in a migration

- Use `BaseCommon` as the base class.
- **Mock external HTTP requests** — a test must not hit the network.
- Take the chance to raise coverage: the migration is the moment when someone
  reads the whole module again.
