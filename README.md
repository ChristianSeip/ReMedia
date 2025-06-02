# ReMedia

**ReMedia** is an AI-ready, open-source media deduplication tool.  
It detects duplicate or similar media (images, later videos) based on hash comparison and will evolve to support AI-driven and context-aware similarity analysis.

## 🔍 Features

- Fast hashing with `dhash` and `phash`
- 5 adjustable accuracy levels (1 = very strict, 5 = generous)
- CLI interface with clean architecture
- Duplicate groups are automatically moved to folders
- Modular: Ready for AI analysis and video comparison

## Getting Started

```bash
git clone https://github.com/ChristianSeip/ReMedia.git
cd ReMedia
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
