import streamlit as st
from dotenv import load_dotenv
from summarizer import summarize_video

load_dotenv()

st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer")
st.write("YouTube URL do — main summary de dunga!")

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
            st.success("✅ Summary ready!")

            st.subheader("📌 Summary:")
            st.write(result["summary"])

            with st.expander("📄 Full Transcript dekho"):
                st.write(result["transcript"])
        else:
            st.error(f"❌ Error: {result['error']}")
    else:
        st.warning("⚠️ Pehle URL daalo!")
