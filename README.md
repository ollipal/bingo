# Bingo Generator

Code mostly generated with Claude 3.5 Sonnet LLM.

Generate multilingual bingo cards for events! This program creates random bingo cards from a list of events in different languages. The cards can be viewed and printed using the included web interface.

## Setup

1. Clone or download this repository
2. Ensure you have Python 3.x installed
3. Place all files in the same directory:
   - `bingo.py` (card generator script)
   - `questions.csv` (questions list)
   - `index.html` (web interface)

## Generating Bingo Cards

Run the program from command line:
```bash
python3 bingo.py <language> <number_of_cards>
```

Examples:
```bash
python3 bingo.py english 2
python3 bingo.py finnish 3
python3 bingo.py spanish 1
```

The program will generate a JSON, file containing your cards, such as `finnish.json`.

## Modifying Word List

The `questions.csv` file contains the words/phrases for the bingo cards. You can modify this file using Excel or any spreadsheet software.

### Using Excel:

1. Open `questions.csv` in Excel
2. Make your changes
3. When saving:
   - Click "File" → "Save As"
   - Choose "CSV (Comma delimited) (*.csv)" as file format
   - Click "Save"
   - If Excel warns about features incompatible with CSV, click "Yes" to keep using CSV format
   - If asked about encoding, choose "UTF-8" if available

Important notes:
- Always save as CSV format, not Excel (.xlsx)
- Ensure you maintain the header row: `english,finnish,spanish`
- Keep exactly 25 words/phrases for each language
- Don't use commas within the phrases (they'll break the CSV format)

## Viewing and Printing Cards

1. Open `index.html` in a web browser
2. Browse the correct JSON file
3. Click `Print cards` button

## File Structure

- `bingo.py` - Main Python script for generating cards
- `questions.csv` - Word list in multiple languages
- `index.html` - Web interface for viewing and printing cards
- `bingo.json` - Generated card data (created when running the script)

## Requirements

- Python 3.x
- Modern web browser
- CSV editor (like Excel, Google Sheets, or LibreOffice)

## Troubleshooting

Common issues:

1. **"File not found" error**
   - Make sure `questions.csv` is in the same directory as `bingo.py`

2. **"Language not found" error**
   - Check that your chosen language is a column header in `questions.csv`

3. **Encoding issues (special characters look wrong)**
   - Ensure `questions.csv` is saved with UTF-8 encoding
   - When using Excel, specifically choose UTF-8 encoding when saving

4. **"Need at least 25 words" error**
   - Verify your `questions.csv` has exactly 25 entries for each language


### Cloudflare pages frontend:

Website: https://wedding-bingo.pages.dev
Build output directory: frontend

### Render.com backend

Backend: https://bingo-4at5.onrender.com
rootDir: backend
buildCommand: ./build.sh
startCommand: ./start.sh
envVars: PYTHON_VERSION=3.11.11



`curl -X POST -F "file=@Personalized Wedding Bingo.xlsx" http://localhost:5000/generate-cards`