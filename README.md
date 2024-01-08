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

### `dns_spf`

SPF(Sender Policy Framework)レコードの設定値に追加する値  
参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-spf-record/

### `dns_dkim_domain`

DKIMレコードを設定するドメイン  
参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dkim-record/  
※DKIMレコードの設定情報の抽出は以下のロールの変数があるかどうかなどを元に抽出判定を行っています。  
(以下のロールのopendkim_domains変数に定義したドメインのいずれかを変数に設定してください)  
https://github.com/wate/ansible-role-opendkim

### `dns_dmarc`

DMARCレコードに設定する値  
参考URL：https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dmarc-record/

### `dns_rtp_domain`

RTPレコードに設定するドメイン名

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
