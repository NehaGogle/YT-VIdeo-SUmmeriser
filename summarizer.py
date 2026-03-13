from dotenv import load_dotenv
load_dotenv()
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import assemblyai as aai
import os
import re

def get_video_id(url):
    patterns = [r'v=([^&]+)', r'youtu\.be/([^?]+)', r'embed/([^?]+)']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_from_captions(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        return " ".join([t.text for t in fetched])
    except:
        return None

def get_transcript_from_assemblyai(url):
    try:
        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        config = aai.TranscriptionConfig(speech_models=[aai.SpeechModel.universal])
        transcriber = aai.Transcriber(config=config)
        # Direct YouTube URL do — no download needed!
        transcript = transcriber.transcribe(url)
        if transcript.status == aai.TranscriptStatus.error:
            print(f"AssemblyAI error: {transcript.error}")
            return None
        return transcript.text
    except Exception as e:
        print(f"AssemblyAI error: {e}")
        return None

def summarize_video(url, language="English", length="Medium (10 points)"):
    video_id = get_video_id(url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL!"}

    # Step 1: Captions try karo
    transcript = get_transcript_from_captions(video_id)
    method = "captions"

    # Step 2: AssemblyAI direct URL
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

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    prompt = PromptTemplate(
        template="""
        Neeche ek YouTube video ka transcript hai.
        Isko {language} mein {length} summarize karo.
        Important points highlight karo.

        Transcript: {transcript}

        Summary:
        """,
        input_variables=["language", "length", "transcript"]
    )
    chain = prompt | llm | StrOutputParser()

    summary = chain.invoke({
        "language": language,
        "length": length_map.get(length, "10 key points mein"),
        "transcript": transcript[:10000]
    })

    return {
        "success": True,
        "summary": summary,
        "transcript": transcript[:2000] + "..." if len(transcript) > 2000 else transcript,
        "method": method
    }
