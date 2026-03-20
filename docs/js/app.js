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

window.loadRanking = loadRanking;

async function loadRanking() {
    const tbody = $("#ranking-body");
    tbody.innerHTML = `<tr><td colspan="8" class="loading-msg">
        <span class="spinner"></span> 랭킹 불러오는 중...</td></tr>`;

    try {
        const snap = await get(ref(db, "records"));
        const raw = [];
        snap.forEach(child => raw.push(child.val()));

        // 같은 uid + 같은 text_name 중 CPM 최고 기록만 유지
        const bestMap = {};
        for (const r of raw) {
            const key = `${r.uid || ""}__${r.text_name || ""}`;
            if (!bestMap[key] || (r.cpm || 0) > (bestMap[key].cpm || 0)) {
                bestMap[key] = r;
            }
        }
        allRecords = Object.values(bestMap);
        allRecords.sort((a, b) => (b.cpm || 0) - (a.cpm || 0));

        // 필터 드롭다운 갱신
        buildFilterOptions();
        renderRanking();
    } catch (err) {
        console.error("랭킹 로드 에러:", err);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">
            랭킹을 불러올 수 없습니다.</td></tr>`;
    }
}

function buildFilterOptions() {
    const select = $("#ranking-filter");
    const current = select.value;
    const textNames = [...new Set(allRecords.map(r => r.text_name || "-"))].sort();

    select.innerHTML = `<option value="__all__">전체</option>`;
    for (const name of textNames) {
        const r = allRecords.find(x => (x.text_name || "-") === name);
        const prefix = r && r.is_custom ? "[커스텀] " : "";
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = prefix + name;
        select.appendChild(opt);
    }
    select.value = current || "__all__";
}

window.filterRanking = function() { renderRanking(); };

function renderRanking() {
    const tbody = $("#ranking-body");
    const filter = $("#ranking-filter").value;

    let rows = allRecords;
    if (filter !== "__all__") {
        rows = rows.filter(r => (r.text_name || "-") === filter);
    }

    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-msg">
            아직 기록이 없습니다.<br>게임에서 연습을 완료해 보세요!</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map((r, i) => {
        const rank = i + 1;
        const cls  = rank <= 3 ? `rank-${rank}` : "";
        let badges = "";
        if (r.challenge_mode) badges += `<span class="badge badge-challenge">도전</span>`;
        if (r.full_combo)     badges += `<span class="badge badge-fullcombo">FULL COMBO</span>`;

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
