import streamlit as st
import google.generativeai as genai
#from gtts import gTTS
import base64
import PyPDF2
import time
import os
import hashlib
import glob
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
import tempfile
import re
import pandas as pd
import plotly.express as px
import random
import textwrap
import requests
from bs4 import BeautifulSoup

# Configure Gemini
genai.configure(api_key="AIzaSyA0PooYvobKUo1s65GElprR5RteDFRpNEg")
model = genai.GenerativeModel("gemini-1.5-flash")

# Set page configuration
st.set_page_config(
    page_title="AI Interview Coach", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.update(
        {
            "stage": 0,
            "questions": [],
            "current_q": 0,
            "answers": [],
            "resume_text": "",
            "audio_played": False,
            "processing": False,
            "job_role": "",
            "transcribed_text": "",
            "difficulty": "medium",
            "question_types": [],
            "interview_type": "Technical Screening",
            "time_per_question": 60,
            "start_time": None,
            "skill_scores": {},
            "previous_answers": [],
            "current_answer": "",
            "force_rerun": False,
            "mode_selected": False,
            "chat_history": [],
            "chat_input": "",
            "show_chat": False,
            "feedback_complete": False,
            "feedback_chat_history": [],
            "last_feedback": "",
            "transcription_success": None
        }
    )

# Custom CSS for background and styling
def set_background_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://www.pixelstalk.net/wp-content/uploads/2016/10/3D-black-diamond-free-desktop-wallpaper-1920x1080.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .main-content {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header { 
            font-size: 32px !important; 
            color: #2b3595 !important; 
            padding: 10px; 
            text-align: center;
        }
        .question { 
            font-size: 20px !important; 
            color: #e14594 !important; 
            padding: 15px;
            background: #f0f2f6;
            border-radius: 10px;
            margin: 10px 0;
        }
        .feedback { 
            background-color: rgba(0, 0, 0, 0.9) !important; 
            color: #ffffff !important;
            padding: 20px !important; 
            border-radius: 10px !important;
            border: 1px solid #4a4a4a !important;
            margin: 20px 0;
        }
        .stAudio { display: none; }
        .progess-text { font-size: 16px !important; }
        .transcript-box {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            background-color: #f9f9f9;
        }
        .difficulty-easy { color: #28a745 !important; font-weight: bold; }
        .difficulty-medium { color: #ffc107 !important; font-weight: bold; }
        .difficulty-hard { color: #dc3545 !important; font-weight: bold; }
        .difficulty-general { color: #17a2b8 !important; font-weight: bold; }
        .skill-meter {
            margin-bottom: 15px;
        }
        .skill-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .answer-history {
            border-left: 3px solid #e14594;
            padding-left: 10px;
            margin: 15px 0;
        }
        .mode-selector {
            text-align: center;
            margin: 30px 0;
        }
        .transcription-error {
            color: #dc3545;
            font-weight: bold;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .button-primary {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
        }
        .button-secondary {
            background-color: #2196F3 !important;
            color: white !important;
            border-radius: 5px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
        }
        .resource-links {
            margin-top: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #6c757d;
        }
        .resource-link {
            display: block;
            margin: 5px 0;
            color: #0d6efd;
            text-decoration: none;
        }
        .resource-link:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background_image()

# Chatbot functions
def get_webpage_content(url):
    """Fetch and extract main content from a webpage"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        main_content = soup.find(["main", "article"]) or soup
        paragraphs = main_content.find_all(["p", "h1", "h2", "h3", "h4", "li"])
        content = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        return textwrap.shorten(content, width=10000, placeholder="... [content truncated]")
    except Exception as e:
        st.error(f"Error fetching URL content: {e}")
        return None

def generate_resource_links(topic):
    """Generate search links for resources with improved GFG link"""
    topic_clean = topic.replace(" ", "%20")  # Better URL encoding
    
    # Improved GFG link that works more reliably
    gfg_link = f"https://www.geeksforgeeks.org/?s={topic_clean}"
    
    return {
        "GeeksforGeeks": gfg_link,
        "YouTube Tutorials": f"https://www.youtube.com/results?search_query={topic_clean}+interview+questions",
        "Google Scholar": f"https://scholar.google.com/scholar?q={topic_clean}",
        "LinkedIn Learning": f"https://www.linkedin.com/learning/search?keywords={topic_clean}",
        "Stack Overflow": f"https://stackoverflow.com/search?q={topic_clean}",
        "MDN Web Docs": f"https://developer.mozilla.org/search?q={topic_clean}",
    }

def generate_chat_response(user_input, is_url=False):
    """Generate response using Gemini Pro"""
    try:
        if is_url:
            content = get_webpage_content(user_input)
            if not content:
                return None, None

            prompt = f"""Analyze this webpage content and provide:
            1. A comprehensive summary
            2. Potential interview questions from this content
            3. Best ways to answer those questions in interviews
            4. Main topics covered
            
            Content: {content}
            
            Format your response with these sections:
            ### Summary
            ### Interview Questions
            ### Answering Strategies
            ### Main Topics
            """
        else:
            prompt = f"""Act as a career coach. For this query: "{user_input}", provide:
            1. Detailed explanation
            2. How to answer in interviews (structure, keywords, examples)
            3. Related concepts to study
            4. Main topic
            
            Format your response with these sections:
            ### Explanation
            ### Interview Response Guide
            ### Related Concepts
            ### Main Topic
            """

        response = model.generate_content(prompt)
        main_topic = None
        
        # Try to extract main topic from response
        try:
            if "### Main Topic" in response.text:
                main_topic = response.text.split("### Main Topic")[1].strip().split("\n")[0].strip()
            elif "### Main Topics" in response.text:
                main_topic = response.text.split("### Main Topics")[1].strip().split("\n")[0].strip()
        except:
            main_topic = None

        return response.text, main_topic
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return None, None

def parse_chat_response(response_text, is_url=False):
    """Parse the AI response into structured sections"""
    sections = {
        "summary": "",
        "explanation": "",
        "interview": "",
        "resources": "",
        "topic": "",
    }

    current_section = None
    for line in response_text.split("\n"):
        line = line.strip()
        if line.startswith("### Summary"):
            current_section = "summary"
        elif line.startswith("### Explanation"):
            current_section = "explanation"
        elif line.startswith("### Interview") or line.startswith("### Answering"):
            current_section = "interview"
        elif line.startswith("### Related Concepts") or line.startswith("### Main Topics"):
            current_section = "resources"
        elif line.startswith("### Main Topic"):
            current_section = "topic"
        elif current_section and line:
            sections[current_section] += line + "\n\n"

    return sections

def feedback_chatbot():
    """Minimal feedback chatbot that appears after feedback"""
    if st.session_state.get('feedback_complete'):
        # Chat interface
        if prompt := st.chat_input("Ask about your feedback...", key="feedback_chat"):
            st.session_state.feedback_chat_history = st.session_state.get('feedback_chat_history', [])
            st.session_state.feedback_chat_history.append({"role": "user", "content": prompt})
            
            # Generate response
            with st.spinner("Thinking..."):
                response = model.generate_content(
                    f"Based on this interview feedback, answer this question: {prompt}\n\n"
                    f"Feedback Context:\n{st.session_state.get('last_feedback', '')}\n\n"
                    "Provide specific, actionable advice."
                )
                reply = response.text
            
            st.session_state.feedback_chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        
        # Display chat history
        for msg in st.session_state.get('feedback_chat_history', []):
            st.chat_message(msg["role"]).write(msg["content"])

# Chatbot UI Component - Simplified Interface
def chat_component():
    if st.session_state.stage == "study":
        st.markdown("## 📚 Study & Preparation Mode")

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], tuple):
                    # Handle content with links
                    text_content, links = message["content"]
                    st.markdown(text_content)
                    if links:
                        st.markdown('<div class="resource-links"><strong>📚 Recommended Resources:</strong>', unsafe_allow_html=True)
                        for name, url in links.items():
                            st.markdown(f'<a class="resource-link" href="{url}" target="_blank">{name}</a>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

        # Centered chat input box
        st.markdown(
            """
            <style>
            .stTextInput > div {
                margin: 0 auto;
                max-width: 600px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Text input for user prompt
        prompt = st.text_input("Ask me anything about interviews...", key="chat_input")

        # Check if the prompt is new and hasn't been processed yet
        if prompt and ("last_prompt" not in st.session_state or st.session_state.last_prompt != prompt):
            st.session_state.last_prompt = prompt  # Store the last prompt to avoid duplication

            # Append user input to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    is_url = prompt.startswith("http")
                    response_text, main_topic = generate_chat_response(prompt, is_url)

                    if response_text:
                        sections = parse_chat_response(response_text, is_url)
                        response_content = ""
                        resource_links = None

                        if sections.get("summary"):
                            response_content += f"**Summary**\n{sections['summary']}\n\n"
                        if sections.get("explanation"):
                            response_content += f"**Explanation**\n{sections['explanation']}\n\n"
                        if sections.get("interview"):
                            response_content += f"**Interview Guidance**\n{sections['interview']}\n\n"
                        if sections.get("resources"):
                            response_content += f"**Related Concepts**\n{sections['resources']}\n\n"

                        # Generate resource links if we have a main topic
                        if main_topic:
                            resource_links = generate_resource_links(main_topic)

                        st.markdown(response_content)

                        # Display resource links if available
                        if resource_links:
                            st.markdown('<div class="resource-links"><strong>📚 Recommended Resources:</strong>', unsafe_allow_html=True)
                            for name, url in resource_links.items():
                                st.markdown(f'<a class="resource-link" href="{url}" target="_blank">{name}</a>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Store both content and links in chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": (response_content, resource_links)
                        })
                    else:
                        st.error("Sorry, I couldn't generate a response. Please try again.")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Sorry, I couldn't generate a response. Please try again."
                        })

            # Mark the input as processed
            st.session_state["input_processed"] = True

# Interview functions
def extract_skills(resume_text):
    """Extract skills from resume text using Gemini"""
    prompt = f"""
    Extract technical and professional skills from this resume text.
    Return ONLY a comma-separated list of skills, nothing else.
    
    Resume Text:
    {resume_text[:3000]}
    """
    response = model.generate_content(prompt)
    skills = response.text.strip().split(",")
    return [skill.strip() for skill in skills if skill.strip()]

def get_job_role_prompt(role, difficulty, interview_type):
    difficulty_map = {
        "easy": "basic and fundamental",
        "medium": "intermediate level with some scenario-based",
        "hard": "advanced and challenging"
    }
    
    type_map = {
        "Technical Screening": "Focus on technical skills and problem-solving",
        "Behavioral": "Focus on behavioral and situational questions using STAR method",
        "Full Loop": "Include both technical and behavioral questions"
    }
    
    return (
        f"Generate 5 {difficulty_map[difficulty]} interview questions for a {role} position. "
        f"{type_map[interview_type]}. "
        "Return only the question text without any numbering, explanations or markdown."
    )

def generate_general_questions(skills):
    prompt = f"""
    Generate 5 basic general interview questions that might be asked about these skills: {', '.join(skills)}.
    These should be questions an interviewer might ask to verify the candidate actually knows these skills.
    Return only the question text without any numbering or explanations.
    """
    response = model.generate_content(prompt)
    return [q.strip() for q in response.text.split("\n") if q.strip()]

def generate_questions(prompt):
    response = model.generate_content(prompt)
    return [q.strip() for q in response.text.split("\n") if q.strip()]

def transcribe_audio(audio_bytes):
    """Enhanced audio transcription with error handling"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_filename = tmp_file.name
    
    r = sr.Recognizer()
    
    try:
        with sr.AudioFile(tmp_filename) as source:
            # Adjust for ambient noise and read the entire file
            r.adjust_for_ambient_noise(source)
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            st.session_state.transcription_success = True
            return text
    except sr.UnknownValueError:
        st.session_state.transcription_success = False
        return "Could not understand audio - please try again or type your answer"
    except sr.RequestError as e:
        st.session_state.transcription_success = False
        return f"Error with the speech recognition service; {e}"
    except Exception as e:
        st.session_state.transcription_success = False
        return f"Error processing audio: {str(e)}"
    finally:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

def process_resume(resume):
    try:
        if resume.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(resume)
            return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        elif resume.type == "text/plain":
            content = resume.getvalue()
            for encoding in ["utf-8", "utf-16", "latin-1", "cp1252"]:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            st.error("Could not decode text file.")
            return None

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def update_skill_assessment(answers):
    """Analyze answers and update skill scores"""
    analysis = model.generate_content(
        f"Analyze these interview answers for skill levels: {answers}\n"
        "Return Python dict with: {\n"
        "  'skill1': score1,\n"
        "  'skill2': score2\n"
        "} where scores are 1-5. Only return the dict."
    )
    try:
        new_scores = eval(analysis.text)
        for skill, score in new_scores.items():
            if skill in st.session_state.skill_scores:
                st.session_state.skill_scores[skill] = round((st.session_state.skill_scores[skill] + score) / 2, 1)
            else:
                st.session_state.skill_scores[skill] = score
    except Exception as e:
        st.error(f"Skill assessment error: {str(e)}")

# Add Back Button Logic
def add_back_button():
    """Add a back button to navigate to the previous stage."""
    if st.session_state.stage > 0:
        if st.button("⬅️ Back", key=f"back_button_{st.session_state.stage}"):
            st.session_state.stage -= 1
            st.session_state.current_q = 0  # Reset current question if going back
            st.rerun()

# Main App UI
def main():
    st.markdown(
        '<div class="header">🧑💼 AI Interview Coach</div>', unsafe_allow_html=True
    )

    # Show chat component in study mode
    if st.session_state.stage == "study":
        chat_component()
        
        if st.button("← Back to mode selection"):
            st.session_state.mode_selected = False
            st.session_state.stage = 0
            st.session_state.chat_history = []
            st.rerun()
        return

    # Initial mode selection
    if not st.session_state.mode_selected:
        with st.container():
            st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
            st.markdown("### Choose your preparation mode:")

            # Divide the page into two parts (left and right)
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown("The Practice Mock Interview mode simulates a realistic interview experience: it analyzes your resume, generates role-specific questions based on selected difficulty and interview type (technical/behavioral), allows voice/text responses with transcription,and delivers comprehensive feedback with strengths/improvement areas")
                if st.button("🎤 Practice Mock Interview", 
                             key="interview_mode", 
                             help="Get realistic interview practice with feedback", 
                             use_container_width=False,  # Reduce button width
                             type="primary"):
                    st.session_state.mode_selected = True
                    st.session_state.stage = 0
                    st.rerun()

            with col2:
                st.markdown("The Study & Prepare mode acts as an interactive learning companion: its chatbot answers technical/career questions, analyzes URLs to extract key concepts, generates tailored interview questions/answers, and provides curated learning resources (GeeksforGeeks, YouTube, etc.) based on the topic being discussed, helping users build knowledge before attempting mock interviews.")
                if st.button("📚 Study & Prepare", 
                             key="study_mode", 
                             help="Learn concepts and practice answers", 
                             use_container_width=False):  # Reduce button width
                    st.session_state.mode_selected = True
                    st.session_state.stage = "study"
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        return

    # Interview mode stages
    # Stage 0: Resume Upload
    if st.session_state.stage == 0:
        # Add Back button to return to mode selection
        if st.button("⬅️ Back to Mode Selection", key="back_to_mode_selection"):
            st.session_state.mode_selected = False
            st.session_state.stage = 0
            st.session_state.resume_text = ""
            st.rerun()

        with st.container():
            st.subheader("📁 Step 1: Upload Your Resume")
            resume = st.file_uploader(
                "", type=["pdf", "txt"], label_visibility="collapsed"
            )
            if resume:
                with st.spinner("🔍 Analyzing your resume..."):
                    resume_text = process_resume(resume)
                    if resume_text:
                        st.session_state.update(
                            {
                                "resume_text": resume_text,
                                "stage": 1,
                            }
                        )
                        st.rerun()

    # Stage 1: Job Role Selection and Difficulty
    elif st.session_state.stage == 1:
        add_back_button()  # Add Back button
        with st.container():
            st.subheader("💼 Step 2: Interview Setup")
            predefined_roles = [
                "Software Engineer",
                "Data Analyst", 
                "Marketing Manager",
                "Project Manager",
                "Other (Specify Below)"
            ]
            selected = st.radio(
                "Choose a job role:",
                predefined_roles,
                index=4 if st.session_state.job_role else 0
            )
            custom_role = ""
            if selected == "Other (Specify Below)":
                custom_role = st.text_input("Enter your desired job role:")
            st.session_state.interview_type = st.radio(
                "Interview Format",
                ["Technical Screening", "Behavioral", "Full Loop"],
                index=0,
                horizontal=True
            )
            st.subheader("🎚️ Select Question Difficulty")
            difficulty = st.radio(
                "Choose difficulty level:",
                ["Easy", "Medium", "Hard", "Mixed"],
                index=1 if st.session_state.difficulty == "medium" else 3,
                horizontal=True
            )
            if st.button("Start Interview", type="primary"):
                final_role = custom_role if custom_role else selected
                if final_role:
                    st.session_state.update({
                        "job_role": final_role,
                        "difficulty": difficulty.lower() if difficulty != "Mixed" else "mixed",
                        "stage": 2,
                        "start_time": None,
                        "previous_answers": [],
                        "current_answer": "",
                        "transcription_success": None
                    })
                    st.rerun()

    # Stage 2: Question Generation and Interview
    elif st.session_state.stage == 2:
        add_back_button()  # Add Back button
        # Generate questions if not already generated
        if not st.session_state.questions:
            with st.spinner("🎯 Generating role-specific questions..."):
                prompt = get_job_role_prompt(
                    st.session_state.job_role,
                    st.session_state.difficulty,
                    st.session_state.interview_type
                )
                if st.session_state.resume_text:
                    skills = extract_skills(st.session_state.resume_text)
                    prompt += f"\n\nConsider these resume skills: {', '.join(skills[:5])}"
                questions = generate_questions(prompt)
                st.session_state.questions = [
                    {"text": q, "type": "role_specific", "difficulty": st.session_state.difficulty}
                    for q in questions if q.strip()
                ][:15]  # Limit to 15 questions
                if st.session_state.resume_text and skills:
                    general_questions = generate_general_questions(skills)
                    st.session_state.questions.extend([
                        {"text": q, "type": "general", "difficulty": "general"}
                        for q in general_questions[:5]
                    ])
                if st.session_state.interview_type in ["Behavioral", "Full Loop"]:
                    behavioral_questions = [
                        "Tell me about a time you faced a difficult challenge and how you handled it.",
                        "Describe a situation where you had to work with a difficult team member.",
                        "Give an example of how you've handled a mistake you made at work."
                    ]
                    st.session_state.questions.extend([
                        {"text": q, "type": "behavioral", "difficulty": "medium"}
                        for q in behavioral_questions
                    ])
                if not st.session_state.questions:
                    st.error("Failed to generate questions. Please try again.")
                    st.session_state.stage = 1
                    st.rerun()

        # Interview flow
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.session_state.force_rerun:
                    st.session_state.force_rerun = False
                    st.rerun()

                if st.session_state.current_q < len(st.session_state.questions):
                    current_q = st.session_state.questions[st.session_state.current_q]
                    question_text = current_q["text"]
                    difficulty = current_q["difficulty"]

                    # Progress
                    progress = (st.session_state.current_q + 1) / len(st.session_state.questions)
                    st.progress(
                        progress,
                        text=f"Question {st.session_state.current_q + 1} of {len(st.session_state.questions)}",
                    )

                    # Question Display with difficulty indicator
                    difficulty_class = f"difficulty-{difficulty}"
                    st.markdown(
                        f'<div class="question">'
                        f'💬 {question_text}<br>'
                        f'<span class="{difficulty_class}">Difficulty: {difficulty.capitalize()}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    # Initialize answer tracking for this question
                    if len(st.session_state.previous_answers) <= st.session_state.current_q:
                        st.session_state.previous_answers.append("")
                        st.session_state.current_answer = ""

                    # Show previous answer if exists
                    if st.session_state.previous_answers[st.session_state.current_q]:
                        st.markdown("### Your Previous Answer")
                        st.markdown(f'<div class="transcript-box">{st.session_state.previous_answers[st.session_state.current_q]}</div>',
                                    unsafe_allow_html=True)

                    # Recording Section
                    st.write("Click the microphone to record your answer:")
                    audio_bytes = audio_recorder(
                        pause_threshold=100.0,
                        sample_rate=41_000,
                        key=f"recorder_{st.session_state.current_q}",
                        energy_threshold=(-1.0, 1.0),
                    )

                    # Single editable text area for answer
                    answer = st.text_area(
                        "Type or edit your answer here:",
                        value=st.session_state.current_answer,
                        height=200,
                        key=f"answer_{st.session_state.current_q}"
                    )

                    # Process audio or text answer
                    if audio_bytes and not st.session_state.processing:
                        st.session_state.processing = True
                        with st.spinner("🔊 Transcribing your answer..."):
                            transcription = transcribe_audio(audio_bytes)
                            st.session_state.current_answer = transcription

                            # Show transcription status
                            if st.session_state.transcription_success is False:
                                st.markdown(
                                    f'<div class="transcription-error">⚠️ {transcription}</div>',
                                    unsafe_allow_html=True
                                )
                            st.rerun()

                    # Update current answer if typing
                    if answer != st.session_state.current_answer:
                        st.session_state.current_answer = answer

                    # Navigation buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("⬅️ Previous Question", type="secondary", disabled=st.session_state.current_q == 0):
                            st.session_state.current_q -= 1
                            st.session_state.current_answer = st.session_state.previous_answers[st.session_state.current_q]
                            st.session_state.processing = False
                            st.rerun()

                    with col2:
                        if st.button("✅ Save Answer", type="primary"):
                            if st.session_state.current_answer.strip():
                                st.session_state.previous_answers[st.session_state.current_q] = st.session_state.current_answer
                                st.session_state.answers.append({
                                    "question": question_text,
                                    "answer": st.session_state.current_answer,
                                    "type": current_q["type"],
                                    "difficulty": difficulty
                                })
                                update_skill_assessment(st.session_state.answers[-1:])

                                # Move to next question
                                st.session_state.current_q += 1
                                st.session_state.current_answer = ""
                                st.session_state.processing = False
                                st.session_state.force_rerun = True
                                st.rerun()
                            else:
                                st.warning("Please provide an answer before saving")

                    with col3:
                        if st.button("⏭️ Skip Question", type="secondary"):
                            st.session_state.answers.append({
                                "question": question_text,
                                "answer": "[Question skipped]",
                                "type": current_q["type"],
                                "difficulty": difficulty
                            })
                            st.session_state.current_q += 1
                            st.session_state.current_answer = ""
                            st.session_state.processing = False
                            st.session_state.force_rerun = True
                            st.rerun()

                else:
                    st.session_state.stage = 3
                    st.rerun()

            with col2:
                st.markdown("### 📊 Current Skills")
                if st.session_state.skill_scores:
                    # Create radar chart if we have enough skills
                    if len(st.session_state.skill_scores) >= 3:
                        skills_df = pd.DataFrame({
                            "skill": list(st.session_state.skill_scores.keys()),
                            "score": list(st.session_state.skill_scores.values())
                        })
                        fig = px.line_polar(
                            skills_df, 
                            r="score", 
                            theta="skill", 
                            line_close=True,
                            range_r=[0,5],
                            template="plotly_dark"
                        )
                        fig.update_traces(fill='toself')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Show simple progress bars if not enough skills for radar
                        for skill, score in st.session_state.skill_scores.items():
                            st.markdown(f'<div class="skill-meter"><div class="skill-name">{skill}</div>', unsafe_allow_html=True)
                            st.progress(score/5)
                else:
                    st.info("Complete questions to see skill analysis")
                
                st.markdown("### 💡 Tips")
                if st.session_state.interview_type == "Technical Screening":
                    st.write("- Be specific about technologies used")
                    st.write("- Explain your thought process clearly")
                    st.write("- Use technical terms accurately")
                elif st.session_state.interview_type == "Behavioral":
                    st.write("- Use STAR method (Situation, Task, Action, Result)")
                    st.write("- Be honest about challenges faced")
                    st.write("- Highlight what you learned")
                else:
                    st.write("- Balance technical and soft skills")
                    st.write("- Adapt to the interviewer's style")
                    st.write("- Ask clarifying questions when needed")

    # Stage 3: Feedback
    elif st.session_state.stage == 3:
        with st.container():
            st.markdown(
                '<div class="header">📝 Interview Feedback</div>',
                unsafe_allow_html=True,
            )

            # Answer History Section
            st.subheader("📋 Your Complete Answers")
            with st.expander("Review all your questions and answers", expanded=True):
                for i, answer in enumerate(st.session_state.answers):
                    st.markdown(f"**Q{i+1}:** {answer['question']}")
                    st.markdown(f"**Your Answer:** {answer['answer']}")
                    st.markdown("---")

            if st.session_state.answers:
                with st.spinner("🔍 Generating detailed feedback..."):
                    # Prepare answers for feedback
                    answers_text = "\n".join(
                        [f"Q: {a['question']}\nA: {a['answer']}\n" for a in st.session_state.answers]
                    )
                    
                    # Get difficulty distribution
                    difficulty_counts = {}
                    for a in st.session_state.answers:
                        difficulty_counts[a['difficulty']] = difficulty_counts.get(a['difficulty'], 0) + 1
                    
                    feedback_prompt = f"""
                    Analyze these interview responses for a {st.session_state.job_role} position and provide structured feedback:
                    
                    Interview Type: {st.session_state.interview_type}
                    Question Difficulty Distribution:
                    {', '.join([f'{k}: {v}' for k, v in difficulty_counts.items()])}
                    
                    Interview Responses:
                    {answers_text}
                    
                    Provide comprehensive feedback including:
                    1. **Overall Rating**: 1-5 stars with detailed justification
                    2. **Strengths**: 3-5 key strengths with specific examples
                    3. **Improvement Areas**: 3-5 actionable suggestions
                    4. **Technical Evaluation**: Assessment of technical knowledge
                    5. **Communication Skills**: Evaluation of clarity, structure, and professionalism
                    6. **Recommendations**: Specific areas to focus on for improvement
                    
                    Format the feedback with clear headings and bullet points for readability.
                    """
                    
                    feedback = model.generate_content(feedback_prompt)
                    st.markdown(
                        f'<div class="feedback">{feedback.text}</div>',
                        unsafe_allow_html=True,
                    )
                    
                    # Store the feedback for chatbot context
                    st.session_state.last_feedback = feedback.text
                    st.session_state.feedback_complete = True
                    
                    # Skill Analysis Section
                    st.subheader("🛠️ Skill Breakdown")
                    if st.session_state.skill_scores:
                        if len(st.session_state.skill_scores) >= 3:
                            skills_df = pd.DataFrame({
                                "skill": list(st.session_state.skill_scores.keys()),
                                "score": list(st.session_state.skill_scores.values())
                            })
                            fig = px.line_polar(
                                skills_df, 
                                r="score", 
                                theta="skill", 
                                line_close=True,
                                range_r=[0,5],
                                template="plotly_dark"
                            )
                            fig.update_traces(fill='toself')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Skill improvement suggestions
                        weakest_skill = min(st.session_state.skill_scores.items(), key=lambda x: x[1])
                        st.markdown(f"**Most needed improvement**: {weakest_skill[0]} (score: {weakest_skill[1]}/5)")
                        improvement = model.generate_content(
                            f"Suggest 3 specific ways to improve {weakest_skill[0]} for {st.session_state.job_role} role"
                        )
                        st.markdown(improvement.text)
                    
                    # Generate a summary
                    with st.expander("📌 Key Takeaways"):
                        summary_prompt = f"""
                        Create a concise bullet-point summary of the key feedback points from this analysis:
                        {feedback.text}
                        
                        Include:
                        - Top 3 strengths
                        - Top 3 areas for improvement
                        - Overall recommendation
                        - Suggested next steps
                        """
                        summary = model.generate_content(summary_prompt)
                        st.markdown(summary.text)
                    
                    # Show the feedback chatbot (simple version)
                    st.markdown("---")
                    st.subheader("❓ Questions about your feedback?")
                    feedback_chatbot()
                    
            else:
                st.warning("No answers recorded to generate feedback")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Start New Interview", type="primary"):
                    # Preserve skill scores while resetting other states
                    skill_scores = st.session_state.skill_scores
                    st.session_state.clear()
                    st.session_state.update({
                        "stage": 0,
                        "skill_scores": skill_scores,
                        "previous_answers": [],
                        "current_answer": "",
                        "mode_selected": False,
                        "chat_history": [],
                        "feedback_complete": False,
                        "feedback_chat_history": [],
                        "transcription_success": None
                    })
                    st.rerun()
            
            with col2:
                if st.button("📚 Switch to Study Mode", type="secondary"):
                    st.session_state.mode_selected = False
                    st.session_state.stage = 0
                    st.rerun()

if __name__ == "__main__":
    main()