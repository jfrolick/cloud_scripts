import ldap
import getopt
import sys

def ldap_query_group_members(ldap_url, bind_dn, bind_password, base_dn):
    # Establish a connection to the LDAP server
    ldap_connection = ldap.initialize(ldap_url)
    ldap_connection.simple_bind_s(bind_dn, bind_password)

    # Enable paged results control with a page size
    page_size = 1000
    control = ldap.controls.SimplePagedResultsControl(True, size=page_size, cookie="")

    # Define the LDAP search filter for group objects
    group_filter = "(objectClass=groupOfNames)"

    try:
        # Search for group objects in the specified organizational unit with pagination
        result = []
        while True:
            msgid = ldap_connection.search_ext(
                base_dn,
                ldap.SCOPE_SUBTREE,
                group_filter,
                serverctrls=[control],
            )
            rtype, rdata, rmsgid, serverctrls = ldap_connection.result3(msgid)
            result.extend(rdata)

            # Get cookie from paged results control
            pctrls = [c for c in serverctrls if c.controlType == ldap.controls.SimplePagedResultsControl.controlType]
            if pctrls:
                cookie = pctrls[0].cookie
                if cookie:
                    control.cookie = cookie
                else:
                    break
            else:
                break

        # Iterate through each group
        for dn, entry in result:
            group_name = entry['cn'][0].decode('utf-8')

            # Retrieve and display group members
            members = entry.get('member', [])
            if members:
                for member in members:
                    member_dn = member.decode('utf-8')

                    # Query the directory for each member object
                    try:
                        if member_dn not in member_cache:
                            member_entry = ldap_connection.search_s(member_dn, ldap.SCOPE_BASE)[0][1]
                            sam_account_name = member_entry.get('sAMAccountName', [''])[0].decode('utf-8')
                            user_principal_name = member_entry.get('userPrincipalName', [''])[0].decode('utf-8')

                            # Cache the member to avoid duplicate lookups
                            member_cache[member_dn] = {
                                'sam_account_name': sam_account_name,
                                'user_principal_name': user_principal_name
                            }

                        # Print information on a single line
                        print(f"{group_name},{member_dn},{member_cache[member_dn]['sam_account_name']},{member_cache[member_dn]['user_principal_name']}")

                    except ldap.LDAPError as e:
                        print(f"Error querying member {member_dn}: {e}")

    except ldap.LDAPError as e:
        print(f"LDAP Error: {e}")

    finally:
        # Close the LDAP connection
        ldap_connection.unbind()

if __name__ == "__main__":
    # Specify your LDAP server details
    ldap_url = "ldap://your-ldap-server:389"
    bind_dn = "cn=admin,dc=example,dc=com"
    bind_password = "your-password"

    # Initialize member cache to avoid duplicate lookups
    member_cache = {}

    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:b:", ["url=", "bind-dn=", "bind-password=", "base-dn="])
    except getopt.GetoptError:
        print("Usage: script.py -u <ldap_url> -b <bind_dn> -p <bind_password> --base-dn <base_dn>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("Usage: script.py -u <ldap_url> -b <bind_dn> -p <bind_password> --base-dn <base_dn>")
            sys.exit()
        elif opt in ("-u", "--url"):
            ldap_url = arg
        elif opt in ("-b", "--bind-dn"):
            bind_dn = arg
        elif opt in ("-p", "--bind-password"):
            bind_password = arg
        elif opt == "--base-dn":
            base_dn = arg

    # Perform the LDAP query for group members
    ldap_query_group_members(ldap_url, bind_dn, bind_password, base_dn)

