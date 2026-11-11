# From poker discussions to structured analytical data

**Elias Brown · Web scraping, unstructured-to-structured data, SQLite, and exploratory analysis · Coursework**

This project uses web scraping and transcript collection to investigate poker discussions and instructional videos. I turned unstructured text into structured records, linked the two sources through shared strategy topics, and used SQL and exploratory analysis to examine topic frequency, tone, and advice-related measures.

I was the sole contributor. My work covered collection, text processing, language-model extraction, SQLite database design, topic mapping, and analysis. The resulting pipeline made narrative material queryable while retaining the relationships among discussions, hands, players, replies, and labels.

## Collect and structure the source material

The forum scraper used Python, Requests, and Beautiful Soup to navigate board pages, identify discussion links, and extract posts and replies. A separate workflow collected video transcripts and prepared them for extraction. The two sources began as text written or spoken for people, rather than as consistent analytical tables.

Language-model extraction converted that text into fields describing hands, participants, actions, strategy topics, sentiment, and advice. Relational tables and a shared topic mapping then connected those records for analysis. The methods explain where collection, model-generated labels, and joins affect the interpretation.

## Two sources, different units

The forum pipeline separates discussions, described hands, players, replies, strategy labels, and betting-round measures. The transcript pipeline stores videos and model-generated labels describing topics, advice density, and tone.

These structures preserve distinctions that matter during analysis. A forum thread is not the same unit as a hand; a hand can carry several labels; and a video may cover several topics. Joining those tables changes the number and meaning of the resulting rows.

<figure class="workflow"><ol class="process-flow"><li><span class="step-label">01</span><strong>Collect</strong><span>Scrape forum discussions and collect video transcripts.</span></li><li><span class="step-label">02</span><strong>Structure</strong><span>Convert unstructured text into fields and related records.</span></li><li><span class="step-label">03</span><strong>Relate</strong><span>Store entities in SQLite and align topic vocabulary.</span></li><li><span class="step-label">04</span><strong>Analyze</strong><span>Explore topics, tone, and advice with explicit units and limits.</span></li></ol><figcaption>The report describes the existing workflow. No source posts, transcripts, usernames, or individual records are reproduced.</figcaption></figure>

## What I built

| Component | Purpose |
|---|---|
| Web scraping and transcript collection | Collect forum posts, replies, and instructional video transcripts |
| Structured extraction | Convert narrative material into fields that can be stored and queried |
| Relational tables | Keep discussions, hands, participants, replies, and labels connected |
| A shared label mapping | Relate differently worded topic labels across the two sources |
| An exploratory notebook | Examine topic frequency, tone, advice-related measures, and described outcomes |

The database work provides a way to trace an analytical row back to its source record within the private project. The public reading edition contains no copied posts, transcripts, usernames, or row-level records.

## The central analytical issue is what a row represents

The saved notebook combines hands, topic labels, and replies. A hand with two labels and three replies can contribute six joined rows. That is a valid representation for some questions about comments by topic, but it is not a count of six separate hands.

Likewise, a strategy topic appearing in both a video and a forum discussion does not demonstrate that the forum participant watched the video or adopted its advice. The connection is shared subject matter, not an observed learning pathway.

These distinctions determine how the exploratory charts should be read. The original notebook includes comparisons described as frequency gaps, tone alignment, and advice uptake. This report treats them as exploratory calculations whose units and assumptions need to be examined, rather than evidence of unmet instructional demand or learning effects.

[Read the methods and interpretation notes](docs/METHODS.md)

## What the project demonstrates

The work combines web scraping, the conversion of unstructured data into structured records, database design, vocabulary alignment, SQL joins, exploratory analysis, and visualization. It also makes visible a recurring analytical problem: creating a common label does not automatically create a comparable measurement.

The extraction stage uses a language model. Its assessments of tone, mistakes, or advice are generated labels, not independent expert annotations. A numeric field therefore needs both a clear definition and a validation argument before it can support a substantive conclusion.

## Contribution and scope

I was the sole contributor to the original project. This report was prepared with AI assistance from the existing source and saved notebook. It does not change the code, rerun extraction, recalculate the analyses, or introduce corrected results.

The original source repository remains private. This public reading edition explains the methods and their limits without distributing the collected corpus or model-level records. It is a data-analysis case study, not an evaluation of profitable poker play.
