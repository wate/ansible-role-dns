dns
=================

Gather Sever DNS recodes

OS Platform
-----------------

### Debian

- bookworm

Role Variables
--------------

設定方法の詳細については[defaults/main.yml](defaults/main.yml)のサンプルコードを参照してください。

### `dns_recodes`

収集したDNSレコードの内容  
※以下の変数に各レコードの情報が追加されていきます

### `dns_spf_default`

SPF(Sender Policy Framework)レコードに設定する初期値  
参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-spf-record/

### `dns_dkim_default`

参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dkim-record/  
現在この変数はロール機能しておらず、  
DKIMレコードの設定情報の抽出は以下のロールの変数があるかどうかなどを元に抽出判定を行っています。  
(以下のロールの変数を元にDNS情報の抽出をこなっています)  
https://github.com/wate/ansible-role-opendkim

### `dns_caa_default`

CAAレコードに設定する初期値  
参考URL：https://www.cybertrust.co.jp/sureserver/support/caa.html

### `dns_dmarc_default`

DMARCレコードに設定する初期値  
参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dmarc-record/

Example Playbook
--------------

```yaml
- hosts: servers
  roles:
    - role: dns
```

License
--------------

Apache License 2.0
