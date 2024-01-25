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

### `dns_domains`

DNS情報を取得するドメイン  
収集されたDNSのレコード情報は「dns_recodes」変数にホスト名毎のディクショナリとして格納されます

### `dns_recode_output_dir`

DNSレコード情報の出力先ディレクトリ

### `dns_spf_default`

SPFレコードに設定する初期値  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-spf-record/  
https://datatracker.ietf.org/doc/html/rfc7208

### `dns_dkim_default`

DKIMレコードに設定する初期値  
※現在この変数はロール機能しておらず、設定情報の抽出は以下のロールの変数があるかどうかなどを元に抽出判定を行っています。  
以下のロールの変数を元にDNS情報の抽出をこなっています。  
https://github.com/wate/ansible-role-opendkim  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dkim-record/  
https://datatracker.ietf.org/doc/html/rfc6376/

### `dns_dmarc_default`

DMARCレコードに設定する初期値  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dmarc-record/  
https://datatracker.ietf.org/doc/html/rfc7489

### `dns_caa_default`

CAAレコードに設定する初期値  
参考URL：  
https://www.cybertrust.co.jp/sureserver/support/caa.html  
https://datatracker.ietf.org/doc/html/rfc6844

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
