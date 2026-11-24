# Source audit · v2

Reviewed 24 November 2026 for this source demonstrator. This is an acquisition/status record, not an independent legal review or an audit of current applicability. The immutable raw snapshots and hashes in `source-lock.json` are the actual build inputs.

## Instrument identity and edition

The original AI Act and GDPR raw snapshots are byte-identical to v1. The [official DSA publication record](https://op.europa.eu/en/publication-detail/-/publication/3ff67256-55c4-11ed-92ed-01aa75ed71a1/language-en) identifies CELEX **32022R2065**, OJ **JOL_2022_277_R_0001**, and the Council/Parliament act. The downloaded official XHTML is the adopted act: 93 articles and 156 recitals. Its header gives OJ publication on 27 October 2022; the act's date is 19 October 2022. These different dates are not conflated.

An initially discovered Law Enforcement Directive publication UUID, `3ed8e2ee-c928-4227-b394-6378a69a66ca`, returned a **consolidated documentation text** marked `02016L0680 — EN — 04.05.2016`. It excluded the adopted preamble and expressly disclaimed legal effect. That candidate was rejected; it is not bundled as the adopted source.

The official linked-data resolver [resource/celex/32016L0680](https://publications.europa.eu/resource/celex/32016L0680), requested with `Accept: application/rdf+xml`, resolved to the Publications Office Cellar work UUID **182703d1-11bd-11e6-ba9a-01aa75ed71a1**. Its public download handler supplied the adopted OJ XHTML with **65 articles and 107 recitals**, including Article 27's data-protection-impact-assessment provision. The downloaded text's identity, complete structure and byte hash are pinned. The large resolver metadata response is not needed to rebuild the graph and is not represented as the legal text.

This check matters: a publication title or familiar date alone does not establish which edition the download contains. Neither source selection nor a successful parse establishes present-day consolidated law.

## Court source identity and status

The three case sources are full public **judgments**, headed `JUDGMENT OF THE COURT`, with matching dates and ECLI identifiers. They are not Advocate General opinions, press-release paraphrases, unofficial case notes or generated events.

| Source | Court/date | Complete numbered sequence | Operative points | Authentic case language |
| --- | --- | ---: | ---: | --- |
| [C-634/21](https://juris.curia.europa.eu/juris/document/document.jsf?docid=280426&doclang=EN) | First Chamber, 7 December 2023 | 1–75 | 1 | German |
| [C-184/20](https://juris.curia.europa.eu/juris/document/document.jsf?docid=263721&doclang=EN) | Grand Chamber, 1 August 2022 | 1–129 | 2 | Lithuanian |
| [C-252/21](https://juris.curia.europa.eu/juris/document/document.jsf?docid=275125&doclang=EN) | Grand Chamber, 4 July 2023 | 1–155 | 8 | German |

The current `curia.europa.eu/juris/...` URLs for two judgments redirected to a JavaScript application shell without readable judgment text. That shell was rejected as a source. The Court's public `juris.curia.europa.eu` document service supplied the full English texts. No sign-in, access challenge, private endpoint or verification bypass was used.

The [Court's copyright notice](https://curia.europa.eu/site/jcms/qua1_6625/en/copyright) permits reproducing the judicial decisions with acknowledgement; third-party works retain separate rights. The [InfoCuria notice](https://curia.europa.eu/common/juris/en/avertissement.html) cautions that documents can be amended. The snapshots are pinned and labelled as English translations rather than authentic case-language judgments. Subsequent national outcomes and present precedential/application status were not audited.

## Outcome fidelity and editorial limits

For SCHUFA, the full operative point retains the receiving third party's **strong reliance** condition. Paragraph 72 preserves the referring court's task concerning national law and GDPR conditions. The reading guide does not turn this into a ban on every score or a completed national-case outcome.

For online declarations, the first operative point retains the **specified respects** in which the national online-publication regime is precluded. The second preserves **indirect** sensitive-data disclosure. The guide does not claim that all declarations or all public-interest publication are prohibited.

For Meta Platforms, operative point 1 preserves **sincere cooperation** with data-protection authorities. Operative point 8 retains that dominance does **not, as such, preclude** valid consent, while remaining an important factor whose validity the operator must prove. It does not resolve every processing operation or establish a DSA breach.

All of these routes are editorial metadata, separate from structural and lexical graph edges. The sources predate the AI Act; no link is presented as a judicial interpretation of that later act. Exact source quirks, including the provisional cross-citation in SCHUFA paragraph 70, remain uncorrected and are disclosed.
