local mod = {}
local config
local on = false
local speed = Mouse.speed

mod.id = 'speed_control'
mod.options = {
    {'alt_speed', 'uint', 5},
    {'change_speed', 'string', 'ctrl + `'}
}

function mod.init(db)
    config = db.get(mod.id)
end

function mod.update()
    if Input.hotkey(config.change_speed) then
        on = not on
        if not on then
            SetMouseSpeed(Mouse.speed)
        else
            SetMouseSpeed(config.alt_speed)
        end
    end
end

return mod
