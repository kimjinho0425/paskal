import streamlit as st
import time
import pandas as pd

st.set_page_config(page_title="파스칼 삼각형 시각화", layout="centered")

st.title("🔺 파스칼 삼각형 시각화")
st.write("파스칼 삼각형은 **위의 두 수를 더해서 아래에 쓰는 규칙**으로 만들어져요.")
st.write("각 행의 합은 항상 2의 거듭제곱이고, 대각선을 따라 더하면 **하키스틱 원리**가 나타나요!")
st.write("또한, 특정 대각선의 합은 **피보나치 수열**을 이룹니다!")

# -------------------------------
# 파스칼 삼각형 생성
# -------------------------------
def pascal_triangle(n_rows=15):
    tri = []
    for n in range(n_rows):
        if n == 0:
            tri.append([1])
        else:
            p = tri[-1]
            tri.append([1] + [p[i] + p[i+1] for i in range(len(p)-1)] + [1])
    return tri

ROWS = 15
tri = pascal_triangle(ROWS)

# -------------------------------
# 보기 옵션
# -------------------------------
st.sidebar.header("📌 보기 옵션")
option = st.sidebar.radio(
    "표시할 특징을 선택하세요 (하나만 선택)",
    ("2ⁿ 관계 보기", "하키스틱 원리 보기", "피보나치 관계 (시각화 ver)"),
)
show_sum = (option == "2ⁿ 관계 보기")
show_hockey = (option == "하키스틱 원리 보기")
show_fibo = (option == "피보나치 관계 (시각화 ver)")

# -------------------------------
# 하키스틱 설정
# -------------------------------
if show_hockey:
    max_col = min(ROWS - 2, 11)
    start_col = st.sidebar.slider("열 위치 (r)", 0, max_col, 2)
    max_len = max(2, (ROWS - 1) - start_col)
    length = st.sidebar.slider("대각선 길이 (칸 수)", 2, max_len, min(5, max_len))
    diag_cells = {(start_col + t, start_col) for t in range(length)}
    end_cell = (start_col + length, start_col + 1)
else:
    diag_cells = set()
    end_cell = (-1, -1)

# -------------------------------
# 피보나치 시각화 설정
# -------------------------------
if "fibo_step" not in st.session_state:
    st.session_state.fibo_step = 0
if "fibo_play" not in st.session_state:
    st.session_state.fibo_play = False

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
# 피보나치 시각화 영역
# -------------------------------
if show_fibo:
    col1, col2 = st.columns([2, 1])

    with st.sidebar:
        speed = st.slider("속도 (초/스텝)", 0.2, 1.0, 0.6, 0.1)
        c1, c2, c3 = st.columns(3)
        if c1.button("▶ 시작"):
            st.session_state.fibo_play = True
            if st.session_state.fibo_step <= 0:
                st.session_state.fibo_step = 1
        if c2.button("⏸ 정지"):
            st.session_state.fibo_play = False
        if c3.button("⟳ 초기화"):
            st.session_state.fibo_play = False
            st.session_state.fibo_step = 0

    # ---------------------------
    # 왼쪽: 파스칼 삼각형
    # ---------------------------
    with col1:
        BOX, GAP = 28, 4
        color_palette = ["#A3E4D7", "#AED6F1", "#F9E79F", "#F5B7B1", "#D7BDE2",
                         "#FAD7A0", "#ABEBC6", "#D2B4DE", "#F5CBA7", "#A9CCE3"]

        html = ["<div style='font-family:monospace; text-align:center;'>"]
        for i, row in enumerate(tri):
            html.append("<div style='display:flex; justify-content:center; align-items:center; margin:1.5px 0;'>")
            html.append(f"<div style='display:flex; justify-content:center; gap:{GAP}px;'>")

            for j, val in enumerate(row):
                color = "#FFFFFF"
                border = "1px solid #ccc"

                cur = st.session_state.fibo_step - 1
                upto = min(max(st.session_state.fibo_step, 0), len(fibo_paths))

                # 이미 계산된 대각선은 색 표시
                for idx in range(upto):
                    for (r, c) in fibo_paths[idx]:
                        if (i, j) == (r, c):
                            color = color_palette[idx % len(color_palette)]

                # 현재 진행 중인 대각선은 강조
                if 0 <= cur < len(fibo_paths):
                    if (i, j) in fibo_paths[cur]:
                        color = color_palette[cur % len(color_palette)]
                        border = "2px solid #1F618D"

                html.append(
                    f"<div style='width:{BOX}px; height:{BOX}px; background:{color}; "
                    f"border:{border}; border-radius:6px; display:flex; "
                    f"align-items:center; justify-content:center; font-size:13px; font-weight:600;'>{val}</div>"
                )
            html.append("</div>")
            html.append("</div>")
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

    # ---------------------------
    # 오른쪽: 피보나치 막대그래프
    # ---------------------------
    with col2:
        st.subheader("📈 피보나치 수 누적 그래프")
        step = st.session_state.fibo_step
        if step > 0:
            df = pd.DataFrame({
                "Diagonal": list(range(1, step + 1)),
                "Value": fib_vals[:step]
            })
        else:
            df = pd.DataFrame({"Diagonal": [], "Value": []})

        st.bar_chart(df, x="Diagonal", y="Value", height=320, use_container_width=True)

        if step > 0:
            st.caption(f"현재 진행: 대각선 {step} / {len(fibo_paths)} → 값 {fib_vals[step-1]}")
        else:
            st.caption("대각선을 따라가며 피보나치 수가 만들어집니다!")

# -------------------------------
# 일반 시각화 (2ⁿ, 하키스틱)
# -------------------------------
if not show_fibo:
    BOX, GAP = 28, 4
    color_palette = [
        "#A3E4D7", "#AED6F1", "#F9E79F", "#F5B7B1", "#D7BDE2",
        "#FAD7A0", "#ABEBC6", "#D2B4DE", "#F5CBA7", "#A9CCE3",
        "#FDEBD0", "#E8DAEF", "#D6EAF8", "#F6DDCC", "#E8F8F5"
    ]

    html = ["<div style='font-family:monospace; text-align:center;'>"]
    for i, row in enumerate(tri):
        html.append("<div style='display:flex; justify-content:center; align-items:center; margin:1.5px 0;'>")
        html.append(f"<div style='display:flex; justify-content:center; gap:{GAP}px;'>")

        for j, val in enumerate(row):
            color = "#FFFFFF"
            border = "1.2px solid #ccc"

            if show_hockey:
                if (i, j) in diag_cells:
                    color = "#FFF59D"
                if (i, j) == end_cell:
                    color = "#FF7043"

            html.append(
                f"<div style='width:{BOX}px; height:{BOX}px; background:{color}; "
                f"border:{border}; border-radius:6px; display:flex; "
                f"align-items:center; justify-content:center; font-size:13px; font-weight:600;'>{val}</div>"
            )
        html.append("</div>")

        if show_sum:
            s = sum(row)
            html.append(f"<div style='margin-left:10px; color:#6b7280; font-size:13px;'>→ 합 = {s} = 2<sup>{i}</sup></div>")

        html.append("</div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# -------------------------------
# 설명
# -------------------------------
st.markdown("---")
st.subheader("📘 설명")

if show_sum:
    st.write("✅ **2ⁿ 관계:** 각 줄의 수를 모두 더하면 2의 거듭제곱이 돼요.")
if show_hockey:
    picked_vals = [tri[start_col + t][start_col] for t in range(length)]
    end_val = tri[end_cell[0]][end_cell[1]]
    st.write("🏑 **하키스틱 원리:** 열 r부터 대각선으로 더하면 끝 수와 같아요.")
    st.write(f"r={start_col}, 길이={length}")
    st.write(f"계산: {' + '.join(map(str, picked_vals))} = {sum(picked_vals)} → {end_val}")
if show_fibo:
    st.write("🐚 **피보나치 관계 (시각화 ver):** 왼쪽 대각선을 따라가며 각 대각선의 합이 피보나치 수열을 만듭니다.")
    st.write("각 대각선은 색으로 구분되고, 오른쪽 막대그래프는 합산된 값을 보여줍니다.")

# -------------------------------
# 애니메이션 진행
# -------------------------------
if show_fibo and st.session_state.fibo_play:
    if st.session_state.fibo_step < len(fibo_paths):
        st.session_state.fibo_step += 1
        time.sleep(speed)
        st.rerun()
    else:
        st.session_state.fibo_play = False

st.caption("ⓒ 2025 Pascal Visualizer — 통합 완전본 (2ⁿ + 하키스틱 + 피보나치 시각화)")
