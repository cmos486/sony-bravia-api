curl -H 'Content-Type: application/json' \
     -H 'X-Auth-PSK: PASSWORD' \
     -X POST \
     -d '{"id":1,"method":"setActiveApp","version":"1.0","params":[{"uri":"com.sony.dtv.com.netflix.ninja.com.netflix.ninja.MainActivity"}]}' \
     http://TV_IP/sony/appControl


