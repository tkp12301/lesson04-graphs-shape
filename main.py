import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # openDt: 여덟 자리 숫자(YYYYMMDD) -> datetime
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
    )

    # genre: 세로막대(|) 기호로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())

    return df


df = load_data()

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ======================================================================
# 1. 장르별 영화 편수 - 도넛 그래프
# ======================================================================
st.header("1️⃣ 장르별 영화 편수")

genre_counts = df["genre_main"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_donut = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.45,
)
fig_donut.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_donut.update_layout(legend_title_text="장르")

st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것:**")
st.info("")

st.divider()

# ======================================================================
# 2. 장르 안의 영화 - 트리맵 (칸 크기 = 총 관객 수)
# ======================================================================
st.header("2️⃣ 장르 안의 영화별 총 관객 수")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
    root_color="lightgrey",
)
fig_treemap.update_layout(margin=dict(t=30, l=10, r=10, b=10))

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것:**")
st.info("")

st.divider()

# ======================================================================
# 3. 총 관객 수 분포 - 히스토그램
# ======================================================================
st.header("3️⃣ 총 관객 수 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객 수"},
)
fig_hist.update_traces(
    hovertemplate="총 관객 수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>"
)
fig_hist.update_layout(yaxis_title="영화 편수", bargap=0.05)

st.plotly_chart(fig_hist, use_container_width=True)

# 대부분의 영화가 몰려 있는 구간 계산
counts, bin_edges = np.histogram(df["total_audi"].dropna(), bins=30)
peak_idx = counts.argmax()
peak_low, peak_high = bin_edges[peak_idx], bin_edges[peak_idx + 1]

# 총 관객 수가 가장 많은 영화 계산
top_movie = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"👉 대부분의 영화는 총 관객 수 **{peak_low:,.0f}명 ~ {peak_high:,.0f}명** 구간에 가장 많이 몰려 있고, "
    f"총 관객이 가장 많은 영화는 **{top_movie['movieNm']}**"
    f"(약 {top_movie['total_audi']:,.0f}명)입니다."
)

st.markdown("**📌 이 그래프로 알 수 있는 것:**")
st.info("")

st.divider()

# ======================================================================
# 4. 개봉일 스크린수와 총 관객 수의 관계 - 산점도
# ======================================================================
st.header("4️⃣ 개봉일 스크린수 vs 총 관객 수")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_main": "장르",
    },
)
fig_scatter.update_layout(legend_title_text="장르")

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것:**")
st.info("")

st.divider()

# ======================================================================
# 5. 장르별 총 관객 수 분포 - 박스플롯
# ======================================================================
st.header("5️⃣ 장르별 총 관객 수 분포")

fig_box = px.box(
    df,
    x="genre_main",
    y="total_audi",
    color="genre_main",
    points="all",
    hover_name="movieNm",
    labels={"genre_main": "장르", "total_audi": "총 관객 수"},
)
fig_box.update_layout(showlegend=False, xaxis_title="장르", yaxis_title="총 관객 수")

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것:**")
st.info("")
