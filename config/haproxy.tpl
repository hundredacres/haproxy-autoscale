global  
	log /dev/log	local0
	log /dev/log	local1 notice
	chroot /var/lib/haproxy
	user haproxy
	group haproxy
	daemon

defaults
	log	global
	mode	http
        balance roundrobin
	option	httplog
	option	dontlognull
	option httpclose
        option forwardfor
        contimeout 5000
        clitimeout 50000
        srvtimeout 50000
	errorfile 400 /etc/haproxy/errors/400.http
	errorfile 403 /etc/haproxy/errors/403.http
	errorfile 408 /etc/haproxy/errors/408.http
	errorfile 500 /etc/haproxy/errors/500.http
	errorfile 502 /etc/haproxy/errors/502.http
	errorfile 503 /etc/haproxy/errors/503.http
	errorfile 504 /etc/haproxy/errors/504.http

frontend ft_gala
  	mode http
  	bind 0.0.0.0:80
  	bind 0.0.0.0:443 ssl crt /etc/haproxy/ssl/arabfilmfestival.pem crt /etc/haproxy/ssl/fearlessbirth.pem crt /etc/haproxy/ssl/himalayan_2014.pem crt /etc/haproxy/ssl/sdaff.pem crt /etc/haproxy/ssl/seattleaaff_2015.pem crt /etc/haproxy/ssl/lgbt.pem crt /etc/haproxy/ssl/demo.pem crt /etc/haproxy/ssl/sdlatino.pem crt /etc/haproxy/ssl/lacomedyshorts.pem crt /etc/haproxy/ssl/aaiff_2014.pem crt /etc/haproxy/ssl/florencedancefest25.pem crt /etc/haproxy/ssl/vaff.org_2015.pem crt /etc/haproxy/ssl/wcff_us_2014.pem crt /etc/haproxy/ssl/aff2014.pem
  	reqadd X-Forwarded-Proto:\ https if { ssl_fc }
  	default_backend gala_engine

backend gala_engine
    	mode http
	cookie SRVNAME insert
    	% for instance in instances['Web Servers']:
    	server ${ instance.id } ${ instance.private_dns_name }:80 cookie S${ instance.id } check inter 2000 rise 2 fall 5
    	% endfor
