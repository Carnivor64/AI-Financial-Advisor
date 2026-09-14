import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit_authenticator as stauth

# إعدادات الصفحة والواجهة
st.set_page_config(page_title="AI Financial Advisor", layout="wide")

# 1. إعداد حسابات المستخدمين وإدارة الذاكرة
if 'credentials' not in st.session_state:
    names = ["Ahmed Ali", "Sarah Mohamed"]
    usernames = ["ahmed123", "sarah_investor"]
    passwords = ["12345", "stock_pass"]
    emails = ["ahmed@example.com", "sarah@example.com"]
    
    hashed_passwords = stauth.Hasher(passwords).generate()
    
    credentials = {"usernames": {}}
    for i in range(len(usernames)):
        credentials["usernames"][usernames[i]] = {
            "name": names[i],
            "password": hashed_passwords[i],
            "email": emails[i]
        }
    st.session_state.credentials = credentials

# 2. إنشاء نموذج المصادقة ونظام تسجيل الدخول
authenticator = stauth.Authenticate(
    st.session_state.credentials,
    cookie_name="portfolio_ai_cookie",
    key="ai_advisor_secret_key",
    cookie_expiry_days=30
)

# واجهة اختيار اللغة المبدئية في شاشة الدخول
selected_lang_name = st.sidebar.selectbox("اختر اللغة / Select Language", ["العربية", "English"])

# قاموس المصطلحات والترجمة الكامل
LANG_DICT = {
    "العربية": {
        "welcome": "👋 مرحباً بك مجدداً، {name}",
        "logout": "تسجيل الخروج 🚪",
        "title": "🎯 مستشارك المالي الذكي & مدير المحفظة الآمن",
        "subtitle": "تحليل الأسهم الفني والأساسي والأخبار + إدارة المحفظة الاستثمارية",
        "select_market": "اختر البورصة المستهدفة",
        "enter_ticker": "أدخل رمز السهم (مثال: AAPL, COMI.CA, HIEM.L)",
        "btn_analyze": "ابدأ التحليل الذكي 🚀",
        "loading": "جاري سحب البيانات وتحليل السهم ماليًا وفنيًا...",
        "error_fetch": "❌ خطأ: لم نتمكن من جلب بيانات هذا الرمز. تأكد من الصيغة الصحيحة وجودة اللاحقة الجغرافية الجيدة مثل .L أو .CA.",
        "basic_info": "📊 بيانات السهم الأساسية",
        "price": "السعر الحالي",
        "market_cap": "القيمة السوقية",
        "pe": "مكرر الربحية (P/E)",
        "analysis_res": "🔍 نتائج الفحص والمشاعر",
        "tech_trend": "الاتجاه الفني",
        "fund_val": "التقييم المالي الأساسي",
        "news_sentiment": "مشاعر الأخبار الحالية",
        "final_rec": "🎯 التوصية النهائية الفورية",
        "reason": "السبب الاستراتيجي",
        "buy": "✅ شراء (Buy)",
        "sell": "🚨 بيع / تجنب (Sell)",
        "hold": "⏳ احتفاظ / مراقبة (Hold)",
        "disclaimer": "⚠️ تنويه: هذا التحليل آلي بالكامل بناءً على خوارزميات رياضية وليس نصيحة استثمارية حتمية.",
        "sent_pos": "إيجابية ومتفائلة 👍",
        "sent_neg": "سلبية وحذرة 👎",
        "sent_neu": "محايدة ومستقرة ⚖️",
        "chart_title": "📈 الرسم البياني التفاعلي لحركة السعر (6 أشهر)",
        "portfolio_section": "💼 إدارة محفظتك الاستثمارية المشفرة",
        "add_to_port": "أضف هذا السهم إلى محفظتك الخاصة",
        "buy_price": "سعر الشراء للسهم",
        "shares_count": "عدد الأسهم المملوكة",
        "btn_save_port": "حفظ السهم في المحفظة 💾",
        "port_status": "📊 وضع محفظتك الحالي:",
        "ticker": "الرمز",
        "qty": "الكمية",
        "avg_cost": "متوسط التكلفة",
        "current_val": "القيمة الحالية",
        "pnl": "الربح / الخسارة",
        "port_empty": "محفظتك فارغة حالياً. ابحث عن سهم وأضفه لبدء التتبع الآمن.",
        "security_tab": "🔐 إدارة الأمان وكلمة المرور",
        "forgot_pass": "هل نسيت كلمة المرور؟ 🔑",
        "change_pass": "تغيير كلمة المرور الحالية 🛠️"
    },
    "English": {
        "welcome": "👋 Welcome back, {name}",
        "logout": "Log Out 🚪",
        "title": "🎯 Secure AI Financial Advisor & Portfolio Manager",
        "subtitle": "Technical, Fundamental & Sentiment Stock Analysis + Secured Portfolio Tracking",
        "select_market": "Select Target Market",
        "enter_ticker": "Enter Stock Ticker (e.g., AAPL, COMI.CA, HIEM.L)",
        "btn_analyze": "Start Smart Analysis 🚀",
        "loading": "Fetching data, analyzing technicals, fundamentals, and news...",
        "error_fetch": "❌ Error: Could not fetch data for this ticker. Please check the symbol and geographic extension (e.g., .L or .CA).",
        "basic_info": "📊 Stock Basic Data",
        "price": "Current Price",
        "market_cap": "Market Cap",
        "pe": "P/E Ratio",
        "analysis_res": "🔍 Deep Inspection & Sentiment",
        "tech_trend": "Technical Trend",
        "fund_val": "Fundamental Valuation",
        "news_sentiment": "Current News Sentiment",
        "final_rec": "🎯 Immediate Recommendation",
        "reason": "Strategic Reason",
        "buy": "✅ Buy",
        "sell": "🚨 Sell / Avoid",
        "hold": "⏳ Hold / Watch",
        "disclaimer": "⚠️ Disclaimer: This analysis is fully automated based on algorithms and is not financial advice.",
        "sent_pos": "Positive & Bullish 👍",
        "sent_neg": "Negative & Bearish 👎",
        "sent_neu": "Neutral & Stable ⚖️",
        "chart_title": "📈 Interactive Price Chart (6 Months)",
        "portfolio_section": "💼 Secured Portfolio Management",
        "add_to_port": "Add this stock to your private portfolio",
        "buy_price": "Purchase Price per Share",
        "shares_count": "Number of Shares Owned",
        "btn_save_port": "Save Stock to Portfolio 💾",
        "port_status": "📊 Your Current Portfolio Status:",
        "ticker": "Ticker",
        "qty": "Quantity",
        "avg_cost": "Avg Cost",
        "current_val": "Current Value",
        "pnl": "Profit / Loss",
        "port_empty": "Your portfolio is currently empty. Analyze and add a stock to track it securely.",
        "security_tab": "🔐 Security & Password Settings",
        "forgot_pass": "Forgot Password? 🔑",
        "change_pass": "Change Current Password 🛠️"
    }
}
ln = LANG_DICT[selected_lang_name]

if selected_lang_name == "العربية":
    st.markdown('<style>body, div, p, h1, h2, h3 {text-align: right; direction: rtl;}</style>', unsafe_allow_html=True)

# عرض شاشة تسجيل الدخول
name, authentication_status, username = authenticator.login("main")

if authentication_status == False:
    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة / Incorrect Credentials")
    
    with st.expander(ln["forgot_pass"]):
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
            if username_of_forgotten_password:
                st.success(f"✅ تم إصدار كلمة مرور مؤقتة جديدة: {new_random_password}")
        except Exception as e:
            st.error(str(e))

elif authentication_status == None:
    st.warning("🔒 يرجى تسجيل الدخول للوصول إلى مستشارك المالي ومحفظتك الاستثمارية")
    
    with st.expander(ln["forgot_pass"]):
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
            if username_of_forgotten_password:
                st.success(f"✅ Temporary password created: {new_random_password}")
        except Exception as e:
            st.error(str(e))

# 3. في حال نجاح تسجيل الدخول
elif authentication_status:
    
    if f'portfolio_{username}' not in st.session_state:
        st.session_state[f'portfolio_{username}'] = {}

    st.sidebar.write(ln["welcome"].format(name=name))
    authenticator.logout(ln["logout"], "sidebar")
    
    with st.sidebar.expander(ln["security_tab"]):
        try:
            if authenticator.reset_password(username):
                st.success('✅ تم تغيير كلمة المرور بنجاح / Password reset successfully')
        except Exception as e:
            st.error(str(e))

    st.title(ln["title"])
    st.subheader(ln["subtitle"])
    st.markdown("---")

    main_col, port_col = st.columns(2)

    with main_col:
        market = st.selectbox(ln["select_market"], ["US البورصة الأمريكية", "EGX البورصة المصرية (.CA)", "LSE بورصة لندن (.L)"])
        ticker_input = st.text_input(ln["enter_ticker"], value="AAPL").strip().upper()

        if st.button(ln["btn_analyze"]):
            with st.spinner(ln["loading"]):
                try:
                    stock = yf.Ticker(ticker_input)
                    df = stock.history(period="6mo")
                    
                    if df.empty:
                        st.error(ln["error_fetch"])
                    else:
                        df['SMA_20'] = df['Close'].rolling(window=20).mean()
                        df['SMA_50'] = df['Close'].rolling(window=50).mean()
                        
                        current_price = df['Close'].iloc[-1]
                        sma_20 = df['SMA_20'].iloc[-1]
                        sma_50 = df['SMA_50'].iloc[-1]
                        
                        info = stock.info
                        pe_ratio = info.get('trailingPE', None)
                        market_cap = info.get('marketCap', 0)
                        currency = info.get('currency', 'USD')
                        
                        news = stock.news
                        pos_words = ['growth', 'profit', 'dividend', 'surge', 'up', 'أرباح', 'نمو', 'صعود']
                        neg_words = ['loss', 'drop', 'decline', 'fall', 'debt', 'خسائر', 'تراجع', 'هبوط']
                        score = 0
                        if news:
                            for item in news[:5]:
                                title_text = item.get('title', '').lower()
                                for pw in pos_words:
                                    if pw in title_text: score += 1
                                for nw in neg_words:
                                    if nw in title_text: score -= 1
                        
                        sentiment_res = ln["sent_pos"] if score > 0 else (ln["sent_neg"] if score < 0 else ln["sent_neu"])

                        tech_signal = "صعودي" if current_price > sma_20 > sma_50 else ("هبوطي" if current_price < sma_20 < sma_50 else "عرضي")
                        
