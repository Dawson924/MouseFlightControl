-- 鼠标全局变量：包含速度、位置、增量
---@class Mouse
---@field speed number 鼠标灵敏度（范围：1-20）
---@field pos number[] 鼠标当前位置，格式 [x坐标, y坐标]（屏幕像素值）
---@field deltaX number 横向移动增量（当前帧 - 上一帧，正数向右，负数向左）
---@field deltaY number 纵向移动增量（当前帧 - 上一帧，正数向下，负数向上）
local Mouse = {}
mouse = Mouse


-- 相机全局变量：控制视角
---@class Camera
---@field active boolean 是否激活自由视角（true=激活，false=未激活）
---@field fov number 视野角度（范围：0-120，数值越大视角越广）
local Camera = {}
camera = Camera


-- 控制全局变量：控制状态
---@class Control
---@field active boolean 是否激活控制（true=正在控制，false=未控制）
---@field steering boolean 是否激活滑行模式（true=滑行模式，false=正常模式）
local Control = {}
control = Control


-- 输入全局变量：检测按键和鼠标滚轮
---@class Input
local Input = {}

---检查按键是否**刚刚按下**（单次触发）
---@param key string
---@return boolean 按下返回 true，否则 false
function Input.pressed(key) end

---检查按键是否**正在按住**（持续触发）
---@param key string
---@return boolean 按住返回 true，否则 false
function Input.pressing(key) end

---检查按键是否**刚刚释放**（单次触发）
---@param key string
---@return boolean 释放返回 true，否则 false
function Input.released(key) end

input = Input


-- 屏幕全局变量：渲染提示消息
---@class Screen
local Screen = {}

---渲染提示消息到屏幕
---@param text string 消息文本内容（如 "控制已激活"）
---@param color string 消息颜色（预定义值："green"、"red"、"yellow"）
---@param duration number 消息显示时长（毫秒，如 1000=显示1秒）
function Screen.renderMessage(text, color, duration) end

screen = Screen
