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
