# Security Policy

## Supported status

The TACITUS Knowledge Pipeline is a public reference implementation and notebook, not a supported production service. Security-sensitive fixes should target the default branch. Earlier notebook revisions and dependency combinations are not guaranteed to receive patches.

## Reporting a vulnerability

Report suspected vulnerabilities privately to **hello@tacitus.me**. Do not open a public issue containing exploit details, API keys, service-account files, database credentials, private documents, or personal data.

Please include the affected commit, notebook or dependency, reproduction steps, likely impact, and any safe containment measure. A report will be acknowledged when reviewed. No response-time or bounty commitment is currently offered.

## Notebook and credential safety

Before running the notebooks:

- review every cell and dependency;
- use a dedicated development environment and least-privilege credentials;
- do not place secrets directly in notebook cells or committed output;
- use synthetic or public documents unless the full processing and retention path has been approved;
- verify graph-database exposure, authentication, and network binding; and
- inspect generated files before publishing or sharing them.

Rotate any credential that may have entered Git history, notebook output, logs, screenshots, Colab state, or issue discussions. Evidence links and deterministic graph operations do not make model extraction or source material inherently safe or correct.

## Disclosure

Allow reasonable time for investigation and remediation before public disclosure. Maintainers may request coordinated disclosure when users or downstream notebooks could remain exposed.
