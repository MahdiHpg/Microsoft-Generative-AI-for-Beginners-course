# -*- coding: utf-8 -*-
"""
Microsoft Generative AI for Beginners - Persian Educational Edition Book Builder
Converts all 22 chapters into a high-fidelity, beautifully styled HTML book with:
- Clickable Table of Contents & Inter-chapter navigation
- Vazirmatn font embedded (Offline Base64)
- Syntax-highlighted code blocks (Pygments friendly theme)
- Embedded translated diagrams and illustrations (Base64)
- Modern Light educational styling with callout boxes and responsive tables
"""

import os
import re
import sys
import glob
import base64
import datetime
import mimetypes
import io
import qrcode
from pathlib import Path
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def to_fa_digits(text):
    fa_digits = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    for en, fa in fa_digits.items():
        text = text.replace(en, fa)
    return text


def generate_qr_base64(url):
    """Generate compact Base64 PNG QR code for print accessibility"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=3,
            border=1
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        return ""

def get_accurate_dates():
    now = datetime.datetime.now()
    gy, gm, gd = now.year, now.month, now.day
    
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy if gm > 2 else gy - 1
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30

    shamsi_months = ['', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    weekdays_fa = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یک‌شنبه']
    greg_months_en = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    greg_months_fa = ['', 'ژانویه', 'فوریه', 'مارس', 'آوریل', 'مه', 'ژوئن', 'ژوئیه', 'اوت', 'سپتامبر', 'اکتبر', 'نوامبر', 'دسامبر']

    weekday_name = weekdays_fa[now.weekday()]
    raw_shamsi = f"{weekday_name} {jd} {shamsi_months[jm]} {jy}"
    shamsi_str = to_fa_digits(raw_shamsi)
    
    greg_str = f"{now.day} {greg_months_fa[now.month]} {now.year} ({now.day} {greg_months_en[now.month]} {now.year})"

    return shamsi_str, greg_str

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR / "repo"
TRANS_DIR = REPO_DIR / "translations" / "fa"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

CHAPTERS_META = [
    {
        "id": "chapter-00",
        "folder": "00-course-setup",
        "num": "۰۰",
        "title": "راه‌اندازی محیط توسعه و شروع به کار",
        "category": "محیط توسعه و مقدمات",
        "summary": "راه‌اندازی GitHub Codespaces، اجرای محلی در ویندوز/مک با Python، و اتصال به ارائه‌دهندگان مدل (OpenAI، Azure و Microsoft Foundry)",
        "sub_files": ["01-setup-codespaces.md", "02-setup-local.md", "03-providers.md"]
    },
    {
        "id": "chapter-01",
        "folder": "01-introduction-to-genai",
        "num": "۰۱",
        "title": "معرفی هوش مصنوعی مولد و مدل‌های زبان بزرگ (LLMs)",
        "category": "مفاهیم پایه",
        "summary": "آشنایی با چیستی هوش مصنوعی مولد، تاریخچه، شبکه‌های عصبی عمیق، توکنایزیشن و سناریوی استارتاپ آموزشی ما",
        "sub_files": []
    },
    {
        "id": "chapter-02",
        "folder": "02-exploring-and-comparing-different-llms",
        "num": "۰۲",
        "title": "کاوش و مقایسه مدل‌های بزرگ زبانی مختلف",
        "category": "مفاهیم پایه",
        "summary": "مقایسه معماری‌های ترنسفورمر، مدل‌های زبانی در برابر چندوجهی (Multimodal)، و تفاوت سرویس‌های متن‌باز با مدل‌های اختصاصی تجاری",
        "sub_files": []
    },
    {
        "id": "chapter-03",
        "folder": "03-using-generative-ai-responsibly",
        "num": "۰۳",
        "title": "استفاده مسئولانه و اخلاقی از هوش مصنوعی مولد",
        "category": "اخلاق و حاکمیت داده",
        "summary": "اصول هوش مصنوعی مسئولانه مایکروسافت، کاهش سوگیری و تعصب الگوریتمی، شفافیت، و جلوگیری از توهم (Hallucination)",
        "sub_files": []
    },
    {
        "id": "chapter-04",
        "folder": "04-prompt-engineering-fundamentals",
        "num": "۰۴",
        "title": "اصول و مبانی مهندسی پرامپت (Prompt Engineering)",
        "category": "مهندسی پرامپت",
        "summary": "ساختار یک پرامپت استاندارد، نقش دستورالعمل‌ها، تکنیک Zero-Shot و Few-Shot، و راهنمای تصویری معماری درخواست‌ها",
        "sub_files": []
    },
    {
        "id": "chapter-05",
        "folder": "05-advanced-prompts",
        "num": "۰۵",
        "title": "طراحی و ساخت پرامپت‌های پیشرفته",
        "category": "مهندسی پرامپت",
        "summary": "تکنیک‌های پیشرفته مهندسی پرامپت، زنجیره تفکر (Chain of Thought - CoT)، جهت‌دهی خروجی ساختاریافته (JSON) و روش‌های ارزیابی پاسخ",
        "sub_files": []
    },
    {
        "id": "chapter-06",
        "folder": "06-text-generation-apps",
        "num": "۰۶",
        "title": "ساخت برنامه‌های کاربردی تولید متن",
        "category": "توسعه کاربردی",
        "summary": "کدنویسی با SDK پایتون و تایپ‌اسکریپت برای فراخوانی API، کنترل پارامترهای Temperature و Top_P و تولید متن‌های خلاقانه و خلاصه",
        "sub_files": []
    },
    {
        "id": "chapter-07",
        "folder": "07-building-chat-applications",
        "num": "۰۷",
        "title": "ساخت برنامه‌های چت و ربات‌های گفتگو",
        "category": "توسعه کاربردی",
        "summary": "معماری چت‌بات‌های مدرن، مدیریت پنجره زمینه (Context Window)، پیام‌های System/User/Assistant و حافظه مکالمه",
        "sub_files": []
    },
    {
        "id": "chapter-08",
        "folder": "08-building-search-applications",
        "num": "۰۸",
        "title": "ساخت برنامه‌های جستجوی هوشمند با پایگاه‌های داده برداری",
        "category": "جستجوی معنایی",
        "summary": "تبدیل متن به بردار (Embeddings)، محاسبه شباهت کسینوسی (Cosine Similarity)، و ساخت سامانه جستجوی معنایی متنی",
        "sub_files": []
    },
    {
        "id": "chapter-09",
        "folder": "09-building-image-applications",
        "num": "۰۹",
        "title": "ساخت برنامه‌های تولید تصویر با DALL-E",
        "category": "چندوجهی و بصری",
        "summary": "آشنایی با مدل‌های انتشار (Diffusion Models)، تولید تصویر با متن، بازسازی و ویرایش تصویر با API و پیاده‌سازی گالری هوشمند",
        "sub_files": []
    },
    {
        "id": "chapter-10",
        "folder": "10-building-low-code-ai-applications",
        "num": "۱۰",
        "title": "ساخت برنامه‌های هوش مصنوعی با ابزارهای کم‌کد (Low-Code)",
        "category": "توسعه سازمانی",
        "summary": "یکپارچه‌سازی مدل‌های هوش مصنوعی با ابزارهای Microsoft Power Platform، Power Apps و ساخت گردش‌کارهای خودکار تجاری بدون کدنویسی پیچیده",
        "sub_files": ["assignment.md"]
    },
    {
        "id": "chapter-11",
        "folder": "11-integrating-with-function-calling",
        "num": "۱۱",
        "title": "یکپارچه‌سازی سیستم‌ها با فراخوانی توابع (Function Calling)",
        "category": "توسعه پیشرفته",
        "summary": "اتصال مدل‌های هوش مصنوعی به پایگاه‌های داده و APIهای خارجی از طریق ابزارسازی و تعریف ساختار شمای توابع (JSON Schema)",
        "sub_files": []
    },
    {
        "id": "chapter-12",
        "folder": "12-designing-ux-for-ai-applications",
        "num": "۱۲",
        "title": "طراحی تجربه کاربری (UX) برای برنامه‌های هوش مصنوعی",
        "category": "طراحی و محصول",
        "summary": "اصول طراحی رابط کاربری برای هوش مصنوعی، مدیریت زمان تاخیر (Streaming)، نحوه گزارش خطاها، ارجاع منابع و جلب اعتماد کاربر",
        "sub_files": []
    },
    {
        "id": "chapter-13",
        "folder": "13-securing-ai-applications",
        "num": "۱۳",
        "title": "امنیت و محافظت از برنامه‌های هوش مصنوعی مولد",
        "category": "امنیت و پدافند سایبری",
        "summary": "تهدیدات امنیتی اختصاصی LLMها، حملات تزریق پرامپت (Prompt Injection)، نشت داده‌ها، نقض حریم خصوصی و راهکارهای دفاعی",
        "sub_files": []
    },
    {
        "id": "chapter-14",
        "folder": "14-the-generative-ai-application-lifecycle",
        "num": "۱۴",
        "title": "چرخه عمر برنامه‌ها و مدیریت LLMOps",
        "category": "عملیات و استقرار",
        "summary": "فرآیند چرخه عمر محصولات هوش مصنوعی مولد از ایده تا استقرار، ارزیابی، نظارت مداوم و راهبردهای LLMOps",
        "sub_files": []
    },
    {
        "id": "chapter-15",
        "folder": "15-rag-and-vector-databases",
        "num": "۱۵",
        "title": "تولید تقویت‌شده با بازیابی (RAG) و پایگاه‌های داده برداری",
        "category": "معماری پیشرفته RAG",
        "summary": "معماری جامع RAG، قطعه‌بندی مستندات (Chunking)، اندیس‌گذاری برداری، بازیابی اطلاعات و تولید پاسخ بر پایه دانش اختصاصی سازمان",
        "sub_files": []
    },
    {
        "id": "chapter-16",
        "folder": "16-open-source-models",
        "num": "۱۶",
        "title": "مدل‌های متن‌باز و اکوسیستم Hugging Face",
        "category": "اکوسیستم متن‌باز",
        "summary": "استفاده از مدل‌های متن‌باز روی پلتفرم Hugging Face، انتخاب مدل‌های سبک و استقرار بر روی زیرساخت‌های ابری و محلی",
        "sub_files": []
    },
    {
        "id": "chapter-17",
        "folder": "17-ai-agents",
        "num": "۱۷",
        "title": "عامل‌های هوش مصنوعی هوشمند (AI Agents)",
        "category": "سیستم‌های عامل هوشمند",
        "summary": "تبدیل مدل‌های زبانی به کارگزاران مستقل خودکار، حافظه، برنامه‌ریزی و تصمیم‌گیری، و چارچوب‌های محبوب مانند AutoGen و Semantic Kernel",
        "sub_files": []
    },
    {
        "id": "chapter-18",
        "folder": "18-fine-tuning",
        "num": "۱۸",
        "title": "تنظیم دقیق مدل‌های زبانی (Fine-Tuning)",
        "category": "یادگیری عمیق",
        "summary": "چه زمانی به Fine-Tuning نیاز داریم؟ مقایسه با RAG، آماده‌سازی مجموعه داده آموزشی، و روش‌های بهینه‌سازی پارامترها (PEFT / LoRA)",
        "sub_files": ["RESOURCES.md"]
    },
    {
        "id": "chapter-19",
        "folder": "19-slm",
        "num": "۱۹",
        "title": "مدل‌های زبانی کوچک (Small Language Models - SLM)",
        "category": "مدل‌های نوین",
        "summary": "انقلاب مدل‌های کوچک با کارایی فوق‌العاده مانند سری Phi-3 مایکروسافت، اجرای محلی بدون نیاز به کارت گرافیک سنگین و کاربرد در Edge",
        "sub_files": []
    },
    {
        "id": "chapter-20",
        "folder": "20-mistral",
        "num": "۲۰",
        "title": "ساخت و توسعه با مدل‌های خانواده Mistral",
        "category": "مدل‌های نوین",
        "summary": "بررسی مدل‌های پیشرفته فرانسوی Mistral 7B و Mixtral 8x7B، معماری مخلوط متخصصین (MoE) و استفاده کاربردی از آن‌ها",
        "sub_files": []
    },
    {
        "id": "chapter-21",
        "folder": "21-meta",
        "num": "۲۱",
        "title": "ساخت و توسعه با مدل‌های خانواده Meta و Llama",
        "category": "مدل‌های نوین",
        "summary": "نقش بنیادین متا در هوش مصنوعی متن‌باز، معماری Llama 3، قابلیت‌های چندزبانه، پروانه‌های انتشار و کاربرد در پروژه‌های مقیاس‌پذیر",
        "sub_files": []
    }
]

def load_font_base64(font_path):
    """Load local TTF font file and return base64 string"""
    with open(font_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def image_to_base64(img_path):
    """Convert image file to data URI"""
    mime_type, _ = mimetypes.guess_type(img_path)
    if not mime_type:
        ext = os.path.splitext(img_path)[1].lower()
        if ext == ".webp":
            mime_type = "image/webp"
        elif ext == ".png":
            mime_type = "image/png"
        elif ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".svg":
            mime_type = "image/svg+xml"
        else:
            mime_type = "image/png"
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


# Index all original English high-resolution images across the repository
ORIGINAL_IMAGES_INDEX = {}
for root, dirs, files in os.walk(REPO_DIR):
    if "translations" in root or "translated_images" in root:
        continue
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")):
            name_no_ext = os.path.splitext(f)[0].lower()
            ORIGINAL_IMAGES_INDEX[name_no_ext] = Path(root) / f

# Educational Persian translations for original English UI and prompt screenshots
IMAGE_TRANSLATIONS = {
    "custom-instructions": {
        "title": "📝 ترجمه و راهنمای فارسی متن تصویر بالا (تنظیمات ChatGPT):",
        "items": [
            ("بخش اول (اطلاعات زمینه شما برای پاسخ بهتر):", "«من در یک شرکت نرم‌افزاری بزرگ در سطح ارشد کار می‌کنم. از سال ۲۰۰۸ به عنوان متخصص فناوری فعالیت دارم، دارای مدرک کارشناسی ارشد در مهندسی نرم‌افزار و برنامه‌نویس باسابقه هستم. همچنین استاد پاره‌وقت علوم کامپیوتر می‌باشم.»"),
            ("بخش دوم (نحوه پاسخ‌دهی مورد انتظار از ChatGPT):", "«مرا با نام یاسمین (Jasmine) خطاب کن. ChatGPT می‌تواند درباره هر موضوعی نظر و دیدگاه شخصی داشته باشد.»")
        ]
    },
    "lesson-plan-prompt": {
        "title": "📝 ترجمه و راهنمای فارسی پرامپت و پاسخ چت در تصویر بالا:",
        "items": [
            ("درخواست کاربر (Prompt):", "«یک طرح درس درباره لیست‌های پیوندی (Linked Lists) برای دانشجویان مقدماتی ایجاد کن.»"),
            ("پاسخ ChatGPT:", "«سلام یاسمین! با توجه به زمینه تخصصی شما در مهندسی نرم‌افزار و تدریس دانشگاهی، طرح درسی عمیق و کاربردی درباره مفهوم لیست‌های پیوندی، پیاده‌سازی گره‌ها و تحلیل پیچیدگی زمانی آن آماده کرده‌ام...»")
        ]
    },
    "notebook-search": {
        "title": "📝 راهنمای فارسی ورودی جستجو در تصویر بالا (VS Code):",
        "items": [
            ("متن جستجو (Query):", "«What is Azure Machine Learning? (ماشین آموزش آزور چیست؟)»"),
            ("عملکرد نوت‌بوک:", "کاربر پرسش خود را در کادر جستجوی تعاملی بالای VS Code وارد کرده و سیستم جستجوی معنایی، مرتبط‌ترین بخش‌های متنی و ویدیویی را بر اساس وکتورها استخراج می‌کند.")
        ]
    },
    "query-results": {
        "title": "📝 راهنمای فارسی نتایج جستجوی معنایی در تصویر بالا:",
        "items": [
            ("پرسش جستجو:", "«Can rstudio be used with Azure ML? (آیا می‌توان از RStudio همراه با Azure ML استفاده کرد؟)»"),
            ("نتیجه الگوریتم:", "مدل تعبیه‌ساز (Embedding) شباهت معنایی پرسش با پایگاه داده را محاسبه کرده و مرتبط‌ترین ویدیوها، اسناد و گویندگان را با امتیاز شباهت (Similarity Score) بازگردانده است.")
        ]
    },
    "who-will-pay": {
        "title": "📝 راهنمای گزینه‌های پنجره GitHub Codespaces:",
        "items": [
            ("گزینه Personal:", "استفاده از سهمیه رایگان ماهیانه حساب کاربری شخصی گیتهاب (بدون هزینه)."),
            ("گزینه Organization:", "پرداخت هزینه‌های ماشین ابری از طریق سازمان متصل به گیتهاب.")
        ]
    }
}

def resolve_image_path(current_dir, img_src):
    """
    Resolve relative image paths preferring high-resolution original English images
    over blurry machine-translated WebP images.
    """
    clean_src = img_src.split("?")[0].strip()
    raw_basename = os.path.basename(clean_src)
    
    # 1. Extract base name without hash if it is a translated image
    # e.g. custom-instructions.b96f59aa69356fcf.webp -> custom-instructions
    clean_name = re.sub(r'\.[a-f0-9]{16}\.webp$', '', raw_basename).lower()
    clean_name = os.path.splitext(clean_name)[0].lower()

    # 2. Check original English images index FIRST for crystal-clear resolution
    if clean_name in ORIGINAL_IMAGES_INDEX:
        return ORIGINAL_IMAGES_INDEX[clean_name]

    # 3. Try directly relative to current directory
    p1 = (current_dir / clean_src).resolve()
    if p1.is_file():
        return p1
        
    # 4. Check in repo/translated_images/fa/
    p2 = REPO_DIR / "translated_images" / "fa" / raw_basename
    if p2.is_file():
        return p2
        
    # 5. Check in original english lesson images
    folder_name = current_dir.name
    p3 = REPO_DIR / folder_name / "images" / raw_basename
    if p3.is_file():
        return p3

    # 6. Check recursive search by filename in repo
    matches = list(REPO_DIR.glob(f"**/{raw_basename}"))
    if matches:
        return matches[0]

    return None

def process_markdown_content(md_text, current_dir, chapter_meta):
    """Preprocess markdown to resolve links, images, video badges, and callouts"""
    
    # 1. Video banner conversion with QR Code and URL for print
    # Pattern: [![alt](image_url)](video_url)
    def video_replacer(match):
        alt = match.group(1)
        img_src = match.group(2)
        video_url = match.group(3)
        img_file = resolve_image_path(current_dir, img_src)
        if img_file:
            data_uri = image_to_base64(img_file)
            qr_uri = generate_qr_base64(video_url)
            qr_html = f'<div class="video-qr-wrapper"><img src="{qr_uri}" alt="QR Code" class="video-qr-code" /><span class="video-qr-text">اسکن کد QR</span></div>' if qr_uri else ''

            card_html = f"""<div class="video-card">
<a href="{video_url}" target="_blank" class="video-banner-link" title="مشاهده ویدیو در یوتیوب"><img src="{data_uri}" alt="{alt}" class="video-banner" /></a>
<div class="video-card-footer">
<div class="video-details">
<div class="video-label">🎥 ویدیوی رسمی آموزش این درس</div>
<div class="video-print-hint"><span class="video-scan-text">📱 برای مشاهده ویدیو، کد QR را اسکن کنید یا پیوند زیر را باز کنید:</span><a href="{video_url}" target="_blank" class="video-url-link">{video_url}</a></div>
</div>
<div class="video-interactive"><a href="{video_url}" target="_blank" class="video-btn">▶️ پخش در یوتیوب</a>{qr_html}</div>
</div>
</div>"""
            return card_html
        return match.group(0)

    md_text = re.sub(
        r'\[\!\[(.*?)\]\((.*?)\)\]\((https?://(?:youtu\.be|www\.youtube\.com|aka\.ms)[^\)]*)\)',
        video_replacer,
        md_text
    )

    # 2. Local & cached images conversion
    def img_replacer(match):
        alt = match.group(1)
        src = match.group(2).strip()
        if "endpoint.png" in src and (ASSETS_DIR / "endpoint.png").is_file():
            data_uri = image_to_base64(ASSETS_DIR / "endpoint.png")
            return f"""
<figure class="img-figure book-diagram-figure">
  <img src="{data_uri}" alt="صفحه دریافت کلید و آدرس نقطه پایانی در پرتال Azure" loading="lazy" />
  <figcaption class="img-caption">📐 شکل: پنجره کلیدها و نقطه پایانی (Keys and Endpoint) در درگاه ابری Azure</figcaption>
  <div class="diagram-guide-box">
    <div class="diagram-guide-title">📌 راهنمای کادرهای قرمز در تصویر بالا (Keys & Endpoint):</div>
    <ul class="diagram-guide-list">
      <li><strong>کادر شماره ۱ (KEY 1):</strong> کلید محرمانه اصلی برای احراز هویت درخواست‌های کلاینت در کد برنامه.</li>
      <li><strong>کادر شماره ۲ (KEY 2):</strong> کلید پشتیبان؛ در صورتی که بخواهید کلید اول را بازتولید (Regenerate) کنید، این کلید دسترسی مداوم را حفظ می‌کند.</li>
      <li><strong>کادر شماره ۳ (Endpoint):</strong> آدرس پایانه اختصاصی وب‌سرویس شما برای اتصال کلاینت OpenAI.</li>
    </ul>
  </div>
  <div class="callout callout-tip practical-ollama-box">
    <div class="callout-header">💡 راهنمای طلایی: اجرای ۱۰۰٪ رایگان و محلی تمرین‌ها با Ollama (بدون نیاز به Azure یا ویزاکارت)</div>
    <p>اگر حساب Azure یا کارت اعتباری بین‌المللی ندارید، اصلاً نگران نباشید! شما می‌توانید تمام تمرین‌های این درس و سراسر کتاب را بدون پرداخت حتی یک ریال، بدون تحریم و کاملاً آفلاین روی کامپیوتر شخصی خودتان اجرا کنید:</p>
    <div class="ollama-steps">
      <div class="ollama-step"><strong>۱. نصب Ollama:</strong> نرم‌افزار رایگان <a href="https://ollama.com" target="_blank">Ollama</a> را دانلود و نصب کنید.</div>
      <div class="ollama-step"><strong>۲. اجرای یک مدل سریع و سبک:</strong> در ترمینال سیستم خود تایپ کنید: <code>ollama run phi3</code> (یا <code>ollama run llama3.2:1b</code>).</div>
      <div class="ollama-step"><strong>۳. اجرای کدهای پایتون این درس:</strong> در کدهای پایتون این درس، کافیست دو خط زیر را تنظیم کنید:
        <div class="code-inline-box">
          <code>client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")</code>
        </div>
        کد شما بلافاصله به مدل محلی متصل شده و پاسخ‌ها را دقیقاً با همان کلاینت استاندارد پایتون تولید می‌کند!
      </div>
    </div>
  </div>
</figure>
"""
        if src.startswith("http://") or src.startswith("https://"):
            return match.group(0)
        img_file = resolve_image_path(current_dir, src)
        if img_file:
            data_uri = image_to_base64(img_file)
            base_key = img_file.stem.lower()
            translation_html = ""
            if base_key in IMAGE_TRANSLATIONS:
                t_info = IMAGE_TRANSLATIONS[base_key]
                items_html = "".join([f'<div class="img-translation-item"><strong>{title}</strong> {desc}</div>' for title, desc in t_info["items"]])
                translation_html = f"""<div class="img-translation-card"><div class="img-translation-header">{t_info["title"]}</div><div class="img-translation-body">{items_html}</div></div>"""

            caption = f'<figcaption class="img-caption">{alt}</figcaption>' if alt and alt != alt.lower() and len(alt) > 3 else ''
            return f'<figure class="img-figure"><img src="{data_uri}" alt="{alt}" loading="lazy" />{caption}{translation_html}</figure>'
        return match.group(0)

    md_text = re.sub(r'\!\[(.*?)\]\((.*?)\)', img_replacer, md_text)

    # 3. Inter-chapter markdown link normalization
    # Pattern: ../02-exploring-and-comparing-different-llms/README.md -> #chapter-02
    def link_replacer(match):
        text = match.group(1)
        url = match.group(2)
        m = re.search(r'(\d{2})-[a-zA-Z0-9_-]+', url)
        if m:
            ch_num = m.group(1)
            return f'<a href="#chapter-{ch_num}" class="internal-link">{text}</a>'
        return match.group(0)

    md_text = re.sub(r'\[(.*?)\]\(((?:\.\./|\./)[\w\-./]+\.md[^\)]*)\)', link_replacer, md_text)

    # 4. Strip excessive tracking query strings from links
    md_text = re.sub(r'\?WT\.mc_id=[a-zA-Z0-9\-_]+', '', md_text)

    # 5. Remove HTML comments from markdown
    # 5. Clean up redundant video hint callouts
    md_text = re.sub(r'>\s*_?\(برای مشاهده ویدئوی این درس روی تصویر بالا کلیک کنید\)_?\s*', '', md_text)
    md_text = re.sub(r'<!--.*?-->', '', md_text, flags=re.DOTALL)

    return md_text

def enhance_html_elements(soup):
    """Post-process HTML to style callouts, tables, and typography"""
    
    # 1. Enhance blockquotes to modern callouts & clean raw [!TAG]
    for bq in soup.find_all('blockquote'):
        # Strip raw [!NOTE], [!TIP], etc. from inner paragraphs
        for p in bq.find_all(['p', 'span', 'li']):
            for c in list(p.contents):
                if isinstance(c, str):
                    new_c = re.sub(r'\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*', '', c)
                    c.replace_with(new_c)

        text = bq.get_text().strip()
        callout_type = "callout-note"
        callout_icon = "💡"
        callout_title = "نکته کاربردی"
        
        if "⚠️" in text or "هشدار" in text or "warning" in text.lower():
            callout_type = "callout-warning"
            callout_icon = "⚠️"
            callout_title = "هشدار و توجه مهم"
        elif "💡" in text or "پیشنهاد" in text or "tip" in text.lower():
            callout_type = "callout-tip"
            callout_icon = "✨"
            callout_title = "نکته و پیشنهاد ویژه"
        elif "سناریو" in text or "استارتاپ" in text:
            callout_type = "callout-scenario"
            callout_icon = "🚀"
            callout_title = "سناریوی استارتاپ ما"
        elif "توجه:" in text or "note" in text.lower():
            callout_type = "callout-info"
            callout_icon = "ℹ️"
            callout_title = "یادداشت تکمیلی"
            
        bq['class'] = bq.get('class', []) + ['callout', callout_type]
        # Prepend a header badge
        header_tag = soup.new_tag('div', attrs={'class': 'callout-header'})
        header_tag.string = f"{callout_icon} {callout_title}"
        bq.insert(0, header_tag)

    # 2. Wrap tables in responsive styled container
    for tbl in soup.find_all('table'):
        container = soup.new_tag('div', attrs={'class': 'table-container'})
        tbl.wrap(container)

    # 3. Ensure all images are wrapped and constrained
    for img in soup.find_all('img'):
        if not img.find_parent('figure') and not img.find_parent('div', class_='video-card'):
            fig = soup.new_tag('figure', attrs={'class': 'img-figure'})
            img.wrap(fig)

    # 4. Enhance code blocks with dedicated developer terminal card & language badge
    lang_labels = {
        "PYTHON": "Python 🐍",
        "TYPESCRIPT": "TypeScript 🔷",
        "JAVASCRIPT": "JavaScript 🟨",
        "BASH": "Terminal / Bash ⚡",
        "SH": "Shell 💻",
        "CMD": "Command Prompt 💻",
        "POWERSHELL": "PowerShell 🔷",
        "OUTPUT": "خروجی برنامه (Output) 📋",
        "JSON": "JSON ⚙️",
        "TEXT": "متن / Text 📝",
        "HTML": "HTML 🌐",
        "CSS": "CSS 🎨",
        "ENV": "تنظیمات محیطی (.env) 🔒",
        "SQL": "SQL 🗄️",
        "MARKDOWN": "Markdown 📄"
    }

    for pre in soup.find_all('pre'):
        if pre.parent and 'code-block-wrapper' in pre.parent.get('class', []):
            continue

        code = pre.find('code')
        lang = "CODE"
        if code and code.get('class'):
            for cls in code['class']:
                if cls.startswith('language-'):
                    lang = cls.replace('language-', '').upper()

        badge_text = lang_labels.get(lang, f"{lang} 💻")

        wrapper = soup.new_tag('div', attrs={'class': 'code-block-wrapper'})
        header = soup.new_tag('div', attrs={'class': 'code-block-header'})

        dots = soup.new_tag('div', attrs={'class': 'code-dots'})
        for d in ['dot-red', 'dot-yellow', 'dot-green']:
            span = soup.new_tag('span', attrs={'class': f'dot {d}'})
            dots.append(span)

        badge = soup.new_tag('span', attrs={'class': 'code-lang-badge'})
        badge.string = badge_text

        header.append(dots)
        header.append(badge)

        pre.wrap(wrapper)
        wrapper.insert(0, header)

    return soup

def build_complete_book():
    print("Preparing Vazirmatn fonts...")
    font_regular = load_font_base64(FONTS_DIR / "Vazirmatn-Regular.ttf")
    font_medium = load_font_base64(FONTS_DIR / "Vazirmatn-Medium.ttf")
    font_bold = load_font_base64(FONTS_DIR / "Vazirmatn-Bold.ttf")

    # Pygments CSS for clean light theme
    pyg_css = HtmlFormatter(style='friendly').get_style_defs('.codehilite')

    css_styles = f"""
@font-face {{
  font-family: 'Vazirmatn';
  src: url(data:font/truetype;charset=utf-8;base64,{font_regular}) format('truetype');
  font-weight: 400;
  font-style: normal;
}}
@font-face {{
  font-family: 'Vazirmatn';
  src: url(data:font/truetype;charset=utf-8;base64,{font_medium}) format('truetype');
  font-weight: 500;
  font-style: normal;
}}
@font-face {{
  font-family: 'Vazirmatn';
  src: url(data:font/truetype;charset=utf-8;base64,{font_bold}) format('truetype');
  font-weight: 700;
  font-style: normal;
}}

/* Reset and Universal Zero-Overflow Layout */
*, *::before, *::after {{
  box-sizing: border-box !important;
  margin: 0;
  padding: 0;
}}

html, body {{
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
}}

body {{
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14.5px;
  line-height: 2.0;
  color: #1e293b;
  background-color: #ffffff;
  direction: rtl;
  text-align: justify;
  text-justify: inter-word;
  word-wrap: break-word !important;
  overflow-wrap: anywhere !important;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  font-family: 'Vazirmatn', sans-serif;
  font-weight: 700;
  line-height: 1.5;
  color: #0f172a;
  page-break-after: avoid;
  break-after: avoid;
}}

h1 {{
  font-size: 24px;
  color: #0369a1;
  margin: 28px 0 16px 0;
  border-bottom: 2px solid #e0f2fe;
  padding-bottom: 8px;
}}

h2 {{
  font-size: 19px;
  color: #0284c7;
  margin: 24px 0 12px 0;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 6px;
}}

h3 {{
  font-size: 16px;
  color: #0f766e;
  margin: 20px 0 10px 0;
}}

h4 {{
  font-size: 14.5px;
  color: #475569;
  margin: 16px 0 8px 0;
}}

p {{
  margin-bottom: 14px;
  color: #334155;
}}

a {{
  color: #0284c7;
  text-decoration: none;
  font-weight: 500;
  word-break: break-all !important;
  overflow-wrap: anywhere !important;
}}

a:hover {{
  text-decoration: underline;
  color: #0369a1;
}}

ul, ol {{
  margin: 10px 0 18px 24px;
  padding-right: 18px;
}}

li {{
  margin-bottom: 6px;
  color: #334155;
}}

hr {{
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 32px 0;
}}

/* Cover Page */
.cover-page {{
  page-break-after: always;
  break-after: page;
  min-height: 250mm;
  padding: 45mm 25mm 30mm 25mm;
  background: linear-gradient(135deg, #090d16 0%, #0f172a 40%, #0369a1 100%);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}}

.cover-badge {{
  display: inline-block;
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
  padding: 6px 16px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 700;
  width: fit-content;
  margin-bottom: 24px;
}}

.cover-title {{
  font-size: 38px;
  font-weight: 800;
  line-height: 1.35;
  color: #ffffff;
  margin-bottom: 16px;
  text-shadow: 0 4px 12px rgba(0,0,0,0.4);
}}

.cover-subtitle {{
  font-size: 17px;
  line-height: 1.8;
  color: #bae6fd;
  font-weight: 400;
  max-width: 90%;
  margin-bottom: 40px;
}}

.cover-meta-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  margin-bottom: 30px;
}}

.cover-meta-item {{
  display: flex;
  flex-direction: column;
}}

.cover-meta-label {{
  font-size: 11.5px;
  color: #94a3b8;
  margin-bottom: 4px;
}}

.cover-meta-val {{
  font-size: 13.5px;
  font-weight: 700;
  color: #f8fafc;
}}

.cover-footer {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  padding-top: 18px;
  font-size: 12px;
  color: #cbd5e1;
}}

/* Preface & Introduction */
.preface-page {{
  page-break-before: always;
  break-before: page;
  padding: 20px 0;
}}

.preface-card {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin: 20px 0;
}}

/* Table of Contents (TOC) */
.toc-section {{
  page-break-before: always;
  break-before: page;
  padding: 10px 0;
}}

.toc-header {{
  text-align: center;
  margin-bottom: 30px;
}}

.toc-badge {{
  display: inline-block;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 20px;
  margin-bottom: 8px;
}}

.toc-title {{
  font-size: 26px;
  color: #0f172a;
}}

.toc-grid {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}

.toc-item {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  text-decoration: none !important;
  color: inherit;
  page-break-inside: avoid;
  break-inside: avoid;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}}

.toc-item:hover {{
  border-color: #38bdf8;
  background: #f0f9ff;
}}

.toc-item-left {{
  display: flex;
  align-items: center;
  gap: 14px;
}}

.toc-num-pill {{
  background: #0284c7;
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 6px;
  min-width: 48px;
  text-align: center;
}}

.toc-item-content {{
  display: flex;
  flex-direction: column;
}}

.toc-item-title {{
  font-size: 14.5px;
  font-weight: 700;
  color: #0f172a;
}}

.toc-item-summary {{
  font-size: 11.5px;
  color: #64748b;
  margin-top: 2px;
}}

.toc-tag {{
  font-size: 11px;
  background: #f1f5f9;
  color: #475569;
  padding: 3px 10px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  white-space: nowrap;
}}

/* Chapter Styles */
.chapter-container {{
  page-break-before: always;
  break-before: page;
  padding-top: 10px;
}}

.chapter-header-banner {{
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  page-break-inside: avoid;
  break-inside: avoid;
}}

.chapter-meta-tag {{
  display: inline-block;
  background: #0284c7;
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 6px;
  margin-bottom: 10px;
}}

.chapter-main-title {{
  font-size: 24px;
  color: #0c4a6e;
  font-weight: 800;
  margin-bottom: 6px;
}}

.chapter-summary-note {{
  font-size: 13.5px;
  color: #0369a1;
  line-height: 1.7;
}}

/* Video Card */
.video-card {{
  margin: 20px 0 26px 0;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  page-break-inside: avoid;
  break-inside: avoid;
}}

.video-banner-link {{
  display: block;
  text-decoration: none;
}}

.video-banner {{
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  display: block;
}}

.video-card-footer {{
  padding: 12px 18px;
  background: #f8fafc;
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: space-between !important;
  border-top: 1px solid #e2e8f0;
  gap: 16px;
  overflow-wrap: normal !important;
  word-break: normal !important;
}}

.video-details {{
  display: flex !important;
  flex-direction: column !important;
  gap: 4px;
  flex: 1 1 65% !important;
  min-width: 200px !important;
  overflow-wrap: normal !important;
  word-break: normal !important;
}}

.video-label {{
  font-size: 13.5px;
  font-weight: 700;
  color: #1e293b;
  white-space: nowrap !important;
  overflow-wrap: normal !important;
}}

.video-print-hint {{
  display: flex !important;
  flex-direction: column !important;
  gap: 2px;
  overflow-wrap: normal !important;
}}

.video-scan-text {{
  font-size: 11px;
  color: #64748b;
  overflow-wrap: normal !important;
  word-break: normal !important;
}}

.video-url-link {{
  font-size: 11px;
  color: #0284c7 !important;
  font-family: 'Consolas', 'Courier New', monospace;
  direction: ltr !important;
  text-align: right;
  text-decoration: underline;
  word-break: break-all !important;
  overflow-wrap: anywhere !important;
}}

.video-interactive {{
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 12px;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}}

.video-btn {{
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px;
  background: #ef4444;
  color: #ffffff !important;
  font-size: 12px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 8px;
  text-decoration: none !important;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.25);
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}}

.video-btn:hover {{
  background: #dc2626;
}}

.video-qr-wrapper {{
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  background: #ffffff;
  padding: 4px 6px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  flex-shrink: 0 !important;
  width: 68px !important;
}}

.video-qr-code {{
  width: 58px !important;
  height: 58px !important;
  display: block !important;
}}

.video-qr-text {{
  font-size: 9px;
  font-weight: 600;
  color: #64748b;
  margin-top: 2px;
  white-space: nowrap !important;
}}

/* Diagram Guide Box */
.diagram-guide-box {{
  margin: 14px auto 0 auto;
  max-width: 95%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 16px;
  text-align: right;
  font-size: 12.5px;
}}

.diagram-guide-title {{
  font-weight: 700;
  color: #0284c7;
  margin-bottom: 6px;
}}

.diagram-guide-list {{
  margin: 0;
  padding-right: 18px;
  color: #334155;
  line-height: 1.8;
}}


/* High-Resolution Screenshot Translation Card */
.img-translation-card {{
  margin: 14px auto 0 auto;
  max-width: 95%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-right: 4px solid #38bdf8;
  border-radius: 8px;
  padding: 12px 18px;
  text-align: right;
  font-size: 12.5px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}

.img-translation-header {{
  font-weight: 700;
  color: #0284c7;
  margin-bottom: 8px;
  font-size: 13px;
}}

.img-translation-item {{
  margin-bottom: 6px;
  line-height: 1.85;
  color: #334155;
}}

.img-translation-item strong {{
  color: #0f172a;
}}

/* Practical Ollama Box */
.practical-ollama-box {{
  margin: 16px auto 0 auto !important;
  max-width: 95%;
  text-align: right;
}}

.ollama-steps {{
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}}

.ollama-step {{
  font-size: 12.5px;
  line-height: 1.8;
  color: #1e293b;
}}

.code-inline-box {{
  direction: ltr;
  text-align: left;
  background: #e2e8f0;
  padding: 6px 12px;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 12px;
  margin: 6px 0;
  color: #0f172a;
}}

/* Figures and Images */
.img-figure {{
  margin: 22px 0;
  text-align: center;
  page-break-inside: avoid;
  break-inside: avoid;
}}

.img-figure img {{
  max-width: 95%;
  max-height: 480px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 8px -2px rgba(0,0,0,0.06);
}}

.img-caption {{
  font-size: 12px;
  color: #64748b;
  margin-top: 8px;
  font-style: italic;
}}

/* Callouts */
.callout {{
  margin: 20px 0;
  padding: 16px 20px;
  border-radius: 10px;
  page-break-inside: avoid;
  break-inside: avoid;
  border-right: 5px solid #0284c7;
  background: #f8fafc;
}}

.callout-header {{
  font-size: 13.5px;
  font-weight: 700;
  margin-bottom: 8px;
}}

.callout-tip {{
  border-right-color: #10b981;
  background: #f0fdf4;
}}
.callout-tip .callout-header {{
  color: #047857;
}}

.callout-warning {{
  border-right-color: #f59e0b;
  background: #fffbeb;
}}
.callout-warning .callout-header {{
  color: #b45309;
}}

.callout-info {{
  border-right-color: #0284c7;
  background: #f0f9ff;
}}
.callout-info .callout-header {{
  color: #0369a1;
}}

.callout-scenario {{
  border-right-color: #8b5cf6;
  background: #faf5ff;
}}
.callout-scenario .callout-header {{
  color: #6d28d9;
}}

/* Tables */
.table-container {{
  margin: 20px 0 26px 0;
  max-width: 100%;
  overflow: visible !important;
  page-break-inside: avoid;
  break-inside: avoid;
}}

table {{
  width: 100% !important;
  max-width: 100% !important;
  border-collapse: collapse;
  font-size: 12.5px;
  direction: rtl;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  table-layout: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
}}

th {{
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 700;
  padding: 10px 14px;
  text-align: right;
  border-bottom: 2px solid #cbd5e1;
  word-wrap: break-word;
  overflow-wrap: break-word;
}}

td {{
  padding: 10px 14px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
  vertical-align: middle;
  word-wrap: break-word;
  overflow-wrap: break-word;
}}

tr:nth-child(even) td {{
  background-color: #f8fafc;
}}

/* Code Blocks & Dedicated Developer Frame */
.code-block-wrapper {{
  margin: 22px 0;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 4px 10px -2px rgba(15, 23, 42, 0.05);
  page-break-inside: avoid;
  break-inside: avoid;
  direction: ltr !important;
}}

.code-block-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f1f5f9;
  padding: 8px 14px;
  border-bottom: 1px solid #e2e8f0;
  direction: ltr !important;
}}

.code-dots {{
  display: flex;
  gap: 6px;
  align-items: center;
}}

.dot {{
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
}}

.dot-red {{ background: #ef4444; }}
.dot-yellow {{ background: #f59e0b; }}
.dot-green {{ background: #10b981; }}

.code-lang-badge {{
  font-family: 'Vazirmatn', 'Cascadia Code', Consolas, monospace;
  font-size: 11px;
  font-weight: 700;
  color: #334155;
  background: #ffffff;
  padding: 3px 12px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  direction: rtl;
}}

pre, .codehilite {{
  direction: ltr !important;
  text-align: left !important;
  font-family: 'Cascadia Code', 'Fira Code', Consolas, Monaco, monospace;
  font-size: 12px;
  line-height: 1.65;
  background: #f8fafc !important;
  border: none !important;
  padding: 16px 18px !important;
  margin: 0 !important;
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  overflow: hidden !important;
  page-break-inside: avoid;
  break-inside: avoid;
}}

code {{
  font-family: 'Cascadia Code', 'Fira Code', Consolas, Monaco, monospace;
  font-size: 12px;
  background: #f1f5f9;
  color: #0f172a;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  direction: ltr;
  display: inline-block;
  white-space: pre-wrap !important;
  word-break: break-word !important;
  overflow-wrap: anywhere !important;
}}

pre code {{
  background: none !important;
  border: none !important;
  padding: 0 !important;
  display: block;
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
}}

/* Eliminate scrollbars across all print and media views */
@media print {{
  * {{
    -ms-overflow-style: none !important;
    scrollbar-width: none !important;
  }}
  *::-webkit-scrollbar {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }}
  pre, .codehilite, pre code, code {{
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    overflow: visible !important;
  }}
  .table-container {{
    overflow: visible !important;
  }}
}}

/* Pygments Syntax Styling */
{pyg_css}

/* Chapter Footer / Navigation */
.chapter-footer {{
  margin-top: 40px;
  padding-top: 18px;
  border-top: 1px dashed #cbd5e1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  page-break-inside: avoid;
  break-inside: avoid;
}}

.back-to-toc {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  color: #0369a1 !important;
  font-size: 12.5px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  text-decoration: none !important;
}}

.back-to-toc:hover {{
  background: #e0f2fe;
}}

/* Sub-sections within chapters */
.sub-document {{
  margin-top: 36px;
  padding-top: 24px;
  border-top: 2px dashed #e2e8f0;
}}

.sub-doc-badge {{
  display: inline-block;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  margin-bottom: 8px;
}}
"""

    # Dynamic accurate dates (Badesaba / Solar Hijri + Full Gregorian)
    shamsi_date, greg_date = get_accurate_dates()

    # Build Cover Page HTML
    cover_html = f"""
<div class="cover-page">
  <div>
    <span class="cover-badge">✨ نسخه جامع و کامل آموزشی — زبان فارسی</span>
    <h1 class="cover-title">هوش مصنوعی مولد<br>برای مبتدیان</h1>
    <p class="cover-subtitle">
      دوره جامع و پروژه‌محور مایکروسافت در ۲۱ درس کامل<br>
      از مفاهیم مدل‌های زبان بزرگ (LLM) تا مهندسی پرامپت، سامانه‌های RAG، پایگاه‌های داده برداری و توسعه عامل‌های هوشمند (AI Agents)
    </p>
  </div>

  <div class="cover-meta-grid">
    <div class="cover-meta-item">
      <span class="cover-meta-label">مؤلف و منبع اصلی:</span>
      <span class="cover-meta-val">تیم مشاوران ابر مایکروسافت (Microsoft Cloud Advocates)</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">محتوای دوره:</span>
      <span class="cover-meta-val">۲۲ فصل کامل، نمونه‌کدهای پایتون و تایپ‌اسکریپت</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">تنظیم و گردآوری:</span>
      <span class="cover-meta-val">مهدی حیدرپور — <a href="https://mahdi-hp.ir/" target="_blank" style="color: #0284c7; font-weight: 700; text-decoration: underline;">mahdi-hp.ir</a></span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">تاریخ تنظیم و گردآوری:</span>
      <span class="cover-meta-val">{shamsi_date}</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">تاریخ میلادی معادل:</span>
      <span class="cover-meta-val">{greg_date}</span>
    </div>
  </div>

  <div class="cover-footer">
    <span>نسخه نهایی مستندات رسمی مایکروسافت (v3)</span>
    <span>تنظیم و گردآوری: مهدی حیدرپور (<a href="https://mahdi-hp.ir/" target="_blank" style="color: #0284c7; text-decoration: underline;">mahdi-hp.ir</a>) — {shamsi_date} ({greg_date})</span>
  </div>
</div>
"""

    # Build Preface & Startup Story HTML
    preface_html = f"""
<div class="preface-page" id="preface">
  <h1>🌱 پیش‌گفتار و راهنمای دوره</h1>
  <p>
    به دوره آموزشی <strong>«هوش مصنوعی مولد برای مبتدیان» (Generative AI for Beginners)</strong> خوش آمدید! این دوره توسط تیم <em>مشاوران فناوری ابری مایکروسافت (Microsoft Cloud Advocates)</em> طراحی شده تا هر توسعه‌دهنده، محقق یا علاقه‌مندی بتواند از نقطه صفر تا سطوح پیشرفته، اصول ساخت برنامه‌های واقعی با هوش مصنوعی مولد را فرا بگیرد.
  </p>
  
  <div class="preface-card">
    <h3 style="color:#0369a1; margin-top:0;">🚀 سناریوی محوری: استارتاپ آموزشی ما</h3>
    <p>
      برای اینکه یادگیری صرفاً تئوری نباشد، تمام دروس این دوره حول یک <strong>استارتاپ فرضی در حوزه آموزش</strong> شکل گرفته‌اند. مأموریت این استارتاپ چنین تعریف شده است:
    </p>
    <blockquote class="callout callout-scenario" style="margin: 10px 0;">
      <em>«افزایش دسترسی به یادگیری در مقیاس جهانی، تضمین آموزش عادلانه و شخصی‌سازی تجربیات آموزشی برای هر دانش‌آموز بر اساس توانایی‌ها و نیازهای فردی.»</em>
    </blockquote>
    <p>
      در طول فصول این کتاب، خواهید دید که چگونه از مدل‌های زبانی برای حل مسائل واقعی مانند تدریس خصوصی ۲۴ ساعته، خلاصه‌سازی متون پیچیده، جستجوی معنایی در منابع درسی، تولید تصاویر کمک‌آموزشی و امنیت داده‌های کاربران استفاده می‌کنیم.
    </p>
  </div>

  <h2>💡 ساختار دروس: «یادگیری» در برابر «ساخت»</h2>
  <p>
    دروس این کتاب به دو دسته اصلی تقسیم شده‌اند:
  </p>
  <ul>
    <li><strong>دروس یادگیری (Learn):</strong> بر درک عمیق مفاهیم، زیرساخت‌ها، ریاضیات و معماری سیستم‌های هوش مصنوعی، توکنایزیشن، ایمنی و اخلاق تمرکز دارند.</li>
    <li><strong>دروس ساخت (Build):</strong> همراه با کدهای عملی به دو زبان <strong>Python</strong> و <strong>TypeScript</strong>، به شما یاد می‌دهند چگونه با کتابخانه‌ها کار کنید، با APIها ارتباط برقرار نمایید و نرم‌افزارهای کامل بسازید.</li>
  </ul>
</div>
"""

    # Build Table of Contents HTML
    toc_html = f"""
<div class="toc-section" id="table-of-contents">
  <div class="toc-header">
    <span class="toc-badge">راهنمای فصول</span>
    <h1 class="toc-title">فهرست مطالب و پیش‌فصل‌ها</h1>
    <p style="color:#64748b; font-size:13.5px; margin-top:6px;">برای پرش مستقیم به هر فصل، روی ردیف مربوطه کلیک کنید:</p>
  </div>

  <div class="toc-grid">
"""

    for ch in CHAPTERS_META:
        toc_html += f"""
    <a href="#{ch['id']}" class="toc-item">
      <div class="toc-item-left">
        <span class="toc-num-pill">{ch['num']}</span>
        <div class="toc-item-content">
          <span class="toc-item-title">{ch['title']}</span>
          <span class="toc-item-summary">{ch['summary']}</span>
        </div>
      </div>
      <span class="toc-tag">{ch['category']}</span>
    </a>
"""

    toc_html += """
  </div>
</div>
"""

    # Process all chapters
    chapters_html = ""

    def highlight_code(code, lang, attrs):
        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()
        formatter = HtmlFormatter(nowrap=True)
        return highlight(code, lexer, formatter)

    md_parser = MarkdownIt('commonmark', {'highlight': highlight_code}).enable('table')

    for ch in CHAPTERS_META:
        print(f"Processing {ch['folder']}...")
        ch_dir = TRANS_DIR / ch["folder"]
        readme_path = ch_dir / "README.md"
        
        if not readme_path.is_file():
            print(f"Warning: {readme_path} not found!")
            continue

        with open(readme_path, "r", encoding="utf-8") as f:
            raw_md = f.read()

        # Remove top level title if we render our own header
        processed_md = process_markdown_content(raw_md, ch_dir, ch)
        
        # If the chapter markdown starts with # title, let's remove it to avoid duplicate titles
        processed_md = re.sub(r'^\s*#\s+[^\n]+\n', '', processed_md)

        # Convert markdown to HTML using CommonMark
        chapter_body_html = md_parser.render(processed_md)

        # Process any sub-files (like setup guides or assignments)
        sub_docs_html = ""
        for sf in ch.get("sub_files", []):
            sf_path = ch_dir / sf
            if sf_path.is_file():
                with open(sf_path, "r", encoding="utf-8") as sff:
                    sf_raw = sff.read()
                sf_proc = process_markdown_content(sf_raw, ch_dir, ch)
                sf_html = md_parser.render(sf_proc)
                sub_docs_html += f"""
<div class="sub-document">
  <span class="sub-doc-badge">بخش تکمیلی / راهنمای همراه</span>
  {sf_html}
</div>
"""

        soup = BeautifulSoup(chapter_body_html + sub_docs_html, 'html.parser')
        soup = enhance_html_elements(soup)

        chapters_html += f"""
<section class="chapter-container" id="{ch['id']}">
  <div class="chapter-header-banner">
    <span class="chapter-meta-tag">درس {ch['num']} از ۲۱</span>
    <h1 class="chapter-main-title">{ch['title']}</h1>
    <p class="chapter-summary-note">{ch['summary']}</p>
  </div>

  <div class="chapter-content">
    {str(soup)}
  </div>

  <div class="chapter-footer">
    <a href="#table-of-contents" class="back-to-toc">🔝 بازگشت به فهرست مطالب</a>
    <span style="font-size:12px; color:#94a3b8;">درس {ch['num']} — هوش مصنوعی مولد مایکروسافت</span>
  </div>
</section>
"""

    # Master HTML Assembly
    full_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>هوش مصنوعی مولد برای مبتدیان — مایکروسافت</title>
  <style>
{css_styles}
  </style>
</head>
<body>
{cover_html}
{preface_html}
{toc_html}
{chapters_html}
</body>
</html>
"""

    output_path = BASE_DIR / "book.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Successfully generated book.html! Size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    build_complete_book()
