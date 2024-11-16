# Comic-Renamer 漫画重命名工具

## 用前必读

当前由于 Bangumi 本身搜索排序质量不佳（see https://github.com/bangumi/server/issues/229 ），所以可能匹配出的第一个条目不正确（特别是存在外传的情况下），这种情况下需要手动进行修改

同时，请尽量保证在重命名之后，使用你的新文件名可以在 Bangumi 上搜索到正确条目，否则如果你想要将当前命名格式再次修改的时候，将无法用这个脚本进行再次重命名

由于每次重命名都需要请求两次 Bangumi 的相关 API，可能重命名速度会很慢

当前由于 Bangumi 的 API 在未搜索到信息的时候可能会返回 API 速率限制错误（see https://github.com/bangumi/api/issues/43），所以你看到的程序抛出的 rate error 可能并不是真的速率限制，而是没有搜索到信息

使用之前请确保已经安装 Python 和需要的依赖

## 用法

```
usage: main.py [-h] [-f FORMAT] path

自动重命名本地漫画文件

positional arguments:
  path                  本地文件夹位置

options:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        命名方式，可使用 {name}, {namecn}, {author}, {press} 进行替换
```

例子：

```
./main.py /path/to/folder -f '{namecn} {author}'
```

这会将指定目录下的所有**可以在 bgm.tv 上搜索到的**漫画（文件 / 文件夹）全部重命名为 `中文名 作者名` 的格式，其余搜索不到的文件则不做修改

支持的替换信息：
- `name`: 日文标题
- `namecn`: 中文标题
- `author`: 作者名字
- `press`: 出版社

## To-do

- [ ] 添加本地数据库查询支持