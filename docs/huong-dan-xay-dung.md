# Hướng dẫn xây dựng & sử dụng QA automation platform

Dành cho QA mới tham gia: dựng lại toàn bộ hệ thống từ đầu trên một máy Mac mới, thêm một app cần test, và
đưa một ticket Jira đi hết pipeline cho tới khi test chạy tự động trên CI.

---

## 0. Tổng quan

### Hệ thống gồm 2 loại repo

```
┌──────────────────────────────┐        ┌──────────────────────────────────────────┐
│  Repo app (dev quản lý)      │        │  Repo QA — qa-pipeline (QA quản lý)       │
│  vd: ios-shop-demo           │        │                                          │
│                              │ build  │  apps/<app>/app.config.yml  ← test build │
│  code app                    │ ─────► │  apps/<app>/specs/          ← spec       │
│  release-build.yml:          │  link  │  apps/<app>/tests/          ← test case  │
│   build → GitHub Release     │        │  .claude/agents/            ← agent AI   │
│   → báo repo QA              │        │  bin/qa + CI                ← chạy test  │
└──────────────────────────────┘        └──────────────────────────────────────────┘
```

- **QA là trung tâm.** Mọi thứ liên quan đến test nằm trong repo QA. Repo app chỉ cần **xuất bản build**.
- Mỗi app cần test là một thư mục `apps/<app>/`. Muốn test app nào, chỉ cần **trỏ `build:` tới bản build**
  (path trên máy, link tải, hoặc GitHub Release), giống `baseURL` trong Playwright.

### Pipeline 6 bước

| Stage | Ai làm | Input → Output |
|---|---|---|
| 1. Intake | QA/PO | Viết ticket Jira có acceptance criteria |
| 2. Parse & Clarify | Agent `spec-extractor` | Ticket → `apps/<app>/specs/<TICKET>/spec.md` (hoặc `open-questions.md` + **dừng**) |
| 3. Design cases | Agent `automation-writer` | spec → `apps/<app>/tests/<module>/<feature>/CASES.md` |
| 4. Observe & Generate | Agent `automation-writer` | CASES.md + app đang chạy → `<REQUIREMENT_ID>.yaml` (Maestro) |
| 5. Commit & Review | QA (con người) | PR vào repo QA, review, merge |
| 6. CI Regression | GitHub Actions, **không AI** | Cài build → chạy Maestro → pass/fail |

**QA review và duyệt kết quả sau mỗi stage.** Agent chỉ được *đề xuất*, không bao giờ tự merge.

### Công cụ

| Công cụ | Dùng để |
|---|---|
| **Claude Code** | Chạy các agent AI (Stage 2–4) |
| **Maestro** | Framework UI test mobile (flow YAML), tương tự Playwright cho mobile |
| **Maestro MCP** | Cho agent "nhìn" màn hình app thật trên simulator để lấy selector |
| **Jira MCP** | Cho agent đọc ticket và comment câu hỏi |
| **GitHub Actions** | Chạy regression tự động |

---

## 1. Chuẩn bị máy (một lần)

Yêu cầu: macOS, tài khoản GitHub, quyền truy cập Jira.

```bash
# 1. Xcode (App Store) + simulator
xcode-select --install
xcrun simctl list devices available | grep iPhone     # phải có ít nhất 1 iPhone

# 2. Homebrew packages
brew install openjdk@17 gh

# 3. Maestro CLI — dùng script chính chủ, KHÔNG dùng `brew install maestro` (đó là sản phẩm khác)
curl -fsSL "https://get.maestro.mobile.dev" | bash

# 4. Biến môi trường (thêm vào ~/.zshrc)
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="$HOME/.maestro/bin:$PATH"

# 5. Kiểm tra
maestro --version
gh auth login            # đăng nhập GitHub
```

Cài **Claude Code** theo hướng dẫn nội bộ của công ty, sau đó mở một terminal thật (không phải terminal tích hợp
có hạn chế) để làm bước 2.

---

## 2. Kết nối MCP cho Claude Code (một lần)

### 2.1 Maestro MCP

```bash
claude mcp add maestro \
  -e JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
  -- $HOME/.maestro/bin/maestro mcp
```

> ⚠️ Phải dùng **đường dẫn tuyệt đối** tới `maestro`. MCP server không đọc `~/.zshrc`, nên nếu chỉ ghi `maestro`
> thì sẽ lỗi `ENOENT`.

### 2.2 Jira MCP

```bash
claude mcp add --transport http <ten-server> https://mcp.atlassian.com/v1/mcp/authv2
claude mcp login <ten-server>      # chạy trong terminal thật: mở trình duyệt để OAuth
claude mcp list                    # cả 2 server phải hiện ✔ Connected
```

`<ten-server>` phải trùng với `tracker_mcp_server` trong `app.config.yml` của app. Với pilot hiện tại là
`atlassian-personal`. Khi áp dụng thật: dùng Jira công ty.

**Kiểm tra:** mở Claude Code, hỏi *"list my Jira projects"* và *"list Maestro devices"*. Cả hai phải trả về dữ
liệu thật.

---

## 3. Dựng repo QA

Nếu repo đã có sẵn thì chỉ cần `git clone` rồi chuyển sang bước 4. Nếu dựng mới từ đầu, cấu trúc cần tạo là:

```
qa-pipeline/
  CLAUDE.md                       # nguyên tắc chung — Claude Code đọc tự động
  .claude/agents/
    spec-extractor.md             # Stage 2
    automation-writer.md          # Stage 3 + 4
  bin/qa                          # runner: cài build + chạy Maestro (chmod +x)
  .github/workflows/
    regression.yml                # CÁCH test (dùng chung, không AI)
    app-<app>.yml                 # KHI NÀO test từng app
  apps/<app>/
    app.config.yml
    specs/  tests/  reports/
  templates/app/                  # mẫu để thêm app mới
  docs/requirements.md            # spec thiết kế đầy đủ
  docs/huong-dan-xay-dung.md      # file này
  .gitignore                      # .qa-work/
```

Repo QA nên để **private**, trong GitHub organization của công ty.

---

## 4. Thêm một app cần test

### 4.1 Phía repo QA

```bash
mkdir -p apps/<app>/{specs,tests,reports}
cp templates/app/app.config.yml apps/<app>/app.config.yml
sed 's/__APP__/<app>/g; s/__App__/<App>/g' templates/app/app-workflow.yml \
  > .github/workflows/app-<app>.yml
```

Sửa `apps/<app>/app.config.yml`:

```yaml
name: <app>
platform: ios
app_id: com.company.app                                    # bundle id của app
build: gh-release:<org>/<app-repo>@latest/<App>.app.zip    # hoặc path / https URL
ios_device: iPhone 16
tracker_mcp_server: <ten-server-jira>
tracker_project_key: <KEY>
```

Các kiểu giá trị của `build:`:

| Dạng | Ví dụ | Dùng khi |
|---|---|---|
| Path | `~/Downloads/App.app.zip`, `/path/App.app` | Dev gửi file, test trên máy |
| Link | `https://…/App.app.zip` (token qua `$QA_BUILD_TOKEN`) | Build nằm trên S3, Firebase, … |
| GitHub Release | `gh-release:org/repo@latest/App.app.zip` | Repo app tự publish build |

> ⚠️ iOS simulator **không chạy được `.ipa`**. File `.ipa` là bản build cho máy thật. Cần xin dev bản build
> simulator (`.app`, nén zip).

### 4.2 Phía repo app (nhờ dev)

1. **Bản build simulator:** thêm workflow build `-sdk iphonesimulator` → `ditto -c -k --keepParent X.app X.app.zip` →
   `gh release create`. Mẫu: `ios-shop-demo/.github/workflows/release-build.yml`.
2. **Accessibility identifier ổn định** cho mọi element cần test (vd `login_email_field`). Đổi ID là test hỏng,
   nên dev phải báo QA trước.
3. (Tuỳ chọn) **Báo repo QA khi có build mới** bằng `repository_dispatch`, event `<app>-build`, payload
   `{"build": "<link build>"}`.

### 4.3 Token (secrets)

Nếu cả hai repo đều private, cần 1 **fine-grained PAT** (GitHub → Settings → Developer settings → Fine-grained
tokens), quyền `Contents: Read and write` trên repo app và repo QA:

```bash
gh secret set QA_BUILDS_TOKEN   -R <org>/qa-pipeline     # repo QA tải build từ repo app
gh secret set QA_DISPATCH_TOKEN -R <org>/<app-repo>      # repo app báo cho repo QA
```

(`gh secret set` sẽ hỏi giá trị, nên không cần dán token vào đâu khác. Không bao giờ commit token vào repo.)

### 4.4 Kiểm tra

```bash
bin/qa apps                 # thấy <app>
bin/qa install <app>        # tải + cài build lên simulator
```

---

## 5. Đưa một ticket đi hết pipeline

Quy tắc: **mỗi stage chạy trong một session Claude Code riêng**. Mở Claude Code ở thư mục gốc repo QA.

### Stage 1: Ticket
Ticket cần có acceptance criteria rõ ràng, nên viết theo dạng Given/When/Then. Có giá trị mong đợi cụ thể (text
lỗi, màn hình kết quả, …).

### Stage 2: Spec (session 1)
```
Use the spec-extractor agent on <TICKET-ID> for app <app>
```
- Kết quả: `apps/<app>/specs/<TICKET-ID>/spec.md`. Mỗi rule có ID `MODULE.FEATURE.RULE`, trích nguyên văn
  ticket (`source_span`) và độ tin cậy.
- Nếu ticket mơ hồ, agent tạo `open-questions.md`, comment câu hỏi lên Jira rồi **dừng**. Trả lời trên ticket,
  sau đó chạy lại.
- ✅ **QA đọc kỹ spec.md** trước khi đi tiếp.

### Stage 3: Test case (session 2)
```
Use the automation-writer agent for <TICKET-ID> (app <app>), Stage 3 only
```
- Kết quả: `apps/<app>/tests/<module>/<feature>/CASES.md`, mỗi rule có một case (preconditions, steps,
  expected).
- ✅ **QA review CASES.md**: dữ liệu test, bước thực hiện, kết quả mong đợi.

### Stage 4: Maestro flow (session 3)
Chuẩn bị: bật simulator, rồi `bin/qa install <app>`.
```
Use the automation-writer agent for <TICKET-ID> (app <app>), Stage 4
```
- Agent **inspect màn hình thật** để lấy selector (không đoán), viết `<REQUIREMENT_ID>.yaml`, rồi chạy thử bằng
  `bin/qa run <app> --module <module> --no-install`.
- Giới hạn: tối đa 15 thao tác / 5 vòng suy luận cho mỗi case. Vượt quá thì agent dừng và báo lại.
- ✅ **QA đọc từng flow và tự chạy lại một lần.**

### Stage 5: PR
```bash
git checkout -b <ticket-id>-<feature>
git add apps/<app>/specs apps/<app>/tests
git commit -m "<TICKET-ID>: <feature> spec, cases, flows"
gh pr create
```
CI tự chạy test của app trên PR. QA khác review, sau đó merge.

### Stage 6: Regression tự động
Sau khi merge, test chạy tự động (xem mục 7). Không cần làm gì thêm.

---

## 6. Chạy test hằng ngày (`bin/qa`)

```bash
bin/qa apps                                        # danh sách app
bin/qa run <app>                                   # cài build trong config + chạy toàn bộ
bin/qa run <app> --build ~/Downloads/X.app.zip     # test một bản build cụ thể
bin/qa run <app> --module auth                     # chỉ một module
bin/qa run <app> --tags smoke                      # chỉ flow có tag smoke
bin/qa run <app> --no-install                      # chạy lại trên app đã cài
bin/qa install <app>                               # chỉ cài (trước khi viết flow mới)
```

Báo cáo JUnit nằm ở `.qa-work/<app>/report.xml`. CI cũng upload file này.

---

## 7. CI chạy khi nào

File `.github/workflows/app-<app>.yml`:

| Sự kiện | Test bản build nào |
|---|---|
| Repo app publish build mới (`repository_dispatch`) | Đúng bản vừa build |
| PR / push vào `main` có thay đổi `apps/<app>/**`, `bin/**`, workflow | Bản trong config (latest) |
| Hằng đêm 03:00 UTC | Bản trong config (latest) |
| Chạy tay (Actions → Run workflow) | Tuỳ chọn: nhập build + module |

Kết quả pass/fail là **exit code của Maestro**. Không có bước AI nào trong CI.

---

## 8. Lỗi thường gặp

| Triệu chứng | Nguyên nhân / cách xử lý |
|---|---|
| `maestro` lạ, không có lệnh `test` | Đã cài bằng `brew install maestro` (sai sản phẩm). Gỡ ra, cài bằng `curl` |
| MCP maestro lỗi `ENOENT` | `claude mcp add` phải dùng đường dẫn tuyệt đối `~/.maestro/bin/maestro` |
| `Unable to locate a Java Runtime` / test fail lạ | Chưa set `JAVA_HOME` sang JDK 17 |
| MCP báo `Device became unreachable` | Đã reboot simulator giữa session. Mở session Claude Code mới |
| `Jira MCP` không login được | `claude mcp login` phải chạy trong terminal thật (cần mở trình duyệt) |
| `is a device build (.ipa)` | Cần bản build simulator (`.app.zip`) |
| `build is 'X' but … expects app_id 'Y'` | Trỏ nhầm build của app khác, sửa `build:` hoặc `app_id` |
| Popup "Save Password?" che màn hình iOS | Dismiss có điều kiện trong flow (`runFlow when visible "Not Now"`) |
| CI không tải được build | Thiếu hoặc hết hạn secret `QA_BUILDS_TOKEN` |

---

## 9. Nguyên tắc không được vi phạm

1. AI không bao giờ được biến fail thành pass. CI chỉ tin exit code của Maestro.
2. Ticket mơ hồ thì dừng lại và hỏi con người, không đoán.
3. Mọi bước tự động đều có giới hạn số lần thử, số thao tác và thời gian.
4. Không có gì vào `main` nếu con người chưa duyệt PR.
5. Mọi file (spec, case, flow) truy ngược được về ticket qua requirement ID.
6. Tài khoản test và token chỉ lưu trong secrets. Không dùng dữ liệu thật của khách hàng hay rider.

---

## 10. Chưa làm (lộ trình)

- **Stage 7 — repair-agent:** tự sửa test khi chỉ đổi selector, từ chối khi app có lỗi thật.
- **Stage 8 — reporter:** báo cáo mỗi lần chạy (model, số lần thử, chi phí, người duyệt).
- **Android runner** trong `bin/qa`.
- Script kiểm tra độ phủ (mọi ID trong spec đều có trong CASES.md) chạy trên CI.
- Tiêu chí "atomic rule" và kỹ thuật thiết kế test (negative, boundary) cho các agent.
