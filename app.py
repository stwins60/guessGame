import streamlit as st
import random

# Initialize session state for the random number and trial count
if 'trial' not in st.session_state:
    st.session_state.trial = 5
if 'RAND_INT' not in st.session_state:
    st.session_state.RAND_INT = random.randint(1, 101)
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# Centered title
st.markdown("<h1 style='text-align: center;'>GUESSING GAME</h1>", unsafe_allow_html=True)

# Input field
input_value = st.text_input(placeholder="Enter number between 1 and 100", label="guessGame", label_visibility="hidden")

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
                st.markdown(f"<h2 style='text-align: center; color: green;'>Congratulations! You guessed the number correctly. It was {st.session_state.RAND_INT}!</h2>", unsafe_allow_html=True)
                st.session_state.game_over = True
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

def new_game():
    st.session_state.game_over = False
    st.session_state.trial = 5
    st.session_state.RAND_INT = random.randint(1, 101)
    

# Button with on_click function
if st.session_state.game_over:
    st.button("Guess", disabled=True)
    if st.button("Start New Game"):
        new_game()
else:
    st.button("Guess", on_click=guess)
    


# Display the number of trials left
st.write(f"You have {st.session_state.trial} trials left.")
