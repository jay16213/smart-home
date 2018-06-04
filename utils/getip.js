'use strict';

const os = require('os');
const ifaces = os.networkInterfaces();

module.exports = () => {
    var ip = '';
    Object.keys(ifaces).forEach((ifname) => {
        var alias = 0;

        ifaces[ifname].forEach((iface) => {
            if(iface.family === 'IPv4' && iface.internal === false)
            {
                if (alias >= 1) {
                    // this single interface has multiple ipv4 addresses
                    console.log(ifname + ':' + alias, iface.address);
                } else {
                    // this interface has only one ipv4 adress
                    ip = iface.address;
                    return iface.address;
                }
                ++alias;
            }
        });
    });
    return ip;
}

