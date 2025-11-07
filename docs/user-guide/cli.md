# CLI (`tmoapi`)

The SDK ships with a small CLI helper named `tmoapi`. It lets you download,
store, and explore the official Postman collection for The Mortgage Office
without touching Python code.

```bash
$ tmoapi --help
usage: tmoapi [-h] {download,copy,list,show} ...
```

The CLI installs automatically alongside the library (`pip install tmo-api`).

## Where specs are stored

`tmoapi` looks for API collection files in two places, in this order:

1. `assets/postman_collection/` inside the installed package (what end users get).
2. The current working directory (handy for SDK development).

When you download or copy a collection, the CLI writes it back to
`assets/postman_collection/tmo_api_collection_YYYYMMDD.json`. During local
development this directory is resolved by walking up from the current working
directory until a `pyproject.toml` file is found.

If you want to use a different file, pass `--api-spec path/to/file.json` to the
commands that read specs.

## Commands

### `download`

Fetches the latest Postman collection from The Mortgage Office developer portal
and stores it locally.

```bash
tmoapi download
tmoapi download --output ./tmo_api_collection_latest.json
```

Option | Description
------ | -----------
`-o`, `--output` | Optional explicit destination. Without it the CLI selects the assets directory automatically and names the file after the publish date embedded in the collection.

### `copy`

Copies a collection from another location (file path or URL) into the local
assets directory. This is useful when you need to pin the SDK to an older spec
revision.

```bash
tmoapi copy ./archives/tmo_api_collection_20230901.json
tmoapi copy https://example.com/tmo_api_collection_preview.json
```

The copied file is always saved into `assets/postman_collection/`.

### `list`

Prints every endpoint contained in the current collection. The output is grouped
in a Rich table that includes the HTTP method, the folder-style name, and the
path.

```bash
tmoapi list
tmoapi list --api-spec ./tmo_api_collection_preview.json
```

Use this command when you need to find the canonical name of an endpoint before
looking up its full documentation.

### `show`

Displays detailed information about a single endpoint. You can search by the
endpoint's GUID, its name, a folder-qualified name, or even a fragment of the
URL. Rich formatting is applied to description text, headers, path variables,
query parameters, and request body snippets so you can quickly copy what you
need.

```bash
tmoapi show "Loan Origination/Create Loan"
tmoapi show 28b56336-cb43-41c6-a8b7-ec360d13a1f7
```

If multiple endpoints match your query the CLI presents them in a table and asks
you to refine the search.

!!! tip
    Pair `list` and `show` for the quickest workflow: use `tmoapi list | rg Payment`
    to find the name you care about, then `tmoapi show "<name>"` to see the
    request details.

## Exit codes

- `0` – success (including the "multiple matches" case for `show`)
- `1` – user or network error (missing file, download failure, unknown command, etc.)
