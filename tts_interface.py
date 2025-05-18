# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
import os
import base64
import requests

# إعداد الصفحة
st.set_page_config(page_title="Text to Speech - Arabic", layout="centered")

st.title("🔊 تحويل النص العربي إلى صوت")
st.write("اختر صورة تحتوي على نص عربي أو اكتب النص يدويًا، وسيتم تحويله إلى صوت.")

# تحميل ملف اللغة العربية لـ Tesseract تلقائيًا
def download_ara_traineddata():
    tessdata_dir = "./tessdata"
    os.makedirs(tessdata_dir, exist_ok=True)
    file_path = os.path.join(tessdata_dir, "ara.traineddata")

    if not os.path.exists(file_path):
        st.info("جارٍ تحميل نموذج اللغة العربية لـ Tesseract...")
        url = "https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata"
        response = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(response.content)
        st.success("✅ تم تحميل نموذج اللغة العربية بنجاح.")
    return tessdata_dir

tessdata_dir = download_ara_traineddata()
os.environ["TESSDATA_PREFIX"] = tessdata_dir

# اختيار طريقة الإدخال
option = st.radio("اختر طريقة الإدخال:", ["📷 إدخال صورة", "✍️ كتابة نص يدويًا"])

# إدخال النص أو الصورة
text = ""

if option == "📷 إدخال صورة":
    uploaded_image = st.file_uploader("ارفع صورة", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="📷 الصورة التي تم رفعها", use_column_width=True)
        text = pytesseract.image_to_string(image, lang='ara')
        if text.strip():
            st.success("✅ تم استخراج النص من الصورة.")
            st.text_area("📝 النص المستخرج:", value=text, height=150)
        else:
            st.warning("⚠️ لم يتم استخراج أي نص من الصورة.")

elif option == "✍️ كتابة نص يدويًا":
    text = st.text_area("✍️ اكتب النص هنا:")

# زر التحويل
if st.button("🎤 تحويل النص إلى صوت"):
    if text.strip() == "":
        st.error("من فضلك أدخل نصًا أولاً.")
    else:
        tts = gTTS(text, lang='ar')
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3", start_time=0)

        # زر التحميل
        with open("output.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            href = f'<a href="data:audio/mp3;base64,{b64}" download="output.mp3">📥 تحميل الصوت</a>'
            st.markdown(href, unsafe_allow_html=True)
