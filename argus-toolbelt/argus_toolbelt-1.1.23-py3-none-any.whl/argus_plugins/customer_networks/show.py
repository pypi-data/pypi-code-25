import os
from argus_cli.plugin import register_command
from argus_cli.helpers import formatting

from argus_api.helpers import authentication
from argus_api.api.customers.v1.customer import get_customer_by_shortname
from argus_api.api.customernetworks.v1.network import get_customer_networks

@register_command(extending="customer-networks")
def list(customer: str, api_key: str = None) -> None:
    """
    This function handles the subcommand "show", and only fetches and displays a list of existing networks

    :param customer: Customer shortname
    :alias customer: C
    """
    authorize = authentication.with_authentication(api_key=api_key or os.environ.get("ARGUS_API_KEY"))

    # Find customer by name
    customer = authorize(get_customer_by_shortname)(shortName=customer)

    if not customer:
        raise LookupError('No customer has been selected. Customer is required to edit customer networks.')

    # Otherwise select the only customer
    networks = authorize(get_customer_networks)(customerID=[customer["data"]["id"]], limit=-1)

    def format_column(value: dict, key: str):
        if key == "flags" and value:
            return ",".join(value)
        elif key == "networkAddress":
            return "%s/%s" % (value["address"], value["maskBits"])
        elif key == "location":
            return value["name"]
        else:
          return value or "-"

    print(
        formatting.table(
          data=networks["data"],
          keys=["networkAddress", "description", "zone", "location", "flags"],
          format=format_column,
          title='Networks for %s' % customer['data']['name'],
        )
    )
  