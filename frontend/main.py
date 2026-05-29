from __future__ import annotations

import json
import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Banking AI Agent", page_icon="🏦", layout="wide")


def run_agent(customer_id: str, message: str) -> dict:
    payload = {"customer_id": customer_id or None, "message": message}
    response = requests.post(f"{API_BASE_URL}/run-agent", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


st.markdown(
    """
    <style>
            .block-container {
                padding-top: 1.25rem;
                padding-bottom: 2rem;
                max-width: 1100px;
            }
            #MainMenu, footer, header {
                visibility: hidden;
            }
      .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0b1220 100%);
        color: #d1fae5;
        padding: 1.5rem 1.8rem;
        border-radius: 24px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35);
      }
      .hero h1 { color: #86efac; }
      .hero .subtle { color: #bbf7d0; }
      .panel {
        background: #ffffff;
        border-radius: 20px;
        border: 1px solid #dbe4f0;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
        color: #0f172a;
      }
            .stTextInput input, .stTextArea textarea {
                border-radius: 14px;
            }
            .stTextInput label, .stTextArea label, .stMarkdown, .stCaption, .stSubheader, .stMetricLabel {
                color: #0f172a !important;
            }
            .panel .stMarkdown p, .panel .stMarkdown div, .panel .stCaption, .panel .stText, .panel li {
                color: #0f172a !important;
            }
            .stButton > button {
                background: #38bdf8;
                color: #082f49;
                border: none;
                border-radius: 999px;
                padding: 0.65rem 1.2rem;
                font-weight: 700;
            }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1 style="margin-bottom:0.35rem;">Banking AI Agent</h1>
      <p class="subtle" style="margin-top:0; margin-bottom:0;">Giao diện web đơn giản để gửi câu hỏi khách hàng và xem kết quả workflow của backend.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.subheader("Nhập yêu cầu")
customer_id = st.text_input("Customer ID", value="C001", placeholder="C001")
message = st.text_area(
    "Customer message",
    value="My transfer failed 20 minutes ago and money was debited from my account",
    height=180,
)
submitted = st.button("Run Agent", use_container_width=False)
st.caption(f"Backend API: {API_BASE_URL}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.subheader("Kết quả")
if submitted:
    if not message.strip():
        st.warning("Vui lòng nhập message trước khi chạy agent.")
    else:
        with st.spinner("Đang xử lý workflow..."):
            try:
                result = run_agent(customer_id, message)
                st.success("Đã nhận kết quả từ backend.")

                intent = result.get("intent", {})
                routing = result.get("routing", {})
                draft = result.get("draft", {})

                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.markdown(
                    f"**Intent**  \n<span style='font-size:1.05rem; color:#0f172a;'>{intent.get('intent', 'N/A')}</span>",
                    unsafe_allow_html=True,
                )
                metric_col2.metric("Priority", result.get("priority", {}).get("priority", "N/A"))
                metric_col3.metric("Action", routing.get("action", "N/A"))

                st.markdown("#### Draft phản hồi")
                st.write(draft.get("draft_reply", ""))

                st.markdown("#### Thông tin còn thiếu")
                missing_information = draft.get("missing_information", [])
                st.write(missing_information if missing_information else ["Không có"])

                st.markdown("#### Kết quả đầy đủ")
                st.json(result)
            except requests.HTTPError as exc:
                st.error(f"Backend trả lỗi HTTP: {exc.response.status_code}")
                st.code(exc.response.text)
            except Exception as exc:
                st.error(f"Không thể gọi backend: {exc}")
else:
    st.info("Nhập message rồi bấm Run Agent để xem JSON kết quả từ backend.")
st.markdown("</div>", unsafe_allow_html=True)
