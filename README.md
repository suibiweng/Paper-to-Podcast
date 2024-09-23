
# Paper to Podcast Generator

This script processes either a single paper (PDF) file or a folder of papers, summarizes their content using OpenAI's GPT, and generates a podcast-style audio file with a male voice using pyttsx3.

## Features:
- **PDF Folder Input**: Allows processing a folder of PDF files instead of a single file.
- **Detailed Summarization**: Every PDF is summarized in detail, with no need for a `--detailed` flag.
- **Female Voice for Podcast**: Uses `pyttsx3` to convert the summarized text into an MP3 file with a female voice.
- **Customizable Prompts**: You can pass a custom prompt for the summarization process.

## Requirements

To install the necessary packages, run:

```bash
pip install -r requirements.txt
```

### List of Required Packages:
- `pymupdf`: For extracting text from PDFs.
- `pyttsx3`: For converting text to speech (offline).
- `openai`: For accessing the OpenAI GPT API.

## Usage

1. Set your OpenAI API key in the script:
   ```python
   openai.api_key = "your_openai_api_key"
   ```

2. Place the PDFs you want to process in a folder.

3. Run the script:

```bash
python paper_to_podcast.py /path/to/pdf/folder
```

This will:
- Extract text from each PDF.
- Summarize the content into a podcast-friendly script.
- Generate an MP3 file with a female voice for each PDF.

### Custom Prompt

You can also pass a custom prompt:

```bash
python paper_to_podcast.py /path/to/pdf/folder --custom-prompt "Summarize in a more conversational style..."
```
### URL WIP......

paper_to_podcast_url.py 

URL must be from Arxiv, IEEE Xplore, or ACM.





## License

This project is licensed under the MIT License.
