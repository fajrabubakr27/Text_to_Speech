# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
import os
import base64
import requests

st.set_page_config(page_title="Arabic Text to Speech", layout="centered")


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


def detect_arabic_emotions(text):
    emotions_dict = {
        "فرح": ["فرح", "سعيد", "مبسوط", "سرور", "ابتسامة", "مسرور", "حلو", "جيد"],
        "حزن": ["حزن", "زعل", "مكسور", "دموع", "حزين", "موجوع", "موت", "خسارة"],
        "غضب": ["غضب", "زعلان", "انفجر", "غاضب", "تعبان", "نفسيتي تعبانة", "مضايق"],
        "خوف": ["خوف", "قلق", "مرعوب", "مخيف", "خايف", "توتر"],
        "تفاؤل": ["تفاؤل", "أمل", "نصر", "نجاح", "سعادة", "مستقبل", "حلم"],
        "دهشة": ["دهشة", "مندهش", "متفاجئ", "مستغرب"],
    }

    text = text.lower()
    emotion_counts = {emotion: 0 for emotion in emotions_dict}

    for emotion, keywords in emotions_dict.items():
        for word in keywords:
            emotion_counts[emotion] += text.count(word)

    total = sum(emotion_counts.values())
    if total == 0:
        return "محايد", {}

    emotion_percentages = {k: v / total for k, v in emotion_counts.items() if v > 0}

    dominant_emotion = max(emotion_percentages, key=emotion_percentages.get)

    return dominant_emotion, emotion_percentages


if st.button("جاهز  تسمع  كلامك؟"):
    if text.strip() == "":
        st.error("فاتتكك ازاي دي بس! نسيت تكتب الكلام...")
    else:
        dominant_emotion, emotion_percentages = detect_arabic_emotions(text)
        st.markdown(f"### الشعور الغالب في النص: **{dominant_emotion}**")
        if emotion_percentages:
            st.markdown("#### نسب المشاعر:")
            for emo, perc in emotion_percentages.items():
                st.write(f"- {emo}: {perc*100:.1f}%")
        else:
            st.write("مافيش مشاعر واضحة في النص (محايد)")

        tts = gTTS(text, lang='ar')
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3", start_time=0)

        with open("output.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            href = f'<a href="data:audio/mp3;base64,{b64}" download="output.mp3">📥 عايز تنزل صوتك؟</a>'
            st.markdown(href, unsafe_allow_html=True)
