import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    import gspread
from google.oauth2.service_account import Credentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(info, scopes=SCOPE)
client = gspread.authorize(creds)

SHEET_ID = "1KhHhAInhJGV3NO0YDZjgg86O_0KbBl5aRuXfVIpsfkU"
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

    df = df.rename(columns={
        'ID': 'id',
        'Full Name': 'name',
        'Sex (M/F)': 'gender',
        'Father ID': 'father_id',
        'Date of Birth': 'birth',
        'Date of Death': 'death'
    })
    return df

data = load_data()

# Build descendant tree
def get_descendants(df, person_id, generations):
    tree = {0: [person_id]}
    for gen in range(1, generations + 1):
        if gen - 1 not in tree:
            break
        current_gen = []
        for parent_id in tree[gen - 1]:
            children = df[df['father_id'] == parent_id]['id'].tolist()
            current_gen.extend(children)
        if current_gen:
            tree[gen] = current_gen
        else:
            break
    return tree

# Build ancestor tree
def get_ancestors(df, person_id, generations):
    tree = {0: [person_id]}
    for gen in range(1, generations + 1):
        if gen - 1 not in tree:
            break
        current_gen = []
        for child_id in tree[gen - 1]:
            father_id = df[df['id'] == child_id]['father_id'].values[0] if not df[df['id'] == child_id].empty else None
            if pd.notna(father_id):
                current_gen.append(father_id)
        if current_gen:
            tree[gen] = current_gen
        else:
            break
    return tree

# Merge ancestors and descendants
def merge_trees(ancestors, descendants):
    tree = {}
    max_ancestor_depth = max(ancestors.keys(), default=-1)
    for depth, ids in ancestors.items():
        tree[-depth] = ids
    for depth, ids in descendants.items():
        tree[depth] = ids
    return tree

# Prepare sunburst data
def prepare_sunburst_data(df, tree):
    labels, parents, ids, genders, hover_texts = [], [], [], [], []
    id_to_info = df.set_index('id').to_dict('index')
    all_ids = set()
    sorted_depths = sorted(tree.keys())
    for depth in sorted_depths:
        for node in tree[depth]:
            if node in all_ids:
                continue
            all_ids.add(node)
            info = id_to_info.get(node, {})
            name = info.get('name', "غير معروف")
            gender = info.get('gender', "M")
            birth = info.get('birth', "")
            death = info.get('death', "")

            birth_year = pd.to_datetime(birth, errors='coerce').year if pd.notna(birth) and birth != "" else ""
            death_year = pd.to_datetime(death, errors='coerce').year if pd.notna(death) and death != "" else ""

            label_parts = [
                f"<span style='color:black'><b>{name}</b></span>",
                f"<span style='color:blue'>{node}</span>"
            ]
            if birth_year:
                label_parts.append(f"<span style='color:green'>{birth_year}</span>")
            if death_year:
                label_parts.append(f"<span style='color:red'>{death_year}</span>")

            label = " ".join(label_parts)

            labels.append(label)
            ids.append(str(node))
            genders.append(gender)

            hover = f"<b>{name}</b><br>ID: {node}"

            father_id = info.get('father_id', "")
            if pd.notna(father_id) and str(father_id).strip() != "":
                hover += f"<br>Father ID: {int(father_id)}"

            if birth_year:
                hover += f"<br>{birth_year}"
            if death_year:
                hover += f"<br>{death_year}"

            extra_cols = [col for col in df.columns if col not in ['id', 'name', 'gender', 'father_id', 'birth', 'death']]
            for col in extra_cols:
                value = info.get(col, "")
                if pd.notna(value) and str(value).strip() != "":
                    hover += f"<br>{value}"

            hover_texts.append(hover)

            parent_found = False
            for prev_depth in sorted_depths:
                if prev_depth >= depth:
                    break
                for possible_parent in tree[prev_depth]:
                    children = df[df['father_id'] == possible_parent]['id'].tolist()
                    if node in children:
                        parents.append(str(possible_parent))
                        parent_found = True
                        break
                if parent_found:
                    break

            if not parent_found:
                parents.append("")

    return ids, labels, parents, genders, hover_texts

# Generate sunburst chart
def draw_sunburst(df, tree, male_color, female_color, zoom_factor):
    ids, labels, parents, genders, hover_texts = prepare_sunburst_data(df, tree)
    colors = [male_color if g == 'M' else female_color for g in genders]

    base_size = 18
    dynamic_font_size = min(26, max(10, int(base_size * zoom_factor)))

    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        marker=dict(colors=colors, line=dict(width=1.5, color='gray')),
        branchvalues="total",
        hoverinfo="text",
        hovertext=hover_texts,
        insidetextorientation='auto',
        textinfo="label",
        textfont=dict(size=dynamic_font_size, family="Arial Black"),
    ))

    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        font=dict(size=dynamic_font_size, family="Arial Black"),
        paper_bgcolor='white',
        sunburstcolorway=[male_color, female_color],
        height=int(800 * zoom_factor),
        width=int(800 * zoom_factor)
    )
    return fig

# UI
st.title("🌸 شجرة العائلة بأسلوب Sunburst")

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 1.0

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("➖", key="zoom_out"):
        st.session_state["zoom"] = max(st.session_state["zoom"] - 0.1, 0.2)

with col2:
    st.markdown(f"<h5 style='text-align: center;'>🔍 <b>{st.session_state.get('zoom', 1.0) * 100:.0f}%</b></h5>", unsafe_allow_html=True)

with col3:
    if st.button("➕", key="zoom_in"):
        st.session_state["zoom"] = min(st.session_state["zoom"] + 0.1, 3.0)

zoom_factor = st.session_state["zoom"]

with st.sidebar:
    st.header("🔍 البحث")
    options = [f"[{row['id']}] {row['name']}" for _, row in data.iterrows()]
    selected = st.selectbox("اختر شخصًا بالاسم أو رقم المعرف", options)
    person_id = int(selected.split(']')[0][1:])
    person_row = data[data['id'] == person_id].iloc[0]
    st.markdown(f"**الشخص المحدد:** {person_row['name']} (ID: {person_id})")

    tree_type = st.radio("نوع الشجرة:", ["الأنسال (الأبناء)", "الأسلاف (الآباء)", "الكل (أسلاف + أنسال)"])

    generations = st.slider("عدد الأجيال", 1, 10, 3)

    with st.expander("🎨 تخصيص المظهر", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            male_color = st.color_picker("🎨 لون الذكور", "#b3e0ff")
        with c2:
            female_color = st.color_picker("🎨 لون الإناث", "#fce4ec")

if tree_type == "الأنسال (الأبناء)":
    tree = get_descendants(data, person_id, generations)
elif tree_type == "الأسلاف (الآباء)":
    tree = get_ancestors(data, person_id, generations)
else:
    ancestors = get_ancestors(data, person_id, generations)
    descendants = get_descendants(data, person_id, generations)
    tree = merge_trees(ancestors, descendants)

fig = draw_sunburst(data, tree, male_color, female_color, zoom_factor)
st.plotly_chart(fig, use_container_width=True)

buf = io.BytesIO()
fig.write_image(buf, format='png')
st.download_button("🗵 تحميل بصيغة PNG", data=buf.getvalue(), file_name="family_sunburst.png", mime="image/png")

buf_pdf = io.BytesIO()
fig.write_image(buf_pdf, format='pdf')
st.download_button("📄 تحميل بصيغة PDF", data=buf_pdf.getvalue(), file_name="family_sunburst.pdf", mime="application/pdf")

buf_svg = io.BytesIO()
fig.write_image(buf_svg, format='svg')
st.download_button("🔼️ تحميل بصيغة SVG", data=buf_svg.getvalue(), file_name="family_sunburst.svg", mime="image/svg+xml")
