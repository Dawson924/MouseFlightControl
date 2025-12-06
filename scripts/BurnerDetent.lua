local mod = {}
mod.id = 'burner_detent'
mod.options = {
    {'key_detent', 'string', ''}
}
mod.i18n = {
    name = {
        en_US = 'Burner Detent',
        zh_CN = '加力止动'
    },
    key_detent = {
        en_US = 'Detent Engage',
        zh_CN = '启用加力止动'
    }
}

local config

function mod.init(database)
    config = database.get(mod.id)
end

function mod.update()
    if Input.pressing(config.key_detent) and GetAttribute('controller') == 1 then
        local detent = Axis.min * 0.5
        if Axis.th < detent then
            Axis.setValue('th', detent)
        end
    end
end

return mod
