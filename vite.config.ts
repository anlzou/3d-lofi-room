import {defineConfig} from 'vite';
// base './' keeps the Electron build working from the room:// protocol.
// host true also prints a LAN address, so phones on the same Wi-Fi can open the room.
// The dev port prefers 5174 and steps up to the next free one if it is taken, so a second
// checkout or another tool on 5174 does not block the room from starting.
export default defineConfig({base:'./', server:{host:true, port:5174}});
