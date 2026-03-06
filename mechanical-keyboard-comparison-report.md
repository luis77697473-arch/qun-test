# 机械键盘对比评测报告

> 执行时间：2026-03-06
> 执行方式：通过 CLI 工具进行网页搜索、抓取评测内容、提取数据并对比

---

## A. 实际执行过的步骤

1. **尝试打开京东 (JD.com)** — 构造搜索 URL `search.jd.com/Search?keyword=机械键盘`，被反爬机制重定向到风控验证页，无法获取结果
2. **切换到 Amazon.com** — 构造筛选 URL（$50-$150 价位，按评价排序），页面依赖 JavaScript 动态渲染，WebFetch 只拿到框架代码，无实际商品数据
3. **尝试 BestBuy** — 返回 503 服务不可用
4. **策略调整：改用 WebSearch 进行全网搜索** — 搜索 "best mechanical keyboard under $100 comparison review 2026"，获得多家评测站（Tom's Hardware, RTINGS, PCWorld, Tom's Guide 等）的推荐汇总
5. **筛选条件决策**（模拟电商页面筛选逻辑）：
   - 价格：$30-$100（适合普通用户预算）
   - 布局：75%/96%/TKL（不选 60% 太精简，不选全尺寸太占桌面）
   - 连接方式：优先有无线选项
   - 品质：有评测机构实测的主流品牌
6. **选出 3 款候选键盘**，分别通过 WebSearch 抓取详细评测信息：
   - Keychron V5 Max（约 $89-99）
   - Ajazz AK820 Pro（约 $55-68）
   - Keychron C3 Pro（约 $37）
7. **提取、对比、给出推荐**

---

## B. 最终比较的 3 个商品

### 1. Keychron V5 Max

| 项目 | 详情 |
|------|------|
| **价格** | ~$89-99 USD |
| **布局** | 96%（紧凑全尺寸，含数字键盘） |
| **连接** | 三模：蓝牙 5.1 / 2.4GHz / USB-C 有线 |
| **轴体** | Gateron Jupiter（红/茶/Banana 可选），热插拔 |
| **电池** | 4000mAh |
| **结构** | Gasket Mount，多层吸音棉，PBT 双色注塑键帽 |
| **软件** | QMK/VIA 全可编程 |
| **主要卖点** | 在 $100 以下价位提供最接近高端定制键盘的体验，声音深沉饱满，手感出色 |
| **缺点** | 较高的键帽轮廓不含手托、numpad 0 键不是标准双倍宽度、键帽字体略显廉价 |
| **适合谁** | Mac/Windows 双系统用户、需要数字键盘的办公 + 轻度游戏用户、想要"一步到位"的入门者 |

### 2. Ajazz AK820 Pro

| 项目 | 详情 |
|------|------|
| **价格** | ~$55-68 USD |
| **布局** | 75%（81 键 + 旋钮） |
| **连接** | 三模：蓝牙 5.1 / 2.4GHz / USB-C |
| **轴体** | Flying Fish / Gift 线性轴，热插拔 |
| **电池** | 4000mAh |
| **结构** | Gasket Mount，5 层隔音棉，Flex-cut PC 定位板 |
| **特色** | 0.85 寸 TFT 彩色小屏幕（显示时间/电量/连接状态），金属旋钮 |
| **键帽** | 双色注塑 PBT |
| **主要卖点** | 价格极具竞争力，开箱即有出色的"thock"手感，小屏幕既实用又有趣 |
| **缺点** | 配套软件偶有 bug，塑料机身有轻微弯曲感，固件更新支持不确定 |
| **适合谁** | 预算有限但追求性价比的年轻用户、喜欢紧凑桌面布局的人、想要"有点不一样"的用户 |

### 3. Keychron C3 Pro

| 项目 | 详情 |
|------|------|
| **价格** | ~$37 USD（促销低至 $30） |
| **布局** | TKL（87 键，无数字键盘） |
| **连接** | 仅 USB-C 有线 |
| **轴体** | Keychron 自有红轴/茶轴（标准版不支持热插拔，RGB 版支持） |
| **结构** | Gasket Mount，钢板定位板，塑料外壳，内部吸音棉 |
| **软件** | QMK/VIA 全可编程 |
| **键帽** | 双色注塑 ABS |
| **主要卖点** | 价格几乎是同类产品的一半，却提供 Gasket Mount + QMK/VIA 的组合，打字手感远超价位 |
| **缺点** | 无无线功能、仅红色背光、ABS 键帽容易打油、标准版不热插拔 |
| **适合谁** | 第一次尝试机械键盘的新手、预算极低的学生党、固定工位不需要无线的用户 |

---

## C. 推荐结论 — 最均衡的一款

### Ajazz AK820 Pro 是最均衡的选择

| 维度 | V5 Max | AK820 Pro | C3 Pro |
|------|--------|-----------|--------|
| 价格 | $$$ | $$ | $ |
| 无线 | 三模 | 三模 | 无 |
| 热插拔 | 有 | 有 | 标准版无 |
| Gasket Mount | 有 | 有 | 有 |
| PBT 键帽 | 有 | 有 | 无（ABS） |
| 特色功能 | QMK/VIA | TFT 小屏+旋钮 | QMK/VIA |
| 电池 | 4000mAh | 4000mAh | N/A |

**AK820 Pro 以约 $60 的价格提供了以下核心价值：**

- 三模无线（这是 C3 Pro 完全不具备的）
- 热插拔（方便未来换轴体验不同手感）
- PBT 键帽（比 C3 Pro 的 ABS 更耐用）
- Gasket Mount + 5 层隔音（开箱即有优秀声音）
- TFT 彩屏和旋钮（实用且增加差异化）

相比 V5 Max，AK820 Pro 便宜 $30-40，核心体验差距并不大。V5 Max 的优势主要在 QMK/VIA 可编程性和 96% 布局（有数字键盘），但对"普通用户"来说，75% 的紧凑布局更节省桌面空间，而 QMK/VIA 的深度自定义大多数人用不上。

**结论：对于不追求极致但想买到"对的东西"的普通用户，Ajazz AK820 Pro 在价格、功能、手感之间取得了最好的平衡。**

---

## D. 执行中遇到的障碍及解决方式

| 障碍 | 解决方式 |
|------|----------|
| **京东 (JD.com) 反爬验证** — 搜索页面被 302 重定向到风控页 | 放弃 JD.com，切换到国际电商站点 |
| **Amazon.com JS 动态渲染** — WebFetch 只能抓到页面框架代码，无法获取商品列表 | 改用 WebSearch 全网搜索评测和比较文章 |
| **BestBuy 503 错误** — 服务拒绝 | 跳过，不再尝试 |
| **RTINGS/Tom's Hardware 详情页 403/404** — 防止直接抓取 | 用 WebSearch 搜索特定产品评测，从搜索摘要中获取详细信息 |
| **无法真正"点击"页面元素** — CLI 环境没有浏览器引擎 | 通过构造 URL 参数模拟筛选条件，通过多次 WebSearch 迭代获取等效信息 |

---

## 参考来源

- [Tom's Hardware - Best Budget Mechanical Keyboards 2026](https://www.tomshardware.com/best-picks/best-budget-mechanical-keyboards)
- [RTINGS - Best Budget Mechanical Keyboards](https://www.rtings.com/keyboard/reviews/best/cheap-mechanical-keyboards)
- [Tom's Guide - Ajazz AK820 Pro Review](https://www.tomsguide.com/computing/peripherals/epomaker-ajazz-ak820-pro-review)
- [Keychron V5 Max Official Page](https://www.keychron.com/products/keychron-v5-max-qmk-via-wireless-custom-mechanical-keyboard)
- [WePC - Keychron V5 Max Review](https://www.wepc.com/reviews/keychron-v5-max-keyboard/)
- [CravingTech - Keychron V5 Max Review](https://www.cravingtech.com/keychron-v5-max-review-96-mechanical-keyboard-worth-of-investment.html)
- [AppleInsider - Keychron C3 Pro Review](https://appleinsider.com/articles/24/01/05/keychron-c3-pro-review-affordable-excellence-in-a-mechanical-keyboard)
- [PCWorld - Keychron C3 Pro Review](https://www.pcworld.com/article/2104107/keychron-c3-pro-review.html)
- [TechRadar - Keychron C3 Pro Review](https://www.techradar.com/computing/keyboards/keychron-c3-pro)
