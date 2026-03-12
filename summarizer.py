from dotenv import load_dotenv
load_dotenv()
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from groq import Groq
import yt_dlp
import re
import os
import tempfile

def get_video_id(url):
    patterns = [
        r'v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'embed/([^?]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_from_captions(video_id):
    """Pehle captions try karo — fast hai"""
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        text = " ".join([t.text for t in fetched])
        return text
    except:
        return None

def get_transcript_from_whisper(url):
    """Captions nahi mile toh Whisper se audio transcribe karo"""
    tmp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(tmp_dir, "audio.mp3")
    
    try:
        # Audio download karo
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmp_dir, 'audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # MP3 file dhundo
        for f in os.listdir(tmp_dir):
            if f.endswith('.mp3'):
                audio_path = os.path.join(tmp_dir, f)
                break
        
        # Groq Whisper se transcribe karo
        client = Groq()
        with open(audio_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        
        return transcription
        
    except Exception as e:
        print(f"Whisper error: {e}")
        return None
    finally:
        # Cleanup
        for f in os.listdir(tmp_dir):
            try:
                os.remove(os.path.join(tmp_dir, f))
            except:
                pass

def summarize_video(url, language="English", length="Medium (10 points)"):
    video_id = get_video_id(url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL!"}

    # Pehle captions try karo
    transcript = get_transcript_from_captions(video_id)
    method = "captions"
    
    # Captions nahi mile toh Whisper
    if not transcript:
        transcript = get_transcript_from_whisper(url)
        method = "whisper"
    
    if not transcript:
        return {"success": False, "error": "Transcript nahi mila! Video private ya unavailable hai."}

    length_map = {
        "Short (5 points)": "5 key points mein",
        "Medium (10 points)": "10 key points mein",
        "Detailed": "detailed paragraphs mein"
    }
    length_instruction = length_map.get(length, "10 key points mein")

    prompt_template = """
    Neeche ek YouTube video ka transcript hai.
    Isko {language} mein {length} summarize karo.
    Important points highlight karo.
    
    Transcript:
    {transcript}
    
    Summary:
    """

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["language", "length", "transcript"]
    )
    chain = prompt | llm | StrOutputParser()

    max_chars = 10000
    trimmed_transcript = transcript[:max_chars] if len(transcript) > max_chars else transcript

    summary = chain.invoke({
        "language": language,
        "length": length_instruction,
        "transcript": trimmed_transcript
    })

    return {
        "success": True,
        "summary": summary,
        "transcript": transcript[:2000] + "..." if len(transcript) > 2000 else transcript,
        "method": method
    }
