# JLPT N1 Exam Prep Assistant

## Goal
To design and implement an assistant to help prepare the user for the JLPT N1 exam (Japanese Language Proficiency Test, N1 being the highest level)

Inline with N1 study level, all explanations should be in Japanese as its primary source. Where appropriate/helper, secondary sources can include explanations in Cantonese (which is closer in terms of heritage compared to Western languages) followed by English as the last resort.

# Product Overview
The product comprises of the following components:
1. database of course content (in the form of LLM maintained wiki, a.k.a. LLM-wiki)
	1. contents are stored in human-readable markdown format (viewable by Obsidian)
	2. contents should fit a pre-defined schema, which covers:
		1. vocabulary or grammar to be learnt
		2. couple of examples to illustrate usage
		3. related concepts/vocabulary/grammar to compare/contrast usage
		4. common mistakes in usage (if any)
		5. JPNT level indicator (N1 etc.; N1 revision may involve N2 contents etc.)
	3. course content will be sourced via ingestion of manually curated source materials - see course content importer (#2) below
2. course content importer
	1. scrap website(s) for grammar/vocabulary content and content into markdown files according to the course content database schema
    2. ingest manually curated course content into the database
        1. Claude Code prompts:
            1. ingest article <ARTICLE.MD>
                1. read article from the markdown file provided
                2. the bulk of the file contains the Japanese article to be added to the LLM-wiki
                3. the markdown file contains vocabularies and/or grammars which are enclosed by [[...]]
                4. the markdown file may contain sections linked from the main article for explanatory notes
                5. based on the above, create new or update existing pages in the LLM-wiki for the vocabulary/grammar etc

3. progress tracker
	1. ability to track progress for a given user (can be single user to start with)
	2. record the number of times a given piece of content from the course content database has been presented so far, and whether the user has passed or failed the quiz on that piece of concept
	3. ability to mark/unark a given piece of content for "Focus" (drill down)
4. daily email / quiz generator
	4. select 1-2 vocabs and 1-2 grammar rules from the course content database
	5. generate email as quiz
	6. track quiz results (see progress tracker)

## CLAUDE AI Roles
- product designer: help design and refine the specification doc (specs.md) per the overview laid down above
-  japanese language instructor: design the course content schema; research on a good external website to perform the initial seeding of course content database 
- software developer: code up the platform per the spec, starting with the scraper to seed the database
- do not spend time on the GUI/daily quiz generator for the time -- first focus on creating the course content schema followed by its initial seeding

## Tenets/Ground Rules
- keep things simple, do not over-engineer
- use existing tools/libraries as much as possible
- code should be writing primarily in python, with some javascript for display going forward. No need for compiled languages.
- keep all docs and course content/schema in markdown MD files (human readable)
- test-driven design, includes automated tests covering positive and negative cases where possible, exercising the code being tested as extensive as possible (e.g. a good pattern is to curate a set of representative test cases as input files to generate expected baseline for comparison)
- avoid hardcoding, use CLI argv where possible (pre-defined defaults are OK) and avoid unobvious coupling in the logic
- data minimalization principle: clean data lineage, avoid storing duplicative copies of data, instead store data keys and look up the authoritative data source
- flag technical debt: trade off to the design and/or code base say in flavor of preserving backward compatibility must be subject to careful deliberation
