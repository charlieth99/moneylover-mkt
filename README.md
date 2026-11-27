# Money Lover · Marketing skills cho Claude

Bộ skill dùng chung của team Marketing Money Lover.

## Skill hiện có

### `app-market-research`: nghiên cứu thị trường app trên Google Play

Bạn chỉ cần nói tự nhiên với Claude, ví dụ:
- "Phân tích app quản lý chi tiêu ở Philippines, so với Money Lover"
- "Top app học tiếng Anh ở Thái Lan, người dùng chê gì?"
- "Khoảng trống thị trường cho Money Lover ở Malaysia"

Claude sẽ:
1. Crawl Google Play của quốc gia đó theo nhóm app.
2. Xếp hạng app theo số review bằng ngôn ngữ địa phương trong 30 ngày.
3. Vẽ xu hướng 6 tháng và lập bản đồ khoảng 25 tính năng.
4. Phân tích review khen/chê, kèm trích dẫn đã dịch sang tiếng Việt.
5. Chấm điểm các khoảng trống và đề xuất lộ trình 90 ngày cho app bạn chọn.
6. Dựng một dashboard tương tác để chia sẻ với team.

**Đã có sẵn:** tiếng Indonesia, tiếng Việt, tiếng Thái; nhóm app tài chính cá nhân. Thị trường hoặc nhóm app mới thì Claude tự thêm cấu hình theo hướng dẫn trong skill.

**Cần biết khi đọc số liệu:**
- Số review không phải số download.
- Lượt cài Google công bố là số toàn cầu.
- Điểm khoảng trống là nhận định của Claude, đã ghi rõ trên dashboard.
- Chỉ có dữ liệu Android.
- Muốn có download thật, dùng `scripts/snapshot_installs.py`: chụp lượt cài mỗi ngày rồi lấy chênh lệch.

## Cài đặt

**Claude.ai (web / app):** tải file [`dist/app-market-research.skill`](dist/app-market-research.skill), mở trong Claude rồi bấm **Save skill**. Hoặc vào Settings → Capabilities → Skills và tải file lên.

**Claude Code:** chạy hai lệnh sau.
```
/plugin marketplace add charlieth99/moneylover-mkt
/plugin install market-research@moneylover-mkt
```

**Yêu cầu khi chạy:** Python 3, `pip install google-play-scraper`, và có mạng tới play.google.com.

## Cấu trúc

```
.claude-plugin/marketplace.json        danh sách plugin của team
plugins/market-research/               plugin (skill + scripts)
  skills/app-market-research/
    SKILL.md                           quy trình Claude làm theo
    scripts/                           crawl, analyze, export, snapshot_installs, langs
    references/                        phương pháp, cấu hình nhóm app, schema dữ liệu
    assets/dashboard_page.html         mẫu dashboard
dist/app-market-research.skill         bản đóng gói để cài vào Claude.ai
```

## Thêm skill mới

Tạo một thư mục trong `plugins/<tên>/skills/<tên-skill>/SKILL.md`, khai báo plugin trong `.claude-plugin/marketplace.json`, rồi đóng gói lại file `.skill` vào `dist/`.
