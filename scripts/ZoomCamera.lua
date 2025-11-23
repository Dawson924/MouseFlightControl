local mod = {}
mod.id = 'zoom_camera'
mod.options = {
    {'key_zoom', 1, ''}
}
mod.i18n = {
    name = {
        en_US = 'Zoom Camera',
        zh_CN = '镜头缩放'
    },
    key_zoom = {
        en_US = 'Zoom in',
        zh_CN = '放大'
    }
}

local key_zoom
local lastFov = GetAttribute('camera_fov')
local targetFov = lastFov / 2

local function fov(value)
    local f = Axis.len / 160
    return Axis.min + f * value
end

local function axis2fov(value)
    return (value - Axis.min) / (Axis.len / 160)
end

IsZooming = false

function mod.init(config)
    key_zoom = config.key_zoom
end

function mod.update()
    if Input.pressed(key_zoom) then
        IsZooming = not IsZooming
        if IsZooming then
            lastFov = axis2fov(Axis.vz)
            Axis.setValue('vz', fov(targetFov))
        else
            Axis.setValue('vz', fov(lastFov))
        end
    end
end

return mod
