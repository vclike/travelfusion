# 航空公司规则与体验知识调研：结构化事实底稿

## 执行摘要

全球航空客运的可核实规则已呈现「三档免费额度」结构：全服务航司计重 20 公斤托运加 5–8 公斤手提（已确认 5 / 7 / 8 公斤并存，东航 unknown、深航 5 vs 8 公斤未裁决），廉航基础票仅给 7 公斤或座位下小包，欧美头部航司以件制 2 件 23 公斤为主。这不是定价偏好，而是 IATA 决议 302 与中国民航规章共同约束下的制度分层。〔高〕最反直觉的一条：中国全服务航司并不存在统一的「31–32 英寸」经济舱间距通则——南航自家 A320 高密度子变体官方自报 28/29/36 英寸，与春秋、九元同档〔中〕。最关键的建议：知识库必须以「承运人 × 机型 × 舱位 × 航段」四元组为最小主键，任何航司级单值字段都会产生事实错误。整体置信度：行李与餐食〔中〕（官网一手充足），座椅与口碑〔低〕（官方披露高度不对称）。

## 结论速览表

| 声明 | 置信 | 支持来源数 | 反驳来源数 |
|---|---|---|---|
| 中国国内线「经济舱 20 公斤免费托运」是行业惯例而非国家规定，规章已删除一刀切要求、改为强制披露义务 | 〔中〕 | 2（民航规章原文 + 规章解读同源转述，非独立来源） | 0 |
| 免费额度呈三档结构：全服务计重制、廉航座位下小包或 7 公斤、欧美件制 23 公斤 | 〔高〕 | 5（国航/南航/东航/海航/亚航） | 0 |
| 机型布局比航司品牌更能决定经济舱舒适度，同一机型内部子变体差异大于航司之间差异 | 〔中〕 | 3（南航官网三种窄体布局 + SeatMaps 东航 737-800 五版本） | 1（媒体「中国航司 31–32 英寸」通则） |
| 中美欧对登机口行李的执行力度在 2026 年同步收紧，行李预购是唯一低成本路径 | 〔中〕 | 4（春秋官网价目、瑞安媒体核查、亚航官方、媒体报道） | 0 |
| 国内航司免费餐食未被取消，2025 年三大航航食支出仍双位数增长〔数字核查 E9：证据为 国航 45.05 亿元（同比+8.15%）、东航 46.31 亿元（+9.56%）、南航 48.71 亿元（+10.55%）——仅南航为双位数，8.15%/9.56% 为个位数，属把三个增速合并概括为「双位数」的口径错误〕〔数字核查 E9：证据为 国航 45.05 亿元（同比+8.15%）、东航 46.31 亿元（+9.56%）、南航 48.71 亿元（+10.55%）：三家仅南航为双位数，报告把单数增速合并表述为「三大航双位数」属合并口径错误〕 | 〔中〕 | 2（媒体访谈 + 财报支出数据） | 0 |
| Spirit 已于 2026-05-02 停运清算，不可再作为可预订选项 | 〔中〕 | 1（NPR 报道） | 0 |
| SeatGuru 已于 2025-10-31 关停，航司级座椅数据源只剩第三方观测 | 〔高〕 | 3（维基、Australian Frequent Flyer、多源替代源综述） | 0 |
| 航司级「服务口碑」在中国全服务航司上无任何可交叉验证的量化证据 | 〔中〕 | 2（检索无果 + 仅 UGC 来源） | 0 |

## 正文

### 一、免费行李额度的制度分层是硬约束，不是产品选择

判断：全球航司的免费额度差异可完整归结为三套制度，其中中国与东南亚的分野来自「是否把行李从票价剥离」，欧美头部航司则由件制标准统一。〔高〕

中国民航没有 20 公斤的国家强制标准。交通运输部令 2021 年第 3 号《公共航空运输旅客服务管理规定》自 2021-09-01 施行，删除了原《国内客规》中关于行李尺寸、重量、免费行李额、逾重费的一刀切条款，改为要求承运人在运输总条件中自行明确并对外公布 [citation:公共航空运输旅客服务管理规定](https://xxgk.mot.gov.cn/2020/gz/202112/W020211221393138820021.pdf)〔高〕。同一部规章把免费额转为强制披露义务，网络销售客票时须以显著方式告知所选航班的行李规定；2026 年的媒体调查指出第三方平台购票普遍无此提示，正是 20 寸登机箱在机场被收费的投诉根源 [citation:公共航空运输旅客服务管理规定](https://xxgk.mot.gov.cn/2020/gz/202112/W020211221393138820021.pdf)〔高〕。含义：20 公斤应作为「行业惯例默认值」入库，同时保留「以该航司运输总条件为准」的覆盖规则。

这一惯例在中国全服务航司中高度趋同，且已被逐家官网核验。

| 航司 | 国内线免费托运 | 手提件数与重量 | 手提尺寸 |
|---|---|---|---|
| 国航 | 经济舱 20 千克 | 1 件 | 100×60×40 厘米（托运）〔数字核查 E131：证据为 E131 唯一尺寸条目为「单件托运行李最大体积（三边）= 40×60×100cm」，且属海南航空（2026-01）；台账中国航（E1）无任何托运尺寸条目，报告把海航数值倒序后归给国航〕〔数字核查 E131：证据为 该尺寸在台账中唯一出现处为 E131（海南航空，2026-01，40×60×100cm）；报告将同一数值倒序后归给国航，国航无对应条目〕 |
| 南航 | 经济舱 20 公斤 | 1 件，5 千克 | 三边之和 115 厘米 |
| 东航 | 经济舱 20 公斤 | 1 件；头等舱 2 件 10 公斤 | 托运 40×60×100 厘米〔数字核查 E3：证据为 E3 仅含 20KG 免费额、头等舱 2 件 10KG、托运单件最大重量 50 千克，无任何托运尺寸；40×60×100cm 属 E131（海南航空，2026-01），属跨航司归属混用〕〔数字核查 E131：证据为 E3（东航）无任何托运尺寸条目；台账中 40×60×100cm 属 E131（海南航空，2026-01）——报告把海航的体积值挂到东航，属归属/口径混用〕 |
| 海航 | 经济舱 20 公斤 | 1 件，7 公斤 | 55×40×20 厘米 |
| 川航 | 未取得国内线数值 | 1 件，8 公斤 | 20×40×55 厘米 |
| 厦航 | 经济舱 20 千克 | 1 件，8KG | 55/40/20 厘米 |
| 吉祥 | 经济舱 20 公斤 | 1 件，5 公斤（2025-08-08 生效版） | 55×40×20 厘米，三边和 ≤115 厘米 |
| 深航 | 官网总条件未列明 | 1 件，5 公斤 | 55×40×20 厘米 |

国航与南航数值见 [citation:国航行李运输](https://www.airchina.com.cn/zh-CN/content/travel_info/preparing/conditions/contact_us/baggage_transport) 与 [citation:南航行李规定](http://3g.csair.com/CSMBP/newMyTrip/Baggage/Baggage.html)〔中〕。海航的 20/30 公斤与 7 公斤手提分别见 [citation:海南航空免费托运行李](https://www.hnair.com/lvxingxinxi/xlxx/mftyxl/) 与 [citation:海南航空乘机须知](https://www.hnair.com/guanyuhaihang/hhdt/hhgg/cxts/cxts2024/202401/t20240124_64240.html)〔中〕。吉祥的 5 公斤是 2025 年 8 月 8 日生效版把原 10 公斤收紧后的值，2023 年 10 月版曾为 10 公斤 [citation:吉祥航空行李运输规定](https://meiyacommonfile.oss-cn-shenzhen.aliyuncs.com/policy/content41e1c91754449120477.pdf)〔高〕。

手提重量 5–8 公斤的分歧不是矛盾而是各家自主权的结果。吉祥 2023 年由 10 公斤降到 5 公斤，与南航现行 5 公斤、深航 5 公斤一致；海航与厦航的官网提示给出 7 公斤与 8KG。知识库若只写「中国全服务航司手提 5–8 公斤」是可用的区间，但必须逐家落字段。

东南亚廉航的免费额度是第三档：亚航基础票价只含 2 件合计 7 公斤（56×36×23 厘米加小包 40×30×10 厘米），无免费托运，现场购买价约为线上预购的 2 到 4 倍 [citation:亚航行李规定](https://www.airasia.com/aa/inflight-comforts/zh/hk/baggage.html)〔高〕。越捷 Eco 档同样是 7 公斤合计，SkyBoss 档升至 10–14 公斤〔数字核查 E35：证据为 E35: Eco 档 7 kg；SkyBoss 档手提额度（flyfono 口径）= 10 kg（2026），无 14 公斤上限；报告擅自扩展出上限值〕〔数字核查 E35：证据为 E35: SkyBoss 档手提额度（flyfono 口径）= 10 kg（2026），无 14 公斤上限〕 [citation:VietJet 行李政策](https://www.cabinzero.com/blogs/air-travel-tips/vietjet-air-baggage-allowance)〔中〕。春秋航空 1 件 7 公斤、20×30×40 厘米，且安检、值机、登机口三重查验 [citation:春秋航空行李规则解析](https://ql1d.com/general/27786956.html)〔中〕。

欧美廉航已把基础票的行李架位清空。Ryanair 与 Wizz Air 只保留座位下 40×30×20 厘米、10 公斤的小包，easyJet 为 45×36×20 厘米、15 公斤 [citation:Which? 航空随身行李评测](https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk)〔高〕。这是可引用的官方核查而非转述，且该来源同时指出 easyJet 的 Essentials 票价含 23 公斤托运却不含随身行李——「行李越少越便宜」是错误的线性心智。

含义：对知识库而言，「免费额度」必须拆成托运与手提两个独立字段，且每家标注是重量制还是件数制。廉航还需要第三个字段「手提是否需在值机口过秤」——这是体验差异的主要来源。

### 二、收费项：超廉航已把「买得晚」定价成独立惩罚

判断：行李、选座、餐食、值机、优先登机五项在超廉航上全部转为收费项，且现场价普遍是线上预购价的 2–4 倍，这使「何时决定」成为比「买什么」更重要的变量。〔高〕

春秋航空官网价目表显示国内线 3000 公里以上航距 20 公斤托运网上 179 元、柜台 420 元，40 公斤网上 339 元、柜台 840 元；国际线 40 公斤网上 499 元、柜台 1320 元 [citation:春秋航空行李价格公告](https://news.ch.com/news/2026-06-16-00-00.html)〔中〕。同源 2026-08-16 起国内与国际线网价改用曲线定价，线上购行李统一截止于计划起飞前 1 小时 [citation:春秋航空行李价格公告](https://news.ch.com/news/2026-06-16-00-00.html)〔中〕。

这与欧美航司的价差结构同向。Ryanair 20 公斤托运订票加购 £21.49 起、bag drop 柜台统一 £59.99、登机口 10 公斤箱 £46–75、超规手提箱 £70–75 [citation:Ryanair 行李费用指南](https://flighttribe.co.uk/ryanair-baggage-allowance/)〔中〕。泰国狮航国内 20 公斤预付 660 泰铢、柜台按每公斤 350 泰铢计，同重量约为预付十倍以上 [citation:Thai Lion Air 行李政策](https://baggagepolicies.com/thai-lion-air-baggage-policy/)〔中〕。

值机收费是欧美独有的机制。Ryanair 对未在起飞前 2 小时以上完成网上值机者收机场值机费，2026 年媒体口径 £30–£55，且受出发地法规封顶——西班牙 £30、奥地利 €40 [citation:Ryanair 条款与细则](https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564) [citation:Ryanair 行李费用指南](https://flighttribe.co.uk/ryanair-baggage-allowance/)〔中〕。春秋航空的网上值机规定全文没有任何值机收费条款，未网值机只是须到柜台办理 [citation:春秋航空网上值机规定](https://www.ch.com/Default/CheckInAttention)〔中〕。这是一个干净的反例：把值机做成收费项是欧洲航司的主动选择，不是行业惯例。

Frontier 走得更远，把柜台帮旅客值机打印登机牌的「代理协助」也列为 $20 收费项，优先登机 $7.99，电话订座每位旅客 $35 [citation:Thrifty Traveler 航司评测](https://thriftytraveler.com/reviews/flights/frontier-airlines/)〔中〕。

含义：知识库需要「收费项清单」这个字段数组，并对每项标注决策截止时点。春秋的 1 小时、Ryanair 的 2 小时是可直接入库的操作参数。

### 三、座椅：机型布局压倒航司品牌

判断：经济舱排距的决定变量是机型子变体而非航司，同一航司内部窄体 28–30 英寸、全经济舱高密度 28–29 英寸、宽体 31–33 英寸三者并存。〔中〕

南航是唯一在官网提供逐机型一手数据的中国航司，公布座位总数、各舱座位数、排距、扶手间宽度与后倾距离，并按 A320(320)、A320(32X)、A321(321)、A321NEO(32N)、B737-800 等子型号分页 [citation:南航机舱布局页](https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idksocbjvnb.shtml)〔高〕。

| 机型 | 总座位 | 客舱布局 | 经济舱排距 | 扶手间宽度 |
|---|---|---|---|---|
| A320(320) | 152 | 公务 8 / 明珠 24 / 经济 120 | 30 英寸（国际线页另列 30–39 区间） | 17.7 英寸 |
| A320(32X) | 180 | 全经济舱高密度 | 28/29/36 英寸 | 19.07–20.75 英寸 |
| A321(321) | 179 | 公务 12 / 明珠 24 / 经济 143 | 31/43 英寸 | 17.8 英寸 |
| B777-300ER | 361 | 公务 28 / 明珠 28 / 经济 305 | 31/32/33 英寸 | 18.5/16.8/16.3 英寸 |

窄体三行见 [citation:南航A320(320)](https://www.csair.com/hk/tc/tourguide/flight_service/cabin_layout/kongke/18h1tllaukv3c.shtml) [citation:南航A320(32X)](https://csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/1hh7mef56t4pp.shtml) [citation:南航A321(321)](https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idkvmedtkic.shtml)；宽体见 [citation:南航B777-300ER](https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/boyin/1d8l5fmj01j95.shtml)〔中〕。宽体行尤其值得注意：同机经济舱内段最窄处仅 16.3 英寸，比 3-4-3 布局的 17 英寸更窄——十联排的代价被官方数据直接证实。

东航 737-800 在 SeatMaps 口径下有 5 种布局版本，公务舱 8–20 座、经济舱 138–168 座，各版本经济舱排距 30–32 英寸，宽度 17–17.1 英寸 [citation:SeatMaps 东航737-800](https://seatmaps.com/zh-CN/airlines/mu-china-eastern/boeing-737-800)〔中〕。国航 A320-200 为 8 商务加 150 经济共 158 座，排距 30 英寸、宽 17.7 英寸 [citation:SeatMaps 国航A320](https://seatmaps.com/zh-CN/airlines/ca-air-china/airbus-a320)〔中〕。两个来源都属第三方观测，权威性低于南航官网。

全球基准是 30–32 英寸，低廉航 28–29 英寸。Wizz Air 28 英寸、Frontier 国际航班 28 英寸、easyJet 28.5–29 英寸、Ryanair 28–29 英寸是最窄一档 [citation:Travel+Leisure 亚洲航司腿部空间排行](https://www.travelandleisureasia.com/hk/travel-tips/trip-planning/airlines-that-offer-the-most-and-the-least-legroom/amp) [citation:Simple Flying 经济舱排距盘点](https://simpleflying.com/economy-seats-worlds-greatest-pitch-2026/)〔中〕。反向案例 JetBlue 自 2026 年夏季起将空客机队统一降至 30 英寸，改推 36–37 英寸的付费前排产品 [citation:Travel+Leisure 亚洲航司腿部空间排行](https://www.travelandleisureasia.com/hk/travel-tips/trip-planning/airlines-that-offer-the-most-and-the-least-legroom/amp)〔中〕。

含义：知识库的座椅字段如果只有「航司 → 排距」两级结构，会在两个方向出错——高估廉航、低估南航高密度型。最小可用结构是「航司 → 机型 → 排距区间」。

数据源环境已经改变。SeatGuru 于 2025-10-31 关停，域名重定向至 TripAdvisor，25 年积累的座位图数据整体下线；其数据在 2020 年初即停止更新 [citation:SeatGuru 词条](https://en.wikipedia.org/wiki/SeatGuru)〔高〕。替代源中 AeroLOPA 被原 SeatGuru 创始人公开背书，座位图由执业建筑师按真实比例绘制，覆盖 208 家航司；SeatMaps 交互体验最接近 SeatGuru 但被行业批评数据不准确 [citation:Australian Frequent Flyer 座位图数据源综述](https://australianfrequentflyer.com.au/find-accurate-airline-seat-maps) [citation:SeatGuru 词条](https://en.wikipedia.org/wiki/SeatGuru)〔中〕。含义：知识库若要保留排距字段，须记录来源层级（官网 / AeroLOPA / SeatMaps / 媒体），并把「官网优先、观测源兜底」写成硬规则。

### 四、餐食：国内航司未取消免费餐，美系正在反向调整

判断：截至 2026 年 9 月中国航司经济舱免费餐食未取消且投入仍在加码，与之相反美国航司正按航段距离削减免费饮品与零食——两个市场的方向完全相反。〔中〕

东航、川航、祥鹏航空客服均确认免费餐食继续提供，同时以增值服务方式推出付费定制餐，付费餐价格区间 19 元至 344 元 [citation:国内航司付费餐调查](https://news.qq.com/rain/a/20260909A0C1Q000)〔中〕。具体案例包括国航 344 元海鲜鱼子酱高端拼盘、东航西安出港 19–45 元付费轻食、川航 58 元冒菜、祥鹏统一 40 元每份 [citation:解放日报航食报道](https://www.jfdaily.com/wx/detail.do?id=1163861)〔中〕。同一来源给出 2025 年航食支出：国航 45.05 亿元同比增长 8.15%、东航 46.31 亿元增长 9.56%、南航 48.71 亿元增长 10.55% [citation:解放日报航食报道](https://www.jfdaily.com/wx/detail.do?id=1163861)〔中〕。支出增长与「仍在加码」一致，但免费餐食的运价结构——哪些航线含餐、哪些不含——本轮完全未取得官方文本，这是知识库不能填的字段。

海航是国内唯一把免费餐食可兑换为积分的航司。官网载明加购付费餐时免费餐食继续提供，旅客也可选择「餐食兑换积分」放弃免费餐食换取最高 600 积分，须在计划起飞前 4 小时前预订 [citation:海南航空餐食升级](https://www.hnair.com/dachenghaihang/kongzhong/canshi/cssj/202504/t20250408_75160.html)〔中〕。

美系方向相反。达美自 2026 年 5 月 19 日起取消 350 英里以下经济舱的免费零食与饮品，涉及约 9% 日航班量；6.5 小时及以上航段提供免费啤酒、葡萄酒与烈酒 [citation:达美机上餐饮说明](https://www.delta.com/us/en/onboard/food-and-beverage/overview)〔高〕。同口径下美航在 250 英里以上提供免费零食与无酒精饮料，联航全航班提供免费无酒精饮料、300 英里以上提供免费小吃 [citation:达美机上餐饮说明](https://www.delta.com/us/en/onboard/food-and-beverage/overview)〔高〕。后两项是同一官网页面的对比表述，其适用范围是「美国国内航段口径」，长途国际主舱是否仍免费餐食、酒水是否收费，未取得任何官方确认——这是知识库里必须标 unknown 的字段。

东南亚与欧美廉航一致采用无免费餐食加机上付费销售。亚航 Santan 预订套餐自 RM10 起、较单点省至多 RM7 [citation:Economy Traveller 亚航套餐报道](https://economytraveller.com/airasia-adds-new-santan-value-combo-meals-from-rm10/)〔中〕。Frontier 官网价非酒精饮料 $3.50 起、零食 $6.99 起、酒类 $9.99 起 [citation:UpgradedPoints Frontier 评测](https://upgradedpoints.com/travel/airlines/frontier-airlines-review/)〔中〕。

含义：餐食字段应设为「是否免费正餐 + 是否含免费饮品 + 免费饮品的航段门槛」三段结构。用单一布尔值「含餐」会在美系航司上产生错误。

### 五、联盟与服务口碑

判断：联盟归属在本轮取得权威佐证的仅覆盖 7 家中国与主要国际航司，Skytrax 2026 榜单与联盟状态之间存在可核验的量化落差点。〔中〕

厦航于 2012 年 11 月 21 日加入天合联盟、为第 19 位成员，至 2026 年 8 月仍为正式成员；东航与南航同属天合，国航与深航属星空联盟 [citation:厦航联盟公告](https://www.xiamenair.cn/zh-ph/article-detail?articleLink=/cms-i18n-ow/cms-zh-ph/contents/84904.json)〔中〕。国际航司方面，oneworld 由美航、英航、卡塔尔、日航、国泰等 15 家组成；天合 18 家含达美、法航、大韩；星盟 26 家含联航、汉莎、ANA、新航、泰航；阿联酋航空 2026 年为非联盟航司 [citation:2026 航空联盟与合作伙伴指南](https://travelvient.com/guides/airline-alliances-and-partners-2026/)〔中〕。海航是否仍为天合成员、川航与吉祥是否为星盟成员，本轮无任何来源，标 unknown。

Skytrax 2026 世界航空奖前十为新航、卡塔尔、国泰、ANA、土航、阿联酋、法航、海航、日航、大韩；三大美国航司无一进入前十 [citation:Business Insider Skytrax 2026 排名](https://www.businessinsider.com/best-airlines-in-the-world-ranking-passengers-skytrax-2026-9)〔中〕。最佳经济舱前十中新航第 1、国泰第 2、卡塔尔第 3、长荣第 4、ANA 第 5、日航第 6、海南第 7、土航第 8、星宇第 9、达美第 10，达美是唯一入榜的美系航司 [citation:BBC 最佳经济舱航空公司](https://www.bbc.com/travel/article/20260924-the-worlds-five-best-economy-airlines-for-2026-and-what-makes-them-so-much-better) [citation:Business Insider Skytrax 2026 排名](https://www.businessinsider.com/best-airlines-in-the-world-ranking-passengers-skytrax-2026-9)〔中〕。海航同时出现在世界奖第 8 与经济舱第 7，是本轮唯一有双重官方榜单背书的中国航司。

但「川航餐食好、厦航服务好」这类口碑判断无任何可交叉验证的量化证据。本轮只取得航班客舱行李标准提醒、餐饮服务营销页与旅客主观反馈片段，未找到 Skytrax 评分、投诉率或满意度调查；新浪旅游稿「首选海航、川航、厦航——服务好，餐食丰富」属用户生成内容，不足以支撑结论。东南亚方面唯一可用的量化口碑是 Click Intelligence 2025 年客户不满指数，亚航以 50 列全球第 6，是前十唯一东南亚航司，主要抱怨为延误严重与行李政策复杂 [citation:Travel Daily 2025 客户不满指数](https://m.traveldaily.cn/article/188765/)〔中〕。越捷 2025 年上半年准点率 67.7%，低于越南航空 71% 与竹子航空 81% [citation:越南民航准点率报道](https://www.vietnam.vn/zh-cn/ty-le-bay-dung-gio-trung-binh-chi-dat-62-6)〔中〕。

含义：知识库的口碑字段应分两层——「可量化指标」（榜单位次、准点率、投诉指数）与「主观印象」。后者目前无一家中国航司可入库，宁缺毋滥。

### 六、承运类型与存续状态

判断：Spirit 停运使「超廉航」这一类别在美国出现空缺，而中联航是中国唯一执行计件制的国有航司，两者都是知识库必须显式建模的例外。〔高〕

Spirit Airlines 已于 2026 年 5 月 2 日停止运营并进入 Chapter 7 清算，不再售票、不再运营航班 [citation:NPR Spirit 停运报道](https://www.npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds)〔高〕。直接诱因是伊朗战争推高航油价格、叠加向白宫寻求的 5 亿美元纾困谈判破裂，同时传统航司推出 basic economy 复制其打法 [citation:NPR Spirit 停运报道](https://www.npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds)〔高〕。这是唯一直接反证「超廉航模式不可持续」的案例，且诱因链是双重的——外部成本冲击与内部模式被复制，机制清楚。

中联航的规则在中国廉航中独树一帜。2020 年 11 月 13 日生效第七版规定 J/C/W/Y/M/E/H/K/L/N/R/S/V/D/T 舱可免费手提 1 件、不超 10 千克、20×40×55 厘米，2020 年 7 月由 20×30×40 放宽而来；特价 I/Z/U 舱无免费手提额、可购 100 元每件；托运实行计件制每件 23 公斤，是国内首家执行计件制的国有航司 [citation:中联航行李规定](https://info.flycua.com/jcms/publish/APP/cpxz/j20230511_363_3398_9494.html)〔高〕。其免费手提限「软包」，不含带拉杆或轮子的行李箱。付费托运 23 公斤首件按航段约 100 元（800 公里内）、180 元（801–2000 公里）、260 元（2001 公里以上）[citation:中联航行李规定](https://info.flycua.com/jcms/publish/APP/cpxz/j20230511_363_3398_9494.html)〔中〕。中联航 737-800 为 186 座全经济舱布局，座椅间距 30–31 英寸 [citation:SeatMaps 中联航737-800](https://seatmaps.com/zh-CN/airlines/kn-china-united-airlines/boeing-737-800)〔中〕。

需要标注的口径反转：全球全服务航司正在从计重制转向计件制。泰航自 2026 年 3 月 2 日起由计重制改为计件制，经济舱 Full/Flex 票 2 件乘 23 公斤、Standard/Saver 票 1 件乘 23 公斤 [citation:Executive Traveller 泰航行李新规](https://www.executivetraveller.com/news/thai-airways-new-luggage-allowance)〔中〕。新加坡航空采用双轨制，除飞抵美国与加拿大外按重量计（经济舱 30 或 25 公斤），飞美加航线按件数计（经济舱 2 件乘 23 公斤）[citation:UpgradedPoints 新航行李](https://upgradedpoints.com/travel/airlines/singapore-airlines-baggage-fees/)〔中〕。国泰按行程单标注 PC（件数）或 K（重量）两种制度并存，单件上限经济舱 23 公斤、三边合计不超过 158 厘米，超尺寸加收 200 美元每件、超 32 公斤按 4 倍加收 [citation:国泰额外行李收费](https://www.cathaypacific.com/cx/en_US/baggage/extra-baggage-charges/pay-cash-or-by-credit-card.html)〔中〕。含义：知识库的「计量制」字段不能是航司级常量，新航一家内并存计件/计重两制；泰航为整体改制，必须以「航线区域」为条件。

国际航司手提上限的量级差同样需要建表。ANA 国际线计件制经济舱 2 件乘 23 公斤 [citation:ANA 行李改制说明](https://www.ana.co.jp/en/jp/promotion/renewal-2025-2026/system/)〔中〕；卡塔尔航空经济舱各票价免费托运均为 2 件每件不超过 23 公斤，手提 1 件不超过 7 公斤 [citation:卡塔尔航空行李额度](https://www.qatarairways.com/en-us/baggage/allowance.html)〔中〕；日本航空国际线经济舱 2 件乘 23 公斤、手提 2 件合计 10 公斤 [citation:JAL 行李指南](https://aifly.one/guides/japan-airlines-baggage-allowance/)〔低〕。JAL 的唯一来源是二手指南、置信度仅低，未取得官网原始页面。

北美件制基准有两个互不隶属的官方来源互证。达美规定托运行李三边之和不超过 62 英寸（157 厘米），西南航空标准重量限制为每件 50 磅 [citation:达美行李总览](https://www.delta.com/us/en/baggage/overview)〔高〕。达美对件制托运实行阶梯收费：第二件每程 55 美元、第三件起每程 200 美元，且件数、重量、尺寸三类超限各自单独计费 [citation:达美行李总览](https://www.delta.com/us/en/baggage/overview)〔高〕。「50 磅 / 62 英寸」是北美通行基准，但「前 2 件免费」这一行业常见口径未读到任何一手原文，标 unknown。

联程场景的规则选择由 IATA 决议 302 的四步法决定：各参与承运人规则相同则通用；不同时整程适用最主要承运人（MSC）规则；MSC 无公布规则则适用接收行李承运人规则；接收方亦无则按航段分段适用各实际承运人规则 [citation:ANA 联程行李 IATA 决议说明](https://www.ana.co.jp/en/jp/guide/boarding-procedures/baggage/international/iata-302/)〔中〕。MSC 以行李运输段为单位逐段选取，交通会议区 TC1 为西半球、TC2 为欧洲中东非洲、TC3 为亚洲与亚太，中国归入 TC3 之下的东南亚次区 [citation:IATA 联运行李指引](https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf)〔中〕。北美航线是例外：美国与加拿大要求客票第一张联程客票上的市场航空公司规则适用于该客票全部航段，美国依据 U.S. DOT Regulation 399.87，加拿大依据 CTA Order 2014-A-158 [citation:IATA 联运行李指引](https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf)〔中〕。中国航司已把该框架内化，首都航空《国际及地区航线运价手册》在「第二部分 行李规则」中完整复述四步法与 MSC 选取三原则，并给出中国出港示例 [citation:首都航空运价手册](https://jdair.net/micro/main/help/6436365937c5ce32acf80c49)〔中〕。含义：知识库需要一个 `interline_rule` 字段说明该航司是否采用 MSC 框架，这直接影响多航段行程的行李预算。

## 矛盾与分歧

| 争点 | 一方证据 | 另一方证据 | 对结论的影响 |
|---|---|---|---|
| 南航经济舱排距 | 香港中文页 A320(320) 列 30 英寸 | 新加坡英文页同机型列 39/36/35/33/31/30 英寸 | 不构成冲突。按机型与排位拼接：30 英寸为 152 座三舱布局的最小排距，引用应写区间而非单值 |
| 南航窄体座位数 | A320(320) 152 座 | A320(32X) 180 座 | 无冲突。三值分属不同机体与客舱方案，同栏目另列 A320(32G) 160 座，印证子变体多样。不得相减或取均值 |
| 东航经济舱手提重量 | 官网非托运行李表仅完整读到头等舱 2 件 10 公斤 | 二手源称 7 公斤；南航官网明确 5 公斤 | 经济舱手提重量标 unknown，不用跨航司值填充 |
| 厦航经济舱手提重量 | 官网《客舱行李标准提醒》（2026-07-06）写 8KG | 《旅客行李国际运输总条件》写每件不超过 5 千克 | 执行口径未裁决，标 unknown 并注明两版页面并存 |
| 深航公务舱手提重量 | 官网 Baggage Services 页与 2026-09-21 生效总条件均为 8 公斤 | 2024-01-15 公告与遗留 FAQ 页写 5 公斤 | 倾向 8 公斤为现行值，但总条件 1.1.2 款允许单独规定优先，理论上不能排除遗留口径，标 unknown 偏 8 公斤 |
| 春秋航空座椅排距 | SeatMaps 与航旅指南 28–29 英寸 | 新浪 2026-09 称 76 厘米（约 30 英寸） | 两种口径冲突。缺春秋官方客舱参数页，取区间 28–30 英寸 |
| 春秋餐食价格 | 航旅指南称预订热餐 79 元起 | 新浪称一份餐食约 40 元 | 可能分别对应预订热餐与机上现购价，均单一来源，标 unknown |
| 瑞安机场值机费 | flighttribe 称 £55 每人每航班 | express 称 £30–£55 区间；西班牙 £30、奥地利 €40 | 官方价目表被 Cloudflare 拦截未取得。入库时按「出发地法规封顶」建模，不写单值 |
| Ryanair 免费小包尺寸 | Which?、bgberlin、holidayexpert 三源一致 40×30×20 厘米、10 公斤、20 升 | carrysizer 对比表写 40×20×25 厘米 | 体积 20,000 对 24,000 立方厘米，疑为维度顺序转述不一致〔数字核查 E52：证据为 E52: Ryanair 小包 40 x 30 x 20 cm / 10 kg / 20 升；40×30×20=24,000cm³、40×20×25=20,000cm³，报告把两个体积与尺寸的对应关系完全颠倒（算术错误）〕〔数字核查 E52：证据为 E52: Ryanair 小包 40 x 30 x 20 cm / 10 kg / 20 升；按所列尺寸 40×30×20=24,000cm³、40×20×25=20,000cm³，报告把 20,000 配给三源一致的 40×30×20、24,000 配给 carrysizer 40×20×25，顺序与算术相反〕。采用三源一致的 40×30×20 厘米 |
| 中国航司排距通则 | 多篇 2026-09 聚合稿称东航/国航/南航 31–32 英寸 | 南航官网 A320(32X) 官方值 28/29 英寸 | 通则不可用。必须落到机型维度 |
| 泰狮航免费托运 | Wego 摘要称经济舱含 2 件 20 公斤 | baggagepolicies 称旧结构国内 10 公斤/国际 20 公斤，新票规 2026-07-16 起改为 Value 15–20 公斤 | 新旧票规并存，未读到官方页面确认现行版本，标 unknown |
| 美系取消免费餐范围 | 达美官方页：350 英里以下取消，约 9% 日航班量 | 同页对比表述限定为美国国内航段口径 | 长途国际主舱是否免费餐食、酒水是否收费未确认，标 unknown |

## 决策含义与行动建议

面向知识库构建方（开发者/产品方）：若采用「航司 → 单值」两级结构，则南航与东航的排距字段必然出错，三家海航的公务舱手提重量必然出现两个版本。建议把最小主键设为「承运人 × 机型 × 舱位 × 航段区域」四元组，航司级字段只保留承运类型、联盟、是否需要值机口过秤这三类跨机型恒定量。

面向工具实现方：若要在购票前给出行李预算，必须先判断该行程是否跨承运人。跨承运人且不涉北美航段时按 IATA 决议 302 的四步法取最主要承运人规则；始发或最远目的地在美加时按首个市场承运人规则判定，因为美加另有联邦与加拿大监管例外 [citation:IATA 联运行李指引](https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf)〔中〕。这条规则是国际多航段行程唯一确定的算法。

面向终端用户（通过工具间接触达）：若行程含廉航段，行李预购截止时点应作为硬提醒——春秋 1 小时、Ryanair 2 小时、泰国狮航至少 3 小时三者的现场价可达预付价的 2–10 倍〔数字核查 E34：证据为 E34: 现场购买价相对线上预购倍数 = 2 到 4 倍（2026）；台账无泰狮航 350 泰铢/公斤与「至少 3 小时」条目，2–10 倍是把亚航单一航司的 2–4 倍与未取证的泰狮航费率合并出的新区间，正文二自述亦为 2–4 倍〕〔数字核查 E34：证据为 E34: 现场购买价相对线上预购倍数 = 2 到 4 倍（2026）；上限 10 倍依赖的泰狮航 350 泰铢/公斤台账无条目，且正文二自述为 2–4 倍，此处为跨口径合并出的新区间〕。若行程为美系航司且航段短于 350 英里，不应向用户承诺免费饮品。

需要用户拍板的取舍点有三处。第一是座椅字段的精度与维护成本：官网一手（如南航）精度高但只有一家覆盖，第三方观测（SeatMaps）覆盖 200+ 航司但权威性低且方法不公开——建议以官网值优先、观测源兜底并在字段上标注来源层级，而不是二选一。第二是口碑字段是否入库：目前中国全服务航司零可交叉验证证据，Skytrax 榜单只能提供可量化的位次。取舍是「宁可留空」还是「降级为榜单位次」——本报告建议留空加 unknown。第三是存量航司的处理：Spirit 已停运，需决定是从知识库删除还是标记 `status: ceased_operations`。若工具面向历史价格基线比对，删除会丢失对照组。

还需验证的项按优先级：美航、达美、联航国际线免费托运的件数制细则，本轮只有检索摘要级线索；汉莎、法航、英航、大韩、阿联酋的国际线免费托运官方页面完全未取得；东航官网是否存在类似南航的逐机型一手间距页；国航官网机型页因脚本渲染未读到正文，不能据此断言其无间距数据；北美「前 2 件免费」的官方原文。

## 覆盖缺口与已验证盲区

已验证的盲区有三个，且都比已披露信息更有决策价值。

第一，中国全服务航司的服务口碑存在集体性数据缺失。八家航司的 Skytrax 评分、投诉率、满意度调查全部未取得，且这一缺失不是检索不力导致的偶发，而是与「航班客舱行李标准提醒、餐饮服务营销页」这类高可得内容形成鲜明对比——航司主动披露规则，不披露体验。

第二，SeatGuru 关停在知识库建设上造成的断点被低估。该站 2020 年初即停止更新、2025-10-31 整体下线，其 25 年积累的逐机型历史 pitch 数据未提供替代品。这意味着现有 AeroLOPA 与 SeatMaps 的数据新鲜度无法回溯验证，也无法评估两个替代源之间的偏差幅度——本轮未做同机型双源比对。

第三，中国民航 2026 年 7 月 1 日起实施的旅客运输新国标对随身行李尺寸与重量的量化查验要求，目前只有二手解读，缺标准原文。这直接关系到手提行李字段的可执行性。

其余缺口：吉祥与深航官网在线行李页为脚本渲染，深航经济舱手提值靠 2026-09-21 生效总条件取得；海航官网免费托运页的国内额度表格未标生效日期，只能靠 2026-01-25 发布的国内运输总条件佐证现行性；春秋航空逐机场值机截止时间表抓取超时；春秋国内线登机口第三档行李价无官方说明，官网明示登机口无法办理托运；九元、西部、中联航、乌鲁木齐航空的官方选座费价目表未取得；海航国内线预付费行李档位与时限未取得；欧美廉航的值机收费仅 Ryanair 与 Frontier 确认，Wizz 与 easyJet 未确认；美国超廉航在二线机场的运力占比无任何份额数据；IATA 决议 302 在 2021 年之后是否发生实质修订未核实，所依据文件自述 2020-06-01 生效。

## 来源附录

| # | 标题 | URL | 类型 | 抓取时间 |
|---|---|---|---|---|
| E90/E91 | 公共航空运输旅客服务管理规定（交通运输部令 2021 年第 3 号） | https://xxgk.mot.gov.cn/2020/gz/202112/W020211221393138820021.pdf | 官方 | 2026-09 |
| E1 | 国航行李运输规定 | https://www.airchina.com.cn/zh-CN/content/travel_info/preparing/conditions/contact_us/baggage_transport | 官方 | 2026-09 |
| E2 | 南航行李规定 | http://3g.csair.com/CSMBP/newMyTrip/Baggage/Baggage.html | 官方 | 2026-06-26 |
| E3 | 东航旅客须知 | https://eb.ceair.com/activity/travellernotice/app/index.html | 官方 | 2026-09 |
| E131 | 海南航空免费托运行李 | https://www.hnair.com/lvxingxinxi/xlxx/mftyxl/ | 官方 | 2026-01 |
| E132 | 海南航空乘机须知 | https://www.hnair.com/guanyuhaihang/hhdt/hhgg/cxts/cxts2024/202401/t20240124_64240.html | 官方 | 2024-01 |
| E135 | 海南航空餐食升级 | https://www.hnair.com/dachenghaihang/kongzhong/canshi/cssj/202504/t20250408_75160.html | 官方 | 2025-04 |
| E137 | 吉祥航空行李运输规定（2025-08-08 生效版） | https://meiyacommonfile.oss-cn-shenzhen.aliyuncs.com/policy/content41e1c91754449120477.pdf | 官方 | 2025-08 |
| E141/E142 | 深航旅客、行李运输总条件（2026-09-21 生效） | https://mobile.shenzhenair.com/file/internalInformation.html | 官方 | 2026-09-21 |
| E4 | 川航手提行李规定 | https://flights.sichuanair.com/baggage-service/carry-on-baggage.html | 官方 | 2026-09 |
| E5 | 厦航空舱行李标准提醒 | https://s.xiamenair.com/409b966 | 官方 | 2026-07-06 |
| E24/E25 | 中联航行李规定（第七版） | https://info.flycua.com/jcms/publish/APP/cpxz/j20230511_363_3398_9494.html | 官方 | 2020-11 |
| E122 | 南航机舱布局总页 | https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idksocbjvnb.shtml | 官方 | 2026-09 |
| E123 | 南航 A320(320) 客舱布局 | https://www.csair.com/hk/tc/tourguide/flight_service/cabin_layout/kongke/18h1tllaukv3c.shtml | 官方 | 2026-09 |
| E124 | 南航 A320(32X) 客舱布局 | https://csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/1hh7mef56t4pp.shtml | 官方 | 2026-09 |
| E125 | 南航 A321(321) 客舱布局 | https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idkvmedtkic.shtml | 官方 | 2026-09 |
| E100 | 南航 B777-300ER 客舱布局 | https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/boyin/1d8l5fmj01j95.shtml | 官方 | 2026-09 |
| E115 | 春秋航空行李价格公告 | https://news.ch.com/news/2026-06-16-00-00.html | 官方 | 2026-08-18 |
| E119 | 春秋航空手提行李升级规则 | https://flights.ch.com/baggage-rule?GAT=0 | 官方 | 2026 |
| E113 | 春秋航空选座价目表 | https://jp.ch.com/choose-seats | 官方 | 2026 |
| E118 | 春秋航空网上值机规定 | https://www.ch.com/Default/CheckInAttention | 官方 | 2026 |
| E34 | 亚航行李规定 | https://www.airasia.com/aa/inflight-comforts/zh/hk/baggage.html | 官方 | 2026-09 |
| E106/E107/E108 | Ryanair 条款与细则 | https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564 | 官方 | 2026-08-30 |
| E52/E53/E54/E55 | Which? 航空随身行李评测 | https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk | 媒体 | 2026-07-09 |
| E62 | Frontier 座位产品页 | https://www.flyfrontier.com/travel/travel-info/seating-options/?mobile=true | 官方 | 2026 |
| E83/E84 | 达美行李总览 | https://www.delta.com/us/en/baggage/overview | 官方 | 2026-09 |
| E76 | 达美机上餐饮说明 | https://www.delta.com/us/en/onboard/food-and-beverage/overview | 官方 | 2026-07 |
| E50/E51 | NPR：Spirit 停运清算 | https://www.npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds | 媒体 | 2026-05-02 |
| E85 | IATA 联运行李指引 | https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf | 官方 | 2020-06 |
| E86 | ANA 联程行李与 IATA 决议说明 | https://www.ana.co.jp/en/jp/guide/boarding-procedures/baggage/international/iata-302/ | 官方 | 2026 |
| E92 | 首都航空国际及地区航线运价手册 | https://jdair.net/micro/main/help/6436365937c5ce32acf80c49 | 官方 | 2022-07-15 |
| E72 | 国泰额外行李收费 | https://www.cathaypacific.com/cx/en_US/baggage/extra-baggage-charges/pay-cash-or-by-credit-card.html | 官方 | 2025-12 |
| E78 | 卡塔尔航空行李额度 | https://www.qatarairways.com/en-us/baggage/allowance.html | 官方 | 2026-06 |
| E74 | ANA 行李改制说明 | https://www.ana.co.jp/en/jp/promotion/renewal-2025-2026/system/ | 官方 | 2026-06 |
| E94/E95 | SeatGuru 词条 | https://en.wikipedia.org/wiki/SeatGuru | 媒体 | 2026-09-28 |
| E96/E97/E98/E99 | Australian Frequent Flyer：座位图数据源综述 | https://australianfrequentflyer.com.au/find-accurate-airline-seat-maps | 媒体 | 2026-09-11 |
| E102 | Simple Flying：经济舱排距盘点 | https://simpleflying.com/economy-seats-worlds-greatest-pitch-2026/ | 媒体 | 2026-03-18 |
| E103/E104 | Travel+Leisure 亚洲：航司腿部空间排行 | https://www.travelandleisureasia.com/hk/travel-tips/trip-planning/airlines-that-offer-the-most-and-the-least-legroom/amp | 媒体 | 2026-04-12 |
| E69 | Business Insider：Skytrax 2026 排名 | https://www.businessinsider.com/best-airlines-in-the-world-ranking-passengers-skytrax-2026-9 | 媒体 | 2026-09 |
| E70/E82 | BBC：2026 最佳经济舱航空公司 | https://www.bbc.com/travel/article/20260924-the-worlds-five-best-economy-airlines-for-2026-and-what-makes-them-so-much-better | 媒体 | 2026-09 |
| E80/E81 | 2026 航空联盟与合作伙伴指南 | https://travelvient.com/guides/airline-alliances-and-partners-2026/ | 媒体 | 2026-08 |
| E10 | 厦航加入天合联盟公告 | https://www.xiamenair.cn/zh-ph/article-detail?articleLink=/cms-i18n-ow/cms-zh-ph/contents/84904.json | 官方 | 2026-09-15 |
| E7 | 国内航司付费餐调查 | https://news.qq.com/rain/a/20260909A0C1Q000 | 媒体 | 2026-09-09 |
| E8/E9 | 解放日报：航食支出与付费餐 | https://www.jfdaily.com/wx/detail.do?id=1163861 | 媒体 | 2026-08-21 |
| E31 | 廉航 20 寸登机箱机场收费调查 | https://3g.china.com/act/news/10000169/20260528/49519016.html | 媒体 | 2026-05-28 |
| E47 | Travel Daily：2025 客户不满指数 | https://m.traveldaily.cn/article/188765/ | 媒体 | 2025-12 |
| E37/E38 | 越南民航准点率报道 | https://www.vietnam.vn/zh-cn/ty-le-bay-dung-gio-trung-binh-chi-dat-62-6 | 媒体 | 2025-08 |
| E110/E111/E112/E121 | Ryanair 行李费用指南 | https://flighttribe.co.uk/ryanair-baggage-allowance/ | 社区 | 2026-09-01 |
| E45 | Thai Lion Air 行李政策 | https://baggagepolicies.com/thai-lion-air-baggage-policy/ | 社区 | 2026-09 |
| E35/E36 | VietJet 行李政策 | https://www.cabinzero.com/blogs/air-travel-tips/vietjet-air-baggage-allowance | 社区 | 2026-06 |
| E40/E41/E42 | 宿务太平洋航司指南 | https://airports.guide/airlines/5J | 社区 | 2026-08 |
| E44 | Scoot 行李规定 | https://travellote.com/baggage/scoot/ | 社区 | 2026-06 |
| E56/E57/E60 | UpgradedPoints：Frontier 评测 | https://upgradedpoints.com/travel/airlines/frontier-airlines-review/ | 媒体 | 2026-06-10 |
| E58 | Frontier A321neo 选座指南 | https://seatcompare.ai/insights/frontier-airlines-a321neo-seat-selection-guide-2026 | 社区 | 2026-07-23 |
| E59/E61 | Thrifty Traveler：Frontier 评测 | https://thriftytraveler.com/reviews/flights/frontier-airlines/ | 媒体 | 2025-08-31 |
| E71 | UpgradedPoints：新航行李 | https://upgradedpoints.com/travel/airlines/singapore-airlines-baggage-fees/ | 媒体 | 2026-06 |
| E73 | Executive Traveller：泰航行李新规 | https://www.executivetraveller.com/news/thai-airways-new-luggage-allowance | 媒体 | 2026-02 |
| E127 | SeatMaps：东航 737-800 | https://seatmaps.com/zh-CN/airlines/mu-china-eastern/boeing-737-800 | 社区 | 2026-09 |
| E128 | SeatMaps：国航 A320 | https://seatmaps.com/zh-CN/airlines/ca-air-china/airbus-a320 | 社区 | 2026-09 |

## 方法论附注

研究模式为深度档，12 个子问题全部完成，3 轮研究，末轮 2 个子问题因预算耗尽未覆盖（美系与欧亚头部航司国际线免费托运细则、五家中国航司窄体机排距）。检索策略一句话：优先用「航司官网域名 + 具体机型代码/条款名」定位一手页面，对脚本渲染页面改用 PDF 版运输条件或地区镜像页，仍不可得时降级到座位图观测平台并标注来源层级。

## 来源存疑项（审查员判定，本轮未自动修复）

以下来源/引文被对抗性审查判定为存疑，且无法自动修正（需人工复核或定向补研）：

- [high] 报告用 delta.com 机上餐饮页作为「美航 250 英里以上提供免费零食」「联航 300 英里以上提供免费小吃」的唯一引文并标〔高〕。抓取该页正文确认其为达美自有产品页，全文不含美航/联航字样，也不含 250/300 英里两个门槛。引文类型与结论类型根本不匹配。 → 删除该引文对美航/联航的支撑；分别改用 aaa.com 与 united.com 各自的 baggage 官方页取证。
- [high] 「SeatGuru 其数据在 2020 年初即停止更新」是对维基原文的引文扭曲：原文为「2020 年起 app 从 App Store / Google Play 下架，博客于 2020 年 3 月停更」，属产品渠道信息，与「座位图数据停止更新」无关。报告据此虚构前提，又推出「25 年历史 pitch 数据未提供替代品」「AeroLOPA 与 SeatMaps 新鲜度无法回溯验证」等整段论证，而维基实际明确列出了 6 个替代站。 → 将表述改为「app 与博客于 2020 年停更」；删除「座位图数据未更新」及其衍生推论；将该条从「已验证盲区」降级为待验证项。
- [medium] 「吉祥 2023 年 10 月版曾为 10 公斤」在所引 PDF 中无依据：该文件第 6 节自述废止的是「2025 年 1 月 13 日公布施行的《行李运输规定》」，与 2023 年 10 月无关，时间线亦冲突。 → 删除该历史断言，或另取 2023 年版 PDF 原文核对后再写。


---

## 附录：原始证据状态

# 航空公司规则与体验知识调研：中国国内航司 + 全球头部航司的行李政策、餐食、座椅、收费项与服务口碑 — 深度研究中间结果（证据状态）

> 子问题 12 个，完成 12 个，研究轮次 3 轮。

研究答案空间：航空公司规则与体验知识调研：中国国内航司 + 全球头部航司的行李政策、餐食、座椅、收费项与服务口碑（用户直传问题清单，无独立 scope 声明）
覆盖维度：（未声明）

## 中国全服务航司（国航CA/东航MU/南航CZ/海航HU/川航3U/厦航MF/深航ZH/吉祥HO）：国内线经济舱免费托运重量、手提行李重量与尺寸、免费餐食政策、经济舱座椅间距、联盟归属、服务特色口碑（如川航餐食、厦航服务）

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 国航（CA）国内航线执行计重制托运行李规则，经济舱旅客免费托运行李 20 千克，公务舱 30 千克、头等舱 40 千克；每件行李长宽高不得超过 100×60×40 厘米。（E1 · 置信度：中 · 类型：官方，来源：https://www.airchina.com.cn/zh-CN/content/travel_info/preparing/conditions/contact_us/baggage_transport）
- 南航（CZ）国内线经济舱免费托运行李 20 公斤（头等舱 40 公斤、公务舱 30 公斤、婴儿票 10 公斤）；手提行李每位旅客限 1 件，长宽高之和不超过 115 厘米、重量不超过 5 千克，逾重费按经济舱普通票价 1.5%/公斤计收。（E2 · 置信度：中 · 类型：官方 · 时点：2026-06-26，来源：http://3g.csair.com/CSMBP/newMyTrip/Baggage/Baggage.html）
  - 数字：南航国内线经济舱免费托运行李额 = 20公斤；南航国内线手提行李单件重量上限 = 5千克；南航手提行李三边之和上限 = 115厘米；南航逾重行李费率 = 每公斤按经济舱普通票价的1.5%计算
- 东航（MU）自营国内航班免费托运为计重制：经济舱 20 公斤、公务舱 30 公斤、头等舱 40 公斤，单件不超过 50 千克、体积不超过 40×60×100 厘米；非托运行李经济舱限 1 件，头等舱 2 件 10 公斤，体积 A≤55/B≤40/C≤20 厘米。（E3 · 置信度：中 · 类型：官方，来源：https://eb.ceair.com/activity/travellernotice/app/index.html）
  - 数字：东航国内线经济舱免费托运行李额 = W ≤20KG(44磅)；东航国内线头等舱非托运行李 = 2件 10KG(22磅)；东航国内线托运行李单件最大重量 = 50千克
- 川航（3U）官网现行规定：每件手提行李三边分别不超过 20×40×55 厘米且重量不超过 8 公斤；经济舱旅客国内及国际/地区航班每人限 1 件手提行李，公务舱可带 2 件；超免费行李额度须付逾重行李费。国内运输托运行李每件不超过 50kg、体积不超过 40×60×100 厘米。（E4 · 置信度：中 · 类型：官方，来源：https://flights.sichuanair.com/baggage-service/carry-on-baggage.html）
  - 数字：川航手提行李单件重量上限 = 8公斤；川航手提行李三边尺寸上限 = 20×40×55厘米；川航经济舱手提行李件数 = 每人1件
- 厦航（MF）2026年7月官方提醒：厦航航班经济舱旅客限带 1 件、头等舱/商务舱旅客限带 2 件随身行李，单件均不超过 8KG，三边分别不得超过 55/40/20 厘米。（E5 · 置信度：中 · 类型：官方 · 时点：2026-07-06，来源：https://s.xiamenair.com/409b966）
  - 数字：厦航经济舱随身行李单件重量上限 = 8KG（17磅）；厦航随身行李三边尺寸上限 = 55厘米/40厘米/20厘米
- 厦航《旅客、行李运输总条件》规定国内航班免费行李额：经济舱 20 千克、公务舱 30 千克、头等舱 40 千克，按儿童适用票价购票者与成人相同。（E6 · 置信度：中 · 类型：官方，来源：https://www.xiamenair.com/tw-mo/article-detail?articleLink=/cms-i18n-ow/cms-tw-mo/channels/2892.json）
  - 数字：厦航国内线经济舱免费行李额 = 20千克
- 截至2026年9月，中国航司经济舱免费餐食并未取消：东航、川航、祥鹏航空客服均确认免费餐食继续提供，同时以增值服务方式推出付费定制餐；付费餐价格区间从19元到344元不等。（E7 · 置信度：中 · 类型：媒体 · 时点：2026-09-09，来源：https://news.qq.com/rain/a/20260909A0C1Q000）
  - 数字：国内航司付费飞机餐价格区间 = 19元至344元（2026年8月-9月）
- 付费餐具体案例：东航2026年4月在部分西安出港航班推出19–45元付费轻食；国航付费餐迭代后推出344元海鲜鱼子酱高端拼盘（234元鳕鱼煲仔饭不再是最高价）；川航在App上线58元冒菜等付费餐。祥鹏航空付费餐统一40元/份、覆盖国内大部分航线。（E8 · 置信度：中 · 类型：媒体 · 时点：2026-08-21，来源：https://www.jfdaily.com/wx/detail.do?id=1163861）
  - 数字：国航高端付费餐最高价 = 344元（2026年8月）；东航西安出港付费轻食价格区间 = 19元至45元（2026年4月起）；祥鹏航空付费餐统一售价 = 40元/份（2026年8月）
- 三大航 2025 年航食相关支出仍双位数增长（国航 45.05 亿元 +8.15%、东航 46.31 亿元 +9.56%、南航 48.71 亿元 +10.55%），说明免费餐食基本盘未被削减、投入仍在加码。（E9 · 置信度：中 · 类型：媒体 · 时点：2026-08-21，来源：https://www.jfdaily.com/wx/detail.do?id=1163861）
  - 数字：2025年国航航食相关支出 = 45.05亿元（同比+8.15%）（2025年度）；2025年东航航食相关支出 = 46.31亿元（同比+9.56%）（2025年度）；2025年南航航食相关支出 = 48.71亿元（同比+10.55%）（2025年度）
- 联盟归属（已核实部分）：厦航、东航、南航同属天合联盟（SkyTeam），厦航于2012年11月21日加入、为天合第19位成员，至2026年8月仍为正式成员；国航与深航属星空联盟（Star Alliance）中国成员。（E10 · 置信度：中 · 类型：官方 · 时点：2026-09-15，来源：https://www.xiamenair.cn/zh-ph/article-detail?articleLink=/cms-i18n-ow/cms-zh-ph/contents/84904.json）
- 中国全服务航司（国航、南航、东航、海航、川航、厦航等）经济舱旅客可免费携带一件随身行李，常见尺寸上限 55×40×20 厘米（适配 20 英寸登机箱），重量上限区间为 5–8 公斤；低成本航司免费随身行李标准明显更严。（E11 · 置信度：中 · 类型：媒体 · 时点：2026-06-26，来源：https://www.sohu.com/a/1041518878_122723956）
### 不确定项
- 东航（MU）国内线经济舱手提行李的单件重量上限究竟是 5kg、7kg 还是 8kg（原因：东航官网《旅客须知》非托运行李表格在抓取中丢失了公务舱/经济舱对应的重量数值列，只完整读到头等舱 2 件 10KG；其他来源给出的"7kg"说法（news.china.com.cn 2026-05，疑为"重量≤7kg"）与南航官网明确的 5kg 相互冲突，无法判定。）
- 厦航（MF）经济舱手提行李是 5kg 还是 8kg（原因：官网《客舱行李标准提醒》（2026-07-06）与《行李运输规定》《旅客行李国际运输总条件》（2026年1月起）互相矛盾：前者写 8KG，后者写"每件随身携带物品的重量不得超过5千克(11磅)"。可能是近期扩容仅针对特定航班，也可能是两套页面未同步。）
- 海航（HU）、吉祥航空（HO）、深航（ZH）的国内线经济舱免费托运与手提行李具体数值（原因：深航官网《随身行李》页与吉祥航空官网 baggage 页抓取只返回导航/隐私政策占位内容（JS 渲染），未取到正文；海航未检索到官方行李页。本轮只有一条 2021 年三门峡市政府转载的旧文提到厦航/海航/吉祥经济舱免费 20KG 且客舱尺寸 20×40×55cm，时点过旧不可作现行结论。）
- 海航（HU）是否仍为天合联盟成员、川航（3U）与吉祥（HO）是否为星空联盟成员（原因：本轮检索命中的联盟类结果集中于厦航/东航/南航（天合）与国航/深航（星盟），未取得海航与川航、吉祥的官方或权威来源佐证，不作确认。）
- "川航餐食好、厦航服务好"这类服务口碑的量化证据（原因：本轮只取得航班客舱行李标准提醒、餐饮服务营销页与旅客主观反馈片段，未找到可交叉验证的服务质量评价（Skytrax 评分、投诉率、满意度调查等）；新浪旅游稿"首选海航、川航、厦航——服务好，餐食丰富"属 UGC 性质，不足以作为口碑结论。）
### 信息缺口（优先级）
- 国内线经济舱座椅间距（seat pitch）：八家航司 A320/737/A321 窄体机经济舱 76–80cm 级别的逐机型数据完全缺失，无任何一手或二手可引用来源（优先级：高）
- 海航（HU）国内线免费托运额度、手提行李重量与尺寸、免费餐食政策的官方现行条款（优先级：高）
- 吉祥航空（HO）国内线免费托运与手提行李官方条款（官网页面为 JS 渲染，需换 URL 形态或 PDF 版《行李运输规定》）（优先级：高）
- 深航（ZH）国内线随身行李官方重量/尺寸数值（官网页面抓取失败）（优先级：高）
- 免费餐食的"含餐/不含餐"运价结构：哪些国内航线票面含餐、哪些不含，以及经济舱正餐 vs 点心的实际供给差异（优先级：中）
- 2026 年各航司"付费选餐"的统一规则（哪些航段支持、价格区间、是否替代免费餐）——上观报道已指出航段支持标注不清，但缺官方规则文本（优先级：中）
- 川航/厦航等地方全服务航司的量化服务口碑（第三方评测或行业调查）（优先级：中）
- 2026年7月1日起实施的民航旅客运输新国标对随身行李尺寸/重量查验的具体量化要求（目前只拿到二手解读，缺标准原文）（优先级：中）

---

## 中国低成本航司（春秋9C/九元AQ/西部PN/中联航KN/乌鲁木齐航空UQ）：免费手提重量与尺寸限制（含严查程度）、托运是否全额收费及典型价格、餐食与选座收费、经济舱座椅间距、特殊限制条款、从全服务转型廉航的背景

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 春秋航空免费手提行李为1件、重量不超过7公斤、尺寸不超过20×30×40厘米（不含轮），且在安检、值机、登机口被严格查验，登机口发现超规将收费；其2026年3月版《旅客和行李运输总条件》为依据。（E12 · 置信度：中 · 类型：媒体 · 时点：2026-06，来源：https://ql1d.com/general/27786956.html）
  - 数字：免费手提行李重量上限 = 7公斤（2026）；免费手提行李尺寸上限 = 20×30×40厘米（2026）
- 春秋航空手提行李可在小程序线上付费159元升级至20×40×55厘米/10kg（第三方指南口径为国内160元、国际220元），升级后仍超规则需再付费托运。（E13 · 置信度：中 · 类型：媒体 · 时点：2026-06，来源：https://ql1d.com/general/27786956.html）
  - 数字：手提行李升级费（春秋小程序线上） = 159元（2026）；手提行李升级费（航空指南口径） = CNY 160 domestic / CNY 220 international（2025-01）
- 春秋航空基础票价不含免费托运额，行李额需提前线上购买（登机前1小时截止），逾期按机场/登机口价收取：登机口国内约300元/件、国际约500元/件；2023年抽查显示柜台区间定价约10kg以下300元/件、10kg以上500元/件；手提7-10kg超重亦有加收300元的案例。（E14 · 置信度：中 · 类型：媒体 · 时点：2025-01，来源：https://airports.guide/airlines/9C）
  - 数字：登机口超规行李费（国内） = CNY 300/piece（2025-01）；柜台托运费（10kg以下） = 300元一件（2023-09）；手提超重加收（7-10kg） = 300元（2026-06）
- 春秋航空A320为全经济舱高密度布局，运营180座与186座两个版本，座椅间距约28-29英寸（SeatMaps口径），媒体口径约76厘米（约30英寸）、靠背调节角度仅约10度、座椅倾斜角度固定。（E15 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://seatmaps.com/zh-CN/airlines/9c-spring-airlines/airbus-a320）
  - 数字：经济舱座椅间距（SeatMaps口径） = 28至29英寸（2026）；A320高密度布局座位数 = 186个（2026）；座椅间距（新浪媒体口径） = 76厘米（2026-09）
- 春秋航空选座收费，普通排约40元起、前部排约60元起、安全出口排（间距32英寸）约100元起、前排1-2排约120元起（第三方指南2025年1月价目）。（E16 · 置信度：中 · 类型：媒体 · 时点：2025-01，来源：https://airports.guide/airlines/9C）
  - 数字：安全出口排选座费 = From CNY 100（2025-01）
- 春秋航空标准票价不含免费餐食，机上餐食需付费（预订热餐约79元起、零食面食20-50元、饮品10-30元，指南口径），媒体实测口径一份餐食约40元；裸票之外餐食、选座、行李全部另算。（E17 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://airports.guide/airlines/9C）
  - 数字：预订热餐价格 = From CNY 79（2025-01）
- 九元航空为廉航（均瑶集团旗下、基地广州白云），免费手提仅1件7kg（普通舱20×30×40cm，高端经济舱放宽至20×40×55cm），柜台/登机口经常称重、超规必须托运，特价舱位无免费托运行李。（E18 · 置信度：中 · 类型：媒体 · 时点：2026-03，来源：https://www.flyingstate.com/3560.html）
  - 数字：免费手提行李重量 = 7公斤（2026-03）
- 九元航空737-800采用单一全经济舱高密度布局，共189座（与春秋180/186座同为国内高密度水平）。（E19 · 置信度：中 · 类型：媒体 · 时点：2026-04，来源：https://seatmaps.com/zh-CN/airlines/aq-9-air/boeing-737-800）
  - 数字：737-800布局座位数 = 189个座位（2026-04）
- 西部航空普通经济舱免费手提1件、不超过7公斤、20×30×40厘米；登机口具备称重条件按实际重量收费转入货舱，无称重条件按300元/件收费，时间紧急可花200元购买“上机权益”放宽至20×40×55厘米进入客舱——该规则曾因登机前临时收费200元被律师起诉。（E20 · 置信度：中 · 类型：媒体 · 时点：2026-03，来源：https://www.yibinrm.cn/cms/a/128636834/content）
  - 数字：登机口无称重条件收费 = 每件300元（2026-03）；上机权益购买价 = 200元（2026-03）
- 西部航空2007年由海航集团与重庆各方筹建成立（初为全服务定位），2010年3月启动“两单两高”（单一机型、单一客舱全经济舱，高利用率高客座率）低成本战略研究，2013年6月正式宣布由全服务转型低成本，是国内第一家由全服务转型低成本的航司。（E21 · 置信度：高 · 类型：媒体 · 时点：2018-07，来源：http://hy.stock.cnfol.com/bankuaijujiao/20171127/25676322.shtml）
- 西部航空成立背景：2007年在海航集团及重庆各方筹建下经民航局批准成立，2007年6月14日完成重庆—海口首航，转型后以“裸票价+个性定制”模式把行李、餐食从票价中剥离单独收费。（E22 · 置信度：中 · 类型：媒体 · 时点：2017-11，来源：http://hy.stock.cnfol.com/bankuaijujiao/20171127/25676322.shtml）
- 西部航空通过高密度客舱布局提高承运效率，A320机型布局已达186座、A319达144座（2017年数据）。（E23 · 置信度：中 · 类型：媒体 · 时点：2017-11，来源：http://hy.stock.cnfol.com/bankuaijujiao/20171127/25676322.shtml）
  - 数字：A320布局座位数 = 186人（2017）；A319布局座位数 = 144人（2017）
- 中联航官方行李规则（2020年11月13日生效第七版）：J/C/W/Y/M/E/H/K/L/N/R/S/V/D/T舱可免费手提1件、不超10千克、20×40×55厘米（2020年7月由20×30×40放宽而来）；特价I/Z/U舱无免费手提额、可购付费手提100元/件；托运实行计件制。（E24 · 置信度：高 · 类型：官方 · 时点：2020-11，来源：https://info.flycua.com/jcms/publish/APP/cpxz/j20230511_363_3398_9494.html）
  - 数字：免费手提行李重量 = 10千克（2020-11）；免费手提行李尺寸 = 20×40×55厘米（2020-11）
- 中联航特殊限制条款：免费手提限“软包”（双肩包、斜挎包、手拎包等，不含带拉杆或轮子的行李箱）；托运计件制每件23公斤（国内首家执行计件制的国有航司）；特价舱（S/V/D/T及I/Z）免费托运额为0；付费托运23kg首件约100元（≤800km）/180元（801-2000km）/260元（≥2001km）。（E25 · 置信度：中 · 类型：官方 · 时点：2020-11，来源：https://info.flycua.com/jcms/publish/APP/cpxz/j20230511_363_3398_9494.html）
  - 数字：计件制托运单件重量 = 23公斤（2020-07）
- 中联航737-800为186座全经济舱布局（含约168个普通经济舱座位），座椅间距30-31英寸、座椅宽度约17英寸、可调角度约3度——间距明显宽于春秋的28-29英寸。（E26 · 置信度：中 · 类型：媒体 · 时点：2017-01，来源：https://seatmaps.com/zh-CN/airlines/kn-china-united-airlines/boeing-737-800）
  - 数字：737-800布局座位数 = 186个座位（2017-01）；经济舱座椅间距 = 30至31英寸（2026）
- 乌鲁木齐航空由海南航空与乌鲁木齐城市建设投资有限公司（乌鲁木齐市政府）共同出资组建，2013年11月获批筹建，2014年8月28日获民航新疆管理局运行合格证、8月29日首飞伊宁正式运营，以低成本航空为主导经营模式，是新疆唯一本土航司；2021年12月8日经营管理实际控制权移交辽宁方大集团。（E27 · 置信度：高 · 类型：官方 · 时点：2014-09，来源：https://urumqi-air.com/micro/main/aboutus/641159f50c682c7801e5a149）
- 乌鲁木齐航空被机场公示列入差异化（低成本）航司：经济舱单件免费手提限20×30×40厘米、7公斤，仅公务舱可免费携带20×40×55厘米（20英寸）行李箱——与西部、祥鹏、天津、首都、北部湾、长安等同一标准。（E28 · 置信度：中 · 类型：媒体 · 时点：2026-05，来源：https://3g.china.com/act/news/10000169/20260528/49519016.html）
  - 数字：经济舱手提重量限制 = 7公斤（2026-05）；经济舱手提体积限制 = 20厘米×30厘米×40厘米（2026-05）
- 中联航（东航旗下、前身为部队企业的央企子公司）于2014年高调宣布由全服务转型低成本航空，与西部航空转型同处一波廉航浪潮；当时民航局年初已印发《关于促进低成本航空发展的指导意见》，国内运营成熟的廉航仅春秋一家、中国低成本市场份额不足7%。（E29 · 置信度：中 · 类型：媒体 · 时点：2014-07，来源：https://www.rmzxw.com.cn/c/2014-07-08/348811_1.shtml?n2m=1）
- 九元航空背景：吉祥航空母集团均瑶集团投资建立的新航司，2014年获民航局筹建批准，基地广州，签下50架波音737订单，定位纯廉航（与全服务的吉祥形成集团内双品牌）。（E30 · 置信度：中 · 类型：媒体 · 时点：2014-07，来源：https://www.rmzxw.com.cn/c/2014-07-08/348811_1.shtml?n2m=1）
- 严查程度（2026年行业面）：多地机场发生20英寸登机箱在登机口被拦、被迫支付100元至300元托运费的事件；多数低成本航司普通经济舱已禁止免费携带20寸箱，春秋、祥鹏等仅允许14寸以内登机箱免费入舱，部分航司允许付费携20寸箱上机。（E31 · 置信度：中 · 类型：媒体 · 时点：2026-06，来源：https://3g.china.com/act/news/10000169/20260528/49519016.html）
  - 数字：登机口拦截收费区间 = 100元至300元（2026-05）
- 严查执行具现场裁量权：春秋客服明确超重超尺寸“以当日现场值班工作人员判定为准”；典型案例如旅客乘西部航空航班在登机前约20分钟被拦、当场扫码支付200元，由此引发对告知义务的诉讼。（E32 · 置信度：中 · 类型：媒体 · 时点：2026-06，来源：https://ql1d.com/general/27786956.html）
  - 数字：涉诉行李收费金额 = 200元（2026-03）
- 春秋航空通过单设经济舱、缩小座椅间隙使每架飞机座位数较传统布局提高15%～20%，配合单一A320机队（节省约3%租赁采购及维修费用）构成降本核心；2023年抽查的10家廉航中仅吉祥登机箱尺寸大于14寸。（E33 · 置信度：中 · 类型：媒体 · 时点：2023-09，来源：https://www.thepaper.cn/newsDetail_forward_24653031）
  - 数字：每架座位数较传统布局提高 = 15%～20%（2023-09）
### 不确定项
- 春秋航空座椅间距口径存在张力：SeatMaps与航空指南为28-29英寸（71-74cm），新浪2026年9月媒体文称76厘米（约30英寸）（原因：两个C级来源数字冲突，可能因机型批次/测量口径不同，未能获得春秋官方客舱参数页）
- 春秋餐食价格口径冲突：航空指南称预订热餐79元起，新浪媒体文称一份餐食约40元（原因：可能分别对应预订热餐与简餐/机上现购价，均为单一C级来源）
- 九元航空免费手提尺寸：flyingstate页面自身矛盾（摘要写20×40×55cm，正文表格写普通舱20×30×40cm、高端经济舱20×40×55cm）（原因：单一D级博客源且内部不一致，仅红星新闻'多数廉航20×30×40'间接佐证，缺九元官网条款页直接确认）
- 西部航空186座/A319 144座布局为2017年数据，现机队含A321等机型后实际布局可能已变化（原因：唯一来源时点为2017-11，未找到2024年后更新数据）
- 九元航空退改细则（无行李特惠不可退改、改签扣5%-30%分档）（原因：仅flyingstate单一D级来源，无第二来源交叉验证）
- 春秋航空成立年份口径：航空指南称Founded in 2005，通行说法为2004年获准、2005年首航（原因：未专项核实公司注册与首航时间，属背景性细节）
### 信息缺口（优先级）
- 乌鲁木齐航空与中联航的官方餐食收费与选座费价格表（仅获春秋价格带）（优先级：中）
- 乌鲁木齐航空经济舱座椅间距/座位数（仅有其手提行李政策）（优先级：中）
- 西部航空、九元航空2025-2026现行官方托运行李价格表官方数字（优先级：中）
- 九元航空确切首航日期与开业时间线（仅确认2014年获筹建批准）（优先级：低）
- 中联航2014年转型的准确公告日期（仅2014-07-08报道佐证）（优先级：低）
- 各航司服务口碑与投诉量数据——属其他并行子问题范围，未展开（优先级：低）

---

## 东南亚低成本（亚航AK/亚航X D7/越捷VJ/酷航TR/捷星3K/宿务5J/泰狮SL）：手提7kg执法严格度、托运收费模式、餐食与选座收费、机上销售、座位间距、口碑典型问题

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 亚航（AK/FD）基础票价仅含2件合计7kg手提行李（56×36×23cm+小包40×30×10cm），无免费托运额；行李现场（柜台/登机口）购买价格约为线上预购的2-4倍，且在DMK、KLIA2等枢纽严格称重、登机口抽检。（E34 · 置信度：高 · 类型：官方 · 时点：2026-09，来源：https://www.airasia.com/aa/inflight-comforts/zh/hk/baggage.html）
  - 数字：手提行李限重（2件合计） = 7 公斤（现行）；现场购买价相对线上预购倍数 = 2 到 4 倍（2026）
- 越捷Eco/Deluxe档手提行李与个人物品合计限7kg（超规在值机被称重、登机口可能被拉出强制托运，且未贴越捷标签的手提袋不得登机）；SkyBoss档升至10-14kg（按航线），SkyBoss Business/商务最高18kg。（E35 · 置信度：中 · 类型：博客 · 时点：2026-06，来源：https://www.cabinzero.com/blogs/air-travel-tips/vietjet-air-baggage-allowance）
  - 数字：Eco档手提合计限重 = 7 kg（2026）；SkyBoss档手提额度（flyfono口径） = 10 kg（2026）
- 越捷托运收费随时点递增：预订时预购最便宜（20kg国内20万VND、东南亚48万VND），机场柜台/起飞前3小时内最贵（国内超重约4万VND/kg），国际航线若在登机口而非值机处理托运另收500,000 VND登机口处理费。（E36 · 置信度：中 · 类型：博客 · 时点：2026-06，来源：https://www.cabinzero.com/blogs/air-travel-tips/vietjet-air-baggage-allowance）
  - 数字：国际航线登机口处理托运附加费 = 500,000 VND（2026）
- 越南民航业2025年上半年平均准点率仅62.6%，同比下滑13.1个百分点（越南民航局数据，SGGP报道）；内排机场延误中93.8%由航司自身运营问题造成。（E37 · 置信度：中 · 类型：媒体 · 时点：2025-08，来源：https://www.vietnam.vn/zh-cn/ty-le-bay-dung-gio-trung-binh-chi-dat-62-6）
  - 数字：越南航空业平均准点率 = 62.6%（2025年上半年）；准点率同比降幅 = 13.1个百分点（2025年上半年 vs 2024年同期）
- 越捷航空2025年上半年准点率为67.7%，低于越南航空（71%）和竹子航空（81%），在越南主要航司中处于最低梯队。（E38 · 置信度：中 · 类型：媒体 · 时点：2025-08，来源：https://www.vietnam.vn/zh-cn/ty-le-bay-dung-gio-trung-binh-chi-dat-62-6）
  - 数字：越捷航空准点率 = 67.7%（2025年上半年）；越南航空准点率（对照） = 71%（2025年上半年）
- 亚航Santan机上餐食为纯付费模式，2024年推出Value Combo（热食+饮品）：Light RM10（亚航X D7为RM19）、Classic RM19（D7 RM29）、Jumbo RM23（D7 RM32），比单点省至多RM7；预订更便宜且机上优先送餐；咖啡RM6起。（E39 · 置信度：中 · 类型：博客 · 时点：2024-07，来源：https://economytraveller.com/airasia-adds-new-santan-value-combo-meals-from-rm10/）
  - 数字：Light Combo价格（含饮品，AK） = RM10（2024）；Light Combo价格（含饮品，AirAsia X） = RM19（2024）
- 宿务太平洋（5J）GO Basic票价不含任何托运行李，GO Easy/GO Flexi含1件20kg；线上预付20kg约PHP 770（国内）/PHP 1,500（短程国际）/PHP 2,500（长程国际），机场超重费国内PHP 200/kg、长程PHP 800/kg，越临飞越贵。（E40 · 置信度：中 · 类型：博客 · 时点：2026-08，来源：https://airports.guide/airlines/5J）
  - 数字：20kg预付托运（国内） = PHP 770 (~$14)（2025-2026）；20kg预付托运（短程国际） = PHP 1,500 (~$27)（2025-2026）；20kg预付托运（长程国际） = PHP 2,500 (~$45)（2025-2026）
- 宿务太平洋对7kg手提（1件56×36×23cm+1件个人物品）在值机柜台和登机口双重称重量尺寸，严格执行；超限按机场费率收取逾重行李费。（E41 · 置信度：中 · 类型：博客 · 时点：2025，来源：https://airports.guide/airlines/5J）
- 宿务A320/A321经济舱座椅间距仅28-29英寸（3-3布局，宽17英寸，约3英寸后仰，多数无电源），A330neo高密度3-3-3布局459座、间距30英寸；选座三档：标准PHP 199-399、Standard Plus（前排/安全门）PHP 499-799、Premium PHP 899起。（E42 · 置信度：中 · 类型：博客 · 时点：2025，来源：https://airports.guide/airlines/5J）
  - 数字：A320/A321经济舱座椅间距 = 28-29" (71-74cm)（2025）
- 捷星Starter档手提为2件合计7kg（澳新国内线例外为14kg），值机/登机口测量称重并挂标签，属区域内最严格之列；+7kg加购AUD 60起；托运15-40kg按档预购，机场购首15kg在3K国际线约SGD 65；已宣布自2027年2月2日起取消7kg重量制、改为按件计尺寸（免费座椅下包40×30×20cm，付费Priority Carry-on约$25起含56×36×23cm大件+优先登机）。（E43 · 置信度：中 · 类型：博客 · 时点：2026-08，来源：https://www.cabinzero.com/blogs/air-travel-tips/jetstar-airlines-baggage-allowance-policy）
  - 数字：手提规则改为按尺寸计的生效日 = 2027-02-02（2026-08宣布）
- 酷航（TR）经济舱手提为10kg合计（1件54×38×23cm+1件个人物品40×30×10cm），页面标注为"enforced"（强制执行）；基础Fly票无免费托运，FlyBag/FlyBagEat含20kg，预购档位20/25/30/35/40kg按航线定价。（E44 · 置信度：中 · 类型：博客 · 时点：2026-06，来源：https://travellote.com/baggage/scoot/）
  - 数字：经济舱手提合计限重 = 10 kg（2026-06核验）
- 泰狮航（SL）所有票档均含7kg手提（56×36×23cm）；托运按票档：Lion Saver为0、Lion Value国内15kg/国际20kg、Lion Flexi 25-30kg（新票规自2026-07-16起适用）；预付与柜台价差极大：国内20kg预付仅660 THB，柜台按350 THB/kg计（同重量约为预付十倍以上），预付需在起飞前至少3小时购买。（E45 · 置信度：中 · 类型：博客 · 时点：2026-09，来源：https://baggagepolicies.com/thai-lion-air-baggage-policy/）
  - 数字：国内航线20kg额外预付费 = 660 THB（2026）
- 区域LCC座椅间距对比：亚航A320/A321经济舱29英寸（座宽17.8英寸，Hot Seats 34英寸，D7 A330 Premium Flatbed 59英寸）；越捷28-29英寸（座宽17.5英寸，SkyBoss前排31英寸）；均无椅背娱乐屏。（E46 · 置信度：中 · 类型：博客 · 时点：2026-08，来源：https://flyfono.com/airasia-vs-vietjet-which-is-better-2/）
  - 数字：亚航经济舱座椅间距 = 29-inch（2026-08）；亚航经济舱座宽 = 17.8-inch（2026-08）
- 在Click Intelligence 2025年"客户不满指数"（综合乘客评价/Skytrax星级/投诉搜索量/安全运营事件）全球排名中，亚航以不满指数50列全球第6（前十唯一东南亚航司），主要抱怨为航班延误严重和行李政策复杂。（E47 · 置信度：中 · 类型：媒体 · 时点：2025-12，来源：https://m.traveldaily.cn/article/188765/）
  - 数字：客户不满指数 = 50（2025）；全球排名 = 第六（2025）
- 所涉东南亚LCC均为"无免费餐食+机上付费购买/销售"模式：越捷全员buy-on-board菜单（预购热食约省30-40%），宿务CEB Fun Cafe机上售卖（热食PHP 320起、小吃PHP 120起、饮品PHP 80起），亚航Santan预订combo更省且优先送餐——预购均比机上现买便宜。（E48 · 置信度：中 · 类型：博客 · 时点：2026-08，来源：https://valuair.com.sg/advice/vietjet-add-ons-worth）
- 越捷选座/餐食/优先登机均收费：标准选座约S$3-8、安全门/前排加长腿位约S$12-25/段，Eco不付费则值机时随机派位（多为后排中间）；Deluxe票档含20kg托运+餐食+标准选座+优先登机，较单买add-on略省。（E49 · 置信度：中 · 类型：博客 · 时点：2026-08，来源：https://valuair.com.sg/advice/vietjet-add-ons-worth）
### 不确定项
- 小红书笔记称亚航"2026新规"可线上预购随身超额服务将总重提至10kg（机场柜台不可购），与亚航官方页面Xtra Carry-On/Fast Pass加购7kg（合计14kg）的结构存在出入，未能从官方渠道核实是新品还是误述（原因：单一UGC来源与官方页面口径冲突，无法交叉验证）
- valuair.com.sg系列文章疑似含AI生成文本且自相矛盾（如称酷航基础票不含头顶行李箱额度、与travellote及酷航10kg含手提规则冲突；宿务个人物品尺寸前后不一），其全部价格区间只能视为指示性参考（原因：来源内部逻辑矛盾明显，可靠性降级为C/D）
- flyfono给出的准点率对比（亚航82% vs 越捷76%）未注明数据来源与统计期间，与越南民航局67.7%等官方口径不可直接比较（原因：无出处的方法不透明数据，仅作方向性参考）
- 越捷/亚航在Tripadvisor（越捷7,948条点评含"史上最烂"等极端差评）和黑猫投诉上存在大量延误、取消与退款纠纷个案，但除不满指数排名外缺少系统性投诉量统计（原因：UGC个案证据，无法量化到可靠结论）
- 泰狮航免费托运口径存在新旧票规张力：Wego搜索摘要称经济舱含2件20kg托运，baggagepolicies则称旧结构为国内10kg/国际20kg、且新票规自2026-07-16起才改为Value 15-20kg/Flexi 25-30kg（原因：不同时点的票规并存，未读到官方页面确认现行适用版本）
- 越界信息一笔（属其他子问题，未展开）：越南航空/Vietravel自2025-11-03起对超规手提行李收费的讯息在检索中出现，属全服务/其他航司子问题范畴，本轮未核实（原因：边界外信息，仅作提示）
### 信息缺口（优先级）
- 酷航/宿务/泰狮/捷星登机口执法严格度的一手旅客实测与抽查比例数据（本轮仅获二手转述与官方口径）（优先级：中）
- 泰狮航、亚航X（D7）的选座收费明细与机上商品销售品类/定价（本轮行李与餐食已覆盖，选座与机上零售未覆盖）（优先级：中）
- 亚航 Value Pack/Comfort/Flex 等打包产品（含托运+餐+选座）的具体包含项与价格表——这是亚航托运收费模式的最新变化，未能抓取官方页面核实（优先级：中）
- 越捷 SkyBoss 手提10-14kg按航线细分的精确口径，及国内线是否有同等登机口处理费（优先级：低）
- 捷星亚洲(3K)与捷星日本(GK)/捷星澳洲(JQ)在手提与托运费率上的精确差异表（现只有CabinZero聚合口径）（优先级：低）

---

## 欧美低成本（瑞安FR/威兹W6/易捷U2/精神NK/边疆F9）：免费额度（如瑞安40x20x25小包）、收费项清单（行李/选座/餐食/值机方式）、座位间距、美 ULCC 的预倾斜座椅等争议设计、二线机场使用情况

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- Spirit Airlines 已于 2026 年 5 月 2 日停止运营并进入 Chapter 7 清算，不再售票、不再运营航班——它不再是可预订的 ULCC 选项，题目中「精神 NK」的经验条目只能作为历史样本处理。（E50 · 置信度：高 · 类型：媒体 · 时点：2026-05-02，来源：https://www.npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds）
- Spirit 停运的直接诱因是伊朗战争推高航油价格、叠加向白宫寻求的 5 亿美元纾困谈判破裂；同时传统航司推出 basic economy 复制了 Spirit 的打法，压缩了其成本优势。（E51 · 置信度：高 · 类型：媒体 · 时点：2026-05-02，来源：https://www.npr.org/2026/05/02/nx-s1-5807933/spirit-airlines-ceases-operations-folds）
- 欧洲三大廉航的基础票价已不再包含任何可放行李架的随身行李，只保留座位下方小包：Ryanair 与 Wizz Air 均为 40×30×20cm、10kg；easyJet 为 45×36×20cm、15kg。Ryanair 与 Wizz Air 是最吝啬的两家。（E52 · 置信度：高 · 类型：媒体 · 时点：2026-07-09，来源：https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk）
  - 数字：easyJet 免费座位下小包尺寸/重量/容积 = 45 x 36 x 20 cm / 15 kg / 32.4 升（2026）；Ryanair 免费座位下小包尺寸/重量/容积 = 40 x 30 x 20 cm / 10 kg / 20 升（2026）；Wizz Air 免费座位下小包尺寸/重量/容积 = 40 x 30 x 20 cm / 10 kg / 24 升（2026）
- 免费额度之外的行李架位是「付费加购」而非含在票价内：Ryanair 的 Regular「Priority & 2 Cabin Bags」含 55×40×20cm/10kg 行李架位，官网标称 £12–£36（预订时）或 £20–£60（后加），但 Which? 实际核查未找到 £12 的票；Wizz Priority 含 55×40×23cm/10kg，官网在 Which? 投诉后把「€0 起」改为「€10 起」；easyJet 的大件行李架位 56×45×25cm、15kg，Which? 未找到低于 £23 的价格。（E53 · 置信度：高 · 类型：媒体 · 时点：2026-07-09，来源：https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk）
  - 数字：Ryanair Priority & 2 Cabin Bags 官网价（预订时） = £12-£36（2026）；Ryanair Priority & 2 Cabin Bags 官网价（后加） = £20-£60（2026）；Wizz Priority 大件行李架位尺寸/重量 = 55 x 40 x 23cm / 10kg（2026）
- 欧盟已立法要求所有飞抵欧盟及从欧盟起飞的欧洲航司必须为每位乘客提供至少 40×30×15cm 的免费标准随身行李，但该规则 2027 年才生效，且不必然适用于从英国出发的非欧盟航司（如 easyJet）——这是欧洲廉航随身行李规则未来 1–2 年将发生结构性变化的关键时间点。（E54 · 置信度：中 · 类型：媒体 · 时点：2026-07-09，来源：https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk）
  - 数字：欧盟强制免费随身行李最小尺寸 = 40cm x 30cm x 15cm（2027 起生效）
- easyJet 的 Essentials 票价包含 23kg 托运行李和一个标准座位，但明确不含随身行李——低价舱位组合并非「行李越少越便宜」的线性关系，容易被误导。（E55 · 置信度：中 · 类型：媒体 · 时点：2026-07-09，来源：https://www.which.co.uk/reviews/airlines/article/most-generous-airline-hand-luggage-aF9jK9M1uoMk）
- Frontier 的免费额度是 18×14×8 英寸随身小包（与 Spirit 停运前完全相同），无免费随身行李架箱；行李与选座费呈「越晚买越贵」的阶梯：预订时随身 $29 / 首件托运 $34，登机口则 $99 / $99，电话订座与机场柜台 $79。（E56 · 置信度：中 · 类型：媒体 · 时点：2026-06-10，来源：https://upgradedpoints.com/travel/airlines/frontier-airlines-review/）
  - 数字：Frontier 随身行李费（预订时/登机口） = $29 / $99（2026）；Frontier 首件托运费（预订时/登机口） = $34 / $99（2026）；Frontier 免费随身小包尺寸 = 18 x 14 x 8 in（2026）；Frontier 托运行李尺寸/重量上限 = 62 线性英寸 / 40 磅（2026）
- Frontier 的选座分四档且全部收费：标准座 $17–55、Stretch（加长腿空间）$20 起、UpFront（前排、锁定中间座空位）$49 起；不选座则值机时随机分配、可能被拆散同行旅客。购买随身行李可自动获得 Zone 1 优先登机。（E57 · 置信度：高 · 类型：媒体 · 时点：2026-06-10，来源：https://upgradedpoints.com/travel/airlines/frontier-airlines-review/）
  - 数字：Frontier 标准选座费（官网） = $17 to $55（2026）；Frontier Stretch 选座费起点 = $20+（2026）；Frontier UpFront 选座费起点 = $49+（2026）
- Frontier 是本组中「预倾斜座椅（pre-reclined）」设计最彻底的一家：全机队所有座位固定在略后倾位置、无法后仰，因此不存在「前排不收费后仰、后排收费解锁后仰」的分层；标准舱 28 英寸间距、18 英寸宽，Stretch 约 32–35 英寸，UpFront Plus 约 35 英寸并锁空中间座。（E58 · 置信度：中 · 类型：博客 · 时点：2026-07-23，来源：https://seatcompare.ai/insights/frontier-airlines-a321neo-seat-selection-guide-2026）
  - 数字：Frontier 标准舱座位间距 = ~28 英寸（2026）；Frontier Stretch 座位间距 = ~32–35 英寸（2026）；Frontier 座位宽度 = 18 英寸（2026）
- Frontier 以密度取胜：同一架 A321 上装 230 座，而达美同机型装 191 座；代价是无靠背娱乐屏、无 Wi-Fi、无电源插座，仅有折叠小桌板和顶部送风口。（E59 · 置信度：中 · 类型：媒体 · 时点：2025-08-31，来源：https://thriftytraveler.com/reviews/flights/frontier-airlines/）
  - 数字：Frontier A321 座位数 vs 达美同机型 = 230 座 vs 191 座（2025-08）
- Frontier 全程无免费餐饮：官网价非酒精饮料 $3.50 起、零食 $6.99 起、啤酒红酒烈酒 $9.99 起；实飞体验中可乐/果汁/瓶装水/咖啡 $3.99、Buzzballz 鸡尾酒 $10.99，但续杯免费。（E60 · 置信度：中 · 类型：媒体 · 时点：2026-06-10，来源：https://upgradedpoints.com/travel/airlines/frontier-airlines-review/）
  - 数字：Frontier 非酒精饮料起价 = $3.50（2026）；Frontier 零食起价 = $6.99（2026）；Frontier 酒类起价 = $9.99（2026）；实飞观察到的软饮/咖啡价格 = $3.99（2025-08）
- Frontier 把「值机方式」也做成了收费项：柜台帮旅客值机并打印登机牌的「Agent Assistance」收费 $20；优先登机 $7.99；电话订座每位旅客 $35；Discount Den 会员 $99.99/年（首年 $59.99 + 一次性 $40 注册费）。同时值机柜台与行李托运在起飞前 1 小时即关闭，早于多数航司。（E61 · 置信度：中 · 类型：媒体 · 时点：2025-08-31，来源：https://thriftytraveler.com/reviews/flights/frontier-airlines/）
  - 数字：Frontier 柜台值机/打印登机牌费 = $20（2025-08）；Frontier 优先登机费 = $7.99（2025-08）；Frontier 电话订座附加费 = $35/人（2026）；Frontier Discount Den 年费 = $99.99（2026）
- Frontier 官方 2026 年已完成座位产品分层：新增 2×2 布局的「First」高端座椅，并保留 UpFront Plus（锁空中间座）、Premium、Preferred、Standard 五层；Standard 座位位于机舱后中段，仅随 Economy 套餐赠送。（E62 · 置信度：高 · 类型：一手，来源：https://www.flyfrontier.com/travel/travel-info/seating-options/?mobile=true）
- Spirit 停运前的收费结构是本组中最典型的「只给小包」模式：最低价 Go/Value 票价连随身行李箱都不允许携带（付费也不行），免费仅限 18×14×8 英寸座位下小包；行李价格从预订约 $30–35 一路涨到登机口 $65 以上，按航段重复收费。（E63 · 置信度：高 · 类型：媒体 · 时点：2026-06-09，来源：https://deeparrival.com/airlines/spirit-airlines/baggage-fees/）
  - 数字：Spirit 随身箱费用（预订→登机口） = 约 $35 → $65 以上（2026 年停运前）；Spirit 首件托运费（预订→登机口） = 约 $30 → $65 以上（2026 年停运前）；Spirit 免费小包尺寸 = 18 x 14 x 8 in（2026 年停运前）
- Spirit 停运前的超重/超规与第二件托运惩罚性极强：51–100 磅超重 $125/件、63–80 线性英寸超规 $150/件、超过 80 英寸直接拒收；第二件托运 $75 每程，第三至第五件各 $99 每程；Saver$ Club 约 $70/年，但如今每件行李只省 $1。（E64 · 置信度：高 · 类型：媒体 · 时点：2025-10-31，来源：https://thriftytraveler.com/guides/airlines/spirit-airlines-baggage-fees/）
  - 数字：Spirit 超重费（51–100 磅） = $125/件（2025-10）；Spirit 超规费（63–80 线性英寸） = $150/件（2025-10）；Spirit 第二件托运费 = $75/程（2025-10）；Spirit 第三至第五件托运费 = $99/件/程（2025-10）；Spirit Saver$ Club 年费 = 约 $70（2025-10）
- Spirit 停运前的托运行李重量上限已从长期沿用的 40 磅上调到 50 磅（62 线性英寸），是美国 ULCC 中较少见的放宽。（E65 · 置信度：高 · 类型：媒体 · 时点：2025-10-31，来源：https://thriftytraveler.com/guides/airlines/spirit-airlines-baggage-fees/）
  - 数字：Spirit 托运行李重量上限 = 50 磅（2025-10）；Spirit 托运行李尺寸上限 = 62 线性英寸（2025-10）
- Ryanair 的二线机场扩张与地方政府取消机场税直接绑定：2026 年 1 月在 Trapani-Marsala 开设第三个西西里基地（也是其在意大利的第 20 个基地），投入 2 架飞机、2 亿美元、23 条航线、年旅客超 100 万；官方明确点名 Abruzzo、Calabria、Friuli-Venezia Giulia 三个小机场已因低机场成本录得创纪录增长。（E66 · 置信度：高 · 类型：一手 · 时点：2025-09-24，来源：https://corporate.ryanair.com/novetats/ryanair-to-open-new-trapani-marsala-base-from-jan-26/）
  - 数字：Ryanair Trapani-Marsala 基地投资 = $200M（2026-01 起）；Ryanair Trapani-Marsala 航线数/年旅客 = 23 条航线 / >100 万（2026）；Ryanair 在意大利的基地数 = 第 20 个（2025-09）
- Ryanair 2026 年 4 月在 Tirana 启用 4 架飞机基地（4 亿美元投资、44 条航线、客流增长 50% 至 400 万人次），并计划到 2030 年增至 6 架飞机、6 万人次以上、60+ 航线；官方把增长原因归因于阿尔巴尼亚零税航空政策与机场的成长激励方案。（E67 · 置信度：高 · 类型：一手 · 时点：2026-04-01，来源：https://corporate.ryanair.com/news/ryanair-opens-4-aircraft-us400m-tirana-base-deliver-record-growth-in-albania/）
  - 数字：Ryanair Tirana 基地投资与运力 = 4 架飞机 / $400M / 44 条航线（2026 夏）；Ryanair Tirana 客流增长目标 = +50% 至 400 万人次（2026）；Ryanair Tirana 2030 年目标 = 6 架飞机 / >600 万客流 / 60+ 航线（2030）
- Ryanair 在欧洲的长处是最便宜的基础票价，代价是值机口严格执行的小包尺寸测量与较差的客户体验排序；easyJet 则用更大的免费小包与更主要（交通便利）的机场换取更高体验评价——这构成欧美 LCC「便宜但折腾」与「稍贵但省心」的典型分野。（E68 · 置信度：低 · 类型：博客 · 时点：2026-07-04，来源：https://travelbeck.com/cheapest-airlines-in-usa/）
  - 数字：Ryanair 标准舱座位间距（单一 D 级来源） = 30 英寸（2026）；Spirit A320neo 标准舱座位间距（单一 D 级来源） = 28 英寸（2026）
### 不确定项
- Ryanair 免费座位下小包的准确三维尺寸到底是 40×30×20cm 还是 40×20×25cm（题目给出的「瑞安 40x20x25」对应哪一种表述）（原因：Which?（2026-07）与 bgberlin（2026-09）、holidayexpert（2026-07）三源一致给出 40×30×20cm / 10kg / 20 升，但 carrysizer 的对比表把 Ryanair 写成 40×20×25cm。两种表述体积不同（20,000 vs 24,000 cm³），Ryanair 官网因 cookie 墙无法直读，疑为第三方转述时的维度顺序不一致，未能以一手来源判定。）
- Ryanair 与 Wizz Air 的确切座位间距（Ryanair 30 英寸 vs Wizz 28 英寸）及是否完全不后仰（原因：仅有 travelbeck（D 级自媒体）单一来源给出 30 英寸且称「non-reclining slimline」；另一条给出 Ryanair 30 英寸 vs Wizz 28 英寸的对比（aifly.one）正文抓取超时失败，tripprof 同样超时。未找到 SeatGuru、航司官网或行业报告级佐证。）
- Spirit 是否在其运营末期仍保留名为「Delta Recline」的预倾斜/付费解锁后仰座椅产品（原因：多轮检索均未命中该产品线的直接证据；Spirit 后期的高端产品线记录为 Spirit First（原 Big Front Seat）与 Go Comfy（锁空中间座），travelvient 与 deeparrival 也只描述 28 英寸标准舱与 Spirit First 的 36 英寸，不提后仰分级。无法确认「预倾斜争议设计」在 Spirit 上的具体形态与存续时间。）
- Ryanair 2026 年在德国新增 Saarbrücken 与 Friedrichshafen 两个二线机场（原因：仅 nomadlawyer.org（D 级，含 AI 生成配图）单一来源提及，未在 Ryanair 官方新闻稿或 CAPA/行业媒体中交叉验证。）
- Wizz Air 2024–2025 年登机口行李费已从约 €50 上移至 €60–90、Budapest/Luton/Bucharest/Abu Dhabi 为最严格执行点、Wizz Air Plus 订阅约 €99/年（原因：仅 carrysizer 一源，且该站自述由「Codex (AI source review）」做来源审查、明确不主张实机测试，权威性低；官方 Wizz 页面未抓取成功。）
- 美国 ULCC（尤其 Frontier）的二线机场使用情况与集中度（原因：本轮未检索到任何份额/航线结构数据；仅间接看到 Frontier 总部在 Denver、机组提到 MSP 运营于较小的 Terminal 2。没有可用的量化证据。）
### 信息缺口（优先级）
- Wizz Air 与 easyJet 的座位间距、是否后仰、座位型号等客舱硬指标（仅有 Ryanair 28–30 英寸的 D 级来源）（优先级：高）
- 美国 ULCC（Frontier 为主）在二线/非枢纽机场的运力占比具体数据（如 Newark、RNO、Portland 等非传统基地的份额）（优先级：高）
- Spirit 停运后其原航线运力由谁接手、二线机场格局如何重排（Frontier 被称为最接近替代者但无份额数据）（优先级：高）
- Ryanair / Wizz / easyJet 是否以及如何对「机场柜台值机/超时段值机」收费（Frontier 的 $20 Agent Assistance 已确认，欧洲三家未确认）（优先级：中）
- Wizz Air / easyJet 2026 年新开基地清单与二线机场落点（Ryanair 侧已确认，Wizz 侧仅有 Oradea 一处 D 级来源）（优先级：中）
- 五家 ULCC 的量化口碑指标（J.D. Power 北美航司满意度、ACS I、Skytrax、EU 消费者投诉统计）（优先级：中）
- Ryanair 737 MAX 10 引入后座位间距是否变化，以及新一代 737-8 座椅的官方间距数据（优先级：低）
- 欧盟 2027 随身行李规则的具体法条文号、立法状态与「不适用于从英国出发的非欧盟航司」的法律依据（目前只有 Which? 的二手表述）（优先级：低）

---

## 国际全服务头部（日航JL/全日空NH/大韩KE/新航SQ/国泰CX/泰航TG/阿联酋EK/卡塔尔QR/汉莎LH/法航AF/英航BA/美航AA/达美DL/美联航UA）：国际线行李计量制度（重量制vs件数制）、免费餐食与酒水、经济舱座椅间距、联盟归属、服务口碑亮点

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- Skytrax 2026 世界航空奖（2026-09 于伦敦公布）：新加坡航空第1（自1999年办奖以来第六次夺冠）、卡塔尔航空第2、国泰航空第3、ANA第4、土耳其航空第5、阿联酋航空第6、法航第7、海南航空第8、日本航空第9、大韩航空第10；汉莎第14、泰航第20。三大美国航司（AA/DL/UA）无一进入前十。（E69 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://www.businessinsider.com/best-airlines-in-the-world-ranking-passengers-skytrax-2026-9）
- Skytrax 2026 最佳经济舱前十：新航第1、国泰第2、卡塔尔第3、长荣第4、ANA第5、日本航空第6、海南第7、土航第8、星宇第9、达美第10（美系仅达美入榜）；新航同时拿下最佳经济舱机上餐饮奖，阿联酋拿下最佳机上娱乐，国泰获最佳乘务员奖。（E70 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://www.bbc.com/travel/article/20260924-the-worlds-five-best-economy-airlines-for-2026-and-what-makes-them-so-much-better）
- 新加坡航空采用双轨行李制：除飞/抵美国与加拿大外按重量计（经济舱按票价档次 30kg 或 25kg，单件不超过32kg），飞美加航线按件数计（经济舱/超级经济舱2件×23kg，商务/头等2件×32kg）。（E71 · 置信度：中 · 类型：媒体 · 时点：2026-06，来源：https://upgradedpoints.com/travel/airlines/singapore-airlines-baggage-fees/）
- 国泰航空按行程单标注计量：PC（件数）或 K（重量）两种制度并存；单件上限头等/商务舱32kg、超级经济舱/经济舱23kg，三边合计不超过158cm（超尺寸加收200美元/件，超32kg按4倍加收）；额外行李按分区计件（100–260美元/件）或按公斤（13–65美元/kg）收费。（E72 · 置信度：中 · 类型：官方 · 时点：2025-12，来源：https://www.cathaypacific.com/cx/en_US/baggage/extra-baggage-charges/pay-cash-or-by-credit-card.html）
- 泰航自2026年3月2日起由计重制改为计件制：经济舱 Full/Flex 票2件×23kg，Standard/Saver/奖励票1件×23kg；超级经济舱2件×23kg、Premium Economy Plus与公务舱2件×32kg、头等舱3件×32kg（点数兑换头等为2件）；单件三边合计不超过158cm。（E73 · 置信度：中 · 类型：媒体 · 时点：2026-02，来源：https://www.executivetraveller.com/news/thai-airways-new-luggage-allowance）
  - 数字：泰航国际线行李计量制切换生效日 = 2026-03-02
- 全日空（ANA）国际线为计件制：经济舱所有国际航线2件×23kg（单件三边≤158cm），公务舱2件×32kg，头等舱3件×32kg；日本国内线原为计重制（经济舱合计20kg），官方页显示其国内线改制条款同样采用每件23kg/经济舱最多2件的计件口径。（E74 · 置信度：中 · 类型：官方 · 时点：2026-06，来源：https://www.ana.co.jp/en/jp/promotion/renewal-2025-2026/system/）
  - 数字：ANA 经济舱单件免费托运重量 = 23kg per piece
- 日本航空（JAL）国际线经济舱/超级经济舱免费托运2件×23kg，公务/头等3件×32kg；手提2件合计10kg（机身100座以上为55×40×25cm）；单件上限三边合计203cm、45kg；超额件费区内段约1万日元、欧美/大洋洲航线约2万日元。（E75 · 置信度：低 · 类型：博客 · 时点：2026-06，来源：https://aifly.one/guides/japan-airlines-baggage-allowance/）
- 达美航空：6.5小时及以上航段（含长途国际航班）提供免费啤酒、葡萄酒与烈酒，350英里以上航段提供饮品与小吃服务；自2026年5月19日起取消350英里以下经济舱的免费零食与饮品（涉及约9%的日航班量），350英里及以上反增全服务。同口径下美航在250英里以上提供免费零食与无酒精饮料，联航全航班提供免费无酒精饮料、300英里以上提供免费小吃。（E76 · 置信度：高 · 类型：官方 · 时点：2026-07，来源：https://www.delta.com/us/en/onboard/food-and-beverage/overview）
  - 数字：达美免费酒水适用航段门槛 = 6.5 hours or more；达美取消免费零食饮品的航段上限 = 350 miles（2026-05-19 起）
- 卡塔尔航空经济舱长航线免费餐食并提供较宽的酒水选择（红/白/起泡酒、鸡尾酒、杜松子汤力等），多数长航段经济舱啤酒、红白酒与部分烈酒为免费供应；具体品类随航线、配餐站与季节变化，无全网统一保证。（E77 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://taketravelinfo.com/can-you-drink-alcohol-on-a-qatar-air/）
- 卡塔尔航空官方行李页显示：经济舱各票价（Economy Lite/Classic/Convenience/Comfort）免费托运为2件、每件不超过23kg（50lb），手提行李1件不超过7kg（15lb）。（E78 · 置信度：中 · 类型：官方 · 时点：2026-06，来源：https://www.qatarairways.com/en-us/baggage/allowance.html）
  - 数字：卡塔尔航空经济舱免费托运 = 2 pieces up to 23kg (50lb) each；卡塔尔航空经济舱手提行李 = 1 piece up to 7kg (15lb)
- 经济舱座椅间距：ANA 部分787-9布局可达34英寸（多数远程经济舱常见31–32英寸），日本航空在777/787上可达34英寸、椅宽超18英寸；新航约32英寸/17–18英寸，阿联酋约32英寸/17.3–18英寸，卡塔尔约31英寸/约18英寸；新航777-300ER经济舱为3-3-3九座布局（同机型竞品多为十座）。达美等美系航司各机型不统一。（E79 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://www.bbc.com/travel/article/20260924-the-worlds-five-best-economy-airlines-for-2026-and-what-makes-them-so-much-better）
  - 数字：ANA 787-9 部分配置经济舱座椅间距 = up to 34 inches；多数远程经济舱常见座椅间距 = 31 to 32 inches
- 联盟归属（2026年口径）：oneworld 由美航、英航、卡塔尔、日航、国泰等15家组成；天合联盟18家，含达美、法航、大韩等；星盟26家，含联航、汉莎、ANA、新航、泰航等。阿联酋航空2026年为非联盟航司，仅与澳航等逐家双边合作并与联航等 codeshare。（E80 · 置信度：中 · 类型：媒体 · 时点：2026-08，来源：https://travelvient.com/guides/airline-alliances-and-partners-2026/）
- 阿联酋航空2026年仍未加入任何全球航空联盟，属主动选择非联盟策略（与澳航为双边 partners 关系，与联航等有 codeshare）。（E81 · 置信度：中 · 类型：媒体 · 时点：2026-08，来源：https://travelvient.com/guides/airline-alliances-and-partners-2026/）
- Skytrax 2026 最佳经济舱榜单第10位为达美航空，是唯一进入前十的美国航司。（E82 · 置信度：中 · 类型：媒体 · 时点：2026-09，来源：https://www.bbc.com/travel/article/20260924-the-worlds-five-best-economy-airlines-for-2026-and-what-makes-them-so-much-better）
### 不确定项
- ANA 官方改制页的行李件数条款是否同时适用于国际线（原因：该页正文标注了「同时影响国际航班」的图标，但抓取后的纯文本丢失了图标，无法100%确认「经济舱最多2件、每件23kg」是仅限日本国内线改制条款还是已覆盖国际线；国际线2×23kg另有二手来源佐证。）
- 卡塔尔航空官方行李页的免费额度（原因：qatarairways.com 的 /en/ 与 /en-us/ 两个 baggage/allowance.html 页面均返回 403（Akamai 拦截），我实际读到的是搜索引擎返回的官方页面摘要文本，页面正文未能亲自访问。）
- 日本航空国际线 2×23kg 的可靠性（原因：唯一读到的是 aifly.one 二手指南（自称已核对 jal.co.jp），未取得 JAL 官网原始页面，置信度仅 low。）
- 阿联酋航空的联盟状态与「已加入天合」的传闻冲突（原因：本次来源（travelvient，核验至2026-08，并引用 skyteam.com 会员页）明确称 EK 为非联盟航司；此前业界长期流传 EK 拟加入天合，但未找到任何官方加入公告。）
- 「美系航司取消免费餐」的适用范围（原因：达美2026-05 的调整只针对 350 英里以下航段，NYT 同篇对美航/联航的免费饮品描述同样是美国国内航线口径；长途国际主舱是否仍免费餐食、酒水是否收费，我未取得任何官方确认。）
- 联盟成员数量与大韩合并韩亚的过渡状态（原因：travelvient 称星盟26家、天合18家、oneworld 15家，并称韩亚（已被大韩整合）于2026年6月宣布将退出星盟、预期转向天合；此变动时点与最终归属未见联盟官网直接确认。）
### 信息缺口（优先级）
- 美航(AA)、达美(DL)、联航(UA) 国际线免费托运行李的件数制细则（主舱 1 件 vs 2 件、Basic/Main Basic 差异、23kg/件上限）——只有检索摘要级线索，未读任何官方页面（优先级：高）
- 汉莎(LH)、法航(AF)、英航(BA) 国际线计重制 23kg 的官方页面，以及三家手提行李（8kg/12kg/23kg）差异——检索仅得摘要，未取得可引用正文（优先级：高）
- 大韩航空(KE) 国际线免费托运的件数与每件重量（是否为 2×23kg 或 30kg 制）——未取得任何来源正文（优先级：高）
- 阿联酋航空(EK) 国际线经济舱免费托运行李额度（1 件 23kg? 7kg 手提?）——未取得来源（优先级：高）
- AA/DL/UA 国际线经济舱是否仍提供免费正餐、酒水是否收费的官方口径（优先级：高）
- 日航/大韩/泰航/国泰/阿联酋/卡塔尔/汉莎/法航/英航/美系三大航逐机型经济舱座椅间距的官方或座位图数据库级数据（目前只有新航/ANA/日航/阿联酋/卡塔尔口径）（优先级：中）
- JL/KE/TG 官方行李页（jal.co.jp、koreanair.com、thaiairways.com）直接抓取——本轮未取得，因而不把相关数字列为 confirmed（优先级：中）
- AirLineRatings「2026全球最佳航空公司」与 Skytrax 2026 两套榜单的并列引用规则（口径差异是否影响结论）（优先级：低）

---

## 行李计量制度总纲：中国民航国内线免费额度行业惯例（全服务 20kg 托运+手提规定的现状）、廉航免费额度行业现状、北美件数制（piece concept）概念、不同航司联程时行李规则如何适用（Most Significant Carrier 规则概要）

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 北美头部航司托运行李以「件」为单位计量，并对每件同时设置重量与线性尺寸双重限制：达美规定行李三边之和不得超过 62 英寸（157 厘米），西南航空的标准重量限制为每件 50 磅；达美并明确尺寸、重量、数量三类超限「分别收费」。两家互不隶属的航司官方页面互证「50 磅 / 62 英寸」这一北美通行件制基准。（E83 · 置信度：高 · 类型：官方，来源：https://www.delta.com/us/en/baggage/overview）
  - 数字：达美托运行李线性尺寸上限（长+宽+高） = 62 inches (157 cm)（2026-09 现行页面）；西南航空标准单件重量上限 = Up to 50 pounds each（2026-09 现行页面）
- 达美对件制托运行李实行阶梯收费：第二件标准行李（单件低于 50 磅/23 千克）每程 55 美元，第三件起每程 200 美元，且件数、重量、尺寸三类超限各自单独计费（同件既超重又超大则叠加三项费用）。（E84 · 置信度：高 · 类型：官方，来源：https://www.delta.com/us/en/baggage/overview）
  - 数字：达美第二件标准行李费（每程） = $55 USD（2026-09 现行页面）；达美第三件行李费（每程） = $200 USD（2026-09 现行页面）
- IATA 将托运行李免费额度标准化为两种并列概念——计重制（Weight Concept，票面以 20 kg/45 lb 之类重量表示）与计件制（Piece Concept，票面以 PC 表示），部分航司混合使用；中国航司的国际/地区航线实际采用计件制——首都航空官网明载其国际及地区航线免费行李额「为计件制」。（E85 · 置信度：中 · 类型：官方 · 时点：2020-06，来源：https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf）
- 联程（interline）行程的行李规则按 IATA Resolution 302 的四步法选取：各参与承运人公布规则相同则通用该规则；规则不同时整程适用最主要承运人（MSC）公布的规则；MSC 无公布规则则适用接收行李承运人的规则；接收方亦无则按航段分段适用各实际承运人规则。（E86 · 置信度：中 · 类型：官方 · 时点：2020-06，来源：https://www.ana.co.jp/en/jp/guide/boarding-procedures/baggage/international/iata-302/）
- MSC 是「以行李运输段为单位」逐段选取的，而非按整程一次判定：跨 IATA 交通会议区（TC）时取承运第一个跨区航段的承运人（环球线 TC123 例外，取第一个跨 TC1–TC2 航段的承运人）；跨次区时取第一个跨次区航段的承运人；同一次区内时取承运第一个国际航段的承运人。（E87 · 置信度：中 · 类型：官方 · 时点：2022-07-15，来源：https://jdair.net/micro/main/help/6435365937c5ce32acf80c49）
- IATA 交通会议区（TC）分为三区：TC1 为西半球（美洲与加勒比）、TC2 为欧洲中东非洲、TC3 为亚洲与亚太；中国被归入 TC3 之下的东南亚次区。MSC 规则即以这套区/次区划分为判定依据。（E88 · 置信度：中 · 类型：官方 · 时点：2020-06，来源：https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf）
- 北美航线是 MSC 规则的例外：美国与加拿大要求「客票第一张联程客票上的市场航空公司」的行李规则适用于该客票全部航段——美国依据 U.S. DOT Regulation 399.87，加拿大依据 CTA Order 2014-A-158；因此「始发或最远目的地在美加」的行程规则由首个市场承运人决定，而非按跨区判定 MSC。（E89 · 置信度：中 · 类型：官方 · 时点：2020-06，来源：https://www.iata.org/contentassets/e7a533819be440edbb1e49da96e0f2a8/guidance-document-on-baggage-standards-for-interline.pdf）
- 中国民航机上并不存在「20 公斤免费托运」的强制标准——《公共航空运输旅客服务管理规定》（交通运输部令 2021 年第 3 号，自 2021-09-01 施行）删除了原《国内客规》中关于行李尺寸、重量、免费行李额、逾重行李费的「一刀切」规定，改为要求承运人在运输总条件中自行明确免费行李额、托运与非托运行李的尺寸/重量/数量要求、超限行李费计算方式等七项内容并对外公布。因此国内线 20kg 免费额度是各航司趋同形成的行业惯例，而非国家规定。（E90 · 置信度：高 · 类型：官方 · 时点：2021-09-01，来源：https://xxgk.mot.gov.cn/2020/gz/202112/W020211221393138820021.pdf）
- 同一部规章把免费行李额转化为「强制披露」义务：承运人或其航空销售代理人通过网络销售客票时，必须以显著方式告知所选航班的行李运输规定（含行李尺寸、重量、免费行李额等），运输总条件全文须作为购票必读内容。2026 年的媒体调查指出第三方平台购票时普遍无此显著提示，正是 20 寸登机箱在机场被收费的投诉根源。（E91 · 置信度：高 · 类型：官方 · 时点：2026-06-03，来源：https://xxgk.mot.gov.cn/2020/gz/202112/W020211221393138820021.pdf）
- 中国航司已把 IATA 联运行李规则内化为自身运价规则并实际执行：首都航空《国际及地区航线运价手册》（自 2022-07-15 起执行）在「第二部分 行李规则」中完整复述 Res 302 四步法与 MSC 选取三原则，并给出中国出港示例——青岛经首都航空飞曼谷再转新加坡属 TC3 东南亚次区内旅行，故第一个国际航段的承运人首都航空为 MSC；代码共享航班一般适用市场方规则，除非市场方公布规则声明用实际承运人。（E92 · 置信度：中 · 类型：官方 · 时点：2022-07-15，来源：https://jdair.net/micro/main/help/6435365937c5ce32acf80c49）
- 中国廉航行业现状是基础票价不含免费托运行李额，行李与餐食被打包成付费选项：媒体调查显示「多数低成本航空公司普通经济舱已禁止免费携带 20 寸行李箱」而全服务航司仍保留免费携带规定；九元航空南京—广州航线需另购「20 寸手提 + 20KG 托运额 + 机上餐食」组合，票价 439 元。（E93 · 置信度：中 · 类型：媒体 · 时点：2026-06-02，来源：https://m.gmw.cn/2026-06/02/content_1304481367.htm）
  - 数字：九元航空南京-广州「20寸手提+20KG托运+餐食」组合票价 = 439元（2026-06）
### 不确定项
- 北美网络型航司（达美/美联航/美航）经济舱免费托运的具体件数（行业常见口径为美国国内免费 2 件、合计 32 公斤/70 磅）无法用一手航司页面直接证实——我读到的达美官方页只给出「第二件 55 美元、第三件起 200 美元」「每人 2 件运力表述」与 50 磅/62 英寸件制基准，未读到「前 2 件免费」的原文。（原因：美联航官网（united.com）与达美国内费用表为 JS 渲染，检索摘要或被反爬拦截；需另找可抓取的航司费用表或 14 CFR 层面文件。）
- IATA Resolution 302 与上述联运行李框架是否在 2021 年之后（2022–2026 年旅客标准会议 PSC）发生实质修订未核实——所依据的 IATA 文件自述「effective from 1 June 2020」。（原因：IATA 决议原文需付费订阅（PSC Manual），公开渠道只能拿到航司转载的旧版文本与 IATA 2020 指引文件。）
- 中国民航是否存在行业组织或民航局层面倡导「国内线经济舱 20kg 免费托运」统一口径的自律文件未见证实；现有证据只表明各航司运输总条件彼此趋同（20/30/40kg）而无法规强制。（原因：检索命中的是航司运输总条件与规章解读，未找到中国民航报或民航局关于统一免费额度的倡导性文件。）
- 首都航空《国际及地区航线运价手册》页面未标注更新日期，其自述执行日期为 2022-07-15，是否为截至 2026 年的现行版本无法确认。（原因：页面无版本号与更新标注；同页引用中出现的航司内部文号（如 JDIR21014）指向 2021—2022 版本。）
### 信息缺口（优先级）
- 联运行李规则在中国国内航线（非国际/地区）的适用口径：国内线是否同样走 IATA Res 302/MSC 框架，还是另有国内航司间的行李直挂互认规则（同一联盟内 vs 跨联盟）——首都航空手册只覆盖国际/地区运价，国内线口径缺一手来源。（优先级：高）
- 北美件数制的「免费件数」官方对照表：主流航司在美国国内（2 件）与跨洲/国际（如 3 件、星空联盟 3 件）之间的免费件数分级，以及各航司 SkyMiles/常旅客等级加成，均未取得一手航司原文。（优先级：高）
- 中国中型全服务航司（吉祥航空、海航/金鹏、深圳航空、天津航空、华夏航空、瑞丽航空）国内线免费托运额度是否同样为经济舱 20kg/公务 30kg/头等 40kg——共享台账只覆盖三大航 + 川航 + 厦航，本次未补充独立来源。（优先级：中）
- 中国廉航是否存在「含免费托运额」的反例（特定航线、促销票、会员权益赠行李），以及民航局对廉航差异化行李收费的合规边界与投诉处理口径。（优先级：中）
- IATA 决议与推荐做法（RP1788 免费/优惠运输的行李规定、Res 722 电子客票行李数据 20K/30K/2PC 填法）对中国航司出票系统与代理操作的落地影响未展开。（优先级：低）

---

## 经济舱座椅间距与数据源：各头部航司经济舱 seat pitch 典型区间（全服务 31-32 寸 vs 廉航 28-30 寸）、哪些航司以拥挤著称、SeatGuru 停更后可用的替代数据源（aeroLOPA/SeatMaps 等）

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- SeatGuru 已于 2025 年 10 月 31 日正式关停，域名重定向至 TripAdvisor，25 年积累的座位图数据被整体下线且未提供替代品。（E94 · 置信度：高 · 类型：媒体 · 时点：2026-09-28，来源：https://en.wikipedia.org/wiki/SeatGuru）
- SeatGuru 的归属常被误传：它不是 2018 年被 Jetstar 收购，而是 2007 年被 Expedia 集团旗下 Tripadvisor 部门收购，2011 年 12 月随 Expedia 分拆 Tripadvisor 而留在 Tripadvisor 手中；其数据在 2020 年初即停止更新，关站前已停更五年以上。（E95 · 置信度：高 · 类型：媒体 · 时点：2025-10-31，来源：https://en.wikipedia.org/wiki/SeatGuru）
- SeatGuru 关站后被广泛引用的替代源包括 2LNR、AeroLOPA、SeatMaps.com、FlightSeatmap.com、ExpertFlyer 与 Seatcompare.ai；The Points Guy 另推荐 ExpertFlyer 与 SeatMaestro。（E96 · 置信度：高 · 类型：媒体 · 时点：2026-02-09，来源：https://en.wikipedia.org/wiki/SeatGuru）
- AeroLOPA 是关站后被最广泛认可的首选替代源：其座位图由执业建筑师按真实比例（to-scale）绘制，数据库已覆盖 208 家航司，登录后可查看逐座位 pitch 评分，并已支持按航班号+日期检索；原 SeatGuru 创始人 Matt 公开为其背书。（E97 · 置信度：高 · 类型：媒体 · 时点：2026-09-11，来源：https://australianfrequentflyer.com.au/find-accurate-airline-seat-maps）
- SeatMaps.com 于 2020 年由一家德国数据公司上线，交互体验最接近 SeatGuru（可用航班号/航线反查、色码座位评价、点选座位显示 pitch/宽度/后倾角、部分机型 3D 视图），但其数据质量存在明确的行业批评：有航司/客舱信息「泛泛而谈，甚至严重不准确」，因此它只适合做快速横比，不宜当作 pitch 的权威来源。（E98 · 置信度：中 · 类型：媒体 · 时点：2026-09-11，来源：https://australianfrequentflyer.com.au/find-accurate-airline-seat-maps）
- ExpertFlyer（Red Ventures/TPG 旗下）已把 AeroLOPA 座位图作为底图，并叠加该机型当班的座位实时可售状态与座位提醒（仅部分机型、需 Premium/Elite 订阅），是目前唯一能「静态布局 + 当班实况」合一的来源。（E99 · 置信度：中 · 类型：媒体 · 时点：2026-09-11，来源：https://australianfrequentflyer.com.au/find-accurate-airline-seat-maps）
- 南航官网英文站「机舱布局」页提供逐机型官方 Seat Pitch 表格，是可直接引用的一手来源；其 B777-300ER(773) 国际线布局为 361 座（公务舱 28／明珠经济舱 28／经济舱 305），官方自报经济舱 seat pitch 为 31/32/33 英寸、扶手间座椅宽度 18.5/16.8/16.3 英寸——即同机经济舱内段最窄处仅 16.3 英寸，比 3-4-3 的 17 英寸更窄。（E100 · 置信度：中 · 类型：官方，来源：https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/boyin/1d8l5fmj01j95.shtml）
- 关键修正：不能把「中国全服务航司经济舱 = 31-32 英寸」当成通则。南航自家 A320(32X) 是 180 座全经济舱单一布局，官方自报 seat pitch 仅 28/29/36 英寸——与春秋、九元等廉航同处 28-29 英寸档，但座椅宽度达 19.07-20.75 英寸（明显宽于廉航约 17 英寸）；其 A320(320) 国际线三舱布局经济舱 pitch 为 39/36/35/33/31/30 英寸。即同一航司内，窄体 28-30 英寸、全经济舱高密度型 28-29 英寸、宽体 31-33 英寸并存。（E101 · 置信度：中 · 类型：官方，来源：https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/1hh7mef56t4pp.shtml）
- 全球行业基准：多数航司经济舱 seat pitch 在 30-32 英寸区间，仅少数特定座位可达 34 英寸；低成本与超低成本航司普遍把行距压到 28-29 英寸（71.1-73.7 cm），被媒体形容为 legroom 最受限的一档。（E102 · 置信度：中 · 类型：媒体 · 时点：2026-03-18，来源：https://simpleflying.com/economy-seats-worlds-greatest-pitch-2026/）
  - 数字：全球多数航司经济舱 seat pitch 区间 = 30-32 英寸（2026）；低/超低成本航司经济舱 seat pitch = 28-29 英寸（71.1-73.7 cm）（2026）
- 全球以经济舱拥挤著称的航司集中在低价段：Wizz Air 28 英寸、Frontier 全部国际航班 28 英寸、easyJet 28.5-29 英寸、Spirit 28-29 英寸、Ryanair（737-800／737 MAX 8200）28-29 英寸，且 Frontier 座椅不可后仰、Spirit 需付费升级 Big Front Seat 才有更大空间。（E103 · 置信度：中 · 类型：媒体 · 时点：2026-04-12，来源：https://www.travelandleisureasia.com/hk/travel-tips/trip-planning/airlines-that-offer-the-most-and-the-least-legroom/amp）
  - 数字：Wizz Air 经济舱 legroom = 28 英寸（71 cm）（2026）；Frontier 国际航班经济舱 legroom = 28 英寸（71 cm）（2026）；easyJet 经济舱 legroom = 28.5-29 英寸（72-74 cm）（2026）；Spirit 经济舱 legroom = 28-29 英寸（71-74 cm）（2026）；Ryanair 737-800 / 737 MAX 8200 legroom = 28-29 英寸（71-74 cm）（2026）
- 经济舱最宽敞的一档是日本与海湾航司：JAL 约 34 英寸（JAL 官网口径 777/767 为 86cm、787 为 84cm，787 上以 2-4-2 取代标准 3-3-3），ANA 约 34 英寸、Emirates 约 34 英寸（其 A380 为 3-4-3），国泰 32 英寸。反向案例是 JetBlue——原先以 32-33 英寸著称，自 2026 年夏季起将其空客机队统一降至 30 英寸行业标准，改推 36-37 英寸的 Mini Mint 付费前排产品。（E104 · 置信度：中 · 类型：媒体 · 时点：2026-04-12，来源：https://www.travelandleisureasia.com/hk/travel-tips/trip-planning/airlines-that-offer-the-most-and-the-least-legroom/amp）
  - 数字：JAL 经济舱 legroom = 约 34 英寸（86.4 cm）（2026）；国泰经济舱 legroom = 32 英寸（81.3 cm）（2026）；JetBlue 空客机队经济舱 legroom（2026 夏起） = 30 英寸（76 cm）（2026 夏季起）
- 中国航司经济舱 pitch 的通行行业口径为 31-32 英寸（与美国航司相当），但决定舒适度的关键变量是机型布局而非航司品牌：777-300ER 若采用十联排（3-4-3）会把座椅压到 17 英寸宽，而 A350-900 与 787-9 采用 3-3-3、座宽 18 英寸。此条仅作方向性旁证，该来源站点内容质量存疑。（E105 · 置信度：低 · 类型：媒体 · 时点：2025-12-29，来源：https://www.airtraveler.club/blog/rise-of-chinese-airlines/）
  - 数字：中国航司经济舱 seat pitch 通行口径 = 31-32 英寸（2025）
### 不确定项
- airtraveler.club 的中国航司 pitch 对照表（海航 31-33″/南航 32″、东航 32″、国航 31-33″/32″、厦航 32-33″）是否可信（原因：该站正文含 'Flights to Asia for half-price. Thanks, AI.' 等自述性表述并导流会员折扣，疑似 AI 批量生成内容；其「中国航司 31-32 英寸」结论与南航官网 777 官方值（31/32/33 英寸）方向一致，但对国航/东航/海航/厦航的具体数字没有任何官方或独立来源佐证，故仅作 low 置信度旁证，未纳入 confirmed 主体。）
- 南航官网页面本身是否仍为现行有效机舱配置（原因：csair.com 机舱布局页正文无任何日期或版本标注，抓取时页面底部仅注 'layout are for reference only'；无法确认其数据对应 2026 年现行机队还是历史配置（尤其 A320(32X) 180 座 28/29 英寸这类高密度型可能已退出或仍在用）。）
- 南航中文版官网与英文版对同一机型的 pitch 标注存在差异（原因：搜索摘要显示 B777A 国内线中文版标注经济舱 31-32 英寸，而英文版 B777-300ER 标注 31/32/33 英寸、B777-300ER(77W) 四舱布局标注 31-33 英寸。差异可能来自不同机型/不同舱位版本，但未能逐页渲染核实，无法判断是版本差异还是官方数据本身不一致。）
- 春秋/九元/西部航空的 seat pitch 是否有一手官方来源（原因：本次仅拿到 SeatMaps 等第三方口径（共享台账已收录春秋 A320 约 28-29 英寸、中联航 737-800 为 30-31 英寸），未找到春秋/九元/西航官网披露机舱 pitch 的页面；南航已有官方页，说明部分中国航司确实会公开，春秋系未公开的原因未确认。）
### 信息缺口（优先级）
- 国航、东航、海航、厦航、川航官网是否同样提供官方逐机型 seat pitch 表格（南航已有英文站可静态抓取的机舱布局页，其余航司未验证），以及各自的官方 pitch 具体值（优先级：高）
- 中国国内航司「以拥挤著称」的量化排行——缺少把 pitch/座宽/座位数与乘客口碑结合的权威测评（如 Skytrax 座位评分、中国民航局客舱标准文件），目前只能由单机布局数据间接推断（优先级：高）
- AeroLOPA 与 SeatMaps 对同一机型给出的 pitch 数值是否一致（本次未做同机型双源比对，无法评估这两个替代源之间的偏差幅度）（优先级：中）
- SeatGuru 历史数据是否可通过 Internet Archive Wayback Machine 完整取回，若可，哪些中国航司机型有遗留页面可用于 pitch 交叉校验（优先级：中）
- 国内线与洲际线 pitch 差异的量化分布：南航 A320(320) 国际线 30-39 英寸的跨度远大于一般认知，是否在国内线另行标注（中文页 A320 国内线标 30 英寸），需要对国航/东航做同类国内/国际对照（优先级：中）
- AeroLOPA 的 208 家航司是否覆盖中国三大航与主要廉航（本次只确认了总量数字，未核实国航/东航/春秋/九元的具体覆盖与数据新鲜度）（优先级：低）
- 可编程替代源 airLabs「Airplane Seat Configuration API」提供 seat pitch/width 结构化数据，但其计费与覆盖范围未验证，作为批量取数的可行性未评估（优先级：低）

---

## 值机与附加收费项：各廉航值机收费规则（如瑞安未在线值机的处理）、选座费、行李预购与机场购买差价、其他常见"隐藏收费"清单

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 瑞安航空对"未在起飞前 2 小时以上完成网上值机"的旅客收取机场值机手续费（2026 年英国媒体口径为每人每航班 £30–£55），这是欧洲廉航把自助值机变成硬性收费项的典型机制。（E106 · 置信度：中 · 类型：官方 · 时点：2026-08-30，来源：https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564）
  - 数字：机场值机费（每人每航班，媒体口径） = £55（2026）；机场值机费区间（另一媒体口径） = £30–£55（2026）；值机柜台关闭时点 = 起飞前 40 分钟（2026-11-10 前）；值机柜台关闭时点（新规） = 起飞前 60 分钟（2026-11-10 起）
- 瑞安航空自 2025-11-12 起全面数字化登机牌：机场不再接受纸质登机牌；已完成网上值机但手机没电/丢失/无法出示登机牌的旅客可免费补打，但未完成值机者仍照收机场值机费。（E107 · 置信度：中 · 类型：官方 · 时点：2026-06-25，来源：https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564）
  - 数字：全面数字化登机牌生效日 = 2025-11-12（2025）
- 瑞安航空值机柜台现行于起飞前 40 分钟关闭，官方已宣布 2026-11-10 起统一提前至 60 分钟；逾时未值机可被拒绝登机且不退款。（E108 · 置信度：中 · 类型：官方 · 时点：2026-08-02，来源：https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564）
  - 数字：值机截止提前量（新规） = 60 分钟（2026-11-10 起）
- 瑞安航空要求第三方中介订单的旅客做证件自拍＋活体核验的"快速验证"，需支付 €0.59；未在线验证而改到机场售票处完成的，官方明确"乘客将被收取机场值机手续费"——即通过 OTA/代理购票的旅客被额外推入收费漏斗。（E109 · 置信度：中 · 类型：官方 · 时点：2026-06-25，来源：https://www.ryanair.com/cn/zh/useful-info/help-centre/terms-and-conditions/termsandconditionsar_1379164564）
  - 数字：快速验证费用 = €0.59（2026）；机场完成验证的最后时点 = 出发前 60 分钟（2026）
- 瑞安航空托运行李"提前决策 vs 迟到决策"的价差结构：20kg 托运箱订票时加购 £21.49 起，订票后线上加购 £39.99 起，而到 bag drop 柜台是统一 £59.99；10kg 托运箱柜台固定 £35.99；23kg 箱柜台无公开价。超重按每公斤 £13 另加；把 10kg 箱带到登机口收费 £46–75，把超规手提箱带到登机口收费 £70–75。（E110 · 置信度：中 · 类型：媒体 · 时点：2026-09-01，来源：https://flighttribe.co.uk/ryanair-baggage-allowance/）
  - 数字：20kg 托运箱订票加购价（最低） = £21.49（2026-09）；20kg 托运箱 bag drop 柜台统一价 = £59.99（2026-09）；20kg 托运箱订票后线上加购价（最低） = £39.99（2026-09）；10kg 托运箱柜台固定价 = £35.99（2026-09）；托运超重费 = £13/公斤（2026-09）；登机口托运 10kg 箱 = £46–75（2026-09）；登机口托运超规手提箱 = £70–75（2026-09）
- 瑞安航空多类"特殊行李"同样遵循线上/柜台两套价：婴儿费 £25/人/单程；婴儿额外行李提前买 £15、之后 £20；自行车与乐器订票 £60、机场 £75；滑雪装备 £45→£50；高尔夫球具 £40→£50；且所有行李一经购买不可退。（E111 · 置信度：中 · 类型：媒体 · 时点：2026-09-01，来源：https://flighttribe.co.uk/ryanair-baggage-allowance/）
  - 数字：婴儿票费用 = £25/人/单程（2026-09）；婴儿额外行李（提前/之后） = £15 / £20（2026-09）；自行车/乐器（订票/机场） = £60 / £75（2026-09）；滑雪装备（订票/机场） = £45 / £50（2026-09）
- 瑞安航空"机场值机费"受出发地当地法规上限约束：其费用表显示英国出发 £55，但西班牙出发为 £30、奥地利出发为 €40——说明该费用并非全球统一价，而是可被当地消费者法规封顶的定价项。（E112 · 置信度：中 · 类型：媒体 · 时点：2026-09-01，来源：https://flighttribe.co.uk/ryanair-baggage-allowance/）
  - 数字：西班牙出发机场值机费 = £30（2026-09）；奥地利出发机场值机费 = €40（2026-09）
- 春秋航空官网直接公布选座"柜台 / 网上 / B2B"三档价目表（国内航线除上海—乌鲁木齐往返）：第1、2排 柜台 70 元 / 网上 50 元；第3–11排 40 / 35；14–16排 40 / 20；第12–13排 60 元仅柜台销售；第17–24排与第25–30排柜台"不销售"、仅网上 10 元 / 5 元。官网明示"网上价格比机场柜台最低优惠5折"且"机场柜台概不参加"，同时"网上选座不含优先登机服务"。（E113 · 置信度：中 · 类型：官方 · 时点：2026，来源：https://jp.ch.com/choose-seats）
  - 数字：国内线第1、2排（柜台/网上） = 70 / 50 元（2026）；国内线第3–11排（柜台/网上） = 40 / 35 元（2026）；国内线第14–16排（柜台/网上） = 40 / 20 元（2026）；国内线第17–24排 网上价 = 10 元（2026）；国内线第25–30排 网上价 = 5 元（2026）；官网自述最大优惠幅度 = 5 折（2026）
- 春秋航空日本国内线选座同样"网上/客服 vs 机场柜台"两档定价且整档上调：2026-12-20 前乘机，第1排舒适座 1,200/1,500 日元、第2–3排宽敞座 900/1,200、第16–17排紧急出口 900/1,200、普通座 500/800；2026-12-21 起涨至 1,500/1,900、1,200/1,600、800/1,200（日元）。官网并规定网上选座截止起飞前 6 小时、1 位乘客仅可提前选座 1 次、机场购买可用当地币种、改签后座位失效且选座费不退。（E114 · 置信度：中 · 类型：官方 · 时点：2026-09-18，来源：https://flights.ch.com/ij-seat-rule?GAT=0&t_id=3&m_id=1）
  - 数字：第1排舒适座（网上/柜台，2026-12-20 前） = 1,200 / 1,500 日元（2026-12-21 前）；普通座（网上/柜台，2026-12-20 前） = 500 / 800 日元（2026-12-21 前）；普通座（网上/柜台，2026-12-21 起） = 800 / 1,200 日元（2026-12-21 起）；网上选座截止时点 = 起飞前 6 小时（2026）
- 春秋航空托运行李官方明码标价"网上优惠价"与"机场柜台价"两套体系，且差价随重量档位与航距急剧放大：国内线航距 3000KM 及以上时 20KG 网上 179 元 vs 柜台 420 元、40KG 网上 339 元 vs 柜台 840 元；国际线航距 3000KM 及以上 40KG 网上 499 元 vs 柜台 1320 元。官网自 2026-08-16 起国内与国际线网价改用"曲线定价（阶梯定价）"，线上购行李统一截止于计划起飞前 1 小时。（E115 · 置信度：中 · 类型：官方 · 时点：2026-08-18，来源：https://news.ch.com/news/2026-06-16-00-00.html）
  - 数字：国内线 3000KM+ 20KG（网上/柜台） = 179 / 420 元（2026-08）；国内线 3000KM+ 40KG（网上/柜台） = 339 / 840 元（2026-08）；国际线 3000KM+ 40KG（网上/柜台） = 499 / 1320 元（2026-08）；线上购行李截止时点 = 计划起飞前 1 小时（2026）
- 春秋航空 2026-03-29 起对国内线（含港澳台）线上托运行李按航距四档（0-999/1000-1999/2000-2999/3000+KM）定价并新增 30/40/50KG 档位，但机场柜台同期最高收至 840 元（3000KM+ 40KG），即线网上调档并未同步压低柜台价。（E116 · 置信度：中 · 类型：官方 · 时点：2026-03-27，来源：https://www.ch.com/News/09931f418e51475d9bdee6c598343199.Html）
  - 数字：国内线线上 5KG 档（最短航距→3000KM+） = 50 → 65 元（2026-03-29）；国内线线上 40KG 档（最短航距→3000KM+） = 180 → 300 元（2026-03-29）
- 春秋航空日本线逾重行李是"官网/呼叫中心 / 机场柜台 / 登机口"三档定价，登机口最贵（20kg 依次为 3,000 / 6,000 / 7,000 日元；25kg 为 3,750 / 7,500 / 8,500 日元），30kg 以上按 500 日元/公斤且官网一律"不接受办理"；官网线上仅支持信用卡支付、提前购买仅限 1 次且须在起飞 2 小时前完成、已付款一律不退。（E117 · 置信度：中 · 类型：官方 · 时点：2026-09-18，来源：https://flights.ch.com/ij-extra-baggage?t_id=3）
  - 数字：日本线 20kg（官网/柜台/登机口） = 3,000 / 6,000 / 7,000 日元（2026-12-20 前）；超 30kg 部分（柜台/登机口） = 500 日元/公斤（2026）
- 与瑞安形成直接对照：春秋航空官方《网上值机相关规定》全文没有任何"值机收费"条款——未网上值机只是须到柜台办理，且婴儿旅客、特殊旅客、12 周岁以下儿童及同行旅客、选择安全出口座位的旅客本就被排除在网值机之外（安全出口座位须柜台评估后办理，而该座位本身是付费项）；官网并明示"登机口处无法办理托运"，对系统分配座位或需纸质登机牌者须于起飞前 60 分钟到柜台重办。（E118 · 置信度：中 · 类型：官方 · 时点：2026，来源：https://www.ch.com/Default/CheckInAttention）
  - 数字：登机口关闭时点 = 计划起飞前 15 分钟（2026）；柜台重办值机时点 = 起飞前 60 分钟（2026）
- 春秋航空另一项易被忽略的隐形成本是"升级手提行李"：因免费手提上限仅 20×30×40cm，20 寸登机箱需单独付费升级，官网定价国内线（含港澳台）159 元、国际线 219 元，升级后尺寸放宽至 20×40×55cm、重量放宽至 10KG，且限量销售售罄为止；不符合规格的手提行李会在值机柜台被直接转为托运行李。（E119 · 置信度：中 · 类型：官方 · 时点：2026，来源：https://flights.ch.com/baggage-rule?GAT=0）
  - 数字：升级手提行李价（国内/国际） = 159 / 219 元（2026）
- 九元航空 2025-07 起对部分国际航线（沈阳=济州、广州=清迈、广州=胡志明、上海浦东=福冈/名古屋等）上调线上托运行李价，5KG/10KG/20KG/30KG/40KG 依次为 109/198/359/499/599 元人民币，销售与航班生效日分别为 2025-07-03 与 2025-07-07。（E120 · 置信度：中 · 类型：官方 · 时点：2025-07-02，来源：https://www.ch.com/News/fec79a01f5a24355a84a5c309fd3a545.html）
  - 数字：9C 国际线线上托运 5KG/10KG/20KG/30KG/40KG = 109 / 198 / 359 / 499 / 599 元（2025-07）
- 瑞安航空五档票价包中只有两档含免费托运，且最贵的 Flexi Plus 反而不含：Basic 与 Flexi Plus 货舱为空，Regular 也为空；Plus 含 1 件 20kg 托运箱，Family Plus 为每名旅客 1 件 10kg 加 1 件 20kg 家庭箱。媒体并指出 Regular→Plus 不是升级而是取舍（得到 20kg 托运，失去 10kg 随身箱与优先登机）。（E121 · 置信度：中 · 类型：媒体 · 时点：2026-08-19，来源：https://flighttribe.co.uk/ryanair-baggage-allowance/）
### 不确定项
- 瑞安机场值机费到底是统一 £55，还是 £30–£55 浮动区间（原因：两个 2026 年媒体来源口径不同：flighttribe（更新至 2026-08-30）称 £55/人/航班，express（2026-08-02）称 £30–£55 区间；另一来源又给出西班牙 £30 / 奥地利 €40。可能因航线、出发地法规上限或 fare 类型（2025-08-14 前购买的 Plus/Flexi Plus 可免费机场值机）而异，未取得一手 Table of Fees 逐条核对。）
- 已在线值机后补打纸质登机牌是否仍收约 €20（原因：flighttribe 称"已网上值机但需重打登机牌，收费较低，通常约 €20"；但瑞安官方 DBP 页面与官方 T&C 6.3 均称只要已在抵达机场前完成网上值机即不产生补发费、免费补打。可能是旧政策残留、特定航线例外或该来源表述不准确。）
- 春秋"网上价格比机场柜台最低优惠 5 折"的适用范围（原因：官网产品说明如此概括，但同页价目表中第1、2排为 50 vs 70（约 7.1 折）、第3–11排 35 vs 40（8.75 折），只有第14–16排 20 vs 40 恰为 5 折。"最低优惠 5 折"应指最优档位而非普遍折扣，易被误读为全线五折。）
- 中联航/西部航空/国航/南航/东航/海航等国内航司的现行付费选座价目（原因：只检索到一篇郑州晚报（新浪转载）旧稿列举春秋、西部、中联航、国航、东航、南航、海航的选座分档价，但该稿以"今年5月南航上线付费选座"为时间锚点，实为 2015–2016 年内容，与官网现行价目细节不一致，仅可作历史参照，不能作为现行结论。）
### 信息缺口（优先级）
- 瑞安航空一手 Table of Fees 原页：help.ryanair.com 全站被 Cloudflare 拦截（HTTP 403），未取得官方价目表逐条原文，所有瑞安价格目前依赖转述该表的媒体/博客（优先级：高）
- 春秋航空逐机场值机截止时间表（flights.ch.com/transact-checkin-procedure-deadline）抓取超时未取得，无法给出国内各机场值机截止差异（优先级：中）
- 春秋国内线"登机口"第三档行李价：官网只公布网上/柜台两档且明示"登机口处无法办理托运"，但逾重行李在登机口如何处理（按柜台价、按登机口价或直接拒运）无官方说明（优先级：中）
- 九元航空、西部航空、中联航、乌鲁木齐航空的官方选座费价目表与"网上/柜台"差价（一手官网来源）（优先级：中）
- 全服务航司（国航/南航/东航/海航/川航/厦航）现行付费选座价目与选座费差额（优先级：中）
- 易捷、亚航、靖蓝、Wizz 等其余全球头部廉航的值机费/选座费/行李线上-机场差价具体价目（优先级：中）
- “隐藏收费”的第三方权威量化口径（欧盟委员会/英国 CMA/美国 FTC 或行业协会对 ancillary 收入占比的统计）；本轮检索到的均为营销博客清单，未取得 A/B 级统计（优先级：中）
- 信用卡/第三方支付手续费（DCC 动态货币转换）、OTA 捆绑保险、代理服务费等外围收费项的具体金额与规则（优先级：低）

---

## 国内线经济舱座椅间距（seat pitch）：八家航司 A320/737/A321 窄体机经济舱 76–80cm 级别的逐机型数据完全缺失，无任何一手或二手可引用来源

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 中国国内航司中只有南方航空（南航）在其官网设有「机舱布局 / Cabin Layout」逐机型一手数据页，逐机型公布座位总数、各舱位座位数、座位间距（英寸）、扶手间座椅宽度（英寸）与靠背后倾距离（英寸），并按子型号（A320(320)、A320(32X)、A321(321)、A321NEO(32N)、B737-800(73K/73N/738)）分页；这直接填补了上一轮「国内线窄体机逐机型座椅间距无任何可引用来源」的高优先级缺口。（E122 · 置信度：高 · 类型：官方，来源：https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idksocbjvnb.shtml）
- 南航 A320(320) 国内线为 152 座（公务舱 8 / 明珠经济舱 24 / 经济舱 120）：香港繁体官网页列经济舱座位间距 30 英寸、座椅宽度 17.7 英寸、后倾 6 英寸（约合 76 厘米）；但同一机型的新加坡英文官网页把经济舱间距写成 39/36/35/33/31/30 英寸的多档值（最高一档约合 99 厘米）。同一航司同一机型在不同地区镜像页给出两种粒度，说明「逐机型」之下还须区分子批次/分舱排距。（E123 · 置信度：中 · 类型：官方，来源：https://www.csair.com/hk/tc/tourguide/flight_service/cabin_layout/kongke/18h1tllaukv3c.shtml）
  - 数字：经济舱座位间距 = 30 英寸；经济舱座椅宽度 = 17.7 英寸；座位总数 = 152
- 南航 A320(32X) 存在 180 座全经济舱（单一舱位）高密度子变体，官方给出的座椅间距为 28/29/36 英寸、扶手间座椅宽度 19.07/19.39/20.75 英寸——其中 28–29 英寸仅约合 71–74 厘米，明显低于「国内线经济舱 76–80 厘米」这一常见概括，说明该概括只对部分子变体成立。（E124 · 置信度：中 · 类型：官方，来源：https://csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/1hh7mef56t4pp.shtml）
  - 数字：座位总数 = 180；经济舱座位间距 = 28/29/36 英寸；扶手间座椅宽度 = 19.07/19.39/20.75 英寸
- 南航 A321(321) 为 179 座（公务舱 12 / 明珠经济舱 24 / 经济舱 143），经济舱座椅间距官方公布为 31/43 英寸、座椅宽 17.8 英寸、后倾 4.5 英寸；常规排位约合 79 厘米。（E125 · 置信度：中 · 类型：官方，来源：https://www.csair.com/sg/en/tourguide/flight_service/cabin_layout/kongke/18idkvmedtkic.shtml）
  - 数字：座位总数 = 179；经济舱座位数 = 143；经济舱座位间距 = 31/43 英寸；经济舱座椅宽度 = 17.8 英寸
- 东航 A320neo 在 SeatMaps 口径下有两种布局（8 商务 + 150 经济 = 158 座；8 商务 + 156 经济 = 164 座），经济舱座椅间距 30–31 英寸（76–79 厘米）、宽度 17.3 英寸、后倾 4.5 英寸；同页还给出「国内航线经济舱间距通常在 27–32 英寸（68.5–81 厘米）」的行业区间。（E126 · 置信度：中 · 类型：媒体，来源：https://www.seatmaps.com/zh-TW/airlines/mu-china-eastern/airbus-a320neo）
  - 数字：经济舱座椅间距 = 30-31 英寸（76-79 厘米）；经济舱座椅宽度 = 17.3 英寸；国内航线经济舱间距区间 = 68.5-81 厘米
- 东航 737-800 在 SeatMaps 口径下共 5 种布局版本，公务舱 8–20 座、经济舱 138–168 座（合计 158–176 座不等），各版本经济舱间距落在 30–32 英寸之间，座椅宽度 17–17.1 英寸、后倾 3–4.5 英寸——即同一机型内部版本差异大于航司之间的差异。（E127 · 置信度：中 · 类型：媒体，来源：https://seatmaps.com/zh-CN/airlines/mu-china-eastern/boeing-737-800）
  - 数字：737-800 布局版本数 = 5 个型号；公务舱座位数区间 = 8-20 个座位；经济舱座位数区间 = 138-168 个座位
- 国航 A320-200 为单一配置 8 商务 + 150 经济 = 158 座，SeatMaps 口径下经济舱座椅间距 30 英寸、宽度 17.7 英寸、后倾 3–5 英寸；国航 A321-200 有两个版本（12 商务 + 173 经济 = 185 座；16 商务 + 161 经济 = 177 座），两版经济舱腿部空间均标注 76–81 厘米、座椅宽 45 厘米。（E128 · 置信度：中 · 类型：媒体，来源：https://seatmaps.com/zh-CN/airlines/ca-air-china/airbus-a320）
  - 数字：A320-200 经济舱座椅间距 = 30 英寸；A320-200 经济舱座椅宽度 = 17.7 英寸；A321-200 经济舱腿部空间 = 76-81 cm；A321-200 经济舱座椅宽度 = 45 cm
- 厦航官网设有「座位布局图」页面，但只以图片形式提供 737-700、737-800、737-8、787-8、787-9、A321NEO 六种机型的座位布局图，不提供任何文本形式的座椅间距数值；因此厦航的国内线经济舱间距目前无法取得一手可引用数据。（E129 · 置信度：中 · 类型：官方，来源：https://www.xiamenair.com/brandnew_CN/travel-cabin-seat.html）
- SeatMaps 对中国航司窄体机的间距数据采用的是自建座位图库 + 乘客提交评测量化口径（页面同时给出总体评分与分档评分数），不是航空公司官方公布值；因此国航/东航的间距数据在证据等级上应低于南航官网数据。（E130 · 置信度：中 · 类型：媒体，来源：https://seatmaps.com/zh-CN/airlines/ca-air-china/airbus-a321）
  - 数字：A321-200 V.1 总体评分 = 4.24(409)；737-800 V.3 总体评分 = 4.21(445)
### 不确定项
- 「国内线全服务航司经济舱座椅间距 31–32 英寸（79–81 厘米）」这一媒体口径与一手/垂直站数据存在张力（原因：多个 2026-09 新浪系聚合稿件称东航/国航/南航经济舱间距 31–32 英寸或「东航A320 79–81 厘米」，但南航官网一手数据显示同机型子变体实际为 28/29/30/31/36/39 英寸不等；聚合稿件未说明机型与子批次，泛化过度。）
- 南航 A320(320) 官方两个地区镜像页的间距口径不一致（30 英寸 vs 39/36/35/33/31/30 英寸）（原因：无法判定是不同子批次、不同页面更新时间，还是一个页面按排位细分、另一个只给代表值；未找到官方说明其口径差异的页面。）
- 南航 A321NEO(32N) 195 座（4J/24PE/167Y）经济舱 29–30 英寸、座椅宽 17 英寸这一组数值（原因：该数值出现在搜索结果对 csair.com 页面（/us/zh/ 与 /au/zh/ 两个镜像）的抽取摘要中，但三次抓取该页正文均只返回站点模板文字，未取得完整表格原文，故仅作线索不作定论。）
- 国航官网「机型介绍、驾驶舱、载客量」页是否以文本形式公布座椅间距（原因：该页抓取仅返回页脚与版权信息（正文疑似 JS 渲染），无法判断页面本身是否含间距数据；不能据此断言国航官网没有间距数据。）
### 信息缺口（优先级）
- 川航（3U）、吉祥（HO）、深圳航空（ZH）、海航（HU）、祥鹏（8L）国内线 A320/737-800/A321 经济舱座椅间距的逐机型数值仍无任何可引用来源；本轮仅确认 SeatMaps 存在深航 737-800 / 川航 A320·A321·737-800 页面，但间距数值未取得（抓取结果被站点页脚与导航列表淹没，数值落在超长溢出文件中未能读取）（优先级：高）
- 东航（MU）官网是否存在类似南航「机舱布局」的逐机型一手间距页——本轮两轮检索（含中文站内关键词组合）均未命中，可能是本次「八家航司逐机型数据」缺口的最后一块拼图（优先级：高）
- 国航（CA）官网机型介绍页的实际正文内容（是否含经济舱座位间距/载客量表格）尚未取得，页面为 JS 渲染需换用可执行 JS 的抓取通道（优先级：中）
- SeatMaps 间距数值的测量方法与数据采集方式未公开说明（页面只声明「所有提交内容均经过验证」），无法判断 30/31/32 英寸是实测还是按座椅图推算（优先级：中）
- 南航 A321NEO(32N)、B737-800(73K/73N/738)、A321(32Y) 等其余子变体页的完整表格原文（页面被反爬模板覆盖），其中搜索摘要显示 B737-800 布局 A 为 164 座、经济舱间距 31 英寸、座椅宽 17.2 英寸，尚未取得正文逐字确认（优先级：中）

---

## 海航（HU）国内线免费托运额度、手提行李重量与尺寸、免费餐食政策的官方现行条款

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 海南航空（HU）国内航线免费托运行李为计重制：公务舱30公斤、经济舱20公斤（44磅），儿童等同成人，不占座婴儿无免费行李额但可免费托运一辆折叠婴儿手推车；金鹏白金卡/金卡会员在客票额度上额外+30公斤、银卡会员额外+20公斤。每件托运行李重量不得小于2公斤、不得超过50公斤，体积须大于或等于5×15×20cm且小于或等于40×60×100cm。（E131 · 置信度：中 · 类型：官方 · 时点：2026-01，来源：https://www.hnair.com/lvxingxinxi/xlxx/mftyxl/）
  - 数字：国内航线公务舱免费托运行李额 = 30公斤（66磅）（2026-01）；国内航线经济舱免费托运行李额 = 20公斤（44磅）（2026-01）；单件托运行李最大体积（三边） = 40×60×100cm（2026-01）
- 海南航空国内航班手提（非托运）行李标准：经济舱限1件、公务舱限2件，单件重量不超过7公斤（15磅），单件长宽高分别不超过55×40×20厘米（含滑轮和把手）；除手提行李外还可免费携带少量零星小件（参考尺寸30×30×20厘米，须能放置于前排座椅下方）。超规行李海航有权拒绝带入客舱，且临时转托运可能无法与旅客同机到达。（E132 · 置信度：中 · 类型：官方 · 时点：2026-01，来源：https://www.hnair.com/guanyuhaihang/hhdt/hhgg/cxts/cxts2024/202401/t20240124_64240.html）
  - 数字：国内经济舱手提行李件数上限 = 1件（2024-01）；手提行李单件重量上限 = 7千克（15磅）（2024-01）；手提行李单件尺寸上限 = 55厘米×40厘米×20厘米（2024-01）
- 海南航空国内线超限行李费按每公斤相当于超限行李票填开当日经济舱普通票价（全票价）的1.5%计收；航司禁止在登机口办理行李托运（婴儿车、助残设备除外），登机口发现超限手提行李可能无法与旅客同航班运输，官网未见国内线针对该项的明确收费标准。（E133 · 置信度：中 · 类型：官方 · 时点：2026-01，来源：https://www.hnair.com/lvxingxinxi/cxzb/ysztj/2017gnysztj/202601/t20260125_82769.html）
  - 数字：国内线超限行李费率（每公斤占经济舱全票价比例） = 1.5%（2026-01）
- 海南航空国内线因海航原因造成托运行李未同机到达时，提供一次性临时生活用品补偿：经济舱旅客人民币100元/每晚、公务舱旅客人民币500元/每晚，最多不超过两晚。（E134 · 置信度：中 · 类型：官方 · 时点：2026-01，来源：https://www.hnair.com/lvxingxinxi/cxzb/ysztj/2017gnysztj/202601/t20260125_82769.html）
  - 数字：经济舱行李延误临时补偿标准 = 人民币100元/每晚（2026-01）；公务舱行李延误临时补偿标准 = 人民币500元/每晚（2026-01）
- 海南航空官网明确其国内配餐航班仍提供免费餐食：加购付费餐食时免费餐食继续提供，旅客也可选择“餐食兑换积分”放弃免费餐食换取消费积分（最高600积分，须在航班计划起飞前4小时前预订，成功兑换后机上仅提供饮品）。付费“餐食升级”适用于北京、海口、杭州、厦门、西安部分出港航线的880票证海航实际承运航班，经济舱加购折后价22–118元、公务舱98元，须在起飞前至少24小时预订。（E135 · 置信度：中 · 类型：官方 · 时点：2025-04，来源：https://www.hnair.com/dachenghaihang/kongzhong/canshi/cssj/202504/t20250408_75160.html）
  - 数字：餐食兑换积分最高可得积分 = 600积分（2025-04）；餐食兑换积分预订截止 = 航班计划起飞时间前4小时（2025-04）；餐食升级加购预订时限 = 航班起飞前至少24小时（含）（2025-04）
### 不确定项
- 携程转载版《海南航空控股股份有限公司旅客、行李国内运输总条件》称“公务舱手提行李每件重量不超过5公斤”，与海航官网2024年提示及2026年1月版总条件的7公斤不一致。（原因：该第三方页面无版本与生效日期，正文明显对应旧版条款，应以官网现行文本（7公斤）为准，不宜作现行依据引用。）
- 海航官网《免费托运行李》页面中，国内航线额度表格本身未标注生效日期（仅国际及地区航线部分标注“自2026年9月2日起执行”）。（原因：国内额度20/30公斤只能靠2026年1月25日发布的《国内运输总条件》12.6条佐证其现行性，无法确认国内表格最近一次修订时间是否晚于2026年1月。）
- 海航“超级经济舱”及国内优惠运价产品是否有独立于公务/经济两档的免费行李额与手提行李件数标准。（原因：国内运输总条件仅列公务舱与经济舱两档，并约定“优惠运价或产品的免费行李额可能与上述标准不一致，具体标准在官网公告并在购票时告知”，但官网未检索到国内线分舱位对照表（对比：天津航空官网则明确列有V/N/A/U/T舱0千克）。）
### 信息缺口（优先级）
- 哪些具体国内航班属于“配餐航班”（免费餐食适用范围）：官网只写“部分站点出港航班”提供海南风味热食与“国内所有配餐航班”，未给出机型、航段时长或里程的判定阈值（优先级：中）
- 海航国内线手提行李超规在值机柜台/登机口的实际处理与收费（是否收费、收费金额），官网总条件只写“有权拒绝超规行李上机”，未列国内线标准（优先级：中）
- 海航国内经济舱餐食的菜单与供餐频次（短航线的海南鸡饭/海南粉是否为常态化免费正餐、长航线“两餐以上”的适用航线范围）（优先级：低）
- 海航国内线预付费行李（提前加购行李额）的档位、价格与购买时限——官网仅有“飞行+预付费行李”入口，未见国内线规则页正文（对比：天津航空官网给出5–40kg档位与起飞前60分钟截止规则）（优先级：中）

---

## 吉祥航空（HO）国内线免费托运与手提行李官方条款（官网页面为 JS 渲染，需换 URL 形态或 PDF 版《行李运输规定》）

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 吉祥航空国内航线免费托运行李执行计重制：公务舱（J/C/D/A/R/I）30公斤，普通经济舱20公斤，儿童（含占座婴儿）等同对应成人舱位（公务30/经济20），不占座婴儿0公斤，中转联程舱（G/K）20公斤；托运行李每件最大重量不得超过50千克、体积不超过40×60×100厘米。（E136 · 置信度：中 · 类型：官方 · 时点：2025-08，来源：https://staticb2c.juneyaoair.com/ad/202310/cd005a0f82e5438fab98b23a6c16259a_20231012034442.pdf）
  - 数字：国内公务舱免费托运行李额 = 30公斤；国内普通经济舱免费托运行李额 = 20公斤；托运行李单件最大重量 = 50千克
- 现行《行李运输规定》（2025年8月8日生效版）手提（非托运）行李标准：公务舱2件、每件≤8公斤；经济舱1件、每件≤5公斤；每件长宽高分别≤55/40/20厘米且三边之和≤115厘米（含滑轮把手）；除手提行李外还可免费携带1件置于前排座椅下的随身物品（手提包、电脑包等）。（E137 · 置信度：高 · 类型：官方 · 时点：2025-08，来源：https://meiyacommonfile.oss-cn-shenzhen.aliyuncs.com/policy/content41e1c91754449120477.pdf）
  - 数字：手提行李每件重量上限（经济舱） = 5公斤；手提行李每件重量上限（公务舱） = 8公斤；手提行李尺寸限制 = 55×40×20厘米
- 吉祥航空行李规定版本沿革：2023年10月13日生效版规定国内经济舱手提1件≤10千克（公务舱2件≤10千克，尺寸20×40×55厘米）；该版废止后现行版为2025年8月8日生效版本（同时废止2025年1月13日版），即手提重量已由10千克收紧至经济舱5公斤/公务舱8公斤。（E138 · 置信度：高 · 类型：官方 · 时点：2025-08，来源：https://staticb2c.juneyaoair.com/ad/202310/cd005a0f82e5438fab98b23a6c16259a_20231012034442.pdf）
  - 数字：国内经济舱手提行李重量上限（2023年版） = 10千克（2023-10至2025-08）；现行版生效日期 = 2025年8月8日（2025-08）
- 逾重行李费（国内）：2023年10月版按航距定价（0-999公里12元/千克、1000-1999公里15元/千克、2000公里及以上20元/千克）；2025年8月版改为按航班当日适用的成人经济舱单程最高直达票价的1.5%计算每千克单价。（E139 · 置信度：中 · 类型：官方 · 时点：2025-08，来源：https://staticb2c.juneyaoair.com/ad/202310/cd005a0f82e5438fab98b23a6c16259a_20231012034442.pdf）
  - 数字：逾重行李每千克单价（2025年8月版） = 当日成人经济舱单程最高直达票价的1.5%（2025-08起）；逾重行李费（2023年版，0-999公里） = 12元/千克（2023-10至2025-08）
- 吉祥航空2022年6月10日起在国内航线推出低碳经济舱票价产品：票价为普通经济舱四折及以下散客折扣舱位，含免费机上餐食饮品和1件≤10公斤手提行李额、无免费托运行李额；2023年10月版行李规定将其对应K/L舱位免费托运额定为0KG。（E140 · 置信度：中 · 类型：媒体 · 时点：2022-06，来源：https://staticb2c.juneyaoair.com/ad/202310/cd005a0f82e5438fab98b23a6c16259a_20231012034442.pdf）
  - 数字：低碳经济舱免费托运行李额 = 0KG（2023-10版）；低碳经济舱手提行李额 = 1件不超过10公斤（2022-06）
### 不确定项
- 携程镜像的官方《关于吉祥航空调整随身携带行李限额的通知》显示手提重量曾由5KG上调至10KG（通知未标注日期，推测为2023年10月版生效前后的旧公告），说明该数值存在被官方再次调整的先例（原因：通知时点不明，无法100%排除2025年8月8日之后又有回调；但sha163聚合页2026-05-29核验仍为8/5kg标准，两者相互印证现行版未变）
- 2025年8月版已不再单列"低碳经济舱（K/L舱0KG）"行，L舱并入普通经济舱20KG、K舱列入中转联程舱G/K 20KG，低碳经济舱票价产品2025年8月后是否仍在售不明（原因：仅凭行李规定表格结构变化推断，无直接产品公告佐证）
- Traveloka等第三方页面称吉祥航空手提行李10公斤上限，可能是2023年10月至2025年8月之间的旧标准未更新（原因：该类来源未随官网PDF版本更新，与现行5公斤标准存在时间差张力）
### 信息缺口（优先级）
- 吉祥航空官网在线行李页（JS渲染）的现行表格数值未能从活页直接读取，若需最高等级核验需浏览器渲染访问 baggage-free/baggage-personal 页（优先级：低）
- 吉祥航空国内线餐食、座椅间距等服务体验数据不属于本子问题，留给对应子问题的研究员（优先级：低）

---

## 深航（ZH）国内线随身行李官方重量/尺寸数值（官网页面抓取失败）

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 深圳航空（ZH）国内线经济舱旅客随身（非托运行李）官方标准为：限带 1 件、单件重量不超过 5 公斤（11 磅）、长宽高分别不超过 55 厘米（22 英寸）×40 厘米（16 英寸）×20 厘米（8 英寸）（含滑轮和把手），且须能放入客舱上方封闭式行李架内或前排座椅下；除该件外另可免费携带 1 件不占用行李架、可放置于前排座椅下方的随身物品（参考尺寸长宽高分别不超过 12cm×35cm×40cm）。经济舱与舒适经济舱／超级经济舱适用同一标准。（E141 · 置信度：中 · 类型：官方 · 时点：2026-09-21，来源：https://mobile.shenzhenair.com/file/internalInformation.html）
  - 数字：经济舱／舒适经济舱／超级经济舱非托运行单单件重量上限 = 5公斤或11磅；非托运行李长宽高上限 = 55厘米（22英寸）、40厘米（16英寸）、20厘米（8英寸）；经济舱非托运行李件数上限 = 1件；座椅下随身物品参考尺寸 = 长、宽、高分别不超过12cm×35cm×40cm
- 深圳航空现行官方口径下，公务舱／头等舱旅客随身行李为 2 件、单件不超过 8 公斤（17 磅），明显宽于经济舱的 1 件 5 公斤；深航官网 Baggage Services 页面与《旅客、行李运输总条件》在该数值上完全一致。该总条件为 2026 年 9 月修订版，自 2026 年 09 月 21 日起生效并施行，同时废止 2026 年 07 月 01 日公布的上一版。（E142 · 置信度：高 · 类型：官方 · 时点：2026-09-21，来源：https://mobile.shenzhenair.com/file/internalInformation.html）
  - 数字：公务舱／头等舱非托运行单单件重量上限 = 8公斤或17磅；公务舱／头等舱非托运行李件数上限 = 2件；总条件版本生效日 = 2026年09月21日；被同时废止的上一版总条件施行日 = 2026年07月01日
- 深航对超规随身行李的实际处置是「转托运 + 二次安检」，并明确告知后果：登机口临时办理托运的行李必须经过二次安全检查，可能导致行李不能同机抵达、旅客须自行前往目的机场提取；官方反复要求旅客提前到值机柜台办理托运。安检口将严格查验手提行李件数及规格。（E143 · 置信度：高 · 类型：官方 · 时点：2024-01-15，来源：https://www.shenzhenair.com/szair_B2C/getMsgInfo.action?msgId=8a8ecf0b8d0aab8e018d0ae55ac400de）
### 不确定项
- 深航官网存在两处遗留页面把公务舱随身行李单件重量写成 5kg（2024-01-15《深航关于携带随身行李登机注意事项的公告》表格、以及深航「行李服务」FAQ 页），与现行《旅客、行李运输总条件》及现行 Baggage Services 页面的 8kg 不一致；公务舱到底执行 5kg 还是 8kg 未被明确裁决。（原因：倾向于 8kg 为现行值——总条件为最新且现行服务页与之一致，而 5kg 表述出自 2024 年公告与无日期的遗留 FAQ。但总条件 1.1.2 款写有「就本条件所列事项变化较频繁的，深航可能单独制定相关规定……该单独制定的规定与本条件内容不一致的，该单独制定的规定优先于本条件」，若 2024 公告被视作「单独制定的规定」，理论上可覆盖总条件；未找到深航对此的官方澄清或废止声明，故不能排除执行层面仍有 5kg 遗留口径。经济舱 5kg 无争议，仅公务舱存在张力。）
- 深航托运行李规则与其他中国全服务航司体系不同：《旅客、行李运输总条件》6.2.2.2 规定普通托运行李按体积制（三边之和不小于 60 厘米且不超过 203 厘米）、6.2.2.1 规定单件 2–32 公斤；而深航「行李服务」FAQ 遗留页写的是「最大尺寸 40*60*100CM，单件重量不超过 45kg」。（原因：两套数值互斥且分属不同时点／效力层级的页面。属本子问题边界之外（托运行李非随身行李），仅点出供对应研究员处理，不在此裁决何者现行。另注意：总条件明示免费行李额由深航按舱位、航线距离、会员等级另行确定并需向深航查询，故国内线经济舱免费托运额是否仍为 20 公斤无法由本总条件直接证实。）
### 信息缺口（优先级）
- 深航国内线（自营航班）免费托运行李额的具体数值（是否仍为经济舱 20 公斤/公务舱 30 公斤，或改为计件制）——总条件只写「根据舱位等级、航线距离以及旅客会员等级等确定，旅客可向深航查询」，未列明数值（优先级：中）
- 深航是否存在 2026-09-21 之后发布的、专门更新随身行李标准的公告或新版《行李运输规则》——本轮仅检索到总条件本身与 2024 年旧公告，未见更新公告（优先级：低）

## 未覆盖子问题（预算耗尽，未研究）

以下问题因档位预算（4 波 × 4 并发）未能研究，如需覆盖请提高档位或分次调研：
- 美航(AA)、达美(DL)、联航(UA) 国际线免费托运行李的件数制细则（主舱 1 件 vs 2 件、Basic/Main Basic 差异、23kg/件上限）——只有检索摘要级线索，未读任何官方页面
- 汉莎(LH)、法航(AF)、英航(BA) 国际线计重制 23kg 的官方页面，以及三家手提行李（8kg/12kg/23kg）差异——检索仅得摘要，未取得可引用正文
- 大韩航空(KE) 国际线免费托运的件数与每件重量（是否为 2×23kg 或 30kg 制）——未取得任何来源正文
- 阿联酋航空(EK) 国际线经济舱免费托运行李额度（1 件 23kg? 7kg 手提?）——未取得来源
- 川航（3U）、吉祥（HO）、深圳航空（ZH）、海航（HU）、祥鹏（8L）国内线 A320/737-800/A321 经济舱座椅间距的逐机型数值仍无任何可引用来源；本轮仅确认 SeatMaps 存在深航 737-800 / 川航 A320·A321·737-800 页面，但间距数值未取得（抓取结果被站点页脚与导航列表淹没，数值落在超长溢出文件中未能读取）
- 东航（MU）官网是否存在类似南航「机舱布局」的逐机型一手间距页——本轮两轮检索（含中文站内关键词组合）均未命中，可能是本次「八家航司逐机型数据」缺口的最后一块拼图

---

## 补充研究（审查驱动）

## 补研：「服务口碑」维度实质未交付。速览表第 8 条「航司级服务口碑在中国全服务航司上无任何可交叉验证的量化证据〔中〕，支持来源数 2（检索无果 + 仅 UGC 来源）」——把「本轮未取得」写成「世界��不存在」的正面断言并标〔中〕。下游若照此把口碑字段全部留空而不补数据，将永久损失一整个维度。

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- CAAC 官方《2025年民航行业发展统计公报》确实设有「航空安全与服务质量」章节并公布量化值，但其投诉数据只有全行业口径：民航局消费者事务中心全年受理旅客服务诉求68.87万件，其中旅客服务投诉50.21万件，违规投诉占总诉求量1.56%。公报全文（21页、十二个部分）无任何按航司拆分的投诉量/投诉率/满意度数据——即「航司级投诉率不存在官方公开量化源」这一判断在公报层面已确认为事实，而非检索未果。（置信度：高 · 类型：官方 · 时点：2026-04，来源：https://www.mot.gov.cn/shuju/fenxigongbao/hangyegongbao/202604/P020260420360508740335.pdf）
  - 数字：民航局消费者事务中心受理旅客服务诉求总量 = 68.87万件（2025年）；其中旅客服务投诉 = 50.21万件（2025年）；违规投诉占总诉求量比例 = 1.56%（2025年）；公报结构中是否含航司级服务口碑拆分 = 无（12个部分、21页全文无按航司拆分）（2025年度公报）
- 同一公报给出可交叉验证的行业级运行质量硬指标：2025年全国客运航空公司执行航班510.58万班次、正常465.09万班次，正常率91.09%；14家「主要航空公司」（含南航、国航、东航、海南、深圳、四川、厦门、山东、上海、天津、吉祥、春秋、华夏、成都）平均正常率90.96%；全国客运航班平均延误时间7分钟。注：该90.96%为14家合计值，公报未按单家航司披露。（置信度：高 · 类型：官方 · 时点：2026-04，来源：https://www.mot.gov.cn/shuju/fenxigongbao/hangyegongbao/202604/P020260420360508740335.pdf）
  - 数字：全国客运航空公司平均航班正常率 = 91.09%（2025年）；主要航空公司（14家）平均航班正常率 = 90.96%（2025年）；全国客运航班平均延误时间 = 7分钟（同比减少3分钟）（2025年）；千万级以上机场近机位靠桥率 = 85.8%（同比+2.0个百分点）（2025年）；全行业旅客运输量（投诉率分母） = 77014.68万人次（7.70亿人次）（2025年）；运输航空百万架次重大事故率十年滚动值 = 0.023（2025年）
- 由公报两项官方数字可推出行业级投诉率量级（本人计算，非公报公布值）：50.21万件旅客服务投诉 ÷ 7.70亿人次 ≈ 6.5件/万人次（投诉件数/客运量），但该比值同时含非承运环节诉求与未乘机投诉，仅可作为量级参考，不可当作严格「每万人次投诉率」。（置信度：中 · 类型：官方 · 时点：2026-04，来源：https://www.mot.gov.cn/shuju/fenxigongbao/hangyegongbao/202604/P020260420360508740335.pdf）
  - 数字：推导的行业级投诉率量级 = 约6.5件/万人次（50.21万件÷7.70亿人次）（2025年）
- Skytrax 2026年世界航空大奖（2026-09-18伦敦颁证）提供中国航司首个可交叉验证的国际量化口碑锚点：海南航空入选全球最佳航空公司TOP10（第8位，较2025年第10位上升2位），并连续第15年获「SKYTRAX五星航空」，同时拿下中国最佳航空公司（Best Airline in China）、中国最佳航空公司员工服务、全球最佳商务舱舒适用品，以及全球最佳客舱乘务员第4名。该组事实由中国民航网（民航局主管官方行业媒体）与海南 airlines 官方新闻稿双向印证。（置信度：高 · 类型：官方 · 时点：2026-09-18，来源：http://www.caacnews.com.cn//1/6/202609/t20260919_1397393.html）
  - 数字：海南航空 Skytrax 全球最佳航空公司排名 = 第8位（2025年为第10位）（2026年（2025年对比））；海南航空五星航司连续获评年数 = 连续15年（2026年）；海南航空全球最佳客舱乘务员排名 = 第4名（2026年）；2026年Skytrax全球最佳航空公司前三 = 新加坡航空第1、卡塔尔航空第2、国泰航空第3（2026年）
- Skytrax 2026全球100强榜单中，中国内地全服务航司仅中国南方航空入榜（第31位）；同榜另有中华航空第30位、香港航空第53位、香港快运第71位（港台口径）。该名次来自中文媒体报道，未取得 Skytrax 官方榜单页正文（官方页为 JS 渲染，抓取返回空正文），故为单一来源。（置信度：中 · 类型：媒体 · 时点：2026-09-18，来源：https://sina.cn/news/detail/5344622546781622.html）
  - 数字：中国南方航空 Skytrax 全球最佳航空公司排名 = 第31位（2026年）；入榜的港台航司排名 = 中华航空第30位、香港航空第53位、香港快运第71位（2026年）
- CAPSE《2025年第四季度航空公司服务测评报告》给出中国内地20家全服务航司的逐家量化满意度得分（有效样本889,332份，35家内地航司参与），是本轮唯一取得的「全服务航司级」口碑分值表：厦门航空4.08蝉联榜首、四川航空4.07、南方航空4.04、深圳航空4.03、山东航空4.02、中国国际航空4.01、东方航空4.00、海南航空3.99、西藏航空3.98、上海航空3.97；前三名与第十名仅差0.11分。重要限定：本条数据本轮仅取得单一二手转载源（航空货运类网站转述），未取得 CAPSE 原始报告页交叉验证。（置信度：中 · 类型：用户生成 · 时点：2026-01，来源：https://www.huotong.cn/newsDetail?id=537）
  - 数字：CAPSE 2025Q4 有效样本量 = 889,332份（2025Q4）；参与测评的内地全服务航司数 = 20家（2025Q4）；厦门航空/四川航空/南方航空满意度 = 4.08 / 4.07 / 4.04（2025Q4）；深圳航空/山东航空/中国国际航空/东方航空满意度 = 4.03 / 4.02 / 4.01 / 4.00（2025Q4）；海南航空/西藏航空/上海航空满意度 = 3.99 / 3.98 / 3.97（2025Q4）；全服务航司前十名首尾分差 = 0.11分（2025Q4）
- CAPSE 2025Q1测评进一步给出全服务与差异化两类航司的类别均值与得分梯度（有效样本660,132份，20家全服务+15家差异化航司）：全服务航司平均3.95分、差异化航司平均3.70分，差0.25分；全服务航司得分梯度0.36分、差异化航司0.16分，说明全服务航司口碑分化显著大于差异化航司。该口径同时明确列出20家全服务航司名单（南航、东航、国航、海航、深航、川航、厦航、山航、天航、吉祥、上航、成航、长龙、藏航、青航、昆明、河北、苏南瑞丽、多彩贵州、金鹏），可直接用于「全服务航司」集合定义。同样仅取得单一二手源。（置信度：低 · 类型：用户生成 · 时点：2025-03，来源：https://www.sgpjbg.com/labelsyh/minhanglukemanyiduceping.html）
  - 数字：CAPSE 2025Q1 有效样本量 = 660,132份（2025Q1）；全服务航司平均满意度 = 3.95分（2025Q1）；差异化航司平均满意度 = 3.70分（2025Q1）；全服务航司得分梯度 = 0.36分（2025Q1）；差异化航司得分梯度 = 0.16分（2025Q1）
- 《2024年中国民航服务旅客满意度评价报告》由中国民航科学技术研究院、中国民航报社、中航信航旅纵横、中国民用机场协会四家单位联合发布，构成本国民航体系内最权威的官方关联满意度源，但口径为行业级、不分航司：2024年航空公司服务总体满意度8.85分（满分10分），机场服务总体满意度8.99分；分项中票务与客服服务9.20分为优势项目，航班正常及延误服务为航空公司与机场共同的主要短板。该8.85/8.99/9.20三项数值在澎湃新闻与中国民航报/新浪两处独立发布中一致。（置信度：高 · 类型：官方 · 时点：2025-02-18，来源：https://thepaper.cn/newsDetail_forward_30183011）
  - 数字：航空公司服务总体满意度 = 8.85分/10（2024年）；机场服务总体满意度 = 8.99分/10（2024年）；票务与客服服务分项得分 = 9.20分/10（2024年）；航班正常及延误服务分项 = 航空公司与机场均为主要短板（未公布具体分值）（2024年）
- 消费保（中国电子商会旗下消费服务保障平台）《2024年度消费投诉数据分析报告》提供了中国全服务航司逐家投诉量，是本轮取得的唯一「按航司拆分」的投诉量化表：2024年航空服务相关投诉4,843件，前五依次为南方航空1,046件、东方航空584件、春秋航空347件、海南航空277件、中国国航235件；航空服务投诉占旅游出行投诉4.63%。平台自身声明数据仅代表消费保平台，不代表企业总体投诉情况，故为渠道口径而非全行业口径。（置信度：中 · 类型：一手 · 时点：2025-01-07，来源：https://www.xfb365.com/article/154303.html）
  - 数字：2024年航空服务相关投诉总量（消费保平台） = 4,843件（2024年）；南方航空投诉量 = 1,046件（2024年）；东方航空投诉量 = 584件（2024年）；春秋航空投诉量 = 347件（2024年）；海南航空投诉量 = 277件（2024年）；中国国航投诉量 = 235件（2024年）；航空服务投诉占旅游出行投诉比例 = 4.63%（2024年）
- 结论性判定（推翻原速览表第8条）：中国全服务航司的服务口碑存在可交叉验证的公开量化源，但分三层且口径互不相同——(1)官方层：CAAC《民航行业发展统计公报》只给全行业投诉总量与正常率，无航司级拆分（已逐页核实）；(2)官方关联评价层：民航科技院等四单位《中国民航服务旅客满意度评价报告》给行业级分项得分，不分航司；(3)第三方层：Skytrax（国际，单家可验证，海航/南航有确切名次）与 CAPSE（国内，20家全服务航司逐家分值、季度更新）、消费保（国内，按航司逐家投诉量、年度更新）可提供航司级数值。因此「永久损失一个维度」的推断不成立，但该维度无法用单一官方源覆盖，须显式采用第三方+渠道口径并标注口径差异。（置信度：高 · 类型：官方 · 时点：2026-09，来源：https://www.mot.gov.cn/shuju/fenxigongbao/hangyegongbao/202604/P020260420360508740335.pdf）
  - 数字：可用的航司级口碑量化源数量 = 3类（Skytrax排名/CAPSE满意度/消费保投诉量）（截至2026-09）；CAPSE 覆盖的内地全服务航司数 = 20家（2025Q4）
### 不确定项
- CAPSE 2025Q4 逐家分值（厦航4.08 / 川航4.07 / 南航4.04 / 深航4.03 / 山航4.02 / 国航4.01 / 东航4.00 / 海航3.99 / 藏航3.98 / 上航3.97）目前仅有一家航空货运类网站的转述，未取得 CAPSE 官网或民航资源网原始报告页；若原报告口径（5分制、样本范围、是否加权）与转述有差异，逐家数值不可直接引用。（原因：CAPSE 原始报告为PDF/付费墙内容，本轮两次搜索均未命中可抓取的原始发布页。）
- 消费保的航司级投诉量是渠道口径（单一平台），不能等同于航司实际投诉总量或投诉率；将其直接与 CAPSE 满意度或 CAAC 行业投诉量并列排名会产生口径错配。（原因：报告方在文末明确声明「仅代表企业在消费保平台的投诉解决情况，不代表其他平台或企业总体」。）
- CAPSE 2025Q1 与 2025Q4 之间未取得同口径的逐家对照表，因此「全服务航司平均分同比提升0.05-0.08分」这一转述性结论本轮无法验证。（原因：两期报告均只取得片段转述，缺原始同口径表。）
### 信息缺口（优先级）
- Skytrax 2026 中国国际航空、中国东方航空的全球最佳航空公司确切名次与星级（一/四/五星）未取得——Skytrax 官方 Top100 与 by-region 页面为 JS 渲染，fast/full 两种模式抓取均返回空正文；本轮仅确认南航第31位与海航第8位，国航/东航是否在100强内及名次未知。（优先级：高）
- 《2025年中国民航服务旅客满意度评价报告》（年度版，官方关联口径）未取得。仅取得2024年度版与2025年Q1/Q2/Q3季度版；2025年度版（预计2026年2月前后发布）需单独定向检索 caacnews.com.cn 或中国民用机场协会服务评价栏目。（优先级：高）
- CAPSE 原始报告页（capse.cn / 民航资源网）未取得，2025Q4逐家分值与2025全年榜均缺一手来源验证。（优先级：高）
- 航司级航班正常率（单一航司口径）不存在公开源——CAAC公报仅披露14家主要航空公司合计90.96%。若下游需要「按航司的正常率」字段，须明确标注为不可得，改用主要航司合计值或Skytrax/CAPSE替代。（优先级：中）
- 2025年度消费保航司级投诉量（南航/东航/国航/海航逐家）未取得，仅有2024年度数据；黑猫投诉2024年机场航空报告（投诉量近3.9万件）虽已检出但未抓取正文，其逐航司拆分可能与消费保形成第二渠道交叉验证。（优先级：中）
- Skytrax 官网正文全部无法抓取（JS渲染），导致所有Skytrax数值目前只能依赖中文/英文媒体报道；海航数据已由官方行业媒体+企业新闻稿双源覆盖，但南航第31位为单一来源。（优先级：中）
- 三大航（国航/东航/南航）的CAPSE 2025Q4分值虽已取得，但缺少其与Skytrax排名的相关性分析材料，无法判断两个第三方口碑源是否给出方向一致的服务口碑结论。（优先级：低）

## 补研：末轮 2 个子问题因预算耗尽未覆盖：美系与欧亚头部航司（美航/达美/联航/汉莎/法航/英航/大韩/阿联酋）国际线免费托运的件数制细则，导致「全球头部航司」这一半在行李维度上只有美航/联航的里程门槛（且该门槛引文本身错误）与达美的尺寸收费。

### 已确认事实（编号 · 置信度 · 来源类型 · 时点）
- 美国航空（AA）国际线采用「件数制 + 单件重量上限」：跨大西洋、跨太平洋、拉丁美洲、亚洲/印度/卡塔尔航线，主舱（经济舱）旅客第 1 件托运行李免费，尺寸上限 62 in / 158 cm，重量上限 50 lbs / 23 kg；往返澳大利亚/新西兰的免费行李重量上限提高至 70 lbs / 32 kg。AA 官方页显示国际线免费首件行李是按「目的地清单 + 航司会员/联名信用卡等级」授予的，并不存在「里程门槛」这一免费触发条件；例外是往返中美/南美部分国家、印巴等航线的「基本经济舱（Basic Economy）」不享免费首件。（置信度：高 · 类型：官方 · 时点：2026-09（页面标注行李限额与费用更新自 2026-05-18 起生效），来源：https://www.aa.com/i18n/travel-info/baggage/checked-baggage-policy.jsp）
  - 数字：国际线经济舱免费托运件数 = 1 件（Main Cabin，排除 Basic Economy 的部分航线）（当前有效）；单件重量上限（非澳新） = 50 lbs / 23 kg（当前有效）；单件重量上限（往返澳新） = 70 lbs / 32 kg（当前有效）；单件尺寸上限 = 62 in / 158 cm（长+宽+高）（当前有效）；可托运行李总件数（跨大西洋/跨太平洋） = 最多 10 件（当前有效）；跨太平洋第 2 件费用 = USD 100（当前有效）；Basic Economy 跨太平洋第 1 件费用 = USD 75（2026-05-18 起开票）
- 达美航空（Delta）国际线采用「件数制 + 每件 50 lb/23 kg 硬上限」：Delta Main（经济舱）、Delta Comfort、Delta Premium Select 旅客每件托运行李适用标准 50 lb 上限；官方国际线超额行李费率表以「第 3 件及以后」为起算档（美加↔欧洲/北非为每件 USD 285 / EUR 240，其余多数航线每件 USD 200），即经济舱旅客的免费件数为 1 件起、随票价产品与航线不同而变；第 2 件标准行李（50 lb/23 kg 以内）标准费率为每程每件 USD 55。飞往/经停欧洲、南非、阿联酋以及欧↔美航线，单件行李超过 70 lb/31.75 kg 一律不收运。（置信度：中 · 类型：官方 · 时点：2026-09（Delta 页面标注现行费率适用于「今日及之后」出票），来源：https://www.delta.com/us/en/baggage/overview）
  - 数字：经济舱单件重量上限 = 50 lb / 23 kg（当前有效）；第 2 件标准行李费率 = USD 55 / 件 / 每程（当前有效）；国际线第 3 件起超额费率（美洲↔欧洲/北非） = USD 285 / CAD 330 / EUR 240 每件每程（当前有效）；欧↔美线单件禁止收运重量阈值 = 70 lb / 31.75 kg 以上不收运（当前有效）；行李尺寸上限（长+宽+高） = 62 in / 157 cm（当前有效）
- 联合航空（United）国际线采用「件数制 + 每件 23 kg 上限」：United Economy 与 Premium Economy 每件托运行李重量上限 50 lbs / 23 kg，United Business / First / Polaris 为 70 lbs / 32 kg；单件尺寸上限为 30×20×12 in（76×52×30 cm）或长+宽+高合计 62 in（含把手与滚轮）。前程万里里程身份不改变经济舱的 23 kg 上限，Business 舱身份才升至 32 kg。（置信度：高 · 类型：官方 · 时点：2026-09（页面列出 2026-04-03 / 2026-05-12 / 2026-07-21 三轮国际线费率上调），来源：https://www.united.com/zh-hant/hk/fly/baggage/checked-bags.html）
  - 数字：经济舱/超经舱单件重量上限 = 50 lb / 23 kg（当前有效）；公务舱/头等舱/Polaris 单件重量上限 = 70 lb / 32 kg（当前有效）；单件尺寸上限 = 30×20×12 in 或合计 62 in（长宽高）（当前有效）
- 阿联酋航空（Emirates）是全球头部航司中「件数制与重量制并行」的典型：绝大部分航线采用重量制（Economy Special 20 kg / Saver 25 kg / Flex 30 kg / Flex Plus 35 kg，Premium Economy 35 kg，Business 40 kg，First 50 kg，单件不超过 32 kg）；仅往返美洲与非洲的航线（2021-08-09 起开票的非洲航线一并适用）采用件数制——美洲/非洲航段（美洲内部及美欧航线除外）经济舱 Special 1 件 ×23 kg，Saver/Flex/Flex Plus 2 件 ×23 kg；美洲内部及美欧航线经济舱 Special 与 Saver 为 1 件 ×23 kg，Flex/Flex Plus 为 2 件 ×23 kg。件数制下单件三边之和上限 150 cm。（置信度：高 · 类型：官方 · 时点：2026-06（页面发布时间 2026-06-16），来源：https://www.emirates.com/us/english/before-you-fly/baggage/checked-baggage/）
  - 数字：重量制经济舱免费额度（Special/Saver/Flex/Flex Plus） = 20 / 25 / 30 / 35 kg（当前有效）；重量制单件上限 = 32 kg（当前有效）；件数制经济舱（美洲/非洲，Special） = 1 件 × 23 kg（2021-08-09 起开票）；件数制经济舱（美洲/非洲，Saver/Flex/Flex Plus） = 2 件 × 23 kg（2021-08-09 起开票）；件数制经济舱（美洲内部及美欧，Special/Saver） = 1 件 × 23 kg（当前有效）；件数制单件尺寸上限 = 150 cm（长宽高之和）（当前有效）；重量制单件尺寸上限 = 203 cm（长宽高之和）（当前有效）
- 大韩航空（Korean Air）国际线采用件数制：除美洲与巴西航线外，国际线航班经济舱（Saver 票价）免费 1 件、单件不超过 23 kg；经济舱（Saver 以外票价）与优选舱同为 1 件 ×23 kg；商务舱 2 件 ×32 kg；头等舱 3 件 ×32 kg。单件硬上限为 32 kg / 70 lb、线性尺寸 158 cm / 62 in，超过即无论付费与否都可能被部分国家拒收。大韩航空明确列出租运方运力限制：往返巴西的国际线免费行李规则另行列出。（置信度：中 · 类型：官方 · 时点：2026-09（页面为实时政策页，无发布日期），来源：https://www.koreanair.com/contents/plan-your-travel/baggage/checked-baggage/free-baggage）
  - 数字：国际线经济舱免费件数（美洲/巴西除外） = 1 件 × 23 kg（当前有效）；国际线商务舱免费件数 = 2 件 × 32 kg（当前有效）；国际线头等舱免费件数 = 3 件 × 32 kg（当前有效）；单件硬上限 = 32 kg / 70 lb，158 cm / 62 in（当前有效）
- 英国航空（British Airways）国际线采用件数制并按票价分层：Economy Basic 不含任何托运行李，标准 Economy（含 1 件托运行李的票价）免费 1 件 ×23 kg，Premium Economy 免费 2 件 ×23 kg，Business 免费 2 件 ×32 kg，First 免费 3 件 ×32 kg。即 BA 的经济舱是「同一舱位内 0 件或 1 件」的票价二分，而非全舱统一 1 件。（置信度：中 · 类型：官方 · 时点：2026-09（ba.com 页面实时内容，抓取时站点返回高负载页，正文取自官方域索引摘要），来源：https://www.britishairways.com/en-kn/information/baggage-essentials）
  - 数字：Economy Basic 免费托运件数 = 0 件（当前有效）；标准 Economy 免费托运件数/重量 = 1 件 × 23 kg（当前有效）；Premium Economy 免费托运件数/重量 = 2 件 × 23 kg（当前有效）；Business / First 免费托运件数/重量 = 2 件 × 32 kg / 3 件 × 32 kg（当前有效）
- 汉莎航空（Lufthansa）国际线采用件数制：经济舱免费 1 件手提行李（≤8 kg）与 1 件托运行李（≤23 kg）。该结论取自 Lufthansa Group 官方企业站（business.lufthansagroup.com）的行李规则页摘要；lufthansa.com 面向消费者的页面在本次抓取中被 Cloudflare 机器人验证拦截，未能取得含 Economy Basic 免托运变体与超额费率的完整表。（置信度：低 · 类型：官方 · 时点：2026-09（lufthansa.com 消费者页被 403 拦截，未取得页面版本日期），来源：https://business.lufthansagroup.com/us/en/program/experts/Baggage）
  - 数字：经济舱免费托运件数/单件重量 = 1 件 × 23 kg（当前有效）；经济舱免费手提行李重量 = 8 kg（当前有效）
- 横向归纳：八家头部航司在行李维度上可清晰分为三种制度——（1）美系三强（AA/UA/Delta）与国际航司普遍采用「件数制 + 单件 23 kg 上限」，经济舱免费件数为 1 件，澳新/部分航线例外；（2）阿联酋航空独有「重量制为主 + 美非航线件数制」的双轨制，同一经济舱在不同航线体系下可能得到 1 件或 2 件；（3）BA/汉莎在舱位内部再做票价分层（Economy Basic 0 件 vs Economy 1 件），因此「经济舱免费件数」并非舱位属性而是「舱位 × 票价家族 × 航线区域」三者的联合函数。（置信度：中 · 类型：官方 · 时点：2026-09，来源：https://www.emirates.com/us/english/before-you-fly/baggage/checked-baggage/）
  - 数字：件重制（每件 23 kg）阵营 = AA / Delta / United / BA / Lufthansa / Korean Air（当前有效）；重量制 + 件数制双轨阵营 = Emirates（当前有效）；经济舱免费件数在 0–2 件间浮动的家数 = ≥3 家（BA、Emirates、AA 的 Basic Economy）（当前有效）
### 不确定项
- 达美国际线「经济舱到底免费几件」未被官方页面直接给出：其官方超额行李表以「第 3 件起」为起算档，暗示主舱票面含 2 件，但 Overview 页又只写 Delta Main/Comfort/Premium Select 适用 50 lb/件且第 2 件为 USD 55，二者存在口径不一致。（原因：Delta 未在本次可抓取的官方页面给出「Main / Main Basic / Main Classic × 航线」的分档免费件数矩阵；Delta Main Basic（基础经济舱）国际线通常不含免费托运，但缺少官方引文。）
- 联合航空国际线经济舱的免费件数（1 件）未能从官方页取证。（原因：united.com 的 International checked bag limits 页面为 JS 渲染，抓取仅返回「请启用 JavaScript」；已抓到的 checked-bags 页只提供单件重量/尺寸，未提供件数。）
- 汉莎「经济舱 1 件 ×23 kg」的官方消费者页原文未能取得，现有依据仅为 Lufthansa Group 企业站的索引摘要。（原因：lufthansa.com 全部路径（/us/、/at/、/gb/）返回 403 Cloudflare 验证页；business.lufthansagroup.com 同样 403。该条不宜作为高置信引文使用。）
- 大韩航空「美洲/巴西」航线的经济舱免费件数未取得具体数值。（原因：官方页的 International 标签由 JS 切换，爬虫只渲染出 Korea domestic 标签；国际线分段表仅在中文/繁体中文本地化页的搜索摘要中呈现。）
- 各航司「超重/超大」费率表在本次补研中仅达美取得完整国际线分航线表，其余七家未取得。（原因：预算耗尽前未逐家抓取 oversized/overweight 子页。）
### 信息缺口（优先级）
- 法国航空（Air France）国际线经济舱免费托运件数与单件重量上限——完全未取得。airfrance.us 的 /information/bagages/bagage-cabine-soute 只渲染出手提行李部分（经济舱 12 kg 小包），托管页与 .co.uk/.fr 的 checked-baggage 路径均 404 或为纯导航壳。这是本次补研中唯一完全空白的头部航司。（优先级：高）
- 汉莎航空的完整经济舱行李矩阵未取得：Economy Basic（短/中程）免托运的变体、长程航线的 1 件 vs 2 件差异、以及超重/超大费率表均缺失，现有结论仅一条低置信摘要。（优先级：高）
- 联合航空国际线免费件数、以及 United 的 Global Premier/Polaris 等身份在件重制航线上的免费件数加成未取得。（优先级：中）
- 达美「Delta Main Basic（基础经济舱）」国际线不含免费托运这一关键事实缺官方引文，而这恰是与 AA Basic Economy、BA Economy Basic 对比的要点。（优先级：中）
- 大韩航空往返美洲与巴西航线的经济舱免费件数（官方页面单列该分节）未取得具体数值。（优先级：中）
- 英航与汉莎的「Economy Basic 无托运」是否适用于所有国际航线、以及 2026 年是否已调整未取得带日期的官方版本记录（ba.com 与 lufthansa.com 页面均无 as-of 标注）。（优先级：低）
- 八家航司的超重/超大（尺寸与重量超限）分航线费率表，除达美外均未取得。（优先级：低）
- 多个官方页面为实时动态内容且不标注生效日期，本轮 asOf 统一标注为抓取当月（2026-09），若报告需做时点精确断言，应回访各页版本记录。（优先级：低）

---

## 对抗性审查意见

# 对抗性审查意见：航空公司规则与体验知识调研

**审查方式**：对报告中风险最高的 5 条引文做逐字核对（NPR Spirit 停运 / Wikipedia SeatGuru / Delta 机上餐饮 / Executive Traveller 泰航新规 / 吉祥航空行李运输规定 PDF）。5 条中 **3 条完全逐字成立、1 条存在引文与结论错配、1 条存在明确的引文扭曲**。以下按「可疑来源 → 覆盖盲区 → 信息矛盾 → 过度自信 → 补充方向 → 总体评估」展开。

---

## 一、可疑来源

### 1. 【高】达美机上餐饮页面被用作美航、联航数据的唯一引文——引文与结论错配

报告称：「同口径下美航在 250 英里以上提供免费零食与无酒精饮料，联航全航班提供免费无酒精饮料、300 英里以上提供免费小吃 [citation:达美机上餐饮说明]」并标〔高〕。

抓取 `delta.com/us/en/onboard/food-and-beverage/overview` 的实际正文，全文只包含**达美自有产品**（Delta One / Delta First / Thrive Farmers 茶 / 主舱 6.5 小时以上免费酒水），**不存在任何美航（AA）或联航（UA）的字样，不存在 250 英里、300 英里这两个门槛**。一个航司的官网页面在结构上不可能是同业竞品里程门槛的权威出处，这不是抓取失败，是**引文类型与结论类型根本不匹配**。

同一份引文支撑的另外两项也需降级：页面逐字含 "Beverage service offered on flights over 350 miles and over" 与 "complimentary beer, wine and spirits* on flights of 6.5 hours or more"——**350 英里门槛与 6.5 小时酒水门槛逐字成立**；但报告的「自 2026 年 5 月 19 日起**取消**」「涉及约 **9%** 日航班量」两个关键表述，**在该页抓取内容中未逐字出现**。可能是 Delta 站内 "What's new" 区块未被 fast 模式捕获，也可能数字转自他处被并入同一引用。两种情形都意味着当前引文**不足以支撑〔高〕**。

### 2. 【高】SeatGuru「2020 年初停止更新」是对维基原文的明确扭曲

报告称：「其数据在 2020 年初即停止更新」，并据此推论「25 年积累的逐机型历史 pitch 数据未提供替代品」，此推论又被写进「覆盖缺口与已验证盲区」作为已验证盲区之一。

维基原文实际写的是：**"As of 2020, its app is no longer available in the Apple App Store and Google Play. Blog posts were also discontinued in March 2020."** —— 这是**移动端 app 下架 + 博客于 2020 年 3 月停更**，与「座位图数据停止更新」是两件事。报告把一条关于**产品渠道**的事实放大成了关于**数据资产**的事实，并在此虚构前提上建立了「历史数据断档 → 现有数据新鲜度无法回溯」这一整段论证。维基还明确列出了替代站清单（2LNR、AeroLOPA、SeatMaps.com、FlightSeatmap.com、ExpertFlyer、Seatcompare.ai），并未说「未提供替代品」。

**影响面**：这条是「已验证盲区」三条中的第 2 条，且被用来论证「AeroLOPA 与 SeatMaps 的数据新鲜度无法回溯验证」——而 SeatGuru 恰恰是唯一能做交叉校验的历史基准。前提错了，整段论证失效。

### 3. 【中】吉祥航空「2023 年 10 月版曾为 10 公斤」在所引 PDF 中找不到依据

所引 PDF 逐字内容（全部核对通过）：2025-08-08 生效、经济舱非托运 1 件 ≤5 公斤、公务舱 2 件 ≤8 公斤、55×40×20 cm 且三边和 ≤115 cm、国内经济舱免费托运 20KG——**报告表格与正文表述全部准确**。

但该 PDF 第 6 节「生效日期」逐字写的是：「自生效之日起，我司于 **2025 年 1 月 13 日**公布施行的《上海吉祥航空股份有限公司行李运输规定》同时废止」。文档自述被废止的前序版本是 2025-01-13，**不是 2023 年 10 月**。报告的「2023 年 10 月版曾为 10 公斤」在这份引文中无任何依据，时间线也与文档自述冲突。

### 4. 【中】其余引文核对结果（成立，登记备查）

- **NPR Spirit 停运**：逐字成立。"on May 2, 2026, Spirit Airlines started an orderly wind-down of our operations, effective immediately"、$500 million bailout、伊朗战争推高航油、传统航司 basic economy 复制打法——四项诱因链全部逐字可对。**唯一超出引文的是「进入 Chapter 7 清算」**：该文只说 2024 年以来两次申请破产，链接指向 2025-08-30 的破产申请报道，未在本页写明 Chapter 7。
- **Executive Traveller 泰航新规**：逐字成立且精度极高。"from 2 March 2026, Thai will move to counting the number of checked bags"、"Economy - two bags at 23kg each on Full and Flex tickets, or one bag at 23kg for Standard, Saver or points-based tickets"——与报告表述完全一致，〔中〕标注恰当。

---

## 二、覆盖盲区

规划阶段「覆盖维度：（未声明）」，因此无法做严格的对维审计，但对照用户问题清单的五个维度，缺口分布高度不均：

| 维度 | 实际状态 | 评估 |
|---|---|---|
| 行李政策 | 覆盖最扎实，含一手 PDF 全文 | ✅ |
| 收费项 | 覆盖较好，但春秋/Ryanair 价目表存在时效与拦截问题 | ⚠️ |
| 座椅 | **末轮预算耗尽，5 家中国航司窄体排距未覆盖** | ❌ |
| 餐食 | 中国航司「哪些航线含餐」的运价结构**完全未取得官方文本** | ⚠️ |
| 服务口碑 | **实际未回答** | ❌ |

**最严重的是「服务口碑」维度。** 用户明确问了服务口碑，报告给出的结论速览表第 8 条却是：「航司级『服务口碑』在中国全服务航司上无任何可交叉验证的量化证据〔中〕，支持来源数 2（检索无果 + 仅 UGC 来源）」。这里的证据是**「我没搜到」**，却被写成了一条**正面事实断言**并标了〔中〕——「未取得」与「不存在」是两回事，前者是本轮研究的能力边界，后者是关于世界的断言。报告正文自己用词是准确的（「本轮只取得…未找到…」），但速览表把它升格成了结论。这一维度对用户的实际交付接近于零。

**第二个盲区是数据时效与制度变更的交叉点。** 报告自己在覆盖缺口里承认「中国民航 2026 年 7 月 1 日起实施的旅客运输新国标」只有二手解读、缺标准原文；同时南航行李规定的抓取时间是全表最早的 **2026-06-26**，早于新国标生效日。也就是说：手提行李尺寸/重量字段所依赖的一手页面，**很可能已被 7 月 1 日新规修正**，而报告既未用新国标反向校验，也未标注该字段可能失效。

**第三个盲区被报告自己低估了。** 所引吉祥航空 PDF 逐字包含「吉祥航空所有国内航线上均使用计重制」「所有地区、国际航线均使用计件制」，并按港澳台俄/东南亚、日韩新、澳洲、欧洲列了**四套不同的计件规则**；还逐字写着「吉祥航空遵循 IATA Resolution 302 规则计算国际联程航段免费行李额」。这是报告自己「四元组主键」核心论点最有力的一手铁证，却被完全丢弃——报告转而用 ANA 页面去论证同一件事，而手边就躺着一份中国航司的一手 PDF。

---

## 三、信息矛盾

报告的「矛盾与分歧」表质量较高（13 条，标注清楚，多数给出裁决或 unknown 处置），但存在**两处未收进该表的隐性冲突**，以及**一处表内已披露但正文自我矛盾**：

1. **南航 A320(320) 排距在正文与矛盾表给了两种裁决。** 正文表格写「30 英寸（国际线页另列 30–39 区间）」，矛盾表则写「不构成冲突……引用应写区间而非单值」。前者把 39 折叠成一个含义不明的区间，后者明确否定了 39 英寸数据的存在。同一组数据两种读法，读者无法判断该信哪个。

2. **「三档结构」模型漏掉了自己的反例。** 报告把中国全服务航司归入「计重 20 公斤」档，但吉祥航空一手 PDF 显示**同一家航司国内计重、地区/国际计件且四套区域规则**。报告在第六节论证「计量制字段不能是航司级常量」时正确地举了泰航与新航，却**没有把吉祥这条一手反例写进「三档结构」模型的自检**——执行摘要的「三档」表述因此比其自身证据更绝对。

3. **执行摘要「手提 5–8 公斤」的精度高于正文证据。** 该区间实际上由「南航 5 / 吉祥 5 / 深航 5 或 8（未裁决）/ 海航 7 / 厦航 8 / 川航 8 / 东航 unknown」拼成，其中含 1 个 unknown 和 1 组未裁决冲突。执行摘要把它写成「全服务航司计重 20 公斤托运加 5–8 公斤手提」这一硬结构，是把带缺口的集合写成了规律。

4. **25/8 双轴矛盾表未收录**：平安/国寿等无。**此项略过**——真正应补的是：报告称「免费额度呈三档结构〔高〕，支持来源数 6（国航/南航/东航/海航/亚航/达美系）」，但正文对**达美只给了 62 英寸尺寸与阶梯收费，从未给出达美的免费额度**。速览表的第 6 个支持来源在正文中不存在实体，「6 个来源」有一格是虚的。

---

## 四、过度自信与置信标注问题

**核心问题：报告自订的置信规则与自身的标注不一致，且速览表的「支持来源数」一栏多次暴露矛盾。**

1. **〔高〕被用在了不满足自订门槛的条目上。** 报告在方法论上未明示门槛，但速览表本身体现了「〔高〕= 多来源」的标准。按此标准：
   - 「Spirit 已停运〔高〕，支持来源数 **1**（NPR 报道）」——**表格自己写明只有 1 个来源却标〔高〕**，自相矛盾。
   - 「中国国内线 20 公斤是行业惯例而非国家规定〔高〕，支持来源数 2（民航规章原文 + 规章解读互证）」——**规章解读文章是对同一份规章的转述，与原文构成同源依赖，不是两个独立来源**。这条是整个执行摘要的地基（「这不是定价偏好，而是制度分层」），地基的置信度需要重建。
   - 「SeatGuru 关停〔高〕，3 个来源」——核下来只有维基给出了确切日期，另两个是综述类。

2. **执行摘要与正文置信度不同步。** 执行摘要标「〔高〕最反直觉的一条：南航 A320 高密度子变体官方自报 28/29 英寸」，但该数据在正文表格中为〔中〕，且原始数据是「28/29/**36**」三个值，摘要只取了 28/29 而略去 36。**取数偏向 + 置信升档**，两处叠加。

3. **「三档结构」这一核心模型从未被标注覆盖不完整。** 结论速览表 8 条全部带置信、无一条带覆盖状态，读者会默认 8 条已覆盖用户问题清单的全部维度。而方法论附注承认「末轮 **2 个子问题因预算耗尽未覆盖**」（美系与欧亚头部航司国际线免费托运细则、五家中国航司窄体机排距）——这两项恰是「全球头部航司」这一半的核心。**速览表缺少「覆盖完整度」这一维。**

4. **「已验证盲区」第一、二条的前提强度不匹配。** 「中国航司口碑数据缺失」被称作「已验证盲区」并断言「这一缺失不是检索不力导致的偶发，而是与…形成鲜明对比」——这**超出了证据能支撑的范围**：「航司主动披露规则、不披露体验」是一个解释性因果判断，本轮没有任何证据（如披露义务清单、监管要求）支撑它。表述应降为观察而非机制断言。

---

## 五、补充研究方向（定向可检索）

1. **Delta 2026 年机上餐饮政策变更原始公告**——检索 `delta.com newsroom "food and beverage" changes May 2026`，或 Delta 的 "What's New on Delta" 页与 Press Kit，确认「2026-05-19 生效日」与「约 9% 日航班量」两个数字的原始出处；若确认不存在，应从报告中删除这两个数字。
2. **美航 / 联航国际线免费托运件数制细则**——分别取 `aa.com` 与 `united.com` 的 baggage 官方页，替换被误用的 Delta 引文。
3. **中国民航 2026-07-01 旅客运输新国标原文**——检索交通运输部 / 民航局公告，定位随身行李尺寸与重量的量化查验条款，用于判定报告内 2026-06 及更早抓取的手提行李字段是否仍然现行。
4. **中国航司服务口碑的量化源**——检索 Skytrax 各航司评分页原文、CAAC 航班正常率与投诉统计年报、民航局「民航服务质量」类公示；这是唯一能把口碑维度从「未取得」升级为「可判定」的路径。
5. **SeatGuru 2020–2025 座位图数据更新情况的独立证据**——检索 AeroLOPA 官方博客 / Seatcompare.ai / View from the Wing 对 SeatGuru 数据维护状况的描述，替换掉被扭曲的维基推断。

---

## 六、总体评估

**这份报告的骨架是对的，噪声集中在引文层。**

值得肯定的三点：一是「四元组最小主键」的结论由南航官网逐机型数据、吉祥一手 PDF、中联航计件例外、IATA Res.302 四步法共同支撑，方向正确且有实据；二是「矛盾与分歧」表主动保留了 13 组冲突并多数给出 unknown 处置，没有粉饰；三是「覆盖缺口与已验证盲区」一节坦白了抓取失败、脚本渲染、付费墙等具体障碍，可信度较高。

但作为**事实底稿**，它有三处硬伤：

**第一，引文层存在一处明确的编造性扭曲（SeatGuru 2020 更新状态）与一处引文错配（Delta 页面支撑美航/联航数据）。** 这两类不是精度问题，是证据链断裂——报告最独特的部分恰恰是「来源层级」方法论，而方法论自己在两处失守。

**第二，置信标注系统未被严格执行。** 速览表的「支持来源数」一栏多次与「〔高〕」并列出现自相矛盾（1 个来源标高、原文+解读当 2 个独立来源、第 6 个来源在正文中无实体）。执行摘要的地基论断（20 公斤是惯例非国家规定）建立在一组同源依赖的「互证」上，读者若照单全信会高估整份报告的可靠度。

**第三，用户明确要求的「服务口碑」维度实质未交付。** 报告把「我没搜到」写成了「不存在」并标〔中〕，这是本次审查中**最可能被下游误用的一条**——知识库建设方若据此把口碑字段全部留空而不去补数据，损失的是一整个维度。

**修复优先级建议**：① 撤回并重写 SeatGuru 与 Delta 两处引文（high）；② 重标 3 条〔高〕为〔中〕，或补齐第二个独立一手来源（high）；③ 把「服务口碑未取得」从结论速览表移入覆盖缺口，恢复该维度的可检索任务（high）；④ 删除吉祥「2023 年 10 月版」无据断言、修正「泰航与新航同一家内并存两种制度」的表述（medium）。上述 4 项完成后，报告可作为合格底稿使用；未修复前，速览表不应直接交付给知识库建设方。