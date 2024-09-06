import pandas as pd
import streamlit as st
import random
import sqlite3 as sql
from prometheus_client import Counter, start_http_server, CollectorRegistry

# Create a global variable to track if Prometheus counters are initialized
metrics_initialized = False

# Function to initialize Prometheus counters only once
def initialize_metrics():
    global metrics_initialized
    if not metrics_initialized:
        global TOTAL_GUESSES, CORRECT_GUESSES, FAILED_GUESSES, TOTAL_USERS
        
        TOTAL_GUESSES = Counter('total_guesses', 'Total number of guesses', registry=CollectorRegistry(auto_describe=False))
        CORRECT_GUESSES = Counter('correct_guesses', 'Total number of correct guesses', registry=CollectorRegistry(auto_describe=False))
        FAILED_GUESSES = Counter('failed_guesses', 'Total number of failed guesses', registry=CollectorRegistry(auto_describe=False))
        TOTAL_USERS = Counter('num_of_users', 'Total number of unique users', registry=CollectorRegistry(auto_describe=False))
        
        metrics_initialized = True

# Start Prometheus server on port 8901 only once
def start_prometheus_server():
    if not hasattr(st, 'prometheus_started'):
        start_http_server(8901, addr='0.0.0.0')
        st.prometheus_started = True

# Call the functions to ensure Prometheus is initialized correctly
initialize_metrics()
start_prometheus_server()

# SQLite Database Setup
db = sql.connect("guessGame.db")
c = db.cursor()

# Create the table with a UNIQUE constraint on the name column
c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                score INTEGER NOT NULL,
                trials_left INTEGER NOT NULL
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
if 'user_registered' not in st.session_state:
    st.session_state.user_registered = False

# Centered title
st.markdown("<h1 style='text-align: center;'>🎮 GUESSING GAME 🎮</h1>", unsafe_allow_html=True)

# Input field for the user name
user = st.text_input("Enter your name")

# Function to check if the username is unique
def is_unique_user(user_name):
    c.execute("SELECT name FROM users WHERE name = ?", (user_name,))
    result = c.fetchone()
    return result is None  # Returns True if the user is not found, meaning it's unique

# Function to register the user if the name is unique
def register_user():
    if user and not st.session_state.user_registered:
        if is_unique_user(user):
            TOTAL_USERS.inc()
        st.session_state.user_registered = True

# Input field for the number guess
input_value = st.text_input(placeholder="Enter number between 1 and 100", label="guessGame", label_visibility="hidden")

# Function to calculate score based on remaining trials
def calculate_score(trials_left):
    # If user has all trials left, score is 100
    return trials_left * 20

# Function to save or update the user's score in the database
def save_or_update_score(user_name, score, trials_left):
    # Check if user already exists
    c.execute("SELECT name FROM users WHERE name = ?", (user_name,))
    result = c.fetchone()
    
    if result:
        # User exists, update score and trials_left
        c.execute("UPDATE users SET score = ?, trials_left = ? WHERE name = ?", (score, trials_left, user_name))
    else:
        # User doesn't exist, insert new record
        c.execute("INSERT INTO users (name, score, trials_left) VALUES (?, ?, ?)", (user_name, score, trials_left))
    
    db.commit()

# Function to retrieve and display all user scores
def display_scores():
    c.execute("SELECT name, score, trials_left FROM users ORDER BY score DESC")
    results = c.fetchall()

    if results:
        st.markdown("<h2 style='text-align: center;'>Leaderboard</h2>", unsafe_allow_html=True)
        df = pd.DataFrame(results, columns=["Name", "Score", "Trials Left"]).reset_index(drop=True)
        st.table(df)
    else:
        st.markdown("<h2 style='text-align: center;'>No scores available</h2>", unsafe_allow_html=True)

# Function to handle the guess button click
def guess():
    if not input_value:
        st.markdown("<h2 style='text-align: center; color: red;'>Please enter a number between 1 and 100</h2>", unsafe_allow_html=True)
    else:
        try:
            user_guess = int(input_value)
            TOTAL_GUESSES.inc()  # Increment total guesses counter
            if user_guess < 1 or user_guess > 100:
                st.markdown("<h2 style='text-align: center; color: red;'>Please enter a valid number between 1 and 100</h2>", unsafe_allow_html=True)
            elif user_guess == st.session_state.RAND_INT:
                st.markdown(f"<h2 style='text-align: center; color: green;'>Congratulations {user}! You guessed the number correctly. It was {st.session_state.RAND_INT}!</h2>", unsafe_allow_html=True)
                CORRECT_GUESSES.inc()  # Increment correct guesses counter
                st.session_state.game_over = True
                
                # Calculate score based on remaining trials
                score = calculate_score(st.session_state.trial)
                
                # Save or update the user's score in the database
                save_or_update_score(user, score, st.session_state.trial)
                
                st.markdown(f"<h2 style='text-align: center;'>Your score is: {score}</h2>", unsafe_allow_html=True)
            elif user_guess < st.session_state.RAND_INT:
                st.markdown("<h2 style='text-align: center; color: red;'>You guessed low. Please try again!</h2>", unsafe_allow_html=True)
                st.session_state.trial -= 1
                FAILED_GUESSES.inc()  # Increment failed guesses counter
            elif user_guess > st.session_state.RAND_INT:
                st.markdown("<h2 style='text-align: center; color: red;'>You guessed high. Please try again!</h2>", unsafe_allow_html=True)
                st.session_state.trial -= 1
                FAILED_GUESSES.inc()  # Increment failed guesses counter

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
    st.session_state.user_registered = False  # Reset user registration
    
register_user()

# Display guess button only if the game is not over
if not st.session_state.game_over:
    if st.button("Guess"):
        guess()

# Button to start a new game if the game is over
if st.session_state.game_over:
    if st.button("Start New Game"):
        new_game()

# Display the number of trials left
st.write(f"You have {st.session_state.trial} trials left.")

# Button to toggle leaderboard visibility
if st.button("Toggle Leaderboard"):
    st.session_state.show_leaderboard = not st.session_state.show_leaderboard

# Display leaderboard if the button was clicked
if st.session_state.show_leaderboard:
    display_scores()
