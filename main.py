import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from pytube import YouTube
import re
import json

# Page Configuration and Styling
st.set_page_config(
    page_title="Content Summarizer",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def load_youtube_content(url):
    """Load YouTube content with enhanced error handling"""
    try:
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
        return loader.load()
    except Exception as e:
        try:
            video_id = extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(clean_url)
            
            transcript = yt.captions.get_by_language_code('en')
            if transcript:
                text = transcript.generate_srt_captions()
            else:
                text = f"Title: {yt.title}\nDescription: {yt.description}"
            
            from langchain.schema import Document
            return [Document(
                page_content=text,
                metadata={
                    "title": yt.title,
                    "url": clean_url,
                    "length": yt.length,
                    "author": yt.author
                }
            )]
        except Exception as inner_e:
            raise Exception(f"Failed to load YouTube content: {str(inner_e)}")


# Chat history storage
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Store chat history


# App Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("📚 Content Summarizer")
    st.markdown("Transform long content into concise summaries")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Groq API Key", value="", type="password")
    st.markdown("---")
    st.markdown("### Model Selection")
    model_selection = st.selectbox(
        "Select a Groq Model:",
        ["llama3-8b-8192", "gemma-7b-it", "llama-3.2-90b-text-preview"],
        help="Choose one of the available models for summarization."
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1,
                             help="Higher values make the output more creative")
    word_count = st.number_input("Summary Word Count", 100, 500, 300, 50,
                                 help="Number of words in the summary")

# Main Content Area
st.markdown("### 🔗 Enter URL")
url_placeholder = "Enter YouTube URL or website link..."
generic_url = st.text_input("URL", placeholder=url_placeholder, label_visibility="collapsed")

# Initialize LLM
llm = ChatGroq(
    model=model_selection,
    groq_api_key=groq_api_key,
    temperature=temperature
)

# Prompt Template
prompt_template = f"""
Provide a clear and concise summary of the following content in {word_count} words:
Content: {{text}}

The summary should:
- Capture the main ideas and key points
- Be well-structured and easy to read
- Maintain the original meaning and context
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

# Process Button
if st.button("🚀 Generate Summary"):
    if not groq_api_key.strip():
        st.error("🔑 Please provide your Groq API key in the sidebar")
    elif not generic_url.strip():
        st.error("🔗 Please enter a URL to summarize")
    elif not validators.url(generic_url):
        st.error("❌ Please enter a valid URL (YouTube video or website)")
    else:
        try:
            with st.spinner("🔄 Processing content..."):
                # Content Type Detection
                is_youtube = "youtube.com" in generic_url or "youtu.be" in generic_url
                content_type = "YouTube Video" if is_youtube else "Website"
                
                # Progress Indicator
                progress_text = st.empty()
                progress_text.markdown(f"📥 Loading {content_type} content...")
                
                # Load Content
                if is_youtube:
                    docs = load_youtube_content(generic_url)
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url],
                        ssl_verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                    docs = loader.load()
                
                progress_text.markdown("🤖 Generating summary...")
                
                # Generate Summary
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                summary = chain.run(docs)
                
                # Save interaction to chat history
                st.session_state.chat_history.append({
                    "input": generic_url,
                    "summary": summary
                })
                
                # Display Results
                st.markdown("### 📋 Summary")
                st.markdown(f"*Source: {content_type}*")
                st.markdown("""<div class="success-box">""", unsafe_allow_html=True)
                st.write(summary)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Metadata Display
                if is_youtube and hasattr(docs[0], 'metadata'):
                    st.markdown("### ℹ️ Video Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Title:** {docs[0].metadata.get('title', 'N/A')}")
                        st.markdown(f"**Author:** {docs[0].metadata.get('author', 'N/A')}")
                    with col2:
                        length = docs[0].metadata.get('length', 0)
                        st.markdown(f"**Duration:** {length//60}:{length%60:02d}")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.markdown("Please try again or contact support if the issue persists.")

# Download Chat History Button
if st.sidebar.button("💾 Download Chat History"):
    if st.session_state.chat_history:
        history_json = json.dumps(st.session_state.chat_history, indent=4)
        st.sidebar.download_button(
            label="Download",
            data=history_json,
            file_name="chat_history.json",
            mime="application/json"
        )
    else:
        st.sidebar.info("No chat history to download.")
