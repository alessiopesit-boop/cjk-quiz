#!/usr/bin/env python3
"""Genera le release notes "In sintesi + Dettagli" dai commit di un range git.

Usata dal workflow `release.yml` in due punti:
- Dopo la pubblicazione di una GitHub Release, per riscriverne il body.
- Quando release-please apre o aggiorna la Release PR, per riscriverne il body
  con un'anteprima dello stile che apparira' nella Release finale.

Il body discorsivo di ogni commit Conventional Commits diventa la sezione
"Dettagli" sotto un titoletto pari al subject ripulito e capitalizzato.
I subject senza body compaiono solo nell'indice "In sintesi".

Wrap "git-style" (newline singoli a meta' frase) viene riunito in paragrafi
perche' GitHub Flavored Markdown rende ogni newline singolo come <br>.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from typing import List, Tuple

# Tipi rilasciabili che appaiono nelle note, con etichetta del gruppo.
GROUPS: List[Tuple[str, str]] = [
    ("feat", "Novita'"),
    ("fix", "Correzioni"),
    ("perf", "Performance"),
    ("refactor", "Refactor"),
]
GROUP_BY_TYPE = dict(GROUPS)

SUBJECT_RE = re.compile(
    r"^(?P<type>[a-z]+)(?P<scope>\([^)]+\))?(?P<bang>!)?:\s*(?P<short>.+)$",
    re.IGNORECASE,
)


def unwrap_paragraphs(text: str) -> str:
    """Collassa wrap singoli (newline a meta' frase) in spazi, preservando i
    paragraph break (doppio newline). Senza questo i commit con wrap a 70
    chars apparirebbero spezzati come <br> in markdown."""
    text = text.strip()
    if not text:
        return ""
    text = re.sub(r"\n[ \t]*\n+", "\x1f", text)
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.replace("\x1f", "\n\n").strip()


def humanize(short_text: str) -> str:
    """Capitalizza la prima lettera del subject ripulito."""
    s = short_text.strip()
    return s[0].upper() + s[1:] if s else ""


def build_notes(rng: str) -> str:
    """Esegue git log sul range e ritorna il body in stile In sintesi + Dettagli.
    Stringa vuota se non ci sono voci rilasciabili."""
    raw = subprocess.check_output(
        ["git", "log", "--format=%H%x00%s%x00%b%x1e", "--reverse", rng],
        text=True,
    )

    buckets = {label: [] for _, label in GROUPS}
    breaking: List[Tuple[str, str]] = []

    for entry in raw.split("\x1e"):
        entry = entry.lstrip("\n")
        if not entry.strip():
            continue
        parts = entry.split("\x00", 2)
        if len(parts) < 3:
            continue
        _sha, subject, body = parts
        subject = subject.strip()
        body = body.strip()
        # Salta i commit di release-please.
        if subject.lower().startswith("chore(main): release"):
            continue
        m = SUBJECT_RE.match(subject)
        if not m:
            continue
        ctype = m.group("type").lower()
        short_human = humanize(m.group("short"))
        if not short_human:
            continue

        body_lines: List[str] = []
        breaking_lines: List[str] = []
        for line in body.splitlines():
            if line.startswith("BREAKING CHANGE:"):
                breaking_lines.append(line.split(":", 1)[1].strip())
            else:
                body_lines.append(line)
        body_clean = unwrap_paragraphs("\n".join(body_lines))

        is_breaking = bool(m.group("bang")) or bool(breaking_lines)
        if is_breaking:
            br_text = breaking_lines[0] if breaking_lines else body_clean or short_human
            breaking.append((short_human, br_text))

        label = GROUP_BY_TYPE.get(ctype)
        if label is not None:
            buckets[label].append((short_human, body_clean))

    sections: List[str] = []

    # Indice
    index_parts: List[str] = []
    if breaking:
        index_parts.append(
            "**Modifiche incompatibili**\n"
            + "\n".join(f"- {sh}" for sh, _ in breaking)
        )
    for _t, label in GROUPS:
        if buckets[label]:
            index_parts.append(
                f"**{label}**\n"
                + "\n".join(f"- {sh}" for sh, _ in buckets[label])
            )
    if index_parts:
        sections.append("## In sintesi\n\n" + "\n\n".join(index_parts))

    # Dettagli (solo per voci con body)
    details_parts: List[str] = []
    if breaking:
        for sh, br in breaking:
            if br and br != sh:
                details_parts.append(f"### {sh}\n\n{br}")
    for _t, label in GROUPS:
        for sh, body_clean in buckets[label]:
            if body_clean:
                details_parts.append(f"### {sh}\n\n{body_clean}")
    if details_parts:
        sections.append("## Dettagli\n\n" + "\n\n".join(details_parts))

    if not sections:
        return ""
    return "\n\n---\n\n".join(sections).rstrip() + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--range",
        dest="range_",
        required=True,
        help='Range git, es. "v1.2.1..v1.2.2" o "v1.2.1..HEAD"',
    )
    args = p.parse_args()
    body = build_notes(args.range_)
    if body:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
