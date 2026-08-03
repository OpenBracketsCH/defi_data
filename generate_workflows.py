"""
Generiert alle Kanton-Workflow-YMLs aus kantone_config.json.

Verwendung:
    python generate_workflows.py

Liest kantone_config.json und schreibt für jeden Kanton eine
.github/workflows/geojson-diff-mail-<id>.yml Datei (analog zum
bewährten ZH-Muster: fetch-depth 2, HEAD_SHA-Check, HEAD^..HEAD-Diff,
rm -f diff.html vor dem Push).

Für Kantone mit reporting_mode "immediate_new_deleted_weekly_changed"
werden zusätzlich zwei Dateien erzeugt:
    geojson-diff-mail-<id>.yml       (sofort: neu/gelöscht)
    geojson-weekly-changes-<id>.yml  (wöchentlich: geändert)
"""

import json
import os

CONFIG_FILE = "kantone_config.json"
OUTPUT_DIR = ".github/workflows"


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def env_block(kanton, config):
    """Partner-Logo wurde entfernt - immer leer."""
    return ""


def build_immediate_workflow(kanton, config):
    kid = kanton["id"]
    name = kanton["name"]
    geojson = kanton["geojson_file"]
    recipient_secret = kanton["mail_recipient_secret"]
    cc_line = "\n          cc: ${{ secrets.MAIL_COPY }}" if kanton.get("use_cc") else ""
    env_lines = env_block(kanton, config)

    return f"""name: Reporting für {name}
on:
  workflow_run:
    workflows: ["Get data from Overpass"]
    types: [completed]
  workflow_dispatch:
jobs:
  diff-and-mail:
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout latest main
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0

      - name: Determine GeoJSON SHA and check if already processed
        run: |
          set -euo pipefail
          mkdir -p .reporting

          # SHA des letzten Commits der GENAU DIESE Datei geändert hat -
          # unabhängig von Bot-Commits anderer Kantone dazwischen.
          GEOJSON_SHA="$(git log -1 --format=%H -- data/json/{geojson})"
          echo "GEOJSON_SHA=$GEOJSON_SHA" >> $GITHUB_ENV

          FILE=".reporting/last_processed_sha_{kid}.txt"
          if [ -f "$FILE" ]; then
            LAST="$(cat "$FILE" | tr -d '[:space:]')"
          else
            LAST=""
          fi

          echo "Letzter GeoJSON-SHA: $GEOJSON_SHA"
          echo "Zuletzt verarbeiteter SHA: $LAST"

          if [ "$GEOJSON_SHA" = "$LAST" ]; then
            echo "ALREADY_PROCESSED=true" >> $GITHUB_ENV
          else
            echo "ALREADY_PROCESSED=false" >> $GITHUB_ENV
          fi

      - name: Stop early if already processed
        if: env.ALREADY_PROCESSED == 'true'
        run: |
          echo "Already processed this GeoJSON commit; skipping mail."
          exit 0

      - name: Setup Python
        if: env.ALREADY_PROCESSED == 'false'
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check if GeoJSON changed in that commit
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          set -euo pipefail
          if git diff --quiet ${{GEOJSON_SHA}}^..${{GEOJSON_SHA}} -- data/json/{geojson}; then
            echo "CHANGED=false" >> $GITHUB_ENV
          else
            echo "CHANGED=true" >> $GITHUB_ENV
          fi

      - name: Create diff HTML
        if: env.ALREADY_PROCESSED == 'false' && env.CHANGED == 'true'{env_lines}
        run: |
          set -euo pipefail
          python scripts/geojson_diff.py \\
            <(git show ${{GEOJSON_SHA}}^:data/json/{geojson}) \\
            data/json/{geojson}

      - name: Check diff.html exists
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          if [ -f diff.html ]; then
            echo "DIFF_EXISTS=true" >> $GITHUB_ENV
          else
            echo "DIFF_EXISTS=false" >> $GITHUB_ENV
          fi

      - name: Mail versenden
        if: env.ALREADY_PROCESSED == 'false' && env.DIFF_EXISTS == 'true'
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: asmtp.mail.hostpoint.ch
          server_port: 587
          secure: false
          username: ${{{{ secrets.MAIL_USER }}}}
          password: ${{{{ secrets.MAIL_PASS }}}}
          subject: "Änderungen an Defis Kanton {name}"
          html_body: file://diff.html
          to: ${{{{ secrets.{recipient_secret} }}}}{cc_line}
          from: defikarte.ch Reports

      - name: Update last processed SHA
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          set -euo pipefail
          mkdir -p .reporting

          FILE=".reporting/last_processed_sha_{kid}.txt"
          echo "$GEOJSON_SHA" > "$FILE"

          git config user.name "defikarte.ch Reporting Bot"
          git config user.email "chrigi@chnuessli.ch"
          git add .reporting/last_processed_sha_{kid}.txt

          # diff.html entfernen damit der Push nicht blockiert wird
          rm -f diff.html
          git commit -m "update last processed sha for _{kid}" || exit 0

          for i in 1 2 3; do
            git pull --rebase origin main && git push origin HEAD:main && break
            echo "Push failed, retry $i..."
            sleep 2
          done
"""


def build_be_style_workflows(kanton, config):
    """Sofort-Workflow (neu/gelöscht) + Weekly-Workflow (geändert) für BE-Stil."""
    kid = kanton["id"]
    name = kanton["name"]
    geojson = kanton["geojson_file"]
    recipient_secret = kanton["mail_recipient_secret"]
    cc_line = "\n          cc: ${{ secrets.MAIL_COPY }}" if kanton.get("use_cc") else ""
    env_lines = env_block(kanton, config)

    immediate = f"""name: Reporting für {name}
on:
  workflow_run:
    workflows: ["Get data from Overpass"]
    types: [completed]
  workflow_dispatch:
jobs:
  diff-and-mail:
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout latest main
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0

      - name: Determine GeoJSON SHA and check if already processed
        run: |
          set -euo pipefail
          mkdir -p .reporting

          GEOJSON_SHA="$(git log -1 --format=%H -- data/json/{geojson})"
          echo "GEOJSON_SHA=$GEOJSON_SHA" >> $GITHUB_ENV

          FILE=".reporting/last_processed_sha_{kid}.txt"
          if [ -f "$FILE" ]; then
            LAST="$(cat "$FILE" | tr -d '[:space:]')"
          else
            LAST=""
          fi

          echo "Letzter GeoJSON-SHA: $GEOJSON_SHA"
          echo "Zuletzt verarbeiteter SHA: $LAST"

          if [ "$GEOJSON_SHA" = "$LAST" ]; then
            echo "ALREADY_PROCESSED=true" >> $GITHUB_ENV
          else
            echo "ALREADY_PROCESSED=false" >> $GITHUB_ENV
          fi

      - name: Stop early if already processed
        if: env.ALREADY_PROCESSED == 'true'
        run: |
          echo "Already processed this GeoJSON commit; skipping mail."
          exit 0

      - name: Setup Python
        if: env.ALREADY_PROCESSED == 'false'
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check if GeoJSON changed in that commit
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          set -euo pipefail
          if git diff --quiet ${{GEOJSON_SHA}}^..${{GEOJSON_SHA}} -- data/json/{geojson}; then
            echo "CHANGED=false" >> $GITHUB_ENV
          else
            echo "CHANGED=true" >> $GITHUB_ENV
          fi

      - name: Create diff (sofort + pending)
        if: env.ALREADY_PROCESSED == 'false' && env.CHANGED == 'true'{env_lines}
        run: |
          set -euo pipefail
          python scripts/geojson_diff_be.py \\
            <(git show ${{GEOJSON_SHA}}^:data/json/{geojson}) \\
            data/json/{geojson} \\
            .reporting/pending_changes_{kid}.json

      - name: Check diff_immediate.html exists
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          if [ -f diff_immediate.html ]; then
            echo "DIFF_EXISTS=true" >> $GITHUB_ENV
          else
            echo "DIFF_EXISTS=false" >> $GITHUB_ENV
          fi

      - name: Mail versenden (neu + gelöscht)
        if: env.ALREADY_PROCESSED == 'false' && env.DIFF_EXISTS == 'true'
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: asmtp.mail.hostpoint.ch
          server_port: 587
          secure: false
          username: ${{{{ secrets.MAIL_USER }}}}
          password: ${{{{ secrets.MAIL_PASS }}}}
          subject: "Neue/gelöschte Defis – {name}"
          html_body: file://diff_immediate.html
          to: ${{{{ secrets.{recipient_secret} }}}}{cc_line}
          from: defikarte.ch Reports

      - name: Update last processed SHA + pending changes committen
        if: env.ALREADY_PROCESSED == 'false'
        run: |
          set -euo pipefail
          mkdir -p .reporting

          FILE=".reporting/last_processed_sha_{kid}.txt"
          echo "$GEOJSON_SHA" > "$FILE"

          git config user.name "defikarte.ch Reporting Bot"
          git config user.email "chrigi@chnuessli.ch"

          git add .reporting/last_processed_sha_{kid}.txt
          if [ -f .reporting/pending_changes_{kid}.json ]; then
            git add .reporting/pending_changes_{kid}.json
          fi

          # diff_immediate.html entfernen damit der Push nicht blockiert wird
          rm -f diff_immediate.html

          git commit -m "update reporting state for _{kid}" || exit 0

          for i in 1 2 3; do
            git pull --rebase origin main && git push origin HEAD:main && break
            echo "Push failed, retry $i..."
            sleep 2
          done
"""

    weekly = f"""name: Wöchentlicher Änderungs-Report {name}
on:
  schedule:
    - cron: "0 7 * * 1"   # jeden Montag um 07:00 UTC
  workflow_dispatch:

jobs:
  weekly-report:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout latest main
        uses: actions/checkout@v4
        with:
          ref: main

      - name: Check if pending changes exist
        run: |
          FILE=".reporting/pending_changes_{kid}.json"
          if [ -f "$FILE" ] && [ -s "$FILE" ]; then
            COUNT=$(python3 -c "import json; data=json.load(open('$FILE')); print(len(data))")
            if [ "$COUNT" -gt "0" ]; then
              echo "HAS_PENDING=true" >> $GITHUB_ENV
              echo "PENDING_COUNT=$COUNT" >> $GITHUB_ENV
            else
              echo "HAS_PENDING=false" >> $GITHUB_ENV
            fi
          else
            echo "HAS_PENDING=false" >> $GITHUB_ENV
          fi

      - name: Setup Python
        if: env.HAS_PENDING == 'true'
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Weekly-HTML generieren
        if: env.HAS_PENDING == 'true'{env_lines}
        run: |
          python3 scripts/build_weekly_report.py \\
            .reporting/pending_changes_{kid}.json \\
            "{name}" \\
            diff_weekly.html

      - name: Weekly-Mail versenden
        if: env.HAS_PENDING == 'true'
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: asmtp.mail.hostpoint.ch
          server_port: 587
          secure: false
          username: ${{{{ secrets.MAIL_USER }}}}
          password: ${{{{ secrets.MAIL_PASS }}}}
          subject: "Wöchentlicher Änderungs-Report – {name} (${{{{ env.PENDING_COUNT }}}} Änderungen)"
          html_body: file://diff_weekly.html
          to: ${{{{ secrets.{recipient_secret} }}}}{cc_line}
          from: defikarte.ch Reports

      - name: Pending changes leeren nach Versand
        if: env.HAS_PENDING == 'true'
        run: |
          set -euo pipefail
          echo "[]" > .reporting/pending_changes_{kid}.json

          git config user.name "defikarte.ch Reporting Bot"
          git config user.email "chrigi@chnuessli.ch"
          git add .reporting/pending_changes_{kid}.json

          rm -f diff_weekly.html
          git commit -m "clear pending changes {kid} after weekly report"

          for i in 1 2 3; do
            git pull --rebase origin main && git push origin HEAD:main && break
            echo "Push failed, retry $i..."
            sleep 2
          done
"""
    return immediate, weekly


def main():
    config = load_config()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for kanton in config["kantone"]:
        mode = kanton.get("reporting_mode", "immediate")
        kid = kanton["id"]

        if mode == "immediate":
            content = build_immediate_workflow(kanton, config)
            path = os.path.join(OUTPUT_DIR, f"geojson-diff-mail-{kid}.yml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Erzeugt: {path}")

        elif mode == "immediate_new_deleted_weekly_changed":
            immediate, weekly = build_be_style_workflows(kanton, config)
            path_immediate = os.path.join(OUTPUT_DIR, f"geojson-diff-mail-{kid}.yml")
            path_weekly = os.path.join(OUTPUT_DIR, f"geojson-weekly-changes-{kid}.yml")
            with open(path_immediate, "w", encoding="utf-8") as f:
                f.write(immediate)
            with open(path_weekly, "w", encoding="utf-8") as f:
                f.write(weekly)
            print(f"Erzeugt: {path_immediate}")
            print(f"Erzeugt: {path_weekly}")

        else:
            print(f"WARNUNG: Unbekannter reporting_mode '{mode}' für {kid} – übersprungen.")


if __name__ == "__main__":
    main()
