
import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import re

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Multilingual Public Service Assistant",
    page_icon="🎙️",
    layout="wide"
)

# ==========================================
# LANGUAGE SETTINGS
# ==========================================

LANGUAGES = {
    "English": {"code": "en", "speech": "en-IN"},
    "Tamil": {"code": "ta", "speech": "ta-IN"},
    "Hindi": {"code": "hi", "speech": "hi-IN"},
    "Telugu": {"code": "te", "speech": "te-IN"},
    "Malayalam": {"code": "ml", "speech": "ml-IN"},
    "Kannada": {"code": "kn", "speech": "kn-IN"},
    "Bengali": {"code": "bn", "speech": "bn-IN"},
    "Marathi": {"code": "mr", "speech": "mr-IN"}
}

# ==========================================
# PUBLIC SERVICE KNOWLEDGE BASE
# ==========================================

SERVICES = [
    {
        "keywords": ["aadhaar", "aadhar", "identity card"],
        "title": "Aadhaar Services",
        "answer": "Aadhaar services include new enrolment, address updates, demographic corrections and e-Aadhaar downloads. Visit https://uidai.gov.in/"
    },
    {
        "keywords": ["pan card", "pan", "income tax"],
        "title": "PAN Card Services",
        "answer": "PAN card services include new applications, corrections and reprints. Visit https://www.incometax.gov.in/ for official information."
    },
    {
        "keywords": ["ration card", "food card", "ration"],
        "title": "Ration Card Services",
        "answer": "Ration card services include new applications, member additions, corrections and status checking. Contact your state food and civil supplies department."
    },
    {
        "keywords": ["voter id", "voter card", "election"],
        "title": "Voter ID Services",
        "answer": "You can register as a voter, update your details and check application status. Visit https://voters.eci.gov.in/"
    },
    {
        "keywords": ["passport", "travel document"],
        "title": "Passport Services",
        "answer": "Passport services include fresh applications, renewals, corrections and appointment booking. Visit https://www.passportindia.gov.in/"
    },
    {
        "keywords": ["scholarship", "student scholarship", "education"],
        "title": "Scholarship Information",
        "answer": "Students can explore government scholarships based on eligibility, academic performance and income criteria. Visit https://scholarships.gov.in/"
    },
    {
        "keywords": ["healthcare", "hospital", "health scheme", "medical"],
        "title": "Healthcare Services",
        "answer": "Government healthcare services include public hospitals, health insurance schemes and medical assistance. Visit https://pmjay.gov.in/ for PM-JAY information."
    },
    {
        "keywords": ["birth certificate", "birth registration"],
        "title": "Birth Certificate",
        "answer": "Birth certificates are generally issued by the local municipality, corporation or authorised registration office. Contact your local authority for application details."
    },
    {
        "keywords": ["death certificate", "death registration"],
        "title": "Death Certificate",
        "answer": "Death certificates can be obtained through the authorised local registration office. Contact your municipality or local authority for the required documents."
    },
    {
        "keywords": ["driving licence", "driving license", "licence"],
        "title": "Driving Licence Services",
        "answer": "You can apply for a learner's licence, permanent driving licence or renewal. Visit https://parivahan.gov.in/"
    },
    {
        "keywords": ["pension", "old age pension", "senior citizen"],
        "title": "Pension Services",
        "answer": "Eligible citizens can explore old-age, disability and other social security pension schemes through their state government and official welfare departments."
    },
    {
        "keywords": ["government job", "job vacancy", "employment"],
        "title": "Employment Services",
        "answer": "Citizens can explore employment opportunities, skill development and job registration through official government employment portals."
    },
    {
        "keywords": ["electricity", "power bill", "electricity bill"],
        "title": "Electricity Services",
        "answer": "For electricity connections, bill payments, complaints and service requests, contact your regional electricity distribution company."
    },
    {
        "keywords": ["water supply", "water connection", "drinking water"],
        "title": "Water Supply Services",
        "answer": "For water connections, water supply complaints and related services, contact your local municipality or water supply department."
    },
    {
        "keywords": ["police", "police complaint", "complaint"],
        "title": "Police Services",
        "answer": "For emergencies in India, call 112. For non-emergency complaints, contact your nearest police station or use your state's official police portal."
    },
    {
        "keywords": ["farmer", "agriculture", "crop", "pm kisan"],
        "title": "Agriculture Services",
        "answer": "Farmers can explore agricultural subsidies, crop support and PM-KISAN information. Visit https://pmkisan.gov.in/ for official scheme details."
    },
    {
        "keywords": ["income certificate", "income proof"],
        "title": "Income Certificate",
        "answer": "Income certificates are issued by authorised revenue departments. Application procedures and required documents vary by state."
    },
    {
        "keywords": ["community certificate", "caste certificate"],
        "title": "Community Certificate",
        "answer": "Community certificates are issued through authorised state revenue departments. Check your state's official e-governance portal for application procedures."
    }
]

# ==========================================
# TRANSLATION FUNCTION
# ==========================================

def translate_text(text, target_language, source="auto"):
    try:
        return GoogleTranslator(
            source=source,
            target=target_language
        ).translate(text)
    except Exception:
        return text

# ==========================================
# QUERY PROCESSING
# ==========================================

def clean_text(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def find_service(query):

    query = clean_text(query)

    best_match = None
    best_score = 0

    for service in SERVICES:

        for keyword in service["keywords"]:

            keyword = clean_text(keyword)

            if keyword in query:
                return service

            words = query.split()

            for word in words:
                if len(word) > 3 and len(keyword) > 3:
                    from difflib import SequenceMatcher

                    score = SequenceMatcher(
                        None, word, keyword
                    ).ratio()

                    if score > best_score:
                        best_score = score
                        best_match = service

    if best_score >= 0.80:
        return best_match

    return None


# ==========================================
# RESPONSE GENERATION
# ==========================================

def generate_response(query, language):

    english_query = translate_text(
        query,
        "en"
    )

    service = find_service(english_query)

    if service:
        response = (
            f"{service['title']}\n\n"
            f"{service['answer']}\n\n"
            "Please verify eligibility, documents and procedures "
            "through the relevant official department."
        )
    else:
        response = (
            "Sorry, I could not find an exact answer to your question. "
            "Please try asking about Aadhaar, PAN card, ration card, "
            "scholarships, healthcare, passport, voter ID or other "
            "public services."
        )

    translated_response = translate_text(
        response,
        language
    )

    return translated_response


# ==========================================
# TEXT TO SPEECH
# ==========================================

def generate_voice(text, language):

    try:
        audio_buffer = BytesIO()

        tts = gTTS(
            text=text,
            lang=language
        )

        tts.write_to_fp(audio_buffer)

        audio_buffer.seek(0)

        return audio_buffer

    except Exception:
        return None


# ==========================================
# SPEECH RECOGNITION
# ==========================================

def recognize_voice(audio_file, language):

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:

            audio = recognizer.record(source)

            text = recognizer.recognize_google(
                audio,
                language=language
            )

            return text

    except sr.UnknownValueError:
        return "Could not understand the audio. Please speak clearly."

    except sr.RequestError:
        return "Speech recognition service is unavailable. Please try again."

    except Exception:
        return "Unable to process the audio. Please try again."


# ==========================================
# SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []


# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #f4f7fb;
}

.title {
    text-align: center;
    font-size: 35px;
    font-weight: bold;
    color: #153e75;
}

.subtitle {
    text-align: center;
    color: #555;
    font-size: 17px;
}

.stButton button {
    background-color: #1769aa;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

.stButton button:hover {
    background-color: #104d80;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# APPLICATION HEADER
# ==========================================

st.markdown(
    '<div class="title">🎙️ Public Service Voice Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">One Voice. Many Languages. Public Services for Everyone.</div>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# LANGUAGE SELECTION
# ==========================================

st.subheader("🌐 Select Your Preferred Language")

selected_language = st.selectbox(
    "Choose Language",
    list(LANGUAGES.keys())
)

language_code = LANGUAGES[selected_language]["code"]

speech_code = LANGUAGES[selected_language]["speech"]

st.success(
    f"Selected Language: {selected_language}"
)

# ==========================================
# SERVICE INFORMATION
# ==========================================

st.subheader("📌 Available Public Services")

columns = st.columns(3)

service_names = [
    "🪪 Aadhaar Services",
    "💳 PAN Card",
    "🍚 Ration Card",
    "🗳️ Voter ID",
    "🎓 Scholarships",
    "🏥 Healthcare",
    "🛂 Passport",
    "🚗 Driving Licence",
    "🌾 Agriculture",
    "👴 Pension",
    "📄 Certificates",
    "🚨 Police Services"
]

for index, name in enumerate(service_names):

    with columns[index % 3]:
        st.info(name)

st.divider()

# ==========================================
# VOICE INPUT
# ==========================================

st.subheader("🎤 Ask Through Your Voice")

st.write(
    "Click the microphone and record your question."
)

audio_file = st.audio_input(
    "Record your question"
)

if st.button("Process Voice Query"):

    if audio_file is not None:

        with st.spinner("Understanding your voice..."):

            recognized_text = recognize_voice(
                audio_file,
                speech_code
            )

            st.write("**Recognized Question:**")
            st.write(recognized_text)

            if not recognized_text.startswith(
                ("Could not", "Speech recognition", "Unable")
            ):

                response = generate_response(
                    recognized_text,
                    language_code
                )

                st.session_state.history.append({
                    "question": recognized_text,
                    "answer": response
                })

                st.subheader("🤖 Assistant Response")

                st.success(response)

                voice = generate_voice(
                    response,
                    language_code
                )

                if voice:
                    st.audio(
                        voice,
                        format="audio/mp3"
                    )

    else:
        st.warning("Please record your question first.")

# ==========================================
# TEXT INPUT
# ==========================================

st.divider()

st.subheader("⌨️ Ask Through Text")

user_query = st.text_input(
    "Enter your public service question",
    placeholder="Example: How can I apply for a ration card?"
)

if st.button("Get Answer"):

    if user_query.strip():

        with st.spinner("Searching for information..."):

            response = generate_response(
                user_query,
                language_code
            )

            st.subheader("🤖 Assistant Response")

            st.success(response)

            st.session_state.history.append({
                "question": user_query,
                "answer": response
            })

            voice = generate_voice(
                response,
                language_code
            )

            if voice:
                st.audio(
                    voice,
                    format="audio/mp3"
                )

    else:
        st.warning("Please enter your question.")

# ==========================================
# CHAT HISTORY
# ==========================================

st.divider()

st.subheader("💬 Conversation History")

if st.session_state.history:

    for index, chat in enumerate(
        reversed(st.session_state.history)
    ):

        with st.expander(
            f"Conversation {len(st.session_state.history) - index}"
        ):

            st.write("**Your Question:**")
            st.write(chat["question"])

            st.write("**Assistant Answer:**")
            st.write(chat["answer"])

    if st.button("Clear Chat History"):

        st.session_state.history = []

        st.rerun()

else:
    st.info("Your conversation history will appear here.")

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<center>

### 🌍 Accessible Services for Every Citizen

Breaking language barriers through Artificial Intelligence.

**Multilingual Voice-Based Public Service Assistant**

</center>
""", unsafe_allow_html=True)

st.caption(
    "Note: Responses are general guidance, not official government decisions. "
    "Always verify details through the relevant government department. "
    "Internet connectivity is required for speech recognition, translation and voice generation."
)
