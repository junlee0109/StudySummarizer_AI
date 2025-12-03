import streamlit as st
import requests

# ==========================
# 1. Groq API 설정
# ==========================

API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"  # ← 여기에 Groq 키를 넣어야 함

def call_ai_api(system_prompt, user_prompt):
    """
    Groq Chat Completions API 호출해서 '답변 텍스트만' 리턴
    """

    if not API_KEY:
        raise ValueError("⚠️ API_KEY가 비어있습니다. app.py 상단에 Groq API 키를 넣어주세요!")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        # Groq의 가장 안정적인 Llama 3.1 모델
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    response = requests.post(API_URL, headers=headers, json=data, timeout=60)

    # 오류 발생 시 메시지 표시
    if response.status_code != 200:
        raise ValueError(f"❌ API 오류: {response.status_code} - {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


# ==========================
# 2. 기능 함수 (요약, 질문답변)
# ==========================

def summarize_text(text):
    system = "너는 학생이 이해하기 쉽게 요약해주는 AI 선생님이다."
    prompt = f"다음 공부 내용을 학생 수준으로 쉽고 간단하게 3~5 문단으로 요약해줘.\n\n{text}"
    return call_ai_api(system, prompt)


def answer_question(context, question):
    system = "너는 주어진 공부 내용 안에서만 답변하는 AI 튜터이다."
    prompt = f"""
[공부 자료]
{context}

[질문]
{question}

⚠️ 공부 자료에 없는 내용은 절대 말하지마.
"""
    return call_ai_api(system, prompt)


# ==========================
# 3. Streamlit 화면 구성
# ==========================

st.set_page_config(page_title="StudySummarizer AI", layout="wide")

st.title("📘 StudySummarizer AI")
st.write("공부 자료를 요약하고, 질문에 답해주는 AI 기반 학습 도우미입니다.")

# ① 공부 자료 입력
st.subheader("1. 공부 자료 입력")
input_text = st.text_area(
    "여기에 공부 내용을 붙여 넣으세요.",
    height=250,
    placeholder="예: 교과서 일부, 프린트물 내용을 붙여 넣으세요."
)

# ② 요약 기능
summary = ""
if st.button("요약하기 ✨"):
    if not input_text.strip():
        st.warning("⚠️ 공부 자료를 먼저 입력하세요!")
    else:
        with st.spinner("📚 요약 생성 중..."):
            try:
                summary = summarize_text(input_text)
                st.session_state["summary"] = summary
                st.success("🎉 요약 완료!")
            except Exception as e:
                st.error(f"❌ 오류: {e}")

if "summary" in st.session_state:
    summary = st.session_state["summary"]

st.subheader("2. 요약 결과")
if summary:
    st.write(summary)
else:
    st.info("아직 요약 결과가 없습니다.")

# ③ 질문 기능
st.subheader("3. 질문하기")
question = st.text_input("궁금한 점을 입력하세요.")

if st.button("질문하기 💬"):
    if not input_text.strip():
        st.warning("📌 먼저 공부 내용을 입력하고 요약을 눌러주세요.")
    elif not question.strip():
        st.warning("📌 질문을 입력하세요!")
    else:
        with st.spinner("💡 답변 생성 중..."):
            try:
                context = input_text[:2000] + "\n\n[요약]\n" + summary
                answer = answer_question(context, question)
                st.success("🧠 답변:")
                st.write(answer)
            except Exception as e:
                st.error(f"❌ 오류: {e}")
