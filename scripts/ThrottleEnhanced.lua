local te = require('ThrottleEnhanced.init')

DETENT_ON = false

local config
local detent

function te.init(database)
    config = database.get(te.id)
    detent = AXIS_MAX * config.afterburner_position
end

function te.update(dt)
    if Control.active and Control.mode ~= 2 then
        if Input.hotkey(config.afterburner_detent) then
            DETENT_ON = not DETENT_ON
        end
        if DETENT_ON and Axis.Throttle > detent then
            SetAxis('Throttle', detent)
        end
    end
end

return te