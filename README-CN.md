# 鼠标飞行控制（Mouse Flight Control）

此软件旨在通过鼠标模拟摇杆功能为游戏提供一种直观的飞行控制方式。


## 功能特点

- **鼠标摇杆模拟**：🖱️ 屏幕中心作为摇杆的中点，屏幕宽度代表X轴，高度代表Y轴。
- **可自定义控制**：🎮 你可以自定义按键映射和各种选项，例如光标显示、提示叠加层，以及将鼠标按钮用作摇杆按钮。


## 安装步骤

### 前置要求
- **vJoy 设备驱动**：你需要安装 vJoy 设备驱动（推荐版本 ≥ 2.1.8）。可从 [https://github.com/shauleiz/vJoy](https://github.com/shauleiz/vJoy) 下载。


### 安装步骤
1. **下载软件**：📥 从 [Releases](https://github.com/Dawson924/MouseFlightControl) 下载软件包。
2. **安装 vJoy**：按照说明安装 vJoy 设备驱动。
3. **运行程序**
4. **控制器设置**：对于 DCS，将 ./Platform/DCS/ 目录下的 MouseFlightControl 文件夹和 Export.lua 文件复制到 C:/.../DCS.openbeta/Scripts 目录中。如果已存在 Export.lua 文件，请在文件底部添加以下代码：
```lua
dofile(lfs.writedir()..[[Scripts\MouseFlightControl\MouseFlightControl.lua]]);
```


## 使用方法

### 启动程序
- 点击“开始”按钮即可开始使用。🚀


### 调整灵敏度
- 使用灵敏度滑块调整鼠标灵敏度，可设置范围为 1-20。🔍


### 控制切换
- 默认情况下，按键盘上的 `~` 键可在暂停和恢复控制之间切换。⏯️


### 配置选项
- 你可以在设置菜单中配置各种选项，包括语言、控制器类型、按键映射和显示选项。⚙️


## 许可证

本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT) 授权。


## 联系方式

如有任何问题或反馈，请联系开发者：[bendawson0924@gmail.com](mailto:bendawson0924@gmail.com)。


---

请注意，本软件目前处于早期阶段。虽然在测试中未发现重大问题，但建议你谨慎使用。如果遇到任何问题或有改进建议，欢迎随时提出。😊
