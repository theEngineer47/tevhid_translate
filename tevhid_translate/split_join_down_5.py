import streamlit as st
import openai
import warnings
from nltk.tokenize import word_tokenize, sent_tokenize
import tiktoken
import PyPDF2


warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Tevhidî Mütercim",
    page_icon="📚"
)

st.caption("Tevhid AI Team")
st.title("Tevhidî Mütercim")
st.write("Metinlerizi çevirmek için geliştirilmiş yapay zekâ tabanlı bir uygulama.")

openai.api_key = st.text_input("API Anahtarı")

def convert_pdf_to_text(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ''
    for page_num in range(pdf_reader.getNumPages()):
        page_obj = pdf_reader.getPage(page_num)
        text += page_obj.extract_text()
    return text
def get_completion(prompt, model="gpt-3.5-turbo-16k-0613", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]  # type: ignore


input_lang = st.selectbox("Orijinal Metin Dili",
                          ["Turkish", "English", "French", "German", "Arabic", "Dutch", "Persian", "Spanish",
                           "Russian","Azerbaijani","Kurdish"])
output_lang = st.selectbox("Talep Edilen Dil",
                           ["English", "Turkish", "French", "German", "Arabic", "Dutch", "Persian", "Spanish",
                            "Russian", "Azerbaijani" ,"Kurdish"])

prompt = f"""Translate the following {input_lang} Islamic text into {output_lang}, maintaining its spiritual and cultural essence, clarity, and accuracy. Adapt cultural references and idioms thoughtfully to suit {output_lang}-speaking readers.Handle sensitive topics respectfully, crafting an engaging tone. Use your knowledge of Islamic teachings, {input_lang} culture, and {output_lang} language nuances to enrich reader understanding, but do not add any comments or extras. Here's the text for translation: """

def read_pdf(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    full_text = ''
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        full_text += page.extractText()
    return full_text

def split_file(file_content, token_limit=2700):
    text = file_content

    tokens = word_tokenize(text)
    sents = sent_tokenize(text)

    i = 0
    part = 0
    output_files = []
    while i < len(tokens):
        current_tokens = 0
        current_sents = []
        while i < len(tokens) and current_tokens + len(word_tokenize(sents[0])) <= token_limit:
            current_sents.append(sents.pop(0))
            current_tokens += len(word_tokenize(current_sents[-1]))
            i += len(word_tokenize(current_sents[-1]))
        output_files.append((' '.join(current_sents), f"part_{part}.txt"))
        part += 1

    return output_files

def get_num_tokens(file_content):
    text = file_content
    tokens = word_tokenize(text)

    return len(tokens)

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def combine_files(file_contents):
    combined_text = ''
    for file_content in file_contents:
        combined_text += file_content + '\n'

    return combined_text

input_type = st.radio("Çeviri tipini seçin", ("Dosya", "Metin"))

if input_type == "Dosya":
    uploaded_file = st.file_uploader("Dosya yükle", type=["txt", "pdf", "docx"])

    if 'translations_dict' not in st.session_state:
        st.session_state.translations_dict = {}

    if uploaded_file is not None:
        file_key = uploaded_file.name + str(uploaded_file.size)

        if uploaded_file.type == "application/pdf":
            file_content = read_pdf(uploaded_file)


        else:
            file_content = uploaded_file.read().decode("utf-8")

        st.write("Total tokens : ", (num_tokens_from_string(file_content)))

        if st.button("Dosyayı Çevir"):
            split_contents = split_file(file_content)
            num_of_files = len(split_contents)
            translated_contents = []
            all_txt = ''
            for content, name in split_contents:
                with st.spinner(f'Çeviriyor: {name.split(".")[0]} / part_{num_of_files}...\nTamamlandığında bildirim alacaksınız...'):
                    translated_content = get_completion(prompt + content)
                    translated_contents.append(translated_content)
                    all_txt += translated_content + '\n'

            st.session_state.translations_dict[file_key] = {"translated_contents": translated_contents, "all_txt": all_txt}

#        if file_key in st.session_state.translations_dict:
#            for content in st.session_state.translations_dict[file_key]["translated_contents"]:
#
#                st.download_button("Çeviriyi İndir", data=st.session_state.translations_dict[file_key]["all_txt"],
#                               file_name="translated_file.txt", mime="text/plain")
#                st.text_area("Çeviri:", content[:100] + "...")

        if file_key in st.session_state.translations_dict:
            for i, content in enumerate(st.session_state.translations_dict[file_key]["translated_contents"]):
                st.download_button("Çeviriyi İndir",data=st.session_state.translations_dict[file_key]["all_txt"],
                    file_name=f"translated_file_{i}.txt",mime="text/plain",key=f"download_button_{i}")  # Benzersiz anahtar)
                st.text_area("Çeviri:", content[:100] + "...", key=f"text_area_{i}")  # Benzersiz anahtar

else:
    text_input = st.text_area("Çevirilecek metni girin")

    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = None

    if st.button("Metni Çevir"):
        translated_text = get_completion(prompt + text_input)
        st.session_state.translated_text = translated_text

    if st.session_state.translated_text is not None:

        st.download_button("Çeviriyi İndir", data=st.session_state.translated_text, file_name="translated_text.txt",
                           mime="text/plain")
        st.text_area("Çeviri:", st.session_state.translated_text)