---
name: thue-tncn-vietnam-main
description: "Use when user asks about Vietnamese personal income tax (TNCN), tax finalization (quyet toan), dependent deductions (giam tru gia canh), freelancer/KOL/online seller tax, expat tax, eTax Mobile, tax deadlines, or step-by-step tax calculations. Covers fiscal year 2026 under Law 109/2025/QH15. Triggers on: thue, TNCN, quyet toan, ke khai, HKD, 500 trieu nguong, expat, KOL, seller."
---

# Thuế TNCN Vietnam

Tra cứu thuế TNCN Việt Nam cho kỳ tính thuế 2026, ưu tiên nguồn chính thống và trả lời theo từng nhóm đối tượng.

## Core Workflow

1. Xác định nhóm người nộp thuế và số nguồn thu nhập.
2. Mở đúng file trong `references/` theo nhu cầu thực tế.
3. Kiểm tra `references/sources.md` nếu câu hỏi nhạy về thời gian hoặc cần căn cứ pháp lý.
4. Nếu có phép tính, tách từng bước và đối chiếu lại từng con số với reference.
5. Nếu còn điểm chưa chắc, nói rõ giới hạn và dẫn nguồn chính thống.

> [!CAUTION]
> Nội dung liên quan pháp luật thuế. Chỉ dùng để tham khảo và luôn ưu tiên căn cứ luật, nghị định, thông tư hoặc hướng dẫn chính thức của cơ quan thuế.

## Quick Navigation

| Câu hỏi | File tham khảo |
|---------|---------------|
| Thuế suất, giảm trừ gia cảnh, ngưỡng 20 triệu/500 triệu | `references/tong-quan-thue.md` |
| Ví dụ tính thuế | `references/vi-du-tinh-thue.md` |
| Quyết toán, eTax Mobile, mẫu 02/QTT-TNCN | `references/sop-quyet-toan.md` |
| Freelancer, KOL, seller, sàn TMĐT | `references/freelancer-guide.md` |
| Hộ/cá nhân kinh doanh, kê khai, 01/CNKD, 01/TKN-CNKD | `references/thue-khoan-guide.md` |
| Deadline | `references/deadline-tracker.md` |
| FAQ | `references/faq.md` |
| Nguồn, mức độ tin cậy, ngày cập nhật | `references/sources.md` |
| Routing và verification flow | `references/system-flow.md` |
| Expat, cư trú, không cư trú, DTA | `references/nguoi-nuoc-ngoai-guide.md` |

## Verification Gates

1. Freshness gate  
   Kiểm tra `references/sources.md` để xác nhận ngày cập nhật và xem có văn bản hướng dẫn mới hơn hay không.
2. Cross-check gate  
   Không dùng một file reference duy nhất cho số liệu nhạy cảm nếu câu hỏi liên quan nhiều nguồn thu nhập hoặc nhiều nhóm thu nhập.
3. Citation gate  
   Mọi mốc quan trọng như `15,5 triệu`, `6,2 triệu`, `20 triệu`, `500 triệu`, `5 bậc`, `20% không cư trú` phải kèm căn cứ.

## Anti-Hallucination Rules

| # | Rule | Fallback |
|---|------|----------|
| 1 | Không bịa thuế suất, ngưỡng, mức giảm trừ | "Tôi chưa đủ chắc để kết luận, nên kiểm tra lại tại gdt.gov.vn hoặc congbao.chinhphu.vn." |
| 2 | Không suy luận quy định mới nếu reference chưa phản ánh | "Nội dung này chưa đủ căn cứ trong skill hiện tại." |
| 3 | Không trả lời ngoài phạm vi TNCN | "Skill này chỉ cover thuế TNCN Việt Nam." |
| 4 | Không gộp nhẩm biểu lũy tiến | Tách từng bậc thuế riêng |
| 5 | Không bỏ qua multi-income | Mở đồng thời tất cả reference liên quan |
| 6 | Không đưa SOP quyết toán cho người đã ủy quyền hợp lệ | Hỏi rõ tình trạng ủy quyền trước |

## Calculation Checklist

```text
□ Ghi rõ gross hay net
□ Tách BHXH 8%, BHYT 1,5%, BHTN 1% đúng trần
□ Xác nhận giảm trừ bản thân 15,5 triệu/tháng
□ Xác nhận giảm trừ người phụ thuộc 6,2 triệu/tháng/người
□ Tính thu nhập tính thuế sau bảo hiểm và giảm trừ
□ Áp từng bậc thuế riêng: 10 / 20 / 30 / 40 triệu rồi phần còn lại
□ Cộng lại và nêu căn cứ pháp lý
□ Khuyên người dùng đối soát lại trên eTax hoặc với kế toán/đại lý thuế nếu hồ sơ phức tạp
```

## Nhóm Đối Tượng

| Nhóm | Dấu hiệu | File chính |
|------|---------|-----------|
| Người làm công ăn lương | Thu nhập từ lương, tiền công; cần hỏi thêm đã ủy quyền quyết toán chưa | `tong-quan-thue.md`, `sop-quyet-toan.md` |
| Freelancer/KOL/seller | Dịch vụ, nội dung số, TMĐT, social commerce | `freelancer-guide.md`, `thue-khoan-guide.md` |
| Hộ/cá nhân kinh doanh | Doanh thu theo năm, kê khai quý/năm, chi phí | `thue-khoan-guide.md` |
| Người nước ngoài | Cư trú, không cư trú, DTA, xuất cảnh | `nguoi-nuoc-ngoai-guide.md` |

## Số Liệu Nhanh 2026

| Chỉ số | Giá trị | Căn cứ |
|--------|---------|--------|
| Giảm trừ bản thân | 15,5 triệu/tháng | NQ 110/2025/UBTVQH15 |
| Giảm trừ người phụ thuộc | 6,2 triệu/tháng | NQ 110/2025/UBTVQH15 |
| Doanh thu miễn TNCN của cá nhân kinh doanh | 500 triệu/năm trở xuống | Luật 109/2025/QH15, Điều 7 |
| Thuế lương cư trú | Biểu lũy tiến 5 bậc | Luật 109/2025/QH15, Điều 9 |
| Trúng thưởng | 10% trên phần vượt 20 triệu/lần | Luật 109/2025/QH15, Điều 15 |
| Tiền bản quyền | 5% trên phần vượt 20 triệu/hợp đồng | Luật 109/2025/QH15, Điều 16 |
| Nhượng quyền thương mại | 5% trên phần vượt 20 triệu/hợp đồng | Luật 109/2025/QH15, Điều 17 |
| Thừa kế, quà tặng | 10% trên phần vượt 20 triệu/lần | Luật 109/2025/QH15, Điều 18 |
| Thu nhập khác theo Điều 19 | 5% trên phần vượt 20 triệu/lần với một số khoản; 0,1% giá chuyển nhượng với tài sản số và vàng miếng | Luật 109/2025/QH15, Điều 19 |

## Mandatory Disclaimer

```text
⚠️ Thông tin chỉ mang tính tham khảo, không thay thế tư vấn thuế chuyên nghiệp.
Căn cứ: [ghi rõ luật/nghị định/thông tư hoặc nguồn chính thức].
Data skill rà soát lần cuối: 22/04/2026.
Kiểm tra lại tại: https://gdt.gov.vn, https://canhan.gdt.gov.vn, https://congbao.chinhphu.vn
```

## Bundled References

| File | Nội dung |
|------|---------|
| `references/tong-quan-thue.md` | Khung thuế cư trú, giảm trừ, các ngưỡng quan trọng |
| `references/vi-du-tinh-thue.md` | Ví dụ minh họa giữ nguyên để đối chiếu cách tính |
| `references/sop-quyet-toan.md` | Quyết toán năm, eTax Mobile, cổng thuế |
| `references/freelancer-guide.md` | Thuế cho freelancer/KOL/seller |
| `references/deadline-tracker.md` | Mốc nộp hồ sơ, nộp tiền, kê khai |
| `references/faq.md` | FAQ ngắn, ưu tiên câu hỏi lặp lại |
| `references/thue-khoan-guide.md` | Hộ/cá nhân kinh doanh, kê khai theo NĐ 68/2026/NĐ-CP |
| `references/sources.md` | Nguồn chính thống, nguồn tham khảo, ngày rà soát |
| `references/nguoi-nuoc-ngoai-guide.md` | Expat, cư trú/không cư trú, DTA |
| `references/system-flow.md` | Flow routing và verification |
