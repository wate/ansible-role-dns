dns
=================

Gather Server DNS records

OS Platform
-----------------

### Debian

- trixie
- bookworm

Role Variables
--------------

### [defaults/main.yml](defaults/main.yml)

設定方法の詳細については[defaults/main.yml](defaults/main.yml)のサンプルコードなどを参照してください。

#### `dns_domains`

DNS情報を取得するドメイン  
収集されたDNSのレコード情報は「dns_records」変数にホスト名毎のディクショナリーとして格納されます

#### `dns_record_output_dir`

DNSレコード情報の出力先ディレクトリ

#### `dns_spf_default`

SPFレコードに設定する初期値  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-spf-record/  
https://datatracker.ietf.org/doc/html/rfc7208

#### `dns_opendkim_keytable_path`

OpenDKIMのKeyTableファイルのパス

#### `dns_dkim_default`

DKIMレコードに設定する初期値  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dkim-record/  
https://salt.iajapan.org/wpmu/anti_spam/admin/tech/explanation/dkim/  
https://datatracker.ietf.org/doc/html/rfc6376/

#### `dns_dmarc_default`

DMARCレコードに設定する初期値  
参考URL：  
https://www.cloudflare.com/ja-jp/learning/dns/dns-records/dns-dmarc-record/  
https://datatracker.ietf.org/doc/html/rfc7489

#### `dns_caa_default`

CAAレコードに設定する初期値  
参考URL：  
https://www.cybertrust.co.jp/sureserver/support/caa.html  
https://datatracker.ietf.org/doc/html/rfc6844

#### `dns_ttl_default`

TTLの初期値

#### `dns_txt_chunk_size`

TXTレコードの1セグメントあたりの最大長  
DNS TXTの文字列は1つのダブルクオート内で255オクテットを超えられません。  
運用上の安全マージンとして200を既定値にします。

#### `dns_save_opendkim_keys`

OpenDKIMキーファイルを取得して保存するかどうか  
注: 有効にする場合、dns_record_output_dir に保存されます

#### `dns_opendkim_keys_dir`

OpenDKIMキーファイルの保存先ディレクトリ名  
dns_record_output_dir内に作成されます

### [vars/main.yml](vars/main.yml)

設定値については[vars/main.yml](vars/main.yml)を参照してください。

#### `dns_records`

#### `dns_recodes`

#### `dns_zones`

#### `dns_auto_append_option`

#### `dns_spf_qualifier_pass`

#### `dns_spf_qualifier_neutral`

#### `dns_spf_qualifier_softfail`

#### `dns_spf_qualifier_fail`

#### `dmarc_policy_none`

#### `dmarc_policy_quarantine`

#### `dmarc_policy_reject`

#### `dmarc_mode_relaxed`

#### `dmarc_mode_strict`

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
