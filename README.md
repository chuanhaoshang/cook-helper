# 做饭助手 · Cook Helper

纯静态网页：今天吃什么、食材找菜、搜菜谱。数据来自开源项目 [HowToCook](https://github.com/Anduin2017/HowToCook)（Unlicense）。
没有后端、不需要登录；收藏、忌口等设置只存在你自己浏览器里。

## 致谢

所有菜谱内容来自开源项目 [HowToCook](https://github.com/Anduin2017/HowToCook)（作者 Anduin2017 及众多贡献者，Unlicense 协议）。网页底部已写明致谢并链接原项目，每道菜的详情页也有"查看原文"链接。**发布时请保留这些致谢。** 本项目是基于该数据的非官方检索工具，与原项目无隶属关系。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 整个网页（界面 + 逻辑），中英文界面可切换 |
| `recipes.js` | 菜谱数据（373 道），由脚本生成 |
| `build_data.py` | 把 HowToCook 的 Markdown 解析成 `recipes.js` |
| `aliases.json` | 食材同义词和英文名（西红柿=番茄 等），可以自己改 |
| `basics.json` | 默认"家里一定有"的基础调料 |

## 部署到 GitHub Pages（免费，手机也能访问）

1. 登录 GitHub，右上角 **+ → New repository**，名字随便取（例如 `cook-helper`），选 **Public**，创建。
2. 在新仓库页面点 **uploading an existing file**，把 `index.html`、`recipes.js` 拖进去（其他文件也可以一起传），点 **Commit changes**。
3. 进入仓库 **Settings → Pages**。在 **Build and deployment** 里，Source 选 **Deploy from a branch**，Branch 选 `main`，文件夹选 `/ (root)`，点 **Save**。
4. 等一两分钟，页面顶部会显示网址：`https://你的用户名.github.io/cook-helper/`。用手机打开，再"添加到主屏幕"就像 app 一样。

> 只想本地看：把 `index.html` 和 `recipes.js` 放在同一个文件夹，双击 `index.html` 即可。

## 更新菜谱数据（HowToCook 上游有新菜时）

需要电脑上装有 Python 3 和 git：

```bash
git clone --depth 1 https://github.com/Anduin2017/HowToCook.git
python3 build_data.py ./HowToCook recipes.js
```

脚本最后会打印"还没有同义词的食材"，把常见的补进 `aliases.json`（格式：标准名 → 同义词列表 + 英文名），重新运行即可。再把新的 `recipes.js` 上传覆盖。

## 已知限制

- **菜谱正文只有中文**。英文模式下，界面和常见食材名（约 100 个）是英文，没有英文名的食材显示中文。
- **用量没有按人数换算**。原文的用量写法不统一，页面只原样展示"每份用量"。购物清单只列出缺哪些食材，不算克数。
- **食材匹配靠名称**。同义词表覆盖了常见食材，冷门写法可能漏匹配，补 `aliases.json` 即可。
- **忌口 / 素食 / 过敏过滤是关键词判断，不保证 100% 准确**，有过敏请自己核对原文。
- 部分菜谱（如速冻水饺、炸薯条）原文没有标准的"必备原料"清单，食材反查时不会出现。
