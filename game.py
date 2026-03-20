import streamlit as st
import random
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="HIT67 - Trang Chủ Chính Thức HIT67", page_icon="🎲")
st.title("🎲 TÀI XỈU 🎲")

st_autorefresh(interval=1000, key="timer")

if "balance" not in st.session_state:
    st.session_state.balance = 10000

if "history" not in st.session_state:
    st.session_state.history = []

if "round_start" not in st.session_state:
    st.session_state.round_start = time.time()

if "bet_choice" not in st.session_state:
    st.session_state.bet_choice = "Tài"

if "bet_amount" not in st.session_state:
    st.session_state.bet_amount = 10

if "rolled" not in st.session_state:
    st.session_state.rolled = False  

ROUND_TIME = 60
elapsed = time.time() - st.session_state.round_start

# Tính toán logic thời gian chuẩn hơn
if elapsed >= ROUND_TIME + 3: # Cho 3 giây để người chơi nhìn kết quả trước khi reset
    st.session_state.round_start = time.time()
    st.session_state.rolled = False
    st.rerun() # Buộc Streamlit cập nhật lại từ đầu giây 60

remaining = int(ROUND_TIME - elapsed)
if remaining < 0: remaining = 0

st.sidebar.metric("💰 Số dư", f"{st.session_state.balance:,.0f} VNĐ")

st.subheader(f"Còn lại: {remaining}s")
st.progress(remaining / 60)

if remaining <= 10:
    st.error(f"⚠️ Khóa cược ⚠️")

st.subheader("Đặt cược")

col1, col2 = st.columns(2)

max_bet = int(st.session_state.balance)

with col1:
    bet = st.number_input(
        "Số tiền cược:",
        min_value=10 if max_bet >= 10 else max_bet,
        max_value=max_bet,
        value=min(st.session_state.bet_amount, max_bet),
        step=10,
        disabled=(remaining <= 0 or max_bet <= 0)
    )


with col2:
    if st.button("🔥 ALL IN 🥶", disabled=(remaining <= 10 or st.session_state.balance <= 0)):
        st.session_state.bet_amount = int(st.session_state.balance)
        st.rerun()  

choice = st.radio(
    "Chọn:",
    ["Tài", "Xỉu"],
    horizontal=True,
    disabled=(remaining <= 10)
)

# Lưu state liên tục để khi autorefresh không bị mất giá trị nhập
st.session_state.bet_amount = bet
st.session_state.bet_choice = choice

# Xử lý Roll Xúc Xắc
if remaining == 0 and not st.session_state.rolled:
    st.session_state.rolled = True 

    # Giả lập lắc
    d1, d2, d3 = [random.randint(1, 6) for _ in range(3)]
    total = d1 + d2 + d3
    result = "Tài" if total > 10 else "Xỉu"

    bet_val = st.session_state.bet_amount
    choice_val = st.session_state.bet_choice

    if bet_val > 0 and bet_val <= st.session_state.balance:
        if choice_val == result:
            profit = bet_val * 0.99
            st.session_state.balance += profit
        else:
            profit = -bet_val
            st.session_state.balance -= bet_val
    else:
        profit = 0

    st.session_state.history.append({
        "dice": (d1, d2, d3),
        "total": total,
        "result": result,
        "bet": bet_val,
        "profit": profit
    })

# Hiển thị kết quả ván vừa xong (nếu đã rolled)
if st.session_state.rolled and st.session_state.history:
    h = st.session_state.history[-1]
    st.info(f"🎲 Kết quả: {h['dice']} | Tổng: {h['total']} -> {h['result'].upper()}")
    if h['profit'] > 0:
        st.success("🎉 BẠN THẮNG!")
    elif h['profit'] < 0:
        st.error("💀 BẠN THUA 💀")

st.subheader("Lịch sử")
if st.session_state.history:
    # Hiển thị 10 ván gần nhất
    recent_history = list(reversed(st.session_state.history))[:10]
    for i, h in enumerate(recent_history):
        color = "⚪" if h["bet"] == 0 else ("🟢" if h["profit"] > 0 else "🔴")
        st.write(
            f"{color} Ván: {h['dice']} | Tổng {h['total']} → {h['result']} | "
            f"Cược {h['bet']} | {'+' if h['profit']>0 else ''}{h['profit']:.0f}"
        )
else:
    st.info("Chưa có lượt chơi nào.")

if st.session_state.balance <= 0:
    st.warning("Bạn đã hết tiền!")
