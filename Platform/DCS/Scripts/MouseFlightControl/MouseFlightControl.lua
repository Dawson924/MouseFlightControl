UDP_SET = {}

package.path  = package.path..";.\\LuaSocket\\?.lua"
package.cpath = package.cpath..";.\\LuaSocket\\?.dll"

socket = require("socket")

-- -----------------------------------
UDP_SET.util = {}

function UDP_SET.util.shallowCopy(source, dest)
	dest = dest or {}
	for k, v in pairs(source) do
		dest[k] = v
	end
	return dest
end
-- ------------------------------------
local log_file = nil
-- ------------------------------------
UDP_SET.protocol = {}
UDP_SET.protocol.maxBytesPerSecond = UDP_SET.protocol.maxBytesPerSecond or 11000
UDP_SET.protocol.maxBytesInTransit = UDP_SET.protocol.maxBytesPerSecond or 4000

function UDP_SET.protocol.processInputLine(line)
	log_file:write(string.format("COMMAND: %s \n", line));
	local cmd, args = line:match("^([^ ]+) (.*)")
	if cmd == "LoSetCommand" then
		LoSetCommand(args);
	end
end
-- -------------------------------------

UDP_SET.protocol_io = {}
UDP_SET.protocol_io.connections = {}

UDP_SET.protocol_io.LuaSocketConnection = {
	conn = nil,
	rxbuf = ""
}
function UDP_SET.protocol_io.LuaSocketConnection:create(args)
	local self = UDP_SET.util.shallowCopy(UDP_SET.protocol_io.LuaSocketConnection)
	return self
end
function UDP_SET.protocol_io.LuaSocketConnection:close()
	self.conn:close()
end

UDP_SET.protocol_io.UDPListener = {}
function UDP_SET.protocol_io.UDPListener:create(args)
	local self = UDP_SET.protocol_io.LuaSocketConnection:create()

	UDP_SET.util.shallowCopy(UDP_SET.protocol_io.UDPListener, self)
	self.port = args.port or 7779
	self.host = args.host or "*"
	return self
end
function UDP_SET.protocol_io.UDPListener:init()
	self.conn = socket.udp()
	self.conn:setsockname("*", self.port)
	self.conn:settimeout(0)
end
function UDP_SET.protocol_io.UDPListener:step()
	local lInput = nil

	while true do
		lInput = self.conn:receive()
		if not lInput then break end
		self.rxbuf = self.rxbuf .. lInput
	end

	while true do
		local line, rest = self.rxbuf:match("^([^\n]*)\n(.*)")
		if line then
			self.rxbuf = rest
			UDP_SET.protocol.processInputLine(line)
		else
			break
		end
	end
end
-- -----------------------------------
UDP_SET.protocol_io.connections = {
	UDP_SET.protocol_io.UDPListener:create({ port = 7779 })
}
-- -----------------------------------
-- Prev Export functions.

local PrevExport = {}
PrevExport.LuaExportStart = LuaExportStart
PrevExport.LuaExportStop = LuaExportStop
PrevExport.LuaExportBeforeNextFrame = LuaExportBeforeNextFrame
PrevExport.LuaExportAfterNextFrame = LuaExportAfterNextFrame

-- Lua Export Functions
LuaExportStart = function()
	log_file = io.open(lfs.writedir()..[[Logs\DCS-UDP-SET.txt]], "w")
	for _, v in pairs(UDP_SET.protocol_io.connections) do v:init() end
	-- Chain previously-included export as necessary
	if PrevExport.LuaExportStart then
		PrevExport.LuaExportStart()
	end
end

LuaExportStop = function()
	for _, v in pairs(UDP_SET.protocol_io.connections) do v:close() end

	-- Chain previously-included export as necessary
	if PrevExport.LuaExportStop then
		PrevExport.LuaExportStop()
	end

end

function LuaExportBeforeNextFrame()
	for _, v in pairs(UDP_SET.protocol_io.connections) do
		if v.step then v:step() end
	end

	-- Chain previously-included export as necessary
	if PrevExport.LuaExportBeforeNextFrame then
		PrevExport.LuaExportBeforeNextFrame()
	end
end

function LuaExportAfterNextFrame()
	-- Chain previously-included export as necessary
	if PrevExport.LuaExportAfterNextFrame then
		PrevExport.LuaExportAfterNextFrame()
	end
end
