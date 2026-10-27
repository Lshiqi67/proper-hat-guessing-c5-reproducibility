# Build the arXiv submission candidate

The entry point is `main.tex`. The clean submission ZIP contains exactly thirteen
TeX files, including every chapter, generated table and bibliography. Figures
are drawn with TikZ. No evidence download, SAT solver, shell escape, external
image, BibTeX invocation or personal filesystem path is required for typesetting.

Run twice in the extracted source directory:

```text
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error main.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

Local validation used Windows, TeX Live 2024 and Python 3.12.14. Both the source
tree and a fresh extraction compiled successfully to 23 pages with identical
page text and no final LaTeX, overfull or underfull warnings. The arXiv server
build and preview remain to be performed; local success does not establish them.
The site currently documents TeX Live 2025 as its default.

The PDF is supplied separately for inspection. Upload `c5-arxiv-source-20261027.zip`
as TeX source; do not submit the full Git repository or computational archives.
The manuscript is a private prepublication candidate. Its fixed evidence URL
is scheduled to become public with the actual arXiv announcement.
