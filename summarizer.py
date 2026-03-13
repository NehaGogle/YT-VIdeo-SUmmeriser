from dotenv import load_dotenv
load_dotenv()
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import assemblyai as aai
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

def get_transcript_from_assemblyai(url):
    try:
        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        
        # Audio download karo temp file mein
        tmp_dir = tempfile.mkdtemp()
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
        audio_path = None
        for f in os.listdir(tmp_dir):
            if f.endswith('.mp3'):
                audio_path = os.path.join(tmp_dir, f)
                break
        
        if not audio_path:
            return None

        # AssemblyAI ko file bhejo
        config = aai.TranscriptionConfig(speech_models=[aai.SpeechModel.universal])
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"AssemblyAI error: {transcript.error}")
            return None
            
        return transcript.text
        
    except Exception as e:
        print(f"AssemblyAI error: {e}")
        return None
    finally:
        # Cleanup
        try:
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))
        except:
            pass

def get_audio_url(url):
    """yt-dlp se audio URL nikalo — download nahi karo"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Audio URL nikalo
            if 'url' in info:
                return info['url']
            # Formats mein dhundo
            for fmt in info.get('formats', []):
                if fmt.get('acodec') != 'none':
                    return fmt['url']
        return None
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return None

def summarize_video(url, language="English", length="Medium (10 points)"):
    video_id = get_video_id(url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL!"}

    # Step 1: Captions try karo
    transcript = get_transcript_from_captions(video_id)
    method = "captions"

    # Step 2: AssemblyAI se try karo
    # Step 2: AssemblyAI se try karo
    if not transcript:
       transcript = get_transcript_from_assemblyai(url)
       method = "assemblyai"

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


