# info 档官方移民链接复核清单（2026-07-29）

> 供人工复核。这些是 **info 档（工作签→永居）** 25 国在职业页"Immigration pathways"段展示的**官方移民门户链接**。
> 来源代码：`aijobrisk-go/internal/data/migration.go`。复核请核对**域名是否官方、路径是否有效、语言是否为英文版**。
> 复核后如需改动，改 `migration.go` 里对应常量/`migInfoSpecial` 条目即可。

## A. EU Blue Card 共享门户（18 国统一指向）

以下 18 国在页面上都用**同一条** EU 官方门户链接（正文按国名插值，但链接相同）：

- 常量：`euImmigrationPortal`
- **URL**：`https://immigration-portal.ec.europa.eu/index_en`
- **LinkText**：`EU Immigration Portal`
- 覆盖国家：FR ES IT NL BE AT PL PT GR HU CZ RO LU SK SI HR FI SE

> ⚠️ 复核点：确认 EU 官方门户当前规范域名是否仍为 `immigration-portal.ec.europa.eu`（欧盟站点历史上有过迁移）。

## B. 各国专属门户（7 国，各自链接）

| 国家 | LinkText（页面显示） | URL | 复核点 |
|---|---|---|---|
| 丹麦 DK | Danish Immigration Service (nyidanmark.dk) | `https://www.nyidanmark.dk/en-GB` | 官方，确认 `en-GB` 路径 |
| 挪威 NO | Norwegian Directorate of Immigration (UDI) | `https://www.udi.no/en/` | 官方 UDI |
| 冰岛 IS | Directorate of Immigration Iceland (utl.is) | `https://utl.is/index.php/en/` | 确认 `index.php/en` 是否仍有效（或改根 `/en/`） |
| 瑞士 CH | State Secretariat for Migration (SEM) | `https://www.sem.admin.ch/sem/en/home.html` | 官方 SEM |
| 新加坡 SG | Ministry of Manpower (MOM) | `https://www.mom.gov.sg/passes-and-permits/employment-pass` | 深链到 Employment Pass 页 |
| 日本 JP | Immigration Services Agency of Japan | `https://www.isa.go.jp/en/` | 官方 ISA |
| 韩国 KR | Korea Immigration Service | `https://www.immigration.go.kr/immigration_eng/index.do` | 确认英文站 `immigration_eng` 路径 |

## 复核结论（请填）

- [ ] EU 门户域名/路径 OK
- [ ] DK / NO / IS / CH / SG / JP / KR 逐一 OK
- [ ] 需要修改的项：____________________
