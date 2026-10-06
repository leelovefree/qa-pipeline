# Hướng dẫn dùng `bin/qa-auto` và các lệnh thủ công

Tài liệu này dành cho QA đang làm **một ticket** và muốn nhờ AI làm phần việc lặp lại (đọc ticket → spec → test case →
Maestro flow → chạy thử → mở PR). Quy trình tổng thể và nguyên tắc nằm ở [huong-dan-qa-pipeline.md](huong-dan-qa-pipeline.md).

> Trạng thái: đã chạy thật end-to-end một lần trên SCRUM-8 (PR #8). Bản "chạy tại chỗ, đọc stage từ file" (mục 3, 4) mới được
> kiểm tra từng hàm, **chưa chạy lại end-to-end** — lần đầu dùng hãy theo dõi sát.

---

## 1. Hai cách làm một ticket

Chọn cho **từng ticket**, đổi giữa chừng được.

| | **Tự động (2a)** | **Thủ công (2b)** |
|---|---|---|
| Kích hoạt | Gắn label `qa-auto` trên Jira, `bin/qa-auto` chạy ở máy bạn | Bạn gõ từng lệnh `/spec`, `/cases`, `/flows`, `/run`, `/fix`, `/pr` trong Claude Code |
| Ai làm | AI làm cả chuỗi, dừng ở các cổng cần người | Bạn điều khiển từng stage, AI làm từng bước |
| Jira | Tool tự comment và đổi label | Bạn tự comment (dùng `no-jira-write`) |
| Bạn làm gì | Trả lời câu hỏi trên ticket, đọc rule + test case trong **một comment** rồi gắn `qa-approved`, review PR | Đọc kết quả sau mỗi stage rồi gọi lệnh tiếp |

Cả hai làm trên **cùng branch `qa/<TICKET-ID>`, cùng file `apps/<app>/...`**. Đó là lý do chuyển qua lại được (mục 5).

> Chưa hỗ trợ: chế độ QA **không mở repo** (AI chạy trên máy chủ chung, QA chỉ dùng Jira + GitHub). Xem mục 9.

---

## 2. Chuẩn bị (một lần)

1. Làm theo mục 1–2 của [huong-dan-qa-pipeline.md](huong-dan-qa-pipeline.md): Xcode + simulator, Maestro, `gh auth login`, Claude Code,
   MCP `maestro` và `atlassian-personal` (kết nối bằng `/mcp` trong một session tương tác).
2. **Chỉ cho tự động (2a):** tạo Atlassian API token tại https://id.atlassian.com/manage-profile/security/api-tokens, rồi:
   ```bash
   mkdir -p ~/.config/qa-auto
   cat > ~/.config/qa-auto/env <<'EOF'
   JIRA_BASE_URL=https://<site>.atlassian.net
   JIRA_EMAIL=<email đăng nhập Jira>
   JIRA_API_TOKEN=<token>
   EOF
   chmod 600 ~/.config/qa-auto/env
   ```
   File này nằm **ngoài repo**, không bao giờ commit.
3. Mỗi ticket cần acceptance criteria rõ (Given/When/Then, có giá trị mong đợi cụ thể). Ticket mơ hồ sẽ bị AI dừng lại và hỏi.
4. Không cần tự boot simulator: tool **tự tạo một simulator riêng tên `qa-auto`** (cùng loại máy với `ios_device` trong `app.config.yml`), cài build, dùng xong thì **xoá**. Simulator của bạn không bị đụng tới.

---

## 3. Tự động (2a): `bin/qa-auto`

### Chạy
```bash
bin/qa-auto run SCRUM-9            # chạy một ticket tới chỗ cần người, rồi dừng
bin/qa-auto poll --interval 60     # canh Jira, thấy ticket có label qa-auto là chạy
bin/qa-auto status                 # xem các ticket đang theo dõi + stage hiện tại
```
`poll` chỉ sống trong terminal/session đang mở. Muốn chạy nền liên tục dùng `templates/launchd/` (launchd là trình quản lý dịch vụ của macOS,
tự bật poller khi đăng nhập). Nếu bạn tự gõ `run` khi cần thì **không cần launchd**.

JQL mặc định: `project = <tracker_project_key> AND labels = qa-auto`. Muốn đổi (ví dụ chỉ ticket giao cho bạn), thêm
`auto_jql: <JQL>` vào `apps/<app>/app.config.yml`.

### Luồng và các cổng cần người
| Bước | Việc xảy ra | Label trên Jira |
|---|---|---|
| 1 | Bạn gắn `qa-auto` | `qa-auto` |
| 2 | **Stage 2**: AI đọc ticket. Nếu mơ hồ → comment câu hỏi, dừng | `qa-needs-info` |
| 2' | Bạn trả lời trên ticket → tool tự chạy lại Stage 2 (resume) | |
| 3 | Rõ ràng → **Stage 3**: AI viết `CASES.md` (chỉ text, không dùng simulator), rồi đăng **một comment** gồm từng rule (ID, Given/When/Then, câu trích gốc, độ tin cậy) **kèm test case của rule đó** (precondition, bước, kết quả mong đợi) | `qa-ready-for-review` |
| 4 | **Bạn đọc cả rule lẫn case rồi gắn `qa-approved`** — một lần duyệt cho cả spec và cases. Sai thì chưa có vòng sửa tự động: gỡ `qa-auto`, tự sửa `spec.md`/`CASES.md` trên branch `qa/<KEY>` (hoặc `/spec`, `/cases`), rồi gắn lại `qa-auto` + `qa-approved` | `qa-approved` |
| 5 | **Stage 4**: dòng `Status: awaiting QA approval` trong `CASES.md` được đổi thành `approved by QA`; AI sinh flow Maestro (inspect màn hình thật), `bin/qa-check` | |
| 5' | **Chốt chặn `known-bug`** (trong code): nếu AI thêm tag `known-bug` vào flow nào (flow mới hoặc flow cũ chưa có tag trên `main`) thì toàn bộ flow vừa sinh bị xoá và ticket dừng ở `qa-error`. Lý do: flow có tag bị bỏ qua khi chạy, nên AI có thể dùng tag để biến test đỏ thành PR xanh. Chỉ người gắn tag, sau khi đã tạo bug ticket thật | `qa-error` |
| 6 | Chạy thử các feature của ticket bằng `bin/qa` (loại flow `known-bug` như CI) | |
| 7 | Test đỏ → `flow-fixer` sửa selector/timing, tối đa 3 lần (bản fix bị từ chối nếu đổi assertion hoặc thêm tag `known-bug`) | |
| 8 | Push branch, mở PR (xanh: PR thường, đỏ: **draft**), comment link PR lên Jira | `qa-pr-open` / `qa-red` |
| 9 | **Bạn review PR và merge.** Không có gì tự merge | |

Lỗi hoặc timeout bất kỳ → comment lên ticket và gắn `qa-error`. **Tool bỏ qua ticket có `qa-error`**; sửa nguyên nhân rồi gỡ label để chạy lại.

### Tool chạy ở đâu, đụng vào gì
- Làm **ngay trong repo của bạn**, trên branch `qa/<TICKET-ID>` tách từ `main` mới nhất. File ở `apps/<app>/specs/<ID>/...` và
  `apps/<app>/tests/...` thật — mở IDE là thấy, kể cả lúc AI đang viết.
  (Bản cũ dùng worktree ẩn trong `.qa-work/` nên có hai thư mục `apps/shopdemo`; bản này không còn.)
- **Chỉ chạy khi bạn đang ở `main` hoặc `qa/<TICKET-ID>` và không có file đã sửa chưa commit.** Nếu không, nó dừng và nói rõ lý do, không đụng gì.
- Chỉ commit file trong `apps/`; hoàn tác một lần fix sai cũng chỉ trong `apps/`, không xóa file khác của bạn.
- Trong lúc chạy nó chiếm thư mục repo: đừng sửa file hay đổi branch. Simulator thì dùng riêng (`qa-auto`), nên bạn dùng simulator của mình vẫn được.
- **Simulator sạch mỗi lần**: tạo mới + cài app trước phiên AI (Stage 4) và trước mỗi lần chạy test, xoá khi xong. Tốn thêm khoảng 1–2 phút mỗi lần, đổi lại không còn lỗi `DeviceUnreachable` do driver cũ còn sót. Nếu vẫn gặp lỗi thiết bị, tool tạo simulator mới và chạy lại đúng 1 lần.
- `.qa-work/` là thư mục tạm bị gitignore (build tải về, `report.xml` của `bin/qa`, và `.qa-work/auto/` gồm `state.json`, `lock`,
  `<KEY>/runs.jsonl` ghi chi phí, session và **model thật + token (input/output/cache) theo từng model** của mỗi stage — lấy từ `modelUsage` mà `claude -p` trả về, không phải model mình yêu cầu). Dòng "Models" trong PR body lấy từ đây. Không bao giờ vào PR.

### Rào chắn bằng code (không phải lời dặn AI)
- **Pass/fail chỉ do exit code của `bin/qa` (Maestro).** AI không được tuyên bố pass.
- `flow-fixer` chỉ sửa file `.yaml` có sẵn trong `apps/<app>/tests/`. Đụng vào dòng `assert*`, sửa file khác hoặc tạo file mới → **tự hoàn tác** lần fix đó.
- Không sửa spec/CASES.md để test xanh. Nghi app bug → fixer báo `POSSIBLE_APP_BUG`, không sửa gì, người triage A/B/C/D (§9.1 của hướng dẫn chung).
- Mỗi stage một session `claude -p` riêng, có danh sách tool cho phép, trần chi phí (spec $1.5 · cases $2 · build $12 · fix $4) và timeout (15 / 15 / 60 / 20 phút).
- Khoá một pipeline tại một thời điểm.
- AI **không bao giờ merge**. Chi phí, session và agent được ghi vào PR để truy vết.

Thực tế SCRUM-8 (2 rule đơn giản): spec 30 giây ($0.27) · sinh case + 2 flow 72 giây ($0.34) · chạy thử 4 flow ~1,5 phút · tổng ~$0.9.
Chạy cả module (14 flow) mất ~6 phút, nên tool chỉ chạy feature của ticket (`<module>/<feature>`).

---

## 4. Thủ công (2b): các lệnh trong Claude Code

Mỗi lệnh = **một stage = một session**. Mở session mới cho mỗi lệnh. Mỗi lệnh dừng ở cổng người; không tự đi tiếp.

| Lệnh | Việc | Bạn làm tiếp |
|---|---|---|
| `/spec <KEY> [app] [no-jira-write]` | Sang branch `qa/<KEY>`, gọi `spec-extractor` | Đọc `spec.md` (hoặc `open-questions.md`) |
| `/cases <KEY> [app]` | Viết `CASES.md`, báo nếu trùng case cũ | Review dữ liệu test, bước, kết quả mong đợi |
| `/flows <KEY> [app]` | Viết flow Maestro sau khi inspect app thật, `bin/qa-check` | Đọc từng flow, chạy lại một lần |
| `/run <app> [module/feature]` | `bin/qa run`, in nguyên văn kết quả | Đỏ thì triage trước khi sửa |
| `/fix <flow hoặc ID>` | `flow-fixer` sửa selector/timing (không đụng assert/spec) | Xem `git diff`, `/run` lại |
| `/pr <KEY>` | Commit file `apps/<app>/specs` và `tests`, push, mở PR | Xác nhận trước khi commit; review và merge |

`no-jira-write`: `spec-extractor` chỉ ghi `open-questions.md`, **không tự comment lên Jira** — bạn tự comment câu hỏi.

Dùng được cả khi không có label Jira nào: bạn gọi từng lệnh theo ý mình.

---

## 5. Chuyển qua lại giữa tự động và thủ công

Vì cả hai chạm cùng branch `qa/<KEY>` và cùng file, và tool **đọc stage từ file trên branch + PR** (không dùng file nhớ riêng), chuyển luồng không cần lệnh đặc biệt:

| Muốn | Làm |
|---|---|
| Tự làm tiếp (2a → 2b) | **Gỡ label `qa-auto`** trên Jira. `poll` không đụng ticket nữa. Dùng `/cases`, `/flows`… bình thường |
| Giao lại cho tool (2b → 2a) | **Gắn lại `qa-auto`.** Tool xem file đã có tới đâu rồi chạy tiếp, **không làm lại từ đầu** |

Tool xác định stage như sau:

| Thấy gì | Stage | Tool làm |
|---|---|---|
| Chưa có branch hoặc chưa có `spec.md` | `none` | Chạy Stage 2 |
| Có `open-questions.md` | `needs_info` | Chạy lại Stage 2 khi có trả lời mới |
| Có `spec.md`, thiếu `CASES.md` cho rule nào đó | `spec_ready` | Chạy Stage 3 (không cần label), đăng comment duyệt |
| Có `spec.md` + `CASES.md` đủ mọi rule, thiếu flow | `cases_ready` | Chờ `qa-approved`, rồi sinh flow (Stage 4), chạy thử, mở PR |
| Có đủ flow cho mọi rule | `flows_ready` | Chờ `qa-approved`, rồi chạy thử và mở PR |
| Đã có PR | `pr_open` | Xong phần của tool; người review |

Lưu ý: sang bước sinh flow / chạy thử / PR **luôn cần label `qa-approved`** (cổng người), kể cả khi flow bạn tự viết.

Ví dụ: bạn tự làm tay `/spec` và `/cases`, rồi muốn AI lo phần còn lại → gắn `qa-auto` và `qa-approved`. Tool thấy đã có `spec.md` + `CASES.md` nhưng chưa có flow, nên chỉ làm Stage 4 trở đi (cases coi như bạn đã duyệt).

---

## 6. Lỗi thường gặp

| Triệu chứng | Nguyên nhân / cách xử lý |
|---|---|
| `you are on branch '<x>'...` | Đang ở branch khác. `git switch main` hoặc `git switch qa/<KEY>` |
| `uncommitted changes to tracked files` | Commit hoặc stash thay đổi, rồi chạy lại |
| `missing JIRA_BASE_URL...` | Chưa tạo `~/.config/qa-auto/env` (mục 2) |
| Ticket đứng im, có label `qa-error` | Đọc comment lỗi trên ticket, sửa nguyên nhân, **gỡ `qa-error`** |
| Ticket có `qa-auto` nhưng không chạy | `poll` đã tắt (nó chỉ sống theo terminal/session) → chạy lại, hoặc `bin/qa-auto run <KEY>` |
| `another instance is running` | Đang có một `qa-auto` khác (khoá một pipeline) |
| Test đỏ nhưng AI "không sửa gì" | Có thể đây là app bug, đọc `Fixer said:` trong PR; triage A/B/C/D |
| Flow đỏ ở bước đăng nhập, không liên quan ticket | Có thể flaky; chạy lại `/run` riêng flow đó trước khi kết luận |

---

## 7. Giới hạn hiện tại (nên biết trước khi tin kết quả)

- **Xanh chưa có nghĩa là test đúng.** Bạn là người kiểm cuối: assertion có khớp expected result của spec không? Tool chưa có cổng chất lượng assertion bằng code.
- Có thể **trùng test cũ** (SCRUM-8 sinh `INCREASE_ONE_TO_TWO` dù `INCREASE` đã phủ). Tool chưa so với test có sẵn; `/cases` có nhắc AI báo trùng nhưng chưa được kiểm chứng.
- Flow hiện **hard-code tài khoản demo** (không nên với dữ liệu thật; theo CLAUDE.md tài khoản test phải nằm ở CI secrets).
- Chưa kiểm chứng thật: nhánh ticket mơ hồ (hỏi lại → trả lời → resume), `flow-fixer` sửa selector thật, PR draft đỏ, chốt chặn `known-bug` (mới chỉ test từng hàm, AI chưa từng thử gắn tag).
- Muốn đánh dấu một test đỏ là bug thật của app: bạn tạo bug ticket rồi tự thêm `tags: [known-bug]` và dòng `# Known-bug: KEY-123` vào flow (qua PR). AI không được làm việc này.
- Chi phí: `claude -p` dùng hạn mức Claude của chính tài khoản bạn.
- Chỉ iOS (simulator cần macOS). Android chưa có runner trong `bin/qa`.

---

## 8. Các file liên quan

| File | Vai trò |
|---|---|
| `bin/qa-auto` | Điều phối chế độ tự động |
| `bin/qa`, `bin/qa-check` | Cài build + chạy flow; kiểm độ phủ rule |
| `.claude/agents/spec-extractor.md` · `automation-writer.md` · `flow-fixer.md` | Agent từng stage |
| `.claude/commands/*.md` | Các lệnh `/spec /cases /flows /run /fix /pr` |
| `templates/launchd/` | Tùy chọn: chạy poller nền trên macOS |
| `.qa-work/` | Thư mục tạm (gitignored) |

---

## 9. Chưa làm: QA không mở repo (Luồng 1)

Cách làm "gắn label rồi chỉ review qua Jira + GitHub, không mở repo" **chưa triển khai**; đã hoãn có chủ đích đến khi scale. Nó cần một
**máy chạy trung lập** (GitHub Actions macOS hoặc Mac mini dùng chung) thay vì máy QA, và thêm: trạng thái lưu trên label/branch,
service account riêng cho Jira, trần chi phí theo ngày, cảnh báo khi hệ thống chết, vòng "QA comment → AI sửa", và review bảo mật/dữ liệu
(ticket thật có thể chứa PII). Thiết kế hiện tại (đọc stage từ file + label) được giữ để chuyển lên máy chủ sau này không phải viết lại.
