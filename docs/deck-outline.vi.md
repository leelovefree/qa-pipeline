# Outline deck — QA mobile có AI hỗ trợ (qa-pipeline) · bản 35 phút

Khán giả: bên thứ ba, có nhiều kinh nghiệm về AI. Không giải thích "LLM là gì"; tập trung vào rủi ro, cách kiểm soát và bằng chứng.

## Cách đọc file này

Mỗi slide có ba khối, tách bạch:
- **[TRÊN SLIDE]**: nội dung hiện trên màn hình (giữ ngắn khi làm slide thật).
- **[LỜI THOẠI]**: câu bạn nói, không hiện trên slide.
- **[GHI CHÚ — không đọc]**: việc chuẩn bị và câu trả lời khi bị hỏi.

Nhãn trạng thái dùng trên slide: **Đã làm** (chạy được, có bằng chứng) · **Đã thiết kế** (chốt chặn đã định rõ, chưa xây) · **Sẽ đo** (chỉ nói sau khi pilot).
Mọi con số của qa-pipeline đo trên **một app đơn giản, 5 lần chạy, một người vận hành**: dùng làm điểm dữ liệu và điểm xuất phát, không phải chuẩn. Cột "ước tính" và "mục tiêu khởi điểm" là giả định kèm lý do, không phải kết quả đã đo. Mọi con số baseline lấy từ `runs.jsonl` (SCRUM-8/9/11/12/13), `bin/qa-auto` và `docs/requirements.md`.

## Thuật ngữ thống nhất (dùng đúng một cách gọi trong cả deck)

| Từ dùng | Nghĩa |
|---|---|
| ticket | yêu cầu viết trong Jira |
| rule | một yêu cầu nhỏ, kiểm tra được, tách ra từ ticket (spec = tập các rule) |
| test case | kịch bản kiểm tra viết bằng ngôn ngữ nghiệp vụ, ứng với rule |
| flow | file test tự động chạy bằng Maestro, ứng với test case |
| selector | cách test tìm một nút/ô trên màn hình |
| assertion | bước kiểm tra "kết quả có đúng không" trong flow |
| regression | chạy lại toàn bộ test để xem có gì hỏng không |
| pilot | đợt thử có phạm vi và thời hạn rõ |

Phương án tiêu đề: (1) **AI Proposes, the Runner Decides** · (2) **A Test That Can't Lie** · (3) **Trust the Exit Code, Not the Model**

## Kế hoạch thời gian (35 phút)

| Phần | Phút |
|---|---|
| S1–S5: vấn đề, quy trình, chốt chặn, chi phí | 11,5 |
| S6 + **Demo 1** (ticket → PR) | 1 + 6 |
| **Demo 2** (CI chạy lại → sửa hay từ chối → báo cáo) + S7 | 5 + 1,5 |
| S8–S10: đánh giá, governance + giới hạn, roadmap + pilot | 7 |
| Dự phòng | ~2,5 |

Nếu phần hỏi đáp nằm trong 35 phút: phát Demo 2 dạng video quay sẵn và rút gọn S9.

---

## S1. Tiêu đề (0,5 phút)

**[TRÊN SLIDE]**
- Tiêu đề (chọn một trong ba) · phụ đề: "Từ ticket Jira đến PR đã review đến kiểm thử hồi quy trên CI — AI luôn có giới hạn"

**[LỜI THOẠI]**
"Hôm nay mình không nói về việc AI viết test giỏi đến đâu. Mình nói về việc làm sao để tin được kết quả đó: những chốt chặn nào, chi phí bao nhiêu, và đã đo được gì."

---

## S2. Để AI viết test: 4 rủi ro và cách chúng tôi kiểm soát (2 phút)

**[TRÊN SLIDE]**

| Rủi ro | Nghĩa là gì | Cách kiểm soát |
|---|---|---|
| Test "xanh giả" | AI sửa test cho qua thay vì báo lỗi | Công cụ chạy test quyết định pass/fail, không phải AI |
| AI tự đoán | Ticket mơ hồ nhưng AI vẫn viết test theo suy đoán | Gặp chỗ mơ hồ thì dừng và hỏi người |
| Chạy không dừng | AI thử đi thử lại, tốn tiền và thời gian | Mỗi bước có trần chi phí, thời gian và số lần thử |
| Không truy vết được | Không biết model nào làm, ai duyệt, tốn bao nhiêu | Ghi lại model, chi phí và người duyệt cho từng bước |

- Ví dụ thật (SCRUM-9): pipeline từng mở một PR báo "xanh" dù chưa có test nào được sinh ra. Đã sửa: chỉ báo xanh khi mọi rule đều có test **và** test pass. **Đã làm**

**[LỜI THOẠI]**
"Ai cũng biết AI viết được test. Câu hỏi thật là: có tin được không? Mình gom lại bốn rủi ro. Một, test xanh giả: AI sửa test cho qua. Hai, AI tự đoán khi yêu cầu mơ hồ. Ba, AI chạy mãi không dừng. Bốn, không truy vết được ai làm gì. Mỗi rủi ro có một cách kiểm soát, và cả buổi hôm nay sẽ đi qua từng cái. Rủi ro đầu không phải lý thuyết: hệ thống của mình từng báo xanh khi chưa có test nào. Mình phát hiện khi chạy trên ticket thật và đã sửa."

**[GHI CHÚ — không đọc]**
- Bốn rủi ro này là khung cho cả buổi: S4 trả lời rủi ro 1–2, S5 trả lời rủi ro 3, S9 trả lời rủi ro 4.

---

## S3. Quy trình 8 bước (3 phút) — slide cốt lõi

**[TRÊN SLIDE]**
Sơ đồ: Nhận ticket → Làm rõ → Thiết kế case → Viết test → Review & merge → Chạy lại trên CI → Chẩn đoán khi lỗi → Báo cáo. Tô màu: **AI** / **Cổng người** / **Không AI**.

| # | Bước | Ai làm | Tình trạng |
|---|---|---|---|
| 1 | Nhận ticket (Jira) | Người | Đã làm |
| 2 | Làm rõ: tách ticket thành rule | AI; người trả lời chỗ mơ hồ | Đã làm |
| 3 | Thiết kế test case | AI; người duyệt rule + case | Đã làm |
| 4 | Viết flow test trên app thật | AI, có giới hạn | Đã làm |
| 5 | Review & merge PR | Người | Đã làm |
| 6 | Chạy lại trên CI | **Không AI**: kết quả của Maestro | Đã làm |
| 7 | Chẩn đoán khi test lỗi | AI; người merge mọi bản vá | Đã thiết kế |
| 8 | Báo cáo & kiểm toán | Phần lớn là code; AI rẻ chỉ viết tóm tắt | Đã thiết kế |

- Mỗi lần test đỏ đều do **người** phân loại: **A** lỗi app · **B** ticket sai · **C** AI hiểu sai · **D** yêu cầu thay đổi.

**[LỜI THOẠI]**
"Đây là toàn bộ quy trình tám bước. Màu xanh là AI làm, màu cam là cổng người duyệt, màu xám là không có AI. Để ý ba điều. Một: ba trong tám bước có cổng người. Hai: bước chạy lại trên CI hoàn toàn không có AI, kết quả pass hay fail là của công cụ chạy test. Ba: khi test đỏ, người phân loại nguyên nhân, AI không tự quyết. QA làm việc trong Jira và không cần mở repo. Bước 7 và 8 mình đang xây, nên slide ghi rõ là đã thiết kế."

**[GHI CHÚ — không đọc]**
- Tên agent (nếu bị hỏi): `spec-extractor` (bước 2), `case-designer` (bước 3), `automation-writer` và `flow-fixer` (bước 4), `repair-agent` (bước 7), `reporter` (bước 8).

---

## S4. Hệ thống hoạt động thế nào và các chốt chặn (3 phút)

**[TRÊN SLIDE]**
```
Ticket Jira
   ▼
AI #1: tách ticket thành các rule  ──▶ mơ hồ? dừng và hỏi người
   ▼
AI #2: thiết kế test case
   ▼
[Người] QA duyệt rule + case
   ▼
AI #3: viết test trên app thật (có trần chi phí và thời gian)
   ▼
Chạy test bằng Maestro  ◀── công cụ này quyết định pass/fail, không có AI
   ▼
Pull request ──▶ [Người] review và merge
```
- Mỗi AI là một agent riêng: làm đúng một việc, trong một phiên làm việc mới.
- Các bước giao kết quả cho nhau bằng **file trong git** (spec, case, test). Người đọc và sửa được; không có "trí nhớ ẩn" của AI.

| Chốt chặn | Hoạt động thế nào | Thực thi bằng |
|---|---|---|
| Pass/fail | Do kết quả chạy của Maestro quyết định; CI không có bước AI | **Code/CI** |
| Đủ yêu cầu | Mỗi rule trong spec phải có test case tương ứng | **Code** |
| "Xanh" trung thực | Chỉ báo xanh khi mọi rule đều có test và test pass | **Code** |
| Không sửa yêu cầu để test qua | CI chặn PR sửa spec và test cùng lúc nếu chưa có người duyệt | **CI** |
| Tự sửa không được đụng phần kiểm tra | Bước tự sửa chỉ được đổi selector hoặc thời gian chờ, không được đổi assertion | **Code** |
| Lấy phần tử từ app thật | AI phải xem màn hình thật của app trước khi viết selector | **Prompt + MCP** |

**[LỜI THOẠI]**
"Cách hoạt động rất đơn giản. Ba AI nối nhau, mỗi AI làm một việc và bàn giao bằng file trong git, nên người đọc và sửa được. Giữa chừng có hai cổng người: trả lời chỗ mơ hồ, và duyệt rule cùng test case. Quan trọng nhất là ô giữa: công cụ chạy test quyết định pass hay fail, không phải AI. Bảng bên dưới là sáu chốt chặn. Mình nói thẳng: năm cái được ép bằng code hoặc CI, còn cái cuối, 'phải xem app thật trước khi viết selector', mới ở mức chỉ dẫn cho AI, chưa có code kiểm tra."

**[GHI CHÚ — không đọc]**
- Tên kỹ thuật, chỉ nói khi bị hỏi: bộ điều phối `bin/qa-auto`, bộ chạy test `bin/qa`, kiểm tra độ phủ `bin/qa-check`, khoá assertion `fix_is_legit`, kiểm tra spec `spec-integrity`, công cụ xem màn hình `inspect_screen` (Maestro MCP).
- Nói rõ dòng nào chỉ ở mức prompt; khán giả có kinh nghiệm tin điều đó hơn là một claim quá tay.

---

## S5. Chi phí: nhỏ, đo được, có trần (3 phút)

**[TRÊN SLIDE]**
- Biểu đồ: chi phí AI mỗi ticket theo từng bước (5 lần chạy trên ShopDemo).
- Ba con số lớn: **~$0,4 mỗi test** (ShopDemo) · **$0** AI khi chạy lại test trên CI · **~$10–70** AI cho cả pilot 10–15 ticket (ước tính).
- Chú thích: "Đây là một điểm dữ liệu, không phải chuẩn. ShopDemo là app đơn giản; app thật có thể cao hơn 1–3 lần (giả định). Trần cứng mỗi bước: $1,5 · $2 · $12 · $4 — rào chắn, không phải dự toán."

| Hạng mục | Đo được (ShopDemo, 5 lần chạy) | Ước tính khi áp dụng cho app thật |
|---|---|---|
| Chi phí mỗi test sinh ra | ~$0,40–$0,46 | ~$0,4–$1,3 (giả định app phức tạp gấp 1–3 lần) |
| 1 ticket có 2–4 test | $0,81–$1,38 | $0,8–$4,5 |
| 1 lần tự sửa selector | $0,09–$0,29 (5 lần) | cùng bậc |
| Bước 7 và bước 8 | chưa có | chưa đo (bước 8 chủ yếu là code) |
| Chạy lại trên CI | $0 AI | $0 AI |
| Cả pilot 10–15 ticket | — | ~$10–70 |

**[LỜI THOẠI]**
"Về chi phí, mình tách ba lớp. Một: trần cứng. Nếu một AI chạy lỡ thì bị dừng ở mức này; trần cao hơn nhiều so với chi phí thật, vì nó là rào chắn chứ không phải dự toán. Hai: số đã đo trên năm ticket thật của một app demo đơn giản, khoảng 0,4 đô cho mỗi test. Đây là một điểm dữ liệu, không phải chuẩn: app thật phức tạp hơn nên có thể cao hơn một đến ba lần, và pilot sẽ đo con số thật. Ba: để dễ hình dung, 0,4 đô tương đương chừng nửa phút công của một kỹ sư, nếu lấy ví dụ 50 đô một giờ. Nghĩa là chi phí đáng kể là thời gian review, không phải tiền AI. Cuối cùng, chạy lại test hằng ngày không tốn đồng AI nào."

**[GHI CHÚ — không đọc]**
- **Vì sao không coi là chuẩn:** 5 lần chạy, 1 app đơn giản, 1 người vận hành, 1 máy. Chỉ dùng làm điểm xuất phát; pilot thay bằng số đo thật.
- **Cách ước tính:** chi phí 1 ticket ≈ ~$0,5 cố định (tách rule ~$0,3 + thiết kế case ~$0,2) + ~$0,17 cho mỗi test viết ra (đo: SCRUM-8 $0,17, SCRUM-12 $0,19, SCRUM-13 $0,16). Kiểm chứng với SCRUM-13: $0,49 + $0,32 = $0,81.
- **Khoảng "1–3 lần" là giả định**, không phải số đo: app thật có nhiều màn hình, flow dài hơn. Pilot: 10 ticket × $0,84 ≈ $10 (cận dưới); 15 ticket × ~$3,5 (3×) ≈ $53, cộng bước 7 → ~$70 (cận trên).
- **Ví dụ "nửa phút công":** $0,4 ÷ $50/giờ ≈ 29 giây. $50/giờ là giả định minh hoạ; thay bằng mức lương thật của đối tác.
- Một cải thiện đo được: tách `case-designer` làm bước thiết kế case rẻ hơn ~$0,30/ticket (từ ~$0,47 xuống $0,17; 3 lần đo trước, 1 lần đo sau). **Đừng nói "giảm từ $1,35 xuống $0,81"**: hai ticket khác số test.
- Chưa có trần chi tiêu theo ngày. Chưa gồm phút chạy runner macOS trên CI.

## S6. Kịch bản demo (1 phút)

**[TRÊN SLIDE]**
App ShopDemo (iOS) chạy trên simulator, ba phiên bản:

| Phiên bản | Thay đổi | Kết quả mong đợi |
|---|---|---|
| Gốc (`build-1`, đã có) | không | test pass |
| Đổi cách tìm phần tử (**cần làm**) | đổi ID một nút, hành vi giữ nguyên | AI sửa selector kèm bằng chứng, chạy lại thì pass — Đã thiết kế |
| Lỗi thật (**cần làm**) | lỗi logic thật | AI **từ chối sửa**, test giữ đỏ, người phân loại là lỗi app (A) — Đã thiết kế |

**[LỜI THOẠI]**
"Mình sẽ demo hai phần. Phần một: từ một ticket Jira đến một PR, chạy thật. Phần hai: chạy lại test trên ba phiên bản của app. Hãy chú ý một điều: không phải AI sửa được test, mà là AI biết phân biệt khi nào được sửa và khi nào phải từ chối."

---

## Demo 1 — từ ticket đến PR (≈6 phút, chạy thật) · Bước 2–5 · Đã làm

**[TRÊN MÀN HÌNH]**
1. Ticket Jira gắn label `qa-auto`; đặc tả (spec) xuất hiện.
2. Một comment Jira duy nhất gồm rule + test case; bạn gắn `qa-approved`.
3. Flow được sinh trên simulator thật; chạy local; PR mở ra, phần mô tả ghi model, session và chi phí.
4. (Ảnh chụp màn hình, không chạy thật) comment `qa-needs-info` của một ticket mơ hồ.

**[LỜI THOẠI]**
"Đây là một ticket thật trên Jira. Mình gắn label qa-auto. Hệ thống đọc ticket và tách thành các rule. Đây là comment duy nhất gửi cho QA, gồm cả rule lẫn test case. Mình gắn label duyệt. Bây giờ AI mở app thật trên simulator để viết test, mất khoảng hai phút. Trong lúc chờ, các bạn thấy trần chi phí và thời gian đang chạy. Xong rồi, đây là PR: có ghi model nào đã dùng và tổng chi phí. Còn nếu ticket mơ hồ thì hệ thống dừng và hỏi như màn hình này, thay vì tự đoán."

**[GHI CHÚ — không đọc]**
- Khởi chạy ticket trước giờ nói để bước tách rule và thiết kế case đã xong. Thời gian thật: tách rule ~33 s, thiết kế case ~40 s, viết test ~139 s, tạo simulator ~86 s.
- Dự phòng: video quay lại đúng lần chạy này.

---

## Demo 2 — chạy lại trên CI, sửa hay từ chối, báo cáo (≈5 phút, kết quả chạy sẵn) · Bước 6–8

**[TRÊN MÀN HÌNH]**
1. CI chạy lại trên phiên bản gốc (dùng nhóm `smoke`, 6 flow) → xanh. Đã làm
2. Phiên bản đổi ID → đỏ → AI mở PR vá selector kèm bằng chứng màn hình → chạy lại xanh. Đã thiết kế
3. Phiên bản lỗi thật → đỏ → AI **từ chối**, test giữ đỏ, chuyển cho người phân loại. Đã thiết kế
4. Báo cáo: model, số lần thử, chi phí, người duyệt. Đã thiết kế

**[LỜI THOẠI]**
"Bây giờ là phần chạy lại test trên CI, không có AI. Phiên bản gốc xanh. Phiên bản thứ hai, một nút bị đổi ID: test đỏ, AI xem màn hình thật, thấy nút vẫn còn, chỉ đổi ID, nên đề xuất một PR sửa selector. Chạy lại thì xanh. Phiên bản thứ ba, app tính sai một giá trị: test cũng đỏ, nhưng lần này AI từ chối sửa, vì đây là lỗi của app. Test giữ nguyên đỏ và chuyển cho người. Cuối cùng là báo cáo của lần chạy."

**[GHI CHÚ — không đọc]**
- Chạy đủ 21 flow mất ~12 phút, nên dùng nhóm `smoke` hoặc video quay sẵn. Chỉ chạy bước 7 thật nếu bạn đo được mỗi lần dưới ~2 phút (hiện chưa đo).
- Dự phòng dùng được ngay: SCRUM-7, một lỗi app thật mà test vẫn đỏ (gắn `known-bug` kèm ticket key, CI loại ra). Dùng nó để cho thấy hệ thống không che lỗi, kể cả khi bước 7 chưa xong.

---

## S7. Điểm mấu chốt: biết khi nào KHÔNG được sửa (1,5 phút)

**[TRÊN SLIDE]**

| AI được tự sửa | AI phải từ chối, chuyển cho người |
|---|---|
| Giao diện đổi nhưng app vẫn đúng. Ví dụ: một nút đổi ID | App chạy sai. Ví dụ: một con số hiển thị sai |
| Cập nhật selector kèm bằng chứng từ màn hình thật, chạy lại, mở PR cho người duyệt | Test giữ nguyên đỏ, người phân loại lỗi A/B/C/D |

- **Sửa cho test xanh thì dễ; khó là phân biệt "giao diện đã dời" với "app đang sai".**

**[LỜI THOẠI]**
"Đây là điều mình muốn các bạn nhớ. Sửa một test cho xanh thì dễ, AI làm được ngay. Cái khó là biết khi nào không được sửa. Một công cụ tự vá mà không phân biệt được 'giao diện đã dời' với 'app đang sai' thì sẽ biến mọi lỗi thật thành test xanh. Vì vậy chúng tôi giới hạn nó chặt, và để người quyết định mọi trường hợp còn lại."

**[GHI CHÚ — không đọc]**
- Đây là câu trả lời cho "self-healing giả". Đổi ví dụ cho khớp hai build demo khi bạn làm xong.
- Chi tiết kỹ thuật, chỉ nói khi bị hỏi (**Đã thiết kế**): tối đa 2 lần thử · phải chạy lại case · bản vá làm test kiểm tra ít đi thì bị từ chối tự động · đầu ra luôn là PR cho người duyệt.
- Có thể bỏ slide này nếu cần thêm thời gian; Demo 2 đã nói lên ý này.

---

## S8. Hiệu quả: đã có gì, mục tiêu khởi điểm, sẽ đo gì (2 phút)

**[TRÊN SLIDE]**

| Chỉ số | Đã có (ShopDemo) | Mục tiêu khởi điểm cho pilot |
|---|---|---|
| Rule đều có test case | Code chặn nếu thiếu; 8 ticket, 32 flow — Đã làm | 100% (do code ép) |
| Ticket ra PR xanh, người không phải sửa flow | 3/5 lần chạy | ≥ 60% (tham chiếu: Meta 57%¹) |
| "Xanh giả" | 1 lần, đã sửa | 0 |
| Tự sửa đúng hay sai | chưa đo (có 2 build đáp án) — Sẽ đo | 2/2 đúng, 0 che lỗi thật |
| Thời gian máy chạy, công sức bảo trì | ShopDemo: 4–5 phút/ticket; bảo trì chưa đo | không đặt trước — pilot đo |

- Cách đo: cùng 10–15 ticket thật, hai nhánh (**cách làm hiện tại** vs **có AI**), cùng app và cùng người review; ghi cỡ mẫu cạnh mỗi con số.
- ¹ Meta TestGen-LLM (FSE 2024): 57% test do AI sinh ra chạy ổn định. Đó là unit test, khác miền — chỉ để tham chiếu.

**[LỜI THOẠI]**
"Mình chia thẳng: cái gì đã có, mục tiêu khởi điểm, và cái gì chưa đo. Đã có: mọi rule đều có test case, vì code chặn nếu thiếu. Các mục tiêu khởi điểm là điểm xuất phát để cùng bàn với các bạn, không phải chuẩn của ngành. Tham chiếu duy nhất mình có là nghiên cứu của Meta: 57% test do AI sinh ra chạy ổn định. Đó là unit test nên khác miền, mình chỉ dùng để kiểm tra mục tiêu sáu mươi phần trăm có hợp lý không. Còn thời gian chạy và công sức bảo trì, mình không đặt con số trước, vì mình muốn pilot trả lời bằng dữ liệu của chính các bạn."

**[GHI CHÚ — không đọc]**
- **Vì sao không đặt "chuẩn":** số của mình là từ 1 app, 5 lần chạy. Đặt thành chuẩn thì khán giả có kinh nghiệm sẽ bắt bẻ ngay. Nói "mục tiêu khởi điểm, cùng thống nhất" an toàn hơn.
- **Cơ sở của "≥ 60%":** 3/5 lần chạy không người trông (SCRUM-8, 12, 13 xanh; SCRUM-9 xanh giả, SCRUM-11 đỏ do lỗi hạ tầng, cả hai đã sửa) và tham chiếu Meta 57%. Hai nguồn độc lập cùng quanh mức 60%, nhưng đều là mẫu nhỏ hoặc khác miền.
- **Meta:** Alshahwan và cộng sự, "Automated Unit Test Improvement using LLMs at Meta" (arXiv 2402.09171, FSE 2024 Industry): 75% test build đúng, 57% chạy ổn định, 25% tăng độ phủ; 73% đề xuất được kỹ sư chấp nhận khi test-a-thon. Đọc lại bài gốc trước khi trích dẫn trên slide.
- **Không dùng** các con số "bảo trì chiếm 40–70% công sức" vì chỉ thấy trong blog của nhà cung cấp, chưa có nguồn nghiên cứu tin cậy.
- "2/2 đúng" và "0 che lỗi" là mục tiêu thiết kế trên 2 build đáp án, chưa phải thống kê.
- Không claim giảm công sức QA hay tăng khả năng phát hiện lỗi.

## S9. Governance, kiểm toán và giới hạn (2 phút)

**[TRÊN SLIDE]**
- **Kiểm toán:** phần mô tả PR ghi model, session và tổng chi phí; việc duyệt là lịch sử label Jira; truy vết được ticket → spec → case → flow → PR. Đã làm. Báo cáo cho mỗi lần chạy (bước 8): Đã thiết kế.
- **Dữ liệu:** không dùng dữ liệu khách hàng/rider thật; thông tin đăng nhập chỉ nằm trong cấu hình máy và CI secrets. Đã làm.
- **Chưa làm:** review data residency và EU AI Act — cần xác nhận trước pilot.
- **Giới hạn hiện tại:**
  - Một app (ShopDemo), chỉ iOS; chưa có Android.
  - Bước 7 và 8 chưa xây.
  - Mới 5 lần chạy, 1 app, 1 người vận hành.
  - Chưa có trần chi tiêu theo ngày.
  - Assertion sinh ra được kiểm bằng review PR của người và độ phủ mức rule; chưa có code kiểm tra rằng mỗi kết quả mong đợi đã duyệt đều thành một assertion.
  - Đang dùng tài khoản Jira/GitHub cá nhân; pilot cần service account và runner CI trung lập.

**[LỜI THOẠI]**
"Về kiểm toán: mỗi PR ghi rõ model nào đã làm, tốn bao nhiêu, và ai duyệt nằm trong lịch sử Jira. Về dữ liệu: chúng tôi không dùng dữ liệu khách hàng thật. Có một việc chưa làm và mình muốn nói ngay: chưa review data residency và EU AI Act, cần xác nhận trước khi chạy pilot. Còn giới hạn thì như trên slide: mới một app, chỉ iOS, năm lần chạy. Mình nói thẳng điều này vì pilot được thiết kế để trả lời đúng những chỗ chưa chắc."

**[GHI CHÚ — không đọc]**
- Hãy tự nói các giới hạn; nghe từ bạn tốt hơn là nghe từ khán giả.
- Chỉ nói thêm khi bị hỏi: chưa xác minh branch protection của GitHub; `bin/qa-auto` chưa có test riêng; flow còn hard-code tài khoản demo.

---

## S10. Roadmap, pilot và kết (2,5 phút)

**[TRÊN SLIDE]**
- **Roadmap:** (1) app thứ hai + Android (cấu trúc nhiều app đã có sẵn) → (2) chạy song song: runner CI trung lập, chia nhỏ CI, trần chi tiêu theo ngày, service account → (3) nhiều nhà cung cấp model, xác thực doanh nghiệp → (4) vòng lặp: CI lỗi → ticket → PR sửa → báo cáo.
- **Pilot đề xuất:** 1 app, 10–15 ticket thật, 4–6 tuần.
  - Tuần 0–1: chuẩn bị (nguồn build, Jira + service account, repo, tài khoản test không có dữ liệu thật, một QA phụ trách).
  - Tuần 1–5: chạy hai nhánh, họp xem lại mỗi tuần.
  - Tuần 6: báo cáo đánh giá theo S8.
  - Chi phí AI kỳ vọng: **~$10–70** cho cả đợt (ước tính, thay bằng số đo thật) (chưa gồm phút chạy CI và công người).
- Tiêu chí tiếp tục, dừng hay mở rộng được thống nhất từ trước.

**[LỜI THOẠI]**
"Bước tiếp theo là một pilot nhỏ: một app, mười đến mười lăm ticket thật, bốn đến sáu tuần. Chi phí AI mình ước tính chừng mười đến bảy mươi đô cho cả đợt, và con số này sẽ được thay bằng số đo thật. Điều chúng tôi mang đến không chỉ là 'có dùng AI', mà là kỷ luật bao quanh AI: công cụ chạy test quyết định, người giữ các cổng, giới hạn bằng code, và những con số chúng tôi công bố kể cả khi chưa đẹp. Cảm ơn các bạn."

**[GHI CHÚ — không đọc]**
- Mục (3) trong roadmap chưa bắt đầu; chỉ làm sau (1) và (2).
- Không claim "giảm công sức QA" hay "tăng khả năng phát hiện lỗi": đó là giả thuyết pilot kiểm tra.

---

## Appendix / FAQ (không trình bày)

- **AI không bao giờ tự quyết:** pass/fail · sửa spec, kết quả mong đợi trong test case hay assertion · giải quyết chỗ mơ hồ · thêm tag `known-bug` · phân loại A/B/C/D · merge.
- **Năm nguyên tắc bất biến:** AI không bao giờ tuyên bố fail là pass · mơ hồ thì dừng và hỏi người · mọi bước tự động đều có trần cứng · không code nào vào `main` nếu người chưa duyệt PR · mọi artefact truy vết được tới ticket, phiên bản model và chi phí.
- **Hai chế độ:** chạy tự động (label `qa-auto`) hoặc thủ công (`/spec /cases /flows /run /fix /pr`), chuyển đổi theo từng ticket.
- **Chi phí theo bước (SCRUM-13, 2 test):** tách rule $0,32 · thiết kế case $0,17 · viết test $0,32. CI: 21 flow ≈ 12 phút, ~80% là thời gian chạy test tuần tự; nhóm `smoke` = 6 flow.
- **Câu hỏi khó có thể gặp:**
  - "Sao không dùng phân tích AI của Maestro trong CI?" — Kết quả pass/fail không được phụ thuộc vào model; bị cấm trong CI ngay từ thiết kế.
  - "Assertion sinh ra có khớp kết quả mong đợi đã duyệt không?" — Hiện dựa vào review PR của người và độ phủ mức rule; check bằng code là khoảng trống đã biết.
  - "AI tự sửa có che được lỗi không?" — Không đổi được assertion và không thêm được `known-bug` (do code chặn); kết quả chạy lại thuộc về công cụ chạy test.
  - "Data residency thì sao?" — Việc còn mở; trả lời trước pilot.
