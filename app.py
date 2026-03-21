# app.py — 호랑이 타자연습 메인 애플리케이션
# pygame 2.0+ 필요 (한글 IME 입력 지원)

import pygame
import sys
import time
import math
import random
import os
import threading
import webbrowser
import jamo as _jamo

from texts import TEXTS, TEXTS_KO, TEXTS_EN
from auth import signup, login, get_nickname, set_nickname, save_record, share_custom_text

# ─── 복합 자모 → 키보드 입력 단위 분해 ──────────────────────────
COMPOUND_VOWELS = {
    'ㅘ': ('ㅗ', 'ㅏ'), 'ㅙ': ('ㅗ', 'ㅐ'), 'ㅚ': ('ㅗ', 'ㅣ'),
    'ㅝ': ('ㅜ', 'ㅓ'), 'ㅞ': ('ㅜ', 'ㅔ'), 'ㅟ': ('ㅜ', 'ㅣ'),
    'ㅢ': ('ㅡ', 'ㅣ'),
}
COMPOUND_FINALS = {
    'ㄳ': ('ㄱ', 'ㅅ'), 'ㄵ': ('ㄴ', 'ㅈ'), 'ㄶ': ('ㄴ', 'ㅎ'),
    'ㄺ': ('ㄹ', 'ㄱ'), 'ㄻ': ('ㄹ', 'ㅁ'), 'ㄼ': ('ㄹ', 'ㅂ'),
    'ㄽ': ('ㄹ', 'ㅅ'), 'ㄾ': ('ㄹ', 'ㅌ'), 'ㄿ': ('ㄹ', 'ㅍ'),
    'ㅀ': ('ㄹ', 'ㅎ'), 'ㅄ': ('ㅂ', 'ㅅ'),
}

# ─── 색상 팔레트 ────────────────────────────────────────────────
BG          = (10,  12,  22)
PANEL       = (18,  22,  40)
PANEL2      = (22,  28,  52)
BORDER      = (38,  48,  80)
ACCENT      = (88, 128, 255)
ACCENT_DIM  = (52,  76, 180)
CORRECT     = (68, 200, 112)
ERROR       = (215,  72,  72)
ERROR_BG    = (70,  16,  16)
UNTYPED     = (125, 130, 158)
CURSOR_BG   = (88, 128, 255)
CURSOR_FG   = (255, 255, 255)
COMPOSING   = (255, 218,  72)
COMP_BG     = (55,  48,  12)
WHITE       = (235, 242, 255)
GRAY        = (80,  88, 118)
DARK_GRAY   = (40,  48,  72)
STAT_VAL    = (190, 208, 255)
STAT_LBL    = (98, 110, 148)
BTN_BG      = (24,  32,  58)
BTN_HOVER   = (42,  56, 100)
BTN_TEXT    = (180, 195, 238)
PROG_BG     = (24,  30,  52)
PROG_FG     = (68, 200, 112)
TITLE_COL   = (200, 215, 255)
STAR_COL    = (180, 195, 240)

# ─── 콤보 색상 (100단위 티어) ─────────────────────────────────────
COMBO_BGS = [
    (10,  12,  22),     # 0-99     기본
    (12,  18,  38),     # 100-199  파랑 틴트
    (22,  12,  36),     # 200-299  보라 틴트
    (32,  16,  14),     # 300-399  붉은 틴트
    (12,  28,  20),     # 400-499  초록 틴트
    (34,  26,   8),     # 500+     금색 틴트
]
COMBO_COLORS = [
    (190, 208, 255),    # 0-99     기본
    (100, 210, 255),    # 100-199  시안
    (190, 140, 255),    # 200-299  보라
    (255, 150, 100),    # 300-399  오렌지
    (100, 255, 170),    # 400-499  민트
    (255, 220,  80),    # 500+     골드
]
COMBO_LABEL_COL = (70, 78, 110)

# ─── 도전 모드 색상 팔레트 ──────────────────────────────────────
CH_BG          = (22,   8,   8)
CH_PANEL       = (40,  14,  14)
CH_PANEL2      = (52,  18,  18)
CH_BORDER      = (80,  30,  30)
CH_ACCENT      = (255,  72,  72)
CH_ACCENT_DIM  = (180,  42,  42)
CH_CORRECT     = (255, 100, 100)
CH_UNTYPED     = (158, 110, 110)
CH_CURSOR_BG   = (255,  72,  72)
CH_WHITE       = (255, 230, 230)
CH_GRAY        = (118,  70,  70)
CH_DARK_GRAY   = (72,  36,  36)
CH_STAT_VAL    = (255, 180, 180)
CH_STAT_LBL    = (148,  80,  80)
CH_BTN_BG      = (58,  18,  18)
CH_BTN_HOVER   = (100,  32,  32)
CH_BTN_TEXT    = (238, 160, 160)
CH_PROG_BG     = (52,  18,  18)
CH_PROG_FG     = (255, 100, 100)
CH_TITLE_COL   = (255, 200, 200)
CH_STAR_COL    = (240, 160, 160)
CH_COMBO_BGS = [
    (22,   8,   8),
    (38,  12,  12),
    (36,  12,  22),
    (40,  20,  10),
    (20,  28,  16),
    (40,  30,   8),
]


SETTINGS_TEST_TEXT = "다람쥐 헌 쳇바퀴에 타고파\nThe quick brown fox jumps over the lazy dog\n1234567890"

COLOR_PALETTE = [
    (255, 255, 255), (200, 200, 200), (150, 150, 150), (100, 100, 100),
    (255,  72,  72), (255, 150, 100), (255, 218,  72), (200, 255,  72),
    (68,  200, 112), (72,  220, 200), (100, 180, 255), (88,  128, 255),
    (150, 100, 255), (200, 100, 255), (255, 100, 200), (125, 130, 158),
]

RESOLUTION_OPTIONS = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080)]
FPS_OPTIONS = [60, 120, 144, 240]


class TypingApp:
    VERSION = "1.0.4"
    GITHUB_REPO = "Recorder001/TigerType"

    W = 1280
    H = 720
    FPS = 240

    # 기준 해상도 (레이아웃 스케일링 기준)
    BASE_W    = 1280
    BASE_H    = 720

    # 텍스트 영역 레이아웃 (기준 해상도 기준값 — _update_layout_scale 에서 재계산)
    TEXT_X    = 80
    TEXT_Y    = 210   # 상단 바 + 진행바 + 콤보 아래
    TEXT_W    = 1120
    LINE_H    = 44
    BOT_H     = 46    # 하단 힌트 바

    COMBO_TIMEOUT  = 1.0   # 콤보 유지 제한 시간(초)
    COMBO_ANIM_DUR = 0.25  # 콤보 애니메이션 지속(초)

    def __init__(self):
        self.disp  = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("호랑이 타자연습")
        self.clock = pygame.time.Clock()

        # ─── 효과음 로드 ───
        pygame.mixer.init()
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self.type_sounds = []
        for i in range(1, 31):
            path = os.path.join(base, 'assets', 'sounds', f'typer{i:02d}.mp3')
            if os.path.exists(path):
                self.type_sounds.append(pygame.mixer.Sound(path))

        def _load_sfx(name):
            p = os.path.join(base, 'assets', 'sounds', name)
            return pygame.mixer.Sound(p) if os.path.exists(p) else None
        self.snd_line_clear     = _load_sfx('LineClear.mp3')
        self.snd_wrong_input    = _load_sfx('WrongInput.mp3')
        self.snd_fullcombo_norm = _load_sfx('FullComboNormal.mp3')
        self.snd_fullcombo_ch   = _load_sfx('FullComboChall.mp3')

        self._update_layout_scale()
        self._setup_fonts()
        self._init_stars()
        self._reset()
        self.state      = 'login'
        self.mouse      = (0, 0)
        self.btn_rects  = {}

        # ─── 로그인/회원가입 상태 ───
        self.auth_user       = None     # 로그인된 사용자 정보
        self.auth_email      = ''       # 입력 중인 이메일
        self.auth_password   = ''       # 입력 중인 비밀번호
        self.auth_focus      = 'email'  # 'email' 또는 'password'
        self.auth_msg        = ''       # 상태 메시지 (오류/성공)
        self.auth_msg_color  = ERROR    # 메시지 색상
        self.auth_show_pw    = False    # 비밀번호 표시 여부
        self.nickname        = ''       # 사용자 닉네임
        self.nickname_edit   = ''       # 닉네임 편집 버퍼
        self.nickname_editing = False   # 닉네임 편집 모드

        self.challenge_mode = False
        # 사용자 설정
        self.cfg = {
            'resolution': (self.W, self.H),
            'fps': self.FPS,
            'font_size': 24,
            'master_volume': 100,
            'type_volume': 100,
            'untyped_color': list(UNTYPED),
            'correct_color': [255, 255, 255],
            'error_color': list(ERROR),
            'cursor_color': [255, 218, 72],
            'particles_enabled': True,
            'particle_color': [255, 255, 255],
        }
        self.cfg_dropdown = None   # 열린 드롭다운 키
        self.cfg_colorpick = None  # 열린 컬러 피커 키
        self.st = None             # 설정 테스트 타이핑 상태
        self.custom_texts = {}     # 커스텀 글귀 {이름: 본문}
        self._build_fade_overlays()
        pygame.key.start_text_input()

        # ─── 업데이트 체크 ───
        self.update_available = None   # None=체크중, False=최신, str=새 버전 태그
        self.update_url = None
        self._check_update_async()

        self._slider_dragging = None   # 드래그 중인 슬라이더 키

    def c(self, normal, challenge):
        """도전 모드에 따라 색상 반환"""
        return challenge if self.challenge_mode else normal

    def _update_layout_scale(self):
        """해상도 변경 시 레이아웃 상수를 기준 해상도(1280×720) 비율로 재계산"""
        sx = self.W / self.BASE_W
        sy = self.H / self.BASE_H
        self.TEXT_X  = int(80  * sx)
        self.TEXT_Y  = int(210 * sy)
        self.TEXT_W  = int(1120 * sx)
        self.LINE_H  = int(44 * sy)
        self.BOT_H   = int(46 * sy)

    def _build_fade_overlays(self):
        """텍스트 영역 위/아래 페이드 오버레이 캐시 생성"""
        area_h     = self.H - self.TEXT_Y - self.BOT_H
        center_y   = (area_h - self.LINE_H) / 2
        fade_range = area_h / 2

        # 위쪽 (중앙 위 → 상단으로 갈수록 어두움)
        top_h = int(center_y)
        self._fade_top = pygame.Surface((self.W, max(top_h, 1)), pygame.SRCALPHA)
        for row in range(top_h):
            dist  = top_h - row
            alpha = min(220, int(220 * dist / fade_range))
            pygame.draw.line(self._fade_top, (0, 0, 0, alpha), (0, row), (self.W, row))
        self._fade_top_h = top_h

        # 아래쪽 (중앙 아래 → 하단으로 갈수록 어두움)
        bot_h = area_h - int(center_y + self.LINE_H)
        self._fade_bot = pygame.Surface((self.W, max(bot_h, 1)), pygame.SRCALPHA)
        for row in range(bot_h):
            alpha = min(220, int(220 * row / fade_range))
            pygame.draw.line(self._fade_bot, (0, 0, 0, alpha), (0, row), (self.W, row))
        self._fade_bot_h = bot_h
        self._fade_bot_start = int(self.TEXT_Y + center_y + self.LINE_H)

    # ─── 초기화 ───────────────────────────────────────────────
    def _setup_fonts(self):
        available = set(pygame.font.get_fonts())
        candidates = [
            "malgungothic", "malgunbd", "malgun",
            "gulim", "gulimche", "dotum", "dotumche",
            "batang", "batangche",
            "nanumsquareroundbold", "nanumgothicbold", "nanumgothic",
        ]
        chosen = next((f for f in candidates if f in available), None)
        s = min(self.W / self.BASE_W, self.H / self.BASE_H)

        def sf(size, bold=False):
            return pygame.font.SysFont(chosen, max(10, int(size * s)), bold=bold)

        self.F = {
            'title'     : sf(52, True),
            'heading'   : sf(28, True),
            'subhead'   : sf(20),
            'text'      : sf(24),
            'small'     : sf(17),
            'stat_v'    : sf(34, True),
            'stat_l'    : sf(15),
            'btn'       : sf(21, True),
            'btn_sm'    : sf(17),
            'result_big': sf(64, True),
            'result_lbl': sf(22),
            'result_sub': sf(17),
            'combo_num' : sf(38, True),
            'combo_lbl' : sf(13),
        }

    def _init_stars(self):
        """메뉴 배경용 떨어지는 별 파티클"""
        rng = random.Random(42)
        self.stars = []
        for _ in range(180):
            self.stars.append(self._make_star(rng, init=True))
        self.menu_scroll = 0   # 메뉴 리스트 스크롤
        if not hasattr(self, 'menu_tab'):
            self.menu_tab = '한글'  # '한글' 또는 '영문'

    def _make_star(self, rng=None, init=False):
        r = rng or random
        return {
            'x': r.uniform(0, self.W),
            'y': r.uniform(0, self.H) if init else r.uniform(-40, -5),
            'vy': r.uniform(15, 60),
            'vx': r.uniform(-8, 8),
            'r': r.uniform(0.6, 2.2),
            'phase': r.uniform(0, 6.28),
            'speed': r.uniform(0.8, 2.5),
            'alpha': r.uniform(0.3, 1.0),
        }

    @staticmethod
    def _decompose(text: str) -> list:
        """텍스트를 키보드 입력 단위 자모 리스트로 분해"""
        result = []
        for ch in text:
            if 0xAC00 <= ord(ch) <= 0xD7A3:
                for j in _jamo.j2hcj(_jamo.h2j(ch)):
                    if j in COMPOUND_VOWELS:
                        result.extend(COMPOUND_VOWELS[j])
                    elif j in COMPOUND_FINALS:
                        result.extend(COMPOUND_FINALS[j])
                    else:
                        result.append(j)
            else:
                result.append(ch)
        return result

    def _play_type_sound(self):
        if self.type_sounds:
            vol = (self.cfg['master_volume'] / 100) * (self.cfg['type_volume'] / 100)
            snd = random.choice(self.type_sounds)
            snd.set_volume(vol)
            snd.play()

    def _play_sfx(self, snd):
        if snd:
            snd.set_volume(self.cfg['master_volume'] / 100)
            snd.play()

    # ─── 업데이트 체크 ──────────────────────────────────────────
    def _check_update_async(self):
        def _worker():
            try:
                import urllib.request, json
                url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
                req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                tag = data.get("tag_name", "").lstrip("vV")
                if tag and tag != self.VERSION:
                    self.update_available = tag
                    self.update_url = data.get("html_url",
                        f"https://github.com/{self.GITHUB_REPO}/releases/latest")
                else:
                    self.update_available = False
            except Exception:
                self.update_available = False
        threading.Thread(target=_worker, daemon=True).start()

    def _reset(self):
        self.name             = ""
        self.target           = ""
        self.typed            = ""
        self.composing        = ""
        self.start_time       = None
        self.end_time         = None
        self.scroll           = 0
        self.layout           = []
        self.layout_h         = 0
        self._stanza_newlines = set()   # 연 구분 위치의 '\n' 인덱스
        # 자모
        self.target_jamo      = []
        self.typed_jamo       = []
        self.char_jamo_ranges = []      # [(start, end), ...] 글자별 자모 범위
        # 콤보
        self.combo            = 0
        self.max_combo        = 0
        self.last_input_time  = 0.0
        self.combo_anim_start = 0.0
        self.combo_break_time = 0.0     # 콤보 끊긴 시점
        self.backspace_count  = 0       # 백스페이스 횟수
        # 조합 중 자모 추적
        self.composing_jamo_processed = 0   # 이펙트 발동 완료된 조합 자모 수
        self.composing_correct        = True
        # 커서 애니메이션 (ease-out)
        self.cursor_x         = 0.0
        self.cursor_y         = 0.0
        self.cursor_target_x  = 0.0
        self.cursor_target_y  = 0.0
        self.cursor_w         = 0.0
        self.cursor_inited    = False
        # 스크롤 ease-out
        self.scroll_target    = 0.0
        # 파티클 & 셰이크
        self.particles        = []
        self.shake_start      = 0.0
        self.shake_intensity  = 0.0

    # ─── 텍스트 준비 ──────────────────────────────────────────
    def _load_text(self, raw: str) -> str:
        """원문의 줄바꿈을 유지한 타이핑용 문자열 생성
        비어 있는 줄(연 구분)은 제거하되, 해당 위치의 '\\n'을
        _stanza_newlines 에 기록해 레이아웃에서 여백을 추가한다."""
        lines = raw.split('\n')
        non_empty = []
        gap_before = set()      # 연 구분이 있는 줄 인덱스
        had_empty = False

        for line in lines:
            s = line.strip()
            if s:
                if had_empty and non_empty:
                    gap_before.add(len(non_empty))
                non_empty.append(s)
                had_empty = False
            else:
                had_empty = True

        text = '\n'.join(non_empty)

        # 연 구분 '\n' 문자의 인덱스 계산
        self._stanza_newlines = set()
        pos = 0
        for i, line in enumerate(non_empty[:-1]):
            pos += len(line)        # pos → 이 줄 뒤의 '\n' 위치
            if (i + 1) in gap_before:
                self._stanza_newlines.add(pos)
            pos += 1                # '\n' 건너뛰기

        return text

    def _start_text(self, name: str):
        self._reset()
        self.name   = name
        all_texts = {**TEXTS, **self.custom_texts}
        self.target = self._load_text(all_texts[name])
        # 자모 매핑 구축
        self.target_jamo = self._decompose(self.target)
        pos = 0
        for ch in self.target:
            n = len(self._decompose(ch))
            self.char_jamo_ranges.append((pos, pos + n))
            pos += n
        self._build_layout()
        self._update_scroll()
        self.scroll = self.scroll_target   # 초기 위치 즉시 적용
        self.state  = 'typing'

    def _open_custom_file(self):
        """tkinter 파일 다이얼로그로 커스텀 글귀 txt 파일 로드"""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(
            title="커스텀 글귀 파일 선택",
            filetypes=[("텍스트 파일", "*.txt")],
        )
        root.destroy()
        if not path:
            return
        self._parse_custom_file(path)

    def _parse_custom_file(self, path):
        """커스텀 글귀 파일 파싱 — @제목 구분자 형식"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return
        # @제목 으로 분리
        entries = {}
        current_title = None
        lines_buf = []
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('@'):
                # 이전 항목 저장
                if current_title and lines_buf:
                    body = '\n'.join(lines_buf).strip()
                    if body:
                        entries[current_title] = body
                current_title = stripped[1:].strip()
                lines_buf = []
            else:
                lines_buf.append(line)
        # 마지막 항목 저장
        if current_title and lines_buf:
            body = '\n'.join(lines_buf).strip()
            if body:
                entries[current_title] = body
        # @가 하나도 없으면 파일명을 제목으로 사용
        if not entries:
            body = content.strip()
            if body:
                fname = os.path.splitext(os.path.basename(path))[0]
                entries[f"📄 {fname}"] = body
        self.custom_texts.update(entries)

    def _build_layout(self):
        """각 문자의 화면 좌표를 미리 계산 (줄바꿈 반영)"""
        f  = self.F['text']
        layout = []
        x, y = 0, 0

        for i, ch in enumerate(self.target):
            if ch == '\n':
                # 줄바꿈 위치만 기록 (화면 표시 없음)
                layout.append({
                    'i': i, 'ch': '', 'x': x, 'y': y, 'w': 0,
                    'newline': True,
                })
                y += self.LINE_H
                if i in self._stanza_newlines:
                    y += self.LINE_H * 2 // 3   # 연 구분 여백
                x = 0
            else:
                cw = f.size(ch)[0]
                if x + cw > self.TEXT_W and x > 0:
                    y += self.LINE_H
                    x  = 0
                layout.append({
                    'i': i, 'ch': ch, 'x': x, 'y': y, 'w': cw,
                    'newline': False,
                })
                x += cw

        self.layout   = layout
        self.layout_h = y + self.LINE_H

    # ─── 통계 (자모 기반) ──────────────────────────────────────
    @property
    def elapsed(self) -> float:
        if not self.start_time:
            return 0.0
        return (self.end_time or time.time()) - self.start_time

    @property
    def cpm(self) -> int:
        """분당 타수 (자모 기준)"""
        e = self.elapsed
        if e < 0.5:
            return 0
        return int(len(self.typed_jamo) / e * 60)

    @property
    def accuracy(self) -> float:
        if not self.typed_jamo:
            return 100.0
        correct = sum(
            1 for i in range(len(self.typed_jamo))
            if self.typed_jamo[i] == self.target_jamo[i]
        )
        return correct / len(self.typed_jamo) * 100

    @property
    def progress(self) -> float:
        if not self.target_jamo:
            return 0.0
        return min(len(self.typed_jamo) / len(self.target_jamo) * 100, 100.0)

    # ─── 입력 처리 (자모 기반) ─────────────────────────────────
    def _char_jamo_correct(self, char_idx: int) -> bool:
        """char_idx 글자의 자모가 모두 정타인지"""
        start, end = self.char_jamo_ranges[char_idx]
        return all(
            j < len(self.typed_jamo) and self.typed_jamo[j] == self.target_jamo[j]
            for j in range(start, end)
        )

    # ─── 조합 중 자모 실시간 추적 ──────────────────────────────
    def _update_composing(self, text: str):
        """TEXTEDITING — 조합 중 자모를 실시간 추적, 새 자모마다 이펙트 발동"""

        # 도전 모드: 조합 중 백스페이스(자모 줄어듦 / 조합 취소) 무시
        if self.challenge_mode and self.composing:
            if not text:
                return  # 조합 취소 무시
            new_jamo = self._decompose(text)
            if len(new_jamo) < self.composing_jamo_processed:
                return  # 자모 줄어듦 무시

        self.composing = text

        if not text:
            self.composing_jamo_processed = 0
            self.composing_correct = True
            return
        if not self.target:
            return
        if not self.start_time:
            self.start_time = time.time()

        now = time.time()
        comp_jamo = self._decompose(text)
        new_count = len(comp_jamo)

        if new_count <= self.composing_jamo_processed:
            # 백스페이스 등으로 줄어듦 — processed 조정, 정타 재평가
            self.composing_jamo_processed = new_count
            self.composing_correct = True
            base = len(self.typed_jamo)
            for k in range(new_count):
                pos = base + k
                if pos < len(self.target_jamo) \
                        and comp_jamo[k] != self.target_jamo[pos]:
                    self.composing_correct = False
                    break
            return

        # 새 자모 추가됨 — 이펙트 발동
        char_idx = len(self.typed)
        if char_idx >= len(self.target):
            self.composing_jamo_processed = new_count
            return

        base = len(self.typed_jamo)
        first_new = True

        for k in range(self.composing_jamo_processed, new_count):
            pos = base + k
            if pos >= len(self.target_jamo):
                break

            self._play_type_sound()
            jamo_correct = (comp_jamo[k] == self.target_jamo[pos])

            # 콤보 갱신
            if not jamo_correct:
                self._play_sfx(self.snd_wrong_input)
                self.combo = 0
                self.combo_break_time = now
                self.composing_correct = False
            elif (first_new and self.last_input_time > 0
                  and (now - self.last_input_time) > self.COMBO_TIMEOUT):
                self.combo = 1
            else:
                self.combo += 1

            self.combo_anim_start = now
            self.max_combo = max(self.max_combo, self.combo)
            first_new = False

            # 파티클 + 셰이크 (정타 시)
            if jamo_correct:
                if self.cfg['particles_enabled']:
                    self._spawn_jamo_particles(char_idx)
                self._trigger_shake(4)

            self.last_input_time = now

        self.composing_jamo_processed = new_count

    # ─── 글자 커밋 ──────────────────────────────────────────────
    def _add_input(self, text: str):
        """TEXTINPUT / Enter — 완성 글자를 커밋, 조합 중 미처리 자모만 이펙트"""
        if not self.target:
            return
        if not self.start_time:
            self.start_time = time.time()

        now = time.time()
        first_new = (self.composing_jamo_processed == 0)

        for ch in text:
            char_idx = len(self.typed)
            if char_idx >= len(self.target):
                break

            user_jamo = self._decompose(ch)
            start, end = self.char_jamo_ranges[char_idx]
            target_n = end - start

            # 이 글자에서 조합 중 이미 이펙트 발동된 자모 수
            already = min(self.composing_jamo_processed, target_n)

            for k in range(target_n):
                if len(self.typed_jamo) >= len(self.target_jamo):
                    break
                uj = user_jamo[k] if k < len(user_jamo) else '\x00'
                jamo_correct = (uj == self.target_jamo[len(self.typed_jamo)])
                self.typed_jamo.append(uj)

                if k < already:
                    continue      # 조합 중 이미 이펙트 발동됨

                self._play_type_sound()
                # 콤보 갱신
                if not jamo_correct:
                    self._play_sfx(self.snd_wrong_input)
                    self.combo = 0
                    self.combo_break_time = now
                elif (first_new and self.last_input_time > 0
                      and (now - self.last_input_time) > self.COMBO_TIMEOUT):
                    self.combo = 1
                else:
                    self.combo += 1
                self.combo_anim_start = now
                self.max_combo = max(self.max_combo, self.combo)
                first_new = False

                # 파티클 + 셰이크
                if jamo_correct and ch != '\n':
                    if self.cfg['particles_enabled']:
                        self._spawn_jamo_particles(char_idx)
                    self._trigger_shake(4)

            # stolen jamo (다음 글자로 넘어가는 자모)
            self.composing_jamo_processed = max(0,
                                                self.composing_jamo_processed - target_n)
            self.typed += ch

            # 줄바꿈 시
            if ch == '\n':
                self._play_sfx(self.snd_line_clear)
                if self._is_line_perfect(char_idx):
                    if self.cfg['particles_enabled']:
                        self._spawn_line_particles(char_idx)
                    self._trigger_shake(10)

        self.composing = ""
        self.composing_correct = True
        self.last_input_time = now

        if len(self.typed_jamo) >= len(self.target_jamo):
            self.end_time = time.time()
            self._save_record_to_db()
            if self.combo_break_time == 0.0:
                # 풀 콤보 — 연출 상태 진입
                self.state = 'fullcombo'
                self.fc_start = time.time()
                self._spawn_fullcombo_particles()
                self._trigger_shake(30)
                if self.challenge_mode:
                    self._play_sfx(self.snd_fullcombo_ch)
                else:
                    self._play_sfx(self.snd_fullcombo_norm)
            else:
                self.result_time = time.time()
                self.state = 'result'

        self._update_scroll()

    def _backspace(self):
        if self.typed:
            self._play_type_sound()
            self.backspace_count += 1
            char_idx = len(self.typed) - 1
            start, end = self.char_jamo_ranges[char_idx]
            n = end - start
            self.typed = self.typed[:-1]
            self.typed_jamo = self.typed_jamo[:-n]
            self._update_scroll()

    def _update_scroll(self):
        """현재 타겟 라인을 텍스트 영역 중앙에 배치"""
        cidx = len(self.typed)
        if not self.layout:
            return
        cy = self.layout[min(cidx, len(self.layout) - 1)]['y']
        area_h = self.H - self.TEXT_Y - self.BOT_H
        # 타겟 라인이 영역 정중앙에 오도록 (음수도 허용)
        self.scroll_target = cy - (area_h - self.LINE_H) / 2

    def _is_line_perfect(self, newline_char_idx: int) -> bool:
        """newline_char_idx 앞 라인의 모든 자모가 정타인지 확인"""
        line_start = 0
        for j in range(newline_char_idx - 1, -1, -1):
            if self.target[j] == '\n':
                line_start = j + 1
                break
        for k in range(line_start, newline_char_idx):
            if not self._char_jamo_correct(k):
                return False
        return True

    # ─── 파티클 & 셰이크 ─────────────────────────────────────
    SHAKE_DUR = 0.25        # 셰이크 지속(초)

    def _trigger_shake(self, intensity: float):
        self.shake_start     = time.time()
        self.shake_intensity = intensity

    def _get_shake_offset(self) -> tuple:
        if self.shake_start <= 0:
            return (0, 0)
        t = (time.time() - self.shake_start) / self.SHAKE_DUR
        if t >= 1.0:
            self.shake_start = 0.0
            return (0, 0)
        amp = self.shake_intensity * (1.0 - t)
        ox  = int(random.uniform(-amp, amp))
        oy  = int(random.uniform(-amp, amp))
        return (ox, oy)

    def _spawn_char_particles(self, char_idx: int):
        """글자 정타 시 주변에서 입자 폭발"""
        for item in self.layout:
            if item['i'] == char_idx:
                break
        else:
            return

        sx = self.TEXT_X + item['x'] + item['w'] / 2
        sy = self.TEXT_Y + item['y'] + self.LINE_H / 2 - self.scroll
        pcol = tuple(self.cfg['particle_color'])

        for _ in range(6):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(60, 200)
            life  = random.uniform(0.25, 0.5)
            size  = random.uniform(2.5, 5.5)
            self.particles.append({
                'x': sx + random.uniform(-6, 6),
                'y': sy + random.uniform(-6, 6),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 50,
                'life': life,
                'max_life': life,
                'size': size,
                'color': pcol,
            })

    def _spawn_jamo_particles(self, char_idx: int):
        """자모 정타 시 파티클 (글자당이 아닌 자모당)"""
        for item in self.layout:
            if item['i'] == char_idx:
                break
        else:
            return

        sx = self.TEXT_X + item['x'] + item['w'] / 2
        sy = self.TEXT_Y + item['y'] + self.LINE_H / 2 - self.scroll
        pcol = tuple(self.cfg['particle_color'])

        for _ in range(3):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(60, 200)
            life  = random.uniform(0.25, 0.5)
            size  = random.uniform(2.5, 5.5)
            self.particles.append({
                'x': sx + random.uniform(-6, 6),
                'y': sy + random.uniform(-6, 6),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 50,
                'life': life,
                'max_life': life,
                'size': size,
                'color': pcol,
            })

    def _spawn_line_particles(self, newline_idx: int):
        """줄바꿈 시 완료된 라인 전체에서 대량 파티클 폭발"""
        line_start = 0
        for j in range(newline_idx - 1, -1, -1):
            if self.target[j] == '\n':
                line_start = j + 1
                break

        pcol = tuple(self.cfg['particle_color'])
        for item in self.layout:
            idx = item['i']
            if idx < line_start or idx >= newline_idx:
                continue
            if item.get('newline'):
                continue

            cx = self.TEXT_X + item['x'] + item['w'] / 2
            cy = self.TEXT_Y + item['y'] + self.LINE_H / 2 - self.scroll

            # 글자당 8개 입자
            for _ in range(8):
                angle = random.uniform(-math.pi, math.pi)
                speed = random.uniform(100, 400)
                life  = random.uniform(0.4, 0.9)
                size  = random.uniform(2.5, 6.0)
                self.particles.append({
                    'x': cx + random.uniform(-6, 6),
                    'y': cy + random.uniform(-6, 6),
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - 120,
                    'life': life,
                    'max_life': life,
                    'size': size,
                    'color': pcol,
                })

    def _update_particles(self, dt: float):
        alive = []
        for p in self.particles:
            p['life'] -= dt
            if p['life'] <= 0:
                continue
            p['x']  += p['vx'] * dt
            p['y']  += p['vy'] * dt
            p['vy'] += 260 * dt       # 중력
            p['vx'] *= 0.97
            alive.append(p)
        self.particles = alive

    def _draw_particles(self):
        for p in self.particles:
            frac  = max(0.0, p['life'] / p['max_life'])
            alpha = int(255 * frac)
            r     = max(1, int(p['size'] * frac))
            col   = p['color']
            surf  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*col, alpha), (r, r), r)
            self.disp.blit(surf, (int(p['x']) - r, int(p['y']) - r))

    # ─── 이벤트 루프 ──────────────────────────────────────────
    def run(self):
        while True:
            self.mouse = pygame.mouse.get_pos()
            self._handle_events()
            self._draw()
            self.clock.tick(self.FPS)

    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if   self.state == 'login':
                self._ev_login(ev)
            elif self.state == 'signup':
                self._ev_signup(ev)
            elif self.state == 'menu':
                self._ev_menu(ev)
            elif self.state == 'typing':
                self._ev_typing(ev)
            elif self.state == 'fullcombo':
                pass   # 연출 중 입력 무시
            elif self.state == 'result':
                self._ev_result(ev)
            elif self.state == 'settings':
                self._ev_settings(ev)

    # ─── 기록 저장 ─────────────────────────────────────────────
    def _save_record_to_db(self):
        """타이핑 완료 시 Firebase에 기록 저장."""
        if not self.auth_user:
            return
        try:
            is_custom = self.name in self.custom_texts
            # 미리보기용 텍스트 (최대 5줄)
            preview_lines = self.target.split('\n')[:5]
            text_preview = '\n'.join(preview_lines)
            record = {
                "nickname": self.nickname,
                "text_name": self.name,
                "is_custom": is_custom,
                "challenge_mode": self.challenge_mode,
                "cpm": self.cpm,
                "elapsed": round(self.elapsed, 2),
                "accuracy": round(self.accuracy, 2),
                "backspace_count": self.backspace_count,
                "max_combo": self.max_combo,
                "total_jamo": len(self.target_jamo),
                "full_combo": self.combo_break_time == 0.0,
                "text_preview": text_preview,
            }
            save_record(self.auth_user["localId"], self.auth_user["idToken"], record)
        except Exception as e:
            print(f"[기록 저장 실패] {e}")

    # ─── 로그인 / 회원가입 이벤트 처리 ─────────────────────────
    def _ev_login(self, ev):
        self._ev_auth_common(ev, mode='login')

    def _ev_signup(self, ev):
        self._ev_auth_common(ev, mode='signup')

    def _ev_auth_common(self, ev, mode):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for key, rect in self.btn_rects.items():
                if rect.collidepoint(ev.pos):
                    if key == '__auth_email__':
                        self.auth_focus = 'email'
                    elif key == '__auth_password__':
                        self.auth_focus = 'password'
                    elif key == '__auth_submit__':
                        self._auth_submit(mode)
                    elif key == '__auth_switch__':
                        self.state = 'signup' if mode == 'login' else 'login'
                        self.auth_msg = ''
                    elif key == '__auth_toggle_pw__':
                        self.auth_show_pw = not self.auth_show_pw
                    elif key == '__quit__':
                        pygame.quit()
                        sys.exit()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_TAB:
                self.auth_focus = 'password' if self.auth_focus == 'email' else 'email'
            elif ev.key == pygame.K_RETURN:
                self._auth_submit(mode)
            elif ev.key == pygame.K_BACKSPACE:
                if self.auth_focus == 'email':
                    self.auth_email = self.auth_email[:-1]
                else:
                    self.auth_password = self.auth_password[:-1]
            elif ev.key == pygame.K_ESCAPE:
                if mode == 'signup':
                    self.state = 'login'
                    self.auth_msg = ''
                else:
                    pygame.quit()
                    sys.exit()

        elif ev.type == pygame.TEXTINPUT:
            if self.auth_focus == 'email':
                self.auth_email += ev.text
            else:
                self.auth_password += ev.text

    def _auth_submit(self, mode):
        email = self.auth_email.strip()
        pw = self.auth_password
        if not email or not pw:
            self.auth_msg = "이메일과 비밀번호를 모두 입력하세요"
            self.auth_msg_color = ERROR
            return
        try:
            if mode == 'signup':
                signup(email, pw)
                self.auth_msg = "회원가입 성공! 로그인 화면으로 이동합니다"
                self.auth_msg_color = CORRECT
                self.auth_password = ''
                self.state = 'login'
            else:
                user = login(email, pw)
                self.auth_user = user
                self.auth_msg = ''
                try:
                    self.nickname = get_nickname(user["localId"], user["idToken"])
                except Exception:
                    self.nickname = email.split("@")[0]
                self.state = 'menu'
        except Exception as e:
            err = str(e)
            if 'EMAIL_EXISTS' in err:
                self.auth_msg = "이미 등록된 이메일입니다"
            elif 'WEAK_PASSWORD' in err:
                self.auth_msg = "비밀번호는 6자 이상이어야 합니다"
            elif 'INVALID_EMAIL' in err:
                self.auth_msg = "올바른 이메일 형식이 아닙니다"
            elif 'EMAIL_NOT_FOUND' in err or 'INVALID_LOGIN_CREDENTIALS' in err:
                self.auth_msg = "이메일 또는 비밀번호가 올바르지 않습니다"
            elif 'INVALID_PASSWORD' in err:
                self.auth_msg = "비밀번호가 올바르지 않습니다"
            else:
                self.auth_msg = "오류가 발생했습니다. 다시 시도하세요"
            self.auth_msg_color = ERROR

    # ─── 로그인 / 회원가입 화면 그리기 ─────────────────────────
    def _draw_auth(self, mode):
        dt = 1.0 / self.FPS
        self._update_stars(dt)
        self._draw_stars()

        # 타이틀
        title = self.F['title'].render("호랑이타자연습", True, TITLE_COL)
        self.disp.blit(title, (self.W // 2 - title.get_width() // 2, 50))

        # 부제
        sub_text = "로그인" if mode == 'login' else "회원가입"
        sub = self.F['heading'].render(sub_text, True, WHITE)
        self.disp.blit(sub, (self.W // 2 - sub.get_width() // 2, 130))

        # 입력 폼 영역
        form_w = 420
        form_x = self.W // 2 - form_w // 2
        field_h = 44
        label_gap = 28

        # 이메일 라벨 + 입력창
        y = 190
        lbl = self.F['btn'].render("이메일", True, STAT_LBL)
        self.disp.blit(lbl, (form_x, y))
        y += label_gap

        email_rect = pygame.Rect(form_x, y, form_w, field_h)
        self.btn_rects['__auth_email__'] = email_rect
        focused_email = self.auth_focus == 'email'
        border_col = ACCENT if focused_email else BORDER
        pygame.draw.rect(self.disp, PANEL2, email_rect, border_radius=8)
        pygame.draw.rect(self.disp, border_col, email_rect, 2, border_radius=8)
        email_surf = self.F['text'].render(self.auth_email, True, WHITE)
        self.disp.blit(email_surf, (form_x + 12, y + field_h // 2 - email_surf.get_height() // 2))
        if focused_email and int(time.time() * 2) % 2:
            cx = form_x + 12 + email_surf.get_width() + 2
            pygame.draw.line(self.disp, ACCENT, (cx, y + 10), (cx, y + field_h - 10), 2)
        y += field_h + 16

        # 비밀번호 라벨 + 입력창
        lbl2 = self.F['btn'].render("비밀번호", True, STAT_LBL)
        self.disp.blit(lbl2, (form_x, y))
        y += label_gap

        pw_rect = pygame.Rect(form_x, y, form_w - 44, field_h)
        self.btn_rects['__auth_password__'] = pw_rect
        focused_pw = self.auth_focus == 'password'
        border_col2 = ACCENT if focused_pw else BORDER
        full_pw_rect = pygame.Rect(form_x, y, form_w, field_h)
        pygame.draw.rect(self.disp, PANEL2, full_pw_rect, border_radius=8)
        pygame.draw.rect(self.disp, border_col2, full_pw_rect, 2, border_radius=8)
        pw_display = self.auth_password if self.auth_show_pw else '*' * len(self.auth_password)
        pw_surf = self.F['text'].render(pw_display, True, WHITE)
        self.disp.blit(pw_surf, (form_x + 12, y + field_h // 2 - pw_surf.get_height() // 2))
        if focused_pw and int(time.time() * 2) % 2:
            cx = form_x + 12 + pw_surf.get_width() + 2
            pygame.draw.line(self.disp, ACCENT, (cx, y + 10), (cx, y + field_h - 10), 2)

        # 비밀번호 표시 토글 버튼
        eye_rect = pygame.Rect(form_x + form_w - 40, y + 4, 36, field_h - 8)
        self.btn_rects['__auth_toggle_pw__'] = eye_rect
        eye_text = "보기" if not self.auth_show_pw else "숨김"
        eye_surf = self.F['btn_sm'].render(eye_text, True, GRAY)
        self.disp.blit(eye_surf, (eye_rect.centerx - eye_surf.get_width() // 2,
                                   eye_rect.centery - eye_surf.get_height() // 2))
        y += field_h + 24

        # 상태 메시지
        if self.auth_msg:
            msg_surf = self.F['small'].render(self.auth_msg, True, self.auth_msg_color)
            self.disp.blit(msg_surf, (self.W // 2 - msg_surf.get_width() // 2, y))
            y += 28

        # 제출 버튼
        y += 8
        btn_text = "로그인" if mode == 'login' else "회원가입"
        btn_surf = self.F['btn'].render(btn_text, True, (255, 255, 255))
        btn_w = max(200, btn_surf.get_width() + 40)
        btn_rect = pygame.Rect(self.W // 2 - btn_w // 2, y, btn_w, 48)
        self.btn_rects['__auth_submit__'] = btn_rect
        hover = btn_rect.collidepoint(self.mouse)
        btn_bg = ACCENT if hover else ACCENT_DIM
        pygame.draw.rect(self.disp, btn_bg, btn_rect, border_radius=10)
        self.disp.blit(btn_surf, (btn_rect.centerx - btn_surf.get_width() // 2,
                                   btn_rect.centery - btn_surf.get_height() // 2))
        y += 64

        # 전환 링크
        if mode == 'login':
            sw_text = "계정이 없으신가요?  회원가입"
        else:
            sw_text = "이미 계정이 있으신가요?  로그인"
        sw_surf = self.F['btn_sm'].render(sw_text, True, ACCENT)
        sw_rect = pygame.Rect(self.W // 2 - sw_surf.get_width() // 2 - 8, y,
                               sw_surf.get_width() + 16, sw_surf.get_height() + 8)
        self.btn_rects['__auth_switch__'] = sw_rect
        sw_hover = sw_rect.collidepoint(self.mouse)
        if sw_hover:
            pygame.draw.line(self.disp, ACCENT,
                             (sw_rect.x + 8, sw_rect.bottom - 4),
                             (sw_rect.right - 8, sw_rect.bottom - 4), 1)
        self.disp.blit(sw_surf, (sw_rect.x + 8, sw_rect.y + 4))

        # 종료 버튼 (좌측 하단)
        quit_surf = self.F['btn_sm'].render("종료", True, GRAY)
        quit_rect = pygame.Rect(20, self.H - 44, quit_surf.get_width() + 20, 32)
        self.btn_rects['__quit__'] = quit_rect
        q_hover = quit_rect.collidepoint(self.mouse)
        pygame.draw.rect(self.disp, BTN_HOVER if q_hover else BTN_BG, quit_rect, border_radius=6)
        pygame.draw.rect(self.disp, BORDER, quit_rect, 1, border_radius=6)
        self.disp.blit(quit_surf, (quit_rect.x + 10, quit_rect.centery - quit_surf.get_height() // 2))

        # 하단 안내
        hint = self.F['small'].render("Tab: 입력 전환  |  Enter: 제출  |  Esc: 뒤로", True, DARK_GRAY)
        self.disp.blit(hint, (self.W // 2 - hint.get_width() // 2, self.H - 36))

        pygame.display.flip()

    def _ev_menu(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for key, rect in self.btn_rects.items():
                if rect.collidepoint(ev.pos):
                    if key == '__quit__':
                        pygame.quit()
                        sys.exit()
                    elif key == '__challenge__':
                        self.challenge_mode = not self.challenge_mode
                        self.challenge_flash = time.time()
                        self._trigger_shake(15)
                    elif key == '__update__':
                        if self.update_url:
                            webbrowser.open(self.update_url)
                    elif key == '__settings__':
                        self._enter_settings()
                    elif key == '__tab_한글__':
                        if self.menu_tab != '한글':
                            self.menu_tab = '한글'
                            self.menu_scroll = 0
                    elif key == '__tab_영문__':
                        if self.menu_tab != '영문':
                            self.menu_tab = '영문'
                            self.menu_scroll = 0
                    elif key == '__custom_load__':
                        self._open_custom_file()
                    elif key == '__logout__':
                        self.auth_user = None
                        self.nickname = ''
                        self.auth_email = ''
                        self.auth_password = ''
                        self.state = 'login'
                    elif key == '__nickname_edit__':
                        self.nickname_editing = True
                        self.nickname_edit = self.nickname
                    elif key == '__nickname_save__':
                        self._save_nickname()
                    elif key == '__nickname_cancel__':
                        self.nickname_editing = False
                    elif key == '__share_text__':
                        self._share_custom_text_ui()
                    else:
                        self._start_text(key)
        if ev.type == pygame.MOUSEWHEEL:
            self.menu_scroll -= ev.y * 40
        if ev.type == pygame.KEYDOWN:
            if self.nickname_editing:
                if ev.key == pygame.K_RETURN:
                    self._save_nickname()
                elif ev.key == pygame.K_ESCAPE:
                    self.nickname_editing = False
                elif ev.key == pygame.K_BACKSPACE:
                    self.nickname_edit = self.nickname_edit[:-1]
                return
            if ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif ev.key == pygame.K_UP:
                self.menu_scroll -= 50
            elif ev.key == pygame.K_DOWN:
                self.menu_scroll += 50
        if ev.type == pygame.TEXTINPUT and self.nickname_editing:
            self.nickname_edit += ev.text

    def _save_nickname(self):
        new_nick = self.nickname_edit.strip()
        if not new_nick:
            return
        self.nickname = new_nick
        self.nickname_editing = False
        if self.auth_user:
            try:
                set_nickname(self.auth_user["localId"],
                             self.auth_user["idToken"], new_nick)
            except Exception:
                pass

    def _share_custom_text_ui(self):
        """현재 선택된 커스텀 글귀를 포럼에 공유."""
        if not self.custom_texts or not self.auth_user:
            return
        for title, body in self.custom_texts.items():
            try:
                share_custom_text(
                    self.auth_user["localId"],
                    self.auth_user["idToken"],
                    title, body, self.nickname)
            except Exception:
                pass
            break   # 첫 번째 커스텀 글귀만 공유

    def _ev_typing(self, ev):
        if ev.type == pygame.TEXTINPUT:
            # 스페이스로 줄바꿈 처리
            char_idx = len(self.typed)
            if ev.text == ' ' and char_idx < len(self.target) \
                    and self.target[char_idx] == '\n':
                self._add_input('\n')
            else:
                self._add_input(ev.text)
        elif ev.type == pygame.TEXTEDITING:
            self._update_composing(ev.text)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                self.composing = ""
                self.composing_jamo_processed = 0
                self.composing_correct = True
                self._add_input('\n')
            elif ev.key == pygame.K_BACKSPACE:
                if self.challenge_mode:
                    pass   # 도전 모드: 백스페이스 비활성
                elif not self.composing:
                    self._backspace()
                # 조합 중이면 IME가 TEXTEDITING으로 처리
            elif ev.key == pygame.K_ESCAPE:
                self.composing = ""
                self.composing_jamo_processed = 0
                self.composing_correct = True
                self.state = 'menu'
                self._reset()

    def _ev_result(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.state = 'menu'
            self._reset()

    # ─── 메인 드로우 ──────────────────────────────────────────
    COMBO_BREAK_DUR = 0.35  # 콤보 끊김 붉은 플래시 지속(초)

    def _combo_bg(self):
        """현재 콤보 티어에 맞는 배경색 (부드러운 보간) + 콤보 끊김 붉은 플래시"""
        bgs = CH_COMBO_BGS if self.challenge_mode else COMBO_BGS
        tier = min(self.combo // 100, len(bgs) - 1)
        if tier < len(bgs) - 1:
            frac = (self.combo % 100) / 100
            a, b = bgs[tier], bgs[tier + 1]
            base = tuple(int(a[i] + (b[i] - a[i]) * frac) for i in range(3))
        else:
            base = bgs[tier]

        # 콤보 끊김 붉은 플래시
        if self.combo_break_time > 0:
            t = (time.time() - self.combo_break_time) / self.COMBO_BREAK_DUR
            if t < 1.0:
                strength = (1.0 - t) ** 2      # ease out
                red = (60, 8, 8)
                return tuple(int(base[i] + (red[i] - base[i]) * strength)
                             for i in range(3))
        return base

    FULLCOMBO_DUR = 4.0   # 풀 콤보 연출 시간(초)
    FC_FADE_DUR   = 0.3   # 페이드 인-아웃 시간(초)

    def _draw(self):
        if self.state == 'typing':
            bg = self._combo_bg()
        elif self.state == 'fullcombo':
            bg = self._fullcombo_bg()
        else:
            bg = self.c(BG, CH_BG)
        self.disp.fill(bg)
        self.btn_rects = {}

        if   self.state == 'login':
            self._draw_auth('login')
        elif self.state == 'signup':
            self._draw_auth('signup')
        elif self.state == 'menu':
            self._draw_menu()
        elif self.state == 'typing':
            self._draw_typing()
        elif self.state == 'fullcombo':
            self._draw_fullcombo()
        elif self.state == 'result':
            self._draw_result()
        elif self.state == 'settings':
            self._draw_settings()

        # 화면 셰이크
        ox, oy = self._get_shake_offset()
        if ox or oy:
            snap = self.disp.copy()
            self.disp.fill(bg)
            self.disp.blit(snap, (ox, oy))

        # 도전 모드 토글 빨간 플래시
        flash_t = getattr(self, 'challenge_flash', 0)
        if flash_t > 0:
            elapsed = time.time() - flash_t
            if elapsed < 0.35:
                strength = (1.0 - elapsed / 0.35) ** 2
                flash_ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
                flash_ov.fill((255, 40, 40, int(120 * strength)))
                self.disp.blit(flash_ov, (0, 0))
            else:
                self.challenge_flash = 0

        pygame.display.flip()

    # ─── 메뉴 화면 ────────────────────────────────────────────
    def _update_stars(self, dt: float):
        """별 파티클을 아래로 이동, 화면 밖으로 나가면 위에서 재생성"""
        for i, s in enumerate(self.stars):
            s['x'] += s['vx'] * dt
            s['y'] += s['vy'] * dt
            if s['y'] > self.H + 10 or s['x'] < -20 or s['x'] > self.W + 20:
                self.stars[i] = self._make_star()

    def _draw_stars(self):
        t_now = time.time()
        for s in self.stars:
            flicker = 0.5 + 0.5 * abs(math.sin(t_now * s['speed'] + s['phase']))
            a = int(255 * s['alpha'] * flicker)
            col = tuple(min(255, int(c * a / 255)) for c in STAR_COL)
            r = max(1, int(s['r']))
            pygame.draw.circle(self.disp, col, (int(s['x']), int(s['y'])), r)

    def _draw_menu(self):
        dt = 1.0 / self.FPS
        self._update_stars(dt)
        self._draw_stars()

        # 도전 모드 버튼 (우측 상단)
        ch_label = "도전 모드 ON" if self.challenge_mode else "도전 모드"
        ch_surf  = self.F['btn_sm'].render(ch_label, True, (255, 255, 255))
        ch_w     = ch_surf.get_width() + 24
        ch_rect  = pygame.Rect(self.W - ch_w - 20, 16, ch_w, 32)
        self.btn_rects['__challenge__'] = ch_rect
        ch_hover = ch_rect.collidepoint(self.mouse)
        ch_bg    = (180, 40, 40) if self.challenge_mode else ((120, 30, 30) if ch_hover else (80, 20, 20))
        ch_bdr   = (255, 72, 72) if (self.challenge_mode or ch_hover) else (120, 40, 40)
        pygame.draw.rect(self.disp, ch_bg, ch_rect, border_radius=6)
        pygame.draw.rect(self.disp, ch_bdr, ch_rect, 1, border_radius=6)
        self.disp.blit(ch_surf, (ch_rect.x + 12, ch_rect.centery - ch_surf.get_height() // 2))

        # 설정 버튼 (좌측 상단)
        st_surf = self.F['btn_sm'].render("설  정", True, (255, 255, 255))
        st_w    = st_surf.get_width() + 24
        st_rect = pygame.Rect(20, 16, st_w, 32)
        self.btn_rects['__settings__'] = st_rect
        st_hover = st_rect.collidepoint(self.mouse)
        st_bg   = self.c(BTN_HOVER, CH_BTN_HOVER) if st_hover else self.c(BTN_BG, CH_BTN_BG)
        st_bdr  = self.c(ACCENT, CH_ACCENT) if st_hover else self.c(BORDER, CH_BORDER)
        pygame.draw.rect(self.disp, st_bg, st_rect, border_radius=6)
        pygame.draw.rect(self.disp, st_bdr, st_rect, 1, border_radius=6)
        self.disp.blit(st_surf, (st_rect.x + 12, st_rect.centery - st_surf.get_height() // 2))

        # 로그아웃 버튼 (설정 옆)
        lo_surf = self.F['btn_sm'].render("로그아웃", True, (255, 255, 255))
        lo_w    = lo_surf.get_width() + 24
        lo_rect = pygame.Rect(st_rect.right + 8, 16, lo_w, 32)
        self.btn_rects['__logout__'] = lo_rect
        lo_hover = lo_rect.collidepoint(self.mouse)
        lo_bg   = self.c(BTN_HOVER, CH_BTN_HOVER) if lo_hover else self.c(BTN_BG, CH_BTN_BG)
        lo_bdr  = self.c(ACCENT, CH_ACCENT) if lo_hover else self.c(BORDER, CH_BORDER)
        pygame.draw.rect(self.disp, lo_bg, lo_rect, border_radius=6)
        pygame.draw.rect(self.disp, lo_bdr, lo_rect, 1, border_radius=6)
        self.disp.blit(lo_surf, (lo_rect.x + 12, lo_rect.centery - lo_surf.get_height() // 2))

        # 닉네임 표시 / 편집 (우측 상단, 도전 모드 아래)
        if self.nickname_editing:
            nk_label = self.F['btn_sm'].render("닉네임: ", True, STAT_LBL)
            nk_input = self.F['btn_sm'].render(self.nickname_edit + "|", True, WHITE)
            nk_w = nk_label.get_width() + nk_input.get_width() + 80
            nk_x = self.W - nk_w - 20
            nk_rect = pygame.Rect(nk_x, 54, nk_w, 28)
            pygame.draw.rect(self.disp, PANEL2, nk_rect, border_radius=6)
            pygame.draw.rect(self.disp, ACCENT, nk_rect, 1, border_radius=6)
            self.disp.blit(nk_label, (nk_x + 8, 57))
            self.disp.blit(nk_input, (nk_x + 8 + nk_label.get_width(), 57))
            # 저장/취소 버튼
            sv_surf = self.F['btn_sm'].render("저장", True, CORRECT)
            sv_rect = pygame.Rect(nk_rect.right - 62, 55, 28, 24)
            self.btn_rects['__nickname_save__'] = sv_rect
            self.disp.blit(sv_surf, (sv_rect.x, sv_rect.y))
            cn_surf = self.F['btn_sm'].render("취소", True, ERROR)
            cn_rect = pygame.Rect(nk_rect.right - 30, 55, 28, 24)
            self.btn_rects['__nickname_cancel__'] = cn_rect
            self.disp.blit(cn_surf, (cn_rect.x, cn_rect.y))
        else:
            nk_text = f"{self.nickname}"
            nk_surf = self.F['btn_sm'].render(nk_text, True, STAT_VAL)
            nk_w = nk_surf.get_width() + 24
            nk_rect = pygame.Rect(self.W - nk_w - 20, 54, nk_w, 28)
            self.btn_rects['__nickname_edit__'] = nk_rect
            nk_hover = nk_rect.collidepoint(self.mouse)
            nk_bg = self.c(BTN_HOVER, CH_BTN_HOVER) if nk_hover else self.c(PANEL2, CH_PANEL2)
            pygame.draw.rect(self.disp, nk_bg, nk_rect, border_radius=6)
            pygame.draw.rect(self.disp, self.c(BORDER, CH_BORDER), nk_rect, 1, border_radius=6)
            self.disp.blit(nk_surf, (nk_rect.x + 12, nk_rect.centery - nk_surf.get_height() // 2))

        # 타이틀
        title = self.F['title'].render("호랑이타자연습", True,
                                       self.c(TITLE_COL, CH_TITLE_COL))
        self.disp.blit(title, (self.W // 2 - title.get_width() // 2, 36))

        # ── 업데이트 배너 ──
        if self.update_available and self.update_available is not False:
            upd_text = f"새 버전 v{self.update_available} 출시! 클릭하여 다운로드"
            upd_surf = self.F['btn_sm'].render(upd_text, True, (255, 255, 255))
            upd_w = upd_surf.get_width() + 32
            upd_rect = pygame.Rect(self.W // 2 - upd_w // 2, 76, upd_w, 28)
            self.btn_rects['__update__'] = upd_rect
            upd_hover = upd_rect.collidepoint(self.mouse)
            upd_bg = (40, 120, 60) if upd_hover else (30, 90, 45)
            pygame.draw.rect(self.disp, upd_bg, upd_rect, border_radius=6)
            pygame.draw.rect(self.disp, CORRECT, upd_rect, 1, border_radius=6)
            self.disp.blit(upd_surf, (upd_rect.centerx - upd_surf.get_width() // 2,
                                      upd_rect.centery - upd_surf.get_height() // 2))

        if self.challenge_mode:
            sub = self.F['subhead'].render("도전 모드: 백스페이스 없음!", True, (255, 72, 72))
            self.disp.blit(sub, (self.W // 2 - sub.get_width() // 2, 100))
        else:
            sub = self.F['subhead'].render("연습할 텍스트를 선택하세요", True, GRAY)
            self.disp.blit(sub, (self.W // 2 - sub.get_width() // 2, 100))

        # ── 한글/영문 탭 토글 ──
        tab_w    = 80
        tab_h    = 32
        tab_gap  = 4
        tab_total = tab_w * 2 + tab_gap
        tab_x    = self.W // 2 - tab_total // 2
        tab_y    = 128

        for i, tab_name in enumerate(('한글', '영문')):
            tx = tab_x + i * (tab_w + tab_gap)
            tr = pygame.Rect(tx, tab_y, tab_w, tab_h)
            self.btn_rects[f'__tab_{tab_name}__'] = tr
            active = (self.menu_tab == tab_name)
            hover  = tr.collidepoint(self.mouse)
            if active:
                bg  = self.c(ACCENT, CH_ACCENT)
                fg  = (255, 255, 255)
            elif hover:
                bg  = self.c(BTN_HOVER, CH_BTN_HOVER)
                fg  = self.c(WHITE, CH_WHITE)
            else:
                bg  = self.c(BTN_BG, CH_BTN_BG)
                fg  = self.c(GRAY, CH_GRAY)
            bdr = self.c(ACCENT, CH_ACCENT) if (active or hover) else self.c(BORDER, CH_BORDER)
            pygame.draw.rect(self.disp, bg, tr, border_radius=6)
            pygame.draw.rect(self.disp, bdr, tr, 1, border_radius=6)
            ts = self.F['btn_sm'].render(tab_name, True, fg)
            self.disp.blit(ts, (tr.centerx - ts.get_width() // 2,
                                tr.centery - ts.get_height() // 2))

        # 구분선
        pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER),
                         (self.W // 2 - 260, tab_y + tab_h + 10),
                         (self.W // 2 + 260, tab_y + tab_h + 10), 1)

        # ── 리스트형 텍스트 선택 ──
        text_src = TEXTS_KO if self.menu_tab == '한글' else TEXTS_EN
        # 내장 글귀 + 커스텀 글귀 합산
        all_src  = {**text_src, **self.custom_texts}
        names    = list(all_src.keys())
        custom_start = len(text_src)   # 커스텀 글귀 시작 인덱스
        list_w   = int(700 * self.W / self.BASE_W)
        item_h   = int(64 * self.H / self.BASE_H)
        gap      = 8
        list_x   = self.W // 2 - list_w // 2
        list_top = tab_y + tab_h + 20
        list_bot = self.H - 60
        total_h  = len(names) * item_h + (len(names) - 1) * gap
        # 커스텀 구분선 높이 추가
        if self.custom_texts:
            total_h += 32

        # 스크롤 범위 제한
        max_scroll = max(0, total_h - (list_bot - list_top))
        self.menu_scroll = max(0, min(self.menu_scroll, max_scroll))

        # 클리핑
        clip = pygame.Rect(0, list_top, self.W, list_bot - list_top)
        self.disp.set_clip(clip)

        y_offset = 0  # 커스텀 구분선 오프셋
        for idx, name in enumerate(names):
            # 커스텀 글귀 구분선
            if idx == custom_start and self.custom_texts:
                sep_y = list_top + idx * (item_h + gap) + y_offset - self.menu_scroll
                if list_top <= sep_y + 16 <= list_bot:
                    sep_label = self.F['small'].render("── 커스텀 글귀 ──", True,
                                                       self.c(GRAY, CH_GRAY))
                    self.disp.blit(sep_label,
                                   (self.W // 2 - sep_label.get_width() // 2, sep_y + 4))
                y_offset += 32

            iy = list_top + idx * (item_h + gap) + y_offset - self.menu_scroll

            # 화면 밖 스킵
            if iy + item_h < list_top or iy > list_bot:
                continue

            rect = pygame.Rect(list_x, iy, list_w, item_h)
            self.btn_rects[name] = rect

            is_custom = idx >= custom_start
            hover = rect.collidepoint(self.mouse)
            bg    = self.c(BTN_HOVER, CH_BTN_HOVER) if hover else self.c(BTN_BG, CH_BTN_BG)
            bdr   = self.c(ACCENT, CH_ACCENT) if hover else self.c(BORDER, CH_BORDER)

            pygame.draw.rect(self.disp, bg,  rect, border_radius=10)
            pygame.draw.rect(self.disp, bdr, rect, 1 + hover, border_radius=10)

            # 커스텀 마크
            if is_custom:
                mark = self.F['small'].render("커스텀", True, COMPOSING)
                self.disp.blit(mark, (list_x + 24, iy + 6))

            # 제목 (왼쪽)
            label = self.F['btn'].render(name, True,
                                         self.c(WHITE, CH_WHITE) if hover
                                         else self.c(BTN_TEXT, CH_BTN_TEXT))
            lbl_y = iy + item_h // 2 - label.get_height() // 2
            if is_custom:
                lbl_y += 4
            self.disp.blit(label, (list_x + 24, lbl_y))

            # 타수 (오른쪽)
            flat = self._load_text(all_src[name])
            info = f"{len(self._decompose(flat))}타"
            info_s = self.F['small'].render(info, True,
                                            self.c(ACCENT, CH_ACCENT) if hover
                                            else self.c(DARK_GRAY, CH_DARK_GRAY))
            self.disp.blit(info_s, (
                list_x + list_w - 24 - info_s.get_width(),
                iy + item_h // 2 - info_s.get_height() // 2
            ))

        self.disp.set_clip(None)

        # 스크롤 인디케이터
        if max_scroll > 0:
            visible = list_bot - list_top
            bar_h   = max(20, int(visible * visible / total_h))
            bar_y   = list_top + int(self.menu_scroll / max_scroll * (visible - bar_h))
            bar_x   = list_x + list_w + 6
            pygame.draw.rect(self.disp, self.c(BORDER, CH_BORDER),
                             (bar_x, bar_y, 4, bar_h), border_radius=2)

        # 커스텀 글귀 로드 버튼 (우측 하단)
        cl_label = self.F['btn_sm'].render("커스텀 글귀 로드", True, (255, 255, 255))
        cl_w     = cl_label.get_width() + 24
        cl_rect  = pygame.Rect(self.W - cl_w - 20, self.H - 50, cl_w, 38)
        self.btn_rects['__custom_load__'] = cl_rect
        cl_hover = cl_rect.collidepoint(self.mouse)
        cl_bg    = self.c(BTN_HOVER, CH_BTN_HOVER) if cl_hover else self.c(BTN_BG, CH_BTN_BG)
        cl_bdr   = self.c(ACCENT, CH_ACCENT) if cl_hover else self.c(BORDER, CH_BORDER)
        pygame.draw.rect(self.disp, cl_bg, cl_rect, border_radius=8)
        pygame.draw.rect(self.disp, cl_bdr, cl_rect, 1, border_radius=8)
        self.disp.blit(cl_label, (cl_rect.x + 12, cl_rect.centery - cl_label.get_height() // 2))

        # 종료 버튼
        quit_rect = pygame.Rect(self.W // 2 - 80, self.H - 50, 160, 38)
        self.btn_rects['__quit__'] = quit_rect
        qhover = quit_rect.collidepoint(self.mouse)
        pygame.draw.rect(self.disp, self.c(BTN_HOVER, CH_BTN_HOVER) if qhover
                         else self.c(BG, CH_BG), quit_rect, border_radius=8)
        pygame.draw.rect(self.disp, self.c(BORDER, CH_BORDER), quit_rect, 1, border_radius=8)
        q = self.F['btn_sm'].render("종  료", True, self.c(GRAY, CH_GRAY))
        self.disp.blit(q, (
            quit_rect.centerx - q.get_width() // 2,
            quit_rect.centery - q.get_height() // 2
        ))

        # 하단 안내
        hint = self.F['small'].render("ESC — 종료   SCROLL — 목록 이동", True, DARK_GRAY)
        self.disp.blit(hint, (self.W // 2 - hint.get_width() // 2, self.H - 14))

    # ─── 타이핑 화면 ──────────────────────────────────────────
    def _draw_typing(self):
        self._update_particles(1.0 / self.FPS)
        self._draw_top_bar()
        self._draw_progress_bar()
        self._draw_combo_overlay()
        self._draw_text_area()
        self._draw_particles()
        self._draw_bottom_bar()

    def _draw_top_bar(self):
        sy = self.H / self.BASE_H
        sx_r = self.W / self.BASE_W
        bar_h = int(118 * sy)
        pygame.draw.rect(self.disp, self.c(PANEL, CH_PANEL), (0, 0, self.W, bar_h))
        pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER), (0, bar_h), (self.W, bar_h), 1)
        self._bar_h = bar_h   # 다른 메서드에서 참조

        # 좌측 제목
        prefix = "호랑이타자연습"
        if self.challenge_mode:
            prefix += " [도전]"
        t = self.F['subhead'].render(f"{prefix}  |  {self.name}", True,
                                     self.c(GRAY, CH_GRAY))
        self.disp.blit(t, (int(20 * sx_r), int(14 * sy)))

        # 우측 ESC 안내
        esc = self.F['small'].render("ESC — 메뉴로", True, self.c(DARK_GRAY, CH_DARK_GRAY))
        self.disp.blit(esc, (self.W - esc.get_width() - int(20 * sx_r), int(14 * sy)))

        # ── 4개 통계 ──
        stats = [
            ("타  수",    f"{self.cpm}"),
            ("정확도",    f"{self.accuracy:.1f}%"),
            ("경과 시간", self._fmt_time(self.elapsed)),
            ("진행률",    f"{self.progress:.1f}%"),
        ]
        # 4등분 좌표
        n = len(stats)
        sx_list  = [int(self.W * (2 * i + 1) / (2 * n)) for i in range(n)]
        dividers = [int(self.W * (i + 1) / n) for i in range(n - 1)]

        for (lbl, val), sxx in zip(stats, sx_list):
            vs = self.F['stat_v'].render(val, True, self.c(STAT_VAL, CH_STAT_VAL))
            ls = self.F['stat_l'].render(lbl, True, self.c(STAT_LBL, CH_STAT_LBL))
            self.disp.blit(vs, (sxx - vs.get_width() // 2, int(38 * sy)))
            self.disp.blit(ls, (sxx - ls.get_width() // 2, int(84 * sy)))

        for dx in dividers:
            pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER),
                             (dx, int(34 * sy)), (dx, int(106 * sy)), 1)

    def _draw_combo_overlay(self):
        """진행바 아래 가운데에 콤보 표시 (1타마다 갱신 애니메이션)"""
        tier = min(self.combo // 100, len(COMBO_COLORS) - 1)
        col  = COMBO_COLORS[tier]

        # 콤보 끊김 시 붉은색 보간
        break_frac = 0.0
        if self.combo_break_time > 0:
            bt = (time.time() - self.combo_break_time) / self.COMBO_BREAK_DUR
            if bt < 1.0:
                break_frac = (1.0 - bt) ** 2
                col = tuple(int(col[i] + (ERROR[i] - col[i]) * break_frac)
                            for i in range(3))

        # 애니메이션 스케일 계산 (ease out: 크게 → 원래)
        if self.combo_anim_start > 0:
            t = min(1.0, (time.time() - self.combo_anim_start) / self.COMBO_ANIM_DUR)
            scale = 1.0 + 0.5 * (1.0 - t) ** 2
        else:
            scale = 1.0

        cx = self.W // 2
        bar_h = getattr(self, '_bar_h', int(118 * self.H / self.BASE_H))
        prog_h = max(4, int(8 * self.H / self.BASE_H))
        cy = bar_h + prog_h + int(6 * self.H / self.BASE_H)

        # 콤보 숫자
        num_surf = self.F['combo_num'].render(str(self.combo), True, col)

        if scale > 1.001:
            sw = int(num_surf.get_width()  * scale)
            sh = int(num_surf.get_height() * scale)
            num_surf = pygame.transform.smoothscale(num_surf, (sw, sh))

        nx = cx - num_surf.get_width() // 2
        base_h = self.F['combo_num'].get_height()
        ny = cy + (base_h - num_surf.get_height()) // 2
        self.disp.blit(num_surf, (nx, ny))

        # "COMBO" 라벨 — 숫자 바로 아래
        lbl_col = col if (self.combo >= 10 or break_frac > 0) else COMBO_LABEL_COL
        lbl = self.F['combo_lbl'].render("COMBO", True, lbl_col)
        self.disp.blit(lbl, (cx - lbl.get_width() // 2, cy + base_h + 2))

    def _draw_progress_bar(self):
        bar_h = getattr(self, '_bar_h', int(118 * self.H / self.BASE_H))
        prog_h = max(4, int(8 * self.H / self.BASE_H))
        pygame.draw.rect(self.disp, self.c(PROG_BG, CH_PROG_BG), (0, bar_h, self.W, prog_h))
        fw = int(self.W * self.progress / 100)
        if fw > 0:
            pygame.draw.rect(self.disp, self.c(PROG_FG, CH_PROG_FG), (0, bar_h, fw, prog_h))
        if 0 < fw < self.W:
            pygame.draw.circle(self.disp, self.c(CORRECT, CH_CORRECT),
                               (fw, bar_h + prog_h // 2), max(3, int(5 * self.H / self.BASE_H)))

    CURSOR_COLOR   = (255, 218, 72)     # 노랑 커서
    CURSOR_EASE_SP = 18.0               # ease-out 속도 계수

    SCROLL_EASE_SP = 12.0               # 스크롤 ease-out 속도

    def _draw_text_area(self):
        area_h   = self.H - self.TEXT_Y - self.BOT_H
        clip     = pygame.Rect(0, self.TEXT_Y, self.W, area_h)
        cursor_i = len(self.typed)
        f        = self.F['text']
        dt       = 1.0 / self.FPS

        # ── 매 프레임 스크롤 목표 갱신 + ease-out 보간 ──
        self._update_scroll()
        scroll_spd = self.SCROLL_EASE_SP * dt
        scroll_spd = min(scroll_spd, 1.0)
        self.scroll += (self.scroll_target - self.scroll) * scroll_spd

        self.disp.set_clip(clip)

        # ── 커서 목표 위치 갱신 ──
        target_item = None
        for item in self.layout:
            if item['i'] == cursor_i:
                target_item = item
                break
        if target_item:
            tx = self.TEXT_X + target_item['x']
            ty = self.TEXT_Y + target_item['y'] - self.scroll
            tw = target_item['w']
            if self.composing:
                tw = max(tw, f.size(self.composing)[0])
            self.cursor_target_x = tx
            self.cursor_target_y = ty
            self.cursor_w        = tw
            if not self.cursor_inited:
                self.cursor_x = tx
                self.cursor_y = ty
                self.cursor_inited = True

        # ease-out 보간
        spd = self.CURSOR_EASE_SP * dt
        spd = min(spd, 1.0)
        self.cursor_x += (self.cursor_target_x - self.cursor_x) * spd
        self.cursor_y += (self.cursor_target_y - self.cursor_y) * spd

        # ── 노랑 커서 배경 (ease-out 위치) ──
        if self.cursor_inited:
            cx = self.cursor_x
            cy = self.cursor_y
            cw = self.cursor_w
            # 오타 시 빨간 배경, 정상 시 설정 커서 색상
            if self.composing and not self.composing_correct:
                cursor_bg = ERROR_BG
                border_c  = tuple(self.cfg['error_color'])
            else:
                cursor_bg = (60, 52, 12)
                border_c  = tuple(self.cfg['cursor_color'])
            pygame.draw.rect(
                self.disp, cursor_bg,
                (cx, cy + 2, cw, self.LINE_H - 6),
                border_radius=3
            )
            pygame.draw.rect(
                self.disp, border_c,
                (cx, cy + 2, cw, self.LINE_H - 6),
                1, border_radius=3
            )

        # ── 글자 렌더링 ──
        for item in self.layout:
            i       = item['i']
            disp_ch = item['ch']
            is_nl   = item.get('newline', False)
            sx      = self.TEXT_X + item['x']
            sy      = self.TEXT_Y + item['y'] - self.scroll

            if sy + self.LINE_H < self.TEXT_Y or sy > self.TEXT_Y + area_h:
                continue
            if is_nl:
                continue

            if i < cursor_i:
                # 이미 입력한 구간
                if i < len(self.typed) and self._char_jamo_correct(i):
                    color = tuple(self.cfg['correct_color'])
                else:
                    pygame.draw.rect(
                        self.disp, ERROR_BG,
                        (sx, sy + 2, item['w'], self.LINE_H - 6),
                        border_radius=3
                    )
                    color = tuple(self.cfg['error_color'])
                surf = f.render(disp_ch, True, color)
                self.disp.blit(surf, (sx, sy))

            elif i == cursor_i:
                # 커서 위치 — 타겟 글자는 미작성 색상으로 표시
                surf = f.render(disp_ch, True, tuple(self.cfg['untyped_color']))
                self.disp.blit(surf, (sx, sy))
                # 조합 중이면 입력 글자를 정타 색상으로 위에 덮어 표시
                if self.composing:
                    comp_color = tuple(self.cfg['correct_color']) \
                                 if self.composing_correct \
                                 else tuple(self.cfg['error_color'])
                    cs = f.render(self.composing, True, comp_color)
                    self.disp.blit(cs, (self.cursor_x, self.cursor_y))

            else:
                col = self.c(DARK_GRAY, CH_DARK_GRAY) if is_nl \
                      else tuple(self.cfg['untyped_color'])
                surf = f.render(disp_ch, True, col)
                self.disp.blit(surf, (sx, sy))

        # ── 중앙 타겟 라인에서 멀어질수록 어둡게 (캐시된 오버레이) ──
        if self._fade_top_h > 0:
            self.disp.blit(self._fade_top, (0, self.TEXT_Y))
        if self._fade_bot_h > 0:
            self.disp.blit(self._fade_bot, (0, self._fade_bot_start))

        self.disp.set_clip(None)

    def _draw_bottom_bar(self):
        by = self.H - self.BOT_H
        pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER), (0, by), (self.W, by), 1)

        if self.challenge_mode:
            hints = [("ESC", "메뉴로"), ("ENTER/SPACE", "줄바꿈")]
        else:
            hints = [("ESC", "메뉴로"), ("ENTER/SPACE", "줄바꿈"), ("BACKSPACE", "한 글자 삭제")]
        x = 24
        for key, desc in hints:
            ks = self.F['small'].render(key, True, self.c(ACCENT, CH_ACCENT))
            ds = self.F['small'].render(f"  {desc}     ", True, self.c(GRAY, CH_GRAY))
            self.disp.blit(ks, (x, by + 14))
            x += ks.get_width()
            self.disp.blit(ds, (x, by + 14))
            x += ds.get_width()

    # ─── 설정 화면 ─────────────────────────────────────────────
    SETTINGS_ITEMS = [
        {'key': 'resolution',         'label': '해상도',              'type': 'dropdown'},
        {'key': 'fps',                'label': '주사율',              'type': 'dropdown'},
        {'key': 'font_size',          'label': '글귀 크기',           'type': 'stepper'},
        {'key': 'master_volume',      'label': '마스터 볼륨',         'type': 'slider'},
        {'key': 'type_volume',        'label': '타건음 볼륨',         'type': 'slider'},
        {'key': 'untyped_color',      'label': '미작성 글귀 색상',    'type': 'color'},
        {'key': 'correct_color',      'label': '정타 글귀 색상',      'type': 'color'},
        {'key': 'error_color',        'label': '오타 글귀 색상',      'type': 'color'},
        {'key': 'cursor_color',       'label': '커서 색상',           'type': 'color'},
        {'key': 'particles_enabled',  'label': '파티클 이펙트 사용',   'type': 'toggle'},
        {'key': 'particle_color',     'label': '파티클 이펙트 색상',   'type': 'color'},
    ]

    def _enter_settings(self):
        self.state = 'settings'
        self.cfg_dropdown = None
        self.cfg_colorpick = None
        self._init_settings_test()

    def _init_settings_test(self):
        """설정 테스트 타이핑 상태 초기화"""
        txt = SETTINGS_TEST_TEXT
        jamo = self._decompose(txt)
        ranges = []
        pos = 0
        for ch in txt:
            n = len(self._decompose(ch))
            ranges.append((pos, pos + n))
            pos += n

        # 레이아웃 빌드 (우측 절반 너비 기준)
        f = self.F['text']
        half_w = self.W // 2 - 80
        layout = []
        x, y = 0, 0
        for i, ch in enumerate(txt):
            if ch == '\n':
                layout.append({'i': i, 'ch': '', 'x': x, 'y': y, 'w': 0, 'newline': True})
                x = 0
                y += self.LINE_H
            else:
                w = f.size(ch)[0]
                if x + w > half_w:
                    x = 0
                    y += self.LINE_H
                layout.append({'i': i, 'ch': ch, 'x': x, 'y': y, 'w': w, 'newline': False})
                x += w

        self.st = {
            'target': txt, 'typed': '', 'composing': '',
            'target_jamo': jamo, 'typed_jamo': [],
            'char_jamo_ranges': ranges,
            'composing_jamo_processed': 0, 'composing_correct': True,
            'layout': layout,
            'combo': 0, 'max_combo': 0,
            'last_input_time': 0.0, 'combo_anim_start': 0.0, 'combo_break_time': 0.0,
            'particles': [],
            'shake_start': 0.0, 'shake_intensity': 0.0,
            'cursor_x': 0.0, 'cursor_y': 0.0,
            'cursor_target_x': 0.0, 'cursor_target_y': 0.0,
            'cursor_w': 0.0, 'cursor_inited': False,
            'start_time': None, 'scroll': 0,
        }

    # ─── 설정 테스트 타이핑 로직 ─────────────────────────────
    def _st_update_composing(self, text):
        s = self.st
        if self.challenge_mode and s['composing']:
            if not text:
                return
            if len(self._decompose(text)) < s['composing_jamo_processed']:
                return
        s['composing'] = text
        if not text:
            s['composing_jamo_processed'] = 0
            s['composing_correct'] = True
            return
        if not s['target']:
            return
        if not s['start_time']:
            s['start_time'] = time.time()
        now = time.time()
        comp_jamo = self._decompose(text)
        new_count = len(comp_jamo)
        if new_count <= s['composing_jamo_processed']:
            s['composing_jamo_processed'] = new_count
            s['composing_correct'] = True
            base = len(s['typed_jamo'])
            for k in range(new_count):
                pos = base + k
                if pos < len(s['target_jamo']) and comp_jamo[k] != s['target_jamo'][pos]:
                    s['composing_correct'] = False
                    break
            return
        char_idx = len(s['typed'])
        if char_idx >= len(s['target']):
            s['composing_jamo_processed'] = new_count
            return
        base = len(s['typed_jamo'])
        first_new = True
        for k in range(s['composing_jamo_processed'], new_count):
            pos = base + k
            if pos >= len(s['target_jamo']):
                break
            self._play_type_sound()
            jamo_correct = (comp_jamo[k] == s['target_jamo'][pos])
            if not jamo_correct:
                self._play_sfx(self.snd_wrong_input)
                s['combo'] = 0
                s['combo_break_time'] = now
                s['composing_correct'] = False
            elif first_new and s['last_input_time'] > 0 \
                    and (now - s['last_input_time']) > self.COMBO_TIMEOUT:
                s['combo'] = 1
            else:
                s['combo'] += 1
            s['combo_anim_start'] = now
            s['max_combo'] = max(s['max_combo'], s['combo'])
            first_new = False
            if jamo_correct and self.cfg['particles_enabled']:
                self._st_spawn_particles(char_idx)
                s['shake_start'] = time.time()
                s['shake_intensity'] = 4
            s['last_input_time'] = now
        s['composing_jamo_processed'] = new_count

    def _st_add_input(self, text):
        s = self.st
        if not s['target']:
            return
        if not s['start_time']:
            s['start_time'] = time.time()
        now = time.time()
        first_new = (s['composing_jamo_processed'] == 0)
        for ch in text:
            char_idx = len(s['typed'])
            if char_idx >= len(s['target']):
                break
            user_jamo = self._decompose(ch)
            start, end = s['char_jamo_ranges'][char_idx]
            target_n = end - start
            already = min(s['composing_jamo_processed'], target_n)
            for k in range(target_n):
                if len(s['typed_jamo']) >= len(s['target_jamo']):
                    break
                uj = user_jamo[k] if k < len(user_jamo) else '\x00'
                jamo_correct = (uj == s['target_jamo'][len(s['typed_jamo'])])
                s['typed_jamo'].append(uj)
                if k < already:
                    continue
                self._play_type_sound()
                if not jamo_correct:
                    self._play_sfx(self.snd_wrong_input)
                    s['combo'] = 0
                    s['combo_break_time'] = now
                elif first_new and s['last_input_time'] > 0 \
                        and (now - s['last_input_time']) > self.COMBO_TIMEOUT:
                    s['combo'] = 1
                else:
                    s['combo'] += 1
                s['combo_anim_start'] = now
                s['max_combo'] = max(s['max_combo'], s['combo'])
                first_new = False
                if jamo_correct and ch != '\n' and self.cfg['particles_enabled']:
                    self._st_spawn_particles(char_idx)
                    s['shake_start'] = time.time()
                    s['shake_intensity'] = 4
            s['composing_jamo_processed'] = max(0, s['composing_jamo_processed'] - target_n)
            s['typed'] += ch
        s['composing'] = ''
        s['composing_correct'] = True
        s['last_input_time'] = now

    def _st_backspace(self):
        s = self.st
        if s['typed']:
            self._play_type_sound()
            ci = len(s['typed']) - 1
            start, end = s['char_jamo_ranges'][ci]
            s['typed'] = s['typed'][:-1]
            s['typed_jamo'] = s['typed_jamo'][:-(end - start)]

    def _st_spawn_particles(self, char_idx):
        s = self.st
        for item in s['layout']:
            if item['i'] == char_idx:
                break
        else:
            return
        ox = self.W // 2 + 40
        sx = ox + item['x'] + item['w'] / 2
        sy = self.TEXT_Y + item['y'] + self.LINE_H / 2 - s['scroll']
        col = tuple(self.cfg['particle_color'])
        for _ in range(3):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(60, 200)
            life  = random.uniform(0.25, 0.5)
            size  = random.uniform(2.5, 5.5)
            s['particles'].append({
                'x': sx + random.uniform(-6, 6),
                'y': sy + random.uniform(-6, 6),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 50,
                'life': life, 'max_life': life,
                'size': size, 'color': col,
            })

    def _st_char_jamo_correct(self, char_idx):
        s = self.st
        start, end = s['char_jamo_ranges'][char_idx]
        return all(
            j < len(s['typed_jamo']) and s['typed_jamo'][j] == s['target_jamo'][j]
            for j in range(start, end)
        )

    # ─── 설정 이벤트 처리 ────────────────────────────────────
    def _ev_settings(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self._apply_settings()
            self.state = 'menu'
            self._reset()
            return

        # 테스트 타이핑 입력
        if ev.type == pygame.TEXTINPUT:
            s = self.st
            char_idx = len(s['typed'])
            if ev.text == ' ' and char_idx < len(s['target']) \
                    and s['target'][char_idx] == '\n':
                self._st_add_input('\n')
            else:
                self._st_add_input(ev.text)
        elif ev.type == pygame.TEXTEDITING:
            self._st_update_composing(ev.text)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                s = self.st
                s['composing'] = ''
                s['composing_jamo_processed'] = 0
                s['composing_correct'] = True
                self._st_add_input('\n')
            elif ev.key == pygame.K_BACKSPACE:
                if not self.challenge_mode and not self.st['composing']:
                    self._st_backspace()

        # 슬라이더 드래그
        if ev.type == pygame.MOUSEMOTION and self._slider_dragging:
            key = self._slider_dragging
            for item_info in getattr(self, '_settings_click_rects', []):
                k, rect, st = item_info
                if k == key and st == 'slider':
                    val = max(0, min(100, int((ev.pos[0] - rect.x) / rect.w * 100)))
                    self.cfg[key] = val
                    break
            return
        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self._slider_dragging:
            self._slider_dragging = None
            return

        # UI 클릭
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            # 드롭다운/컬러피커 닫기 (외부 클릭 시)
            handled = False

            # 열린 드롭다운 항목 클릭 처리
            if self.cfg_dropdown:
                dd_rect = getattr(self, '_dd_rects', {})
                for val, rect in dd_rect.items():
                    if rect.collidepoint(mx, my):
                        self.cfg[self.cfg_dropdown] = val
                        if self.cfg_dropdown == 'font_size':
                            self._apply_font_size()
                        self.cfg_dropdown = None
                        handled = True
                        break
                if not handled:
                    self.cfg_dropdown = None
                    handled = True

            # 열린 컬러 피커 클릭 처리
            if self.cfg_colorpick and not handled:
                cp_rects = getattr(self, '_cp_rects', {})
                for col, rect in cp_rects.items():
                    if rect.collidepoint(mx, my):
                        self.cfg[self.cfg_colorpick] = list(col)
                        self.cfg_colorpick = None
                        handled = True
                        break
                if not handled:
                    self.cfg_colorpick = None
                    handled = True

            if not handled:
                # 설정 항목 클릭
                for item_info in getattr(self, '_settings_click_rects', []):
                    key, rect, stype = item_info
                    if rect.collidepoint(mx, my):
                        if stype == 'dropdown':
                            self.cfg_dropdown = key
                        elif stype == 'color':
                            self.cfg_colorpick = key
                        elif stype == 'slider':
                            val = max(0, min(100, int((mx - rect.x) / rect.w * 100)))
                            self.cfg[key] = val
                            self._slider_dragging = key
                        elif stype == 'toggle':
                            self.cfg[key] = not self.cfg[key]
                        elif stype == 'stepper_down':
                            self.cfg['font_size'] = max(16, self.cfg['font_size'] - 2)
                            self._apply_font_size()
                            self._init_settings_test()
                        elif stype == 'stepper_up':
                            self.cfg['font_size'] = min(40, self.cfg['font_size'] + 2)
                            self._apply_font_size()
                            self._init_settings_test()
                        break

                # 초기화 버튼
                reset_r = getattr(self, '_st_reset_rect', None)
                if reset_r and reset_r.collidepoint(mx, my):
                    self._init_settings_test()

                # 뒤로 버튼
                back_r = getattr(self, '_st_back_rect', None)
                if back_r and back_r.collidepoint(mx, my):
                    self._apply_settings()
                    self.state = 'menu'
                    self._reset()

    def _apply_font_size(self):
        sz = self.cfg['font_size']
        chosen = None
        available = set(pygame.font.get_fonts())
        for f in ["malgungothic", "malgunbd", "malgun", "gulim", "gulimche",
                   "dotum", "dotumche", "batang", "batangche",
                   "nanumsquareroundbold", "nanumgothicbold", "nanumgothic"]:
            if f in available:
                chosen = f
                break
        self.F['text'] = pygame.font.SysFont(chosen, sz)

    def _apply_settings(self):
        """설정 값을 실제 앱에 적용"""
        rw, rh = self.cfg['resolution']
        if (rw, rh) != (self.W, self.H):
            self.W, self.H = rw, rh
            self.disp = pygame.display.set_mode((self.W, self.H))
            self._update_layout_scale()
            self._setup_fonts()
            self._init_stars()
            self._build_fade_overlays()
        self.FPS = self.cfg['fps']
        self._apply_font_size()

    # ─── 설정 화면 그리기 ────────────────────────────────────
    def _draw_settings(self):
        self.disp.fill(BG)
        half = self.W // 2

        # 좌측: 설정 패널
        pygame.draw.rect(self.disp, PANEL, (0, 0, half, self.H))
        pygame.draw.line(self.disp, BORDER, (half, 0), (half, self.H), 2)

        # 헤더
        title = self.F['heading'].render("설  정", True, WHITE)
        self.disp.blit(title, (half // 2 - title.get_width() // 2, 20))
        pygame.draw.line(self.disp, BORDER, (20, 60), (half - 20, 60), 1)

        # 뒤로 가기 버튼
        back_s = self.F['btn_sm'].render("← 메뉴로", True, WHITE)
        bw = back_s.get_width() + 20
        back_rect = pygame.Rect(20, 18, bw, 28)
        self._st_back_rect = back_rect
        bk_hover = back_rect.collidepoint(self.mouse)
        pygame.draw.rect(self.disp, BTN_HOVER if bk_hover else BTN_BG,
                         back_rect, border_radius=6)
        self.disp.blit(back_s, (30, 21))

        # 설정 항목들
        self._settings_click_rects = []
        self._dd_rects = {}
        self._cp_rects = {}
        sy = int(78 * self.H / self.BASE_H)
        f_lbl = self.F['small']
        f_val = self.F['btn_sm']

        deferred_popup = None  # 드롭다운/컬러피커는 모든 항목 위에 그리기 위해 후처리

        for item in self.SETTINGS_ITEMS:
            key   = item['key']
            label = item['label']
            stype = item['type']

            # 라벨
            ls = f_lbl.render(label, True, STAT_LBL)
            self.disp.blit(ls, (36, sy + 8))

            ctrl_x = half - int(220 * self.W / self.BASE_W)
            ctrl_w = int(190 * self.W / self.BASE_W)
            ctrl_h = int(30 * self.H / self.BASE_H)

            if stype == 'dropdown':
                # 현재 값 표시
                if key == 'resolution':
                    v = self.cfg[key]
                    val_str = f"{v[0]}×{v[1]}"
                    options = RESOLUTION_OPTIONS
                elif key == 'fps':
                    val_str = f"{self.cfg[key]} Hz"
                    options = FPS_OPTIONS
                else:
                    val_str = str(self.cfg[key])
                    options = []

                rect = pygame.Rect(ctrl_x, sy + 4, ctrl_w, ctrl_h)
                hover = rect.collidepoint(self.mouse)
                pygame.draw.rect(self.disp, BTN_HOVER if hover else BTN_BG,
                                 rect, border_radius=6)
                pygame.draw.rect(self.disp, ACCENT if hover else BORDER,
                                 rect, 1, border_radius=6)
                vs = f_val.render(val_str, True, WHITE)
                self.disp.blit(vs, (rect.centerx - vs.get_width() // 2,
                                    rect.centery - vs.get_height() // 2))
                # ▼ 표시
                arrow = f_lbl.render("▼", True, GRAY)
                self.disp.blit(arrow, (rect.right - 20, rect.centery - arrow.get_height() // 2))
                self._settings_click_rects.append((key, rect, 'dropdown'))

                # 드롭다운이 열려 있으면 후처리로 예약
                if self.cfg_dropdown == key:
                    deferred_popup = ('dropdown', key, ctrl_x, ctrl_w, ctrl_h, rect.bottom, options)

            elif stype == 'stepper':
                val = self.cfg[key]
                # < 버튼
                lr = pygame.Rect(ctrl_x, sy + 4, 36, ctrl_h)
                lh = lr.collidepoint(self.mouse)
                pygame.draw.rect(self.disp, BTN_HOVER if lh else BTN_BG,
                                 lr, border_radius=6)
                ls2 = f_val.render("◀", True, WHITE)
                self.disp.blit(ls2, (lr.centerx - ls2.get_width() // 2,
                                     lr.centery - ls2.get_height() // 2))
                self._settings_click_rects.append((key, lr, 'stepper_down'))
                # 값
                vs = f_val.render(str(val), True, WHITE)
                self.disp.blit(vs, (ctrl_x + ctrl_w // 2 - vs.get_width() // 2,
                                    sy + 4 + ctrl_h // 2 - vs.get_height() // 2))
                # > 버튼
                rr = pygame.Rect(ctrl_x + ctrl_w - 36, sy + 4, 36, ctrl_h)
                rh = rr.collidepoint(self.mouse)
                pygame.draw.rect(self.disp, BTN_HOVER if rh else BTN_BG,
                                 rr, border_radius=6)
                rs = f_val.render("▶", True, WHITE)
                self.disp.blit(rs, (rr.centerx - rs.get_width() // 2,
                                    rr.centery - rs.get_height() // 2))
                self._settings_click_rects.append((key, rr, 'stepper_up'))

            elif stype == 'color':
                col = tuple(self.cfg[key])
                rect = pygame.Rect(ctrl_x, sy + 4, ctrl_w, ctrl_h)
                pygame.draw.rect(self.disp, col, rect, border_radius=6)
                pygame.draw.rect(self.disp, WHITE, rect, 1, border_radius=6)
                self._settings_click_rects.append((key, rect, 'color'))

                # 컬러 피커가 열려 있으면 후처리로 예약
                if self.cfg_colorpick == key:
                    deferred_popup = ('color', key, ctrl_x, ctrl_w, ctrl_h, rect.bottom)

            elif stype == 'slider':
                val = self.cfg[key]   # 0~100
                track_rect = pygame.Rect(ctrl_x, sy + 4 + ctrl_h // 2 - 3, ctrl_w, 6)
                pygame.draw.rect(self.disp, DARK_GRAY, track_rect, border_radius=3)
                fill_w = int(ctrl_w * val / 100)
                fill_rect = pygame.Rect(ctrl_x, track_rect.y, fill_w, 6)
                pygame.draw.rect(self.disp, ACCENT, fill_rect, border_radius=3)
                # 핸들
                handle_x = ctrl_x + fill_w
                handle_r = pygame.Rect(handle_x - 8, sy + 4 + ctrl_h // 2 - 8, 16, 16)
                pygame.draw.circle(self.disp, WHITE, handle_r.center, 8)
                # 값 표시
                vs = f_val.render(f"{val}%", True, STAT_VAL)
                self.disp.blit(vs, (ctrl_x + ctrl_w + 10, sy + 4 + ctrl_h // 2 - vs.get_height() // 2))
                # 클릭/드래그 영역 (트랙 전체)
                slider_area = pygame.Rect(ctrl_x, sy + 4, ctrl_w, ctrl_h)
                self._settings_click_rects.append((key, slider_area, 'slider'))

            elif stype == 'toggle':
                val = self.cfg[key]
                rect = pygame.Rect(ctrl_x, sy + 4, 80, ctrl_h)
                hover = rect.collidepoint(self.mouse)
                bg_c = CORRECT if val else ERROR
                pygame.draw.rect(self.disp, bg_c, rect, border_radius=6)
                ts = f_val.render("ON" if val else "OFF", True, WHITE)
                self.disp.blit(ts, (rect.centerx - ts.get_width() // 2,
                                    rect.centery - ts.get_height() // 2))
                self._settings_click_rects.append((key, rect, 'toggle'))

            sy += int(48 * self.H / self.BASE_H)

        # ── 팝업 후처리: 드롭다운 / 컬러 피커를 모든 항목 위에 그림 ──
        if deferred_popup is not None:
            if deferred_popup[0] == 'dropdown':
                _, key, ctrl_x, ctrl_w, ctrl_h, top_y, options = deferred_popup
                dy = top_y + 2
                for opt in options:
                    if key == 'resolution':
                        opt_str = f"{opt[0]}×{opt[1]}"
                    elif key == 'fps':
                        opt_str = f"{opt} Hz"
                    else:
                        opt_str = str(opt)
                    orect = pygame.Rect(ctrl_x, dy, ctrl_w, ctrl_h)
                    ohover = orect.collidepoint(self.mouse)
                    pygame.draw.rect(self.disp, BTN_HOVER if ohover else PANEL2,
                                     orect, border_radius=4)
                    pygame.draw.rect(self.disp, BORDER, orect, 1, border_radius=4)
                    os = f_val.render(opt_str, True, WHITE if ohover else BTN_TEXT)
                    self.disp.blit(os, (orect.centerx - os.get_width() // 2,
                                        orect.centery - os.get_height() // 2))
                    self._dd_rects[opt] = orect
                    dy += ctrl_h + 2
            elif deferred_popup[0] == 'color':
                _, key, ctrl_x, ctrl_w, ctrl_h, top_y = deferred_popup
                px = ctrl_x
                py = top_y + 4
                cols_per_row = 8
                cs = 24
                cgap = 3
                # 배경 패널
                rows = (len(COLOR_PALETTE) + cols_per_row - 1) // cols_per_row
                panel_w = cols_per_row * (cs + cgap) - cgap + 8
                panel_h = rows * (cs + cgap) - cgap + 8
                pygame.draw.rect(self.disp, PANEL2,
                                 (px - 4, py - 4, panel_w, panel_h), border_radius=6)
                pygame.draw.rect(self.disp, BORDER,
                                 (px - 4, py - 4, panel_w, panel_h), 1, border_radius=6)
                for ci, pc in enumerate(COLOR_PALETTE):
                    row, col_i = divmod(ci, cols_per_row)
                    cr = pygame.Rect(px + col_i * (cs + cgap),
                                     py + row * (cs + cgap), cs, cs)
                    pygame.draw.rect(self.disp, pc, cr, border_radius=4)
                    if tuple(self.cfg[key]) == pc:
                        pygame.draw.rect(self.disp, WHITE, cr, 2, border_radius=4)
                    self._cp_rects[pc] = cr

        # 우측: 테스트 타이핑
        self._draw_settings_test()

    def _draw_settings_test(self):
        """설정 화면 우측 테스트 타이핑 영역"""
        s = self.st
        if s is None:
            return

        half = self.W // 2
        ox   = half + 40    # 텍스트 시작 X
        dt   = 1.0 / self.FPS
        f    = self.F['text']
        cursor_i = len(s['typed'])

        # 헤더
        th = self.F['heading'].render("미리보기", True, WHITE)
        self.disp.blit(th, (half + (half // 2) - th.get_width() // 2, 20))

        # 초기화 버튼
        rs = self.F['btn_sm'].render("초기화", True, WHITE)
        rw = rs.get_width() + 20
        rr = pygame.Rect(self.W - rw - 20, 18, rw, 28)
        self._st_reset_rect = rr
        rh = rr.collidepoint(self.mouse)
        pygame.draw.rect(self.disp, BTN_HOVER if rh else BTN_BG, rr, border_radius=6)
        pygame.draw.rect(self.disp, BORDER, rr, 1, border_radius=6)
        self.disp.blit(rs, (rr.x + 10, rr.centery - rs.get_height() // 2))

        pygame.draw.line(self.disp, BORDER, (half + 20, 60), (self.W - 20, 60), 1)

        # 커서 애니메이션
        target_item = None
        for item in s['layout']:
            if item['i'] == cursor_i:
                target_item = item
                break
        if target_item:
            tx = ox + target_item['x']
            ty = self.TEXT_Y + target_item['y'] - s['scroll']
            tw = target_item['w']
            if s['composing']:
                tw = max(tw, f.size(s['composing'])[0])
            s['cursor_target_x'] = tx
            s['cursor_target_y'] = ty
            s['cursor_w'] = tw
            if not s['cursor_inited']:
                s['cursor_x'] = tx
                s['cursor_y'] = ty
                s['cursor_inited'] = True

        spd = min(self.CURSOR_EASE_SP * dt, 1.0)
        s['cursor_x'] += (s['cursor_target_x'] - s['cursor_x']) * spd
        s['cursor_y'] += (s['cursor_target_y'] - s['cursor_y']) * spd

        # 클립
        area_top = 70
        area_h = self.H - area_top - 20
        clip = pygame.Rect(half, area_top, half, area_h)
        self.disp.set_clip(clip)

        # 커서 배경
        if s['cursor_inited']:
            cx, cy, cw = s['cursor_x'], s['cursor_y'], s['cursor_w']
            if s['composing'] and not s['composing_correct']:
                cbg = ERROR_BG
                cbdr = tuple(self.cfg['error_color'])
            else:
                cbg = (60, 52, 12)
                cbdr = tuple(self.cfg['cursor_color'])
            pygame.draw.rect(self.disp, cbg,
                             (cx, cy + 2, cw, self.LINE_H - 6), border_radius=3)
            pygame.draw.rect(self.disp, cbdr,
                             (cx, cy + 2, cw, self.LINE_H - 6), 1, border_radius=3)

        # 글자 렌더링
        for item in s['layout']:
            i = item['i']
            disp_ch = item['ch']
            is_nl = item.get('newline', False)
            sx = ox + item['x']
            sy = self.TEXT_Y + item['y'] - s['scroll']

            if sy + self.LINE_H < area_top or sy > area_top + area_h:
                continue
            if is_nl:
                continue

            if i < cursor_i:
                if self._st_char_jamo_correct(i):
                    color = tuple(self.cfg['correct_color'])
                else:
                    pygame.draw.rect(self.disp, ERROR_BG,
                                     (sx, sy + 2, item['w'], self.LINE_H - 6),
                                     border_radius=3)
                    color = tuple(self.cfg['error_color'])
                surf = f.render(disp_ch, True, color)
                self.disp.blit(surf, (sx, sy))
            elif i == cursor_i:
                surf = f.render(disp_ch, True, tuple(self.cfg['untyped_color']))
                self.disp.blit(surf, (sx, sy))
                if s['composing']:
                    cc = (255, 255, 255) if s['composing_correct'] \
                         else tuple(self.cfg['error_color'])
                    cs = f.render(s['composing'], True, cc)
                    self.disp.blit(cs, (s['cursor_x'], s['cursor_y']))
            else:
                surf = f.render(disp_ch, True, tuple(self.cfg['untyped_color']))
                self.disp.blit(surf, (sx, sy))

        # 파티클
        alive = []
        for p in s['particles']:
            p['life'] -= dt
            if p['life'] <= 0:
                continue
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 300 * dt
            alive.append(p)
            alpha = int(255 * (p['life'] / p['max_life']))
            sz = int(p['size'] * (p['life'] / p['max_life']))
            if sz < 1:
                continue
            ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*p['color'], alpha), (sz, sz), sz)
            self.disp.blit(ps, (p['x'] - sz, p['y'] - sz))
        s['particles'] = alive

        self.disp.set_clip(None)

        # 테스트 영역 셰이크 (가벼운 오프셋)
        if s['shake_start'] > 0:
            st = (time.time() - s['shake_start']) / 0.15
            if st < 1.0:
                amp = s['shake_intensity'] * (1.0 - st)
                # 셰이크는 시각적으로만 표현 (메인 셰이크와 독립)
            else:
                s['shake_start'] = 0

    # ─── 풀 콤보 연출 ─────────────────────────────────────────
    def _spawn_fullcombo_particles(self):
        """모든 글자에서 대량 파티클 폭발"""
        for item in self.layout:
            if item.get('newline'):
                continue
            cx = self.TEXT_X + item['x'] + item['w'] / 2
            cy = self.TEXT_Y + item['y'] + self.LINE_H / 2 - self.scroll
            for _ in range(4):
                angle = random.uniform(-math.pi, math.pi)
                speed = random.uniform(200, 600)
                life  = random.uniform(0.8, 1.8)
                size  = random.uniform(3, 7)
                self.particles.append({
                    'x': cx + random.uniform(-4, 4),
                    'y': cy + random.uniform(-4, 4),
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - 150,
                    'life': life,
                    'max_life': life,
                    'size': size,
                    'color': (255, 255, 255),
                })
        # 글자 흩뿌리기 데이터 생성
        self.fc_chars = []
        f = self.F['text']
        for item in self.layout:
            if item.get('newline') or not item['ch']:
                continue
            cx = self.TEXT_X + item['x']
            cy = self.TEXT_Y + item['y'] - self.scroll
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(100, 350)
            self.fc_chars.append({
                'ch': item['ch'],
                'x': float(cx), 'y': float(cy),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 80,
                'rot': random.uniform(-300, 300),   # 도/초
                'angle': 0.0,
                'alpha': 255.0,
            })

    def _fullcombo_bg(self):
        """흰색 플래시 → 서서히 원래 배경으로"""
        t = (time.time() - self.fc_start) / self.FULLCOMBO_DUR
        t = min(t, 1.0)
        # 처음 0.15초 강한 흰색 플래시, 이후 감쇠
        if t < 0.075:
            strength = 1.0
        else:
            strength = max(0, 1.0 - ((t - 0.075) / 0.4)) ** 2
        white = (255, 255, 255)
        base = CH_BG if self.challenge_mode else BG
        return tuple(int(base[i] + (white[i] - base[i]) * strength) for i in range(3))

    def _draw_fullcombo(self):
        dt = 1.0 / self.FPS
        t  = time.time() - self.fc_start

        # 진행 중 추가 셰이크 (2초까지만, 점점 감소)
        if t < 2.0:
            remaining = max(0, 1.0 - t / 2.0)
            if random.random() < remaining:
                self._trigger_shake(int(20 * remaining) + 4)

        # 진행 중 추가 파티클 (화면 랜덤 위치에서)
        if t < 1.5:
            for _ in range(8):
                sx = random.uniform(60, self.W - 60)
                sy = random.uniform(self.TEXT_Y, self.H - self.BOT_H)
                angle = random.uniform(-math.pi, math.pi)
                speed = random.uniform(100, 400)
                life  = random.uniform(0.4, 1.0)
                size  = random.uniform(2, 6)
                self.particles.append({
                    'x': sx, 'y': sy,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - 100,
                    'life': life,
                    'max_life': life,
                    'size': size,
                    'color': (255, 255, 255),
                })

        # 흩어지는 글자들 업데이트 + 그리기
        f = self.F['text']
        for c in self.fc_chars:
            c['x']     += c['vx'] * dt
            c['y']     += c['vy'] * dt
            c['vy']    += 200 * dt    # 중력
            c['angle'] += c['rot'] * dt
            c['alpha']  = max(0, c['alpha'] - 180 * dt)

            if c['alpha'] > 0:
                surf = f.render(c['ch'], True, (255, 255, 255))
                rotated = pygame.transform.rotate(surf, c['angle'])
                rotated.set_alpha(int(c['alpha']))
                self.disp.blit(rotated, (c['x'], c['y']))

        # 파티클 업데이트 + 그리기
        self._update_particles(dt)
        self._draw_particles()

        # "FULL COMBO!!" 텍스트
        fc_t = min(t / 0.4, 1.0)   # 0.4초에 걸쳐 등장
        scale = 1.0 + 0.6 * (1.0 - fc_t) ** 2   # ease-out 확대
        alpha = min(255, int(255 * fc_t * 2))

        main_color = (255, 72, 72) if self.challenge_mode else (255, 218, 72)
        base_surf = self.F['result_big'].render("FULL COMBO!!", True, main_color)
        sw = int(base_surf.get_width() * scale)
        sh = int(base_surf.get_height() * scale)
        scaled = pygame.transform.smoothscale(base_surf, (sw, sh))
        cx_fc = self.W // 2 - sw // 2
        cy_fc = self.H // 2 - sh // 2

        if self.challenge_mode:
            # 색수차(크로마틱 글리치) 이펙트
            glitch_pulse = 0.5 + 0.5 * math.sin(t * 12)
            offset = int(3 + 4 * glitch_pulse)
            # 빈번한 글리치 점프 (랜덤 횡 오프셋)
            jitter_x = 0
            if random.random() < 0.3:
                jitter_x = random.randint(-8, 8)
            # 빨강 채널
            r_surf = self.F['result_big'].render("FULL COMBO!!", True, (255, 0, 0))
            r_scaled = pygame.transform.smoothscale(r_surf, (sw, sh))
            r_scaled.set_alpha(min(alpha, 120))
            self.disp.blit(r_scaled, (cx_fc - offset + jitter_x, cy_fc))
            # 파랑 채널
            b_surf = self.F['result_big'].render("FULL COMBO!!", True, (0, 100, 255))
            b_scaled = pygame.transform.smoothscale(b_surf, (sw, sh))
            b_scaled.set_alpha(min(alpha, 120))
            self.disp.blit(b_scaled, (cx_fc + offset + jitter_x, cy_fc))

        scaled.set_alpha(alpha)
        self.disp.blit(scaled, (cx_fc, cy_fc))

        # 도전 모드: 서브 텍스트
        if self.challenge_mode:
            sub_t = max(0, min((t - 0.3) / 0.4, 1.0))  # 0.3초 뒤 등장
            if sub_t > 0:
                sub_surf = self.F['heading'].render("도전 모드 풀 콤보 달성!", True, (255, 180, 180))
                sub_alpha = min(255, int(255 * sub_t * 2))
                # 색수차
                s_offset = int(2 + 3 * glitch_pulse)
                sr = self.F['heading'].render("도전 모드 풀 콤보 달성!", True, (255, 0, 0))
                sr.set_alpha(min(sub_alpha, 90))
                sb = self.F['heading'].render("도전 모드 풀 콤보 달성!", True, (0, 100, 255))
                sb.set_alpha(min(sub_alpha, 90))
                sub_x = self.W // 2 - sub_surf.get_width() // 2
                sub_y = cy_fc + sh + 12
                self.disp.blit(sr, (sub_x - s_offset, sub_y))
                self.disp.blit(sb, (sub_x + s_offset, sub_y))
                sub_surf.set_alpha(sub_alpha)
                self.disp.blit(sub_surf, (sub_x, sub_y))

        # 마지막 0.3초: 검정 페이드아웃
        fade_start = self.FULLCOMBO_DUR - self.FC_FADE_DUR
        if t >= fade_start:
            fade_t = min((t - fade_start) / self.FC_FADE_DUR, 1.0)
            fade_alpha = int(255 * fade_t)
            fade_overlay = pygame.Surface((self.W, self.H))
            fade_overlay.fill((0, 0, 0))
            fade_overlay.set_alpha(fade_alpha)
            self.disp.blit(fade_overlay, (0, 0))

        # 연출 종료 → 페이드인 상태로 전환
        if t >= self.FULLCOMBO_DUR:
            self.result_time = time.time()
            self.fc_fadein_start = time.time()
            self.state = 'result'

    # ─── 결과 화면 ────────────────────────────────────────────
    def _draw_result(self):
        # 반투명 오버레이
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov_col = (18, 5, 5, 210) if self.challenge_mode else (5, 7, 18, 210)
        overlay.fill(ov_col)
        self.disp.blit(overlay, (0, 0))

        sc = min(self.W / self.BASE_W, self.H / self.BASE_H)
        cw, ch = int(580 * sc), int(522 * sc)
        cx = self.W // 2 - cw // 2
        cy = self.H // 2 - ch // 2

        # 카드
        pygame.draw.rect(self.disp, self.c(PANEL2, CH_PANEL2), (cx, cy, cw, ch), border_radius=18)
        pygame.draw.rect(self.disp, self.c(ACCENT, CH_ACCENT), (cx, cy, cw, ch), 2, border_radius=18)

        # 완료 헤딩
        head_text = "도전 완료!" if self.challenge_mode else "연습 완료!"
        head = self.F['result_lbl'].render(head_text, True, self.c(ACCENT, CH_ACCENT))
        self.disp.blit(head, (cx + cw // 2 - head.get_width() // 2, cy + int(28 * sc)))

        pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER),
                         (cx + int(40 * sc), cy + int(66 * sc)),
                         (cx + cw - int(40 * sc), cy + int(66 * sc)), 1)

        # 통계 목록
        stats = [
            ("최종 타수",   f"{self.cpm} 타/분"),
            ("정 확 도",    f"{self.accuracy:.1f}%"),
            ("소요 시간",   self._fmt_time(self.elapsed)),
            ("전체 타 수",   f"{len(self.target_jamo)} 타"),
            ("최대 콤보",   f"{self.max_combo} 콤보"),
            ("Backspace",  f"{self.backspace_count} 회"),
        ]
        row_h = int(52 * sc)
        sy = cy + int(82 * sc)
        pad = int(50 * sc)
        for lbl, val in stats:
            ls = self.F['result_lbl'].render(lbl, True, self.c(STAT_LBL, CH_STAT_LBL))
            vs = self.F['result_lbl'].render(val, True, self.c(STAT_VAL, CH_STAT_VAL))
            self.disp.blit(ls, (cx + pad,            sy))
            self.disp.blit(vs, (cx + cw - pad - vs.get_width(), sy))
            pygame.draw.line(self.disp, self.c(BORDER, CH_BORDER),
                             (cx + int(36 * sc), sy + int(34 * sc)),
                             (cx + cw - int(36 * sc), sy + int(34 * sc)), 1)
            sy += row_h

        # 정확도에 따른 평가 메시지
        acc = self.accuracy
        if acc >= 98:
            grade, gcol = "완벽해요!", self.c(CORRECT, CH_CORRECT)
        elif acc >= 95:
            grade, gcol = "훌륭해요!", (130, 200, 255)
        elif acc >= 90:
            grade, gcol = "잘 하셨어요!", self.c(STAT_VAL, CH_STAT_VAL)
        else:
            grade, gcol = "조금 더 연습해요!", self.c(GRAY, CH_GRAY)

        gsurf = self.F['subhead'].render(grade, True, gcol)
        self.disp.blit(gsurf, (cx + cw // 2 - gsurf.get_width() // 2, sy + int(4 * sc)))

        # 돌아가기 버튼
        btn_w, btn_h = int(220 * sc), int(44 * sc)
        br = pygame.Rect(cx + cw // 2 - btn_w // 2, cy + ch - int(66 * sc), btn_w, btn_h)
        bhover = br.collidepoint(self.mouse)
        pygame.draw.rect(self.disp, self.c(BTN_HOVER, CH_BTN_HOVER) if bhover
                         else self.c(BTN_BG, CH_BTN_BG), br, border_radius=10)
        pygame.draw.rect(self.disp, self.c(ACCENT, CH_ACCENT), br, 1, border_radius=10)
        bl = self.F['btn'].render("메뉴로 돌아가기", True, self.c(WHITE, CH_WHITE))
        self.disp.blit(bl, (br.centerx - bl.get_width() // 2,
                             br.centery - bl.get_height() // 2))

        hint = self.F['small'].render("클릭하여 메뉴로 돌아가기", True,
                                      self.c(DARK_GRAY, CH_DARK_GRAY))
        self.disp.blit(hint, (self.W // 2 - hint.get_width() // 2, cy + ch + int(18 * sc)))

        # 풀 콤보 후 페이드인 (검정 → 투명)
        fi_start = getattr(self, 'fc_fadein_start', 0)
        if fi_start > 0:
            fi_t = (time.time() - fi_start) / self.FC_FADE_DUR
            if fi_t < 1.0:
                fade_alpha = int(255 * (1.0 - fi_t))
                fade_overlay = pygame.Surface((self.W, self.H))
                fade_overlay.fill((0, 0, 0))
                fade_overlay.set_alpha(fade_alpha)
                self.disp.blit(fade_overlay, (0, 0))
            else:
                self.fc_fadein_start = 0

    # ─── 유틸 ─────────────────────────────────────────────────
    @staticmethod
    def _fmt_time(secs: float) -> str:
        m = int(secs) // 60
        s = int(secs) % 60
        return f"{m:02d}:{s:02d}"
