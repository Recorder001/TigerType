// ══════════════════════════════════════════════════════════
// 호랑이타자연습 공식 포럼 — Firebase 클라이언트
// ══════════════════════════════════════════════════════════

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.7.3/firebase-app.js";
import {
    getAuth,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    onAuthStateChanged,
    signOut,
} from "https://www.gstatic.com/firebasejs/11.7.3/firebase-auth.js";
import {
    getDatabase,
    ref,
    set,
    push,
    get,
    update,
} from "https://www.gstatic.com/firebasejs/11.7.3/firebase-database.js";

// ── Firebase 설정 ──────────────────────────────────────
const firebaseConfig = {
    apiKey: "AIzaSyDHJeJiAkW3T-EJAY_CM4m5If0TeJBDPbU",
    authDomain: "tigertype-c66fd.firebaseapp.com",
    databaseURL: "https://tigertype-c66fd-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "tigertype-c66fd",
    storageBucket: "tigertype-c66fd.firebasestorage.app",
    messagingSenderId: "1047815304853",
    appId: "1:1047815304853:web:45593a1ee2e5f06d95cd9c",
};

const app  = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db   = getDatabase(app);

// ── 상태 ───────────────────────────────────────────────
let currentUser = null;
let nickname    = "";

// ── DOM 캐시 ───────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ── 페이지 라우팅 (SPA) ────────────────────────────────
function navigate(page) {
    $$(".page").forEach(el => el.classList.remove("active"));
    const target = $(`#page-${page}`);
    if (target) target.classList.add("active");
    window.scrollTo(0, 0);
}

// ── 토스트 알림 ────────────────────────────────────────
function toast(msg, type = "success") {
    const el = $("#toast");
    el.textContent = msg;
    el.className = `toast toast-${type} show`;
    setTimeout(() => el.classList.remove("show"), 3000);
}

// ── 시간 포맷 ──────────────────────────────────────────
function fmtTime(secs) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}

function fmtDate(ts) {
    const d = new Date(ts * 1000);
    return d.toLocaleDateString("ko-KR") + " " +
           d.toLocaleTimeString("ko-KR", {hour:"2-digit", minute:"2-digit"});
}

// ── 네비게이션 UI 업데이트 ─────────────────────────────
function updateNav() {
    const loggedIn = $("#nav-logged-in");
    const loggedOut = $("#nav-logged-out");
    const nickEl = $("#nav-nickname");

    if (currentUser) {
        loggedIn.style.display = "flex";
        loggedOut.style.display = "none";
        nickEl.textContent = nickname || "익명";
    } else {
        loggedIn.style.display = "none";
        loggedOut.style.display = "flex";
    }
}

// ══════════════════════════════════════════════════════════
// 인증
// ══════════════════════════════════════════════════════════

// 로그인
async function handleLogin(e) {
    e.preventDefault();
    const email = $("#login-email").value.trim();
    const pw    = $("#login-pw").value;
    if (!email || !pw) return toast("이메일과 비밀번호를 입력하세요", "error");

    try {
        await signInWithEmailAndPassword(auth, email, pw);
        toast("로그인 성공!");
        navigate("main");
    } catch (err) {
        const code = err.code || "";
        if (code.includes("user-not-found") || code.includes("invalid-credential"))
            toast("이메일 또는 비밀번호가 올바르지 않습니다", "error");
        else if (code.includes("wrong-password"))
            toast("비밀번호가 올바르지 않습니다", "error");
        else
            toast("로그인 중 오류가 발생했습니다", "error");
    }
}

// 회원가입
async function handleSignup(e) {
    e.preventDefault();
    const email = $("#signup-email").value.trim();
    const pw    = $("#signup-pw").value;
    if (!email || !pw) return toast("이메일과 비밀번호를 입력하세요", "error");

    try {
        const cred = await createUserWithEmailAndPassword(auth, email, pw);
        const uid  = cred.user.uid;
        const nick = email.split("@")[0];
        await set(ref(db, `users/${uid}`), {
            email,
            nickname: nick,
            created_at: Math.floor(Date.now() / 1000),
        });
        toast("회원가입 성공! 자동으로 로그인됩니다");
        navigate("main");
    } catch (err) {
        const code = err.code || "";
        if (code.includes("email-already"))
            toast("이미 등록된 이메일입니다", "error");
        else if (code.includes("weak-password"))
            toast("비밀번호는 6자 이상이어야 합니다", "error");
        else if (code.includes("invalid-email"))
            toast("올바른 이메일 형식이 아닙니다", "error");
        else
            toast("회원가입 중 오류가 발생했습니다", "error");
    }
}

// 로그아웃
async function handleLogout() {
    await signOut(auth);
    currentUser = null;
    nickname = "";
    updateNav();
    navigate("main");
    toast("로그아웃 되었습니다");
}

// 인증 상태 감시
onAuthStateChanged(auth, async (user) => {
    currentUser = user;
    if (user) {
        try {
            const snap = await get(ref(db, `users/${user.uid}/nickname`));
            nickname = snap.val() || user.email.split("@")[0];
        } catch {
            nickname = user.email.split("@")[0];
        }
    } else {
        nickname = "";
    }
    updateNav();
    loadRanking();
    loadSharedTexts();
});

// ══════════════════════════════════════════════════════════
// 닉네임
// ══════════════════════════════════════════════════════════

function openProfile() {
    if (!currentUser) { navigate("login"); return; }
    $("#profile-email").textContent = currentUser.email;
    $("#profile-nick").value = nickname;
    navigate("profile");
}

async function handleProfileSave(e) {
    e.preventDefault();
    const newNick = $("#profile-nick").value.trim();
    if (!newNick) return toast("닉네임을 입력하세요", "error");
    if (!currentUser) return;

    try {
        await update(ref(db, `users/${currentUser.uid}`), { nickname: newNick });
        nickname = newNick;
        updateNav();
        toast("닉네임이 변경되었습니다!");
        navigate("main");
    } catch {
        toast("닉네임 변경 중 오류가 발생했습니다", "error");
    }
}

// ══════════════════════════════════════════════════════════
// 랭킹
// ══════════════════════════════════════════════════════════

let allRecords = [];   // 전체 기록 캐시
let rankMode = "cpm";  // "cpm" | "text" | "challenge"
let selectedText = null; // 연습글 랭킹에서 선택된 텍스트

window.loadRanking = loadRanking;
window.filterRanking = function() { renderRanking(); };

window.switchRankMode = function(mode) {
    rankMode = mode;
    selectedText = null;

    // 서브 탭 활성화
    $$(".sub-tab-btn").forEach(el => el.classList.remove("active"));
    event.target.classList.add("active");

    // 도전 모드 테마 전환
    if (mode === "challenge") {
        document.body.classList.add("challenge-theme");
    } else {
        document.body.classList.remove("challenge-theme");
    }

    // 제목 변경
    const titles = { cpm: "타수 랭킹", text: "연습글 랭킹", challenge: "도전 모드 랭킹" };
    $("#ranking-title").textContent = titles[mode];

    // 표시 전환
    if (mode === "text") {
        $("#text-cards-wrap").style.display = "block";
        $("#ranking-table-wrap").style.display = "none";
        renderTextCards();
    } else {
        $("#text-cards-wrap").style.display = "none";
        $("#ranking-table-wrap").style.display = "block";
        renderRanking();
    }
};

window.selectTextCard = function(textName) {
    selectedText = textName;
    // 카드 활성화 표시
    $$(".text-card").forEach(el => el.classList.remove("active"));
    const card = document.querySelector(`.text-card[data-name="${CSS.escape(textName)}"]`);
    if (card) card.classList.add("active");
    renderTextDetail();
};

window.closeTextDetail = function() {
    selectedText = null;
    $$(".text-card").forEach(el => el.classList.remove("active"));
    $("#text-detail-wrap").innerHTML = "";
};

async function loadRanking() {
    const tbody = $("#ranking-body");
    tbody.innerHTML = `<tr><td colspan="8" class="loading-msg">
        <span class="spinner"></span> 랭킹 불러오는 중...</td></tr>`;

    try {
        const snap = await get(ref(db, "records"));
        const raw = [];
        snap.forEach(child => raw.push(child.val()));

        // 같은 uid + 같은 text_name + 같은 모드 중 CPM 최고 기록만 유지
        const bestMap = {};
        for (const r of raw) {
            const ch = r.challenge_mode ? "C" : "N";
            const key = `${r.uid || ""}__${r.text_name || ""}__${ch}`;
            if (!bestMap[key] || (r.cpm || 0) > (bestMap[key].cpm || 0)) {
                bestMap[key] = r;
            }
        }
        allRecords = Object.values(bestMap);
        allRecords.sort((a, b) => (b.cpm || 0) - (a.cpm || 0));

        if (rankMode === "text") {
            renderTextCards();
        } else {
            renderRanking();
        }
    } catch (err) {
        console.error("랭킹 로드 에러:", err);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">
            랭킹을 불러올 수 없습니다.</td></tr>`;
    }
}

// ── 연습글 카드 렌더링 ─────────────────────────────────
function renderTextCards() {
    const grid = $("#text-card-grid");
    const normal = allRecords.filter(r => !r.challenge_mode);

    // 연습글별 그룹핑: 가장 높은 글자수와 기록 수
    const textMap = {};
    for (const r of normal) {
        const name = r.text_name || "-";
        if (!textMap[name]) {
            textMap[name] = { name, total_jamo: r.total_jamo || 0, count: 0, is_custom: r.is_custom, preview: r.text_preview || "" };
        }
        textMap[name].count++;
        if ((r.total_jamo || 0) > textMap[name].total_jamo) textMap[name].total_jamo = r.total_jamo;
        if (!textMap[name].preview && r.text_preview) textMap[name].preview = r.text_preview;
    }

    const texts = Object.values(textMap);
    texts.sort((a, b) => b.total_jamo - a.total_jamo);

    if (texts.length === 0) {
        grid.innerHTML = `<div class="empty-msg" style="grid-column:1/-1;">
            아직 기록이 없습니다.<br>게임에서 연습을 완료해 보세요!</div>`;
        return;
    }

    grid.innerHTML = texts.map(t => {
        const prefix = t.is_custom ? "[커스텀] " : "";
        const active = selectedText === t.name ? "active" : "";
        return `<div class="text-card ${active}" data-name="${esc(t.name)}"
                     onclick="selectTextCard('${esc(t.name).replace(/'/g, "\\'")}')">
            <div class="tc-title">${esc(prefix + t.name)}</div>
            <div class="tc-meta">
                <span class="tc-jamo">${t.total_jamo} 타</span>
                <span class="tc-count">${t.count}명 참여</span>
            </div>
        </div>`;
    }).join("");

    // 선택된 텍스트가 있으면 상세도 갱신
    if (selectedText) renderTextDetail();
}

// ── 연습글 상세 (미리보기 + 랭킹) ──────────────────────
function renderTextDetail() {
    const wrap = $("#text-detail-wrap");
    if (!selectedText) { wrap.innerHTML = ""; return; }

    const rows = allRecords
        .filter(r => !r.challenge_mode && (r.text_name || "-") === selectedText)
        .sort((a, b) => (b.cpm || 0) - (a.cpm || 0));

    // 미리보기 텍스트 찾기
    const previewRecord = rows.find(r => r.text_preview) || rows[0];
    const preview = previewRecord?.text_preview || "";
    const prefix = previewRecord?.is_custom ? "[커스텀] " : "";

    let tableHtml = "";
    if (rows.length === 0) {
        tableHtml = `<div class="empty-msg">이 연습글의 기록이 없습니다.</div>`;
    } else {
        tableHtml = `<table class="ranking-table">
            <thead><tr>
                <th>#</th><th>닉네임</th><th>타수</th><th>정확도</th>
                <th class="hide-mobile">시간</th><th class="hide-mobile">Backspace</th><th>태그</th>
            </tr></thead>
            <tbody>${rows.map((r, i) => {
                const rank = i + 1;
                const cls = rank <= 3 ? `rank-${rank}` : "";
                let badges = "";
                if (r.full_combo) badges += `<span class="badge badge-fullcombo">FULL COMBO</span>`;
                return `<tr class="${cls}">
                    <td>${rank}</td>
                    <td>${esc(r.nickname || "익명")}</td>
                    <td class="cpm-val">${r.cpm} 타/분</td>
                    <td class="acc-val">${(r.accuracy || 0).toFixed(1)}%</td>
                    <td class="hide-mobile">${fmtTime(r.elapsed || 0)}</td>
                    <td class="hide-mobile">${r.backspace_count ?? 0}회</td>
                    <td>${badges}</td>
                </tr>`;
            }).join("")}</tbody>
        </table>`;
    }

    wrap.innerHTML = `<div class="text-detail">
        <div class="td-header">
            <h2>${esc(prefix + selectedText)}</h2>
            <button class="td-close" onclick="closeTextDetail()">닫기</button>
        </div>
        ${preview ? `<div class="td-preview">${esc(preview)}</div>` : ""}
        <div class="td-label">랭킹</div>
        <div style="overflow-x:auto;">${tableHtml}</div>
    </div>`;

    // 스크롤
    wrap.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── 타수/도전 테이블 렌더링 ────────────────────────────
function renderRanking() {
    const tbody = $("#ranking-body");

    let rows;
    if (rankMode === "challenge") {
        rows = allRecords.filter(r => r.challenge_mode);
    } else {
        rows = allRecords.filter(r => !r.challenge_mode);
    }

    rows.sort((a, b) => (b.cpm || 0) - (a.cpm || 0));

    if (rows.length === 0) {
        const msg = rankMode === "challenge"
            ? "도전 모드 기록이 없습니다.<br>도전 모드에서 연습을 완료해 보세요!"
            : "아직 기록이 없습니다.<br>게임에서 연습을 완료해 보세요!";
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">${msg}</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map((r, i) => {
        const rank = i + 1;
        const cls  = rank <= 3 ? `rank-${rank}` : "";
        let badges = "";
        if (r.full_combo) badges += `<span class="badge badge-fullcombo">FULL COMBO</span>`;

        const namePrefix = r.is_custom ? "[커스텀] " : "";
        const displayName = namePrefix + (r.text_name || "-");

        return `<tr class="${cls}">
            <td>${rank}</td>
            <td>${esc(r.nickname || "익명")}</td>
            <td>${esc(displayName)}</td>
            <td class="cpm-val">${r.cpm} 타/분</td>
            <td class="acc-val">${(r.accuracy || 0).toFixed(1)}%</td>
            <td class="hide-mobile">${fmtTime(r.elapsed || 0)}</td>
            <td class="hide-mobile">${r.backspace_count ?? 0}회</td>
            <td>${badges}</td>
        </tr>`;
    }).join("");
}

// ══════════════════════════════════════════════════════════
// 공유 글귀
// ══════════════════════════════════════════════════════════

async function loadSharedTexts() {
    const grid = $("#shared-grid");
    grid.innerHTML = `<div class="loading-msg"><span class="spinner"></span> 불러오는 중...</div>`;

    // 로그인 시 공유 폼 표시
    const shareForm = $("#share-form-wrap");
    shareForm.style.display = currentUser ? "block" : "none";

    try {
        const snap = await get(ref(db, "shared_texts"));
        const items = [];
        snap.forEach(child => {
            const val = child.val();
            val._key = child.key;
            items.push(val);
        });
        items.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));

        if (items.length === 0) {
            grid.innerHTML = `<div class="empty-msg" style="grid-column:1/-1; text-align:center;">
                공유된 글귀가 없습니다.<br>첫 번째로 글귀를 공유해 보세요!</div>`;
            return;
        }

        grid.innerHTML = items.map((s, idx) => {
            // data 속성에 저장하여 안전하게 전달
            return `<div class="shared-card">
                <div class="card-title" id="stitle-${idx}">${esc(s.title)}</div>
                <div class="card-body" id="sbody-${idx}">${esc(s.body)}</div>
                <div class="card-meta">
                    <span class="author">${esc(s.nickname || "익명")}</span>
                    <span>${fmtDate(s.timestamp)}</span>
                </div>
                <div class="card-actions">
                    <button class="btn-copy" onclick="downloadTxt('stitle-${idx}', 'sbody-${idx}')">
                        .txt 다운로드
                    </button>
                </div>
            </div>`;
        }).join("");
    } catch {
        grid.innerHTML = `<div class="empty-msg">글귀를 불러올 수 없습니다.</div>`;
    }
}

async function handleShare(e) {
    e.preventDefault();
    if (!currentUser) { navigate("login"); return; }

    const title = $("#share-title").value.trim();
    const body  = $("#share-body").value.trim();
    if (!title || !body) return toast("제목과 내용을 모두 입력하세요", "error");

    try {
        await push(ref(db, "shared_texts"), {
            uid: currentUser.uid,
            nickname,
            title,
            body,
            timestamp: Math.floor(Date.now() / 1000),
        });
        toast("글귀가 공유되었습니다!");
        $("#share-title").value = "";
        $("#share-body").value  = "";
        loadSharedTexts();
    } catch {
        toast("공유 중 오류가 발생했습니다", "error");
    }
}

// ── .txt 다운로드 (커스텀 글귀 양식) ───────────────────
window.downloadTxt = function(titleId, bodyId) {
    const title = document.getElementById(titleId)?.textContent || "글귀";
    const body  = document.getElementById(bodyId)?.textContent || "";
    const content = `@${title}\n${body}\n`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `${title}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// ── 클립보드 복사 ──────────────────────────────────────
window.copyFromEl = function(btn, elId) {
    const text = document.getElementById(elId)?.textContent || "";
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = "복사됨!";
        btn.classList.add("copied");
        setTimeout(() => {
            btn.textContent = "복사하기";
            btn.classList.remove("copied");
        }, 2000);
    });
};

// ── HTML 이스케이프 ────────────────────────────────────
function esc(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
}

// ══════════════════════════════════════════════════════════
// 별 배경 캔버스
// ══════════════════════════════════════════════════════════

function initStars() {
    const canvas = $("#stars-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let W, H;

    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    const stars = Array.from({length: 120}, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.5 + 0.3,
        speed: Math.random() * 0.4 + 0.1,
        alpha: Math.random() * 0.5 + 0.2,
    }));

    function draw() {
        ctx.clearRect(0, 0, W, H);
        for (const s of stars) {
            s.y += s.speed;
            if (s.y > H) { s.y = -2; s.x = Math.random() * W; }
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(180,195,240,${s.alpha})`;
            ctx.fill();
        }
        requestAnimationFrame(draw);
    }
    draw();
}

// ══════════════════════════════════════════════════════════
// 탭 전환
// ══════════════════════════════════════════════════════════

window.switchTab = function(name) {
    $$(".tab-content").forEach(el => el.classList.remove("active"));
    $$(".tab-btn").forEach(el => el.classList.remove("active"));
    $(`#tab-${name}`).classList.add("active");
    event.target.classList.add("active");
    // 랭킹 탭이 아니면 도전 모드 테마 해제
    if (name !== "ranking") {
        document.body.classList.remove("challenge-theme");
    } else if (rankMode === "challenge") {
        document.body.classList.add("challenge-theme");
    }
};

// ══════════════════════════════════════════════════════════
// 초기화
// ══════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    initStars();

    // 네비게이션 이벤트
    $$("#nav-login").forEach(el => el.addEventListener("click",  () => navigate("login")));
    $$("#nav-signup").forEach(el => el.addEventListener("click", () => navigate("signup")));
    $("#nav-profile")?.addEventListener("click", openProfile);
    $("#nav-logout")?.addEventListener("click",  handleLogout);
    $("#nav-logo")?.addEventListener("click", () => navigate("main"));

    // 폼 이벤트
    $("#login-form")?.addEventListener("submit",   handleLogin);
    $("#signup-form")?.addEventListener("submit",  handleSignup);
    $("#profile-form")?.addEventListener("submit", handleProfileSave);
    $("#share-form")?.addEventListener("submit",   handleShare);

    // 폼 내 링크
    $("#link-to-signup")?.addEventListener("click", () => navigate("signup"));
    $("#link-to-login")?.addEventListener("click",  () => navigate("login"));
    $("#link-to-main")?.addEventListener("click",   () => navigate("main"));

    // 초기 페이지
    navigate("main");

    // 30초마다 자동 갱신
    setInterval(() => {
        loadRanking();
        loadSharedTexts();
    }, 30000);
});
