import streamlit as st
import random
import sqlite3 as sql

db = sql.connect("guessGame.db")
c = db.cursor()

c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
            """)

# Initialize session state for the random number and trial count
if 'trial' not in st.session_state:
    st.session_state.trial = 5
if 'RAND_INT' not in st.session_state:
    st.session_state.RAND_INT = random.randint(1, 100)
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'show_leaderboard' not in st.session_state:
    st.session_state.show_leaderboard = False

# Centered title
st.markdown("<h1 style='text-align: center;'>🎮 GUESSING GAME 🎮</h1>", unsafe_allow_html=True)

# Input field for the user name
user = st.text_input("Enter your name")

# Input field for the number guess
input_value = st.text_input(placeholder="Enter number between 1 and 100", label="guessGame", label_visibility="hidden")

# Function to save the user's name and score in the database
def save_score(user_name, score):
    c.execute("INSERT INTO users (name, score) VALUES (?, ?)", (user_name, score))
    db.commit()

# Function to retrieve and display all user scores
def display_scores():
    c.execute("SELECT name, score FROM users ORDER BY score DESC")
    results = c.fetchall()

    if results:
        st.markdown("<h2 style='text-align: center;'>Leaderboard</h2>", unsafe_allow_html=True)
        for row in results:
            st.write(f"Name: {row[0]}, Score: {row[1]}")
    else:
        st.markdown("<h2 style='text-align: center;'>No scores available</h2>", unsafe_allow_html=True)

# Function to handle the button click
def guess():
    if not input_value:
        st.markdown("<h2 style='text-align: center; color: red;'>Please enter a number between 1 and 100</h2>", unsafe_allow_html=True)
    else:
        try:
            user_guess = int(input_value)
            if user_guess < 1 or user_guess > 100:
                st.markdown("<h2 style='text-align: center; color: red;'>Please enter a valid number between 1 and 100</h2>", unsafe_allow_html=True)
            elif user_guess == st.session_state.RAND_INT:
                st.markdown(f"<h2 style='text-align: center; color: green;'>Congratulations {user}! You guessed the number correctly. It was {st.session_state.RAND_INT}!</h2>", unsafe_allow_html=True)
                st.session_state.game_over = True
                
                # Calculate score based on remaining trials
                score = st.session_state.trial
                
                # Save user's name and score to the database
                save_score(user, score)
                
                st.markdown(f"<h2 style='text-align: center;'>Your score is: {score}</h2>", unsafe_allow_html=True)
            elif user_guess < st.session_state.RAND_INT:
                st.markdown("<h2 style='text-align: center; color: red;'>You guessed low. Please try again!</h2>", unsafe_allow_html=True)
                st.session_state.trial -= 1
            elif user_guess > st.session_state.RAND_INT:
                st.markdown("<h2 style='text-align: center; color: red;'>You guessed high. Please try again!</h2>", unsafe_allow_html=True)
                st.session_state.trial -= 1

            if st.session_state.trial <= 0:
                st.markdown(f"<h2 style='text-align: center; color: red;'>Game Over! The correct number was {st.session_state.RAND_INT}.</h2>", unsafe_allow_html=True)
                st.session_state.game_over = True
        except ValueError:
            st.markdown("<h2 style='text-align: center; color: red;'>Please enter a valid number between 1 and 100</h2>", unsafe_allow_html=True)

# Function to start a new game
def new_game():
    st.session_state.game_over = False
    st.session_state.trial = 5
    st.session_state.RAND_INT = random.randint(1, 100)
    st.session_state.show_leaderboard = False  # Reset leaderboard view

# Display guess button only if the game is not over
if not st.session_state.game_over:
    if st.button("Guess"):
        guess()

# Button to start a new game if the game is over
if st.session_state.game_over:
    if st.button("Start New Game"):
        new_game()
        # st.experimental_rerun()

# Display the number of trials left
st.write(f"You have {st.session_state.trial} trials left.")

# Button to toggle leaderboard visibility
if st.button("Toggle Leaderboard"):
    st.session_state.show_leaderboard = not st.session_state.show_leaderboard

# Display leaderboard if the button was clicked
if st.session_state.show_leaderboard:
    display_scores()
