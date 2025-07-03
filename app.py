import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Funkcja do sprawdzania poprawności klucza API
def is_valid_api_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()  # Próba dostępu do modeli
        return True
    except Exception:
        return False

# Inicjalizacja stanu sesji
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Sprawdzanie autentykacji
if not st.session_state.authenticated:
    api_key_input = st.text_input("🔑 Wprowadź swój klucz OpenAI:", type="password")
    if st.button("Zaloguj"):
        if is_valid_api_key(api_key_input):
            st.session_state.authenticated = True
            st.session_state.api_key = api_key_input
            st.success("✅ Pomyślnie zalogowano!")
            st.rerun()  # ✅ POPRAWIONE
        else:
            st.error("❌ Nieprawidłowy klucz API. Spróbuj ponownie.")
    st.stop()

# Inicjalizacja klienta OpenAI z poprawnym kluczem API
client = OpenAI(api_key=st.session_state.api_key)

# Obrazek nagłówkowy
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
    response = client.chat.completions.create(
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
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Prosty czarno-biały rysunek do kolorowania dla dzieci: {idea}",
            n=1,
            size="1024x1024",
            quality="standard"
        )
        images.append(response.data[0].url)
    return images

# Funkcja do generowania kolorowanki
def generate_coloring(idea):
    st.write(f"🎨 Generowanie kolorowanki dla: *{idea}*")
    images = generate_coloring_book_images(idea, num_images=1)
    for img_url in images:
        st.image(img_url, caption=f"Kolorowanka: {idea}")

# Nagłówek aplikacji
st.markdown("<h1 style='color: #FF5733; font-family: Comic Sans MS;'>Kolorowanki Fantazja</h1>", unsafe_allow_html=True)

st.markdown("""
<div style="color: #1F618D; font-family: Comic Sans MS;">
    <p>Zabierz swoje dziecko w magiczną podróż po świecie kolorów i wyobraźni! Nasza aplikacja oferuje różnorodne wzory i motywy, które rozwijają kreatywność i umiejętności manualne najmłodszych. Zawiera intuicyjny interfejs, idealny dla małych artystów. Odkryj alfabet, zwierzęta, baśniowe postacie i wiele innego! Kolorowanie nigdy nie było tak ekscytujące i edukacyjne.</p>
</div>
""", unsafe_allow_html=True)

# Pole tekstowe do wpisania tematu
user_input = st.text_input("🖌️ Co chcesz narysować? (np. zwierzęta, kosmos, owoce...)")

# Lista pomysłów (jeśli są)
ideas_list = st.session_state.get("ideas", [])
selected_idea = st.selectbox("📋 Wybierz pomysł na kolorowankę:", ideas_list, key="idea_choice")

# Przycisk do generowania pomysłów
if st.button("🔍 Pokaż pomysły"):
    if user_input.strip():
        ideas = generate_coloring_book_ideas(user_input)
        save_ideas(user_input, ideas)
        st.session_state["ideas"] = ideas
        st.session_state["selected_idea"] = ideas[0] if ideas else None
        st.rerun()
    else:
        st.warning("⚠️ Proszę wpisać temat, np. 'dinozaury', 'zima', 'samochody'...")

# Przycisk do generowania kolorowanki
if st.button("🖼️ Generuj Kolorowankę"):
    if selected_idea:
        generate_coloring(selected_idea)
    else:
        st.warning("⚠️ Najpierw wybierz pomysł z listy!")