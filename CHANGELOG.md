# Changelog - Docker Images

## Versions

### v0.1 (all packages) - April 6th, 2021

Initial build for Praekelt.

### v0.2 (all packages) - May 3rd, 2021

Added:
- Authentication in all containers

### v0.3 (api_model only) - May 21st, 2021

Added:
- Contextualization
- Support for handling misspellings
- Modifications to scoring function
- Text processing: re-include various question stop words (who, what, etc.), change punctuation cleaning, bug fixes (pairwise when only len(tokens) == 2)
- Pass scoring dict with floats between functions, stringify just before returning/saving JSON
- Model: check lowercase before title case, bug fixes (don't return repeated FAQs)

### v0.4 (all packages; major updates) - June 11th, 2021

api_model:
- Refactor code to reduce redundant model lookups, by nearly 100x (i.e., pass in vectors where possible)
- Precompute all model components (contextualization, FAQs, etc.) at container startup, not with each inbound query
- Add endpoint/cron job to refresh FAQs at hourly cadence
- Add endpoint for checking new possible tags

api_demo_apicall:
- Add UI for checking new possible tags

api_faq_db: No changes.

### v0.5 - June 29th, 2021

api_model:
- Prenormalization; linear algebra speed optimization
- Save and return spell-corrected version of query in scoring
- Add gunicorn workers to handle ~80 req/s

api_faq_db:
- Add functionality to edit and delete FAQs

### v0.5.1 - July 13th, 2021

api_model:
- Bug fix: tag check endpoint

### v0.6 - August 3rd, 2021

api_model:
- Minor changes to contextualization
- Add endpoint to check if tags are in model

api_demo_apicall:
- Change wording on Check New Tags page
- Check New Tags page: validate if tags are in model before submit

api_faq_db:
- Changed message flashing style
- Validate if tags are in model before add/edit

### v0.7

api_model:
- Cleaner packaging of model resources/constants
- Feedback endpoint as PUT instead of POST, allowing for continuous updates of feedback over time

api_faq_db:
- Changed gunicorn workers to be asynchronous to properly handle DB operations
- Separated "Old Tags" and "New Tags" on Edit FAQ page (so that new tags aren't cleared by bad input)

api_demo_apicall:
- Changed gunicorn workers to be asynchronous to properly handle DB operations
- Cleaned up UI, with simpler language
- Share spell corrected user query in UI


