import requests
import fitz  # PyMuPDF for PDF extraction
import openai
import pyttsx3
import re
import argparse
import os
from bs4 import BeautifulSoup

# Set up your OpenAI API key
openai.api_key = ""

def download_pdf_from_arxiv(arxiv_url, output_pdf_path):
    """
    Downloads a PDF from an Arxiv URL.
    """
    pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf"
    response = requests.get(pdf_url)
    
    if response.status_code == 200:
        with open(output_pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF from {pdf_url}")
        return output_pdf_path
    else:
        raise Exception(f"Failed to download PDF from {pdf_url}. HTTP Status: {response.status_code}")

def download_pdf_from_ieee(ieee_url, output_pdf_path):
    """
    Parses the IEEE Xplore page to find the PDF link and downloads the PDF.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(ieee_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the link to the PDF
        pdf_link = soup.find('a', href=re.compile(r'pdf'))
        
        if pdf_link:
            full_pdf_url = "https://ieeexplore.ieee.org" + pdf_link['href']
            pdf_response = requests.get(full_pdf_url, headers=headers)
            
            if pdf_response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"Downloaded PDF from {full_pdf_url}")
                return output_pdf_path
            else:
                raise Exception(f"Failed to download PDF from {full_pdf_url}. HTTP Status: {pdf_response.status_code}")
        else:
            raise Exception("Could not find the PDF link on the IEEE Xplore page.")
    else:
        raise Exception(f"Failed to access IEEE Xplore page. HTTP Status: {response.status_code}")

def download_pdf_from_acm(acm_url, output_pdf_path):
    """
    Parses the ACM page to find the PDF link and downloads the PDF.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(acm_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the link to the PDF
        pdf_link = soup.find('a', href=re.compile(r'/doi/pdf/'))
        
        if pdf_link:
            full_pdf_url = "https://dl.acm.org" + pdf_link['href']
            pdf_response = requests.get(full_pdf_url, headers=headers)
            
            if pdf_response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"Downloaded PDF from {full_pdf_url}")
                return output_pdf_path
            else:
                raise Exception(f"Failed to download PDF from {full_pdf_url}. HTTP Status: {pdf_response.status_code}")
        else:
            raise Exception("Could not find the PDF link on the ACM page.")
    else:
        raise Exception(f"Failed to access ACM page. HTTP Status: {response.status_code}")

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

        # Remove in-text references like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)

        # Remove references section
        reference_start = re.search(r"\b(references|REFERENCES)\b", text, re.IGNORECASE)
        if reference_start:
            text = text[:reference_start.start()]

    return text.strip(), title

def process_and_summarize_sections_with_gpt(paper_text, custom_prompt=None):
    """
    Use GPT to dynamically identify and summarize sections from the paper in a podcast-friendly format.
    """
    chunk_size = 3000
    words = paper_text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    podcast_script = ""
    for chunk in chunks:
        prompt = custom_prompt if custom_prompt else (
            "You are a podcast host summarizing a scientific paper. Focus on key sections such as Introduction, Related Work, "
            "System Design, User Study, Results, Discussion, and Conclusion. Also emphasize the research questions. "
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
        if "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    # Save the script as an audio file
    engine.save_to_file(podcast_script, output_file)
    engine.runAndWait()
    print(f'Audio content written to file {output_file}')

def save_text_to_file(text, output_file):
    """
    Saves text content into a text file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

def process_url(url, custom_prompt=None):
    """
    Processes a URL, downloads the corresponding PDF, extracts text, summarizes it, and generates a podcast.
    """
    pdf_output_path = "downloaded_paper.pdf"
    
    if "arxiv.org" in url:
        download_pdf_from_arxiv(url, pdf_output_path)
    elif "ieeexplore.ieee.org" in url:
        download_pdf_from_ieee(url, pdf_output_path)
    elif "dl.acm.org" in url:
        download_pdf_from_acm(url, pdf_output_path)
    else:
        raise ValueError("URL must be from Arxiv, IEEE Xplore, or ACM.")

    # Extract text from the downloaded PDF
    cleaned_text, paper_title = extract_cleaned_text_from_pdf(pdf_output_path)
    if not paper_title:
        paper_title = "podcast_" + os.path.basename(pdf_output_path)
    
    # Clean the title to make it a valid file name
    paper_title = re.sub(r'[\\/*?:"<>|]', "_", paper_title)
    mp3_output_file = f"{paper_title}.mp3"
    txt_output_file = f"{paper_title}.txt"

    # Use GPT to summarize the sections
    podcast_script = process_and_summarize_sections_with_gpt(cleaned_text, custom_prompt=custom_prompt)

    # Save the podcast script to a text file
    save_text_to_file(podcast_script, txt_output_file)

    # Convert the script into an MP3 file
    text_to_speech(podcast_script, mp3_output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a paper from Arxiv, IEEE Xplore, or ACM, summarize it, and generate a podcast")
    parser.add_argument("url", type=str, help="URL of the paper (Arxiv, IEEE Xplore, or ACM)")
    parser.add_argument("--custom-prompt", type=str, help="Provide a custom prompt for summarization", default=None)
    args = parser.parse_args()

    url = args.url
    custom_prompt = args.custom_prompt

    # Process the URL
    process_url(url, custom_prompt=custom_prompt)
