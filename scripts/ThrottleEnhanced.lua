local te = require('ThrottleEnhanced.init')

DETENT_ON = false

local config
local accumulator = 0.0
local interval = 1.0/60
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
        if DETENT_ON and Axis.th > detent then
            SetAxis('th', detent)
        end

        accumulator = accumulator + dt
        while accumulator >= interval do
            if Input.pressing(config.throttle_increase) then
                SetAxis('th', Axis.th + config.throttle_speed)
            elseif Input.pressing(config.throttle_decrease) then
                SetAxis('th', Axis.th - config.throttle_speed)
            end
            accumulator = accumulator - interval
        end
    end
end

return te
