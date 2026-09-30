# Hướng dẫn cho dev iOS — build & giao bản build cho QA

Dành cho dev của một app iOS có automation test do team QA quản lý. QA viết và chạy test trong repo QA
riêng (`qa-pipeline`). Dev **không cần viết test**, chỉ cần làm 3 việc:

1. Xuất **bản build simulator** (`.app.zip`) cho mỗi version.
2. Đặt bản build ở **chỗ QA tải được**, tốt nhất là tự động qua GitHub Release.
3. Giữ **accessibility identifier ổn định** cho các element QA cần test.

```
repo app (dev)                                   repo QA (QA)
push main ─► build simulator ─► GitHub Release ─► báo QA ─► tải build ─► cài lên simulator ─► chạy test
             (.app.zip)          build-<n>         (dispatch)
```

Hướng dẫn cho phía QA: [`huong-dan-qa-pipeline.md`](huong-dan-qa-pipeline.md).

---

## 1. Vì sao cần bản build simulator (không phải `.ipa`)

| | `.app` (simulator) | `.ipa` (máy thật) |
|---|---|---|
| SDK | `iphonesimulator` | `iphoneos` |
| Chạy trên iOS Simulator (CI, máy QA) | ✅ | ❌ |
| Cần ký (signing, provisioning) | Không | Có |
| Dùng cho | Automation test hằng ngày | TestFlight, test tay trên máy thật |

Hai loại có thể build từ cùng một commit. **QA cần bản simulator**, còn `.ipa` vẫn giữ cho TestFlight như bình thường.

---

## 2. Build bản simulator trên máy (để thử)

```bash
# (nếu dự án dùng XcodeGen / CocoaPods thì chạy trước: xcodegen generate / pod install)

xcodebuild -project MyApp.xcodeproj -scheme MyApp \
  -sdk iphonesimulator -configuration Release \
  -derivedDataPath build CODE_SIGNING_ALLOWED=NO build
# dự án có .xcworkspace: thay -project bằng -workspace MyApp.xcworkspace

APP=$(find build/Build/Products/Release-iphonesimulator -maxdepth 1 -name '*.app' | head -1)
ditto -c -k --keepParent "$APP" MyApp.app.zip
```

Ví dụ với ShopDemo:
```bash
cd ios-shop-demo
xcodegen generate
xcodebuild -project ShopDemo.xcodeproj -scheme ShopDemo -sdk iphonesimulator \
  -configuration Release -derivedDataPath build build
ditto -c -k --keepParent build/Build/Products/Release-iphonesimulator/ShopDemo.app ShopDemo.app.zip
```

Lưu ý:
- **Phải nén bằng `ditto`**, không dùng `zip -r` hay upload thẳng thư mục `.app`. Làm vậy có thể mất quyền thực thi
  hoặc symlink, và app sẽ không mở được.
- Dùng cấu hình **Release**, trỏ tới backend **staging** hoặc môi trường test. Không trỏ production.
- Máy Mac chip Apple (và runner `macos-15` của GitHub) build ra `arm64`. Nếu QA dùng Mac Intel, thêm
  `ARCHS="arm64 x86_64" ONLY_ACTIVE_ARCH=NO`.

**Tự kiểm tra trước khi giao:**
```bash
plutil -extract DTPlatformName raw "$APP/Info.plist"      # → iphonesimulator
plutil -extract CFBundleIdentifier raw "$APP/Info.plist"  # → bundle id QA đang dùng
xcrun simctl install booted "$APP" && xcrun simctl launch booted <bundle-id>   # app mở được
```

---

## 3. Tự động publish bản build (GitHub Actions)

Dùng workflow mẫu [`templates/dev-ios/release-build.yml`](../templates/dev-ios/release-build.yml) trong repo QA:

1. Chép vào repo app, đặt tại `.github/workflows/release-build.yml`.
2. Thay các placeholder:

   | Placeholder | Ví dụ |
   |---|---|
   | `__SCHEME__` | `ShopDemo` |
   | `__PROJECT__` | `-project ShopDemo.xcodeproj` (hoặc `-workspace X.xcworkspace`) |
   | `__APP__` | `shopdemo`, tức tên thư mục của app trong repo QA, hỏi QA nếu chưa biết |
   | `__QA_REPO__` | `leelovefree/qa-pipeline` |

3. Thêm các bước setup riêng của dự án (XcodeGen, CocoaPods, secret cấu hình staging…) vào chỗ đã đánh dấu.
4. Merge vào `main`. Mỗi lần push, workflow sẽ:
   - build bản simulator, rồi nén thành `<Scheme>.app.zip`,
   - tạo GitHub Release `build-<n>`, đánh dấu **latest**,
   - báo repo QA qua `repository_dispatch` (event `<app>-build`, payload `{"build": "gh-release:<repo>@build-<n>/<zip>"}`).

Ví dụ đang chạy thật: [`ios-shop-demo/.github/workflows/release-build.yml`](https://github.com/leelovefree/ios-shop-demo/blob/main/.github/workflows/release-build.yml).

**Chỉ muốn build khi code app thay đổi?** Thêm `paths:` vào trigger `push`, ví dụ `Sources/**`, `project.yml`.

### Token

| Secret (trong repo app) | Dùng để | Bắt buộc? |
|---|---|---|
| `QA_DISPATCH_TOKEN` | Báo repo QA có build mới | Không. Nếu thiếu, QA vẫn test bản `latest` mỗi đêm |

Repo QA cũng cần quyền **đọc Release** của repo app nếu repo app là private. Phần này QA tự cấu hình
(secret `QA_BUILDS_TOKEN` bên repo QA). Cả hai dùng một fine-grained PAT hoặc GitHub App với quyền
`Contents: Read and write` trên hai repo. Trong org công ty, nên dùng **GitHub App** thay cho token cá nhân.

---

## 4. Không dùng GitHub Release?

Được, miễn là QA tải được bản build qua một **link cố định**:

| Nơi lưu | QA cấu hình |
|---|---|
| S3 / GCS (presigned hoặc có auth) | `build: https://…/MyApp.app.zip` (token qua `QA_BUILD_TOKEN` nếu cần) |
| Firebase App Distribution, server nội bộ | Link tải trực tiếp tới file `.app.zip` |
| Gửi tay (Slack, Drive…) | Chỉ để QA test trên máy, CI không dùng được |

Nên có cả link **"latest"** (luôn trỏ tới bản mới nhất) lẫn link theo **từng version**.

---

## 5. Accessibility identifier: điều quan trọng nhất cho QA

Test của QA tìm element theo **accessibility identifier**, không theo text hay vị trí. ID mà thay đổi thì test hỏng.

```swift
TextField("Email", text: $email)
    .accessibilityIdentifier("login_email_field")
Button("Log In") { … }
    .accessibilityIdentifier("login_submit_button")
```

Quy ước (ví dụ ShopDemo): `screen_element_role[_variantId]`, như `login_email_field`, `home_screen`,
`cart_item_qty_increment_button_<id>`.

- ✅ Mọi element QA cần tap hoặc kiểm tra đều có ID, kể cả **container của màn hình** (vd `home_screen`) để QA
  xác nhận đang ở đúng màn hình.
- ✅ ID giữ nguyên giữa các version, và không phụ thuộc ngôn ngữ.
- ✅ Bản build cho QA **giữ nguyên ID**. Không strip hay obfuscate.
- ⚠️ **Đổi hoặc xoá ID thì báo QA trước**, ví dụ ghi trong PR description hoặc tag QA review.

Kiểm tra ID trên simulator:
```bash
xcrun simctl launch booted <bundle-id>
maestro hierarchy | grep -oE '"resource-id" *: *"[^"]+"' | sort -u   # Maestro hiện accessibility identifier ở key resource-id
```

---

## 6. Checklist trước khi giao bản build cho QA

- [ ] Là bản **simulator** (`DTPlatformName = iphonesimulator`), nén bằng `ditto`.
- [ ] **Bundle id** đúng, và không đổi so với các bản trước.
- [ ] Mở được trên simulator, trỏ tới **staging**.
- [ ] Các element mới có **accessibility identifier**, và các ID cũ không đổi (hoặc đã báo QA).
- [ ] Đã publish lên GitHub Release hoặc link cố định (workflow ở mục 3 tự làm việc này).

---

## 7. Lỗi thường gặp

| Triệu chứng | Nguyên nhân / cách xử lý |
|---|---|
| QA báo `is a device build (.ipa)` | Đã giao `.ipa`. Cần build với `-sdk iphonesimulator` |
| QA báo `build is 'X' but … expects app_id 'Y'` | Bundle id đã đổi, hoặc giao nhầm app. Báo QA cập nhật `app_id` nếu đổi có chủ đích |
| App cài được nhưng không mở | Nén bằng `zip`/upload thư mục làm mất quyền. Dùng `ditto -c -k --keepParent` |
| `Code signing is required` khi build simulator | Thêm `CODE_SIGNING_ALLOWED=NO` |
| `No such module` / thiếu dependency trên CI | Thêm bước `pod install` / resolve SPM trước khi build |
| Workflow tạo Release lỗi `403` | Thiếu `permissions: contents: write` trong workflow |
| Test QA fail sau khi dev refactor UI | ID bị đổi. Xem mục 5 |

---

## 8. Android (sắp có)

Phía QA chưa hỗ trợ Android. Khi hỗ trợ, dev cần giao một **`.apk`** (không phải `.aab`) bản debug hoặc
staging, cùng quy tắc về `resource-id` ổn định như mục 5.
