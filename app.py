import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Spotify Fun Analyzer", layout="wide")
st.title("🎧 Spotify Fun Analyzer — Mahan's Edition")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=True, low_memory=False)
    dt_cols = [c for c in df.columns if 'date' in c or 'time' in c or 'played' in c]
    if dt_cols:
        for c in dt_cols:
            try:
                df[c] = pd.to_datetime(df[c])
            except:
                pass
    return df

df = load_data("data/full_clean_spotify_data.csv")
st.sidebar.header("Controls")
min_plays = st.sidebar.slider("Minimum plays to include for top lists", 1, 5, 2)

st.header("Dataset snapshot")
st.write(df.head())

# Top artists
st.subheader("Top Artists")
if 'artist_name' in df.columns:
    artist_counts = df['artist_name'].value_counts().reset_index()
    artist_counts.columns = ['artist','plays']
    st.dataframe(artist_counts.head(20))
    top_artist = artist_counts.iloc[0]['artist']
    st.markdown(f"**Most listened artist:** {top_artist}")
else:
    st.info("No 'artist_name' column found in dataset.")

# Top tracks
st.subheader("Top Tracks")
if 'track_name' in df.columns:
    track_counts = df['track_name'].value_counts().reset_index()
    track_counts.columns = ['track','plays']
    st.dataframe(track_counts.head(20))
else:
    st.info("No 'track_name' column found in dataset.")

# Listening by hour heatmap
st.subheader("Listening by Hour and Day")
if 'play_hour' in df.columns and 'play_dayofweek' in df.columns:
    heat = df.groupby(['play_dayofweek','play_hour']).size().reset_index(name='plays')
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat['play_dayofweek'] = pd.Categorical(heat['play_dayofweek'], categories=days, ordered=True)
    chart = alt.Chart(heat).mark_rect().encode(
        x=alt.X('play_hour:O', title='Hour of day'),
        y=alt.Y('play_dayofweek:N', title='Day of week'),
        color='plays:Q',
        tooltip=['play_dayofweek','play_hour','plays']
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No play_hour/play_dayofweek columns to build heatmap.")

# Fun: Mood playlist generator (mock)
st.subheader("Mood Playlist Generator (fun, not live)")
mood = st.selectbox("Choose a mood", ["Chill","Energetic","Sad","Romantic","Focus"])
def mood_picker(df,mood,limit=10):
    if 'track_name' in df.columns:
        picks = df['track_name'].value_counts().index.tolist()
        np.random.seed(abs(hash(mood)) % 2**32)
        np.random.shuffle(picks)
        return picks[:limit]
    else:
        return []

playlist = mood_picker(df, mood, 10)
st.write("Here's a playful playlist for **" + mood + "**:")
for i,t in enumerate(playlist,1):
    st.write(f"{i}. {t}")

# Mini stats
st.subheader("Mini Stats")
col1,col2,col3 = st.columns(3)
with col1:
    st.metric("Total plays", int(len(df)))
with col2:
    if 'ms_played' in df.columns:
        st.metric("Total listening hours", round(df['ms_played'].sum()/1000/60/60,2))
    else:
        st.metric("Total listening hours", "N/A")
with col3:
    if 'track_name' in df.columns:
        st.metric("Unique tracks", int(df['track_name'].nunique()))
    else:
        st.metric("Unique tracks", "N/A")
