# Publishing this report

This folder contains the reading edition and its presentation files. The original project and its contributions are described in the report.

Build from this folder with Python 3.10+ and Pandoc installed:

```sh
python3 scripts/check_site_files.py
python3 scripts/build_portfolio_site.py
```

GitHub Pages serves the generated files from the `gh-pages` branch, at its root. Publish only the contents of `_site/` to that branch after checking the report and its links. The default branch retains the editable report sources. Changes to source Markdown must be rebuilt and published to update the live site.

`site-files.txt` is the explicit website input list. Keep employer material, collected corpora, credentials, and personal preparation notes outside this report package.
