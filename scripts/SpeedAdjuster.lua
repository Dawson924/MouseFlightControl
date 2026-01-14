local Script = require('script')

local script = Script:new('speed_adjuster')
script.loadTranslation('scripts/locales/speed_adjuster.tr')
script.addOption('secondary_speed', 'uint', 4)
script.addOption('toggle_secondary_speed', 'string', 'ctrl + `')

local config
local on = false

function script.init(db)
    config = db.get(script.id)
end

function script.update()
    if Input.hotkey(config.toggle_secondary_speed) then
        on = not on
        if not on then
            SetMouseSpeed(Mouse.speed)
        else
            SetMouseSpeed(config.secondary_speed)
        end
    end
end

return script
