#scp -P 3522 target_server/AIPainting/* "myh@166.111.139.44:/mnt/share/atlantix/AP/target_server/AIPainting/" & scp -P 3522 target_server/static/js/* "myh@166.111.139.44:/mnt/share/atlantix/AP/target_server/static/js/" & scp -P 3522 target_server/templates/*.html "myh@166.111.139.44:/mnt/share/atlantix/AP/target_server/templates/"

tar cvfz - target_server/AIPainting target_server/static/js target_server/static/lib target_server/templates | ssh -p 3522 myh@166.111.139.44 "cd /mnt/share/atlantix/AP/; tar xvfz -"

tar cvfz - target_server/AIPainting target_server/static/js target_server/static/lib  target_server/templates | ssh xujianjing@114.113.33.223 "cd Aesthetic-Painting/web/; tar xvfz -"