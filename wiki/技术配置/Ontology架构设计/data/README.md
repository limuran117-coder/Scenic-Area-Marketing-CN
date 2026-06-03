# Ontology 数据目录

```
data/
├── metric_snapshots_YYYYMMDD.json    ← 每日抖音/小红书数据
├── content_assets_YYYYMMDD.json      ← 内容资产
├── events_YYYYMMDD.json              ← 事件/动态
├── links_YYYYMMDD.json               ← 链接关系实例
└── logs/
    ├── adapter-douyin-YYYYMMDD.json       ← 各 adapter 运行日志
    ├── adapter-xiaohongshu-YYYYMMDD.json
    └── daily-work-YYYYMMDD.json           ← 每日工作日志
```

数据定位：所有采集数据经过 adapter 转换为 Ontology 对象后写入此目录。
这些 JSON 文件是知识图谱的"实物层"，wiki 中的 markdown 是"解释层"。
