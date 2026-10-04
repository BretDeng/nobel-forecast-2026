# 知乎 CLI 的 GitHub Actions 验收

2026-10-04 已核验官方发布索引，Linux x64 CLI 0.6.1 可下载；下载包大小、SHA-256、单文件归档和 Linux x86-64 ELF 格式均已通过本机校验。GitHub 托管 Ubuntu 24.04 runner 的实际安装与执行也已通过。

官方知乎 Skill 的 `references/cli.md` 明确规定：CI 使用进程环境变量 `ZHIHU_ACCESS_SECRET`，优先于系统密钥链；无界面 Linux 不需要运行 `auth set` 或配置 Secret Service。已用非真实凭证执行本机 CLI 的离线 `auth status`，确认来源为 `environment`；随后已在 GitHub Ubuntu runner 使用 Actions Secret 完成真实凭证认证及 limit=1 的回答摘要调用。

本项目的同步脚本已支持 `ZHIHU_CLI_BINARY`，后续 Linux 同步时传入安装后的绝对路径即可；Python 子进程会继承 `ZHIHU_ACCESS_SECRET`。无需调用长期运行的本地 `server.mjs`。

## 云端验收步骤

1. 创建 GitHub 仓库，将 `.github/workflows/verify-zhihu-cli.yml` 放到默认分支。
2. 从 <https://developer.zhihu.com/profile> 获取自己的 Access Secret。
3. 在仓库 Settings → Secrets and variables → Actions → New repository secret 中添加 `ZHIHU_ACCESS_SECRET`，值为该 Secret。不要写入源码、聊天或网页。
4. 在 Actions 中选择 **Verify Zhihu CLI on GitHub**，点击 **Run workflow**。
5. 确认日志出现安装执行、环境变量认证和回答摘要 API 三项 `PASS`，且整个 job 成功。

工作流固定使用已校验的官方 CLI 0.6.1。它仅手动触发，权限为空，不检出项目、不执行同步、不调用直答 AI、不发布 Pages、不修改仓库，也不上传日志或数据 artifact。CLI stdout/stderr 被捕获，日志只输出阶段状态和条目数量。

认证阶段会调用一次本人内容接口验证凭证，再读取一次医学问题的回答摘要（limit=1），可能分别消耗对应接口额度。返回零条摘要也可以通过，但必须是成功且结构正常的业务响应。

## 云端验收结果

仓库：<https://github.com/BretDeng/nobel-forecast-2026>。

2026-10-04 云端 CLI 验收通过：<https://github.com/BretDeng/nobel-forecast-2026/actions/runs/37197003896>。官方 Linux 包安装执行、环境变量认证、真实凭证验证以及一条回答摘要读取均成功。凭证仅存放于 Actions Secret。

首次完整抓取、复核、缓存提交和 Pages 再发布已成功：<https://github.com/BretDeng/nobel-forecast-2026/actions/runs/37197049463>。两小时同步工作流已启用；完整同步使用当前项目的直答复核逻辑，不额外发起无关 AI 请求。

失败时保留当前网站和数据，不自动重试。CLI 退出码：3 为凭证问题，4 为额度/频率限制，5 为网络/超时，6 为服务端/协议问题。按对应原因修复后手动再次运行。

## 依据

- 知乎官方发布索引：<https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/manifest.json>
- 已安装的知乎官方 Skill：`/Users/bret/.codex/skills/zhihu/references/cli.md`
- GitHub Actions Secrets：<https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets>
