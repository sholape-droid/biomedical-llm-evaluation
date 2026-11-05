# Biomedical LLM Evaluation

## Project overview
A comparative evaluation of two AI chatbots on 35 biomedical questions across seven topic areas. **Status: data collection in progress; no results are claimed yet.**

## Method
- Ask each model the same question using a consistent prompt and record the model name/version and evaluation date.
- Independently check answers against appropriate textbooks, lecture notes and/or peer-reviewed references.
- Score accuracy, reasoning, completeness and safety from 1 (poor) to 4 (excellent).
- Record concrete evidence for scores in the `notes` column; categorise errors in `error_type`.
- Use the Python script to validate entries, analyse the scores with SQLite and produce a chart.

## Files
- `question_bank.csv`: 35 proposed questions; review and adapt them before testing.
- `evaluations.csv`: blank results template, awaiting real scored responses.
- `analyse_evaluations.py`: Python, pandas, SQLite and Matplotlib analysis.
- `results/`: generated output after data collection and script execution.

## Run
```bash
python3 -m pip install pandas matplotlib
python3 analyse_evaluations.py
```
Run only after entering real scored responses in `evaluations.csv`.

## Results (complete after evaluation)
- Models and versions: **[enter actual names and versions]**
- Questions scored per model: **[enter actual number]**
- Average total scores: **[enter actual values out of 16]**
- Main error patterns: **[summarise findings]**
- Key lessons and limitations: **[summarise findings]**

## Limitations
This is a small, manually scored evaluation, not a clinical validation. Scoring can be subjective and model responses may vary across runs. AI answers must not be used as a substitute for professional clinical judgement.
