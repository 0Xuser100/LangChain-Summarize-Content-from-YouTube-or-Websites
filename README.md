
---

# 📚 Content Summarizer with Streamlit & LangChain

This application uses **LangChain**, **Groq AI models**, and **Streamlit** to summarize long-form content like YouTube videos and website articles. Users can interact with various language models to generate concise and well-structured summaries.

## ✨ Features
- 🔗 Summarize YouTube videos or any public web page.
- 🎛️ Choose between multiple language models (e.g., `llama3-8b-8192`, `gemma-7b-it`).
- 🔥 Adjustable **temperature** for creative or precise summaries.
- 📋 Set custom word counts for the summary output.
- 💾 Download all chat history as a JSON file for future reference.

## 🚀 Technologies Used
- **Streamlit**: For building the web interface.
- **LangChain**: For managing model prompts and summarization chains.
- **Groq AI Models**: Advanced LLMs for generating summaries.
- **Pytube**: For handling YouTube video metadata and captions.
- **Python**: Backend logic and processing.

---

## 🛠️ Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/0Xuser100/LangChain-Summarize-Content-from-YouTube-or-Websites.git
   cd LangChain-Summarize-Content-from-YouTube-or-Websites
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

5. Open your browser at `http://localhost:8501` to access the app.

---

## 📒 Usage

1. **Enter your Groq API key** in the sidebar.
2. **Paste a YouTube video link** or any public website URL into the input field.
3. Select your preferred model, adjust the settings, and click **"Generate Summary"**.
4. Review the summary output, metadata (for YouTube videos), and download the chat history if needed.

---

## 📂 File Structure

```
.
├── app.py                 # Main application script
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── ... (other files and assets)
```

---

## 🧑‍💻 Contributing
Contributions are welcome! If you’d like to contribute:
1. Fork the repository.
2. Create a new branch (`feature/new-feature`).
3. Submit a pull request.

---

## 🔒 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## 📧 Contact
For any issues or inquiries, feel free to reach out:
- **Author**: Mahmoud Abdelhamid  
- **Email**: [mahmoudabdulhamid22@gmail.com](mahmoudabdulhamid22@gmail.com)  
- **GitHub**: [https://github.com/0Xuser100](https://github.com/0Xuser100)

---

