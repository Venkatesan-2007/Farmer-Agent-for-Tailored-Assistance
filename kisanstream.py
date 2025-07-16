import streamlit as st
import time

def show_success_page():
    """
    Displays the success page in Streamlit.
    """
    st.empty() # Clear the main content
    st.success("✔ Verified Successfully!", icon="✅")
    st.balloons()
    time.sleep(2)
    st.info("Navigating to Home Screen (Simulated: App would typically transition here).")
    st.stop() # Stop the execution after success (simulating app exit or full navigation)

def app():
    """
    Main Streamlit application for Kisan Card Authentication.
    """
    st.set_page_config(
        page_title="Kisan Card Authentication",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for styling
    st.markdown("""
        <style>
        .stApp {
            background-color: #DDE40A; /* Background color for the main window */
        }
        .card-frame {
            background-color: white;
            border: 2px solid #0AD03F;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
            margin-top: 50px;
            margin-bottom: 50px;
        }
        .title-text {
            font-size: 32px;
            font-weight: bold;
            color: #0AD03F;
            text-align: center;
            margin-bottom: 20px;
        }
        .instruction-text {
            font-size: 14px;
            color: gray;
            text-align: center;
            margin-bottom: 20px;
        }
        .stTextInput > div > div > input {
            text-align: center;
            font-size: 20px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        .stButton > button {
            background-color: #29B927; /* Background color */
            color: white;    /* Text color */
            font-size: 20px;
            font-weight: bold;
            padding: 10px 40px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #0AD03F; /* Active background color */
            color: white;
        }
        .validation-icon {
            font-size: 24px;
            text-align: center;
            height: 30px;
            margin-top: -10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-frame">', unsafe_allow_html=True)
    st.markdown('<div class="title-text">Kisan Card Authentication</div>', unsafe_allow_html=True)

    code = st.text_input(
        "Enter 12 Digit number in Kisan Card",
        max_chars=12,
        key="kisan_code",
        help="Please enter the 12-digit number from your Kisan Card."
    )

    validation_message_placeholder = st.empty()
    loading_message_placeholder = st.empty()

    is_code_valid = False
    if code:
        if code.isdigit() and len(code) == 12:
            is_code_valid = True
            validation_message_placeholder.markdown('<div class="validation-icon" style="color:green;">✔</div>', unsafe_allow_html=True)
        else:
            validation_message_placeholder.markdown('<div class="validation-icon" style="color:red;">❌ Invalid Format</div>', unsafe_allow_html=True)
    else:
        validation_message_placeholder.markdown('<div class="validation-icon"></div>', unsafe_allow_html=True)


    if st.button("Verify"):
        if is_code_valid:
            loading_message_placeholder.info("Verifying...")
            time.sleep(2) # Simulate network delay

            if code == "123456789123":
                show_success_page()
            else:
                st.error("❌ Invalid Data")
                loading_message_placeholder.empty() # Clear loading message
        else:
            st.warning('⚠️ Please enter 12 digits')
            loading_message_placeholder.empty() # Clear loading message

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()