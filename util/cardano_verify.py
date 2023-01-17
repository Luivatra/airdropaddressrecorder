import requests
from bs4 import BeautifulSoup


def verify_address(address, blockfrost_project_id):
  address_url = "https://cardano-mainnet.blockfrost.io/api/v0/addresses/{address}"
  headers = {'project_id': blockfrost_project_id}
  stake_address = None

  # if 'stake' in address:
  #   return verify_pool(address, blockfrost_project_id)

  response = requests.get(
    address_url.format(address=address),
    headers=headers
    )

  if response.status_code == 200:
    # stake_address = response.json()['stake_address']
    # return verify_pool(stake_address, blockfrost_project_id)
    return True
  else:
    # cardanoscan_url = 'https://cardanoscan.io/address/{address}'
    # page = requests.get(cardanoscan_url.format(address=address))
    # soup = BeautifulSoup(page.content, "html.parser")
    # addrs = soup.find_all('span', {'class': 'text-muted'})
    # for a in addrs:
    #   if 'stake' in a.string:
    #     stake_address = a.string
    #     return verify_address(stake_address, blockfrost_project_id)
    return False
  

# def verify_pool(stake_address, blockfrost_project_id):
#   stake_url = 'https://cardano-mainnet.blockfrost.io/api/v0/accounts/{stake_address}/delegations'
#   headers = {'project_id': blockfrost_project_id}

#   response = requests.get(
#     stake_url.format(stake_address=stake_address),
#     headers=headers
#     )

#   correct_pools = [
#     'pool17h6slydr6rd9vquqa38p5cf9xqnpc24w6a99rhllcjzljgugx6x',
#     'pool15hx9hze8ulcsw6e7ceelz2pem2g3u9c29wqe4eszkhspj3wcdlx',
#     'f5f50f91a3d0da560380ec4e1a612530261c2aaed74a51dfffc485f9',
#     'a5cc5b8b27e7f1076b3ec673f12839da911e170a2b819ae602b5e019'
#     ]
#   if len(response.json())>0:
#     users_current_pool = response.json()[-1]['pool_id']

#     if users_current_pool in correct_pools:
#       return True
#     else:
#       return False
#   else:
#     return False