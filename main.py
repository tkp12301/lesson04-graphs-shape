import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(page_title="영화 데이터 그래프 도감 2", page_icon="🎬", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    # 장르가 '액션|드라마'처럼 여러 개면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미상")
    )
    # 개봉일: 여덟 자리 숫자(예: 20240131) -> 날짜
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")
    return df


def takeaway_box(key: str) -> None:
    """그래프 아래 '이 그래프로 알 수 있는 것' 한 문장 자리."""
    st.markdown("**💡 이 그래프로 알 수 있는 것**")
    st.text_input(
        "한 문장을 적어 주세요",
        key=key,
        placeholder="여기에 그래프에서 읽은 내용을 한 문장으로 적어 보세요.",
        label_visibility="collapsed",
    )


st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("최근 1년간 박스오피스 10위권에 든 영화 중 이 기간에 개봉한 영화의 요약표를 그래프로 살펴봅니다.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

st.write(f"불러온 영화: **{len(df)}편**")
with st.expander("데이터 미리보기"):
    st.dataframe(df.head(20), use_container_width=True)

st.divider()

# ── 구역 1: 장르별 영화 편수 (도넛 그래프) ─────────────────────────
st.header("1. 장르별 영화 편수")

with st.container(border=True):
    genre_counts = df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig = go.Figure(
        go.Pie(
            labels=genre_counts["genre"],
            values=genre_counts["count"],
            hole=0.45,
            sort=True,
            textinfo="label+percent",
            hovertemplate="%{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend_title_text="장르",
        annotations=[
            dict(text=f"총 {len(df)}편", x=0.5, y=0.5, font_size=18, showarrow=False)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    takeaway_box("takeaway_genre")

st.divider()

# ── 구역 8: 10위권 머문 날수와 총 관객 (산점도) ─────────────────────
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가?")

with st.container(border=True):
    scatter_df = df.dropna(subset=["days_in_top10", "total_audi"])

    fig8 = go.Figure(
        go.Scatter(
            x=scatter_df["days_in_top10"],
            y=scatter_df["total_audi"],
            mode="markers",
            marker=dict(size=9, opacity=0.7),
            customdata=scatter_df["movieNm"],
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                "10위권 머문 날수: %{x}일<br>"
                "총 관객: %{y:,}명<extra></extra>"
            ),
        )
    )
    fig8.update_layout(
        xaxis_title="10위권에 머문 날수 (일)",
        yaxis_title="총 관객 (명)",
        margin=dict(t=20, b=20, l=20, r=20),
    )
    st.plotly_chart(fig8, use_container_width=True)

    takeaway_box("takeaway_scatter")

st.divider()
