import streamlit as st
import pandas as pd
import io
import json

# --- পেজ কনফিগারেশন ---
st.set_page_config(page_title="Data Collector", page_icon="🚀", layout="centered")

# --- কাস্টম ডিজাইন ---
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }

    /* টাইটেল স্টাইল */
    .title-text { 
        color: #2ecc71 !important; 
        text-align: center; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 30px; 
        font-weight: bold; 
        text-shadow: 0 0 10px rgba(46, 204, 113, 0.5);
        margin-bottom: 20px;
    }

    /* আপলোডার লেবেল স্টাইল */
    .upload-label {
        color: #ffffff !important; 
        font-weight: 900 !important;
        font-size: 16px !important;
        margin-bottom: 10px;
        display: block;
        letter-spacing: 1px;
    }

    /* বাটন গুলোর জন্য গ্লোবাল স্টাইল */
    .stButton>button, [data-testid="stDownloadButton"] button { 
        width: 100% !important; 
        border-radius: 12px !important; 
        font-weight: 900 !important; 
        font-size: 15px !important;
        background-color: #2ecc71 !important; 
        color: #ffffff !important; 
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        height: 48px !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-8px); }
        50% { transform: translateX(8px); }
        75% { transform: translateX(-8px); }
        100% { transform: translateX(0); }
    }

    div[data-testid="stFileUploader"] section { 
        background-color: #161b22 !important; 
        border: 2px dashed #2ecc71 !important; 
        border-radius: 15px !important;
    }
    
    div[data-testid="stFileUploader"] section:hover {
        animation: shake 0.4s ease-in-out !important;
        border-color: #ffffff !important;
    }

    div[data-testid="stFileUploader"] button {
        background-color: #2ecc71 !important; 
        color: #000000 !important; 
        font-weight: 900 !important;
    }

    .stTextInput>div>div>input {
        background-color: #161b22 !important;
        color: #2ecc71 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='title-text'>Excel Data Collector</div>", unsafe_allow_html=True)

if 'final_df' not in st.session_state:
    st.session_state.final_df = pd.DataFrame()
if 'file_count' not in st.session_state:
    st.session_state.file_count = 0

def format_code(code):
    code = str(code)
    return f"{code[:4]}...{code[-4:]}" if len(code) > 10 else code

st.markdown('<span class="upload-label">📁 DRAG OR SELECT CSV, XLSX, XLS FILES</span>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True)
st.markdown('<p style="text-align: center; margin-top: -15px; color: #2ecc71; font-weight: 900;">CSV, XLSX, XLS</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 START COLLECTING"):
        if uploaded_files:
            all_new_data = []
            new_file_count = 0
            for f in uploaded_files:
                try:
                    df = pd.read_csv(f, on_bad_lines='skip') if f.name.endswith('.csv') else pd.read_excel(f)
                    if not df.empty:
                        all_new_data.append(df)
                        new_file_count += 1
                except: continue
            
            if all_new_data:
                st.session_state.final_df = pd.concat(all_new_data, axis=0, ignore_index=True, sort=False)
                st.session_state.file_count = new_file_count
                st.toast(f"✅ {st.session_state.file_count} Files Collected!", icon='🔥')
        else:
            st.error("⚠️ Boss, Please Select Files First!")

with col2:
    if st.button("🧹 CLEAR ALL"):
        st.session_state.final_df = pd.DataFrame()
        st.session_state.file_count = 0
        st.rerun()

if not st.session_state.final_df.empty:
    total_rows = len(st.session_state.final_df)
    st.markdown(f"""
        <p style='color: #2ecc71; font-weight: 900; font-size: 16px; text-align: center; text-transform: uppercase;'>
            📂 Total File: {st.session_state.file_count}  ||  📊 Total Date: {total_rows}
        </p>
    """, unsafe_allow_html=True)
    
    df_display = st.session_state.final_df.copy()
    if '2FCode' in df_display.columns:
        df_display['2FCode'] = df_display['2FCode'].apply(format_code)
    
    st.dataframe(df_display, use_container_width=True, height=400)

    # --- ফিক্সড কপি বাটন লজিক ---
    copy_data_tsv = st.session_state.final_df.to_csv(index=False, sep='\t')
    # JSON dump ব্যবহার করা হয়েছে যাতে নিউ-লাইন ও স্পেশাল ক্যারেক্টার নিরাপদ থাকে
    safe_data = json.dumps(copy_data_tsv)

    st.components.v1.html(f"""
        <div style="text-align:center;">
            <button id="copyBtn" onclick="copyToClipboard()" style="
                width: 100%; height: 50px; background-color: #238636; 
                color: #ffffff; border: none; border-radius: 12px; 
                font-weight: 900; cursor: pointer; font-size: 15px; text-transform: uppercase;
                transition: all 0.3s;
            " onmouseover="this.style.transform='scale(1.01)';"
               onmouseout="this.style.transform='scale(1)';">
                📋 CLICK TO COPY ALL DATA
            </button>
        </div>
        <script>
            function copyToClipboard() {{
                const data = {safe_data};
                const el = document.createElement('textarea');
                el.value = data;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                
                const btn = document.getElementById('copyBtn');
                btn.innerText = "✨ ALL DATA COPIED SUCCESS!";
                btn.style.backgroundColor = "#ffffff"; 
                btn.style.color = "#0d1117";
                setTimeout(() => {{
                    btn.innerText = "📋 CLICK TO COPY ALL DATA";
                    btn.style.backgroundColor = "#238636"; 
                    btn.style.color = "#ffffff";
                }}, 2000);
            }}
        </script>
    """, height=70)

    st.markdown("<hr style='border: 0.5px solid #30363d;'>", unsafe_allow_html=True)
    new_filename = st.text_input("📝 Rename Your File:", placeholder="e.g. nayem", key="rename_input")
    final_name = f"{new_filename if new_filename else 'Collected_Accounts'}_({total_rows} pcs).xlsx"

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.final_df.to_excel(writer, index=False)
    
    st.download_button(
        label=f"📥 DOWNLOAD AS {final_name.upper()}",
        data=output.getvalue(),
        file_name=final_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.markdown("<div style='text-align: center; color: #8b949e; font-weight: 900; text-transform: uppercase;'>Ready to work, Boss!</div>", unsafe_allow_html=True)