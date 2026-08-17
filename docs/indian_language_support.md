# Indian Language Support

The AI service now supports the 22 languages listed in the Eighth Schedule of
the Constitution of India:

Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani,
Malayalam, Manipuri, Marathi, Maithili, Nepali, Odia, Punjabi, Sanskrit,
Santali, Sindhi, Tamil, Telugu and Urdu.

The catalogue is stored in `data/indian_languages.csv`.

`GET /ai/languages` returns the language code and display name for the UI.

Portfolio insight requests accept either a supported language code or its
display name. English is retained only as a system/fallback language; it is
not counted as one of the 22 scheduled Indian languages.

The LLM prompt always receives the selected canonical language name, so the
same portfolio-insight flow can generate Hindi, Telugu, Tamil, Bengali, etc.
without creating separate hardcoded prompt branches for each language.

The existing Week 2 Hindi checklist remains in place because Hindi was the
original task requirement. This file extends the implementation to all 22
scheduled languages.
