import streamlit as st
import openai

###############################################################################
# SETUP
###############################################################################
# 1) Provide your OpenAI API key (or load from Streamlit secrets / environment)
openai.api_key = "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# 2) Page Config for Streamlit
st.set_page_config(
    page_title="Agentic Six Talking Hats",
    layout="centered"
)

###############################################################################
# CSS for Dark Mode
###############################################################################
dark_css = """
<style>
body {
    background-color: #000000; /* black background */
    color: #ffffff;            /* white text */
}
[data-testid="stAppViewContainer"] {
    background-color: #000000 !important;
}
[data-testid="stHeader"] {
    background-color: #000000 !important;
}
[data-testid="stSidebar"] {
    background-color: #111111 !important;
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

###############################################################################
# SYSTEM MESSAGES FOR EACH HAT
###############################################################################
SYSTEM_MESSAGES = {
    "white": (
        "You are the White Hat. Focus on providing objective facts, data, "
        "and relevant information about the conversation so far. Avoid opinions."
    ),
    "red": (
        "You are the Red Hat. Offer emotional, instinctive, and intuitive responses "
        "to the conversation so far."
    ),
    "black": (
        "You are the Black Hat. Provide critical, cautious perspectives, highlighting "
        "potential problems or risks in the conversation so far."
    ),
    "yellow": (
        "You are the Yellow Hat. Provide optimistic, positive perspectives, "
        "emphasizing potential benefits and solutions."
    ),
    "green": (
        "You are the Green Hat. Offer creative, unconventional ideas in response "
        "to the conversation so far. Think outside the box."
    ),
    "blue": (
        "You are the Blue Hat. Summarize and synthesize all responses from the other "
        "hats and the user so far, reflecting on the overall process. Provide a coherent, "
        "big-picture recommendation or conclusion."
    )
}

###############################################################################
# OPENAI CHAT FUNCTION
###############################################################################
def chat_with_gpt(messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=200):
    """
    Sends a list of messages (with roles system/user/assistant) to the OpenAI ChatCompletion API.
    Returns the model's text response.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

###############################################################################
# APP LOGIC
###############################################################################
def generate_hat_response(hat_color, conversation):
    """
    1) Build a system message for the specified hat_color.
    2) Combine it with the entire conversation so far (user + hats).
    3) Get the hat's response from OpenAI and append to conversation.
    """
    system_msg = {"role": "system", "content": SYSTEM_MESSAGES[hat_color]}

    messages_for_api = [system_msg]
    # Convert our conversation (a list of dicts) into the API message format
    for entry in conversation:
        messages_for_api.append({
            "role": entry["role"],
            "content": entry["content"]
        })

    hat_output = chat_with_gpt(messages_for_api)
    
    # Append the hat's response to the conversation, labeling it
    conversation.append({
        "role": "assistant",
        "content": hat_output,
        "hat_color": hat_color.capitalize()  # E.g. "Red", "Green"
    })

    return conversation, hat_output

###############################################################################
# STREAMLIT APP
###############################################################################

# Initialize session state for conversation and final_synthesis
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "final_synthesis" not in st.session_state:
    st.session_state.final_synthesis = None

st.title("Agentic Six Talking Hats with Memory")

# Display the conversation history
if st.session_state.conversation:
    st.subheader("Conversation History")
    for entry in st.session_state.conversation:
        if "hat_color" in entry:
            # Display hat name
            st.markdown(f"**{entry['hat_color']} Hat**: {entry['content']}")
        else:
            # Display user or other role
            st.markdown(f"**{entry['role'].capitalize()}**: {entry['content']}")

# User input
user_prompt = st.text_input("Ask a question or follow-up")

# Button to process user prompt
if st.button("Send"):
    if user_prompt.strip():
        # 1) Add user message
        st.session_state.conversation.append({
            "role": "user",
            "content": user_prompt
        })
        # 2) Hats respond in sequence
        st.session_state.conversation, _ = generate_hat_response("white",  st.session_state.conversation)
        st.session_state.conversation, _ = generate_hat_response("red",    st.session_state.conversation)
        st.session_state.conversation, _ = generate_hat_response("black",  st.session_state.conversation)
        st.session_state.conversation, _ = generate_hat_response("yellow", st.session_state.conversation)
        st.session_state.conversation, _ = generate_hat_response("green",  st.session_state.conversation)

        # 3) Blue Hat for final synthesis
        st.session_state.conversation, synthesis = generate_hat_response("blue", st.session_state.conversation)
        st.session_state.final_synthesis = synthesis

        # Rerun to display updated conversation
        st.experimental_rerun()

# If there's a final synthesis, show it in a separate section
if st.session_state.final_synthesis:
    st.write("---")
    st.subheader("Blue Hat's Synthesis")
    st.write(st.session_state.final_synthesis)

# Reset button to clear conversation
if st.button("Reset Conversation"):
    st.session_state.conversation = []
    st.session_state.final_synthesis = None
    st.experimental_rerun()
