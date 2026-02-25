/* ================= IMPORTS ================= */
import readline from "readline";
import fs from "fs";
import os from "os";
import path from "path";
import yts from "yt-search";
import { spawn } from "child_process";
import { createCanvas } from "canvas";
import { getAudioUrl } from "google-tts-api";
import ffmpeg from "fluent-ffmpeg";
import ffmpegPath from "ffmpeg-static";

ffmpeg.setFfmpegPath(ffmpegPath);


import makeWASocket, {
  useMultiFileAuthState,
  fetchLatestBaileysVersion,
  DisconnectReason,
  downloadContentFromMessage
} from "@whiskeysockets/baileys";

const MAX_BOTS = 4;
let PREFIX = "/";
let MODE = "eco";
let GLOBAL_DELAY = 3;
let LAST_LOGO_STYLE = null;

const ADMIN_PHONE = "917479655490@s.whatsapp.net";
const ADMIN_LID = "74638512132163@lid";
const AUTO_REACT = new Map(); // chatId -> emoji

const EMOJIS = ["🔥","😈","👑","⚡","💀","🚀","🖤","☠️","✨"];

const GLOBAL_NC_STATE = new Map();


const MENU_WAITING = new Set();

const TTS_LANG = new Map();

const LANGUAGES = {
  en: "English",
  hi: "Hindi",
  ur: "Urdu",
  ar: "Arabic",
  fr: "French",
  es: "Spanish",
  de: "German",
  ru: "Russian",
  ja: "Japanese",
  ko: "Korean",
  zh: "Chinese"
};

const TARGET_MESSAGES = [
  "ɢᴜʟᴀᴀᴍ 🢣🍆",
  "ʟᴀɴᴅ ᴋʜᴀ 🢣🍆",
  "𝙃𝘼𝙏𝙀𝙍 𝙆𝙀 𝙋𝘼𝙋𝘼 〲𝙎TROM ⃝𖤐",
 "TERI MAA RANDI H ESTNI BAAR? > ~> I🎀",
 "TERI MAA RANDI H ESTNI BAAR? > ~> II😄",
 "TERI MAA RANDI H ESTNI BAAR? > ~> III😂",
 "TERI MAA RANDI H ESTNI BAAR? > ~> IV😊",
 "TERI MAA RANDI H ESTNI BAAR? > ~> V😉",
 "TERI MAA RANDI H ESTNI BAAR? > ~> VI😍",
 "OYE HATER -(⸸)- 🇲​​🇰​​🇱",
 "OYE HATER -(𖤐)- ​🇹​​🇲​​🇰​​🇨​",
 "OYE HATER -(🜏)- ​🇷​​🇦​​🇳​​🇩​​🇮​​🇰​​🇪​",
 "OYE HATER -(⛧⃝)- ʀᴀɴᴅ",
 "OYE HATER -(𓄃)- ​🇭​​🇮​​🇯​​🇩​​🇪​",
 "OYE HATER -(⛧)- ​🇱​​🇦​​🇳​​🇬​​🇩​​🇪​",
 "OYE HATER -(𓃵)- ​🇰​​🇺​​🇹​​🇹​​🇮​ ​🇰​​🇪​",
 "OYE HATER -(´ཀ`)- ​🇹​​🇧​​🇰🇧​",
 "OYE HATER -(𓀐𓂸)- ​🇨​​🇭​​🇺​​🇩​​🇱​​🇪​",
 "OYE HATER -(×̷̷͜×̷)- ​🇹​​🇲​​🇷​??",
 "TERI MAA RANDI H ESTNI BAAR? > ~> VII😘",
 "TERI MAA RANDI H ESTNI BAAR? > ~> VIII😎",
 "TERI MAA RANDI H ESTNI BAAR? > ~> XXIV🐭",
 "TERI MAA RANDI H ESTNI BAAR? > ~> XXV🐹",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💚︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💙︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💜︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💛︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🧡︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴❤️︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🤍︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🤎︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💖︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💗︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💓︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💕︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💞︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💘︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💝︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴💟︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🌸︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🌹︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🌺︴",
 "〆HATER ⫸ 𝙇𝙊𝙒 𝙇𝙀𝙑𝙀𝙇 𝙆𝙐𝙏𝙏𝙀𝙔 ︴🌻︴",
 "TERI MAA RANDI H ESTNI BAAR? > ~> XXVI🐰",
 "TERI MAA RANDI H ESTNI BAAR? > ~> XXVII🦊",
 "TERI MAA RANDI H ESTNI BAAR? > ~> XXVIII🐻",
 "TERA BAAP 𝙎TROM ⃝𖤐 KE ALAWA KON HAI",
  "ʙʜᴀɢᴏᴅᴇ 🢣🍆",
  "ɴᴀᴋʟɪ sᴘᴀᴍᴍᴇʀ 🢣🍆"
];

function generateLogoImage(text) {
  const width = 900;
  const height = 420;

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");

  const styles = ["neon", "cyber", "fire", "ice", "royal"];

const isCmd = text.startsWith(PREFIX);
const [cmd, ...args] = isCmd
  ? text.slice(PREFIX.length).trim().split(/\s+/)
  : [];

const reply = (t) =>
  sock.sendMessage(chatId, { text: t }, { quoted: msg });

  let style;
  do {
    style = styles[Math.floor(Math.random() * styles.length)];
  } while (style === LAST_LOGO_STYLE && styles.length > 1);

  LAST_LOGO_STYLE = style;

  let bg;
  switch (style) {
    case "neon":
      bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#020617");
      bg.addColorStop(1, "#0f172a");
      break;

    case "cyber":
      bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#020617");
      bg.addColorStop(1, "#022c22");
      break;

    case "fire":
      bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#1f1300");
      bg.addColorStop(1, "#450a0a");
      break;

    case "ice":
      bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#020617");
      bg.addColorStop(1, "#082f49");
      break;

    case "royal":
      bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#020617");
      bg.addColorStop(1, "#312e81");
      break;
  }

  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  let fontSize = 90;
  do {
    ctx.font = `bold ${fontSize}px Arial`;
    fontSize -= 2;
  } while (ctx.measureText(text).width > width - 80);

  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  switch (style) {
    case "neon": {
      ctx.shadowColor = "#38bdf8";
      ctx.shadowBlur = 30;

      const grad = ctx.createLinearGradient(0, 0, width, 0);
      grad.addColorStop(0, "#22c55e");
      grad.addColorStop(0.5, "#38bdf8");
      grad.addColorStop(1, "#a855f7");
      ctx.fillStyle = grad;
      break;
    }

    case "cyber":
      ctx.shadowColor = "#22d3ee";
      ctx.shadowBlur = 22;
      ctx.fillStyle = "#22d3ee";
      break;

    case "fire": {
      ctx.shadowColor = "#f97316";
      ctx.shadowBlur = 38;

      const grad = ctx.createLinearGradient(0, 0, 0, height);
      grad.addColorStop(0, "#fde047");
      grad.addColorStop(0.5, "#f97316");
      grad.addColorStop(1, "#dc2626");
      ctx.fillStyle = grad;
      break;
    }

    case "ice":
      ctx.shadowColor = "#7dd3fc";
      ctx.shadowBlur = 26;
      ctx.fillStyle = "#e0f2fe";
      break;

    case "royal": {
      ctx.shadowColor = "#facc15";
      ctx.shadowBlur = 32;

      const grad = ctx.createLinearGradient(0, 0, width, 0);
      grad.addColorStop(0, "#fde68a");
      grad.addColorStop(1, "#a16207");
      ctx.fillStyle = grad;
      break;
    }
  }

  ctx.fillText(text.toUpperCase(), width / 2, height / 2);

  ctx.shadowBlur = 0;
  ctx.fillStyle = "#94a3b8";
  ctx.font = "22px Arial";
  ctx.fillText(
    `INFINITY BOT • ${style.toUpperCase()} STYLE`,
    width / 2,
    height - 36
  );

  return canvas.toBuffer("image/png");
}


function generateMenuImage({ PREFIX, MODE, GLOBAL_DELAY }) {
  const width = 1000;
  const height = 1450;

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");

  /* ===== BACKGROUND GRADIENT ===== */
  const bg = ctx.createLinearGradient(0, 0, 0, height);
  bg.addColorStop(0, "#020617");
  bg.addColorStop(1, "#020617");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  /* ===== TITLE ===== */
  ctx.textAlign = "center";
  ctx.font = "bold 56px Arial";
  ctx.fillStyle = "#38bdf8";
  ctx.shadowColor = "#38bdf8";
  ctx.shadowBlur = 25;
  ctx.fillText("✦ INFINITY BOT ✦ COMMAND MENU", width / 2, 90);

  ctx.shadowBlur = 0;

  let y = 150;

  const card = (title, emoji, lines) => {
    const cardHeight = 60 + lines.length * 38;

    ctx.fillStyle = "#0f172a";
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(50, y, width - 100, cardHeight, 18);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#22c55e";
    ctx.font = "bold 34px Arial";
    ctx.textAlign = "left";
    ctx.fillText(`${emoji} ${title}`, 80, y + 42);

    ctx.fillStyle = "#e5e7eb";
    ctx.font = "28px Arial";
    let ty = y + 82;

    for (const line of lines) {
      ctx.fillText(line, 100, ty);
      ty += 36;
    }

    y += cardHeight + 26;
  };

  card("SYSTEM", "⚙️", [
    `${PREFIX}menu`,
    `${PREFIX}menupic`,
    `${PREFIX}ping`,
    `${PREFIX}stats`,
    `${PREFIX}mode`,
    `${PREFIX}eco / ${PREFIX}rage`,
    `${PREFIX}delay <1–5>`,
    `${PREFIX}prefix <new>`
  ]);

  card("GROUP NAME", "📝", [
    `${PREFIX}nc <name>`,
    `${PREFIX}stopnc`
  ]);

  card("TARGET", "🎯", [
    `Reply + ${PREFIX}target`,
    `${PREFIX}free`
  ]);

  card("MEDIA", "🎵", [
    `${PREFIX}yts <query>`,
    `${PREFIX}song`,
    `${PREFIX}video`,
    `${PREFIX}tts <text>`,
    `${PREFIX}setlang <code>`,
    `${PREFIX}langmenu`
  ]);

  card("ADMIN", "👑", [
    `Reply + ${PREFIX}coadmin`,
    `${PREFIX}clearall`
  ]);

  ctx.textAlign = "center";
  ctx.fillStyle = "#94a3b8";
  ctx.font = "26px Arial";
  ctx.fillText(
    `Mode: ${MODE.toUpperCase()}  •  Delay: ${GLOBAL_DELAY}s`,
    width / 2,
    height - 70
  );

  ctx.font = "24px Arial";
  ctx.fillText("© Infinity | All Rights Reserved", width / 2, height - 35);

  return canvas.toBuffer("image/png");
}


const TARGET_DELAY_MS = 900;

const START_TIME = Date.now();
const TARGET_SESSIONS = new Map();
const YTS_CACHE = new Map(); // chatId -> video data
const VIDEO_REQUESTS = new Map(); // chatId -> waitingForChoice
const COADMINS = new Set(); // stores jid of co-admins

const DATA_DIR = "./data";
const SETTINGS_FILE = `${DATA_DIR}/settings.json`;

const SAVED = loadSettings();

PREFIX = SAVED.prefix || "/";
MODE = SAVED.mode || "eco";

for (const jid of SAVED.coadmins || []) {
  COADMINS.add(jid);
}


const log = (...a) =>
  console.log(`[${new Date().toLocaleTimeString()}]`, ...a);

const bare = jid => jid?.split(":")[0];

function loadSettings() {
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);

    if (!fs.existsSync(SETTINGS_FILE)) {
      const defaults = {
        prefix: "/",
        mode: "eco",
        coadmins: []
      };
      fs.writeFileSync(SETTINGS_FILE, JSON.stringify(defaults, null, 2));
      return defaults;
    }

    const raw = fs.readFileSync(SETTINGS_FILE, "utf-8");
    return JSON.parse(raw);
  } catch (err) {
    console.error("❌ Failed to load settings:", err);
    return { prefix: "/", mode: "eco", coadmins: [] };
  }
}

function saveSettings() {
  try {
    const data = {
      prefix: PREFIX,
      mode: MODE,
      coadmins: [...COADMINS]
    };
    fs.writeFileSync(SETTINGS_FILE, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error("❌ Failed to save settings:", err);
  }
}


const isMainAdmin = jid =>
  bare(jid) === ADMIN_PHONE || jid === ADMIN_LID;

const isAdminOrCoadmin = jid => {
  const clean = bare(jid);
  return (
    clean === ADMIN_PHONE ||
    jid === ADMIN_LID ||
    COADMINS.has(clean)
  );
};

const randomEmoji = () =>
  EMOJIS[Math.floor(Math.random() * EMOJIS.length)];


function isCommand(text, cmd) {
  return (
    text === `${PREFIX}${cmd}` ||
    text.startsWith(`${PREFIX}${cmd} `)
  );
}

function getArg(text) {
  return text
    .slice(PREFIX.length)
    .trim()
    .split(" ")
    .slice(1)
    .join(" ");
}

function formatUptime(ms) {
  const s = Math.floor(ms / 1000);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${h}h ${m}m ${sec}s`;
}


async function startBot(botId) {
  const authDir = `./auth_bot_${botId}`;
  const { state, saveCreds } = await useMultiFileAuthState(authDir);
  const { version } = await fetchLatestBaileysVersion();

  const running = new Map(); // chatId -> { baseName, timer }

  const sock = makeWASocket({
    auth: state,
    version,
    printQRInTerminal: false
  });

  sock.ev.on("creds.update", saveCreds);

  let pairCodeRequested = false;

  sock.ev.on("connection.update", async ({ connection, lastDisconnect }) => {
    if (!pairCodeRequested && !sock.authState.creds.registered) {
      pairCodeRequested = true;
      const rl2 = readline.createInterface({ input: process.stdin, output: process.stdout });
      rl2.question(`\n📱 [BOT ${botId}] Enter your WhatsApp number (with country code, e.g. 919876543210): `, async (phone) => {
        rl2.close();
        phone = phone.replace(/[^0-9]/g, "");
        try {
          const code = await sock.requestPairingCode(phone);
          const formatted = code.match(/.{1,4}/g).join("-");
          console.log(`\n╔══════════════════════════════╗`);
          console.log(`║   🔑 INFINITY BOT PAIR CODE   ║`);
          console.log(`╠══════════════════════════════╣`);
          console.log(`║        ${formatted}        ║`);
          console.log(`╚══════════════════════════════╝`);
          console.log(`\n👉 WhatsApp → Linked Devices → Link a Device → Link with Phone Number\n   Enter the code above.\n`);
        } catch (err) {
          console.error(`❌ [BOT ${botId}] Failed to get pair code:`, err.message || err);
        }
      });
    }

if (connection === "open") {
  log(`✅ BOT ${botId} connected — INFINITY BOT ONLINE`);

  for (const [gid, state] of GLOBAL_NC_STATE) {
    if (running.has(gid)) continue;

    const timer = setInterval(async () => {
      try {
        await sock.groupUpdateSubject(
          gid,
          `${state.baseName} ${randomEmoji()}`
        );
      } catch (e) {
        console.log("NC restore error:", e?.message || e);
      }
    }, GLOBAL_DELAY * 1000);

    running.set(gid, { baseName: state.baseName, timer });
  }
}


    if (
      connection === "close" &&
      lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut
    ) {
      startBot(botId);
    }
  });

  const restartNC = (chatId, data) => {
    clearInterval(data.timer);
    data.timer = setInterval(async () => {
      try {
        await sock.groupUpdateSubject(
          chatId,
          `${data.baseName} ${randomEmoji()}`
        );
      } catch {}
    }, GLOBAL_DELAY * 1000);
  };

  sock.ev.on("messages.upsert", async ({ messages }) => {
    for (const msg of messages) {
      if (!msg.message) continue;

      const chatId = msg.key.remoteJid;
      const isGroup = chatId.endsWith("@g.us");
      const isDM = chatId.endsWith("@s.whatsapp.net");

const sender = isGroup
  ? msg.key.participant || msg.participant
  : msg.key.remoteJid;
      if (!isAdminOrCoadmin(sender)) continue;

      const text =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text;

      if (!text) continue;

      if (MODE === "eco" && botId !== 1) continue;

async function fetchBuffer(url) {
  const res = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0" }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
}

if (
  AUTO_REACT.has(chatId) &&
  !msg.key.fromMe &&
  msg.key.id
) {
  try {
    await sock.sendMessage(chatId, {
      react: {
        text: AUTO_REACT.get(chatId),
        key: msg.key
      }
    });
  } catch (e) {
    console.log("Reaction error:", e.message);
  }
}

if (isCommand(text, "nc")) {
  const baseName = getArg(text).trim();

  if (!baseName) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Usage: /nc <name>" },
      { quoted: msg }
    );
    continue;
  }

  if (GLOBAL_DELAY < 0.8) GLOBAL_DELAY = 0.8;

  if (running.has(chatId)) {
    clearInterval(running.get(chatId).timer);
    running.delete(chatId);
  }

  const timer = setInterval(async () => {
    try {
      await sock.groupUpdateSubject(
        chatId,
        `${baseName} ${randomEmoji()}`
      );
    } catch (e) {
      console.log("NC error:", e?.message || e);
    }
  }, GLOBAL_DELAY * 800);

  running.set(chatId, { baseName, timer });
  GLOBAL_NC_STATE.set(chatId, { baseName });

  await sock.sendMessage(
    chatId,
    {
      text:
        `✅ *NC STARTED*\n\n` +
        `📝 Name: ${baseName}\n` +
        `⏱ Delay: ${GLOBAL_DELAY}s\n\n` +
        `⚠️ Safe mode active`
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "stopnc")) {
  const s = running.get(chatId);

  if (!s) {
    await sock.sendMessage(
      chatId,
      { text: "ℹ️ NC is not running" },
      { quoted: msg }
    );
    continue;
  }

  clearInterval(s.timer);
  running.delete(chatId);
  GLOBAL_NC_STATE.delete(chatId);

  await sock.sendMessage(
    chatId,
    { text: "🛑 *NC STOPPED*" },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "delay")) {
  const v = parseFloat(getArg(text));

  if (isNaN(v) || v < 0.2 || v > 5.0) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Delay must be between 0.2 and 5.0 seconds" },
      { quoted: msg }
    );
    continue;
  }

  GLOBAL_DELAY = v;

  for (const [gid, data] of running) {
    clearInterval(data.timer);

    data.timer = setInterval(async () => {
      try {
        await sock.groupUpdateSubject(
          gid,
          `${data.baseName} ${randomEmoji()}`
        );
      } catch (e) {
        console.log("NC delay update error:", e?.message || e);
      }
    }, GLOBAL_DELAY * 1000);
  }

  await sock.sendMessage(
    chatId,
    { text: `✅ Delay updated to ${v.toFixed(1)} seconds` },
    { quoted: msg }
  );

  continue;
}


      if (isCommand(text, "eco")) {
        MODE = "eco";
        await sock.sendMessage(chatId, { text: "ECO mode enabled" }, { quoted: msg });
        continue;
      }

      if (isCommand(text, "rage")) {
        MODE = "rage";
        await sock.sendMessage(chatId, { text: "RAGE mode enabled" }, { quoted: msg });
        continue;
      }

      if (isCommand(text, "mode")) {
        await sock.sendMessage(
          chatId,
          { text: `Mode: ${MODE}\nDelay: ${GLOBAL_DELAY}s` },
          { quoted: msg }
        );
        continue;
      }

if (isCommand(text, "react")) {
  const emoji = getArg(text)?.trim();

  if (!emoji) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}react 😈` },
      { quoted: msg }
    );
    continue;
  }

  AUTO_REACT.set(chatId, emoji);

  await sock.sendMessage(
    chatId,
    {
      text:
`✅ *_AUTO REACTION ENABLED_*

Emoji: ${emoji}

Use ${PREFIX}stopreact to stop.`
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "stopreact")) {
  AUTO_REACT.delete(chatId);

  await sock.sendMessage(
    chatId,
    { text: "🛑 Auto reaction disabled." },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "yts")) {
  const query = getArg(text).trim();

  if (!query) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}yts <song name>` },
      { quoted: msg }
    );
    continue;
  }

  let res;
  try {
    res = await yts(query);
  } catch (e) {
    await sock.sendMessage(
      chatId,
      { text: "❌ YouTube search failed." },
      { quoted: msg }
    );
    continue;
  }

  if (!res.videos || res.videos.length === 0) {
    await sock.sendMessage(
      chatId,
      { text: "❌ No results found." },
      { quoted: msg }
    );
    continue;
  }

  const video = res.videos[0];
  YTS_CACHE.set(chatId, video);

  const caption =
`🎵 *${video.title}*

👤 Channel: ${video.author.name}
⏱ Duration: ${video.timestamp}
👁 Views: ${video.views.toLocaleString()}
📅 Uploaded: ${video.ago}
🔗 URL: ${video.url}

👉 Send */song* to download MP3`;

  await sock.sendMessage(
    chatId,
    {
      image: { url: video.thumbnail },
      caption
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "song")) {
  const video = YTS_CACHE.get(chatId);

  if (!video) {
    await sock.sendMessage(
      chatId,
      { text: "❌ No song selected. Use /yts first." },
      { quoted: msg }
    );
    continue;
  }

  const tempDir = "./temp_music";
  if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir);

  const safeTitle = video.title.replace(/[\\/:*?"<>|]/g, "");
  const outputPath = path.resolve(tempDir, `${safeTitle}.mp3`);

  await sock.sendMessage(
    chatId,
    { text: "⏬ Downloading MP3, please wait…" },
    { quoted: msg }
  );

  const args = [
    "-x",
    "--audio-format", "mp3",
    "--audio-quality", "128K",
    "--no-playlist",
    "-o", outputPath,
    video.url
  ];

  const dl = spawn("yt-dlp", args, { windowsHide: true });

  dl.on("error", async err => {
    console.error("YT-DLP ERROR:", err);
    await sock.sendMessage(
      chatId,
      { text: "❌ yt-dlp failed to start." },
      { quoted: msg }
    );
  });

  dl.on("close", async code => {
    if (code !== 0 || !fs.existsSync(outputPath)) {
      await sock.sendMessage(
        chatId,
        { text: "❌ Download failed." },
        { quoted: msg }
      );
      return;
    }

    await sock.sendMessage(
      chatId,
      {
        audio: fs.readFileSync(outputPath),
        mimetype: "audio/mpeg",
        fileName: `${safeTitle}.mp3`
      },
      { quoted: msg }
    );

    fs.unlinkSync(outputPath);
    YTS_CACHE.delete(chatId);
  });

  continue;
}

if (isCommand(text, "video")) {
  const video = YTS_CACHE.get(chatId);

  if (!video) {
    await sock.sendMessage(
      chatId,
      { text: "❌ No video selected. Use /yts first." },
      { quoted: msg }
    );
    continue;
  }

  VIDEO_REQUESTS.set(chatId, true);

  await sock.sendMessage(
    chatId,
    {
      text:
        "🎬 *Select Video Quality*\n\n" +
        "1️⃣ 420p (Fast / Low size)\n" +
        "2️⃣ 720p (HD / Bigger size)\n\n" +
        "Reply with *1* or *2*"
    },
    { quoted: msg }
  );

  continue;
}

if (VIDEO_REQUESTS.has(chatId)) {
  if (text !== "1" && text !== "2") continue;

  VIDEO_REQUESTS.delete(chatId);

  const video = YTS_CACHE.get(chatId);
  if (!video) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Video session expired. Use /yts again." },
      { quoted: msg }
    );
    continue;
  }

  const quality =
    text === "1"
      ? "bestvideo[height<=420]+bestaudio/best[height<=420]"
      : "bestvideo[height<=720]+bestaudio/best[height<=720]";

  const label = text === "1" ? "420p" : "720p";

  const tempDir = "./temp_video";
  if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir);

  const safeTitle = video.title.replace(/[\\/:*?"<>|]/g, "");
  const output = path.resolve(tempDir, `${safeTitle}_${label}.mp4`);

  await sock.sendMessage(
    chatId,
    { text: `⏬ Downloading *${label}* video, please wait…` },
    { quoted: msg }
  );

  const args = [
    "-f", quality,
    "--merge-output-format", "mp4",
    "--no-playlist",
    "-o", output,
    video.url
  ];

  const dl = spawn("yt-dlp", args, { windowsHide: true });

  dl.on("error", async () => {
    await sock.sendMessage(
      chatId,
      { text: "❌ Failed to start video download." },
      { quoted: msg }
    );
  });

  dl.on("close", async code => {
    if (code !== 0 || !fs.existsSync(output)) {
      await sock.sendMessage(
        chatId,
        { text: "❌ Video download failed." },
        { quoted: msg }
      );
      return;
    }

    await sock.sendMessage(
      chatId,
      {
        video: fs.readFileSync(output),
        mimetype: "video/mp4",
        caption:
          `🎬 *${video.title}* (${label})\n\n` +
          `👁 Views: ${video.views.toLocaleString()}\n` +
          `⚡ Powered by *INFINITY*`
      },
      { quoted: msg }
    );

    fs.unlinkSync(output);
    YTS_CACHE.delete(chatId);
  });

  continue;
}

if (isCommand(text, "coadmin")) {

  if (!isMainAdmin(sender)) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Only main admin can assign co-admins." },
      { quoted: msg }
    );
    continue;
  }

  const ctx = msg.message?.extendedTextMessage?.contextInfo;

  if (!ctx?.participant) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Reply to a user's message to promote." },
      { quoted: msg }
    );
    continue;
  }

  const userJid = bare(ctx.participant);

  if (COADMINS.has(userJid)) {
    await sock.sendMessage(
      chatId,
      { text: "ℹ️ User is already a co-admin." },
      { quoted: msg }
    );
    continue;
  }

  COADMINS.add(userJid);

  await sock.sendMessage(
    chatId,
    {
      text:
        `✅ *CO-ADMIN ADDED*\n\n` +
        `👤 User: @${userJid.split("@")[0]}\n` +
        `Role: Co-Admin`
    },
    {
      quoted: msg,
      mentions: [ctx.participant]
    }
  );

  continue;
}

if (isCommand(text, "clearall")) {
  if (!isMainAdmin(sender)) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Only main admin can clear co-admins." },
      { quoted: msg }
    );
    continue;
  }

  COADMINS.clear();

  await sock.sendMessage(
    chatId,
    { text: "🧹 *All co-admins have been removed.*" },
    { quoted: msg }
  );

  continue;
}


      if (isCommand(text, "target")) {
        const ctx = msg.message?.extendedTextMessage?.contextInfo;
        if (!ctx?.participant || !ctx?.quotedMessage) continue;

        if (TARGET_SESSIONS.has(chatId)) {
          clearInterval(TARGET_SESSIONS.get(chatId).timer);
          TARGET_SESSIONS.delete(chatId);
        }

        let i = 0;
        const quoted = {
          key: {
            remoteJid: chatId,
            fromMe: false,
            id: ctx.stanzaId,
            participant: ctx.participant
          },
          message: ctx.quotedMessage
        };

        const timer = setInterval(async () => {
          await sock.sendMessage(
            chatId,
            { text: TARGET_MESSAGES[i++ % TARGET_MESSAGES.length] },
            { quoted }
          );
        }, TARGET_DELAY_MS);

        TARGET_SESSIONS.set(chatId, { timer });

        await sock.sendMessage(chatId, { text: "🎯 Target locked" }, { quoted: msg });
        continue;
      }

      if (isCommand(text, "free")) {
        const s = TARGET_SESSIONS.get(chatId);
        if (s) {
          clearInterval(s.timer);
          TARGET_SESSIONS.delete(chatId);
          await sock.sendMessage(chatId, { text: "🟢 Target cleared" }, { quoted: msg });
        }
        continue;
      }



if (text.startsWith(`${PREFIX}prefix`)) {
  const parts = text.split(" ");

  if (parts.length < 2) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}prefix <new_prefix>` },
      { quoted: msg }
    );
    continue;
  }

  const newPrefix = parts[1];

  if (
    newPrefix.length > 3 ||
    /\s/.test(newPrefix)
  ) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Prefix must be 1–3 characters, no spaces." },
      { quoted: msg }
    );
    continue;
  }

  const oldPrefix = PREFIX;
  PREFIX = newPrefix;

  await sock.sendMessage(
    chatId,
    {
      text:
        `✅ Prefix updated successfully\n\n` +
        `Old: ${oldPrefix}\n` +
        `New: ${PREFIX}\n\n` +
        `Example: ${PREFIX}menu`
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "langmenu")) {
  let menu = `🌐 *TTS LANGUAGE MENU*\n\n`;
  menu += `Use: ${PREFIX}setlang <code>\n\n`;

  for (const [code, name] of Object.entries(LANGUAGES)) {
    menu += `• ${code} → ${name}\n`;
  }

  await sock.sendMessage(
    chatId,
    { text: menu.trim() },
    { quoted: msg }
  );
  continue;
}

if (isCommand(text, "setlang")) {
  const lang = getArg(text).toLowerCase();

  if (!lang || !LANGUAGES[lang]) {
    await sock.sendMessage(
      chatId,
      {
        text:
`❌ Invalid or missing language

Use:
${PREFIX}langmenu`
      },
      { quoted: msg }
    );
    continue;
  }

  TTS_LANG.set(chatId, lang);

  await sock.sendMessage(
    chatId,
    {
      text:
`✅ TTS language updated

Language : ${LANGUAGES[lang]}
Code     : ${lang}`
    },
    { quoted: msg }
  );
  continue;
}

if (isCommand(text, "menupic")) {
  const img = generateMenuImage({
    PREFIX,
    MODE,
    GLOBAL_DELAY
  });

  await sock.sendMessage(
    chatId,
    {
      image: img,
      caption: "📸 INFINITY — Full Command Menu"
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "logo")) {
  const logoText = getArg(text);

  if (!logoText) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}logo <text>` },
      { quoted: msg }
    );
    continue;
  }

  const img = generateLogoImage(logoText);

  await sock.sendMessage(
    chatId,
    {
      image: img,
      caption: "🎨 *_CODES WITH INFINITY_* "
    },
    { quoted: msg }
  );

  continue;
}


if (isCommand(text, "tts")) {
  const ttsText = getArg(text);

  if (!ttsText) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}tts <text>` },
      { quoted: msg }
    );
    continue;
  }

  const lang = TTS_LANG.get(chatId) || "en";

  let audioUrl;
  try {
    audioUrl = getAudioUrl(ttsText, {
      lang,
      slow: false,
      host: "https://translate.google.com"
    });
  } catch (err) {
    await sock.sendMessage(
      chatId,
      { text: "❌ TTS generation failed." },
      { quoted: msg }
    );
    continue;
  }

  await sock.sendMessage(
    chatId,
    {
      audio: { url: audioUrl },
      mimetype: "audio/mp4",
      ptt: true
    },
    { quoted: msg }
  );

  continue;
}


if (isCommand(text, "ping")) {
  const start = Date.now();

  const sent = await sock.sendMessage(
    chatId,
    { text: "🏓 Pinging *_INFINITY BOT_* ..." },
    { quoted: msg }
  );

  const end = Date.now();
  const latency = end - start;

  await sock.sendMessage(
    chatId,
    {
      text:
        `🏓 *_INFINITY BOT PONG_*\n\n` +
        `⏱ Response Time: *${latency} ms*\n` +
        `🤖 Bot: BOT ${botId}`
    },
    { quoted: sent }
  );

  continue;
}

if (MENU_WAITING.has(chatId)) {

  if (text === "1") {
    MENU_WAITING.delete(chatId);

    const menuText =
`╔══════════════════════╗
║   ✦ INFINITY BOT ✦   ║
║      HELP MENU        ║
╚══════════════════════╝

━━━━━━━━━━━━━━━━━━
⚙️ SYSTEM
━━━━━━━━━━━━━━━━━━
> ${PREFIX}menu
> ${PREFIX}ping
> ${PREFIX}stats
> ${PREFIX}mode
> ${PREFIX}eco
> ${PREFIX}rage
> ${PREFIX}delay <1–5>
> ${PREFIX}prefix <new>

━━━━━━━━━━━━━━━━━━
📝 GROUP NAME
━━━━━━━━━━━━━━━━━━
> ${PREFIX}nc <name>
> ${PREFIX}stopnc

━━━━━━━━━━━━━━━━━━
🎯 TARGET
━━━━━━━━━━━━━━━━━━
> Reply + ${PREFIX}target
> ${PREFIX}free

━━━━━━━━━━━━━━━━━━
🎵 MEDIA
━━━━━━━━━━━━━━━━━━
> ${PREFIX}yts <query>
> ${PREFIX}song
> ${PREFIX}video
> ${PREFIX}tts <text>
> ${PREFIX}setlang <code>
> ${PREFIX}langmenu
> ${PREFIX}logo <text>

━━━━━━━━━━━━━━━━━━
👑 ADMIN
━━━━━━━━━━━━━━━━━━
> Reply + ${PREFIX}coadmin
> ${PREFIX}clearall

━━━━━━━━━━━━━━━━━━
📊 STATUS
━━━━━━━━━━━━━━━━━━
> Prefix : ${PREFIX}
> Mode   : ${MODE.toUpperCase()}
> Delay  : ${GLOBAL_DELAY}s

✦ Powered by INFINITY ✦
© All Credits to Infinity`;

    await sock.sendMessage(
      chatId,
      { text: menuText },
      { quoted: msg }
    );

    continue;
  }

  if (text === "2") {
    MENU_WAITING.delete(chatId);

    const fullMenuImg = generateMenuImage({
      PREFIX,
      MODE,
      GLOBAL_DELAY
    });

    await sock.sendMessage(
      chatId,
      {
        image: fullMenuImg,
        caption: "📸 *INFINITY — ALL COMMANDS*"
      },
      { quoted: msg }
    );

    continue;
  }
}

if (isCommand(text, "menu")) {
  const menuImagePath = "./menu.png"; // main menu image

  if (!fs.existsSync(menuImagePath)) {
    await sock.sendMessage(
      chatId,
      { text: "❌ Menu image not found." },
      { quoted: msg }
    );
    continue;
  }

  await sock.sendMessage(
    chatId,
    {
      image: fs.readFileSync(menuImagePath),
      caption:
        "🌟 *_INFINITY BOT — MENU_*\n\n" +
        "Reply with:\n" +
        "1️⃣ Text Command Menu\n" +
        "2️⃣ Image Command Menu"
    },
    { quoted: msg }
  );

  MENU_WAITING.add(chatId);
  continue;
}


if (isCommand(text, "stats")) {
  const totalRam = os.totalmem();
  const freeRam = os.freemem();
  const usedRam = totalRam - freeRam;

  const ncStatus = running.has(chatId) ? "🟢 ON" : "🔴 OFF";
  const targetStatus = TARGET_SESSIONS.has(chatId) ? "🟢 ON" : "🔴 OFF";

  const caption =
    `📊 *_INFINITY BOT — SYSTEM STATS_*\n\n` +

    `🤖 *Bot Info*\n` +
    `• Bot ID  : BOT ${botId}\n` +
    `• Mode    : ${MODE.toUpperCase()}\n` +
    `• Prefix  : ${PREFIX}\n\n` +

    `⚙️ *Feature Status (This Group)*\n` +
    `• Name Changer (NC) : ${ncStatus}\n` +
    `• Target System    : ${targetStatus}\n` +
    `• NC Delay         : ${GLOBAL_DELAY}s\n\n` +

    `💾 *System Resources*\n` +
    `• RAM Used  : ${(usedRam / 1024 / 1024).toFixed(2)} MB\n` +
    `• RAM Free  : ${(freeRam / 1024 / 1024).toFixed(2)} MB\n` +
    `• RAM Total : ${(totalRam / 1024 / 1024).toFixed(2)} MB\n\n` +

    `⏱ *Uptime*\n` +
    `• ${formatUptime(Date.now() - START_TIME)}\n\n` +

    `⚡ Powered by *_INFINITY_*`;

  const statsImagePath = "./stats.png";

  if (fs.existsSync(statsImagePath)) {
    await sock.sendMessage(
      chatId,
      {
        image: fs.readFileSync(statsImagePath),
        caption
      },
      { quoted: msg }
    );
  } else {
    await sock.sendMessage(
      chatId,
      { text: caption },
      { quoted: msg }
    );
  }

  continue;
}

if (isCommand(text, "gif")) {
  const q = getArg(text);

  if (!q) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}gif <text>` },
      { quoted: msg }
    );
    continue;
  }

  await sock.sendMessage(
    chatId,
    {
      text:
`🖼 *TEXT IMAGE*

╔══════════════╗
║  ${q}
╚══════════════╝`
    },
    { quoted: msg }
  );

  continue;
}

if (isCommand(text, "gif2")) {
  const q = getArg(text);

  if (!q) {
    await sock.sendMessage(
      chatId,
      { text: `❌ Usage: ${PREFIX}gif2 <text>` },
      { quoted: msg }
    );
    continue;
  }

  await sock.sendMessage(
    chatId,
    {
      text:
`✨ *FANCY STYLE*

🌈━━━━━━━━━━━━━━🌈
🔥  ${q.toUpperCase()}
🌈━━━━━━━━━━━━━━🌈

⚡ INFINITY`
    },
    { quoted: msg }
  );

  continue;
}


    }
  });
}

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
rl.question(`How many bots? (1–${MAX_BOTS}): `, n => {
  const c = parseInt(n);
  if (!c || c < 1 || c > MAX_BOTS) process.exit(1);
  for (let i = 1; i <= c; i++) startBot(i);
  rl.close();
});
