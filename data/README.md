# Portfolio project data

`projects.json` is the single source of truth for project metadata that changes across the portfolio.

Edit this file when changing:

- selected project order
- Chinese / English project title or card description
- tags and badges
- screenshot alt text (filename is derived from the project slug)
- Live Demo / Live Site URL
- GitHub repository URL
- case-study facts and evidence-based framing

Every project in this manifest appears in Selected Work. Local Case Study paths and WebP filenames are derived from `slug`; the shared case-study year is stored once as `project_year`. Case-study page metadata is in `case_page`, while the unique section content lives in `data/case-studies/`; one renderer supplies the shared head, navigation, facts, framing and action links.

During `scripts/build_site.sh`, `scripts/render_site.py` reads the manifest and regenerates:

- Chinese and English homepage project cards
- homepage selected-project JSON-LD
- Case Study facts, framing and action buttons
- project URLs in the generated `sitemap.xml`

`scripts/check_site.py` reads the same manifest rather than maintaining its own project list.

Do not add project-specific URL replacement logic to `assets/main.js` or a new one-off publish script. If a project link changes, update `projects.json` only.
