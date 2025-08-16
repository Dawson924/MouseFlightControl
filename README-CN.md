# 鼠标飞行控制（Mouse Flight Control）

此软件旨在通过鼠标模拟摇杆功能为游戏提供一种直观的飞行控制方式。


## 功能特点

- **鼠标摇杆模拟**：🖱️ 屏幕中心作为摇杆的中点，屏幕宽度代表X轴，高度代表Y轴。
- **可自定义控制**：🎮 你可以自定义按键映射和各种选项，例如光标显示、提示叠加层，以及将鼠标按钮用作摇杆按钮。


## 安装步骤

### 前置要求
- **vJoy 设备驱动**：你需要安装 vJoy 设备驱动（推荐版本 ≥ 2.1.8）。可从 [https://github.com/shauleiz/vJoy](https://github.com/shauleiz/vJoy) 下载。注：Windows 11 用户请选择v2.1.9版本，点击[此处下载](https://github.com/jshafer817/vJoy/releases)


### 安装步骤
1. **下载软件**：📥 从 [这里](https://github.com/Dawson924/MouseFlightControl/releases) 下载软件包。
2. **安装 vJoy**：按照说明安装 vJoy 设备驱动。
3. **运行程序**
4. **分配虚拟轴**:
  - X: 横滚轴
  - Y: 俯仰轴
  - Z: 节流阀
  - RZ: 脚舵
  - RX: 自由视角水平方向
  - RY: 自由视角垂直方向
  - SL0: 自由视角缩放

强烈建议在轴调整设置中将RX和RY的"Y轴边界"设定为38和50左右。这样可以在自由视角中达成这种效果：鼠标在屏幕中点和屏幕边缘中间时，视角正好看向正侧方。鼠标在屏幕边缘时正好看向侧后方。  
而且使用阿帕奇的头盔瞄准联动机炮时也能更加准确。不设置边界可能会导致自由视角灵敏度偏高（手柄摇杆移动视角也是同理）。

## 使用教程

- [简体中文](https://github.com/Dawson924/MouseFlightControl/wiki/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)


## 许可证

本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT) 授权。


## 联系方式

如有任何问题或反馈，请联系开发者：[bendawson0924@gmail.com](mailto:bendawson0924@gmail.com) 或 [bilibili](https://space.bilibili.com/1738605283)。


---

请注意，本软件目前处于早期阶段。虽然在测试中未发现重大问题，但建议你谨慎使用。如果遇到任何问题或有改进建议，欢迎随时提出。😊
