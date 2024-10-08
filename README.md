
# Paper to Podcast Generator

This script processes either a single paper (PDF) file or a folder of papers, summarizes their content using OpenAI's GPT, and generates a podcast-style audio file with a male voice using pyttsx3.

## Features:
- **PDF Folder Input**: Allows processing a folder of PDF files instead of a single file.
- **Voice for Podcast**: Uses `pyttsx3` to convert the summarized text into an MP3 file with a voice.
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


## Getting OpenAI ChatGPT API Key

Follow these steps to get an API key for OpenAI's ChatGPT.

1. Sign Up or Log In

Visit [OpenAI's platform](https://platform.openai.com/signup) and either create a new account or log in if you already have one.

2. Access the API Keys Section

Once logged in, follow these steps:
- Click on your profile avatar in the top-right corner.
- From the dropdown, select **"API keys"**.

3. Create a New API Key

- Click **"Create new secret key"**.
- This will generate a new API key for you.

4. Save the API Key

- Copy the API key and store it securely. You will **not** be able to view it again later.
- If you lose the API key, you will need to generate a new one.
Once you have the API key, you can use it to access OpenAI's API and integrate it into your applications.

For more information, visit the [OpenAI API Documentation](https://platform.openai.com/docs).




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

Run the script:
```bash
python paper_to_podcast_url.py "https://ieeexplore.ieee.org/document/XXXXX"
```

