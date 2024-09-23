# Updated script now includes both single PDF and folder-based processing.

import os
import fitz  # PyMuPDF for PDF extraction
import openai
import pyttsx3
import re
import argparse

# Set up your OpenAI API key
openai.api_key = ""

def extract_cleaned_text_from_pdf(pdf_file_path):
    """
    Extracts cleaned text from a PDF file while:
    - Removing references section.
    - Retaining only relevant numbered sections like Introduction, Related Work, System Design, etc.
    - Removing in-text references in brackets (e.g., [1], [2]).
    """
    with fitz.open(pdf_file_path) as doc:
        text = ""
        title = None

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text

            if page_num == 0:
                title_match = re.search(r'\b[A-Za-z0-9][^\n]+', page_text)
                if title_match:
                    title = title_match.group(0).strip()

        # Remove references
        text = re.sub(r'\[\d+\]', '', text)  # Remove in-text references
        reference_start = re.search(r"\b(references|REFERENCES)\b", text, re.IGNORECASE)
        if reference_start:
            text = text[:reference_start.start()]

    return text.strip(), title

def process_and_summarize_sections_with_gpt(paper_text, custom_prompt=None):
    """
    Use GPT to dynamically identify and summarize sections from the paper in a podcast-friendly format.
    Focuses on key sections: Introduction, Related Work, System Design, User Study, Results and Discussion, and Conclusion.
    """
    chunk_size = 3000
    words = paper_text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    podcast_script = ""
    for chunk in chunks:
        prompt = custom_prompt if custom_prompt else (
            "You are a podcast host summarizing a scientific paper. Focus on key sections such as Introduction, Related Work, "
            "System Design, User Study, Results, Discussion, and Conclusion. Also emphasize the research questions. "
            "Read the title at the start,and dont splt to serveral episodes. Keep it in one."
            "Present the content in a conversational style, engaging the audience and making the research accessible. "
            "Here is the academic text to summarize:\n\n" + chunk
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            podcast_script += response['choices'][0]['message']['content'].strip() + "\n"
        except openai.error.InvalidRequestError as e:
            print(f"Error with GPT request: {e}")
            break

    return podcast_script

def text_to_speech(podcast_script, output_file):
    """
    Converts the cleaned podcast script into an MP3 file using pyttsx3 (offline, free).
    Sets the voice to female if available.
    """
    engine = pyttsx3.init()  # Initialize TTS engine

    # Set properties: speed and volume
    engine.setProperty('rate', 150)  # Speed (default is around 200)
    engine.setProperty('volume', 1)  # Volume (range is 0.0 to 1.0)

    # Get available voices and set a female voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower():  # Set to the first female voice available
            engine.setProperty('voice', voice.id)
            break

    # Save the script as an audio file
    engine.save_to_file(podcast_script, output_file)

    # Run the engine to process the text
    engine.runAndWait()

    print(f'Audio content written to file {output_file}')

def save_text_to_file(text, output_file):
    """
    Saves text content into a text file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

def process_single_pdf(pdf_file_path, custom_prompt=None):
    """
    Process a single PDF file, extracting text, summarizing it, and generating a podcast.
    """
    # Step 1: Extract cleaned text from the PDF
    print(f"Extracting text from {pdf_file_path}...")
    cleaned_text, paper_title = extract_cleaned_text_from_pdf(pdf_file_path)
    if not paper_title:
        paper_title = "podcast_" + os.path.basename(pdf_file_path)
    print(f"Title extracted: {paper_title}")

    # Clean the title to make it a valid file name
    paper_title = re.sub(r'[\\/*?:"<>|]', "_", paper_title)
    mp3_output_file = f"{paper_title}.mp3"
    txt_output_file = f"{paper_title}.txt"

    # Step 2: Use GPT to identify and summarize sections
    print("Generating podcast script...")
    podcast_script = process_and_summarize_sections_with_gpt(cleaned_text, custom_prompt=custom_prompt)

    # Step 3: Save the podcast script to a text file
    print(f"Saving podcast script to {txt_output_file}...")
    save_text_to_file(podcast_script, txt_output_file)

    # Step 4: Convert the script into an MP3 file using a female voice
    print(f"Converting podcast script to audio ({mp3_output_file})...")
    text_to_speech(podcast_script, mp3_output_file)
    print("Podcast generation complete.")

def process_pdf_folder(folder_path, custom_prompt=None):
    """
    Process a folder of PDF files, extracting text, summarizing it, and generating podcasts.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(folder_path, filename)

            # Process each PDF in the folder
            process_single_pdf(pdf_file_path, custom_prompt)

def process_input_path(input_path, custom_prompt=None):
    """
    Determines whether the input path is a folder or a single PDF and processes accordingly.
    """
    if os.path.isdir(input_path):
        process_pdf_folder(input_path, custom_prompt=custom_prompt)
    elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
        process_single_pdf(input_path, custom_prompt=custom_prompt)
    else:
        print(f"Invalid input path: {input_path}. Please provide a folder or a valid PDF file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF(s) and generate podcast(s)")
    parser.add_argument("input_path", type=str, help="Path to a single PDF file or a folder containing PDF files")
    parser.add_argument("--custom-prompt", type=str, help="Provide a custom prompt for summarization", default=None)
    args = parser.parse_args()

    input_path = args.input_path
    custom_prompt = args.custom_prompt

    # Process input path (folder or single PDF)
    process_input_path(input_path, custom_prompt=custom_prompt)

