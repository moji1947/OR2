import streamlit as st
import pandas as pd
import pulp as pl
from model_logic import solve_logistics 

st.set_page_config(page_title="Logistics DSS - Chonburi Case Study", layout="wide")

# --- ส่วนหัวของเว็บ ---
st.title("🚛 Logistics Decision Support System")
st.caption("ระบบวางแผนเส้นทางขนส่งสินค้ากรณีศึกษาจังหวัดชลบุรี")
st.markdown("---")

# --- โหลดข้อมูลจาก Database ---
try:
    df = pd.read_excel("database.xlsx")
except Exception as e:
    st.error(f"❌ ไม่พบไฟล์ database.xlsx: {e}")
    st.stop()

# --- ส่วนการเลือกวัน ---
col1, col2 = st.columns([1, 2])
with col1:
    st.info("📅 เลือกวันเพื่อวางแผนการจัดส่ง")
    day = st.selectbox("วันจัดส่ง:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    
    # ✂️ Logic กรองกลุ่มลูกค้าตามรายงานวิจัย
    if day in ["Monday", "Wednesday", "Friday"]:
        working_df = df[df['Group'].isin([1, 3])].copy()
    else:
        working_df = df[df['Group'].isin([2, 3])].copy()
    
    working_df = working_df.reset_index(drop=True)

# --- ล็อกค่าข้อจำกัดตามรายงาน ---
t_cap = 20000     # ความจุรถสูงสุด 20 ตัน [cite: 102, 114]
b_lim = 5000      # งบประมาณต่อคัน
d_lim = 400       # ระยะทางสูงสุด
drop_lim = 4      # จำนวนลูกค้าสูงสุดต่อรอบ [cite: 98, 117]
cost_rate = 23.5  # อัตราค่าขนส่งตามที่บริษัทกำหนด [cite: 181]

with col1:
    st.write("---")
    st.markdown("🔍 **เงื่อนไขวันนี้:**")
    st.write(f"- ความจุรถ: {t_cap:,} กก.")
    st.write(f"- จุดแวะสูงสุด: {drop_lim} จุด")
    calculate = st.button("🚀 คำนวณแผนการจัดส่ง", use_container_width=True)

if calculate:
    m, X, Trucks, Customers, Names, W, Dist = solve_logistics(
        working_df, t_cap, b_lim, d_lim, drop_lim, cost_rate
    )

    with col2:
        if pl.LpStatus[m.status] == 'Optimal':
            st.success(f"✅ พบแผนที่เหมาะสมที่สุดสำหรับ {day}")
            res_cols = st.columns(len(Trucks))
            for i in Trucks:
                with res_cols[i]:
                    st.markdown(f"#### 🚛 คันที่ {i+1}")
                    truck_w, truck_d = 0, 0
                    has_del = False
                    for j in Customers:
                        if X[(i,j)].varValue == 1.0:
                            st.write(f"• **{Names[j]}**: {W[j]:,} กก.")
                            truck_w += W[j]
                            truck_d += Dist[j]
                            has_del = True
                    if has_del:
                        st.divider()
                        st.metric("Total Load", f"{truck_w:,} kg")
                        st.metric("Cost", f"{(truck_d * cost_rate):,.2f} B")
        else:
            st.error("❌ ไม่สามารถจัดสรรรถได้ (Infeasible)")

# --- ตารางฉบับมินิมอลด้านล่าง ---
st.markdown("---")
st.markdown("### 📋 รายชื่อลูกค้าที่ต้องส่งวันนี้")

# เลือกเฉพาะคอลัมน์ที่ต้องการและซ่อน Index
minimal_df = working_df[['Customer', 'Weight', 'Distance']]
st.dataframe(
    minimal_df, 
    use_container_width=True, 
    hide_index=True  # 👈 นี่คือคำสั่งซ่อนเลขลำดับด้านซ้ายครับ
)