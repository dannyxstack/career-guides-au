# -*- coding: utf-8 -*-
"""多国(NZ/CA/US/UK/DE/FR/ES) 能源电力 + 半导体/电子 11 个新兴细分工程岗数据入库。

承接 seed_energy_semiconductor_au.py（AU 母本）。角色职责/评分复用 AU；各国单独设定：
分类码(ANZSCO/NOC/SOC/KldB/ROME/CNO)、货币、薪资档(联网调研)、移民语义与签证、PR 评分、市场前景。
AI 分析块通过 copy_ai_blocks 从 AU 同岗复制（AI 影响与国别无关）。

薪资来源(2025-2026)：ERI SalaryExpert / PayScale / Glassdoor / Indeed / talent.com 各国站点。
评分 10 分制。occ_code 采用「父级码-角色后缀」唯一合成，页面只展示 anzsco_code。

运行：PYTHONIOENCODING=utf-8 python -m scripts.seed_energy_semiconductor_multi
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation_v2

# ============================ 角色母本（通用，跨国复用）============================
# family: eng=电力工程 / eng_low=EV充电 / top_eng=数据中心 / semi_top=高端半导体 / semi=IC验证 / emb=嵌入式 / tech=技术员
ROLES = [
    {"key": "PWR", "zh": "电力系统工程师", "en": "Power Systems Engineer", "family": "eng", "cat": "Engineering & Infrastructure",
     "tier": "eng", "workforce": 8000, "shortage": 1,
     "sum_zh": "电力系统工程师负责发电、输电、配电网络的规划、分析与运行，做潮流计算、短路与稳定性分析、保护整定和并网研究，是能源转型中最紧缺的核心工程角色之一。",
     "sum_en": "Power systems engineers plan, analyse and operate generation, transmission and distribution networks — running load-flow, short-circuit and stability studies, protection settings and grid-connection studies — one of the most in-demand core engineering roles in the energy transition.",
     "growth": ["可再生能源并网", "输配电网规划与稳定性分析", "电网调度与市场建模", "储能与虚拟电厂接入", "电网数字化与实时仿真"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (6, "中等"),
           "job_demand": (9, "极高"), "competition": (4, "低"), "work_intensity": (6, "中等"),
           "income_level": (8, "较高"), "future_prospect": (10, "极好"), "ai_risk": (3, "低")}},
    {"key": "BESS", "zh": "储能系统工程师", "en": "Battery Energy Storage (BESS) Engineer", "family": "eng", "cat": "Engineering & Infrastructure",
     "tier": "eng", "workforce": 2000, "shortage": 1,
     "sum_zh": "储能系统工程师负责电池储能电站(BESS)的电气设计、系统集成、并网与调试，涵盖 PCS 变流器、EMS 能量管理、BMS 电池管理与安全消防合规，是能源领域增长最快、供给最紧缺的工程岗之一。",
     "sum_en": "BESS engineers handle electrical design, system integration, grid connection and commissioning of battery energy storage systems — PCS inverters, EMS, BMS and fire/safety compliance — one of the fastest-growing and most supply-constrained roles in the energy sector.",
     "growth": ["电网级储能电站设计与并网", "储能系统集成(PCS/EMS/BMS)与调试", "储能安全与消防合规", "虚拟电厂与户用储能聚合", "储能项目并网研究与市场套利建模"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (6, "中等"),
           "job_demand": (9, "极高"), "competition": (3, "极低"), "work_intensity": (6, "中等"),
           "income_level": (8, "较高"), "future_prospect": (10, "极好"), "ai_risk": (3, "低")}},
    {"key": "EVCI", "zh": "电动车充电基础设施工程师", "en": "EV Charging Infrastructure Engineer", "family": "eng_low", "cat": "Engineering & Infrastructure",
     "tier": "eng_low", "workforce": 1500, "shortage": 1,
     "sum_zh": "电动车充电基础设施工程师负责公共/商用充电站的电气设计、配电接入、并网与合规，涵盖直流快充(DCFC)、负荷管理、OCPP 通信与场站储能集成，随 EV 保有量上升而快速分化。",
     "sum_en": "EV charging infrastructure engineers handle electrical design, grid/distribution connection and compliance for public and commercial charging stations — DC fast charging, load management, OCPP and on-site storage integration — a role branching off fast as EV fleets grow.",
     "growth": ["公共快充/超充站电气设计与并网", "充电网络负荷管理与配电升级", "充电桩标准与合规(OCPP)", "车网互动(V2G)与站点储能集成", "车队与商用充电基础设施规划"],
     "R": {"learning_difficulty": (7, "较高"), "learning_duration": (7, "较长"), "certification_difficulty": (6, "中等"),
           "job_demand": (8, "高"), "competition": (4, "低"), "work_intensity": (6, "中等"),
           "income_level": (7, "中高"), "future_prospect": (9, "很好"), "ai_risk": (3, "低")}},
    {"key": "DCE", "zh": "数据中心电气工程师", "en": "Data Centre Electrical Engineer", "family": "top_eng", "cat": "Engineering & Infrastructure",
     "tier": "top_eng", "workforce": 3000, "shortage": 1,
     "sum_zh": "数据中心电气工程师负责数据中心的供配电系统设计与运维，涵盖中低压配电、UPS 与发电机冗余、2N 架构可靠性、高密度/液冷机柜供电与容量规划。AI 算力需求使该岗成为电气工程中薪资与需求都极高的方向。",
     "sum_en": "Data centre electrical engineers design and operate power distribution — MV/LV distribution, UPS and generator redundancy, 2N reliability, high-density/liquid-cooled rack power and capacity planning. AI compute demand makes this one of the highest-paid, most in-demand electrical specialisations.",
     "growth": ["超大规模/AI 数据中心供电设计", "关键供电冗余(UPS/发电机/2N)与可靠性", "液冷/高密度机柜供电与散热配合", "数据中心并网与容量规划", "关键设施(Critical Facilities)电气运维"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (6, "中等"),
           "job_demand": (10, "极高"), "competition": (3, "极低"), "work_intensity": (7, "较高"),
           "income_level": (9, "高"), "future_prospect": (10, "极好"), "ai_risk": (3, "低")}},
    {"key": "PNC", "zh": "保护与控制工程师", "en": "Protection & Control Engineer", "family": "eng", "cat": "Engineering & Infrastructure",
     "tier": "eng", "workforce": 3500, "shortage": 1,
     "sum_zh": "保护与控制工程师负责电网变电站的继电保护整定、二次系统与自动化设计、SCADA 与 IEC 61850 通信、以及保护系统调试投运，是保障电网安全稳定运行的关键角色。",
     "sum_en": "Protection & control engineers handle substation relay-protection settings, secondary/automation design, SCADA and IEC 61850 communications, and protection commissioning — a role critical to safe, stable grid operation.",
     "growth": ["变电站保护整定与继电保护(IEC 61850)", "SCADA/自动化与二次系统设计", "可再生并网保护与孤岛检测", "储能/换流站保护与控制", "保护系统调试与现场投运"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (6, "中等"),
           "job_demand": (8, "高"), "competition": (4, "低"), "work_intensity": (6, "中等"),
           "income_level": (8, "较高"), "future_prospect": (9, "很好"), "ai_risk": (3, "低")}},
    {"key": "EVBD", "zh": "电动车电池诊断专家", "en": "EV Battery Diagnostics Specialist", "family": "tech", "cat": "Engineering & Infrastructure",
     "tier": "tech", "workforce": 2000, "shortage": 0,
     "sum_zh": "电动车电池诊断专家负责高压电池组的故障诊断、健康状态(SoH)评估、模组维修与更换，横跨 EV 售后、保修与储能运维，需要高压安全资质与诊断工具经验，是随 EV 保有量上升快速兴起的技术专才岗。",
     "sum_en": "EV battery diagnostics specialists diagnose faults, assess state-of-health (SoH), and repair/replace high-voltage battery modules across EV after-sales, warranty and storage operations — requiring HV safety credentials and diagnostic-tool experience, a fast-emerging technical specialist role.",
     "growth": ["高压电池组诊断与故障定位", "电池健康(SoH)评估与梯次利用", "EV 售后与保修诊断(OEM 体系)", "电池维修与模组更换(高压安全)", "储能电池现场诊断与运维"],
     "R": {"learning_difficulty": (5, "中等"), "learning_duration": (4, "较短"), "certification_difficulty": (5, "中等"),
           "job_demand": (7, "较高"), "competition": (5, "中等"), "work_intensity": (6, "中等"),
           "income_level": (5, "中等"), "future_prospect": (8, "很好"), "ai_risk": (5, "中等")}},
    {"key": "EMB", "zh": "嵌入式/固件工程师", "en": "Embedded / Firmware Engineer", "family": "emb", "cat": "IT & Digital",
     "tier": "emb", "workforce": 12000, "shortage": 1,
     "sum_zh": "嵌入式/固件工程师在微控制器与 SoC 上开发底层软件，涵盖 RTOS/裸机、驱动、通信协议栈、低功耗与固件安全，广泛应用于物联网、汽车、医疗与工业设备，是软硬件交界的高价值岗位。",
     "sum_en": "Embedded/firmware engineers build low-level software on microcontrollers and SoCs — RTOS/bare-metal, drivers, communication stacks, low-power and firmware security — across IoT, automotive, medical and industrial devices, a high-value hardware-software boundary role.",
     "growth": ["物联网(IoT)与边缘设备固件", "汽车/医疗/工业嵌入式(功能安全)", "RTOS 与裸机低功耗开发", "无线通信固件(BLE/LoRa/5G 模组)", "嵌入式安全与 OTA 升级"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (4, "低"),
           "job_demand": (8, "高"), "competition": (5, "中等"), "work_intensity": (6, "中等"),
           "income_level": (8, "较高"), "future_prospect": (9, "很好"), "ai_risk": (4, "中低")}},
    {"key": "FPGA", "zh": "FPGA 工程师", "en": "FPGA Engineer", "family": "semi_top", "cat": "IT & Digital",
     "tier": "semi_top", "workforce": 800, "shortage": 1,
     "sum_zh": "FPGA 工程师用 Verilog/VHDL 在可编程逻辑器件上实现高性能数字电路，涵盖信号处理、低延迟计算与硬件加速，主要就业于国防航天、高频交易与半导体/通信公司，岗位稀缺、门槛高、薪资优厚。",
     "sum_en": "FPGA engineers implement high-performance digital circuits on programmable logic using Verilog/VHDL — signal processing, low-latency compute and hardware acceleration — mainly in defence/aerospace, HFT and semiconductor/telecom firms; scarce, demanding and well-paid.",
     "growth": ["国防与航天信号处理(雷达/SDR)", "高频交易(HFT)低延迟 FPGA", "视频/图像与 AI 加速(边缘推理)", "通信基带与 5G/卫星", "FPGA 原型验证与 SoC 加速"],
     "R": {"learning_difficulty": (9, "很高"), "learning_duration": (8, "长"), "certification_difficulty": (4, "低"),
           "job_demand": (6, "中等"), "competition": (4, "低"), "work_intensity": (6, "中等"),
           "income_level": (9, "高"), "future_prospect": (8, "很好"), "ai_risk": (3, "低")}},
    {"key": "ASIC", "zh": "ASIC 芯片设计工程师", "en": "ASIC Design Engineer", "family": "semi_top", "cat": "IT & Digital",
     "tier": "semi_top", "workforce": 400, "shortage": 1,
     "sum_zh": "ASIC 设计工程师负责专用集成电路的数字前端(RTL 设计/综合)或后端(物理设计/时序收敛)，面向 SoC、AI 加速器与专用芯片，是稀缺、高门槛、高薪的深科技岗位。",
     "sum_en": "ASIC design engineers handle the digital front-end (RTL/synthesis) or back-end (physical design/timing closure) of application-specific chips for SoCs, AI accelerators and specialised silicon — a scarce, high-barrier, high-pay deep-tech role.",
     "growth": ["数字前端 RTL 设计与综合", "低功耗/高性能 SoC 设计", "AI 加速器与专用芯片(ASIC)", "后端物理设计与时序收敛", "芯片初创与无晶圆(fabless)设计"],
     "R": {"learning_difficulty": (9, "很高"), "learning_duration": (9, "很长"), "certification_difficulty": (4, "低"),
           "job_demand": (5, "中等偏低"), "competition": (4, "低"), "work_intensity": (7, "较高"),
           "income_level": (9, "高"), "future_prospect": (8, "很好"), "ai_risk": (3, "低")}},
    {"key": "AMS", "zh": "模拟/混合信号 IC 设计工程师", "en": "Analog / Mixed-Signal IC Design Engineer", "family": "semi_top", "cat": "IT & Digital",
     "tier": "semi_top", "workforce": 300, "shortage": 1,
     "sum_zh": "模拟/混合信号 IC 设计工程师设计芯片中的模拟与数模混合模块，如 ADC/DAC、PLL、电源管理(PMIC)、射频前端与高速接口，是公认最难自动化、最依赖经验直觉的芯片设计方向，专家极为稀缺。",
     "sum_en": "Analog/mixed-signal IC design engineers design the analog and mixed-signal blocks in chips — ADC/DAC, PLLs, power management, RF front-ends and high-speed interfaces — the hardest to automate and most experience-driven area of chip design, with extremely scarce experts.",
     "growth": ["数据转换器(ADC/DAC)与 PLL/时钟", "电源管理 IC(PMIC)与 LDO", "射频/无线前端(RFIC)", "传感器接口与信号链", "SerDes 与高速模拟接口"],
     "R": {"learning_difficulty": (10, "极高"), "learning_duration": (9, "很长"), "certification_difficulty": (4, "低"),
           "job_demand": (5, "中等偏低"), "competition": (3, "极低"), "work_intensity": (7, "较高"),
           "income_level": (9, "高"), "future_prospect": (8, "很好"), "ai_risk": (2, "极低")}},
    {"key": "ICV", "zh": "IC 验证工程师", "en": "IC Verification Engineer", "family": "semi", "cat": "IT & Digital",
     "tier": "semi", "workforce": 600, "shortage": 1,
     "sum_zh": "IC 验证工程师在芯片流片前用 SystemVerilog/UVM 搭建验证环境、编写测试平台、做覆盖率驱动与形式化验证，确保设计符合规格。验证工作量通常占芯片开发一半以上，岗位比设计更多，是进入半导体行业相对可行的高薪路径。",
     "sum_en": "IC verification engineers build verification environments and testbenches in SystemVerilog/UVM and run coverage-driven and formal verification before tape-out. Verification typically takes over half of chip-development effort and roles outnumber design roles — a relatively feasible high-paid route into semiconductors.",
     "growth": ["UVM/SystemVerilog 功能验证", "覆盖率驱动与形式化验证", "SoC 级验证与仿真环境", "低功耗/安全验证(UPF、ISO 26262)", "验证方法学与自动化(含 AI 辅助)"],
     "R": {"learning_difficulty": (8, "高"), "learning_duration": (8, "长"), "certification_difficulty": (4, "低"),
           "job_demand": (6, "中等"), "competition": (4, "低"), "work_intensity": (7, "较高"),
           "income_level": (8, "较高"), "future_prospect": (8, "很好"), "ai_risk": (3, "低")}},
]

# ============================ 薪资档（本币，单位千）：SAL[cc][tier] = (jr_lo,jr_hi, mid_lo,mid_hi, sr_lo,sr_hi) ============================
SAL = {
    "NZ": {"top_eng": (95,120,125,160,160,195), "eng": (90,110,110,145,145,180), "eng_low": (80,100,100,135,135,165),
           "semi_top": (95,120,120,150,150,185), "semi": (90,115,115,145,145,175), "emb": (80,105,105,135,135,170), "tech": (58,75,75,98,98,120)},
    "CA": {"top_eng": (85,110,110,145,145,180), "eng": (80,105,105,140,140,175), "eng_low": (72,95,95,125,125,155),
           "semi_top": (90,115,115,150,150,190), "semi": (85,110,110,145,145,175), "emb": (80,105,105,135,135,165), "tech": (55,72,72,95,95,118)},
    "US": {"top_eng": (95,125,125,165,165,210), "eng": (85,115,115,150,150,190), "eng_low": (78,105,105,140,140,175),
           "semi_top": (120,155,155,200,200,250), "semi": (110,140,140,180,180,225), "emb": (95,125,125,160,160,200), "tech": (55,75,75,100,100,125)},
    "UK": {"top_eng": (45,58,58,78,78,100), "eng": (38,50,50,70,70,90), "eng_low": (35,46,46,62,62,80),
           "semi_top": (40,55,55,75,75,100), "semi": (38,52,52,70,70,92), "emb": (35,48,48,65,65,85), "tech": (26,35,35,45,45,58)},
    "DE": {"top_eng": (52,65,65,85,85,105), "eng": (48,60,60,80,80,100), "eng_low": (45,56,56,72,72,90),
           "semi_top": (55,70,70,90,90,110), "semi": (52,66,66,84,84,102), "emb": (48,60,60,78,78,95), "tech": (35,45,45,58,58,72)},
    "FR": {"top_eng": (42,55,55,72,72,92), "eng": (39,52,52,68,68,88), "eng_low": (37,48,48,62,62,80),
           "semi_top": (42,55,55,75,75,95), "semi": (40,52,52,68,68,88), "emb": (38,50,50,65,65,82), "tech": (28,38,38,48,48,62)},
    "ES": {"top_eng": (32,42,42,56,56,72), "eng": (28,38,38,52,52,68), "eng_low": (26,35,35,48,48,62),
           "semi_top": (32,42,42,58,58,78), "semi": (30,40,40,54,54,70), "emb": (28,38,38,52,52,68), "tech": (20,28,28,38,38,50)},
}

# ============================ 分类码映射：CODE[cc] = (type, {family_group: code}) ============================
# family_group: PWR=电力/电气 ELEC=电子/半导体 EMB=嵌入式 TECH=技术员
CODE = {
    "NZ": ("ANZSCO", {"PWR": "233311", "ELEC": "233411", "EMB": "261313", "TECH": "312412"}),
    "CA": ("NOC",    {"PWR": "21310",  "ELEC": "21310",  "EMB": "21311",  "TECH": "22310"}),
    "US": ("SOC",    {"PWR": "17-2071","ELEC": "17-2072","EMB": "17-2061","TECH": "17-3023"}),
    "UK": ("SOC",    {"PWR": "2123",   "ELEC": "2124",   "EMB": "2124",   "TECH": "3113"}),
    "DE": ("KldB",   {"PWR": "2630",   "ELEC": "2630",   "EMB": "2630",   "TECH": "2620"}),
    "FR": ("ROME",   {"PWR": "H1202",  "ELEC": "H1202",  "EMB": "M1805",  "TECH": "I1305"}),
    "ES": ("CNO",    {"PWR": "2441",   "ELEC": "2442",   "EMB": "2442",   "TECH": "3132"}),
}
# role.key -> family_group（用于取码）
ROLE_GROUP = {"PWR": "PWR", "BESS": "PWR", "EVCI": "PWR", "DCE": "PWR", "PNC": "PWR",
              "EVBD": "TECH", "EMB": "EMB", "FPGA": "ELEC", "ASIC": "ELEC", "AMS": "ELEC", "ICV": "ELEC"}

# ============================ 各国配置 ============================
COUNTRY = {
    "NZ": {"zh": "新西兰", "cur": "NZD", "body": "Engineering New Zealand",
           "visa_eng": [("Green List", "技能紧缺清单直通居留", "Green List（技能紧缺）：电气/软件工程符合条件可直接申请居留（Straight to Residence）"),
                        ("AEWV", "认可雇主工签", "Accredited Employer Work Visa：雇主担保工签"),
                        ("SMC", "技术移民居留", "Skilled Migrant Category：积分制技术移民居留")],
           "visa_tech": [("AEWV", "认可雇主工签", "Accredited Employer Work Visa：技术员岗主要走雇主担保"),
                         ("SMC", "技术移民居留", "Skilled Migrant Category：积分制，技术员岗积分较低")],
           "pr_eng": (9, "高", "电气/软件工程多在 Green List，可直通居留"), "pr_diff_eng": (4, "低", "紧缺职业，技术移民较易"),
           "pr_tech": (5, "中等", "技术员岗主要依赖雇主担保"), "pr_diff_tech": (6, "较高", "非 Green List，独立移民较难"),
           "platforms": ["Seek NZ", "Trade Me Jobs", "LinkedIn"],
           "src": [("ERI SalaryExpert", "Power Systems Engineer NZ 约 NZ$143k；入门 $102k、资深 $165k", "https://www.erieri.com/salary/job/power-systems-engineer/new-zealand"),
                   ("SEEK NZ / PayScale", "Firmware/Embedded 约 NZ$110k~$128k；电子工程参考", "https://www.seek.co.nz/career-advice/role/firmware-engineer/salary")]},
    "CA": {"zh": "加拿大", "cur": "CAD", "body": "Engineers Canada / 省工程师协会",
           "visa_eng": [("Express Entry", "联邦快速通道", "Express Entry（FSW/CEC）：电气电子工程师、软件工程师可积分制永居"),
                        ("PNP", "省提名", "Provincial Nominee Program：省提名加分通道"),
                        ("GTS", "全球人才快通", "Global Talent Stream：两周快速工签")],
           "visa_tech": [("PNP", "省提名", "Provincial Nominee Program：技术员岗多走省提名"),
                         ("LMIA 工签", "雇主担保工签", "雇主提供 LMIA 支持的工作签证")],
           "pr_eng": (9, "高", "电气电子/软件工程在 Express Entry 可积分永居"), "pr_diff_eng": (4, "低", "紧缺职业，移民较易"),
           "pr_tech": (5, "中等", "技术员岗多走省提名/雇主担保"), "pr_diff_tech": (6, "较高", "联邦快速通道竞争力较弱"),
           "platforms": ["Job Bank", "Indeed CA", "LinkedIn"],
           "src": [("ERI SalaryExpert", "Power Systems Engineer CA 约 C$126k；入门 $86k、资深 $153k", "https://www.erieri.com/salary/job/power-systems-engineer/canada"),
                   ("Indeed CA / Glassdoor", "FPGA 约 C$114k~$139k；ASIC $94k~$154k；嵌入式 $110k~$130k", "https://ca.indeed.com/career/fpga-engineer/salaries")]},
    "US": {"zh": "美国", "cur": "USD", "body": "州 PE 执照 / NCEES",
           "visa_eng": [("H-1B", "专业工作签证", "H-1B：专业职位工签（抽签制）"),
                        ("O-1", "杰出人才", "O-1：杰出能力工签"),
                        ("EB-2/EB-3", "职业移民绿卡", "EB-2/EB-3：雇主担保职业移民（含 PERM 劳工证）"),
                        ("EB-2 NIW", "国家利益豁免", "EB-2 NIW：国家利益豁免自主申请绿卡")],
           "visa_tech": [("H-1B", "专业工作签证", "H-1B：需学历，技术员岗申请较难"),
                         ("EB-3 Skilled", "技术工绿卡", "EB-3：技术工/技能岗雇主担保绿卡")],
           "pr_eng": (5, "中等", "无积分制，依赖雇主担保与 H-1B 抽签"), "pr_diff_eng": (7, "较高", "H-1B 抽签+绿卡排期，周期长"),
           "pr_tech": (3, "低", "技术员岗签证选择有限"), "pr_diff_tech": (8, "高", "无学历时移民路径很窄"),
           "platforms": ["Indeed US", "Glassdoor", "LinkedIn"],
           "src": [("ERI / Glassdoor", "Power Systems Engineer US 约 $140k（$110k~$181k）；数据中心 $114k~$160k", "https://www.erieri.com/salary/job/power-systems-engineer/united-states"),
                   ("Glassdoor / Salary.com", "ASIC/FPGA 约 $164k~$186k（$153k~$231k）", "https://www.glassdoor.com/Salaries/asic-fpga-design-engineer-salary-SRCH_KO0,25.htm")]},
    "UK": {"zh": "英国", "cur": "GBP", "body": "Engineering Council（CEng/IEng）",
           "visa_eng": [("Skilled Worker", "技术工作签证", "Skilled Worker：雇主担保，工程类为符合职业"),
                        ("Global Talent", "全球人才签证", "Global Talent：科技/工程杰出或潜力人才"),
                        ("HPI", "高潜力人才", "High Potential Individual：顶尖高校毕业生工签")],
           "visa_tech": [("Skilled Worker", "技术工作签证", "Skilled Worker：需达到技能与薪资门槛，技术员岗视具体职位")],
           "pr_eng": (8, "高", "Skilled Worker 通道通畅，工程为符合职业"), "pr_diff_eng": (5, "中低", "需雇主担保，达标后转永居"),
           "pr_tech": (5, "中等", "技术员岗需满足 Skilled Worker 门槛"), "pr_diff_tech": (6, "较高", "薪资/技能门槛限制较多"),
           "platforms": ["Indeed UK", "Reed", "LinkedIn"],
           "src": [("ERI / Glassdoor UK", "Power Systems Engineer UK 约 £45k~£70k（区间 £48k~£85k）", "https://www.erieri.com/salary/job/power-systems-engineer/united-kingdom"),
                   ("IT Jobs Watch / Indeed", "FPGA 中位 £70k；初级 £34k~£48k，资深 £60k~£80k，Lead £75k~£100k", "https://www.itjobswatch.co.uk/jobs/uk/fpga%20engineer.do")]},
    "DE": {"zh": "德国", "cur": "EUR", "body": "学历认证（Anabin）/ VDI",
           "visa_eng": [("EU Blue Card", "欧盟蓝卡", "EU Blue Card：高薪+学历工程师快速永居通道"),
                        ("Skilled Worker", "技术工签证", "Fachkräfte 技术工签证：认可学历+工作合同"),
                        ("Opportunity Card", "机会卡", "Chancenkarte：积分制求职签证")],
           "visa_tech": [("Skilled Worker", "技术工签证", "Fachkräfte：职业资格认证(Anerkennung)后可担保"),
                         ("Opportunity Card", "机会卡", "Chancenkarte：积分制求职签证")],
           "pr_eng": (8, "高", "工程师符合欧盟蓝卡，永居通道快"), "pr_diff_eng": (4, "低", "蓝卡持有者最快 21~27 个月永居"),
           "pr_tech": (6, "中等", "职业资格认证后可走技术工签证"), "pr_diff_tech": (6, "较高", "需完成学历/资格认证"),
           "platforms": ["StepStone", "Indeed DE", "LinkedIn"],
           "src": [("Glassdoor / PayScale DE", "FPGA 约 €67.5k（€59k~€79k，顶 €89k）；嵌入式 €57k", "https://www.glassdoor.com/Salaries/germany-fpga-engineer-salary-SRCH_IL.0,7_IN96_KO8,21.htm"),
                   ("germantechjobs / levels.fyi", "资深 FPGA/模拟在 ST/NXP 可超 €85k", "https://germantechjobs.de/en/salaries/Embedded/all/all")]},
    "FR": {"zh": "法国", "cur": "EUR", "body": "学历认证（ENIC-NARIC）",
           "visa_eng": [("Passeport Talent", "人才护照", "Passeport Talent（salarié qualifié）：合格工程师多年居留"),
                        ("Salarié", "受雇居留", "Carte de séjour salarié：雇主合同工作居留")],
           "visa_tech": [("Salarié", "受雇居留", "Carte de séjour salarié：技术员岗以雇主合同为主"),
                         ("Travailleur", "临时工作", "Travailleur temporaire 临时工作居留，路径较受限")],
           "pr_eng": (7, "较高", "Passeport Talent 面向合格工程师，通道尚可"), "pr_diff_eng": (5, "中低", "需雇主与薪资门槛"),
           "pr_tech": (4, "中低", "技术员岗主要依赖雇主合同"), "pr_diff_tech": (7, "较高", "无 Passeport Talent 资格，路径受限"),
           "platforms": ["Indeed FR", "APEC", "LinkedIn"],
           "src": [("talent.com / Glassdoor FR", "电子工程中位约 €63k（起步 €39k，资深 FPGA/模拟 >€85k）", "https://fr.talent.com/salary?job=ingenieur+electronique+fpga"),
                   ("Glassdoor FR", "数据中心工程师约 €51.5k（€43k~€60k）", "https://www.glassdoor.fr/Salaires/ingenieur-datacenter-salaire-SRCH_KO0,20.htm")]},
    "ES": {"zh": "西班牙", "cur": "EUR", "body": "学历认证（homologación）",
           "visa_eng": [("PAC Ley 14/2013", "高技能专业人才", "Profesional Altamente Cualificado（Ley 14/2013）高技能专业人才居留"),
                        ("Tarjeta Azul UE", "欧盟蓝卡", "EU Blue Card：高薪+学历工程师通道"),
                        ("Cuenta ajena", "受雇工作", "受雇工作居留许可")],
           "visa_tech": [("Cuenta ajena", "受雇工作", "受雇工作居留许可，技术员岗为主"),
                         ("Arraigo", "扎根居留", "长期居住后的扎根社会/劳动通道")],
           "pr_eng": (6, "中等", "高技能专业人才/蓝卡通道，但整体名额有限"), "pr_diff_eng": (6, "较高", "薪资门槛与名额限制"),
           "pr_tech": (4, "中低", "技术员岗以受雇工作许可为主"), "pr_diff_tech": (7, "较高", "独立技术移民路径有限"),
           "platforms": ["InfoJobs", "Indeed ES", "LinkedIn"],
           "src": [("talent.com / Indeed ES", "电子工程师约 €38k；系统工程师约 €46k；电气 €26k~€32k", "https://es.talent.com/salary?job=ingeniero+electronico"),
                   ("Indeed ES", "资深半导体/FPGA 在 Indra/Minsait 等高于均值", "https://es.indeed.com/career/ingeniero-electronico/salaries")]},
}

# ============================ 生成器 ============================
FAMILY_FC = {  # 市场前景 forecast（{c}=国家，{r}=职业中文名）
    "eng": "在{c}，能源转型、电网升级与数据中心建设推动电力工程需求，{r}中长期需求向好，资深并网/合规人才紧缺。",
    "eng_low": "在{c}，电动车渗透与充电网络铺设推动需求上行，{r}绑定电气工程紧缺趋势，前景良好。",
    "top_eng": "在{c}，AI 算力引爆数据中心建设，{r}供不应求，是电气工程中薪资与需求都极高的方向。",
    "semi_top": "在{c}，全球芯片自主与 AI 加速需求外溢，{r}岗位稀缺、供给更少，资深人才紧俏、薪资位于电子工程高端。",
    "semi": "在{c}，芯片复杂度上升使验证需求增长，{r}通常多于设计岗，是进入半导体相对可行的高薪路径。",
    "emb": "在{c}，设备联网化与汽车/医疗/国防电子推动嵌入式需求，{r}供需偏紧，前景稳健。",
    "tech": "在{c}，电动车保有量上升带来电池售后与诊断需求，{r}熟手短缺；作为技术员岗，技术移民路径较受限。",
}
FAMILY_TR = {  # 趋势 trend
    "eng": "{c}风光储并网、电网数字化与算力扩张持续，掌握并网/稳定性/合规的工程师最抢手；AI 辅助分析，电网安全责任仍由持证工程师承担。",
    "eng_low": "{c}超快充与车队充电成为热点，站点常需配电升级与储能削峰；AI 辅助选址与负荷预测，核心电气设计与合规由工程师完成。",
    "top_eng": "{c} AI 数据中心以高密度供电与液冷为特征，2N 冗余与可靠性设计是核心；AI 辅助监控，供电可靠性责任由工程师承担。",
    "semi_top": "{c} AI 加速器与低功耗/模拟设计为主线，掌握 RTL/时序/版图的工程师稀缺；AI 辅助有限，架构与流片责任高度专业。",
    "semi": "{c} SoC 级验证、低功耗与安全验证成为重点；AI 提升测试生成与调试效率，方法学与覆盖率收敛仍由工程师主导。",
    "emb": "{c}边缘 AI、功能安全与设备安全成为热点，懂底层调试与实时约束的固件工程师稀缺；AI 生成样板，硬件底层仍依赖人。",
    "tech": "{c}高压电池诊断与健康评估成为热点，掌握 OEM 诊断与高压安全者抢手；诊断读数可自动化，高压拆装与判断仍需人工。",
}
FAMILY_FC_EN = {
    "eng": "In {c}, the energy transition, grid upgrades and data-centre build-out drive demand for power engineering; {r} has a solid medium-to-long-term outlook with senior grid-connection/compliance talent in short supply.",
    "eng_low": "In {c}, EV uptake and charging-network roll-out push demand up; {r} is tied to the electrical-engineering shortage with a good outlook.",
    "top_eng": "In {c}, AI compute has ignited data-centre construction; {r} is in severe shortage and one of the highest-paid, most in-demand electrical specialisations.",
    "semi_top": "In {c}, global chip-sovereignty and AI-acceleration demand spill over; {r} roles are scarce with even scarcer supply, keeping senior talent well-paid at the top of electronics engineering.",
    "semi": "In {c}, rising chip complexity grows verification demand; {r} roles usually outnumber design roles — a relatively feasible high-paid route into semiconductors.",
    "emb": "In {c}, device connectivity and automotive/medical/defence electronics drive embedded demand; {r} sits in tight supply with a steady outlook.",
    "tech": "In {c}, a growing EV fleet drives battery after-sales and diagnostics demand; {r} lacks skilled hands. As a technician role, skilled-migration pathways are more limited.",
}
FAMILY_TR_EN = {
    "eng": "{c}'s renewable connection, grid digitalisation and compute expansion continue; engineers skilled in grid connection, stability and compliance are most sought-after. AI assists analysis, but grid-safety accountability stays with chartered engineers.",
    "eng_low": "In {c}, ultra-fast and fleet charging are hotspots; sites often need distribution upgrades and storage. AI assists siting and load forecasting, but core electrical design and compliance are engineer-led.",
    "top_eng": "{c}'s AI data centres feature high-density power and liquid cooling; 2N redundancy and reliability design are core. AI assists monitoring, but power-reliability accountability stays with engineers.",
    "semi_top": "In {c}, AI accelerators and low-power/analog design lead; engineers strong in RTL, timing and layout are scarce. AI's help is limited, and architecture and tape-out accountability stay highly specialised.",
    "semi": "In {c}, SoC-level, low-power and safety verification are focal points; AI boosts test generation and debug, but methodology and coverage closure stay engineer-led.",
    "emb": "In {c}, edge AI, functional safety and device security are hotspots; firmware engineers strong in low-level debugging and real-time constraints are scarce. AI generates boilerplate, but hardware-level work stays human.",
    "tech": "In {c}, HV battery diagnostics and state-of-health assessment are hotspots; those fluent in OEM diagnostics and HV safety are sought-after. Tools automate data reads, but HV disassembly and judgement stay manual.",
}


def money(n, cur):
    sym = {"USD": "$", "CAD": "$", "NZD": "$", "AUD": "$", "GBP": "£", "EUR": "€"}.get(cur, "")
    return f"{sym}{n*1000:,.0f}"


def salaries_for(role, cc):
    t = SAL[cc][role["tier"]]
    cur = COUNTRY[cc]["cur"]
    labels = ["初级（0~3 年）", "中级（3~7 年）", "资深/主任（8 年+）"]
    notes = ["起薪，随雇主与地区", "行业中位区间", "资深/专家，含项目津贴"]
    if role["tier"] == "tech":
        labels = ["初级/技术员（0~3 年）", "诊断专家（3~7 年）", "资深/主管（8 年+）"]
    out = []
    for i in range(3):
        lo, hi = t[i*2], t[i*2+1]
        out.append({"experience": labels[i], "salary_min": lo*1000, "salary_max": hi*1000,
                    "salary_note": f"{notes[i]}（{money(lo,cur)}~{money(hi,cur)}）", "sort_order": i})
    return out


def ratings_for(role, cc):
    C = COUNTRY[cc]
    is_tech = role["tier"] == "tech"
    R = []
    for dim, (stars, label) in role["R"].items():
        R.append({"dimension": dim, "label_zh": label, "stars": stars, "note": None})
    prf = C["pr_tech"] if is_tech else C["pr_eng"]
    prd = C["pr_diff_tech"] if is_tech else C["pr_diff_eng"]
    R.append({"dimension": "pr_friendliness", "label_zh": prf[1], "stars": prf[0], "note": prf[2]})
    R.append({"dimension": "pr_difficulty", "label_zh": prd[1], "stars": prd[0], "note": prd[2]})
    return R


def edu_for(role, cc):
    C = COUNTRY[cc]
    if role["tier"] == "tech":
        return [
            {"stage": "汽车电气/机电 Certificate 或电子技术文凭", "duration": "1~2 年", "cost_min": 3000, "cost_max": 20000, "cost_note": "职业院校/技术学院；EV 高压方向加分", "sort_order": 0},
            {"stage": "高压电动车安全资质（HV/De-energise）", "duration": "数天~数周", "cost_min": 500, "cost_max": 3000, "cost_note": "高压电池作业法定安全要求", "sort_order": 1},
            {"stage": f"学历/资格认证（{C['body']}）与 OEM 诊断培训", "duration": "数周~数月", "cost_min": 800, "cost_max": 8000, "cost_note": "海外从业需完成认证；品牌诊断体系", "sort_order": 2},
        ]
    if role["family"] in ("semi_top", "semi", "emb"):
        deg = "电子/微电子/计算机工程学位（部分岗位需硕士）"
    else:
        deg = "电气/电力/机电工程学位"
    return [
        {"stage": f"认可{deg}", "duration": "4~6 年", "cost_min": 20000, "cost_max": 200000, "cost_note": "本地生较低，国际生较高", "sort_order": 0},
        {"stage": "专业方向进阶（仿真/RTL/验证/储能等）", "duration": "6~24 个月", "cost_min": 2000, "cost_max": 40000, "cost_note": "岗位核心工具链与方法学实操", "sort_order": 1},
        {"stage": f"学历认证/职业评估（{C['body']}）", "duration": "2~6 个月", "cost_min": 500, "cost_max": 3000, "cost_note": "技术移民与执业所需", "sort_order": 2},
    ]


def quals_for(role, cc):
    C = COUNTRY[cc]
    if role["tier"] == "tech":
        return [
            {"qual_name": "高压电动车作业安全资质（HV/De-energise）", "issuer": "认可培训机构 / OEM", "note": "高压电池作业法定安全门槛", "is_mandatory": 1, "sort_order": 0},
            {"qual_name": f"学历/资格认证（{C['body']}）", "issuer": C["body"], "note": "海外从业者本地化门槛", "is_mandatory": 1, "sort_order": 1},
            {"qual_name": "OEM 诊断系统认证", "issuer": "各汽车厂商", "note": "售后与保修诊断岗常要求", "is_mandatory": 0, "sort_order": 2},
        ]
    return [
        {"qual_name": f"认可工程学位 / 学历认证（{C['body']}）", "issuer": C["body"], "note": "执业与技术移民评估基础", "is_mandatory": 1, "sort_order": 0},
        {"qual_name": "岗位核心工具/方法学能力", "issuer": "项目实践", "note": "如并网仿真、RTL/时序、UVM 验证、储能标准等", "is_mandatory": 0, "sort_order": 1},
    ]


def jobs_for(role, cc):
    C = COUNTRY[cc]
    p = C["platforms"]
    # 半导体/技术员岗数量偏少
    if role["family"] in ("semi_top",):
        base = [(5, 40), (10, 50), (15, 70)]
    elif role["family"] in ("semi",):
        base = [(8, 50), (15, 60), (20, 80)]
    elif role["tier"] == "tech":
        base = [(80, 300), (60, 250), (80, 250)]
    else:
        base = [(150, 500), (100, 350), (200, 600)]
    return [{"platform": p[i], "count_min": base[i][0], "count_max": base[i][1],
             "note": f"{role['zh']}及相邻岗位（{C['zh']}）"} for i in range(3)]


def faqs_for(role, cc):
    C = COUNTRY[cc]
    cur = C["cur"]
    t = SAL[cc][role["tier"]]
    jr = f"{money(t[0],cur)}~{money(t[1],cur)}"
    sr = f"{money(t[4],cur)}~{money(t[5],cur)}"
    is_tech = role["tier"] == "tech"
    mig_q = f"{role['zh']}能在{C['zh']}技术移民吗？"
    if is_tech:
        mig_a = f"较难独立移民。作为技术员级岗位路径受限，主要依赖雇主担保等通道，建议先在{C['zh']}就业积累再推进。"
        rec_a = f"需取得{C['zh']}本地资质与高压电动车安全资质；海外 EV 诊断经验有帮助，但高压作业资质是硬门槛（{C['body']}）。"
        ai_a = "部分。诊断读数与故障码分析可自动化，但高压电池拆装、模组更换与现场安全判断仍需人工，属人机协作。"
    else:
        mig_a = f"能。归入紧缺工程职业，可走{C['zh']}对应的技术移民/雇主担保通道；具体门槛见签证表。"
        rec_a = f"海外学历需经{C['body']}认证/评估；岗位核心工具与项目经验是直接加分项。"
        ai_a = "风险低。AI 辅助分析与生成，但工程设计、安全合规与责任判断由持证工程师承担，属 AI 增强型岗位。"
    return [
        {"faq_type": "salary", "sort_order": 0, "question": f"{C['zh']}{role['zh']}工资多少？",
         "answer": f"初级约 {jr}；资深约 {sr}（{cur}）。薪资随地区、行业与项目而定，具体见薪资表。"},
        {"faq_type": "demand", "sort_order": 1, "question": f"{role['zh']}在{C['zh']}需求怎样？",
         "answer": FAMILY_FC[role["family"]].format(c=C["zh"], r=role["zh"])},
        {"faq_type": "recognition", "sort_order": 2, "question": f"海外经验在{C['zh']}认可吗？", "answer": rec_a},
        {"faq_type": "ai_risk", "sort_order": 3, "question": f"{role['zh']}会被 AI 替代吗？", "answer": ai_a},
        {"faq_type": "difficulty", "sort_order": 4, "question": mig_q, "answer": mig_a},
    ]


FIT_ENG = ["相关工程背景，愿深耕能源/半导体新兴方向", "掌握或愿学岗位核心工具与方法学", "希望进入长期增长赛道并考虑技术移民", "细致、责任心强，能承担工程判断"]
UNFIT_ENG = ["数理/工程基础薄弱且不愿长期投入", "排斥标准、合规与安全为核心的工程工作", "期望短期速成、不接受多年经验积累"]
FIT_TECH = ["有汽车电气/机电或电子技术背景，想切入 EV 电池方向", "愿意考取高压安全资质并做现场诊断", "对电池健康评估、故障定位与维修有兴趣", "接受以雇主担保为主的移民路径"]
UNFIT_TECH = ["排斥动手维修与高压作业风险", "希望走独立技术移民的快速通道（此岗受限）", "不愿学习 OEM 诊断系统与安全规程"]


def build_occ(role, cc):
    C = COUNTRY[cc]
    ctype, cmap = CODE[cc]
    code = cmap[ROLE_GROUP[role["key"]]]
    is_tech = role["tier"] == "tech"
    occ = {"country_code": cc, "occ_code": f"{code}-{role['key']}", "occ_code_type": ctype, "anzsco_code": code,
           "anzsco_title": role["en"], "category": role["cat"], "currency": C["cur"],
           "workforce_size": role["workforce"], "shortage_listed": role["shortage"],
           "is_migration": 2 if is_tech else 1,
           "growth_areas": json.dumps(role["growth"], ensure_ascii=False)}
    zh = {"locale": "zh-CN", "name": role["zh"], "summary": role["sum_zh"],
          "forecast_note": FAMILY_FC[role["family"]].format(c=C["zh"], r=role["zh"]),
          "trend_summary": FAMILY_TR[role["family"]].format(c=C["zh"])}
    en = {"locale": "en", "name": role["en"], "summary": role["sum_en"],
          "forecast_note": FAMILY_FC_EN[role["family"]].format(c=C["zh"], r=role["en"]).replace(C["zh"], {"新西兰":"New Zealand","加拿大":"Canada","美国":"the US","英国":"the UK","德国":"Germany","法国":"France","西班牙":"Spain"}[C["zh"]]),
          "trend_summary": FAMILY_TR_EN[role["family"]].format(c={"新西兰":"New Zealand","加拿大":"Canada","美国":"the US","英国":"the UK","德国":"Germany","法国":"France","西班牙":"Spain"}[C["zh"]])}
    visas = C["visa_tech"] if is_tech else C["visa_eng"]
    VISA = [{"visa_subclass": v[0][:20], "visa_name": v[1], "description": v[2], "sort_order": i} for i, v in enumerate(visas)]
    fit = FIT_TECH if is_tech else FIT_ENG
    unfit = UNFIT_TECH if is_tech else UNFIT_ENG
    SOURCES = [{"source_name": s[0], "content": s[1], "url": s[2]} for s in C["src"]]
    return occ, zh, en, edu_for(role, cc), quals_for(role, cc), jobs_for(role, cc), salaries_for(role, cc), VISA, ratings_for(role, cc), fit, unfit, SOURCES, faqs_for(role, cc)


def run(countries):
    total = 0
    with get_cursor() as cur:
        for cc in countries:
            for role in ROLES:
                args = build_occ(role, cc)
                oid = seed_occupation_v2(cur, *args)
                total += 1
            print(f"[{cc}] {len(ROLES)} 个职业入库完成")
    print(f"\n[OK] 共入库 {total} 条（{len(countries)} 国 × {len(ROLES)} 职业）")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="NZ,CA,US,UK,DE,FR,ES")
    a = ap.parse_args()
    run([c.strip() for c in a.countries.split(",") if c.strip()])
