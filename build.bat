@echo off
chcp 65001 >nul
echo.
echo ========================================================
echo   Sakht-e Ketab-e PDF: Microsoft Generative AI (FA)
echo   Tanzim va Gerdavari: mahdi-hp.ir
echo ========================================================
echo.

if not exist repo (
    echo [EKHTAR] Pooshe-ye 'repo' peyda nashod!
    echo Dar hal-e clone kardan-e repo-ye asli az Microsoft...
    git clone https://github.com/microsoft/generative-ai-for-beginners.git repo
    if errorlevel 1 (
        echo [KHATA] Clone ba moshkel movajeh shod. Lotfan internet ra baresi konid.
        pause
        exit /b 1
    )
)

echo [1/3] Dar hal-e sakht-e HTML ba Python (build_book.py)...
python scripts/build_book.py
if errorlevel 1 (
    echo [KHATA] Sakht-e HTML ba moshkel movajeh shod.
    pause
    exit /b 1
)

echo [2/3] Dar hal-e tabdil-e HTML be PDF ba Brave/Chrome CDP (generate_pdf.js)...
node scripts/generate_pdf.js
if errorlevel 1 (
    echo [KHATA] Sakht-e PDF ba moshkel movajeh shod.
    pause
    exit /b 1
)

echo [3/3] Dar hal-e tazrigh-e Bookmark-haye drakhti be PDF (add_bookmarks.py)...
python scripts/add_bookmarks.py
if errorlevel 1 (
    echo [KHATA] Ezafe kardan-e bookmark-ha ba moshkel movajeh shod.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   [TABRIK] Ketab-e PDF ba movafaghiat sakhte shod!
echo   File: Microsoft-Generative-AI-Beginners-FA.pdf
echo   Site: https://mahdi-hp.ir/
echo ========================================================
echo.
pause
