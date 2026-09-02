# Portfolio project data

`projects.json` is the single source of truth for project metadata that changes across the portfolio.

Edit this file when changing:

- selected project order
- Chinese / English project title or card description
- tags and badges
- screenshot filename / alt text
- Case Study path
- Live Demo / Live Site URL
- GitHub repository URL
- whether a project appears in Selected Work or Additional System

During `scripts/build_site.sh`, `scripts/render_projects.py` reads the manifest and regenerates:

- Chinese and English homepage project cards
- homepage selected-project JSON-LD
- Case Study action buttons
- project URLs in the generated `sitemap.xml`

`enhance_site.py`, `check_site.py`, and `check_p3.py` also read the same manifest rather than maintaining their own project lists.

Do not add project-specific URL replacement logic to `assets/main.js` or a new one-off publish script. If a project link changes, update `projects.json` only.
