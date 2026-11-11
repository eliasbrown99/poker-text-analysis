# Data structure, extraction, and the meaning of the comparisons

**Methods and interpretation · Based on the existing implementation and saved notebook**

The analysis brings together text that was not originally collected under a shared measurement design. Its usefulness depends on preserving the source units, making extraction choices visible, and interpreting each join correctly.

## Collect unstructured text for analysis

The forum collection workflow uses Requests to retrieve board and thread pages and Beautiful Soup to parse their HTML. It normalizes discussion URLs, extracts the original post and replies, and stores the collected material in SQLite. This web-scraping stage produces a source record; the later extraction stage interprets the poker content within that record.

The video workflow enumerates videos in a playlist and retrieves available transcript segments. It retains raw segments separately from text prepared for extraction. The preparation step uses a language model to correct transcription errors and attempt to fill gaps, so the prepared text is a transformed input rather than a verbatim transcript. That distinction adds another source of uncertainty to downstream labels.

The analytical pipeline then turns the two text sources into structured entities and measures. The public report describes that process without redistributing the collected posts or transcripts.

## Preserve the source units

| Entity | Intended unit | Relationship that matters |
|---|---|---|
| Forum discussion | One collected thread | May describe more than one hand |
| Hand | One parsed hand account | Can have several players, replies, and labels |
| Player | One participant record within a hand | Is linked to that hand rather than treated as a stand-alone observation |
| Reply | One extracted comment record | Multiple replies can attach to one hand |
| Strategy label | A tag associated with a hand or video | More than one tag can describe the same record |
| Video | One collected video and transcript | Has a separate set of model-generated descriptors |

The forum schema uses separate tables and foreign-key relationships to represent these entities. The transcript database stores video records and extracted label fields. A bridge table maps observed topic labels to a shared vocabulary so that the sources can be compared by subject.

## Treat extraction as a measurement step

The pipeline requests structured outputs from a language model and writes selected fields into the databases. Forum outputs include descriptions of the hand, actions, perceived mistakes, and sentiment. Transcript outputs include topic labels, advice density, and overall sentiment.

Requiring JSON makes a response easier to process; it does not establish that each classification is correct. Similarly, requesting a percentage of advice-bearing transcript lines does not make the model’s estimate equivalent to a manually counted and validated proportion.

The shared label mapping is also model-assisted. It groups labels into common categories while retaining the aliases. That is a practical integration step, but grouping decisions can affect which records are compared. The report does not claim an independently validated taxonomy or an annotated accuracy benchmark.

## Account for row multiplication

<figure class="workflow"><div class="grain-example"><div><strong>1 hand</strong><span>The source account</span></div><span class="math-symbol">×</span><div><strong>2 labels</strong><span>Two associated topics</span></div><span class="math-symbol">×</span><div><strong>3 replies</strong><span>Three comments</span></div><span class="math-symbol">=</span><div><strong>6 rows</strong><span>After the two joins</span></div></div><figcaption>Illustrative join example, created for this report. It is not a record from the collected data.</figcaption></figure>

The notebook’s forum helper table joins hand labels to individual replies. Counts taken after that join can give a hand more weight when it has more replies. They therefore require a different interpretation from counts of videos, unique hands, or unique discussion threads.

The same issue arises when several aliases map to a common topic. The final analytical unit must be checked after mapping and joining, rather than inferred from the original table names.

## Read each comparison according to its construction

| Exploratory view | What the reviewed calculation uses | Interpretation limit |
|---|---|---|
| Topic frequency gap | Creator-side label rows and forum rows after joining to replies | Raw differences across differently sized and weighted sources do not measure unmet demand |
| Tone alignment | Forum sentiment and a selected matching video for each topic | The notebook selects one matching video; it does not estimate the mean tone of every creator video on that topic |
| Advice density and “uptake” | Model-assigned advice density and forum records sharing a topic | Shared topics do not establish viewing, adoption, or causation; topic overlap also creates dependence |
| Reported mistakes | Presence of an extracted perceived-mistake field | A populated field is not an independently verified strategic error |
| Hand-range display | Described cards linked to a player-position filter | The query does not independently identify all opening decisions or a representative opening range |

These limits explain why the reading edition focuses on the pipeline and analytical design. It does not relabel the original charts as validated findings, and it does not silently substitute a new analysis for the submitted work.

## What would support a stronger substantive finding

A cross-source claim would need a clearly defined unit, comparable denominators, and aggregation that matches the question. Model-generated labels would need a review sample or another independent standard. A claim about learning would require evidence connecting exposure to the instructional material with later behavior.

Those are requirements for interpreting the existing questions, not changes made as part of this report. No scraping, paid model calls, database migrations, or analytical reruns were performed to create this reading edition.

[Return to the project overview](../README.md)
