---

# AI Mock Interview

## Project Description

**AI Mock Interview** is an interactive, AI-powered interview preparation tool designed to help job seekers enhance their interview skills. Built using **Streamlit** and integrated with **Google's Gemini API**, this application provides a seamless experience where users can upload their resumes, participate in simulated interviews, and receive intelligent, AI-generated feedback.

Key features include **resume parsing**, **voice input with transcription**, **personalized question generation**, **AI-based feedback on interview performance**, and a **study chatbot** for continuous learning and preparation.

## Installation Instructions

Follow these steps to set up and run the project on your local machine:

### Prerequisites

* **Python 3.10 or higher**
* pip (Python package installer)
* Google API credentials for Gemini integration

### Steps

1. **Clone the repository**

   ```bash
   git clone <repository_url>
   cd ai-mock-interview
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API credentials**

   Update the application with your **Gemini API credentials** where required in the code.

## Usage

To run the application locally:

```bash
streamlit run app.py
```

Once running, the application will open in your default web browser. Here’s how you can interact with it:

* **Upload your resume (PDF format)** to allow the AI to parse your information and tailor interview questions.
* **Participate in mock interviews** using real-time voice input and text transcription.
* **Receive AI-generated personalized feedback** on your interview responses.
* **Use the study chatbot** for practice questions, interview tips, and preparation materials.

## Features

* **Resume Parsing and Extraction**

  * Analyze uploaded resumes to extract relevant skills and experiences.
* **Real-time AI-Driven Interview Simulations**

  * Simulate interview scenarios with voice input and dynamic question generation.
* **Personalized Feedback After Interviews**

  * AI-generated feedback to identify strengths and areas for improvement.
* **Voice Input Transcription and Integration**

  * Accept voice responses during interviews, transcribe them, and analyze the text.
* **Study Chatbot for Interview Preparation**

  * Interactive chatbot to assist users in studying and preparing for interviews.

## Technologies Used

* **Python**
* **Streamlit**
* **Google Gemini API**
* **Natural Language Processing (NLP)**
* **Speech Recognition**
* **OpenAI / LLM Integrations (if applicable)**
* **PDF Parsing Libraries (PyPDF2 or similar)**

## Contributing

Contributions are welcome and appreciated. To contribute:

1. Fork the repository.

2. Create a new branch.

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Commit your changes.

   ```bash
   git commit -m "Add your message"
   ```

4. Push to the branch.

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request.

For bug reports or feature suggestions, please open an issue on the repository.

## License

This project is licensed under the **MIT License**.

## Acknowledgements

* **Streamlit** for enabling rapid interactive web application development.
* **Google Gemini API** for AI-powered text and language processing.
* **SpeechRecognition**, **PyPDF2**, and other Python libraries for supporting core functionalities.
* Community resources, tutorials, and documentation that assisted during development.

## Contact Information

For questions, feedback, or inquiries:

**Project Owner:** \[Hrushikesh Ramesh]
**Email:** \[[rameshsrinivasan300@gmail.com](mailto:rameshsrinivasan300@gmail.com)]



