"""自定义 CSS 样式 - Linear/Vercel 风格 + 21st.dev 灵感
"""
import streamlit as st

def apply_custom_styles():
    """应用 Linear/Vercel 风格的现代 CSS 样式 + 炫酷动画效果"""
    st.markdown("""
        <style>
        /* 引入 Inter 字体 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            /* Linear/Vercel 深色主题配色 - 增强版 */
            --bg-primary: #050505;
            --bg-secondary: #0a0a0a;
            --bg-tertiary: #111111;
            --bg-elevated: #161616;
            --bg-hover: #1a1a1a;
            
            --border-subtle: rgba(255, 255, 255, 0.06);
            --border-default: rgba(255, 255, 255, 0.1);
            --border-hover: rgba(255, 255, 255, 0.18);
            
            --text-primary: #fafafa;
            --text-secondary: #a1a1a1;
            --text-tertiary: #666666;
            
            /* 更丰富的渐变色 */
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-tertiary: #d946ef;
            --accent-hover: #818cf8;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            
            /* 霓虹色彩 */
            --neon-green: #00ff88;
            
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #3b82f6;
            
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-xl: 20px;
            --radius-2xl: 24px;
            
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.5);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.6);
            --shadow-glow: 0 0 60px rgba(99, 102, 241, 0.2);
            
            /* 动画时间 */
            --transition-fast: 0.15s;
            --transition-normal: 0.25s;
        }

        /* 全局基础样式 */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .stApp {
            background: var(--bg-primary);
            background-image:
                radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.12), transparent),
                radial-gradient(ellipse 60% 40% at 100% 100%, rgba(139, 92, 246, 0.08), transparent);
            color: var(--text-primary);
            min-height: 100vh;
        }

        /* 主内容区域 */
        .main .block-container {
            padding: 1.5rem 2rem;
            max-width: 1600px;
        }

        /* ================= Hero Section - 增强版 ================= */
        .hero-section {
            position: relative;
            padding: 4rem 2rem 3rem;
            margin-bottom: 2rem;
            text-align: center;
            overflow: hidden;
            border-radius: var(--radius-2xl);
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            border: 1px solid var(--border-subtle);
            backdrop-filter: blur(20px);
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            left: 50%;
            transform: translateX(-50%);
            width: 800px;
            height: 600px;
            background:
                radial-gradient(ellipse at center, rgba(99, 102, 241, 0.2) 0%, transparent 50%),
                radial-gradient(ellipse at 30% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
                radial-gradient(ellipse at 70% 30%, rgba(217, 70, 239, 0.1) 0%, transparent 40%);
            pointer-events: none;
            animation: heroGlow 8s ease-in-out infinite alternate;
        }

        .hero-section::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-primary), var(--accent-secondary), var(--accent-tertiary), transparent);
            opacity: 0.5;
        }

        @keyframes heroGlow {
            0% { transform: translateX(-50%) scale(1); opacity: 0.8; }
            100% { transform: translateX(-50%) scale(1.1); opacity: 1; }
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--accent-primary);
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            animation: badgePulse 3s ease-in-out infinite;
        }

        @keyframes badgePulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.2); }
            50% { box-shadow: 0 0 20px 5px rgba(99, 102, 241, 0.1); }
        }

        .hero-badge .dot {
            width: 8px;
            height: 8px;
            background: var(--neon-green);
            border-radius: 50%;
            animation: dotPulse 2s infinite;
            box-shadow: 0 0 10px var(--neon-green);
        }

        @keyframes dotPulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.9); }
        }

        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            line-height: 1.05;
            margin-bottom: 1.25rem;
            color: var(--text-primary);
            text-shadow: 0 0 80px rgba(99, 102, 241, 0.3);
        }

        .gradient-text {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 5s ease infinite;
            background-size: 200% 200%;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .hero-subtitle {
            font-size: 1.2rem;
            color: var(--text-secondary);
            max-width: 650px;
            margin: 0 auto 2rem;
            line-height: 1.7;
            font-weight: 400;
        }

        .hero-features {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .hero-feature {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-subtle);
            border-radius: 100px;
            transition: all var(--transition-normal) ease;
        }

        .hero-feature:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: var(--border-default);
            transform: translateY(-2px);
        }

        .hero-feature svg {
            color: var(--accent-secondary);
            filter: drop-shadow(0 0 4px var(--accent-secondary));
        }

        /* ================= 卡片样式 - 玻璃态增强 ================= */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.25rem;
            transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            opacity: 0;
            transition: opacity var(--transition-normal) ease;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: var(--border-hover);
            box-shadow: var(--shadow-lg), var(--shadow-glow);
            transform: translateY(-2px);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover::before {
            opacity: 1;
        }

        /* Expander - 增强版 */
        div[data-testid="stExpander"] {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.6) 0%, rgba(10, 10, 10, 0.8) 100%);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }

        div[data-testid="stExpander"]:hover {
            border-color: var(--border-default);
        }

        div[data-testid="stExpander"] summary {
            color: var(--text-primary);
            font-weight: 500;
            padding: 1rem 1.25rem;
        }

        div[data-testid="stExpander"] summary:hover {
            background: rgba(255, 255, 255, 0.02);
        }

        /* ================= Metric Card - Shimmer 效果 ================= */
        .metric-card {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.25rem;
            transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
            transition: left 0.6s ease;
        }

        .metric-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg), var(--shadow-glow);
        }

        .metric-card:hover::before {
            left: 100%;
        }

        .metric-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }

        .metric-delta {
            display: inline-flex;
            align-items: center;
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.5rem;
            padding: 2px 8px;
            border-radius: 4px;
        }

        .delta-positive { background: rgba(16, 185, 129, 0.15); color: var(--success); }
        .delta-negative { background: rgba(239, 68, 68, 0.15); color: var(--error); }
        .delta-neutral { background: var(--bg-tertiary); color: var(--text-tertiary); }

        /* 隐藏原生 Metric */
        div[data-testid="stMetric"] {
            background: transparent !important;
            border: none !important;
        }
        div[data-testid="stMetric"] label { color: var(--text-tertiary) !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }

        /* ================= 按钮 - Shimmer 效果 ================= */
        .stButton button {
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-elevated) 100%);
            color: var(--text-primary);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            padding: 0.625rem 1.25rem;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .stButton button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s ease;
        }

        .stButton button:hover {
            background: linear-gradient(135deg, var(--bg-hover) 0%, var(--bg-tertiary) 100%);
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .stButton button:hover::before {
            left: 100%;
        }

        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            border: none;
            color: white;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .stButton button[kind="primary"]:hover {
            background: linear-gradient(135deg, var(--accent-hover) 0%, var(--accent-primary) 100%);
            box-shadow: 0 6px 25px rgba(99, 102, 241, 0.4), var(--shadow-glow);
            transform: translateY(-2px);
        }

        .stButton button[kind="primary"]:active {
            transform: translateY(0);
        }

        /* ================= Tabs - 发光效果 ================= */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%);
            padding: 6px;
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-subtle);
            backdrop-filter: blur(10px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            background: transparent;
            border-radius: var(--radius-lg);
            border: none;
            color: var(--text-tertiary);
            font-weight: 500;
            font-size: 0.875rem;
            padding: 0 1.5rem;
            transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.03);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.15), inset 0 1px 0 rgba(255,255,255,0.05);
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
        }

        /* Tab 下划线隐藏 */
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }

        /* Tab 内容区域 */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1.5rem;
        }

        /* ================= 输入框 - 发光聚焦 ================= */
        .stTextInput input, .stTextArea textarea {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%) !important;
            border: 1px solid var(--border-default) !important;
            border-radius: var(--radius-lg) !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem;
            padding: 0.75rem 1rem !important;
            transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15), 0 0 20px rgba(99, 102, 241, 0.1) !important;
            background: linear-gradient(135deg, rgba(22, 22, 22, 0.9) 0%, rgba(17, 17, 17, 1) 100%) !important;
        }

        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: var(--text-tertiary) !important;
        }

        /* Select - 增强版 */
        .stSelectbox div[data-baseweb="select"] {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%);
            border-color: var(--border-default);
            border-radius: var(--radius-lg);
            transition: all var(--transition-normal) ease;
        }

        .stSelectbox div[data-baseweb="select"]:hover {
            border-color: var(--border-hover);
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
        }

        .stSelectbox div[data-baseweb="select"]:focus-within {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }

        /* ================= 侧边栏 ================= */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            border-right: 1px solid var(--border-subtle);
        }

        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-secondary);
        }

        /* ================= Divider ================= */
        hr {
            border-color: var(--border-subtle);
            margin: 2rem 0;
        }

        /* ================= 文件上传 - 增强版 ================= */
        .stFileUploader {
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.6) 0%, rgba(10, 10, 10, 0.8) 100%);
            border: 2px dashed var(--border-default);
            border-radius: var(--radius-xl);
            transition: all var(--transition-normal) ease;
            position: relative;
            overflow: hidden;
        }

        .stFileUploader::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            opacity: 0;
            transition: opacity var(--transition-normal) ease;
            pointer-events: none;
        }

        .stFileUploader:hover {
            border-color: var(--accent-primary);
            background: linear-gradient(135deg, rgba(22, 22, 22, 0.8) 0%, rgba(17, 17, 17, 0.9) 100%);
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.1);
        }

        .stFileUploader:hover::before {
            opacity: 1;
        }

        /* ================= DataFrame ================= */
        .stDataFrame {
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            overflow: hidden;
        }

        /* ================= 进度条 ================= */
        .stProgress > div > div {
            background: var(--accent-gradient);
            border-radius: 100px;
        }

        /* ================= 消息提示 - 增强版 ================= */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: var(--radius-lg);
            border: none;
            backdrop-filter: blur(10px);
        }

        .stSuccess {
            background: rgba(16, 185, 129, 0.1);
            border-left: 3px solid var(--success);
        }

        .stInfo {
            background: rgba(59, 130, 246, 0.1);
            border-left: 3px solid var(--info);
        }

        .stWarning {
            background: rgba(245, 158, 11, 0.1);
            border-left: 3px solid var(--warning);
        }

        .stError {
            background: rgba(239, 68, 68, 0.1);
            border-left: 3px solid var(--error);
        }

        /* ================= 隐藏默认元素 ================= */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        footer { display: none; }

        #MainMenu { visibility: hidden; }

        /* ================= 滚动条 ================= */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--bg-hover);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--border-hover);
        }

        /* ================= 标题样式 ================= */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        p, span, label {
            color: var(--text-secondary);
        }

        /* ================= Chat 样式 ================= */
        .stChatMessage {
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
        }

        .stChatInputContainer {
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-lg);
        }

        /* ================= 滚动球体加载动画 ================= */
        .loader {
            --ballcolor: #f2f2f2;
            --shadow: 0px 0 #ffffff00;
            --shadowcolor: #ffffff00;
            width: 10px;
            height: 10px;
            left: -120px;
            border-radius: 50%;
            position: relative;
            color: var(--ballcolor);
            animation: shadowRolling 2s linear infinite;
        }

        @keyframes shadowRolling {
            0% {
                box-shadow: var(--shadow),
                    var(--shadow),
                    var(--shadow),
                    var(--shadow);
            }

            12% {
                box-shadow: 100px 0 var(--ballcolor),
                    var(--shadow),
                    var(--shadow),
                    var(--shadow);
            }

            25% {
                box-shadow: 110px 0 var(--ballcolor),
                    100px 0 var(--ballcolor),
                    var(--shadow),
                    var(--shadow);
            }

            36% {
                box-shadow: 120px 0 var(--ballcolor),
                    110px 0 var(--ballcolor),
                    100px 0 var(--ballcolor),
                    var(--shadow);
            }

            50% {
                box-shadow: 130px 0 var(--ballcolor),
                    120px 0 var(--ballcolor),
                    110px 0 var(--ballcolor),
                    100px 0 var(--ballcolor);
            }

            62% {
                box-shadow: 200px 0 var(--shadowcolor),
                    130px 0 var(--ballcolor),
                    120px 0 var(--ballcolor),
                    110px 0 var(--ballcolor);
            }

            75% {
                box-shadow: 200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor),
                    130px 0 var(--ballcolor),
                    120px 0 var(--ballcolor);
            }

            87% {
                box-shadow: 200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor),
                    130px 0 var(--ballcolor);
            }

            100% {
                box-shadow: 200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor),
                    200px 0 var(--shadowcolor);
            }
        }

        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            min-height: 100px;
        }

        .loading-text {
            margin-top: 2rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
        }

        /* ================= 炫酷按钮样式 1 - 发光效果 ================= */
        .fancy-button {
            --black-700: hsla(0 0% 12% / 1);
            --border_radius: 9999px;
            --transtion: 0.3s ease-in-out;
            --offset: 2px;

            cursor: pointer;
            position: relative;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transform-origin: center;
            padding: 1rem 2rem;
            background-color: transparent;
            border: none;
            border-radius: var(--border_radius);
            transform: scale(calc(1 + (var(--active, 0) * 0.1)));
            transition: transform var(--transtion);
        }

        .fancy-button::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 100%;
            background-color: var(--black-700);
            border-radius: var(--border_radius);
            box-shadow: inset 0 0.5px hsl(0, 0%, 100%), inset 0 -1px 2px 0 hsl(0, 0%, 0%),
                0px 4px 10px -4px hsla(0 0% 0% / calc(1 - var(--active, 0))),
                0 0 0 calc(var(--active, 0) * 0.375rem) hsl(260 97% 50% / 0.75);
            transition: all var(--transtion);
            z-index: 0;
        }

        .fancy-button::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 100%;
            background-color: hsla(260 97% 61% / 0.75);
            background-image: radial-gradient(
                    at 51% 89%,
                    hsla(266, 45%, 74%, 1) 0px,
                    transparent 50%
                ),
                radial-gradient(at 100% 100%, hsla(266, 36%, 60%, 1) 0px, transparent 50%),
                radial-gradient(at 22% 91%, hsla(266, 36%, 60%, 1) 0px, transparent 50%);
            background-position: top;
            opacity: var(--active, 0);
            border-radius: var(--border_radius);
            transition: opacity var(--transtion);
            z-index: 2;
        }

        .fancy-button:is(:hover, :focus-visible) {
            --active: 1;
        }

        .fancy-button:active {
            transform: scale(1);
        }

        .fancy-button .dots_border {
            --size_border: calc(100% + 2px);
            overflow: hidden;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: var(--size_border);
            height: var(--size_border);
            background-color: transparent;
            border-radius: var(--border_radius);
            z-index: -10;
        }

        .fancy-button .dots_border::before {
            content: "";
            position: absolute;
            top: 30%;
            left: 50%;
            transform: translate(-50%, -50%);
            transform-origin: left;
            transform: rotate(0deg);
            width: 100%;
            height: 2rem;
            background-color: white;
            mask: linear-gradient(transparent 0%, white 120%);
            animation: rotate 2s linear infinite;
        }

        .fancy-button .sparkle {
            position: relative;
            z-index: 10;
            width: 1.75rem;
        }

        .fancy-button .sparkle .path {
            fill: currentColor;
            stroke: currentColor;
            transform-origin: center;
            color: hsl(0, 0%, 100%);
        }

        .fancy-button:is(:hover, :focus) .sparkle .path {
            animation: path 1.5s linear 0.5s infinite;
        }

        .fancy-button .sparkle .path:nth-child(1) {
            --scale_path_1: 1.2;
        }
        .fancy-button .sparkle .path:nth-child(2) {
            --scale_path_2: 1.2;
        }
        .fancy-button .sparkle .path:nth-child(3) {
            --scale_path_3: 1.2;
        }

        @keyframes path {
            0%, 34%, 71%, 100% {
                transform: scale(1);
            }
            17% {
                transform: scale(var(--scale_path_1, 1));
            }
            49% {
                transform: scale(var(--scale_path_2, 1));
            }
            83% {
                transform: scale(var(--scale_path_3, 1));
            }
        }

        .fancy-button .text_button {
            position: relative;
            z-index: 10;
            background-image: linear-gradient(
                90deg,
                hsla(0 0% 100% / 1) 0%,
                hsla(0 0% 100% / var(--active, 0)) 120%
            );
            background-clip: text;
            font-size: 1rem;
            color: transparent;
        }

        /* ================= 炫酷按钮样式 2 - 文字描边动画 ================= */
        .stroke-button {
            margin: 0;
            height: auto;
            background: transparent;
            padding: 0.8rem 1.5rem;
            border: none;
            cursor: pointer;
            --border-right: 4px;
            --text-stroke-color: rgba(255,255,255,0.6);
            --animation-color: #37FF8B;
            --fs-size: 1rem;
            letter-spacing: 2px;
            text-decoration: none;
            font-size: var(--fs-size);
            font-family: 'Inter', Arial, sans-serif;
            position: relative;
            text-transform: uppercase;
            color: transparent;
            -webkit-text-stroke: 1px var(--text-stroke-color);
            transition: all 0.3s ease;
        }

        .stroke-button .hover-text {
            position: absolute;
            box-sizing: border-box;
            color: var(--animation-color);
            width: 0%;
            inset: 0;
            border-right: var(--border-right) solid var(--animation-color);
            overflow: hidden;
            transition: 0.5s;
            -webkit-text-stroke: 1px var(--animation-color);
            display: flex;
            align-items: center;
            padding: 0.8rem 1.5rem;
        }

        .stroke-button:hover .hover-text {
            width: 100%;
            filter: drop-shadow(0 0 23px var(--animation-color));
        }
        
        /* ================= 隐藏侧边栏的实际按钮 ================= */
        button[kind="secondary"]:has-text("🔍 获取可用模型") {
            display: none !important;
        }
        
        /* 通用隐藏方式 - 针对包含特定文本的按钮 */
        .stButton button[kind="secondary"] {
            opacity: 1;
        }
        
        /* 隐藏获取模型按钮的容器 */
        div[data-testid="column"]:has(button[kind="secondary"]) button[kind="secondary"]:only-child {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        /* ================= 标题加载动画效果 ================= */
        .absolute {
            position: absolute;
        }

        .inline-block {
            display: inline-block;
        }

        .loader {
            display: flex;
            margin: 0.25em 0;
        }

        .w-2 {
            width: 0.5em;
        }

        .dash {
            animation: dashArray 2s ease-in-out infinite,
                dashOffset 2s linear infinite;
        }

        .spin {
            animation: spinDashArray 2s ease-in-out infinite,
                spin 8s ease-in-out infinite,
                dashOffset 2s linear infinite;
            transform-origin: center;
        }

        @keyframes dashArray {
            0% {
                stroke-dasharray: 0 1 359 0;
            }

            50% {
                stroke-dasharray: 0 359 1 0;
            }

            100% {
                stroke-dasharray: 359 1 0 0;
            }
        }

        @keyframes spinDashArray {
            0% {
                stroke-dasharray: 270 90;
            }

            50% {
                stroke-dasharray: 0 360;
            }

            100% {
                stroke-dasharray: 270 90;
            }
        }

        @keyframes dashOffset {
            0% {
                stroke-dashoffset: 365;
            }

            100% {
                stroke-dashoffset: 5;
            }
        }

        @keyframes spin {
            0% {
                rotate: 0deg;
            }

            12.5%,
            25% {
                rotate: 270deg;
            }

            37.5%,
            50% {
                rotate: 540deg;
            }

            62.5%,
            75% {
                rotate: 810deg;
            }

            87.5%,
            100% {
                rotate: 1080deg;
            }
        }
        
        /* 标题装饰圈 */
        .title-loader {
            display: inline-block;
            vertical-align: middle;
            margin-left: 0.5rem;
            width: 2.5rem;
            height: 2.5rem;
        }
        
        </style>
    """, unsafe_allow_html=True)


def render_loading(text: str = "Loading..."):
    """渲染滚动球体加载动画
    
    Args:
        text: 加载提示文字
    """
    st.markdown(f"""
        <div class="loading-container">
            <div class="loader"></div>
            <div class="loading-text">{text}</div>
        </div>
    """, unsafe_allow_html=True)