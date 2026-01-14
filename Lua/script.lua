local ini = require('ini')

local Script = {}

function Script:new(id)
    local _class = {}
    _class.id = id
    _class.options = {}
    _class.i18n = nil

    function _class.addOption(name, type, value)
        local _default = value or nil
        table.insert(_class.options, { name, type, _default })
    end

    function _class.addTranslation(code, translation)
        if _class.i18n == nil then
            _class.i18n = {}
        end

        if type(translation) == 'string' then
            local locale = ini.load(translation)
            _class.i18n[code] = locale
        elseif type(translation) == 'table' then
            _class.i18n[code] = translation
        end
    end

    function _class.loadTranslation(path)
        _class.i18n = ini.load(path)
    end

    return _class
end

return Script
