import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Wczytaj zmienne środowiskowe
load_dotenv()

# Wstaw do sesji jeśli brakuje klucza API
if "openai_api_key" not in st.session_state:
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        st.session_state["openai_api_key"] = openai_api_key
    else:
        st.info("Podaj swój klucz OpenAI:")
        st.session_state["openai_api_key"] = st.text_input("Klucz API", type="password")
        if st.session_state["openai_api_key"]:
            st.experimental_rerun()

# Użyj klucza z sesji do inicjalizacji klienta OpenAI
llm_client = OpenAI(api_key=st.session_state["openai_api_key"])

# Obrazek
st.image("obrazek.png", use_container_width=True)

# Ścieżka do pliku z zapisanymi propozycjami
SAVE_FILE = "coloring_ideas.json"

# Funkcja do zapisywania pomysłów do pliku JSON
def save_ideas(topic, ideas):
    data = load_saved_ideas()
    data[topic] = ideas
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Funkcja do ładowania zapisanych pomysłów
def load_saved_ideas():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Funkcja do generowania pomysłów na kolorowanki
def generate_coloring_book_ideas(topic):
    response = llm_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś kreatywnym asystentem, który generuje pomysły na kolorowanki dla dzieci. Odpowiadaj tylko w języku polskim."},
            {"role": "user", "content": f"Wygeneruj 5 prostych i zabawnych pomysłów na kolorowanki związane z tematem: {topic}. Pomysły powinny być odpowiednie dla dzieci."}
        ]
    )
    ideas = response.choices[0].message.content.strip().split("\n")
    return ideas

# Funkcja do generowania obrazów kolorowanek
def generate_coloring_book_images(idea, num_images=1):
    images = []
    for _ in range(num_images):
        response = llm_client.images.generate(
            model="dall-e-3",
            prompt=f"Prosty czarno-biały rysunek dla dziecięcej kolorowanki: {idea}",
            n=1,
            size="1024x1024",
            quality="standard"
        )
        images.append(response.data[0].url)
    return images

# Funkcja do generowania obrazka na podstawie wybranego pomysłu
def generate_coloring(idea):
    st.write(f"Generowanie kolorowanki dla: {idea}")
    images = generate_coloring_book_images(idea, num_images=1)
    for img_url in images:
        st.image(img_url, caption=f"Kolorowanka: {idea}")

# Nagłówek aplikacji
title_html = "<h1 style='color: #FF5733; font-family: Comic Sans MS;'>Kolorowanki Fantazja</h1>"
st.markdown(title_html, unsafe_allow_html=True)

description_html = """
<div style="color: #1F618D; font-family: Comic Sans MS;">
    <p>Zabierz swoje dziecko w magiczną podróż po świecie kolorów i wyobraźni! Nasza aplikacja oferuje różnorodne wzory i motywy, które rozwijają kreatywność i umiejętności manualne najmłodszych. Zawiera intuicyjny interfejs, idealny dla małych artystów. Odkryj alfabet, zwierzęta, baśniowe postacie i wiele innego! Kolorowanie nigdy nie było tak ekscytujące i edukacyjne.</p>
</div>
"""
st.markdown(description_html, unsafe_allow_html=True)

# Pole tekstowe do wpisania, co ma być narysowane
user_input = st.text_input("Co chcesz narysować?")

# Pole wyboru pomysłów (sygnalizacja dla wyboru)
ideas_list = st.session_state.get("ideas", [])
selected_idea = st.selectbox("Wybierz pomysł na kolorowankę:", ideas_list, key="idea_choice")

# Przycisk do wyświetlenia pomysłów
if st.button("Pokaż pomysły"):
    if user_input.strip():
        ideas = generate_coloring_book_ideas(user_input)
        save_ideas(user_input, ideas)
        st.session_state["ideas"] = ideas
        st.session_state["selected_idea"] = ideas[0] if ideas else None
    else:
        st.warning("Proszę wpisać coś, co ma być narysowane!")

# Przycisk do generowania kolorowanki
if st.button("Generuj Kolorowankę"):
    if selected_idea:
        generate_coloring(selected_idea)
    else:
        st.warning("Najpierw wybierz pomysł z dostępnej listy!")