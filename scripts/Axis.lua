return {
    id = 'axis',
    i18n = {
        name = {
            en_US = 'Axis Tune',
            zh_CN = '轴设置'
        },
        damping_h = {
            en_US = 'Horizontal Damping',
            zh_CN = '水平阻尼系数'
        },
        damping_v = {
            en_US = 'Vertical Damping',
            zh_CN = '垂直阻尼系数'
        }
    },
    options = {
        {'damping_h', 'float', 0.7},
        {'damping_v', 'float', 0.9}
    }
}