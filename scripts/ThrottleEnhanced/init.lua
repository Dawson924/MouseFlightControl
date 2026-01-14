local Script = require('script')

local init = Script:new('throttle_enhanced')
init.options = require('ThrottleEnhanced.options')
init.addTranslation('en_US', 'scripts/ThrottleEnhanced/locales/en_us.tr')
init.addTranslation('zh_CN', 'scripts/ThrottleEnhanced/locales/zh_cn.tr')

return init
