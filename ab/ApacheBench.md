# Использование ApacheBench для тестирования нагрузки на веб-сервер!


## Нагрузочное тестирование с ab:

https://github.com/artemonsh/grafana-deploy
```
ab -k -c 5 -n 20000 'http://localhost:8080/'
```

```
ab -k -c 5 -n 3000 'http://localhost:8080/status/409' & \
ab -k -c 5 -n 5000 'http://localhost:8080/status/500' & \
ab -k -c 50 -n 5000 'http://localhost:8080/status/200?seconds_sleep=1' & \
ab -k -c 50 -n 2000 'http://localhost:8080/status/200?seconds_sleep=2'
```


### Создать идеально пустой файл:

```bash
: > empty_post.txt    # или
echo -n "" > empty_post.txt
wc -c empty_post.txt  # должно быть 0
```

```bash
ab -n 100 -c 10 -k \
  -p empty_post.txt \
  -T 'application/json' \
  -C 'PGADMIN_LANGUAGE=en; pga4_session=d8ae69ff-e477-4be8-b3cf-af46b47dac49!2/cm08oJdStXhoCLioluqr1sQeapNhlXGXh5c0CdfOw=; user_access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzYyNDg3ODYzLCJ0eXBlIjoiYWNjZXNzIn0.6EuyFze5Rsww6f9ptdtxAl2-C-9E2_Mj4n_1N1ng6tg; user_refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzYzMDkyNjUzLCJ0eXBlIjoicmVmcmVzaCJ9.g1s0qoMEYtoFJK6lfJDTqKXCUAdV0I0LJrHVcJntuaY; grafana_session=d4ff598bfc13b16c13b8873ae49757c7; grafana_session_expiry=1762488645' \
  -H 'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'Connection: keep-alive' \
  -H 'Origin: http://localhost:8080' \
  -H 'Referer: http://localhost:8080/docs' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36' \
  -H 'accept: application/json' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Chromium";v="142"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  'http://localhost:8080/auth/refresh'
```