import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="HR Chat Agent",
    page_icon="💬",
    layout="centered",
)


def initialize_session_state():
    defaults = {
        "token": None,
        "employee_id": None,
        "conversation_id": None,
        "messages": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login(employee_id: str, password: str):
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "employee_id": employee_id,
            "password": password,
        },
        timeout=30,
    )

    if response.status_code == 200:
        return response.json()

    return None


def create_conversation():
    response = requests.post(
        f"{API_BASE_URL}/chat/conversations",
        headers={
            "Authorization": f"Bearer {st.session_state.token}"
        },
        timeout=30,
    )

    if response.status_code == 200:
        return response.json()["conversation_id"]

    if response.status_code == 401:
        st.session_state.token = None

    raise RuntimeError(
        f"Unable to create conversation: "
        f"{response.status_code} {response.text}"
    )


def send_message(message: str):
    response = requests.post(
        f"{API_BASE_URL}/chat",
        headers={
            "Authorization": f"Bearer {st.session_state.token}"
        },
        json={
            "conversation_id": st.session_state.conversation_id,
            "message": message,
        },
        timeout=120,
    )

    if response.status_code == 200:
        return response.json()

    if response.status_code == 401:
        st.session_state.token = None

    raise RuntimeError(
        f"Unable to process chat request: "
        f"{response.status_code} {response.text}"
    )


def logout():
    st.session_state.token = None
    st.session_state.employee_id = None
    st.session_state.conversation_id = None
    st.session_state.messages = []


initialize_session_state()


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.token:

    st.title("💬 HR Chat Agent")

    st.write(
        "Secure HR assistant powered by FastAPI, LangGraph, "
        "RAG, SQLite and Ollama."
    )

    st.divider()

    st.subheader("Employee Login")

    with st.form("login_form"):

        employee_id = st.text_input(
            "Employee ID",
            placeholder="EMP1001",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Password@123",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:

        if not employee_id or not password:
            st.error("Please enter Employee ID and password.")

        else:
            try:
                result = login(employee_id, password)

                if result:

                    st.session_state.token = result["access_token"]
                    st.session_state.employee_id = employee_id

                    st.session_state.conversation_id = (
                        create_conversation()
                    )

                    st.session_state.messages = []

                    st.success("Login successful.")

                    st.rerun()

                else:
                    st.error(
                        "Invalid employee ID or password."
                    )

            except requests.RequestException as exc:
                st.error(
                    f"Unable to connect to HR API: {exc}"
                )

            except Exception as exc:
                st.error(str(exc))


# ============================================================
# CHAT SCREEN
# ============================================================

else:

    st.title("💬 HR Chat Agent")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.caption(
            f"Authenticated employee: "
            f"{st.session_state.employee_id}"
        )

    with col2:
        if st.button("Logout"):
            logout()
            st.rerun()

    st.divider()

    # Display conversation history
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input(
        "Ask an HR question..."
    )

    if prompt:

        # Display user message immediately
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # Call FastAPI
        try:

            with st.chat_message("assistant"):

                with st.spinner(
                    "HR Agent is thinking..."
                ):

                    result = send_message(prompt)

                    answer = result["message"]

                    st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except requests.RequestException as exc:

            st.error(
                f"Unable to connect to HR API: {exc}"
            )

        except Exception as exc:

            st.error(str(exc))