# ReMedia

**ReMedia** is an AI-ready, open-source media deduplication tool.  
It detects duplicate or similar media (images, and later videos) using perceptual hashing and is prepared to support AI-driven, context-aware similarity detection.

## Key Features

- Fast hashing with dhash and phash
- 5 adjustable accuracy levels (1 = very strict, 5 = generous)
- CLI interface with clean architecture
- Duplicate groups are automatically moved to folders
- Modular: Ready for AI analysis and video comparison

## Getting Started

### Requirements
- Python 3.10 or later

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ChristianSeip/ReMedia.git
cd ReMedia

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate

# 3. Install the package

# For normal usage (recommended)
pip install .

# For development (if you want to modify the code)
pip install -e .

# 4. Run the tool
remedia
```