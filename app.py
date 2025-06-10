import streamlit as st
from musicRecomendation import recommend_by_song, recommend_by_artist, recommend_by_mood

# Safe rerun untuk berbagai versi Streamlit
try:
    rerun = st.experimental_rerun
except AttributeError:
    rerun = st.rerun

st.set_page_config(page_title="MelodAI", layout="wide")
st.title("MelodAI – Music Recommender")
st.markdown("Mau dengerin musik berdasarkan apa hari ini?")

left, right = st.columns([1, 2])

# === Inisialisasi state ===
if "filter" not in st.session_state:
    st.session_state.filter = None
if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None
if "stored_results" not in st.session_state:
    st.session_state.stored_results = []
if "shown_count" not in st.session_state:
    st.session_state.shown_count = 10
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# === KIRI: Filter ===
with left:
    st.markdown("### Pilih Filter Rekomendasi")
    if st.button("🎵 Lagu", use_container_width=True):
        st.session_state.filter = "song"
        st.session_state.selected_mood = None
        st.session_state.stored_results = []
        st.session_state.shown_count = 10
        st.session_state.last_input = ""

    if st.button("🎤 Penyanyi", use_container_width=True):
        st.session_state.filter = "artist"
        st.session_state.selected_mood = None
        st.session_state.stored_results = []
        st.session_state.shown_count = 10
        st.session_state.last_input = ""

    if st.button("😎 Mood", use_container_width=True):
        st.session_state.filter = "mood"
        st.session_state.stored_results = []
        st.session_state.shown_count = 10
        st.session_state.last_input = ""

    # Tombol mood muncul jika filter mood dipilih
    if st.session_state.filter == "mood":
        st.markdown("### Pilih Mood:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("😢 Sad", use_container_width=True):
                st.session_state.selected_mood = "sad"
                st.session_state.stored_results = []
                st.session_state.shown_count = 10
                st.session_state.last_input = ""
        with col2:
            if st.button("🧘 Calm", use_container_width=True):
                st.session_state.selected_mood = "calm"
                st.session_state.stored_results = []
                st.session_state.shown_count = 10
                st.session_state.last_input = ""

        col3, col4 = st.columns(2)
        with col3:
            if st.button("😁 Happy", use_container_width=True):
                st.session_state.selected_mood = "happy"
                st.session_state.stored_results = []
                st.session_state.shown_count = 10
                st.session_state.last_input = ""
        with col4:
            if st.button("🎉 Party", use_container_width=True):
                st.session_state.selected_mood = "party"
                st.session_state.stored_results = []
                st.session_state.shown_count = 10
                st.session_state.last_input = ""

# === KANAN: Rekomendasi ===
with right:
    ftype = st.session_state.filter
    count = st.session_state.shown_count

    if ftype == "song":
        song = st.text_input("Masukkan nama lagu:")
        if song:
            if song != st.session_state.last_input:
                st.session_state.stored_results = recommend_by_song(song, top_n=100)
                st.session_state.shown_count = 10
                st.session_state.last_input = song

            results = st.session_state.stored_results
            if not results:
                st.warning("Lagu tidak ditemukan.")
            else:
                start = max(count - 10, 0)
                end = count
                for item in results[start:end]:
                    st.markdown(f"**{item['artist']}** – *{item['title']}*")
                    if item["link"] and "youtube.com/watch" in item["link"]:
                        st.video(item["link"])
                    else:
                        st.warning("Video tidak ditemukan.")

                with left:
                    if count < len(results):
                        st.markdown("#### Masih kurang puas?")
                        if st.button("Tampilkan lebih banyak", key="more_song"):
                            st.session_state.shown_count += 10
                            rerun()

    elif ftype == "artist":
        artist = st.text_input("Masukkan nama penyanyi:")
        if artist:
            if artist != st.session_state.last_input:
                st.session_state.stored_results = recommend_by_artist(artist, top_n=100)
                st.session_state.shown_count = 10
                st.session_state.last_input = artist

            results = st.session_state.stored_results
            if not results:
                st.warning("Penyanyi tidak ditemukan.")
            else:
                start = max(count - 10, 0)
                end = count
                for item in results[start:end]:
                    st.markdown(f"**{item['artist']}** – *{item['title']}*")
                    if item["link"] and "youtube.com/watch" in item["link"]:
                        st.video(item["link"])
                    else:
                        st.warning("Video tidak ditemukan.")

                with left:
                    if count < len(results):
                        st.markdown("#### Masih kurang puas?")
                        if st.button("Tampilkan lebih banyak", key="more_artist"):
                            st.session_state.shown_count += 10
                            rerun()

    elif ftype == "mood" and st.session_state.selected_mood:
        mood = st.session_state.selected_mood
        if mood != st.session_state.last_input:
            st.session_state.stored_results = recommend_by_mood(mood, top_n=100)
            st.session_state.shown_count = 10
            st.session_state.last_input = mood

        results = st.session_state.stored_results
        if not results:
            st.warning("Tidak ada lagu ditemukan untuk mood ini.")
        else:
            st.subheader(f"🎶 Lagu untuk mood '{mood}'")
            start = max(count - 10, 0)
            end = count
            for item in results[start:end]:
                st.markdown(f"**{item['artist']}** – *{item['title']}*")
                if item["link"] and "youtube.com/watch" in item["link"]:
                    st.video(item["link"])
                else:
                    st.warning("Video tidak ditemukan.")

            with left:
                if count < len(results):
                    st.markdown("#### Masih kurang puas?")
                    if st.button("Tampilkan lebih banyak", key="more_mood"):
                        st.session_state.shown_count += 10
                        rerun()