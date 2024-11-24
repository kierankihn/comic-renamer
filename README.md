# Comic-Renamer 漫画重命名工具

## 用前必读

当前由于 Bangumi 本身搜索排序质量不佳（see https://github.com/bangumi/server/issues/229 ），所以可能匹配出的第一个条目不正确（特别是存在外传的情况下），这种情况下需要手动进行修改

同时，请尽量保证在重命名之后，使用你的新文件名可以在 Bangumi 上搜索到正确条目，否则如果你想要将当前命名格式再次修改的时候，将无法用这个脚本进行再次重命名

由于每次重命名都需要请求两次 Bangumi 的相关 API，可能重命名速度会很慢

当前由于 Bangumi 的 API 在未搜索到信息的时候可能会返回 API 速率限制错误（see https://github.com/bangumi/api/issues/43 ），所以你看到的程序抛出的 rate error 可能并不是真的速率限制，而是没有搜索到信息

使用之前请确保已经安装 Python 和需要的依赖

## 用法

目前已有 GUI 版本（原谅我第一次用 Python 写 GUI 写的很难看）

新版本增加了是否使用台版出版社的选项，默认不使用，勾选之后会增加本地 `data.json` 文件中的出版社的权重，默认写了 12 个出版社（[数据来源](https://bgm.tv/index/58593)），可以自行修改 / 添加你想要的出版社

你可以勾选 `Show More Logs` 选项来开启 `DEBUG` 日志，开启后会输出网络日志和重命名的日志

`format` 支持的替换信息：
- `name`: 日文标题
- `namecn`: 中文标题
- `author`: 作者名字
- `press`: 出版社

## To-do

- [ ] 添加本地数据库查询支持