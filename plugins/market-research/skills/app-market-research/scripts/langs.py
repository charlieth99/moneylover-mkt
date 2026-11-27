"""Language profiles: how to tell a review is written by a local user, and how to tag its themes.

Each profile has:
  is_local(text) -> bool      the review looks written in this market's language
  contrast                    regex for "but / however" (praise that still carries a complaint)
  themes                      ordered dict name -> regex; complaint themes first, then praise themes
  n_complaint                 how many of the first themes are complaints
Theme names are written in the report language (Vietnamese by default) so the dashboard can show them.

To add a market, copy a profile, translate the marker words and theme patterns, and register it in PROFILES.
"""
import re

# ---------- Indonesian ----------
_ID_ONLY = set("""gak ga nggak ngga enggak engga banget bgt aja aj udah udh sih dong deh kok kak min mimin
bisa tidak tdk bagus mantap mantul membantu terbantu sekali pake pakai cuma doang gimana bikin kasih makasih
kalo kalau jadi jd sama sm lagi lg tolong mohon kenapa knp dimana gampang mudah praktis keren rekomen
aplikasinya fiturnya iklannya iklan emang memang yg dgn utk""".split())
_MS_ONLY = set("""tak boleh sikit awak korang best gila sbb ke kat nak dah pasal guna berguna tu ni dekat macam mcm
takde xde x camne ape""".split())
_ID_SHARED = set("sangat yang dan ini itu untuk saya aplikasi dengan ada sudah tapi tetapi juga lebih masih".split())


def _is_indonesian(text):
    w = re.findall(r"[a-z]+", (text or "").lower())
    idn = sum(t in _ID_ONLY for t in w)
    ms = sum(t in _MS_ONLY for t in w)
    sh = sum(t in _ID_SHARED for t in w)
    return ms <= idn and (idn >= 1 or sh >= 2)


ID = {
    "play_lang": "id",
    "is_local": _is_indonesian,
    "contrast": r"\b(tapi|tp|tpi|namun|sayang(?:nya)?|cuma|cuman|kurang)\b",
    "wish": r"tolong|mohon|semoga|kalau bisa|kalo bisa|saran|tambah(?:kan|in)? fitur|request",
    "n_complaint": 7,
    "themes": {
        "Quảng cáo nhiều": r"iklan|\bads\b|advertis",
        "Giá / bắt trả premium": r"premium|berbayar|bayar|langganan|subscri|mahal|\bpro\b|beli|harga|dibatasi|terbatas|limit",
        "Mất dữ liệu / sao lưu": r"hilang|ilang|kehapus|terhapus|kehilangan|backup|cadang|restore|pulih",
        "Lỗi / crash / chậm": r"error|eror|bug|crash|force close|keluar sendiri|lemot|lambat|\blag\b|ngelag|nge-?hang|macet|tidak bisa dibuka|gak bisa dibuka|ga bisa dibuka|gagal",
        "Đăng nhập / sync": r"login|log in|masuk akun|sinkron|sync|akun saya|daftar",
        "Sau cập nhật bị hỏng": r"update|pembaruan|versi baru|diperbarui",
        "Muốn thêm tính năng": r"tolong (?:tambah|ditambah|adakan)|mohon (?:tambah|ditambah)|semoga (?:ada|bisa|ditambah)|kalau bisa|kalo bisa|saran|request",
        "Dễ dùng / đơn giản": r"mudah|gampang|simpel|simple|sederhana|praktis|user friendly|ringan",
        "Giúp đạt mục tiêu": r"membantu|terbantu|ngatur|mengatur|kontrol|hemat|nabung|menabung|disiplin|bermanfaat",
        "Giao diện đẹp": r"tampilan|desain|design|\bui\b|lucu|cute|imut|warna|cantik|estetik|menarik",
        "Báo cáo / thống kê": r"grafik|laporan|statistik|chart|rekap|report",
        "Tự động / AI": r"otomatis|\bauto|\bai\b|scan|struk|notifikasi|chat|suara|voice",
    },
}

# ---------- Vietnamese ----------
_VI_CHARS = re.compile(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
_VI_PLAIN = set("""khong ko k dc duoc rat tot hay qua nhung minh cua nay xai dung ung dung tien chi tieu thu ok ma thi
la va voi cho cai nhieu it de su giup quan ly can them nua lam bi loi""".split())


def _is_vietnamese(text):
    t = text or ""
    if _VI_CHARS.search(t):
        return True
    return sum(x in _VI_PLAIN for x in re.findall(r"[a-z]+", t.lower())) >= 3


VI = {
    "play_lang": "vi",
    "is_local": _is_vietnamese,
    "contrast": r"\b(nhưng|tuy nhiên|mỗi tội|chỉ tiếc|tiếc là|nhưng mà|có điều|hơi)\b",
    "wish": r"mong|nên có|thêm tính năng|thêm chức năng|giá như|đề xuất|góp ý|bổ sung|ước gì",
    "n_complaint": 7,
    "themes": {
        "Quảng cáo nhiều": r"quảng cáo|\bqc\b|\bads?\b",
        "Giá / bắt trả premium": r"premium|trả phí|mất phí|tính phí|thu phí|nâng cấp|đắt|mua gói|\bvip\b|\bpro\b|subscription|gia hạn|tốn tiền|mất tiền",
        "Mất dữ liệu / sao lưu": r"mất (?:hết |sạch |toàn bộ )?(?:dữ liệu|data|ghi chép)|bay (?:hết|sạch|mất)|sao lưu|backup|khôi phục|mất hết",
        "Lỗi / crash / chậm": r"lỗi|\bbug|crash|văng|\bđơ\b|\blag\b|chậm|treo|không vào được|ko vào được|k vào được|không mở được|giật",
        "Đăng nhập / sync": r"đăng nhập|login|đồng bộ|\bsync|tài khoản",
        "Sau cập nhật bị hỏng": r"cập nhật|update|phiên bản mới|bản mới",
        "Muốn thêm tính năng": r"mong (?:app|có|ứng dụng|nhà phát triển|admin|dev|sẽ)|nên có|thêm tính năng|thêm chức năng|giá như|đề xuất|góp ý|bổ sung|ước gì",
        "Dễ dùng / đơn giản": r"dễ (?:dùng|sử dụng|hiểu|thao tác)|đơn giản|tiện lợi|\btiện\b|\bgọn\b|\bnhẹ\b",
        "Giúp đạt mục tiêu": r"quản lý|kiểm soát|tiết kiệm|biết được|theo dõi|hữu ích|hữu dụng",
        "Giao diện đẹp": r"giao diện|\bđẹp\b|dễ thương|cute|màu sắc|xinh",
        "Báo cáo / thống kê": r"báo cáo|biểu đồ|thống kê",
        "Tự động / AI": r"tự động|\bai\b|quét|giọng nói|\bchat|liên kết ngân hàng|đọc thông báo",
    },
}

# ---------- Thai ----------
# Thai script is its own Unicode block (Lao is separate), so script detection is enough.
# Thai has no spaces between words: patterns below avoid \b around Thai text.
_TH_CHARS = re.compile(r"[\u0E01-\u0E5B]")


def _is_thai(text):
    t = text or ""
    return len(_TH_CHARS.findall(t)) >= 3


TH = {
    "play_lang": "th",
    "is_local": _is_thai,
    "contrast": r"แต่|ติดที่|ติดตรง|เสียดาย|ยกเว้น|ถ้า.{0,20}จะดีมาก",
    "wish": r"อยากให้|อยากได้|ควรมี|ขอให้|เพิ่มฟีเจอร์|เพิ่มฟังก์ชัน|แนะนำให้|จะดีมาก",
    "n_complaint": 7,
    "themes": {
        "Quảng cáo nhiều": r"โฆษณา|แอด(?!มิน)|\bads?\b",
        "Giá / bắt trả premium": r"พรีเมียม|premium|เสียเงิน|จ่ายเงิน|แพง|สมัครสมาชิก|ตัดเงิน|รายเดือน|รายปี|\bpro\b|\bvip\b|โปร(?!แกรม|ไฟล์)",
        "Mất dữ liệu / sao lưu": r"ข้อมูล.{0,12}หาย|หายหมด|หายไป|สำรองข้อมูล|แบ็คอัพ|แบคอัพ|backup|กู้คืน|กู้ข้อมูล",
        "Lỗi / crash / chậm": r"บัค|บั๊ก|bug|error|เด้ง|ค้าง|ช้า|แลค|แล็ก|\blag\b|เปิดไม่ได้|เปิดไม่ขึ้น|เข้าไม่ได้|ใช้ไม่ได้|crash",
        "Đăng nhập / sync": r"ล็อกอิน|ล็อคอิน|login|เข้าสู่ระบบ|ซิงค์|sync|บัญชีผู้ใช้",
        "Sau cập nhật bị hỏng": r"อัปเดต|อัพเดท|อัพเดต|อัปเดท|update|เวอร์ชันใหม่",
        "Muốn thêm tính năng": r"อยากให้|อยากได้|ควรมี|ขอให้มี|เพิ่มฟีเจอร์|เพิ่มฟังก์ชัน|แนะนำให้",
        "Dễ dùng / đơn giản": r"ใช้ง่าย|ง่าย|สะดวก|ไม่ซับซ้อน|เรียบง่าย|ไม่ยุ่งยาก",
        "Giúp đạt mục tiêu": r"ช่วย|ประหยัด|ออมเงิน|เก็บเงิน|วินัย|ควบคุม|รู้ว่า|มีประโยชน์|เห็นภาพ",
        "Giao diện đẹp": r"สวย|น่ารัก|ดีไซน์|หน้าตา|\bui\b|สีสัน|มินิมอล",
        "Báo cáo / thống kê": r"กราฟ|รายงาน|สถิติ|สรุปยอด|สรุป",
        "Tự động / AI": r"อัตโนมัติ|(?-i:\bAI\b)|สแกน|สลิป|แชท|เสียง",
    },
}

PROFILES = {"id": ID, "vi": VI, "th": TH}


def get(code):
    if code not in PROFILES:
        raise SystemExit(f"No language profile '{code}'. Add one to scripts/langs.py (see the Indonesian and Vietnamese ones).")
    return PROFILES[code]
