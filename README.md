# EA SPORTS™ WRC 简体中文纯资源汉化补丁 (Pure `.pak` Localization Patch)

面向 *EA SPORTS™ WRC*（UE4.27 + EA Javelin Anticheat）的**纯 `.pak` 资源型简体中文补丁**与开源构建工具链。

- **零 DLL 注入 / 零反作弊改动**：仅通过虚幻引擎标准本地化资源（`Game.locres`）与字体替换（`.ufont`）打包为 `pakchunk0-WindowsNoEditor_0_P.pak`，完全兼容官方最新版 EA Anticheat，不会触发「不受信任文件」或版本校验拦截。
- **开箱即用字体**：内嵌基于 **Noto Sans SC**（SIL OFL 1.1）导出的 Regular / Medium / Bold 静态 TrueType 字体，完整覆盖简体中文菜单、生涯、调校、说明与字幕，同时保留 HUD 7 段数码管数字字体风格。
- **全量覆盖与回退安全**：同时编译 `en` 与 `en-US` 两套本地化包；人名（车手/领航员/制作人员名单）、车名、真实赛段地名与 EA 法律协议原文保持英文原样，其余界面、生涯、工程师对话、改装配件、拉力学院、精彩瞬间与输入提示全面中文化。

---

## 安装使用（面向玩家）

1. 将发布包中的 `pakchunk0-WindowsNoEditor_0_P.pak` 复制到游戏目录：
   ```
   <Steam或EA安装目录>\EA SPORTS WRC\WRC\Content\Paks\
   ```
2. 在启动器中添加启动参数 **`-fileopenlog`**（必需，否则游戏不会加载外部 `_P.pak` 模组）：
   - **Steam**：右键游戏 → 属性 → 通用 → 启动选项，填入 `-fileopenlog`
   - **EA App**：游戏 → 管理 → 查看属性 → 高级启动选项，填入 `-fileopenlog`
3. 确保游戏语言设为 **English**，直接启动即可。
4. **卸载**：删除 `WRC\Content\Paks\pakchunk0-WindowsNoEditor_0_P.pak` 即可恢复原版，无需验证游戏文件完整性。

---

## 从源码自行构建（面向开发者）

### 环境准备

1. Python 3.10+
2. 下载以下开源工具并放入工作工具目录（默认可通过 `--tools-dir` 指定）：
   - `repak`（[trumank/repak](https://github.com/trumank/repak)）
   - `UE4LocalizationsTool`（[amrshaheen61/UE4LocalizationsTool](https://github.com/amrshaheen61/UE4LocalizationsTool)）
3. 从正版游戏 `WRC/Content/Paks/pakchunk0-WindowsNoEditor.pak` 中使用 `repak` 解出原版 `en/Game.locres` 与 `en-US/Game.locres`，并用 `UE4LocalizationsTool export` 导出 `.txt`。

### 校验与打包

```bash
# 校验全部翻译分片（占位符、标签与完整性检查）
python scripts/validate_translations.py

# 构建 pakchunk0-WindowsNoEditor_0_P.pak
python scripts/build_pak.py --tools-dir <工具目录> --output dist/pakchunk0-WindowsNoEditor_0_P.pak
```

---

## 协议

- 构建脚本与原创译文采用 [MIT License](LICENSE)。
- 内置字体 **Noto Sans SC** 采用 [SIL Open Font License 1.1](fonts/OFL-NotoSansSC.txt)。
