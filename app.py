import streamlit as st
from dotenv import load_dotenv
from summarizer import summarize_video

load_dotenv()

st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer")
st.write("YouTube URL do — main summary de dunga!")

# Info box
st.info("""
ℹ️ **Supported Videos:**
- ✅ Videos with captions/subtitles (CC button wali)
- ✅ TED Talks, News channels, Tutorials, Lectures
- ❌ Videos without captions not supported

**Tip:** YouTube pe video open karo — agar CC button dikh raha hai toh summary milegi!
""")

url = st.text_input("YouTube URL yahan daalo:", placeholder="https://www.youtube.com/watch?v=...")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("Summary ki language:", ["English", "Hindi", "Hinglish"])
with col2:
    length = st.selectbox("Summary kitni lambi:", ["Short (5 points)", "Medium (10 points)", "Detailed"])

if st.button("📝 Summarize Karo!", type="primary"):
    if url:
        with st.spinner("Video ka transcript le raha hoon... ⏳"):
            result = summarize_video(url, language, length)

        if result["success"]:
            st.success(f"✅ Summary ready! _(Method: {result['method']})_")
            st.subheader("📌 Summary:")
            st.write(result["summary"])
            with st.expander("📄 Full Transcript dekho"):
                st.write(result["transcript"])
        else:
            st.error("❌ Is video ka transcript nahi mila!")
            st.warning("""
            **Possible reasons:**
            - Video pe captions nahi hain
            - Video private hai
            - Video unavailable hai
            
            **Try karo:**
            - TED Talks: youtube.com/@TED
            - News: BBC, NDTV YouTube channels
            - Koi bhi tutorial video
            """)
    else:
        st.warning("⚠️ Pehle URL daalo!")
