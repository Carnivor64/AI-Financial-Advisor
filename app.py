# -*- coding: utf-8 -*-
"""
AI Stock & Fund Advisor
========================
تطبيق Streamlit لتحليل الأسهم والصناديق (فنياً + مالياً + معنويات الأخبار)
وإصدار توصية آلية (شراء / بيع / احتفاظ) لأسواق:
  - البورصة الأمريكية (بدون لاحقة، مثل: AAPL)
  - البورصة المصرية EGX  (لاحقة .CA، مثل: COMI.CA)
  - بورصة لندن LSE       (لاحقة .L،  مثل: HSBA.L)

تشغيل التطبيق:
    pip install streamlit yfinance pandas numpy plotly requests
    streamlit run ai_stock_fund_advisor.py

تنويه: هذا التطبيق أداة تحليل آلية تعليمية وليس نصيحة استثمارية.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

st.set_page_config(page_title="AI Stock & Fund Advisor", page_icon="📊", layout="wide")

# =====================================================================
# 1) الترجمة (عربي / إنجليزي)
# =====================================================================
LANG_DICT = {
    "العربية": {
        "title": "📊 المستشار المالي الذكي للأسهم والصناديق",
        "subtitle": "تحليل فني ومالي وأخبار آلي + توصية فورية (شراء / بيع / احتفاظ)",
        "select_market": "اختر السوق",
        "market_us": "🇺🇸 البورصة الأمريكية",
        "market_egx": "🇪🇬 البورصة المصرية (.CA)",
        "market_lse": "🇬🇧 بورصة لندن (.L)",
        "enter_ticker": "أدخل رمز السهم أو الصندوق",
        "ticker_help": "أمثلة: AAPL أو MSFT (أمريكية) — COMI أو HRHO (مصرية) — HSBA أو VOD (لندن)",
        "btn_analyze": "ابدأ التحليل الذكي 🚀",
        "loading": "جاري سحب البيانات وتحليلها فنياً ومالياً وإخبارياً...",
        "error_fetch": "❌ تعذر جلب بيانات هذا الرمز. تأكد من صحة الرمز والسوق المختار، أو حاول مرة أخرى بعد قليل.",
        "warn_empty_ticker": "⚠️ من فضلك أدخل رمز السهم أولاً.",
        "asset_type_equity": "سهم شركة",
        "asset_type_fund": "صندوق استثماري / ETF",
        "asset_type_other": "أداة مالية",
        "basic_info": "📌 البيانات الأساسية",
        "price": "السعر الحالي",
        "day_change": "التغير اليومي",
        "market_cap": "القيمة السوقية",
        "currency": "العملة",
        "chart_title": "📈 حركة السعر والمؤشرات الفنية (6 أشهر)",
        "price_panel": "السعر والمتوسطات المتحركة",
        "rsi_panel": "مؤشر القوة النسبية RSI",
        "macd_panel": "مؤشر MACD",
        "fund_section": "💰 التحليل المالي الأساسي (القوائم المالية)",
        "pe": "مكرر الربحية P/E",
        "pb": "مكرر القيمة الدفترية P/B",
        "roe": "العائد على حقوق الملكية ROE",
        "net_margin": "هامش صافي الربح",
        "debt_equity": "نسبة الدين إلى حقوق الملكية",
        "current_ratio": "نسبة السيولة الحالية",
        "revenue_growth": "نمو الإيرادات (سنوي)",
        "dividend_yield": "عائد التوزيعات",
        "fund_not_available": "⚠️ لا تتوفر بيانات قوائم مالية تفصيلية لهذه الأداة (شائع في الصناديق وETFs)، سيعتمد التحليل بشكل أكبر على الجانب الفني والأخبار.",
        "news_section": "📰 تحليل مشاعر الأخبار الحديثة",
        "no_news": "لا توجد أخبار حديثة متاحة لهذا الرمز حالياً.",
        "sent_pos": "إيجابية 👍",
        "sent_neg": "سلبية 👎",
        "sent_neu": "محايدة ⚖️",
        "final_rec": "🎯 التوصية النهائية",
        "confidence": "درجة الثقة في التوصية",
        "score_breakdown": "🔍 تفاصيل التقييم (فني / مالي / أخبار)",
        "reasons_title": "الأسباب الرئيسية للتوصية:",
        "buy": "✅ شراء (Buy)",
        "sell": "🚨 بيع / تجنب (Sell)",
        "hold": "⏳ احتفاظ / مراقبة (Hold)",
        "conf_high": "مرتفعة",
        "conf_medium": "متوسطة",
        "conf_low": "منخفضة",
        "tech_axis": "الدرجة الفنية",
        "fund_axis": "الدرجة المالية",
        "news_axis": "درجة الأخبار",
        "final_axis": "الدرجة الإجمالية",
        "disclaimer": "⚠️ تنويه هام: هذا التحليل مولَّد بالكامل بواسطة خوارزميات رياضية آلية اعتماداً على بيانات علنية، وليس توصية استثمارية أو نصيحة مالية مُلزمة. استشر مستشاراً مالياً مرخصاً قبل اتخاذ أي قرار استثماري.",
    },
    "English": {
        "title": "📊 AI Financial Advisor for Stocks & Funds",
        "subtitle": "Automated Technical, Fundamental & News-Sentiment Analysis + Instant Recommendation",
        "select_market": "Select Market",
        "market_us": "🇺🇸 US Market",
        "market_egx": "🇪🇬 Egyptian Exchange EGX (.CA)",
        "market_lse": "🇬🇧 London Stock Exchange (.L)",
        "enter_ticker": "Enter Ticker Symbol",
        "ticker_help": "Examples: AAPL or MSFT (US) — COMI or HRHO (Egypt) — HSBA or VOD (London)",
        "btn_analyze": "Start Smart Analysis 🚀",
        "loading": "Fetching data and running technical, fundamental & news analysis...",
        "error_fetch": "❌ Could not fetch data for this ticker. Check the symbol/market, or try again shortly.",
        "warn_empty_ticker": "⚠️ Please enter a ticker symbol first.",
        "asset_type_equity": "Company Stock",
        "asset_type_fund": "Fund / ETF",
        "asset_type_other": "Financial Instrument",
        "basic_info": "📌 Basic Data",
        "price": "Current Price",
        "day_change": "Day Change",
        "market_cap": "Market Cap",
        "currency": "Currency",
        "chart_title": "📈 Price Action & Technical Indicators (6 Months)",
        "price_panel": "Price & Moving Averages",
        "rsi_panel": "RSI Indicator",
        "macd_panel": "MACD Indicator",
        "fund_section": "💰 Fundamental Analysis (Financial Statements)",
        "pe": "P/E Ratio",
        "pb": "P/B Ratio",
        "roe": "Return on Equity (ROE)",
        "net_margin": "Net Profit Margin",
        "debt_equity": "Debt / Equity Ratio",
        "current_ratio": "Current Ratio",
        "revenue_growth": "Revenue Growth (YoY)",
        "dividend_yield": "Dividend Yield",
        "fund_not_available": "⚠️ Detailed financial statement data isn't available for this instrument (common for funds/ETFs). Analysis will rely more on technicals and news.",
        "news_section": "📰 Recent News Sentiment Analysis",
        "no_news": "No recent news available for this ticker.",
        "sent_pos": "Positive 👍",
        "sent_neg": "Negative 👎",
        "sent_neu": "Neutral ⚖️",
        "final_rec": "🎯 Final Recommendation",
        "confidence": "Recommendation Confidence",
        "score_breakdown": "🔍 Score Breakdown (Technical / Fundamental / News)",
        "reasons_title": "Key reasons behind this recommendation:",
        "buy": "✅ Buy",
        "sell": "🚨 Sell / Avoid",
        "hold": "⏳ Hold / Watch",
        "conf_high": "High",
        "conf_medium": "Medium",
        "conf_low": "Low",
        "tech_axis": "Technical Score",
        "fund_axis": "Fundamental Score",
        "news_axis": "News Score",
        "final_axis": "Overall Score",
        "disclaimer": "⚠️ Important: This analysis is fully automated based on public data and mathematical scoring. It is NOT financial advice. Consult a licensed financial advisor before making investment decisions.",
    },
}

# =====================================================================
# 2) شبكة الاتصال الآمنة
# =====================================================================
@st.cache_resource
def create_secure_session():
    session = requests.Session()
    retry = Retry(total=3, connect=3, backoff_factor=0.5,
                   status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def normalize_ticker(raw_ticker: str, market_key: str) -> str:
    """يضيف اللاحقة المناسبة للسوق المختار إن لم تكن موجودة بالفعل."""
    ticker = raw_ticker.strip().upper()
    suffix_map = {"market_egx": ".CA", "market_lse": ".L", "market_us": ""}
    suffix = suffix_map.get(market_key, "")
    if suffix and not ticker.endswith(suffix):
        # تجنب لاحقة مزدوجة لو المستخدم كتبها بالفعل
        if not (ticker.endswith(".CA") or ticker.endswith(".L")):
            ticker = f"{ticker}{suffix}"
    return ticker


# =====================================================================
# 3) المؤشرات الفنية
# =====================================================================
def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calculate_macd(close: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SMA_20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["SMA_200"] = df["Close"].rolling(window=200, min_periods=1).mean()
    df["RSI_14"] = calculate_rsi(df["Close"])
    macd_line, signal_line, hist = calculate_macd(df["Close"])
    df["MACD"] = macd_line
    df["MACD_SIGNAL"] = signal_line
    df["MACD_HIST"] = hist
    return df


def score_technicals(df: pd.DataFrame) -> dict:
    """يرجع درجة فنية من -100 إلى 100 مع أسباب."""
    last = df.iloc[-1]
    price, sma20, sma50, sma200 = last["Close"], last["SMA_20"], last["SMA_50"], last["SMA_200"]
    rsi, macd, macd_signal = last["RSI_14"], last["MACD"], last["MACD_SIGNAL"]

    contributions = []  # (weight, score -100..100, reason_key)

    if price > sma20 > sma50:
        contributions.append((1.0, 100, "trend_up"))
    elif price < sma20 < sma50:
        contributions.append((1.0, -100, "trend_down"))
    else:
        contributions.append((1.0, 0, "trend_sideways"))

    if len(df) >= 200 and not np.isnan(sma200):
        if sma50 > sma200:
            contributions.append((0.6, 60, "golden_cross"))
        else:
            contributions.append((0.6, -60, "death_cross"))

    if rsi < 30:
        contributions.append((0.7, 70, "rsi_oversold"))
    elif rsi > 70:
        contributions.append((0.7, -70, "rsi_overbought"))
    else:
        contributions.append((0.7, 0, "rsi_neutral"))

    if macd > macd_signal:
        contributions.append((0.5, 50, "macd_bullish"))
    else:
        contributions.append((0.5, -50, "macd_bearish"))

    total_weight = sum(w for w, _, _ in contributions)
    final_score = sum(w * s for w, s, _ in contributions) / total_weight if total_weight else 0
    reasons = [key for _, _, key in contributions]
    return {"score": round(final_score, 1), "reasons": reasons,
            "rsi": round(rsi, 1), "price": price, "sma20": sma20, "sma50": sma50, "sma200": sma200}


# =====================================================================
# 4) التحليل المالي الأساسي (من القوائم المالية)
# =====================================================================
def get_row_series(df: pd.DataFrame, possible_names):
    if df is None or df.empty:
        return None
    for name in possible_names:
        if name in df.index:
            row = df.loc[name].dropna()
            if not row.empty:
                return row
    return None


def compute_fundamentals(stock: yf.Ticker, info: dict) -> dict:
    ratios = {
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "market_cap": info.get("marketCap"),
        "currency": info.get("currency", "USD"),
        "roe": None, "net_margin": None, "debt_equity": None,
        "current_ratio": None, "revenue_growth": None,
    }

    try:
        income = stock.financials
        balance = stock.balance_sheet
    except Exception:
        income, balance = None, None

    revenue_row = get_row_series(income, ["Total Revenue", "TotalRevenue"])
    net_income_row = get_row_series(income, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
    equity_row = get_row_series(balance, ["Total Stockholder Equity", "Stockholders Equity",
                                           "Total Equity Gross Minority Interest"])
    liab_row = get_row_series(balance, ["Total Liab", "Total Liabilities Net Minority Interest",
                                         "Total Liabilities"])
    curr_assets_row = get_row_series(balance, ["Total Current Assets", "Current Assets"])
    curr_liab_row = get_row_series(balance, ["Total Current Liabilities", "Current Liabilities"])

    if revenue_row is not None and net_income_row is not None:
        try:
            ratios["net_margin"] = float(net_income_row.iloc[0]) / float(revenue_row.iloc[0]) * 100
        except (ZeroDivisionError, IndexError):
            pass

    if revenue_row is not None and len(revenue_row) >= 2:
        try:
            prev, curr = float(revenue_row.iloc[1]), float(revenue_row.iloc[0])
            if prev != 0:
                ratios["revenue_growth"] = (curr - prev) / abs(prev) * 100
        except IndexError:
            pass

    if net_income_row is not None and equity_row is not None:
        try:
            equity_val = float(equity_row.iloc[0])
            if equity_val:
                ratios["roe"] = float(net_income_row.iloc[0]) / equity_val * 100
        except (ZeroDivisionError, IndexError):
            pass

    if liab_row is not None and equity_row is not None:
        try:
            equity_val = float(equity_row.iloc[0])
            if equity_val:
                ratios["debt_equity"] = float(liab_row.iloc[0]) / equity_val
        except (ZeroDivisionError, IndexError):
            pass

    if curr_assets_row is not None and curr_liab_row is not None:
        try:
            liab_val = float(curr_liab_row.iloc[0])
            if liab_val:
                ratios["current_ratio"] = float(curr_assets_row.iloc[0]) / liab_val
        except (ZeroDivisionError, IndexError):
            pass

    return ratios


def score_fundamentals(ratios: dict, is_fund: bool) -> dict:
    if is_fund:
        return {"score": 0, "reasons": [], "usable": False}

    contributions = []

    pe = ratios.get("pe_ratio")
    if pe is not None and not np.isnan(pe):
        if pe < 0:
            contributions.append((1.0, -80, "pe_negative"))
        elif pe < 15:
            contributions.append((1.0, 80, "pe_cheap"))
        elif pe <= 25:
            contributions.append((1.0, 0, "pe_fair"))
        else:
            contributions.append((1.0, -60, "pe_expensive"))

    roe = ratios.get("roe")
    if roe is not None:
        if roe > 15:
            contributions.append((0.8, 80, "roe_strong"))
        elif roe > 5:
            contributions.append((0.8, 20, "roe_ok"))
        else:
            contributions.append((0.8, -60, "roe_weak"))

    de = ratios.get("debt_equity")
    if de is not None:
        if de < 0.5:
            contributions.append((0.6, 60, "debt_low"))
        elif de <= 1.5:
            contributions.append((0.6, 0, "debt_moderate"))
        else:
            contributions.append((0.6, -70, "debt_high"))

    margin = ratios.get("net_margin")
    if margin is not None:
        if margin > 15:
            contributions.append((0.6, 60, "margin_strong"))
        elif margin >= 0:
            contributions.append((0.6, 10, "margin_thin"))
        else:
            contributions.append((0.6, -80, "margin_negative"))

    growth = ratios.get("revenue_growth")
    if growth is not None:
        if growth > 10:
            contributions.append((0.5, 60, "growth_strong"))
        elif growth >= 0:
            contributions.append((0.5, 10, "growth_slow"))
        else:
            contributions.append((0.5, -60, "growth_negative"))

    if not contributions:
        return {"score": 0, "reasons": [], "usable": False}

    total_weight = sum(w for w, _, _ in contributions)
    final_score = sum(w * s for w, s, _ in contributions) / total_weight
    reasons = [key for _, _, key in contributions]
    return {"score": round(final_score, 1), "reasons": reasons, "usable": True}


# =====================================================================
# 5) تحليل مشاعر الأخبار
# =====================================================================
POS_WORDS = ["growth", "profit", "profits", "surge", "soar", "beat", "upgrade", "bullish",
             "record", "rally", "gain", "expansion", "dividend increase",
             "أرباح", "نمو", "صعود", "ارتفاع", "توسع", "تفوق", "قفزة", "مكاسب"]
NEG_WORDS = ["loss", "losses", "drop", "decline", "fall", "downgrade", "bearish", "lawsuit",
             "fraud", "debt crisis", "recall", "layoff", "cut", "miss", "plunge",
             "خسائر", "تراجع", "هبوط", "انخفاض", "أزمة", "ديون", "دعوى قضائية", "تسريح"]


def extract_news_title(item: dict) -> str:
    if item.get("title"):
        return item["title"]
    content = item.get("content")
    if isinstance(content, dict):
        return content.get("title", "") or ""
    return ""


def extract_news_link(item: dict) -> str:
    if item.get("link"):
        return item["link"]
    content = item.get("content")
    if isinstance(content, dict):
        url_field = content.get("clickThroughUrl") or content.get("canonicalUrl")
        if isinstance(url_field, dict):
            return url_field.get("url", "") or ""
    return ""


def analyze_news_sentiment(news_list) -> dict:
    if not news_list:
        return {"score": 0, "headlines": [], "usable": False}

    headlines = []
    total = 0
    for item in news_list[:8]:
        title = extract_news_title(item)
        if not title:
            continue
        link = extract_news_link(item)
        title_lower = title.lower()
        item_score = 0
        for w in POS_WORDS:
            if w in title_lower:
                item_score += 1
        for w in NEG_WORDS:
            if w in title_lower:
                item_score -= 1
        total += item_score
        tag = "pos" if item_score > 0 else ("neg" if item_score < 0 else "neu")
        headlines.append({"title": title, "link": link, "tag": tag})

    if not headlines:
        return {"score": 0, "headlines": [], "usable": False}

    # تطبيع الدرجة إلى مدى -100..100
    normalized = max(-100, min(100, total * 25))
    return {"score": normalized, "headlines": headlines, "usable": True}


# =====================================================================
# 6) التوصية النهائية
# =====================================================================
def compute_final_recommendation(tech_result, fund_result, news_result, is_fund: bool) -> dict:
    if is_fund or not fund_result.get("usable"):
        weights = {"tech": 0.65, "fund": 0.05, "news": 0.30}
    else:
        weights = {"tech": 0.40, "fund": 0.40, "news": 0.20}

    tech_score = tech_result["score"]
    fund_score = fund_result["score"] if fund_result.get("usable") else 0
    news_score = news_result["score"] if news_result.get("usable") else 0

    final_score = (tech_score * weights["tech"] +
                   fund_score * weights["fund"] +
                   news_score * weights["news"])
    final_score = round(final_score, 1)

    if final_score >= 25:
        action = "buy"
    elif final_score <= -25:
        action = "sell"
    else:
        action = "hold"

    abs_score = abs(final_score)
    if abs_score >= 55:
        confidence = "high"
    elif abs_score >= 25:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "action": action, "confidence": confidence, "final_score": final_score,
        "tech_score": tech_score, "fund_score": fund_score, "news_score": news_score,
        "weights": weights,
    }


REASON_TEXT = {
    "trend_up": {"العربية": "السعر أعلى من المتوسطين المتحركين 20 و50 يوم (اتجاه صاعد).",
                 "English": "Price is above SMA20 & SMA50 (uptrend)."},
    "trend_down": {"العربية": "السعر أقل من المتوسطين المتحركين 20 و50 يوم (اتجاه هابط).",
                   "English": "Price is below SMA20 & SMA50 (downtrend)."},
    "trend_sideways": {"العربية": "لا يوجد اتجاه فني واضح حالياً (تذبذب).",
                        "English": "No clear technical trend (sideways)."},
    "golden_cross": {"العربية": "المتوسط 50 يوم أعلى من المتوسط 200 يوم (إشارة صعودية متوسطة المدى).",
                      "English": "SMA50 above SMA200 (medium-term bullish signal)."},
    "death_cross": {"العربية": "المتوسط 50 يوم أقل من المتوسط 200 يوم (إشارة هبوطية متوسطة المدى).",
                     "English": "SMA50 below SMA200 (medium-term bearish signal)."},
    "rsi_oversold": {"العربية": "مؤشر RSI في منطقة التشبع البيعي (فرصة ارتداد محتملة).",
                      "English": "RSI is in oversold territory (potential bounce)."},
    "rsi_overbought": {"العربية": "مؤشر RSI في منطقة التشبع الشرائي (خطر تصحيح).",
                        "English": "RSI is in overbought territory (pullback risk)."},
    "rsi_neutral": {"العربية": "مؤشر RSI في منطقة محايدة.", "English": "RSI is in a neutral zone."},
    "macd_bullish": {"العربية": "مؤشر MACD يعطي إشارة شرائية (فوق خط الإشارة).",
                      "English": "MACD is above its signal line (bullish)."},
    "macd_bearish": {"العربية": "مؤشر MACD يعطي إشارة بيعية (تحت خط الإشارة).",
                      "English": "MACD is below its signal line (bearish)."},
    "pe_cheap": {"العربية": "مكرر الربحية منخفض نسبياً (السهم قد يكون رخيصاً).",
                 "English": "Low P/E ratio (stock may be undervalued)."},
    "pe_fair": {"العربية": "مكرر الربحية في نطاق معقول.", "English": "P/E ratio is in a reasonable range."},
    "pe_expensive": {"العربية": "مكرر الربحية مرتفع (السهم قد يكون مبالغاً في تقييمه).",
                      "English": "High P/E ratio (stock may be overvalued)."},
    "pe_negative": {"العربية": "مكرر الربحية سالب (الشركة تحقق خسائر حالياً).",
                     "English": "Negative P/E (company is currently loss-making)."},
    "roe_strong": {"العربية": "عائد قوي على حقوق الملكية (ROE > 15%).",
                   "English": "Strong return on equity (ROE > 15%)."},
    "roe_ok": {"العربية": "عائد مقبول على حقوق الملكية.", "English": "Acceptable return on equity."},
    "roe_weak": {"العربية": "عائد ضعيف على حقوق الملكية.", "English": "Weak return on equity."},
    "debt_low": {"العربية": "مستوى دين منخفض مقارنة بحقوق الملكية.",
                 "English": "Low debt relative to equity."},
    "debt_moderate": {"العربية": "مستوى دين معتدل.", "English": "Moderate debt level."},
    "debt_high": {"العربية": "مستوى دين مرتفع (مخاطرة مالية أعلى).",
                  "English": "High debt level (higher financial risk)."},
    "margin_strong": {"العربية": "هامش ربح صافٍ قوي.", "English": "Strong net profit margin."},
    "margin_thin": {"العربية": "هامش ربح صافٍ ضعيف نسبياً.", "English": "Relatively thin net margin."},
    "margin_negative": {"العربية": "هامش ربح صافٍ سالب (الشركة خاسرة).",
                         "English": "Negative net margin (company is losing money)."},
    "growth_strong": {"العربية": "نمو قوي في الإيرادات مقارنة بالعام السابق.",
                       "English": "Strong year-over-year revenue growth."},
    "growth_slow": {"العربية": "نمو إيرادات بطيء.", "English": "Slow revenue growth."},
    "growth_negative": {"العربية": "تراجع في الإيرادات مقارنة بالعام السابق.",
                         "English": "Revenue declined year-over-year."},
}

# =====================================================================
# 7) تشغيل التحليل الكامل
# =====================================================================
@st.cache_data(ttl=300, show_spinner=False)
def run_full_analysis(ticker: str):
    session = create_secure_session()
    stock = yf.Ticker(ticker, session=session)

    df = stock.history(period="6mo")
    if df is None or df.empty or len(df) < 5:
        return None

    df = add_technical_indicators(df)

    try:
        info = stock.info or {}
    except Exception:
        info = {}

    quote_type = str(info.get("quoteType", "")).upper()
    is_fund = quote_type in ("ETF", "MUTUALFUND", "INDEX")

    tech_result = score_technicals(df)
    ratios = compute_fundamentals(stock, info)
    fund_result = score_fundamentals(ratios, is_fund)

    try:
        news_list = stock.news
    except Exception:
        news_list = []
    news_result = analyze_news_sentiment(news_list)

    recommendation = compute_final_recommendation(tech_result, fund_result, news_result, is_fund)

    return {
        "df": df, "info": info, "quote_type": quote_type, "is_fund": is_fund,
        "tech": tech_result, "ratios": ratios, "fund": fund_result,
        "news": news_result, "recommendation": recommendation,
    }


# =====================================================================
# 8) واجهة المستخدم
# =====================================================================
with st.sidebar:
    selected_lang_name = st.selectbox("اللغة / Language", ["العربية", "English"])

ln = LANG_DICT[selected_lang_name]

if selected_lang_name == "العربية":
    st.markdown(
        "<style>.block-container {direction: rtl; text-align: right;}</style>",
        unsafe_allow_html=True,
    )

st.title(ln["title"])
st.caption(ln["subtitle"])
st.markdown("---")

with st.sidebar:
    market_key = st.radio(
        ln["select_market"],
        options=["market_us", "market_egx", "market_lse"],
        format_func=lambda k: ln[k],
    )
    raw_ticker = st.text_input(ln["enter_ticker"], value="AAPL", help=ln["ticker_help"])
    analyze_clicked = st.button(ln["btn_analyze"], type="primary", use_container_width=True)

if analyze_clicked:
    if not raw_ticker.strip():
        st.warning(ln["warn_empty_ticker"])
    else:
        final_ticker = normalize_ticker(raw_ticker, market_key)
        with st.spinner(ln["loading"]):
            result = run_full_analysis(final_ticker)

        if result is None:
            st.error(ln["error_fetch"])
        else:
            df = result["df"]
            info = result["info"]
            tech = result["tech"]
            ratios = result["ratios"]
            fund = result["fund"]
            news = result["news"]
            rec = result["recommendation"]
            currency = ratios.get("currency", "USD")

            asset_label = (ln["asset_type_fund"] if result["is_fund"]
                            else ln["asset_type_equity"] if result["quote_type"] == "EQUITY"
                            else ln["asset_type_other"])
            st.subheader(f"{final_ticker} — {info.get('shortName', '')} · {asset_label}")

            # ---------- بيانات أساسية ----------
            last_close = df["Close"].iloc[-1]
            prev_close = df["Close"].iloc[-2] if len(df) > 1 else last_close
            day_change_pct = ((last_close - prev_close) / prev_close * 100) if prev_close else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(ln["price"], f"{last_close:,.2f} {currency}")
            c2.metric(ln["day_change"], f"{day_change_pct:+.2f}%")
            mcap = ratios.get("market_cap")
            c3.metric(ln["market_cap"], f"{mcap:,.0f}" if mcap else "—")
            c4.metric(ln["currency"], currency)

            # ---------- الرسم الفني ----------
            st.markdown(f"### {ln['chart_title']}")

            rec_marker_color = {"buy": "#1e8e3e", "sell": "#d93025", "hold": "#f29900"}[rec["action"]]
            rec_marker_symbol = {"buy": "triangle-up", "sell": "triangle-down", "hold": "circle"}[rec["action"]]

            fig = make_subplots(
                rows=3, cols=1, shared_xaxes=True,
                vertical_spacing=0.04, row_heights=[0.55, 0.2, 0.25],
                subplot_titles=(ln["price_panel"], ln["rsi_panel"], ln["macd_panel"]),
            )

            # --- لوحة السعر: الشموع + المتوسطات ---
            fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                name=final_ticker, showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20",
                                      line=dict(width=1.3)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50",
                                      line=dict(width=1.3)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], name="SMA 200",
                                      line=dict(width=1.3, dash="dot")), row=1, col=1)

            # --- علامة التوصية على آخر نقطة سعر (تربط الرسم بالتوصية النهائية) ---
            last_x = df.index[-1]
            last_y = df["High"].iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_x], y=[last_y * 1.02], mode="markers+text",
                marker=dict(symbol=rec_marker_symbol, size=16, color=rec_marker_color,
                            line=dict(width=1, color="white")),
                text=[ln[rec["action"]]], textposition="top center",
                textfont=dict(color=rec_marker_color, size=12),
                name=ln[rec["action"]], showlegend=False,
            ), row=1, col=1)

            # --- لوحة RSI مع تظليل مناطق التشبع ---
            fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.06, line_width=0, row=2, col=1)
            fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.06, line_width=0, row=2, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], name="RSI 14",
                                      line=dict(color="#8e44ad")), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            # --- لوحة MACD ---
            fig.add_trace(go.Bar(x=df.index, y=df["MACD_HIST"], name="Histogram",
                                  marker_color="gray", opacity=0.5), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                                      line=dict(color="#2980b9")), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="Signal",
                                      line=dict(color="#e67e22")), row=3, col=1)

            fig.update_layout(
                height=780, xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", y=1.06),
                margin=dict(t=70, b=20),
                title=dict(
                    text=f"{final_ticker} · {ln[rec['action']]} · {ln['final_axis']}: {rec['final_score']:+.1f}",
                    font=dict(size=15, color=rec_marker_color), x=0.01,
                ),
            )
            fig.update_yaxes(title_text=currency, row=1, col=1)
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
            fig.update_yaxes(title_text="MACD", row=3, col=1)
            st.plotly_chart(fig, use_container_width=True)

            # ---------- التحليل المالي الأساسي ----------
            st.markdown(f"### {ln['fund_section']}")
            if not fund.get("usable"):
                st.info(ln["fund_not_available"])
            else:
                fcols = st.columns(4)
                def fmt_pct(v): return f"{v:.2f}%" if v is not None else "—"
                def fmt_num(v): return f"{v:.2f}" if v is not None else "—"

                fcols[0].metric(ln["pe"], fmt_num(ratios.get("pe_ratio")))
                fcols[1].metric(ln["pb"], fmt_num(ratios.get("pb_ratio")))
                fcols[2].metric(ln["roe"], fmt_pct(ratios.get("roe")))
                fcols[3].metric(ln["net_margin"], fmt_pct(ratios.get("net_margin")))

                fcols2 = st.columns(4)
                fcols2[0].metric(ln["debt_equity"], fmt_num(ratios.get("debt_equity")))
                fcols2[1].metric(ln["current_ratio"], fmt_num(ratios.get("current_ratio")))
                fcols2[2].metric(ln["revenue_growth"], fmt_pct(ratios.get("revenue_growth")))
                dy = ratios.get("dividend_yield")
                fcols2[3].metric(ln["dividend_yield"], fmt_pct(dy * 100) if dy else "—")

            # ---------- الأخبار ----------
            st.markdown(f"### {ln['news_section']}")
            if not news.get("usable"):
                st.info(ln["no_news"])
            else:
                tag_label = {"pos": ln["sent_pos"], "neg": ln["sent_neg"], "neu": ln["sent_neu"]}
                tag_color = {"pos": "green", "neg": "red", "neu": "gray"}
                for item in news["headlines"]:
                    color = tag_color[item["tag"]]
                    label = tag_label[item["tag"]]
                    if item["link"]:
                        st.markdown(f"- :{color}[{label}] — [{item['title']}]({item['link']})")
                    else:
                        st.markdown(f"- :{color}[{label}] — {item['title']}")

            # ---------- التوصية النهائية ----------
            st.markdown("---")
            st.markdown(f"## {ln['final_rec']}")

            action_style = {
                "buy": ("buy", "green"), "sell": ("sell", "red"), "hold": ("hold", "orange"),
            }
            action_key, color = action_style[rec["action"]]
            conf_key = f"conf_{rec['confidence']}"

            rc1, rc2 = st.columns([2, 1])
            with rc1:
                st.markdown(f"### :{color}[{ln[action_key]}]")
                st.write(f"**{ln['confidence']}:** {ln[conf_key]}")
                st.write(f"**{ln['final_axis']}:** {rec['final_score']:+.1f} / 100")
            with rc2:
                st.metric(ln["tech_axis"], f"{rec['tech_score']:+.1f}")
                if fund.get("usable"):
                    st.metric(ln["fund_axis"], f"{rec['fund_score']:+.1f}")
                if news.get("usable"):
                    st.metric(ln["news_axis"], f"{rec['news_score']:+.1f}")

            st.markdown(f"**{ln['reasons_title']}**")
            all_reason_keys = tech["reasons"] + (fund["reasons"] if fund.get("usable") else [])
            for key in all_reason_keys:
                text = REASON_TEXT.get(key, {}).get(selected_lang_name, key)
                st.markdown(f"- {text}")

st.markdown("---")
st.caption(ln["disclaimer"])
