# 知乎 CLI 的 GitHub Actions 验收

2026-10-04 已核验官方发布索引，Linux x64 CLI 0.6.1 可下载；下载包大小、SHA-256、单文件归档和 Linux x86-64 ELF 格式均已通过本机校验。当前宿主为 macOS，尚未在 GitHub Linux runner 执行该二进制。

官方知乎 Skill 的 `references/cli.md` 明确规定：CI 使用进程环境变量 `ZHIHU_ACCESS_SECRET`，优先于系统密钥链；无界面 Linux 不需要运行 `auth set` 或配置 Secret Service。已用非真实凭证执行本机 CLI 的离线 `auth status`，确认来源为 `environment`；这不代表真实凭证有效。

本项目的同步脚本已支持 `ZHIHU_CLI_BINARY`，后续 Linux 同步时传入安装后的绝对路径即可；Python 子进程会继承 `ZHIHU_ACCESS_SECRET`。无需调用长期运行的本地 `server.mjs`。

## 云端验收步骤

1. 创建 GitHub 仓库，将 `.github/workflows/verify-zhihu-cli.yml` 放到默认分支。
2. 从 <https://developer.zhihu.com/profile> 获取自己的 Access Secret。
3. 在仓库 Settings → Secrets and variables → Actions → New repository secret 中添加 `ZHIHU_ACCESS_SECRET`，值为该 Secret。不要写入源码、聊天或网页。
4. 在 Actions 中选择 **Verify Zhihu CLI on GitHub**，点击 **Run workflow**。
5. 确认日志出现安装执行、环境变量认证和回答摘要 API 三项 `PASS`，且整个 job 成功。

工作流固定使用已校验的官方 CLI 0.6.1。它仅手动触发，权限为空，不检出项目、不执行同步、不调用直答 AI、不发布 Pages、不修改仓库，也不上传日志或数据 artifact。CLI stdout/stderr 被捕获，日志只输出阶段状态和条目数量。

认证阶段会调用一次本人内容接口验证凭证，再读取一次医学问题的回答摘要（limit=1），可能分别消耗对应接口额度。返回零条摘要也可以通过，但必须是成功且结构正常的业务响应。

## 当前未完成的条件

尚无目标 GitHub 仓库，也未配置云端 Secret，因此不能声称云端认证已经通过。以上工作流成功后，再验证 `zhida-fast-1p5` 的最小调用，最后接入两小时同步、复核状态保存与 Pages 发布。

失败时保留当前网站和数据，不自动重试。CLI 退出码：3 为凭证问题，4 为额度/频率限制，5 为网络/超时，6 为服务端/协议问题。按对应原因修复后手动再次运行。

## 依据

- 知乎官方发布索引：<https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/manifest.json>
- 已安装的知乎官方 Skill：`/Users/bret/.codex/skills/zhihu/references/cli.md`
- GitHub Actions Secrets：<https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets>
