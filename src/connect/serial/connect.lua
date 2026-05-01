NAMESPACE = "FLIGHT CONNECT"
HOST_ADDRESS = "127.0.0.1"
TCP_PORT = 20070
UDP_PORT = 20069

log.write(NAMESPACE, log.INFO)

local tcpServer                        = nil
local udpSpeaker                       = nil
package.path                           = package.path .. ";" .. lfs.currentdir() .. "/LuaSocket/?.lua"
package.cpath                          = package.cpath .. ";" .. lfs.currentdir() .. "/LuaSocket/?.dll"
package.path = package.path .. ";.\\Scripts\\?.lua;.\\Scripts\\UI\\?.lua;.\\dxgui\\loader\\?.lua;.\\dxgui\\bind\\?.lua;.\\dxgui\\skins\\common\\?.lua;.\\dxgui\\skins\\skinME\\?.lua"
local socket                           = require("socket")
local JSON                             = loadfile("Scripts\\JSON.lua")()

local upstreamLuaExportStart           = LuaExportStart
local upstreamLuaExportAfterNextFrame  = LuaExportAfterNextFrame
local upstreamLuaExportBeforeNextFrame = LuaExportBeforeNextFrame


function LuaExportStart()
    if upstreamLuaExportStart ~= nil then
        successful, err = pcall(upstreamLuaExportStart)
        if not successful then
            log.write(NAMESPACE, log.ERROR, "Error in upstream LuaExportStart function" .. tostring(err))
        end
    end

    udpSpeaker = socket.udp()
    udpSpeaker:settimeout(0)
    tcpServer = socket.tcp()
    tcpServer:bind(HOST_ADDRESS, TCP_PORT)
    tcpServer:listen(1)
    tcpServer:settimeout(0)
end

local data
local busy = false;
local isPressed = false
local currCommandIndex = 1
local lastDevice = ""
local lastCode = ""
local lastNeedDepress = true
local whenToDepress = nil
local stringtoboolean={ ["true"]=true, ["false"]=false }
function LuaExportBeforeNextFrame()
    if upstreamLuaExportBeforeNextFrame ~= nil then
        successful, err = pcall(upstreamLuaExportBeforeNextFrame)
        if not successful then
            log.write(NAMESPACE, log.ERROR, "Error in upstream LuaExportBeforeNextFrame function" .. tostring(err))
        end
    end

    if busy then
        if isPressed then
            -- check if the time has come to depress
            local currTime = socket.gettime()
            if currTime >= whenToDepress then
                -- check if it even needs a depress
                if lastNeedDepress then
                    GetDevice(lastDevice):performClickableAction(lastCode, 0)
                end
                isPressed = false
                currCommandIndex = currCommandIndex + 1
            end
        else
            -- Prepare for new button push
            local decodedData = JSON:decode(data)
            local keys = decodedData["payload"]
            --check if there are buttons left to press
            if currCommandIndex <= #keys then
                lastDevice = keys[currCommandIndex]["device"]
                lastCode = keys[currCommandIndex]["code"]
                lastNeedDepress = stringtoboolean[keys[currCommandIndex]["addDepress"]]
                local delay = tonumber(keys[currCommandIndex]["delay"])
                local activate = tonumber(keys[currCommandIndex]["activate"])
                -- Push the button
                GetDevice(lastDevice):performClickableAction(lastCode, activate)
                --Store the time when we will need to depress
                whenToDepress = socket.gettime() + (delay / 1000)
                isPressed = true
            else
                --if there's nothing else to press, we are done
                busy = false
                currCommandIndex = 1
            end
        end
    else
        local client, err = tcpServer:accept()
        if client ~= nil then
            client:settimeout(10)
            data, err = client:receive()
            if err then
                log.write(NAMESPACE, log.ERROR, "Error at receiving: " .. err)
            end

            if data then
                local keys = JSON:decode(data)
                if keys["type"] == "action" then
                    busy = true
                end
            end
        end
    end
end

function LuaExportAfterNextFrame()
    if upstreamLuaExportAfterNextFrame ~= nil then
        successful, err = pcall(upstreamLuaExportAfterNextFrame)
        if not successful then
            log.write(NAMESPACE, log.ERROR, "Error in upstream LuaExportAfterNextFrame function" .. tostring(err))
        end
    end


    local camPos = LoGetCameraPosition()
    local loX = camPos['p']['x']
    local loZ = camPos['p']['z']
    local elevation = LoGetAltitude(loX, loZ)
    local coords = LoLoCoordinatesToGeoCoordinates(loX, loZ)
    local pitch, bank, yaw = LoGetADIPitchBankYaw()
    local selfData = LoGetSelfData()
    local module = selfData and selfData['Name'] or 'Spectator'
    local message = {}

    message["module"] = module
    message['heading'] = LoGetMagneticYaw()
    message['pitch'] = pitch
    message['bank'] = bank
    message['yaw'] = yaw
    message['airspeed'] = {}
    message['airspeed']['indicated'] = LoGetIndicatedAirSpeed()
    message['airspeed']['true'] = LoGetTrueAirSpeed()
    message['aoa'] = LoGetAngleOfAttack()
    message['mach'] = LoGetMachNumber()
    message["coords"] = {}
    message["coords"]["lat"] = tostring(coords.latitude)
    message["coords"]["long"] = tostring(coords.longitude)
    message["elev"] = tostring(elevation)
    message["mech"] = LoGetMechInfo()
    local toSend = JSON:encode(message)

    if pcall(function()
            socket.try(udpSpeaker:sendto(toSend, HOST_ADDRESS, UDP_PORT))
        end) then
    else
        log.write(NAMESPACE, log.ERROR, "Unable to send data")
    end
end

log.write(NAMESPACE, log.INFO, "Done")
