// @ts-check
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

function findBrowser() {
  if (process.env.BROWSER_PATH && fs.existsSync(process.env.BROWSER_PATH)) {
    return process.env.BROWSER_PATH;
  }
  const candidates = [
    'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
    'C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
    path.join(process.env.LOCALAPPDATA || '', 'BraveSoftware\\Brave-Browser\\Application\\brave.exe'),
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe'),
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    '/usr/bin/brave-browser',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  ];
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe';
}

const BRAVE_PATH = findBrowser();
const HTML_FILE = path.resolve(__dirname, '..', 'book.html');
const PDF_OUTPUT = path.resolve(__dirname, '..', 'Microsoft-Generative-AI-Beginners-FA.pdf');
const PORT = 9224;

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getBraveVersion(port) {
  for (let i = 0; i < 40; i++) {
    await sleep(250);
    try {
      const data = await new Promise((resolve, reject) => {
        const req = http.get(`http://127.0.0.1:${port}/json/version`, res => {
          let buf = '';
          res.on('data', chunk => buf += chunk);
          res.on('end', () => {
            try {
              resolve(JSON.parse(buf));
            } catch (e) {
              reject(e);
            }
          });
        });
        req.on('error', reject);
        req.setTimeout(1000, () => req.destroy());
      });
      return data;
    } catch (e) {}
  }
  throw new Error('Failed to connect to Brave CDP after multiple attempts.');
}

async function main() {
  console.log('Starting Brave browser in headless mode...');
  const tempDir = path.join(process.env.TEMP || 'C:\\Temp', `brave_pdf_gen_${Date.now()}`);
  fs.mkdirSync(tempDir, { recursive: true });

  const braveProc = spawn(BRAVE_PATH, [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${tempDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-networking',
    '--run-all-compositor-stages-before-draw',
    'about:blank'
  ]);

  braveProc.on('error', err => {
    console.error('Brave process error:', err);
  });

  try {
    const versionInfo = await getBraveVersion(PORT);
    console.log(`Connected to Brave browser (${versionInfo.Browser})`);

    const ws = new WebSocket(versionInfo.webSocketDebuggerUrl);
    let msgId = 1;
    const pending = new Map();

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (pending.has(msg.id)) {
        const { resolve, reject } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
    };

    await new Promise((resolve, reject) => {
      ws.onopen = resolve;
      ws.onerror = reject;
    });

    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = msgId++;
        pending.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    }

    console.log('Creating browser page target...');
    const target = await send('Target.createTarget', { url: 'about:blank' });
    const session = await send('Target.attachToTarget', { targetId: target.targetId, flatten: true });
    const sessionId = session.sessionId;

    function sendSession(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = msgId++;
        pending.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, sessionId, method, params }));
      });
    }

    await sendSession('Page.enable');
    await sendSession('Runtime.enable');

    const fileUrl = 'file:///' + HTML_FILE.replace(/\\/g, '/');
    console.log(`Navigating to book HTML: ${fileUrl}`);
    await sendSession('Page.navigate', { url: fileUrl });

    // Wait for document to settle and fonts to render
    console.log('Waiting for document, fonts, and images to settle...');
    for (let i = 0; i < 30; i++) {
      await sleep(500);
      try {
        const res = await sendSession('Runtime.evaluate', {
          expression: 'document.readyState === "complete" && document.fonts.status === "loaded"',
          returnByValue: true
        });
        if (res.result && res.result.value) {
          console.log('Page readyState is complete and fonts are loaded!');
          break;
        }
      } catch (e) {}
    }

    // Additional settle delay for layout computation
    await sleep(2000);

    console.log('Generating PDF via Brave CDP (Page.printToPDF)...');
    const headerHtml = `
      <div style="font-family: -apple-system, sans-serif; font-size: 8px; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; color: #94a3b8; direction: rtl;">
        <span>دوره هوش مصنوعی مولد مایکروسافت (Generative AI for Beginners)</span>
        <span>نسخه آموزشی فارسی</span>
      </div>
    `;

    const footerHtml = `
      <div style="font-family: -apple-system, sans-serif; font-size: 8px; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; color: #64748b; direction: rtl;">
        <span style="color: #0284c7; font-weight: 600;">Microsoft Generative AI for Beginners</span>
        <span>صفحه <span class="pageNumber"></span> از <span class="totalPages"></span></span>
      </div>
    `;

    const printResult = await sendSession('Page.printToPDF', {
      printBackground: true,
      preferCSSPageSize: true,
      paperWidth: 8.27, // A4
      paperHeight: 11.69,
      marginTop: 0.6,
      marginBottom: 0.6,
      marginLeft: 0.5,
      marginRight: 0.5,
      displayHeaderFooter: true,
      headerTemplate: headerHtml,
      footerTemplate: footerHtml,
      generateTaggedPDF: true
    });

    console.log('Writing PDF buffer to disk...');
    const pdfBuffer = Buffer.from(printResult.data, 'base64');
    
    const possibleTargets = [
      PDF_OUTPUT,
      path.resolve(__dirname, '..', 'Microsoft-Generative-AI-Beginners-Course.pdf'),
      path.resolve(__dirname, '..', 'Microsoft-Generative-AI-Beginners-FA-Updated.pdf')
    ];
    
    let finalOutputPath = null;
    for (const targetPath of possibleTargets) {
      try {
        fs.writeFileSync(targetPath, pdfBuffer);
        finalOutputPath = targetPath;
        console.log(`✅ Saved PDF to: ${targetPath}`);
        break;
      } catch (e) {
        if (e.code === 'EBUSY') {
          console.log(`⚠️ ${path.basename(targetPath)} is locked by another process, trying next...`);
        } else {
          throw e;
        }
      }
    }

    if (!finalOutputPath) {
      finalOutputPath = path.resolve(__dirname, '..', `Microsoft-Generative-AI-Beginners-FA-${Date.now()}.pdf`);
      fs.writeFileSync(finalOutputPath, pdfBuffer);
      console.log(`✅ Saved PDF to fallback: ${finalOutputPath}`);
    }

    // Save current active pdf path to a text file for bookmarks script
    fs.writeFileSync(path.resolve(__dirname, '..', '.active_pdf.txt'), finalOutputPath, 'utf-8');

    const sizeMb = (pdfBuffer.length / (1024 * 1024)).toFixed(2);
    console.log(`File: ${finalOutputPath}`);
    console.log(`Size: ${sizeMb} MB`);

    ws.close();
  } finally {
    braveProc.kill();
    // Clean up temporary user data dir
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch (e) {}
  }
}

main().catch(err => {
  console.error('Fatal error during PDF generation:', err);
  process.exit(1);
});
