local decrease_key = GetAttribute('__external__.decrease_throttle_speed')

function Update()
    if Input.pressing(decrease_key) then
        local detent = Axis.min * 0.5
        print(detent)
        if Axis.th < detent then
            Axis.setValue('th', detent)
        end
    end
end
