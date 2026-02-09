# Agentic Hiring System

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Hugging Face token:
   ```
   HF_TOKEN=your_actual_token_here
   ```
   
   Get your token from: https://huggingface.co/settings/tokens

3. **Add your data:**
   - Place job description PDF in `data/` folder
   - Place candidate resumes in `data/` folder

4. **Run the system:**
   ```bash
   python main.py
   ```

## Security Notes

- **Never commit `.env` file** - it's already in `.gitignore`
- **Never commit actual tokens** - use environment variables
- The `.env.example` file shows the required variables without sensitive data

## Output Files

The system generates:
- `analysis_output.pdf` - Privacy-protected parsed data
- `candidate_ranking_report.pdf` - Comprehensive ranking report
- `candidate_ranking.txt` - Text summary of rankings
