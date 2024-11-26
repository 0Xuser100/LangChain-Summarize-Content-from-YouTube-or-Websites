import urllib3
import validators
import streamlit as st
import yt_dlp as ytdlp
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document  # Import Document class
import io

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to extract video information using yt-dlp
def extract_video_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
        }
        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'No title available')
            video_description = info_dict.get('description', 'No description available')
            return video_title, video_description
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return None, None

# Streamlit App
st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")
st.title("🦜 LangChain: Summarize Text From YT or Website")
st.subheader('Summarize URL')

# Get the Groq API Key and URL (YT or website) to be summarized
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value="", type="password")

# Dropdown to select the model
model_option = st.selectbox(
    "Select Groq Model",
    ["gemma2-9b-it", "llama3-groq-70b-8192-tool-use-preview", "Llama-3.2-90b-text-preview", "Mixtral-8x7b-32768"]
)

generic_url = st.text_input("URL", label_visibility="collapsed")

# Selected Groq Model Using Groq API
llm = ChatGroq(model=model_option, groq_api_key=groq_api_key)

prompt_template = """
Provide a summary of the following content in 300 words:
Content: {text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

if st.button("Summarize the Content from YT or Website"):
    # Validate all the inputs
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide the information to get started")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL. It can be a YT video URL or website URL.")
    else:
        try:
            with st.spinner("Waiting..."):
                # Loading the website or YT video data
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    video_title, video_description = extract_video_info(generic_url)
                    if not video_title:
                        st.error("Unable to extract video info.")
                    else:
                        # Wrap the video description in a Document object
                        docs = [Document(page_content=video_description, metadata={"source": generic_url})]
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url],
                        ssl_verify=True,  # Ensure SSL verification
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                    docs = loader.load()

                # Chain for Summarization
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary = chain.invoke(docs)  # Use invoke() instead of run()

                st.success("Summarized Content:")
                st.markdown(f"### Summary:")
                
                # Displaying the summary as clickable link (Markdown)
                summary_with_link = f"[Click here to read the full summary](data:text/plain;charset=utf-8,{output_summary})"
                st.markdown(summary_with_link, unsafe_allow_html=True)

                # Option to download the summarized content
                download_button = st.button("Download Full Summary")
                if download_button:
                    # Convert summary to a downloadable text file
                    summary_text = output_summary
                    byte_data = summary_text.encode()
                    buffer = io.BytesIO(byte_data)

                    st.download_button(
                        label="Download Summary as Text File",
                        data=buffer,
                        file_name="summarized_content.txt",
                        mime="text/plain"
                    )

        except Exception as e:
            st.exception(f"Exception: {e}")
