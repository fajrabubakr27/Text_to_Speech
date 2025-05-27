# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
import os
import base64
import requests

# Emotion Detection imports
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

st.set_page_config(page_title="Arabic Text to Speech", layout="centered")

# Arabic direction styling
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("الكلام  بقى  ليه  صوت")
st.write("ارفع  صورة  فيها  كلام  بالعربي  أو  اكتبه  بإيدك  وسيب  الباقي  علينا")

# Setup for Tesseract
def download_ara_traineddata():
    tessdata_dir = "./tessdata"
    os.makedirs(tessdata_dir, exist_ok=True)
    file_path = os.path.join(tessdata_dir, "ara.traineddata")

    if not os.path.exists(file_path):
        url = "https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata"
        response = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(response.content)
    return tessdata_dir

tessdata_dir = download_ara_traineddata()
os.environ["TESSDATA_PREFIX"] = tessdata_dir

option = st.radio("اختار  اللي  تحبه:", ["هرفعلك  صورة", "هكتب  الكلام  بإيدي"])

text = ""

if option == "هرفعلك  صورة":
    uploaded_image = st.file_uploader("ارفع  صورة", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة  اللي  رفعتها", use_container_width=True)
        text = pytesseract.image_to_string(image, lang='ara')
        if text.strip():
            st.success("عرفنا  نطلع  الكلام  اللي  في  الصورة")
            st.text_area("الكلام  اللي  في  الصورة:", value=text, height=150)
        else:
            st.warning("معرفناش  نخرج  الكلام  من  الصورة  حاول  تاني  بصورة أوضح")

elif option == "هكتب  الكلام  بإيدي":
    text = st.text_area(" اكتب  الكلام  هنا:")

# Sentiment/Emotion Detection Setup
@st.cache_resource
def load_emotion_model():
    model_name = "akhooli/bert-base-arabic-emotion"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_emotion_model()
emotion_labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']

def detect_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.nn.functional.softmax(logits, dim=-1).squeeze().cpu().numpy()
    top_idx = np.argmax(probs)
    return emotion_labels[top_idx], probs

# Emotion detection button
if st.button("طلعلي إحساس الكلام"):
    if text.strip() == "":
        st.error("اكتب حاجة الأول 😅")
    else:
        emotion, probs = detect_emotion(text)
        st.success(f"الإحساس الغالب في الكلام: **{emotion}** 🎭")
        st.bar_chart({label: float(prob) for label, prob in zip(emotion_labels, probs)})

# TTS Button
if st.button("جاهز  تسمع  كلامك؟"):
    if text.strip() == "":
        st.error("فاتتكك ازاي دي بس! نسيت تكتب الكلام...")
    else:
        tts = gTTS(text, lang='ar')
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3", start_time=0)

        with open("output.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            href = f'<a href="data:audio/mp3;base64,{b64}" download="output.mp3">📥 عايز تنزل صوتك؟</a>'
            st.markdown(href, unsafe_allow_html=True)

