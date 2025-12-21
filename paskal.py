import streamlit as st
import time
import pandas as pd

st.set_page_config(page_title="파스칼 삼각형", layout="centered")

st.title("파스칼 삼각형")

# -------------------------------
# 기본 함수들
# -------------------------------
def pascal_triangle(n_rows=16):
    tri = []
    for n in range(n_rows):
        if n == 0:
            tri.append([1])
        else:
            p = tri[-1]
            tri.append([1] + [p[i] + p[i + 1] for i in range(len(p) - 1)] + [1])
    return tri

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True

# 기본 삼각형
ROWS = 16
tri = pascal_triangle(ROWS)

# -------------------------------
# 보기 모드
# -------------------------------
st.sidebar.header("📌 보기 옵션")
option = st.sidebar.radio(
    "표시할 특징을 선택하세요 (하나만 선택)",
    (
        "2ⁿ 관계 보기",
        "하키스틱 원리 보기",
        "피보나치 관계 보기",
        "이항정리 관계 보기",
        "프랙탈 구조 보기",
        "소수 행 특징 보기",
    ),
)

show_sum     = (option == "2ⁿ 관계 보기")
show_hockey  = (option == "하키스틱 원리 보기")
show_fibo    = (option == "피보나치 관계 보기")
show_binom   = (option == "이항정리 관계 보기")
show_fractal = (option == "프랙탈 구조 보기")
show_prime   = (option == "소수 행 특징 보기")

# -------------------------------
# 하키스틱 설정
# -------------------------------
if show_hockey:
    max_col   = min(ROWS - 2, 11)
    start_col = st.sidebar.slider("열 위치 (r)", 0, max_col, 2)
    max_len   = max(2, (ROWS - 1) - start_col)
    length    = st.sidebar.slider("대각선 길이 (칸 수)", 2, max_len, min(5, max_len))
    diag_cells = {(start_col + t, start_col) for t in range(length)}
    end_cell   = (start_col + length, start_col + 1)
else:
    diag_cells = set()
    end_cell   = (-1, -1)

# -------------------------------
# 세션 상태
# -------------------------------
if "fibo_step" not in st.session_state:
    st.session_state.fibo_step = 0
if "fibo_play" not in st.session_state:
    st.session_state.fibo_play = False
if "fractal_rows" not in st.session_state:
    st.session_state.fractal_rows = 8
if "fractal_play" not in st.session_state:
    st.session_state.fractal_play = False
if "fibo_speed" not in st.session_state:
    st.session_state.fibo_speed = 0.8
if "fractal_done" not in st.session_state:
    st.session_state.fractal_done = False

# -------------------------------
# 피보나치 경로 및 합
# -------------------------------
fibo_paths, fib_vals = [], []
for n in range(1, ROWS + 1):
    path = []
    for k in range(n):
        i = n - 1 - k
        if 0 <= i < len(tri) and 0 <= k < len(tri[i]):
            path.append((i, k))
    fibo_paths.append(path)
    fib_vals.append(sum(tri[i][j] for (i, j) in path))

# -------------------------------
# 프랙탈용 삼각형
# -------------------------------
MAX_FRACTAL_ROWS = 32
tri_to_show = pascal_triangle(st.session_state.fractal_rows) if show_fractal else tri

# -------------------------------
# ✅ 프랙탈 색칠 기준 (selectbox → radio만 변경)
# -------------------------------
if show_fractal:
    st.sidebar.markdown("🎨 색칠 기준")
    color_mode = st.sidebar.radio(
        "색칠 기준 선택",
        ("홀수(시어핀스키삼각형)", "짝수", "2의 배수", "3의 배수", "4의 배수", "5의 배수"),
        index=0,
    )
else:
    color_mode = None

# 소수 행 모드 슬라이더
if show_prime:
    prime_row = st.sidebar.slider("확인할 행 번호 p", 2, ROWS - 1, 7)
else:
    prime_row = None

# -------------------------------
# 본 시각화
# -------------------------------
if show_fibo:
    colA, colB = st.columns([2, 1])
else:
    colA = st.container()
    colB = None

with colA:
    BOX, GAP = 26, 4
    html = ["<div style='font-family:monospace; text-align:center;'>"]
    for i, row in enumerate(tri_to_show):
        html.append("<div style='display:flex; justify-content:center; margin:1px;'>")
        html.append(f"<div style='display:flex; justify-content:center; gap:{GAP}px;'>")
        for j, val in enumerate(row):
            color  = "#FFFFFF"
            border = "1px solid #ccc"

            if show_hockey:
                if (i, j) in diag_cells:
                    color = "#FFF59D"
                if (i, j) == end_cell:
                    color = "#FF7043"

            if show_fibo:
                cur  = st.session_state.fibo_step - 1
                upto = min(max(st.session_state.fibo_step, 0), len(fibo_paths))
                palette = ["#A3E4D7", "#AED6F1", "#F9E79F", "#F5B7B1", "#D7BDE2"]
                for idx in range(upto):
                    for (r, c) in fibo_paths[idx]:
                        if (i, j) == (r, c):
                            color = palette[idx % len(palette)]
                if 0 <= cur < len(fibo_paths):
                    if (i, j) in fibo_paths[cur]:
                        color  = palette[cur % len(palette)]
                        border = "2px solid #1F618D"

            if show_fractal:
                if color_mode == "홀수(시어핀스키삼각형)":
                    color = "#000000" if val % 2 == 1 else "#FFFFFF"
                elif color_mode == "짝수":
                    color = "#000000" if val % 2 == 0 else "#FFFFFF"
                elif color_mode == "2의 배수":
                    color = "#000000" if val % 2 == 0 else "#FFFFFF"
                elif color_mode == "3의 배수":
                    color = "#000000" if val % 3 == 0 else "#FFFFFF"
                elif color_mode == "4의 배수":
                    color = "#000000" if val % 4 == 0 else "#FFFFFF"
                elif color_mode == "5의 배수":
                    color = "#000000" if val % 5 == 0 else "#FFFFFF"

            if show_prime and i == prime_row:
                if is_prime(prime_row):
                    if j == 0 or j == len(row) - 1:
                        color = "#FFF59D"
                    elif val % prime_row == 0:
                        color = "#F28B82"
                else:
                    color = "#E0E0E0"

            if show_binom:
                n_sel = st.session_state.get("binomial_row", 4)
                if i == n_sel:
                    color = "#FFF59D"

            html.append(
                f"<div style='width:{BOX}px; height:{BOX}px; background:{color}; "
                f"border:{border}; border-radius:6px; display:flex; align-items:center; "
                f"justify-content:center; font-size:13px; font-weight:600;'>{val}</div>"
            )
        html.append("</div>")
        if show_sum:
            s = sum(row)
            html.append(f"<div style='margin-left:10px; color:#6b7280; font-size:13px;'>→ 합 = {s} = 2<sup>{i}</sup></div>")
        html.append("</div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# -------------------------------
# 이하 (피보나치 그래프, 애니메이션, 자동 리셋)
# → 네가 준 코드와 완전히 동일
# -------------------------------
