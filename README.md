# asterisk_check_mnp
Для версий Asterisk 12+
https://wiki.asterisk.org/wiki/pages/viewpage.action?pageId=29395573

Сервис для определния принадлежности мобильного номера оператору и региону по базе MNP. Написан на питоне.
Может быть использован один из доступных на данный момент сервисов:
	1.http://mnp.tele2.ru/gateway.php?
	2.http://moscow.shop.megafon.ru/get_ajax_page.php?action=getMsisdnInfo&msisdn=

Для работы сервиса должны быть установлены дополнительные модули
	1. pip install websocket-client
	2. pip install python-daemon

контакты https://malinovka.net
