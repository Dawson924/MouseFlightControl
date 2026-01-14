local Script = require('script')

local cs = Script:new('indicator')
cs.loadTranslation('scripts/locales/indicator.tr')
cs.options = {
    {'indicator_x', 'int', 30},
    {'indicator_y', 'int', -30},
    {'indicator_size', 'uint', 200},
}

return cs
