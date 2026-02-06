#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible module for collecting DNS record information from domains.
Generates DNS records and BIND zone file data.
"""

from ansible.module_utils.basic import AnsibleModule
import os
import re

try:
    import dns.resolver
    import dns.rdatatype
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False

try:
    import publicsuffix2
    HAS_PUBLICSUFFIX = True
except ImportError:
    HAS_PUBLICSUFFIX = False


class DNSRecordCollector:
    """Collect DNS records and generate zone file data"""

    def __init__(self, module, domains, server_ipv4, server_ipv6, opendkim_keytable_path,
                 spf_default, dkim_default, dmarc_default, caa_default, ttl_default):
        self.module = module
        self.domains = domains
        self.server_ipv4 = server_ipv4
        self.server_ipv6 = server_ipv6
        self.opendkim_keytable_path = opendkim_keytable_path
        self.spf_default = spf_default or {}
        self.dkim_default = dkim_default or {}
        self.dmarc_default = dmarc_default or {}
        self.caa_default = caa_default or {}
        self.ttl_default = ttl_default or 3600
        self.dkim_keytable_data = {}

    def collect(self):
        """Collect DNS records for all domains"""
        records = {}
        zones = {}

        # Parse OpenDKIM KeyTable if available
        self.dkim_keytable_data = self._parse_opendkim_keytable()
        dkim_key_items = self._flatten_dkim_keytable(self.dkim_keytable_data)

        # Normalize domains (add registrable domains)
        normalized_domains = self._normalize_domains()

        # Process each domain
        for domain, domain_settings in normalized_domains.items():
            zone = self._get_registrable_domain(domain)

            # Initialize zone if needed
            if zone not in zones:
                zones[zone] = {'A': [], 'AAAA': [], 'TXT': [], 'MX': [], 'CAA': []}

            # Get record name (subdomain or @)
            record_name = self._get_record_name(domain, zone)

            # Initialize domain records
            domain_records = {}

            # Skip flags
            skip_a = domain_settings.get('skip_a', False)
            skip_aaaa = domain_settings.get('skip_aaaa', False)
            skip_spf = domain_settings.get('skip_spf', False)
            skip_dkim = domain_settings.get('skip_dkim', False)
            skip_dmarc = domain_settings.get('skip_dmarc', False)
            skip_caa = domain_settings.get('skip_caa', False)
            skip_site_verification = domain_settings.get('skip_site_verification', False)

            # A Record
            if not skip_a:
                a_value = self._generate_a_record(domain_settings)
                if a_value:
                    domain_records['A'] = {
                        'name': record_name,
                        'type': 'A',
                        'value': a_value,
                        'ttl': self.ttl_default
                    }
                    zones[zone]['A'].append({
                        'name': self._format_zone_name(record_name, zone),
                        'ttl': self.ttl_default,
                        'type': 'A',
                        'value': a_value
                    })

            # AAAA Record
            if not skip_aaaa:
                aaaa_value = self._generate_aaaa_record(domain_settings)
                if aaaa_value:
                    domain_records['AAAA'] = {
                        'name': record_name,
                        'type': 'AAAA',
                        'value': aaaa_value,
                        'ttl': self.ttl_default
                    }
                    zones[zone]['AAAA'].append({
                        'name': self._format_zone_name(record_name, zone),
                        'ttl': self.ttl_default,
                        'type': 'AAAA',
                        'value': aaaa_value
                    })

            # SPF Record
            if not skip_spf:
                spf_value = self._generate_spf_record(domain_settings)
                if spf_value:
                    domain_records['SPF'] = {
                        'name': record_name,
                        'type': 'TXT',
                        'value': spf_value,
                        'ttl': self.ttl_default
                    }
                    zones[zone]['TXT'].append({
                        'name': self._format_zone_name(record_name, zone),
                        'ttl': self.ttl_default,
                        'type': 'TXT',
                        'value': spf_value,
                        'comment': 'SPF Record'
                    })

            # DKIM Record
            if not skip_dkim:
                dkim_record = self._generate_dkim_record(domain)
                if dkim_record:
                    domain_records['DKIM'] = dkim_record['domain_record']
                    zones[zone]['TXT'].append(dkim_record['zone_record'])

            # DMARC Record
            if not skip_dmarc and domain == self._get_registrable_domain(domain):
                dmarc_value = self._generate_dmarc_record(domain_settings)
                if dmarc_value:
                    domain_records['DMARC'] = {
                        'name': '_dmarc',
                        'type': 'TXT',
                        'value': dmarc_value,
                        'ttl': self.ttl_default
                    }
                    zones[zone]['TXT'].append({
                        'name': '_dmarc.' + zone + '.',
                        'ttl': self.ttl_default,
                        'type': 'TXT',
                        'value': dmarc_value,
                        'comment': 'DMARC Record'
                    })

            # Site Verification Record
            if not skip_site_verification and 'site_verification' in domain_settings:
                sv_value = domain_settings['site_verification']
                domain_records['site_verification'] = {
                    'name': record_name,
                    'type': 'TXT',
                    'value': sv_value,
                    'ttl': self.ttl_default
                }

            # CAA Record
            if not skip_caa:
                caa_records = self._generate_caa_record(domain, domain_settings)
                if caa_records:
                    for i, caa_record in enumerate(caa_records):
                        domain_records[f'CAA_{i}'] = caa_record['domain_record']
                        zones[zone]['CAA'].append(caa_record['zone_record'])

            # CNAME Record
            if 'cname' in domain_settings:
                cname_value = domain_settings['cname']
                domain_records['CNAME'] = {
                    'name': record_name,
                    'type': 'CNAME',
                    'value': cname_value,
                    'ttl': self.ttl_default
                }

            records[domain] = domain_records

        return records, zones, dkim_key_items

    def _flatten_dkim_keytable(self, keytable_data):
        """Flatten KeyTable data into list for easy iteration"""
        items = []
        for domain, selectors in (keytable_data or {}).items():
            for selector_name, selector_data in selectors.items():
                items.append({
                    'domain': domain,
                    'name': selector_name,
                    'data': selector_data
                })
        return items

    def _normalize_domains(self):
        """Normalize domains by adding registrable domains"""
        result = {}

        for domain, settings in self.domains.items():
            # Ensure settings is a dict
            result[domain] = settings if settings and isinstance(settings, dict) else {}

        # Extract registrable domains
        registrable_domains = set()
        for domain in self.domains.keys():
            reg_domain = self._get_registrable_domain(domain)
            if reg_domain not in result:
                registrable_domains.add(reg_domain)

        # Add registrable domains
        for domain in registrable_domains:
            result[domain] = {}

        # Process CNAME domains
        for domain, settings in list(result.items()):
            if settings and isinstance(settings, dict) and 'cnames' in settings:
                for cname in settings['cnames']:
                    cname_domain = cname + '.' + domain
                    if cname_domain not in result:
                        result[cname_domain] = {'cname': domain}

        return result

    def _parse_opendkim_keytable(self):
        """Parse OpenDKIM KeyTable file"""
        keytable_data = {}

        if not self.opendkim_keytable_path or not os.path.exists(self.opendkim_keytable_path):
            return keytable_data

        try:
            with open(self.opendkim_keytable_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if len(parts) < 2:
                        continue

                    # Format: selector.domain key:path
                    key_spec = parts[0]
                    key_location = parts[1]

                    if ':' not in key_location:
                        continue

                    # Extract domain and key path
                    key_parts = key_location.split(':')
                    if len(key_parts) >= 3:
                        domain = key_parts[0]
                        selector = key_parts[1]
                        key_path = key_parts[2]

                        # Store selector and path for domain
                        if domain not in keytable_data:
                            keytable_data[domain] = {}

                        keytable_data[domain][selector] = {
                            'name': key_spec.split('.')[0],  # selector
                            'key_path': key_path,
                            'txt_path': key_path.replace('.private', '.txt')
                        }
        except (IOError, OSError) as e:
            self.module.fail_json(msg=f"Failed to read KeyTable: {str(e)}")

        return keytable_data

    def _get_registrable_domain(self, domain):
        """Get registrable domain (using simple logic)"""
        # Prefer publicsuffix list when available
        if HAS_PUBLICSUFFIX:
            registrable = publicsuffix2.get_sld(domain)
            if registrable:
                return registrable
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain

    def _get_record_name(self, domain, zone):
        """Get record name (subdomain or @)"""
        if domain == zone:
            return '@'
        # Remove zone from domain
        if domain.endswith('.' + zone):
            return domain[:-len('.' + zone)]
        return domain

    def _format_zone_name(self, record_name, zone):
        """Format zone name for BIND format"""
        if record_name == '@':
            return zone + '.'
        return record_name + '.' + zone + '.'

    def _generate_a_record(self, domain_settings):
        """Generate A record value"""
        ipaddr = domain_settings.get('ipaddr', {})
        ipv4 = ipaddr.get('ipv4') or self.server_ipv4
        return ipv4 if ipv4 else None

    def _generate_aaaa_record(self, domain_settings):
        """Generate AAAA record value"""
        ipaddr = domain_settings.get('ipaddr', {})
        ipv6 = ipaddr.get('ipv6') or self.server_ipv6
        return ipv6 if ipv6 else None

    def _generate_spf_record(self, domain_settings):
        """Generate SPF record value"""
        spf_parts = ['v=spf1']

        # Add IP addresses
        ipaddr = domain_settings.get('ipaddr', {})
        ipv4 = ipaddr.get('ipv4') or self.server_ipv4
        ipv6 = ipaddr.get('ipv6') or self.server_ipv6

        if ipv4:
            spf_parts.append(f'ip4:{ipv4}')
        if ipv6:
            spf_parts.append(f'ip6:{ipv6}')

        # Add other values
        spf_config = domain_settings.get('spf', {})
        other_values = spf_config.get('other_values', self.spf_default.get('other_values', []))
        spf_parts.extend(other_values)

        # Add all qualifier
        all_qualifier = spf_config.get('all_qualifier', self.spf_default.get('all_qualifier', '~'))
        spf_parts.append(f'{all_qualifier}all')

        return ' '.join(spf_parts)

    def _generate_dkim_record(self, domain):
        """Generate DKIM record value"""
        if domain not in self.dkim_keytable_data:
            return None

        records = {}
        for selector, key_data in self.dkim_keytable_data[domain].items():
            txt_path = key_data['txt_path']
            dkim_name = f"{selector}._domainkey"

            # Try to read zone file
            dkim_value = None
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, 'r') as f:
                        content = f.read()
                        # Extract public key from zone file
                        dkim_value = self._parse_dkim_zone_file(content)
                except (IOError, OSError):
                    pass

            if dkim_value:
                return {
                    'domain_record': {
                        'name': dkim_name,
                        'type': 'TXT',
                        'value': dkim_value,
                        'ttl': self.ttl_default
                    },
                    'zone_record': {
                        'name': self._format_zone_name(dkim_name, domain),
                        'ttl': self.ttl_default,
                        'type': 'TXT',
                        'value': dkim_value,
                        'comment': 'DKIM Record'
                    }
                }

        return None

    def _parse_dkim_zone_file(self, content):
        """Parse DKIM zone file and extract public key"""
        # Extract quoted parts
        quoted_parts = re.findall(r'"([^"]*)"', content)
        if quoted_parts:
            return ''.join(quoted_parts)

        # Try parentheses format
        match = re.search(r'\(\s*(.*?)\s*\)', content, re.DOTALL)
        if match:
            inner = match.group(1)
            # Remove quotes and normalize
            inner = re.sub(r'"[ \t\r\n]+"', '', inner)
            inner = re.sub(r'^\"|\"$', '', inner).strip()
            return inner

        return None

    def _generate_dmarc_record(self, domain_settings):
        """Generate DMARC record value"""
        dmarc_config = domain_settings.get('dmarc', self.dmarc_default)

        dmarc_parts = ['v=DMARC1']

        if 'p' in dmarc_config:
            dmarc_parts.append(f"p={dmarc_config['p']}")
        if 'pct' in dmarc_config:
            dmarc_parts.append(f"pct={dmarc_config['pct']}")
        if 'sp' in dmarc_config:
            dmarc_parts.append(f"sp={dmarc_config['sp']}")
        if 'aspf' in dmarc_config:
            dmarc_parts.append(f"aspf={dmarc_config['aspf']}")
        if 'adkim' in dmarc_config:
            dmarc_parts.append(f"adkim={dmarc_config['adkim']}")
        if 'rua' in dmarc_config:
            dmarc_parts.append(f"rua={dmarc_config['rua']}")
        if 'ruf' in dmarc_config:
            dmarc_parts.append(f"ruf={dmarc_config['ruf']}")

        return ';'.join(dmarc_parts)

    def _generate_caa_record(self, domain, domain_settings):
        """Generate CAA record values"""
        caa_config = domain_settings.get('caa', self.caa_default)

        if not caa_config or 'ca_domain' not in caa_config:
            return []

        records = []
        flag = caa_config.get('flag', 0)
        tag = caa_config.get('tag', 'issue')
        ca_domain = caa_config['ca_domain']

        caa_value = f'{flag} {tag} "{ca_domain}"'

        records.append({
            'domain_record': {
                'name': '@',
                'type': 'CAA',
                'value': caa_value,
                'ttl': self.ttl_default
            },
            'zone_record': {
                'name': domain + '.',
                'ttl': self.ttl_default,
                'type': 'CAA',
                'value': caa_value
            }
        })

        return records


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domains=dict(type='dict', required=True),
            server_ipv4=dict(type='str', default=None),
            server_ipv6=dict(type='str', default=None),
            opendkim_keytable_path=dict(type='str', default='/etc/opendkim/KeyTable'),
            spf_default=dict(type='dict', default={}),
            dkim_default=dict(type='dict', default={}),
            dmarc_default=dict(type='dict', default={}),
            caa_default=dict(type='dict', default={}),
            ttl_default=dict(type='int', default=3600),
        ),
        supports_check_mode=True
    )

    if not HAS_DNSPYTHON:
        module.fail_json(msg='dnspython is required for this module')

    try:
        collector = DNSRecordCollector(
            module,
            domains=module.params['domains'],
            server_ipv4=module.params['server_ipv4'],
            server_ipv6=module.params['server_ipv6'],
            opendkim_keytable_path=module.params['opendkim_keytable_path'],
            spf_default=module.params['spf_default'],
            dkim_default=module.params['dkim_default'],
            dmarc_default=module.params['dmarc_default'],
            caa_default=module.params['caa_default'],
            ttl_default=module.params['ttl_default'],
        )

        records, zones, dkim_key_items = collector.collect()

        module.exit_json(
            changed=False,
            records=records,
            zones=zones,
            dkim_keytable_data=collector.dkim_keytable_data,
            dkim_key_items=dkim_key_items
        )

    except Exception as e:
        module.fail_json(msg=f"Error collecting DNS records: {str(e)}")


if __name__ == '__main__':
    main()
